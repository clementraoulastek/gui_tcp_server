from collections import OrderedDict
import datetime
import logging
from threading import Thread
import time
from typing import Dict, List, Optional, Union
import pytz

from tzlocal import get_localzone
from src.client.client import Client
from src.client.controller.worker import Worker
from src.client.core.qt_core import (
    QObject,
    QHBoxLayout,
    QLayout,
    QWidget,
    QEvent,
    QEnterEvent,
    QIcon,
    QTimer,
    QListWidgetItem,
    QVBoxLayout,
    QSize,
    QSizePolicy,
    QPlainTextEdit
)
from src.client.controller.event_manager import EventManager
from src.client.view.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.layout.body_scroll_area import BodyScrollArea
from src.client.view.layout.message_layout import MessageLayout
from src.tools.commands import Commands
from src.client.view.layout.login_layout import LoginLayout
from src.client.view.customWidget.AvatarQLabel import AvatarStatus, AvatarLabel
from src.client.core.qt_core import QHBoxLayout, QLabel, Qt
from src.tools.utils import Themes, Icon, ImageAvatar, QIcon_from_svg, check_str_len, GenericColor
from src.client.controller.api_controller import ApiController, ApiStatus
from src.client.controller.tcp_controller import TcpServerController
import src.client.controller.global_variables as global_variables
from functools import partial

NB_OF_MESSAGES = 50

class GuiController:
    def __init__(
        self,
        ui,
        messages_dict: dict[str, MessageLayout],
        api_controller: ApiController,
        tcp_controller: TcpServerController,
        event_manager: EventManager,
        theme: Themes
    ) -> None:
        self.ui = ui
        self.theme = theme
        self.messages_dict: dict[str, List[MessageLayout]] = messages_dict
        self.api_controller = api_controller
        self.tcp_controller = tcp_controller
        self.dm_avatar_dict: dict[str, AvatarLabel] = {}
        self.event_manager = event_manager
        
    def __init_working_signals(self) -> None:
        """
        Init signals for incoming messages
        """
        self.event_manager.coming_message_signal.connect(self.__diplay_coming_message_on_gui)

        self.event_manager.users_connected_signal.connect(self.__update_gui_with_connected_avatar)

        self.event_manager.users_disconnected_signal.connect(
            self.__update_gui_with_disconnected_avatar
        )
        self.event_manager.react_message_signal.connect(
            self.__update_react_message_on_gui
        )
        self.worker_thread = Thread(
            target=self.__callback_routing_messages_on_ui, daemon=False
        )
        self.worker_thread.start()

        # Update buttons status
        self.update_buttons()

    def diplay_self_message_on_gui(
        self,
        sender: str,
        message: str,
        frame_name: Optional[Union[str, None]] = None,
        message_id: Optional[Union[int, None]] = None,
        nb_react: Optional[int] = 0,
        date: Optional[str] = "",
        response_model: Optional[Union[MessageLayout, None]] = None,
        display: Optional[bool] = True,
        reverse: Optional[bool] = False
    ) -> None:
        """
        Display message on gui and clear the message entry

        Args:
            sender (str): username
            message (str): message
            frame_name (Optional[Union[str, None]], optional): layout name. Defaults to None.
            messsage_id (Optional[Union[int, None]], optional): message id. Defaults to None.
            nb_react (Optional[int], optional): number of reactions. Defaults to 0.
            date (Optional[str], optional): date to display. Defaults to "".
            response_model (Optional[Union[MessageLayout, None]]): MessageLayout object. Defaults to None.
        """
        comming_msg: dict[str, str] = {"id": sender, "message": message}
 
        # Init dict key
        if frame_name not in self.messages_dict.keys():
            self.messages_dict[frame_name] = OrderedDict()

        # Avoid to re-create the same message from an older request from a response model
        if message_id not in self.messages_dict[frame_name].keys():
            message = MessageLayout(
                self,
                comming_msg,
                content=self.ui.users_pict[sender],
                message_id=message_id,
                nb_react=nb_react,
                date=date,
                response_model=response_model,
            )
            # Update the dict
            self.messages_dict[frame_name][message_id] = message
            
            if response_model and response_model.sender_ == self.ui.client.user_name:
                self.update_stylesheet_with_focus_event(message, border_color=self.theme.emoji_color)
        else:
            message = self.messages_dict[frame_name][message_id]
        
        # Display message on gui on the frame
        if display:
            if reverse:
                self.ui.body_gui_dict[frame_name].main_layout.insertLayout(0, message)
            else:
                self.ui.body_gui_dict[frame_name].main_layout.addLayout(message)
            message.is_displayed = True
        
        self.ui.footer_widget.entry.clear()
        
        # Avoid gui troubles on scroll
        if not reverse:
            QTimer.singleShot(0, self.__update_scroll_bar)
        
    def add_older_messages_on_scroll(self) -> None:
        """
        Add older messages on scroll
        """     
        # To avoid multiple scroll event, fetch the first message id
        first_id = self.api_controller.get_first_message_id(self.ui.scroll_area.name, self.ui.client.user_name)
        try:
            message_id_list = list(self.messages_dict[self.ui.scroll_area.name].values())
        except KeyError:
            logging.debug("No messages to display")
            return True

        message_id_list.sort(key=lambda x: x.message_id)

        last_message_id = next((message.message_id for message in message_id_list if message.is_displayed))

        # If the first id is the same as the last message id, it means that we have reached the end of the messages
        if first_id == last_message_id:
            return True
        
        self.fetch_older_messages(last_message_id, NB_OF_MESSAGES, self.ui.scroll_area.name, display=True)

    def display_older_messages(
        self, 
        older_messages: dict, 
        display: Optional[bool] = True,
        reverse: Optional[bool] = False
    ) -> None:
        """
        Update gui with older messages
        """
        sender_list: list[str] = []

        for message in older_messages:
            (
                message_id,
                sender,
                receiver,
                message,
                reaction_nb,
                date,
                is_readed,
                response_id,
            ) = (
                message["message_id"],
                message["sender"],
                message["receiver"],
                message["message"],
                message["reaction_nb"],
                message["created_at"],
                message["is_readed"],
                message["response_id"],
            )
            if (
                receiver != "home"
                and sender != self.ui.client.user_name
                and receiver != self.ui.client.user_name
            ):
                continue

            if receiver == "home":
                dict_name = "home"
            else:
                dict_name = receiver if sender == self.ui.client.user_name else sender

            # Add new room to the messages dict
            if dict_name not in self.messages_dict.keys():
                self.messages_dict[dict_name] = OrderedDict()

            if response_id and response_id not in self.messages_dict[dict_name]:
                older_message = self.api_controller.get_older_message(response_id)
                self.display_older_messages(
                    older_message, 
                    display=False, 
                    reverse=True
                )

            message_model = self.messages_dict[dict_name][response_id] if response_id else None

            # Add a special char to handle the ":" in the message
            message = message.replace(Client.SPECIAL_CHAR, ":")

            # Add sender to a list to avoid multiple avatar update
            if sender not in sender_list:
                sender_list.append(sender)

            # Display message on gui on the home frame
            if receiver == "home":
                self.diplay_self_message_on_gui(
                    sender,
                    message,
                    frame_name="home",
                    message_id=message_id,
                    nb_react=int(reaction_nb),
                    date=date,
                    response_model=message_model,
                    display=display,
                    reverse=reverse
                )
            # Display message on gui on the direct message frame
            elif self.ui.client.user_name in (sender, receiver):
                direct_message_name = (
                    receiver if sender == self.ui.client.user_name else sender
                )
                icon = AvatarLabel(
                    content=self.ui.users_pict[direct_message_name],
                    status=AvatarStatus.DEACTIVATED,
                )
                self.add_gui_for_mp_layout(direct_message_name, icon)

                # Update avatar status with DM circle popup
                if is_readed == False and self.ui.client.user_name == receiver:
                    self.update_pixmap_avatar(direct_message_name, AvatarStatus.DM)

                self.diplay_self_message_on_gui(
                    sender,
                    message,
                    frame_name=direct_message_name,
                    message_id=message_id,
                    nb_react=int(reaction_nb),
                    date=date,
                    response_model=message_model,
                    display=display,
                    reverse=reverse
                )

        # Reset dict to handle new avatar images from conn
        if self.ui.client.user_name in sender_list:
            sender_list.remove(self.ui.client.user_name)

    def __diplay_coming_message_on_gui(self) -> None:
        """
        Callback to update gui with input messages
        """
        if not global_variables.comming_msg["message"]:
            return
        
        message_id= global_variables.comming_msg["message_id"]

        message_model = None
        message = global_variables.comming_msg["message"]

        receiver = global_variables.comming_msg["receiver"]
        
        if response_id := global_variables.comming_msg["response_id"]:
            response_id = int(response_id)
            if receiver == self.ui.client.user_name:
                response_model_receiver = global_variables.comming_msg["id"]
            else:
                response_model_receiver = receiver
            message_model = self.messages_dict[response_model_receiver][response_id]

        message = MessageLayout(
            self,
            global_variables.comming_msg,
            content=self.ui.users_pict[global_variables.comming_msg["id"]],
            message_id=message_id
            if global_variables.comming_msg["id"] != "server"
            else None,
            response_model=message_model,
        )
        if message_model and message_model.sender_ == self.ui.client.user_name:
            self.update_stylesheet_with_focus_event(message, border_color=self.theme.emoji_color)
            if global_variables.comming_msg["receiver"] == "home":
                self.room_icon.update_pixmap(AvatarStatus.DM, background_color=self.theme.rgb_background_color_rooms)
        
        # Revert sender and receiver for DM if the sender is the user
        if receiver == self.ui.client.user_name:
            receiver = global_variables.comming_msg["id"]
            update_avatar = True
        else:
            update_avatar = False
            
        if receiver not in {"home", self.ui.client.user_name}:
            self.add_gui_for_mp_layout(
                receiver,
                AvatarLabel(
                    content=self.ui.users_pict[global_variables.comming_msg["id"]],
                    status=AvatarStatus.DM,
                ),
            )
            
        if update_avatar:
            # Update avatar status with DM circle popup
            self.dm_avatar_dict[receiver].update_pixmap(AvatarStatus.DM, background_color=self.theme.rgb_background_color_actif)
            
        # Init dict key
        if receiver not in self.messages_dict.keys():
            self.messages_dict[receiver] = OrderedDict()
          
        self.messages_dict[receiver][message_id] = message
         
        self.ui.body_gui_dict[receiver].main_layout.addLayout(message)
        message.is_displayed = True

        # Clear the dict values
        global_variables.comming_msg = dict.fromkeys(global_variables.comming_msg, "")

    def __update_scroll_bar(self) -> None:
        """
        Callback to handle scroll bar update
        """
        self.ui.scroll_area.scrollToBottom()

    def __update_react_message_on_gui(self) -> None:
        """
        Callback to update gui with input messages
        """
        if not global_variables.comming_msg["reaction"]:
            return

        message_id, nb_reaction = (
            global_variables.comming_msg["message_id"],
            global_variables.comming_msg["reaction"],
        )
        if global_variables.comming_msg["receiver"] == "home":
            dict_name = "home"
        else:
            dict_name = global_variables.comming_msg["receiver"] if global_variables.comming_msg["id"] == self.ui.client.user_name else global_variables.comming_msg["id"]
        
        message: MessageLayout = self.messages_dict[dict_name][int(message_id)]
        message.update_react(int(nb_reaction))

        # Reset global variables
        (
            global_variables.comming_msg["reaction"], 
            global_variables.comming_msg["id"],
            global_variables.comming_msg["receiver"],
            global_variables.comming_msg["message_id"]
        ) = (
            "",
            "",
            "",
            ""
        )

    def __callback_routing_messages_on_ui(self) -> None:
        """
        Read messages comming from server
        """
        WAITING_TIME = 0.01

        while self.ui.client.is_connected:
            header, payload = self.ui.client.read_data()
            if payload:
                self.__routing_coming_messages(header, payload)
            else:
                break
            time.sleep(WAITING_TIME)

        logging.debug("Connection lost with the server")

    def __routing_coming_messages(self, header: int, payload: str) -> None:
        """
        Update global variables with input messages

        Args:
            header (int): header of the message
            payload (str): payload of the message
        """
        if ":" in payload:
            if header == Commands.CONN_NB.value:
                nb_of_users = payload.split(":")[1]
                self.ui.left_nav_widget.info_label.setText(
                    f"Users online   |   {nb_of_users}"
                )
            elif header == Commands.HELLO_WORLD.value:
                self.__add_sender_avatar(payload, global_variables.user_disconnect)
                # Return welcome to hello world
                self.ui.client.send_data(Commands.WELCOME, Commands.WELCOME.name)
            elif header == Commands.WELCOME.value:
                self.__add_sender_avatar(payload, global_variables.user_disconnect)
            elif header == Commands.GOOD_BYE.value:
                self.__remove_sender_avatar(
                    payload,
                    global_variables.user_connected,
                    global_variables.user_disconnect,
                )
            elif header in [Commands.ADD_REACT.value, Commands.RM_REACT.value]:
                self.__handle_reaction(payload)
            else:
                self.__handle_message(payload)
            
    def __handle_reaction(self, payload: str) -> None:
        """
        Get the message reaction and update global variables

        Args:
            payload (str): payload of the message with reaction number inside
        """
        payload_fields = payload.split(":")
        sender = payload_fields[0]
        receiver = payload_fields[1]
        message = payload_fields[2]
        payload = message.replace(" ", "")
        payload_list = payload.split(";")
        
        message_id, nb_reaction = payload_list[0], payload_list[1]
        
        global_variables.comming_msg["id"] = sender
        global_variables.comming_msg["receiver"] = receiver
        global_variables.comming_msg["message_id"] = message_id
        global_variables.comming_msg["reaction"] = nb_reaction
        
        self.event_manager.event_react_message()

    def __handle_message(self, payload: str) -> None:
        """
        Get the message and update global variables

        Args:
            payload (str): payload of the message
        """
        payload_fields = payload.split(":")
        
        message_id = payload_fields[0]
        sender = payload_fields[1]
        receiver = payload_fields[2]
        message = payload_fields[3]

        if len(payload_fields) == 5:
            response_id = payload_fields[4]
            global_variables.comming_msg["response_id"] = response_id

        global_variables.comming_msg["message_id"] = int(message_id)
        global_variables.comming_msg["id"] = sender
        global_variables.comming_msg["receiver"] = receiver.replace(" ", "")
        global_variables.comming_msg["message"] = message.replace("$replaced$", ":")
        
        self.event_manager.event_coming_message()

    def __remove_sender_avatar(
        self,
        payload: str,
        user_connected: dict[str, List[Union[str, bool]]],
        user_disconnect: dict[str, List[Union[str, bool]]],
    ) -> None:
        """
        Remove the user icon from the connected layout from a GOOD BYE message

        Args:
            payload (str): payload of the command
            user_connected (dict[str, List[Union[str, bool]]]): dict of connected users
            user_disconnect (dict[str, List[Union[str, bool]]]): dict of disconnected users
        """
        id_, _ = payload.split(":", 1)
        self.clear_avatar("user_inline", self.ui.left_nav_widget, f"{id_}_layout")
        self.api_controller.add_sender_picture(id_)
        user_disconnect[id_] = [user_connected[id_][0], False]
        self.ui.users_connected.pop(id_)
        
        if id_ in self.dm_avatar_dict.keys() and self.dm_avatar_dict[id_].status != AvatarStatus.DM:
            self.dm_avatar_dict[id_].update_pixmap(AvatarStatus.DEACTIVATED)
        
        self.event_manager.event_users_disconnected()

    def __add_sender_avatar(
        self, payload: str, user_disconnect: dict[str, List[Union[str, bool]]]
    ) -> None:
        """
        Add the user icon to the connected layout from a HELLO WORLD or WELCOME message

        Args:
            payload (str): payload of the command
            user_disconnect (dict[str, List[Union[str, bool]]]): dict of disconnected users
        """
        id_, _ = payload.split(":", 1)

        # In case of new user not register before
        if id_ not in self.ui.users_pict.keys():
            self.api_controller.add_sender_picture(id_)

        # Remove user's icon disconnected from the disconnected layout
        if id_ in user_disconnect:
            self.clear_avatar(
                "user_offline", self.ui.left_nav_widget, f"{id_}_layout_disconnected"
            )
            user_disconnect.pop(id_)

        if id_ in self.dm_avatar_dict.keys() and self.dm_avatar_dict[id_].status != AvatarStatus.DM:
            self.dm_avatar_dict[id_].update_pixmap(AvatarStatus.ACTIVATED)

        # Add the user icon to the connected layout
        if id_ not in self.ui.users_connected.keys():
            self.ui.users_connected[id_] = True
            self.api_controller.update_user_connected(id_, self.ui.users_pict[id_])
            
        self.event_manager.event_users_connected()

    def update_user_icon(self) -> None:
        """
        Update user icon
        """
        username = self.ui.client.user_name
        if self.ui.backend.send_user_icon(username, None):
            self.clear_avatar("user_inline", self.ui.left_nav_widget, f"{username}_layout")
            self.api_controller.get_user_icon(update_personal_avatar=True)
            self.user_profile_widget.hide()
            
            
    def show_user_profile(self) -> None:
        if hasattr(self, "user_profile_widget") and self.user_profile_widget.isVisible():
            return
        
        creation_date, description = self.api_controller.get_user_creation_date(self.ui.client.user_name)
        local_timezone = get_localzone()
        dt_object = datetime.datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        local_dt_object = dt_object.replace(tzinfo=pytz.utc).astimezone(
            local_timezone
        )
        date_time = local_dt_object.strftime("%d/%m/%Y at %H:%M:%S")
        self.user_profile_widget = QWidget()
        self.user_profile_widget.setStyleSheet(
            f"border-radius: 8px; border: 1px solid; border-color: {self.theme.nav_color};"
        )
        height = 250
        self.user_profile_widget.move(
            self.ui.footer_widget.user_info_widget.x() + 15, 
            self.ui.footer_widget.send_widget.y() - height
        )
        self.user_profile_widget.setFixedSize(
            QSize(self.ui.footer_widget.user_info_widget.width() // 1.5 , height))
        user_profile_layout = QVBoxLayout(self.user_profile_widget)
        user_profile_layout.setSpacing(5)
        user_profile_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add user avatar
        user_avatar = AvatarLabel(
            content=self.ui.users_pict[self.ui.client.user_name],
            status=AvatarStatus.ACTIVATED,
        )
        user_name = QLabel(self.ui.client.user_name)
        user_name.setStyleSheet("font-weight: bold; border: 0px solid;")
        
        user_info = QLabel(
            f"<strong>Creation date:</strong>\
            <br>\
            {date_time}\
            <br><br>\
            <strong>Description:</strong>"
        )
        user_info.setWordWrap(True)
        user_info.setStyleSheet("border: 0px solid;")
        user_info.setContentsMargins(5, 5, 5, 5)
        
        self.status_widget = QPlainTextEdit()
        self.status_widget.setPlaceholderText(
            description or "Right your description here ..."
        )
        self.status_widget.setStyleSheet(
            f"background-color: {self.theme.inner_color};"
        )
        self.status_widget.setFixedHeight(60)
        
        user_action_widget = QWidget()
        user_action_widget.setFixedHeight(40)
        user_action_widget.setStyleSheet(
            f"border: 0px solid; background-color: {self.theme.search_color};"
        )
        user_action_layout = QHBoxLayout(user_action_widget)
        user_action_layout.setContentsMargins(0, 0, 0, 0)
        
        user_info_layout = QHBoxLayout()
        user_info_layout.setContentsMargins(10, 10, 10, 10)
        user_info_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        user_info_layout.setSpacing(10)
        
        # Add user update button
        update_button = CustomQPushButton(" Update")
        update_button.setToolTip("Update Avatar")
        update_button.setFixedSize(QSize(80, 30))
        update_button.clicked.connect(self.update_user_icon)
        
        save_button = CustomQPushButton("")
        update_user_icon = QIcon(QIcon_from_svg(Icon.SAVE.value, color=self.theme.text_color))
        save_button.setIcon(update_user_icon)
        save_button.setFixedSize(QSize(30, 30))
        save_button.clicked.connect(self.update_user_description)
        
        close_btn = CustomQPushButton()
        close_btn.clicked.connect(self.user_profile_widget.hide)    
        close_btn.setToolTip("Close")
        close_btn.setFixedSize(QSize(30, 30))
        
        update_user_icon = QIcon(QIcon_from_svg(Icon.SWITCH_COLOR.value, color=self.theme.text_color))
        close_icon = QIcon(QIcon_from_svg(Icon.CLOSE.value, color=GenericColor.RED.value))
        update_button.setIcon(update_user_icon)
        close_btn.setIcon(close_icon)
        
        user_info_layout.addWidget(
            user_avatar, 
        )
        user_info_layout.addWidget(user_name)
        user_action_layout.addWidget(update_button)
        user_action_layout.addWidget(save_button)
        user_action_layout.addWidget(close_btn)
        
        user_profile_layout.addLayout(user_info_layout)
        user_profile_layout.addWidget(user_info, alignment=Qt.AlignmentFlag.AlignTop)
        user_profile_layout.addWidget(self.status_widget, alignment=Qt.AlignmentFlag.AlignTop)
        user_profile_layout.addWidget(user_action_widget)
        
        self.ui.main_layout.addChildWidget(self.user_profile_widget)
        self.user_profile_widget.setFocus()

    def __update_gui_with_connected_avatar(self) -> None:
        """
        Callback to update gui with input connected avatar
        """
        user_connected_dict = global_variables.user_connected.copy()
        
        for user, data in user_connected_dict.items():
            if data[1] == True:
                continue
            global_variables.user_connected[user] = [data[0], True]
            # Layout
            user_widget = CustomQPushButton()
            user_widget.setFixedHeight(50)
            user_widget.setStyleSheet("border: none")
            user_layout = QHBoxLayout(user_widget)
            user_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            user_layout.setSpacing(10)
            user_layout.setContentsMargins(5, 0, 0, 0)
            username = user
            user_layout.setObjectName(f"{username}_layout")
            content = data[0]

            def hover(event: QEvent, user_widget):
                if isinstance(event, QEnterEvent):
                    color = self.theme.background_color
                    user_pic.update_pixmap(
                        AvatarStatus.ACTIVATED, background_color=self.theme.rgb_background_color_innactif
                    )
                else:
                    color = self.theme.inner_color
                    user_pic.update_pixmap(AvatarStatus.ACTIVATED, background_color=self.theme.rgb_background_color_actif)
                style_ = """
                QWidget {{
                background-color: {color};
                border-radius: 8px;
                border: 1px solid {color};
                }} 
                """
                user_widget.setStyleSheet(style_.format(color=color))

            # Create avatar label
            user_pic, dm_pic = AvatarLabel(
                content=content, status=AvatarStatus.ACTIVATED, background_color=self.theme.rgb_background_color_actif
            ), AvatarLabel(content=content, status=AvatarStatus.ACTIVATED, background_color=self.theme.rgb_background_color_actif)

            # Update picture alignment
            user_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dm_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            user_pic.setStyleSheet("border: 0px;")
            
            # Avoid gui troubles with bigger username
            username_label = check_str_len(username)
            user_name = QLabel(username_label)
            
            if username in self.dm_avatar_dict.keys() and self.dm_avatar_dict[username].status != AvatarStatus.DM:
                self.dm_avatar_dict[username].update_pixmap(
                    AvatarStatus.ACTIVATED, 
                    background_color=self.theme.rgb_background_color_actif
                )

            # StyleSheet
            style_ = """
            QLabel {{
            text-align: left;
            font-weight: bold;
            border-radius: 8px;
            border: 1px solid;
            border-color: transparent;
            }} 
            """
            # Add user menu
            if username != self.ui.client.user_name:
                user_widget.setToolTip("Open direct message")
                user_widget.enterEvent = partial(hover, user_widget=user_widget)
                user_widget.leaveEvent = partial(hover, user_widget=user_widget)

                user_widget.clicked.connect(
                    partial(self.add_gui_for_mp_layout, username, dm_pic, True)
                )
                hover_ = """
                QPushButton:hover {{
                text-decoration: underline;
                }}
                """
                style_ = f"{style_}{hover_}"
            user_name.setStyleSheet(style_.format(color=self.theme.background_color))

            # Add widgets to the layout
            user_layout.addWidget(user_pic)
            user_layout.addWidget(user_name)
            self.ui.left_nav_widget.user_inline.insertWidget(
                1,
                user_widget
            )
            self.ui.left_nav_widget.user_inline.update()

    # TODO: Avoid code duplication
    def __update_gui_with_disconnected_avatar(self) -> None:
        """
        Callback to update gui with input disconnected avatar
        """
        user_disconnected_dict = global_variables.user_disconnect.copy()
        
        for user, data in user_disconnected_dict.items():
            if data[1] == True:
                continue
            # Layout
            user_widget = CustomQPushButton()
            user_widget.setToolTip("Open direct message")
            user_widget.setFixedHeight(50)
            style_ = """
            QWidget {{
            border-radius: 8px;
            border: 0px solid {color};
            }} 
            """
            def hover(event: QEvent, user_widget, user_pic: AvatarLabel):
                if isinstance(event, QEnterEvent):
                    color = self.theme.background_color
                    user_pic.graphicsEffect().setEnabled(False)
                    user_pic.update_pixmap(
                        AvatarStatus.DEACTIVATED,
                        background_color=self.theme.rgb_background_color_innactif,
                    )
                else:
                    color = self.theme.inner_color
                    user_pic.graphicsEffect().setEnabled(True)
                    user_pic.update_pixmap(AvatarStatus.DEACTIVATED, background_color=self.theme.rgb_background_color_actif)
                style_ = """
                QWidget {{
                background-color: {color};
                border-radius: 8px;
                border: 0px solid {color};
                }} 
                """
                user_widget.setStyleSheet(style_.format(color=color))
                user_widget.update()

            user_widget.setStyleSheet(style_.format(color=self.theme.background_color))
            user_widget.setContentsMargins(0, 0, 0, 0)

            user_layout = QHBoxLayout(user_widget)
            user_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            user_layout.setSpacing(10)
            user_layout.setContentsMargins(5, 0, 0, 0)
            username = user
            content = data[0]
            user_layout.setObjectName(f"{username}_layout_disconnected")

            # Create avatar label
            user_pic, dm_pic = AvatarLabel(
                content=content, status=AvatarStatus.DEACTIVATED,
            ), AvatarLabel(content=content, status=AvatarStatus.DEACTIVATED)

            user_widget.enterEvent = partial(
                hover, user_widget=user_widget, user_pic=user_pic
            )
            user_widget.leaveEvent = partial(
                hover, user_widget=user_widget, user_pic=user_pic
            )

            # Update picture
            user_pic.set_opacity(0.2)
            user_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dm_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            user_pic.setStyleSheet(
                f"border: 0px solid;\
                border-color: {self.theme.background_color};"
            )

            # Avoid gui troubles with bigger username
            username_label = check_str_len(username)
            user_name = QLabel(username_label)
            user_name.setContentsMargins(0, 0, 0, 0)

            # Add user menu
            user_widget.clicked.connect(
                partial(self.add_gui_for_mp_layout, username, dm_pic, True)
            )
            style_ = """
            QLabel {{
            text-align: left;
            font-weight: bold;
            border-radius: 8px;
            border: 1px solid;
            border-color: {color};
            }}
            """
            user_name.setStyleSheet(style_.format(color="transparent"))

            # Add widgets to the layout
            user_layout.addWidget(user_pic)
            user_layout.addWidget(user_name)
            self.ui.left_nav_widget.user_offline.insertWidget(
                1,
                user_widget
            )
            self.ui.left_nav_widget.user_offline.update()

            global_variables.user_disconnect[user] = [data[0], True]

        self.ui.left_nav_widget.info_disconnected_label.setText(
            f"Users offline   |   {len(global_variables.user_disconnect)}"
        )

    def clear(self) -> None:
        """
        Clear the main layout
        """
        for i in reversed(range(self.ui.scroll_area.main_layout.count())):
            layout = self.ui.scroll_area.main_layout.itemAt(i).layout()
            if isinstance(layout, QLayout):
                for j in reversed(range(layout.count())):
                    layout.itemAt(j).widget().deleteLater()
        self.ui.scroll_area.main_layout.update()

    def clear_avatar(
        self,
        parent_layout: QLayout,
        parent=None,
        layout_name: Optional[Union[QHBoxLayout, None]] = None,
        delete_all: Optional[bool] = False,
    ) -> None:
        """
        Clear avatars or all widgets from the layout

        Args:
            parent_layout (QLayout): parent layout
            layout_name (Optional[Union[QHBoxLayout, None]], optional): layout name. Defaults to None.
            delete_all (Optional[bool], optional): delete all widgets. Defaults to False.
        """
        for i in reversed(range(getattr(parent or self.ui, parent_layout).count())):
            if widget := getattr(parent or self.ui, parent_layout).itemAt(i).widget():
                widget: QWidget
                if type(widget) != CustomQPushButton and not delete_all:
                    continue
                layout = widget.layout()
                if not layout:
                    widget.setParent(None)
                    widget.deleteLater()
                    continue
                if (
                    layout_name
                    and layout_name == layout.objectName()
                    or not layout_name
                ):
                    layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()

        getattr(parent or self.ui, parent_layout).update()

    def login(self) -> None:
        """
        Display the login form
        """
        self.clear()
        if not hasattr(self.ui, "login_form") or not self.ui.login_form:
            self.ui.login_form = LoginLayout(theme = self.theme)
            self.ui.scroll_area.main_layout.addLayout(self.ui.login_form)
            self.ui.scroll_area.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

            # Connect signals
            self.ui.login_form.password_entry.returnPressed.connect(
                lambda: self.login_form(self.api_controller.send_login_form)
            )
            self.ui.login_form.username_entry.returnPressed.connect(
                lambda: self.login_form(self.api_controller.send_login_form)
            )
            self.ui.login_form.send_action.triggered.connect(
                lambda: self.login_form(self.api_controller.send_login_form)
            )
            self.ui.login_form.entry_action.triggered.connect(
                lambda: self.login_form(self.api_controller.send_register_form)
            )

    def login_form(self, callback) -> None:
        """
        Update the layout if login succeed
        """
        status = callback()
        if status == ApiStatus.SUCCESS:
            self._handle_sucess_gui_conn()
        elif status == ApiStatus.FORBIDDEN:
            self.ui.login_form.error_label.setText("Error: Empty username or password")
        elif status == ApiStatus.ERROR:
            self.ui.login_form.error_label.setText(
                "Error: Username or password incorect"
            )
        else:
            self.ui.login_form.error_label.setText(
                "Enable to join the server, please try again later"
            )

    def _handle_sucess_gui_conn(self):
        """
        Show GUI panels if login succeed
        """
        self._clean_gui_and_connect(update_avatar=True)
        self.show_left_layout()
        self.show_right_layout()
        self.show_footer_layout()
        self.ui.upper_widget.show()
        self.ui.header.frame_research.show()
        self.ui.header.frame_research.clearFocus()
        self.ui.header.avatar.height_, self.ui.header.avatar.width_ = 20, 20
        self.ui.header.avatar.update_picture(
            status=AvatarStatus.ACTIVATED,
            content=self.ui.users_pict[self.ui.client.user_name]
        )
        self.ui.header.avatar.show()
        self.ui.header.welcome_label.setText(f"{self.ui.client.user_name}")
        self.ui.header.welcome_label.show()
        self.ui.header.separator.show()
        
        # Signal
        self.ui.header.frame_research.textChanged.connect(self.display_users_from_research)
        hide_research = self.ui.header.frame_research.focusOutEvent
        self.ui.header.frame_research.focusOutEvent = lambda e: self.hide_research(e, hide_research)

    def _clean_gui_and_connect(self, update_avatar: bool) -> None:
        """
        Clean GUI

        Args:
            update_avatar (bool): update user avatar
        """
        self.ui.users_connected[self.ui.client.user_name] = True
        
        if self.tcp_controller.is_connected_to_server():
            self.__init_working_signals()
            self.ui.client.send_data(Commands.HELLO_WORLD, Commands.HELLO_WORLD.name)
            self.ui.login_form = None
            self.clear()
            self.api_controller.get_user_icon(update_personal_avatar=update_avatar)
            self.ui.left_nav_widget.info_disconnected_label.show()
            self.fetch_all_users_username()
            self.fetch_all_rooms()
            
            # Get older messages from the server
            dm_list = self.get_all_dm_users_username()["usernames"]

            last_message_id = self.api_controller.get_last_message_id()

            # In case of empty database
            if last_message_id:
                last_message_id = int(last_message_id)
            else:
                return
                
            for dm in dm_list:
                self.fetch_older_messages(
                    start=last_message_id + 1,
                    number=NB_OF_MESSAGES, 
                    username=dm
                )
            
            self.ui.footer_widget.reply_entry_action.triggered.connect(lambda: None)
            
    def get_all_dm_users_username(self) -> dict[str, list[str]]:
        """
        Get all dm users username
        """
        return self.api_controller.get_all_dm_users_username(self.ui.client.user_name)
            
    def fetch_older_messages(self, start: int, number: int, username: str, display=True) -> None:
        """
        Fetch older messages from the server

        Args:
            start (int): start offset
            number (int): number of messages
        """
        older_messages_list: List = self.api_controller.get_older_messages(start, number, self.ui.client.user_name, username)
        
        self.display_older_messages(older_messages_list, display, reverse=True)
        

    def hide_left_layouts_buttons(self) -> None:
        """
        Hide left button
        """
        self.ui.header.close_left_nav_button.hide()

    def show_left_layouts_buttons(self) -> None:
        """
        Show left button
        """
        self.ui.show_left_nav_button.show()
        self.ui.close_left_nav_button.show()

    def hide_right_layouts_buttons(self) -> None:
        """
        Hide right button
        """
        self.ui.header.close_right_nav_button.hide()

    def show_right_layouts_buttons(self) -> None:
        """
        Show right button
        """
        self.ui.header.show_right_nav_button.show()
        self.ui.header.close_right_nav_button.show()

    def hide_left_layout(self) -> None:
        """
        Hide left layout
        """
        if self.ui.left_nav_widget.scroll_area_avatar.isHidden():
            self.ui.left_nav_widget.slide_out()
        else:
            self.ui.left_nav_widget.slide_in()

    def show_left_layout(self) -> None:
        """
        Show left layout
        """
        self.ui.rooms_widget.main_widget.show()
        self.ui.left_nav_widget.scroll_area_avatar.show()
        self.ui.header.close_left_nav_button.show()

    def hide_right_layout(self) -> None:
        """
        Hide right layout
        """
        if self.ui.right_nav_widget.scroll_area_dm.isHidden():
            self.ui.right_nav_widget.slide_out()
        else:
            self.ui.right_nav_widget.slide_in()

    def show_right_layout(self) -> None:
        """
        Show right layout
        """
        self.ui.right_nav_widget.scroll_area_dm.show()
        self.ui.header.close_right_nav_button.show()

    def show_footer_layout(self) -> None:
        """
        Show footer layout
        """
        self.ui.footer_widget.send_widget.show()

    def hide_footer_layout(self) -> None:
        """
        Hide footer layout
        """
        self.ui.footer_widget.send_widget.hide()

    def logout(self) -> None:
        """
        Disconnect the client
        """
        # Update backend connection status
        self.api_controller.send_login_status(
            username=self.ui.client.user_name, status=False
        )
        self.api_controller.is_connected = False

        # Socket disconnection
        self.ui.client.close_connection()
        
        # Update the gui with home layout for reconnection
        self.update_gui_for_mp_layout("home")

        # Dict clear
        global_variables.user_connected.clear()
        global_variables.user_disconnect.clear()
        self.ui.users_pict.clear()
        self.ui.users_connected.clear()
        self.dm_avatar_dict.clear()
        self.ui.right_nav_widget.room_list.clear()
        self.messages_dict.clear()
        
        # Reset scroll variables
        self.api_messages_max_range = False
        self.nb_of_scroll = 1

        # UI update
        self.update_buttons()
        self.clear_avatar("user_inline", self.ui.left_nav_widget)
        self.clear_avatar("user_offline", self.ui.left_nav_widget)
        self.clear_avatar("main_layout", self.ui.rooms_widget, delete_all=True)
        self.clear_avatar("direct_message_layout", self.ui.right_nav_widget)
        self.ui.footer_widget.reply_entry_action.triggered.disconnect()
        self.ui.header.frame_research.hide()
        self.ui.header.welcome_label.hide()
        self.ui.header.separator.hide()
        self.ui.header.avatar.hide()
        self.ui.rooms_widget.main_widget.hide()

        self.ui.left_nav_widget.info_disconnected_label.hide()
        self.ui.upper_widget.hide()

        # Show login form
        self.login()

    def update_buttons(self) -> None:
        """
        Update input widgets
        """
        if self.ui.client.is_connected:
            self._set_buttons_status(False, "Enter your message to Rooms | home")
            username_label = check_str_len(self.ui.client.user_name)
            self.ui.footer_widget.user_name.setText(username_label)
        else:
            self._set_buttons_status(True, "Please login")
            self.ui.footer_widget.user_name.setText("User disconnected")
            self.ui.left_nav_widget.info_label.setText("Welcome")
            self.ui.footer_widget.user_picture.update_picture(
                status=AvatarStatus.DEACTIVATED,
                content="",
                background_color=self.theme.rgb_background_color_innactif,
            )

    def _set_buttons_status(self, activate: bool, lock_message: str) -> None:
        """
        Update buttons state

        Args:
            activate (bool): status of the button needed
            lock_message (str): message for the entry
        """
        self.ui.footer_widget.logout_button.setDisabled(activate)
        self.ui.footer_widget.entry.setDisabled(activate)
        self.ui.footer_widget.entry.setPlaceholderText(lock_message)

    def add_gui_for_mp_layout(
        self, room_name: str, icon, switch_frame: Optional[bool] = False
    ) -> None:
        if room_name not in self.ui.right_nav_widget.room_list:
            # Layout
            direct_message_widget = CustomQPushButton()
            direct_message_widget.setToolTip("Open direct message")
            direct_message_widget.setFixedHeight(50)
            direct_message_widget.setStyleSheet("border: 1px solid transparent;")
            direct_message_layout = QHBoxLayout(direct_message_widget)
            direct_message_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            direct_message_layout.setSpacing(12)
            direct_message_layout.setContentsMargins(5, 0, 5, 0)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            close_button = CustomQPushButton()
            close_button.setToolTip("Close")
            close_button.clicked.connect(direct_message_widget.deleteLater)
            close_button.setFixedHeight(30)
            close_button.setFixedWidth(30)
            close_icon = QIcon(QIcon_from_svg(Icon.CLOSE.value, color=self.theme.text_color))
            close_button.setIcon(close_icon)
            retain = close_button.sizePolicy()
            retain.setRetainSizeWhenHidden(True)
            close_button.setSizePolicy(retain)
            close_button.hide()

            def hover(event: QEvent, user_widget, close_button: CustomQPushButton):
                if isinstance(event, QEnterEvent):
                    color = self.theme.background_color
                else:
                    color = self.theme.inner_color
                style_ = """
                QWidget {{
                background-color: {color};
                border-radius: 8px;
                border: 0px solid transparent;
                }} 
                """
                user_widget.setStyleSheet(style_.format(color=color))
                close_button.show() if isinstance(
                    event, QEnterEvent
                ) else close_button.hide()

            direct_message_widget.enterEvent = partial(
                hover, user_widget=direct_message_widget, close_button=close_button
            )
            direct_message_widget.leaveEvent = partial(
                hover, user_widget=direct_message_widget, close_button=close_button
            )

            partial_room_name = check_str_len(room_name)

            btn = QLabel(partial_room_name)
            self.dm_avatar_dict[room_name] = icon
            direct_message_widget.clicked.connect(
                partial(self.update_gui_for_mp_layout, room_name)
            )

            style_ = """
            QLabel {{
            text-align: left;
            font-weight: bold;
            border-radius: 8px;
            border: 0px solid transparent;
            }} 
            """
            btn.setStyleSheet(style_.format(color=self.theme.background_color))
            btn.update()
            btn.setContentsMargins(0, 0, 0, 0)

            direct_message_layout.addWidget(icon)
            direct_message_layout.addWidget(btn)
            direct_message_layout.addWidget(
                close_button, stretch=1, alignment=Qt.AlignmentFlag.AlignRight
            )
            self.ui.right_nav_widget.room_list[room_name] = direct_message_layout
            # Insert widget after the separator
            self.ui.right_nav_widget.direct_message_layout.insertWidget(
                1,
                direct_message_widget
            )

            # --- Add Body Scroll Area --- #
            self.ui.body_gui_dict[room_name] = BodyScrollArea(name=room_name, gui_controller=self)
            
            # Add new room to the messages dict
            if room_name not in self.messages_dict.keys():
                self.messages_dict[room_name] = OrderedDict()
            
        if switch_frame:
            self.update_gui_for_mp_layout(room_name)

    def update_gui_for_mp_layout(self, room_name: str) -> None:
        """
        Update the GUI based on the room selected

        Args:
            room_name (str): room frame
        """
        # Update reply entry
        self.ui.footer_widget.reply_entry_action.triggered.emit()
    
        if room_name != "home":
            # Update avatar status with iddle
            self.update_pixmap_avatar(room_name, AvatarStatus.ACTIVATED if room_name in self.ui.users_connected.keys() else AvatarStatus.DEACTIVATED)
            self.api_controller.update_is_readed_status(
                room_name, self.ui.client.user_name
            )
        else:
            self.room_icon.update_pixmap(AvatarStatus.IDLE, background_color=self.theme.rgb_background_color_rooms)

        old_widget = self.ui.scroll_area
        old_widget.hide()

        widget = self.ui.body_gui_dict[room_name]
        index = self.ui.body_layout.indexOf(old_widget)

        self.ui.body_layout.removeWidget(old_widget)
        self.ui.body_layout.insertWidget(index, widget)

        type_room = "Rooms" if room_name == "home" else "Messages"
        self.ui.frame_name.setText(f"{type_room} \n| {room_name}")
        self.ui.frame_research.setPlaceholderText(f"Search in {type_room} | {room_name}")
        self.ui.footer_widget.entry.setPlaceholderText(
            f"Enter your message to {type_room} | {room_name}"
        )
        self.ui.scroll_area = widget
        self.ui.scroll_area.show()
        self.ui.scroll_area.scrollToBottom()

    def update_pixmap_avatar(self, room_name: str, status: AvatarStatus) -> None:
        """
        Update pixmap avatar

        Args:
            room_name (str): room frame
            status (AvatarStatus): status needed
        """
        self.dm_avatar_dict[room_name].update_pixmap(status)

    def fetch_all_users_username(self):
        """
        Fetch all users picture from backend
        """
        usernames: List[str] = self.ui.backend.get_all_users_username()
        for username in usernames:
            self.api_controller.add_sender_picture(username)

    def fetch_all_rooms(self):
        """
        Fetch all rooms
        """
        room_widget = CustomQPushButton()
        room_widget.setFixedHeight(50)
        room_layout = QHBoxLayout(room_widget)
        room_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        room_layout.setContentsMargins(0, 0, 0, 0)

        divider = QIcon(QIcon_from_svg(Icon.SEPARATOR_HORIZ.value, color=self.theme.background_color))
        divider_label = QLabel()
        divider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        divider_label.setPixmap(divider.pixmap(20, 20))

        self.room_icon = AvatarLabel(
            content=ImageAvatar.ROOM.value,
            status=AvatarStatus.DEACTIVATED,
        )
        self.room_icon.setToolTip("Display home room")

        self.room_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        room_widget.clicked.connect(lambda: self.update_gui_for_mp_layout("home"))

        def hover(event: QEvent, user_widget):
            if isinstance(event, QEnterEvent):
                color = self.theme.background_color
            else:
                color = self.theme.rooms_color
            style_ = """
            QWidget {{
            font-weight: bold;
            text-align: center;
            background-color: {color};
            border-radius: 8px;
            border: 1px solid transparent;
            }} 
            """
            user_widget.setStyleSheet(style_.format(color=color))

        room_widget.enterEvent = partial(hover, user_widget=room_widget)
        room_widget.leaveEvent = partial(hover, user_widget=room_widget)

        style_ = """
            QWidget {{
            font-weight: bold;
            text-align: center;
            border: 1px solid transparent;
            }} 
            """
        room_widget.setStyleSheet(style_.format())

        room_layout.addWidget(self.room_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        self.ui.rooms_widget.main_layout.addWidget(room_widget)
        self.ui.rooms_widget.main_layout.addWidget(divider_label)
        
    def focus_in_message(self, message: MessageLayout) -> None:
        """
        Focus in a message

        Args:
            message (MessageLayout): message layout
        """
        style_sheet_main = message.main_widget.styleSheet()
        style_sheet_left = message.left_widget.styleSheet()
        
        self.update_stylesheet_with_reply(message)
        
        def callback(message: MessageLayout, styleSheet_main: str, styleSheet_left):
            message.main_widget.setStyleSheet(
                styleSheet_main
            )
            message.left_widget.setStyleSheet(
                styleSheet_left
            )
            self.is_focused = False
        self.ui.scroll_area.ensureWidgetVisible(message.main_widget)
        
        QTimer.singleShot(1000, partial(callback, message, style_sheet_main, style_sheet_left))
        
    def update_stylesheet_with_reply(
        self, message: MessageLayout
    ) -> None:
        message.main_widget.setStyleSheet(
            f"color: {self.theme.title_color};\
            margin-bottom: 1px;\
            margin-right: 2px;\
            background-color: {self.theme.inner_color};\
            border-left: 0px solid;"
        )
        message.left_widget.setStyleSheet(
            "border-left: 0px solid"
        )
        
    def update_stylesheet_with_focus_event(
        self, message: MessageLayout, border_color: str
    ) -> None:
        message.main_widget.setStyleSheet(
            f"color: {self.theme.title_color};\
            margin-bottom: 1px;\
            margin-right: 2px;\
            background-color: {self.theme.inner_color};"
        )
        message.left_widget.setStyleSheet(
            f"""QWidget{{
                border-left: 2px solid;\
                border-color: {border_color};
            }}
            AvatarLabel{{
                border: 0px solid;
            }}"""
        )
        
    def reply_to_message(self, message: MessageLayout) -> None:
        """
        Reply to a message

        Args:
            message_id (int): message id
        """
        # Update reply entry
        self.ui.footer_widget.reply_entry_action.triggered.emit()
        
        style_sheet_main = message.main_widget.styleSheet()
        style_sheet_left = message.left_widget.styleSheet()

        self.update_stylesheet_with_focus_event(message, border_color=GenericColor.RED.value)

        def callback(message: MessageLayout, older_room_name: str, styleSheet_main: str, styleSheet_left: str):
            message.main_widget.setStyleSheet(
                styleSheet_main
            )
            message.left_widget.setStyleSheet(
                styleSheet_left
            )
            global_variables.reply_id = ""
            older_room_name = older_room_name.replace("\n", "")
            self.ui.footer_widget.entry.setPlaceholderText(older_room_name)
            self.ui.footer_widget.reply_entry_action.setVisible(False)
            
        older_room_name = f"Enter your message to {self.ui.frame_name.text()}"
        self.ui.footer_widget.entry.setPlaceholderText(
            f"Reply to {message.username_label}"
        )
        self.ui.footer_widget.entry.setFocus()
        self.ui.footer_widget.reply_entry_action.triggered.connect(
            partial(callback, message, older_room_name, style_sheet_main, style_sheet_left)
        )
        global_variables.reply_id = f"#{message.message_id}/"

        self.ui.footer_widget.reply_entry_action.setVisible(True)

    def send_emot_react(self, cmd: Commands, messageId: int, react_nb: int) -> None:
        """
        Send emot message to the server

        Args:
            cmd (Commands): Commands.RM_REACT ou Commands.ADD_REACT
            messageId (int): id of the message
            react_nb (int): number of reaction
        """
        receiver: str = self.ui.scroll_area.objectName()

        self.ui.client.send_data(
            cmd,
            ";".join([str(messageId), str(react_nb)]),
            receiver=receiver,
        )
        
    def display_users_from_research(self):
        """
        Display users list from research
        """
        # Move the list under the research bar
        x = self.ui.header.frame_research.x()
        y = self.ui.header.frame_research.y() + self.ui.header.frame_research.height()
        self.ui.header.frame_research_list.move(x, y)
        self.ui.header.frame_research_list.clear()
        
        # Get the text from the research bar
        text_from_research = self.ui.header.frame_research.text()
        if not text_from_research:
            self.ui.header.frame_research_list.hide()
            self.ui.header.frame_research.reset_layout()
            return
        
        # Get all users
        users = self.ui.users_pict.keys()
        
        def hover(event: QEvent, user_widget) -> None:
            if isinstance(event, QEnterEvent):
                color = self.theme.background_color
            else:
                color = self.theme.search_color

            style_ = """
            QWidget {{
            background-color: {color};
            border-radius: 8px;
            border: 0px solid {color};
            }} 
            """
            user_widget.setStyleSheet(style_.format(color=color))
            user_widget.update()
        
        nb_users = 0
        for user in users:
            # If the user is in the research text bar
            if text_from_research in user and user != "server" and user != self.ui.client.user_name:
                nb_users+=1
                self.ui.header.frame_research_list.show()
                self.ui.header.frame_research.update_layout()
                user_widget = CustomQPushButton()
                content = global_variables.user_connected[user][0] if user in global_variables.user_connected else global_variables.user_disconnect[user][0]
                dm_pic = AvatarLabel(
                    content=content, 
                    status=AvatarStatus.IDLE,
                )
                
                def callback(user, dm_pic):
                    self.add_gui_for_mp_layout(user, dm_pic, True)
                    self.ui.header.frame_research.clear()
                    self.ui.header.frame_research_list.hide()
                    self.ui.header.frame_research.reset_layout()
                    self.ui.header.frame_research.clearFocus()
                    
                user_widget.clicked.connect(
                    partial(callback, user, dm_pic)
                )
                user_widget.enterEvent = partial(
                    hover, user_widget=user_widget
                )
                user_widget.leaveEvent = partial(
                    hover, user_widget=user_widget
                )
                user_widget.setContentsMargins(5, 0, 0, 0)
                user_widget.setFixedHeight(30)
                user_layout = QHBoxLayout(user_widget)
                
                user_pic = AvatarLabel(
                    content=content, 
                    status=AvatarStatus.IDLE,
                    height=20,
                    width=20
                )
                
                user_layout.setContentsMargins(0, 0, 0, 0)
                user = check_str_len(user)
                label = QLabel(user)
                label.setStyleSheet(
                    f"font-weight: bold;\
                    background-color: transparent;\
                    color: {self.theme.title_color};"
                )
                user_layout.addWidget(user_pic)
                user_layout.addWidget(label)
                user_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
                item = QListWidgetItem()
                self.ui.header.frame_research_list.addItem(item)
                self.ui.header.frame_research_list.setItemWidget(item, user_widget)
        if not nb_users:
            self.ui.header.frame_research_list.hide()
            self.ui.header.frame_research.reset_layout()

        self.ui.header.frame_research_list.setFixedHeight(50 * 3 if nb_users > 0 else 0)
        
    def hide_research(self, event, hide_research):
        hide_research(event)
        if self.ui.header.frame_research_list.hasFocus():
            return
        self.ui.header.frame_research.clear()
        self.ui.header.frame_research_list.hide()
        self.ui.header.frame_research.reset_layout()
        
    def display_theme_board(self):
        """
        Display theme board
        """
        if hasattr(self, "theme_board") and self.theme_board.isVisible():
            return
        self.theme_board = QWidget()

        height = 250
        self.theme_board.setFixedSize(QSize(240, height))
        self.theme_board.move(
            self.ui.footer_widget.bottom_right_widget.x() + 5, 
            self.ui.footer_widget.send_widget.y() - height + self.ui.footer_widget.bottom_right_widget.height() - 5
        )
        self.theme_board.setContentsMargins(0, 0, 0, 0)
        self.theme_board.setStyleSheet(
            f"background-color: {self.theme.background_color};\
            border-radius: 8px;\
            border: 1px solid {self.theme.nav_color};"
        )
        theme_board_layout = QVBoxLayout(self.theme_board)
        theme_board_layout.setContentsMargins(15, 15, 15, 15)
        theme_board_layout.setSpacing(5)
        list_theme_label = [
            QLabel(color_name.capitalize().replace("_color", ""))
            for color_name in self.theme.list_colors
        ]
        list_theme_line_edit = [
            CustomQLineEdit(
                text=getattr(self.theme, self.theme.list_colors[i]),
                place_holder_text="#",
                radius=4
            ) for i in range(len(list_theme_label))
        ]

        for label in list_theme_label:
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setStyleSheet(
                f"color: {self.theme.title_color};\
                font-weight: bold;\
                border: 0px solid"
            )
        for line_edit in list_theme_line_edit:
            line_edit.setFixedSize(QSize(120, 15))
            line_edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        for label, line_edit in zip(list_theme_label, list_theme_line_edit):
            widget = QWidget()
            widget.setStyleSheet(
                "border: 0px solid;"
            )
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(5, 0, 5, 0)
            layout.setSpacing(0)
            layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(line_edit, alignment=Qt.AlignmentFlag.AlignLeft)
            theme_board_layout.addWidget(widget)

        # Update layout
        update_widget = QWidget()
        update_widget.setStyleSheet(
            f"border: 0px solid;\
            background-color: {self.theme.search_color};"
        )
        update_layout = QHBoxLayout(update_widget)
        update_layout.setContentsMargins(5, 5, 5, 5)

        # Update theme button
        theme_icon = QIcon(QIcon_from_svg(Icon.SWITCH_COLOR.value, color=self.theme.title_color))
        update_button = self._create_theme_button(
            "Custom", 80, theme_icon
        )
        update_button.clicked.connect(
            partial(self.theme.create_custom_theme, self, list_theme_line_edit)
        )
        # Black theme
        black_icon = QIcon(QIcon_from_svg(Icon.STATUS.value, color="#000000"))
        black_theme_button = self._create_theme_button(
            "", 30, black_icon
        )
        black_theme_button.clicked.connect(
            partial(self.theme.switch_theme, self, Themes.ThemeColor.BLACK)
        )
        
        # White theme
        white_icon = QIcon(QIcon_from_svg(Icon.STATUS.value, color="#ffffff"))
        white_theme_button = self._create_theme_button(
            "", 30, white_icon
        )
        white_theme_button.clicked.connect(
            partial(self.theme.switch_theme, self, Themes.ThemeColor.WHITE)
        )
        # close button
        close_icon = QIcon(QIcon_from_svg(Icon.CLOSE.value, color=GenericColor.RED.value))
        close_button = self._create_theme_button("", 30, close_icon)
        close_button.clicked.connect(self.theme_board.hide)
        
        update_layout.addWidget(update_button)
        update_layout.addWidget(black_theme_button)
        update_layout.addWidget(white_theme_button)
        update_layout.addWidget(close_button)
        
        theme_board_layout.addWidget(update_widget)

        self.ui.main_layout.addChildWidget(self.theme_board)
        self.theme_board.setFocus()
        
    def _create_theme_button(self, arg0, arg1, arg2):
        result = CustomQPushButton(arg0)
        result.setFixedSize(QSize(arg1, 30))
        result.setIcon(arg2)

        return result
    
    def update_user_description(self):
        self.api_controller.update_user_description(
            self.ui.client.user_name,
            self.status_widget.toPlainText()
        )
        self.user_profile_widget.hide()
            
            
        

        