import logging
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
)
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.layout.body_scroll_area import BodyScrollArea
from src.client.view.layout.message_layout import MessageLayout
from src.client.view.tools.graphical_effects import widget_shadow
from src.tools.commands import Commands
from src.client.view.layout.login_layout import LoginLayout
from src.client.view.customWidget.AvatarQLabel import AvatarStatus, AvatarLabel
from src.client.core.qt_core import QHBoxLayout, QLabel, QThread, Signal, Qt
from src.tools.utils import Color, Icon, ImageAvatar, check_str_len
from src.client.controller.api_controller import ApiController
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
    ) -> None:
        self.ui = ui
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
        id_sender: str,
        message: str,
        frame_name: Optional[Union[str, None]] = None,
        messsage_id: Optional[Union[int, None]] = None,
        nb_react: Optional[int] = 0,
        date: Optional[str] = "",
    ) -> None:
        """
        Display message on gui and clear the message entry

        Args:
            id_sender (str): username
            message (str): message
            frame_name (Optional[Union[str, None]], optional): layout name. Defaults to None.
            messsage_id (Optional[Union[int, None]], optional): message id. Defaults to None.
            nb_react (Optional[int], optional): number of reactions. Defaults to 0.
            date (Optional[str], optional): date to display. Defaults to "".
        """
        comming_msg: dict[str, str] = {"id": id_sender, "message": message}
        
        # Update the last message id 
        if messsage_id:
            self.last_message_id = messsage_id
        else:
            self.last_message_id += 1
            
        message = MessageLayout(
            self.ui.main_widget,
            self,
            comming_msg,
            content=self.ui.users_pict[id_sender],
            message_id=self.last_message_id,
            nb_react=nb_react,
            date=date,
        )
        self.ui.body_gui_dict[frame_name].main_layout.addLayout(message)
        
        # Update the dict
        self.messages_dict[self.last_message_id] = message
        self.ui.footer_widget.entry.clear()

    def display_older_messages(self) -> None:
        """
        Update gui with older messages
        """
        sender_list: list[str] = []
        
        # Get older messages from the server
        messages_dict = self.api_controller.get_older_messages()
        for message in messages_dict:
            message_id, sender, receiver, message, reaction_nb, date, is_readed = (
                message["message_id"],
                message["sender"],
                message["receiver"],
                message["message"],
                message["reaction_nb"],
                message["created_at"],
                message["is_readed"],
            )
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
                )
            # Display message on gui on the direct message frame
            elif self.ui.client.user_name in (sender, receiver):
                direct_message_name = (
                    receiver if sender == self.ui.client.user_name else sender
                )
                icon = AvatarLabel(
                    content=self.ui.users_pict[direct_message_name],
                    status=AvatarStatus.IDLE,
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
            
        message = MessageLayout(
            self.ui.main_widget,
            self,
            global_variables.comming_msg,
            content=self.ui.users_pict[global_variables.comming_msg["id"]],
            message_id=self.last_message_id
            if global_variables.comming_msg["id"] != "server"
            else None,
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
            self.dm_avatar_dict[dict_key].update_pixmap(AvatarStatus.DM)

        self.ui.body_gui_dict[dict_key].main_layout.addLayout(message)
        (
            global_variables.comming_msg["id"],
            global_variables.comming_msg["receiver"],
            global_variables.comming_msg["message"],
        ) = ("", "", "")

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
                self.ui.left_nav_widget.info_label.setText(f"Users online   |   {nb_of_users}")
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
                message_id, receiver, message = payload.split(":")
                global_variables.comming_msg["id"] = message_id
                global_variables.comming_msg["receiver"] = receiver.replace(" ", "")
                global_variables.comming_msg["message"] = message.replace(
                    "$replaced$", ":"
                )
        else:
            (
                global_variables.comming_msg["id"],
                global_variables.comming_msg["receiver"],
                global_variables.comming_msg["message"],
            ) = ("unknown", "unknown", payload)

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
        self.clear_avatar("user_inline", self.ui, f"{id_}_layout")
        self.api_controller.add_sender_picture(id_)
        user_disconnect[id_] = [user_connected[id_][0], False]
        self.ui.users_connected.pop(id_)

    def __add_sender_avatar(
        self, payload: str, user_disconnect: dict[str, List[Union[str, bool]]]
    ) -> None:
        """
        Add the user icon to the connected layout from a HELLO WORLD message

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
            self.clear_avatar("user_offline", self.ui.left_nav_widget, f"{id_}_layout_disconnected")
            user_disconnect.pop(id_)
            
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
            user_layout.setSpacing(10)
            user_layout.setContentsMargins(0, 0, 0, 0)
            username = user
            user_layout.setObjectName(f"{username}_layout")
            content = data[0]
            
            def hover(event: QEvent, user_widget):
                if isinstance(event, QEnterEvent):
                    color = Color.DARK_GREY.value
                else:
                    color = "transparent"
                style_ = """
                QWidget {{
                background-color: {color};
                border-radius: none;
                border: 0px solid;
                }} 
                """
                user_widget.setStyleSheet(style_.format(color=color))
                
            # Create avatar label
            user_pic, dm_pic = AvatarLabel(
                content=content, status=AvatarStatus.ACTIVATED
            ), AvatarLabel(content=content, status=AvatarStatus.IDLE)

            # Update picture alignment
            user_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dm_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            user_pic.setStyleSheet("border: 0px;")
            
            # Avoid gui troubles with bigger username
            username_label = check_str_len(username)
            user_name = QLabel(username_label)
            
            # StyleSheet
            style_ = """
            QLabel {{
            text-align: left;
            font-weight: bold;
            border-radius: none;
            border: none;
            }} 
            """
            # Add user menu
            if username != self.ui.client.user_name:
                user_widget.enterEvent = partial(hover, user_widget=user_widget)
                user_widget.leaveEvent = partial(hover, user_widget=user_widget)
                
                user_widget.clicked.connect(
                    partial(self.add_gui_for_mp_layout, username, dm_pic, True)
                )
                hover = """
                QPushButton:hover {{
                text-decoration: underline;
                }}
                """
                style_ = f"{style_}{hover}"
            user_name.setStyleSheet(style_.format())
            
            # Add widgets to the layout
            user_layout.addWidget(user_pic)
            user_layout.addWidget(user_name)
            self.ui.left_nav_widget.user_inline.addWidget(user_widget)

    def __update_gui_with_disconnected_avatar(self) -> None:
        """
        Callback to update gui with input disconnected avatar
        """
        for user, data in global_variables.user_disconnect.items():
            if data[1] == True:
                continue
            # Layout
            user_widget = CustomQPushButton()
            user_widget.setFixedHeight(50)
            style_ = """
            QWidget {{
            border-radius: none;
            border: 0px solid;
            }} 
            """
            
            def hover(event: QEvent, user_widget):
                if isinstance(event, QEnterEvent):
                    color = Color.DARK_GREY.value
                else:
                    color = "transparent"
                style_ = """
                QWidget {{
                background-color: {color};
                border-radius: none;
                border: 0px solid;
                }} 
                """
                user_widget.setStyleSheet(style_.format(color=color))
            
            user_widget.enterEvent = partial(hover, user_widget=user_widget)
            user_widget.leaveEvent = partial(hover, user_widget=user_widget)
            user_widget.setStyleSheet(style_.format())
            
            user_widget.setContentsMargins(0, 0, 0, 0)
            user_layout = QHBoxLayout(user_widget)
            user_layout.setSpacing(10)
            user_layout.setContentsMargins(0, 0, 0, 0)
            username = user
            content = data[0]
            user_layout.setObjectName(f"{username}_layout_disconnected")
            
            # Create avatar label
            user_pic, dm_pic = AvatarLabel(
                content=content, status=AvatarStatus.DEACTIVATED
            ), AvatarLabel(content=content, status=AvatarStatus.IDLE)
            
            # Update picture alignment
            user_pic.set_opacity(0.2)
            user_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dm_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            user_pic.setStyleSheet(
                f"border: 0px solid;\
                border-color: {Color.GREY.value};"
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
            border-radius: 0px;
            border: 1px solid;
            border-color: {color};
            }}
            """
            user_name.setStyleSheet(style_.format(color="transparent"))
            
            # Add widgets to the layout
            user_layout.addWidget(user_pic)
            user_layout.addWidget(user_name)
            self.ui.left_nav_widget.user_offline.addWidget(user_widget)
            
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
        self, parent_layout: QLayout, parent = None, layout_name: Optional[Union[QHBoxLayout, None]] = None
    ) -> None:
        """
        Clear avatars from the layout

        Args:
            parent_layout (QLayout): parent layout
            layout_name (Optional[Union[QHBoxLayout, None]], optional): layout name. Defaults to None.
        """
        for i in reversed(range(getattr(parent or self.ui, parent_layout).count())):
            if widget := getattr(parent or self.ui, parent_layout).itemAt(i).widget():
                widget: QWidget
                if not type(widget) == QWidget:
                    continue
                layout = widget.layout()
                if (
                    layout_name
                    and layout_name == layout.objectName()
                    or not layout_name
                ):
                    widget.setParent(None)

        getattr(parent or self.ui, parent_layout).update()


    def login(self) -> None:
        """
        Display the login form
        """
        self.clear()
        if not hasattr(self.ui, "login_form") or not self.ui.login_form:
            self.ui.login_form = LoginLayout()
            self.ui.scroll_area.main_layout.addLayout(self.ui.login_form)
            self.ui.scroll_area.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.ui.login_form.password_entry.returnPressed.connect(self.login_form)
            self.ui.login_form.send_button.clicked.connect(self.login_form)
            self.ui.login_form.register_button.clicked.connect(self.register_form)

    def login_form(self) -> None:
        """
        Update the layout if login succeed
        """
        if status := self.api_controller.send_login_form():
            self._clean_gui_and_connect(update_avatar=True)
            self.show_left_layout()
            self.show_right_layout()
            self.show_footer_layout()
            self.ui.upper_widget.show()
            self.update_gui_for_mp_layout("home")
        elif status == False:
            self.ui.login_form.error_label.setText("Error: Empty username or password")
        else:
            self.ui.login_form.error_label.setText(
                "Error: Username or password incorect"
            )

    def register_form(self) -> None:
        """
        Update the layout if register succeed
        """
        if status := self.api_controller.send_register_form():
            self._clean_gui_and_connect(update_avatar=True)
            self.show_left_layout()
            self.show_right_layout()
            self.show_footer_layout()
            self.ui.upper_widget.show()
        elif status == False:
            self.ui.login_form.error_label.setText("Error: Empty username or password")
        else:
            self.ui.login_form.error_label.setText(
                "Error: Username or password incorect"
            )

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
            self.ui.left_nav_widget.message_label.hide()
            self.ui.left_nav_widget.info_disconnected_label.show()
            self.fetch_all_users_username()
            self.display_older_messages()

    def hide_left_layouts_buttons(self) -> None:
        """
        Hide left button
        """
        self.ui.header.show_left_nav_button.hide()
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
        self.ui.header.show_right_nav_button.hide()
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
        self.ui.left_nav_widget.scroll_area_avatar.hide()
        self.ui.header.close_left_nav_button.hide()
        self.ui.header.show_left_nav_button.show()

    def show_left_layout(self) -> None:
        """
        Show left layout
        """
        self.ui.left_nav_widget.scroll_area_avatar.show()
        self.ui.header.show_left_nav_button.hide()
        self.ui.header.close_left_nav_button.show()

    def hide_right_layout(self) -> None:
        """
        Hide right layout
        """
        self.ui.right_nav_widget.scroll_area_dm.hide()
        self.ui.header.close_right_nav_button.hide()
        self.ui.header.show_right_nav_button.show()

    def show_right_layout(self) -> None:
        """
        Show right layout
        """
        self.ui.right_nav_widget.scroll_area_dm.show()
        self.ui.header.show_right_nav_button.hide()
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
        self.api_controller.send_login_status(username=self.ui.client.user_name, status=False)
        self.api_controller.is_connected = False
        
        # Socket disconnection
        self.ui.client.close_connection()

        # Dict clear
        global_variables.user_connected.clear()
        global_variables.user_disconnect.clear()
        self.ui.users_pict = {"server": ImageAvatar.SERVER.value}
        self.ui.users_connected.clear()
        self.ui.right_nav_widget.room_list.clear()

        # UI update
        self.update_buttons()
        self.clear_avatar("user_inline", self.ui.left_nav_widget)
        self.clear_avatar("user_offline", self.ui.left_nav_widget)
        self.clear_avatar("direct_message_layout", self.ui.right_nav_widget)

        self.ui.left_nav_widget.message_label.show()
        self.ui.left_nav_widget.info_disconnected_label.hide()
        self.ui.upper_widget.hide()

        self.login()

    def update_buttons(self) -> None:
        """
        Update input widgets
        """
        if self.ui.client.is_connected:
            self._set_buttons_status(False, "Enter your message")
            username_label = check_str_len(self.ui.client.user_name)
            self.ui.footer_widget.user_name.setText(username_label)
        else:
            self._set_buttons_status(True, "Please login")
            self.ui.footer_widget.user_name.setText("User disconnected")
            self.ui.left_nav_widget.info_label.setText("Welcome")
            self.ui.footer_widget.user_picture.update_picture(
                status=AvatarStatus.DEACTIVATED, content=""
            )

    def _set_buttons_status(self, activate: bool, lock_message: str) -> None:
        """
        Update buttons state

        Args:
            activate (bool): status of the button needed
            lock_message (str): message for the entry
        """
        self.ui.footer_widget.custom_user_button.setDisabled(activate)
        self.ui.footer_widget.logout_button.setDisabled(activate)
        self.ui.footer_widget.send_button.setDisabled(activate)
        self.ui.footer_widget.entry.setDisabled(activate)
        self.ui.footer_widget.entry.setPlaceholderText(lock_message)

    def add_gui_for_mp_layout(
        self, room_name: str, icon, switch_frame: Optional[bool] = False
    ) -> None:
        if room_name not in self.ui.right_nav_widget.room_list:
            # Layout
            direct_message_widget = CustomQPushButton()
            direct_message_widget.setFixedHeight(50)
            direct_message_widget.setStyleSheet("border: 0px solid;")
            direct_message_layout = QHBoxLayout(direct_message_widget)
            direct_message_layout.setSpacing(10)
            direct_message_layout.setContentsMargins(0, 0, 0, 0)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            def hover(event: QEvent, user_widget):
                if isinstance(event, QEnterEvent):
                    color = Color.DARK_GREY.value
                else:
                    color = "transparent"
                style_ = """
                QWidget {{
                background-color: {color};
                border-radius: none;
                border: 0px solid;
                }} 
                """
                user_widget.setStyleSheet(style_.format(color=color))
            
            direct_message_widget.enterEvent = partial(hover, user_widget=direct_message_widget)
            direct_message_widget.leaveEvent = partial(hover, user_widget=direct_message_widget)
            
            partial_room_name = check_str_len(room_name)
            
            btn = QLabel(partial_room_name)
            self.dm_avatar_dict[room_name] = icon
            direct_message_widget.clicked.connect(partial(self.update_gui_for_mp_layout, room_name))
            
            style_ = """
            QLabel {{
            text-align: left;
            font-weight: bold;
            border-radius: none;
            border: 0px solid;
            }} 
            """
            btn.setStyleSheet(style_.format(color=Color.GREY.value))
            btn.update()
            btn.setContentsMargins(0, 0, 0, 0)
            
            direct_message_layout.addWidget(icon)
            direct_message_layout.addWidget(btn)
            self.ui.right_nav_widget.room_list[room_name] = direct_message_layout
            self.ui.right_nav_widget.direct_message_layout.addWidget(direct_message_widget)

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
        if room_name != "home":
            # Update avatar status with iddle
            self.update_pixmap_avatar(room_name, AvatarStatus.IDLE)
            
            self.api_controller.update_is_readed_status(room_name, self.ui.client.user_name)
            
        old_widget = self.ui.scroll_area
        old_widget.hide()
        
        widget = self.ui.body_gui_dict[room_name]
        index = self.ui.body_layout.indexOf(old_widget)
        
        self.ui.body_layout.removeWidget(old_widget)
        self.ui.body_layout.insertWidget(index, widget)
        self.ui.frame_icon.update_picture(
            None,
            content=Icon.ROOM.value if room_name == "home" else Icon.MESSAGE.value,
        )
        
        self.ui.frame_name.setText(f"{room_name}")
        self.ui.scroll_area = widget
        self.ui.scroll_area.show()
        
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
