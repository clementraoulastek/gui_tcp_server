import logging
import re
from threading import Thread
import time
from typing import List, Optional, Union
from src.client.client import Client
from src.client.controller.worker import Worker
from src.client.core.qt_core import (
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
    QSizePolicy
)
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


class GuiController:
    def __init__(
        self,
        ui,
        messages_dict: dict[str, MessageLayout],
        last_message_id: int,
        api_controller: ApiController,
        tcp_controller: TcpServerController,
        theme: Themes
    ) -> None:
        self.ui = ui
        self.theme = theme
        self.messages_dict = messages_dict
        self.last_message_id = last_message_id
        self.api_controller = api_controller
        self.tcp_controller = tcp_controller
        self.dm_avatar_dict: dict[str, AvatarLabel] = {}
        

    def __init_working_signals(self) -> None:
        """
        Init signals for incoming messages
        """
        # Worker for incoming messages
        self.read_worker = Worker(parent=self.ui)
        self.read_worker.signal.connect(self.__diplay_coming_message_on_gui)
        self.read_worker.start()

        # Worker for incoming avatar
        self.read_avatar_worker = Worker(parent=self.ui)
        self.read_avatar_worker.signal.connect(self.__update_gui_with_connected_avatar)
        self.read_avatar_worker.start()

        # Worker for outdated avatar
        self.read_outdated_avatar_worker = Worker(parent=self.ui)
        self.read_outdated_avatar_worker.signal.connect(
            self.__update_gui_with_disconnected_avatar
        )
        self.read_outdated_avatar_worker.start()

        # Worker for react
        self.read_react_message_worker = Worker(parent=self.ui)
        self.read_react_message_worker.signal.connect(
            self.__update_react_message_on_gui
        )
        self.read_react_message_worker.start()

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
        messsage_id: Optional[Union[int, None]] = None,
        nb_react: Optional[int] = 0,
        date: Optional[str] = "",
        response_model: Optional[Union[MessageLayout, None]] = None,
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

        # Update the last message id
        if messsage_id:
            self.last_message_id = messsage_id
        else:
            self.last_message_id += 1

        message = MessageLayout(
            self.ui.main_widget,
            self,
            comming_msg,
            content=self.ui.users_pict[sender],
            message_id=self.last_message_id,
            nb_react=nb_react,
            date=date,
            response_model=response_model,
        )
        self.ui.body_gui_dict[frame_name].main_layout.addLayout(message)

        # Update the dict
        self.messages_dict[self.last_message_id] = message
        self.ui.footer_widget.entry.clear()

        QTimer.singleShot(0, self.__update_scroll_bar)

    def display_older_messages(self) -> None:
        """
        Update gui with older messages
        """
        sender_list: list[str] = []

        # Get older messages from the server
        messages_dict = self.api_controller.get_older_messages()

        for message in messages_dict:
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

            # TODO: Avoid to fetch all messages
            if (
                receiver != "home"
                and sender != self.ui.client.user_name
                and receiver != self.ui.client.user_name
            ):
                self.last_message_id = message_id
                continue

            message_model = self.messages_dict[response_id] if response_id else None

            # Add a special char to handle the ":" in the message
            message = message.replace(Client.SPECIAL_CHAR, ":")

            # Add sender to a list to avoid multiple avatar update
            if sender not in sender_list:
                sender_list.append(sender)

            # Dipslay message on gui on the home frame
            if receiver == "home":
                self.diplay_self_message_on_gui(
                    sender,
                    message,
                    frame_name="home",
                    messsage_id=message_id,
                    nb_react=int(reaction_nb),
                    date=date,
                    response_model=message_model,
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
                    messsage_id=message_id,
                    nb_react=int(reaction_nb),
                    date=date,
                    response_model=message_model,
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

        if global_variables.comming_msg["id"] != "server":
            self.last_message_id += 1

        message_model = None
        message = global_variables.comming_msg["message"]

        if response_id := global_variables.comming_msg["response_id"]:
            response_id = int(response_id)
            message_model = self.messages_dict[response_id]

        message = MessageLayout(
            self.ui.main_widget,
            self,
            global_variables.comming_msg,
            content=self.ui.users_pict[global_variables.comming_msg["id"]],
            message_id=self.last_message_id
            if global_variables.comming_msg["id"] != "server"
            else None,
            response_model=message_model,
        )
        if global_variables.comming_msg["id"] != "server":
            self.messages_dict[self.last_message_id] = message

        if global_variables.comming_msg["receiver"] == "home":
            dict_key = "home"
        else:
            dict_key = global_variables.comming_msg["id"]

        if dict_key != "home":
            self.add_gui_for_mp_layout(
                dict_key,
                AvatarLabel(
                    content=self.ui.users_pict[global_variables.comming_msg["id"]],
                    status=AvatarStatus.DM,
                ),
            )
            # Update avatar status with DM circle popup
            self.dm_avatar_dict[dict_key].update_pixmap(AvatarStatus.DM, background_color=self.theme.rgb_background_color_actif)
         
        self.ui.body_gui_dict[dict_key].main_layout.addLayout(message)

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
            global_variables.comming_msg["id"],
            global_variables.comming_msg["reaction"],
        )
        message: MessageLayout = self.messages_dict[int(message_id)]
        message.update_react(int(nb_reaction))

        # Reset global variables
        global_variables.comming_msg["reaction"], global_variables.comming_msg["id"] = (
            "",
            "",
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
                payload = payload.split(":")[-1].replace(" ", "")
                payload_list = payload.split(";")
                message_id, nb_reaction = payload_list[0], payload_list[1]
                global_variables.comming_msg["id"] = message_id
                global_variables.comming_msg["reaction"] = nb_reaction
            else:
                self.__handle_message(payload)
        elif header == Commands.LAST_ID.value:
            self.last_message_id += 1

    def __handle_message(self, payload: str) -> None:
        """
        Get the message and update global variables

        Args:
            payload (str): payload of the message
        """
        payload_fields = payload.split(":")
        message_id = payload_fields[0]
        receiver = payload_fields[1]
        message = payload_fields[2]

        if len(payload_fields) == 4:
            response_id = payload_fields[3]
            global_variables.comming_msg["response_id"] = response_id

        global_variables.comming_msg["id"] = message_id
        global_variables.comming_msg["receiver"] = receiver.replace(" ", "")
        global_variables.comming_msg["message"] = message.replace("$replaced$", ":")

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
        
        if id_ in self.dm_avatar_dict.keys():
            self.dm_avatar_dict[id_].update_pixmap(AvatarStatus.DEACTIVATED, background_color=self.theme.rgb_background_color_innactif)

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
            with global_variables.user_disconnect_lock:
                user_disconnect.pop(id_)

        if id_ in self.dm_avatar_dict.keys():
            self.dm_avatar_dict[id_].update_pixmap(AvatarStatus.ACTIVATED)

        # Add the user icon to the connected layout
        if id_ not in self.ui.users_connected.keys():
            self.ui.users_connected[id_] = True
            self.api_controller.update_user_connected(id_, self.ui.users_pict[id_])

    def update_user_icon(self) -> None:
        """
        Update user icon
        """
        username = self.ui.client.user_name
        if self.ui.backend.send_user_icon(username, None):
            self.clear_avatar("user_inline", self.ui, f"{username}_layout")
            self.api_controller.get_user_icon(update_personal_avatar=True)

    def __update_gui_with_connected_avatar(self) -> None:
        """
        Callback to update gui with input connected avatar
        """
        for user, data in global_variables.user_connected.items():
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
            
            if username in self.dm_avatar_dict.keys():
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

    # TODO: Avoid code duplication
    def __update_gui_with_disconnected_avatar(self) -> None:
        """
        Callback to update gui with input disconnected avatar
        """
        with global_variables.user_disconnect_lock:
            for user, data in global_variables.user_disconnect.items():
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
            self.display_older_messages()

            self.ui.footer_widget.reply_entry_action.triggered.connect(lambda: None)

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
            self.ui.left_nav_widget.scroll_area_avatar.show()
        else:
            self.ui.left_nav_widget.scroll_area_avatar.hide()

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
            self.ui.right_nav_widget.scroll_area_dm.show()
        else:
            self.ui.right_nav_widget.scroll_area_dm.hide()

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
            self.ui.body_gui_dict[room_name] = BodyScrollArea(name=room_name)
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

        room_icon = AvatarLabel(
            content=ImageAvatar.ROOM.value,
            status=AvatarStatus.DEACTIVATED,
        )
        room_icon.setToolTip("Display home room")

        room_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
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

        room_layout.addWidget(room_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        self.ui.rooms_widget.main_layout.addWidget(room_widget)
        self.ui.rooms_widget.main_layout.addWidget(divider_label)
        
    def focus_in_message(self, message: MessageLayout) -> None:
        """
        Focus in a message

        Args:
            message (MessageLayout): message layout
        """
        self.update_stylesheet_with_focus_event(message)
        
        def callback(message: MessageLayout):
            message.main_widget.setStyleSheet(
                f"color: {self.theme.title_color};\
                margin-bottom: 1px;\
                margin-right: 2px;\
                background-color: transparent;\
                border: 0px"
            )
            message.left_widget.setStyleSheet(
                "border-left: 0px solid;"
            )
        
        self.ui.scroll_area.ensureWidgetVisible(message.main_widget)
        
        QTimer.singleShot(1000, partial(callback, message))
        
    def update_stylesheet_with_focus_event(
        self, message: MessageLayout
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
                border-color: {self.theme.emoji_color};
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

        self.update_stylesheet_with_focus_event(message)

        def callback(message: MessageLayout, older_room_name: str):
            message.main_widget.setStyleSheet(
                f"color: {self.theme.title_color};\
                margin-bottom: 1px;\
                margin-right: 2px;\
                background-color: transparent;\
                border: 0px"
            )
            message.left_widget.setStyleSheet(
                "border-left: 0px solid;"
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
            partial(callback, message, older_room_name)
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
            border: 1px solid {self.theme.inner_color};"
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
            
            
        

        