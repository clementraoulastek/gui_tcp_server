import logging
from threading import Thread
import time
from typing import List, Optional, Union
from src.client.core.qt_core import (
    QHBoxLayout,
    QLabel,
    QThread,
    Signal,
    QWidget,
    QLayout,
)
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.layout.body_scroll_area import BodyScrollArea
from src.client.view.layout.message_layout import MessageLayout
from src.tools.commands import Commands
from src.client.view.layout.login_layout import LoginLayout
from src.client.view.customWidget.CustomQLabel import AvatarStatus, RoundedLabel
from src.client.core.qt_core import QHBoxLayout, QLabel, QThread, Signal, Qt
from src.tools.utils import ImageAvatar, check_str_len
from src.client.controller.api_controller import ApiController
from src.client.controller.tcp_controller import TcpServerController
import src.client.controller.global_variables as global_variables
from src.tools.utils import Color
from functools import partial


class Worker(QThread):
    """Tricks to update the GUI with deamon thread

    Args:
        QThread (QThread): Thread
    """

    signal = Signal()

    def __init__(self, polling_interval: Optional[int] = 0.01) -> None:
        super(Worker, self).__init__()
        self._is_running = True
        self.polling_interval = polling_interval

    def run(self) -> None:
        if not self._is_running:
            self._is_running = True

        while self._is_running:
            self.signal.emit()
            time.sleep(self.polling_interval)

    def stop(self) -> None:
        self._is_running = False
        self.terminate()
        self.exit()


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

    def __init_working_signals(self) -> None:
        # Worker for incoming messages
        self.read_worker = Worker()
        self.read_worker.signal.connect(self.__diplay_coming_message_on_gui)
        self.read_worker.start()

        # Worker for incoming avatar
        self.read_avatar_worker = Worker()
        self.read_avatar_worker.signal.connect(self.__update_gui_with_connected_avatar)
        self.read_avatar_worker.start()

        # Worker for outdated avatar
        self.read_outdated_avatar_worker = Worker()
        self.read_outdated_avatar_worker.signal.connect(
            self.__update_gui_with_disconnected_avatar
        )
        self.read_outdated_avatar_worker.start()

        self.worker_thread = Thread(
            target=self.__callback_routing_messages_on_ui, daemon=True
        )
        self.worker_thread.start()

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
            id_sender (str): id from the sender
            message (str): message to display
        """
        comming_msg: dict[str, str] = {"id": id_sender, "message": message}
        if messsage_id:
            self.last_message_id = messsage_id
        else:
            self.last_message_id += 1
        message = MessageLayout(
            self,
            comming_msg,
            content=self.ui.users_pict[id_sender],
            reversed_=self.ui.client.user_name == id_sender,
            message_id=self.last_message_id,
            nb_react=nb_react,
            date=date,
        )
        if not frame_name:
            self.ui.scroll_area.main_layout.addLayout(message)
        else:
            self.ui.body_gui_dict[frame_name].main_layout.addLayout(message)
        self.messages_dict[self.last_message_id] = message
        self.ui.entry.clear()

    def display_older_messages(self) -> None:
        """
        Create backend request to get older users messages
        """
        sender_list: list = []
        messages_dict = self.api_controller.get_older_messages()
        for message in messages_dict:
            message_id, sender, receiver, message, reaction_nb, date = (
                message["message_id"],
                message["sender"],
                message["receiver"],
                message["message"],
                message["reaction_nb"],
                message["created_at"],
            )
            message = message.replace("$replaced$", ":")
            if sender not in sender_list:
                sender_list.append(sender)
            if receiver == "home":
                self.diplay_self_message_on_gui(
                    sender,
                    message,
                    frame_name="home",
                    messsage_id=message_id,
                    nb_react=int(reaction_nb),
                    date=date,
                )
            elif self.ui.client.user_name in (sender, receiver):
                direct_message_name = (
                    receiver if sender == self.ui.client.user_name else sender
                )
                icon = RoundedLabel(
                    content=self.ui.users_pict[direct_message_name],
                    status=AvatarStatus.DM,
                )
                self.add_gui_for_mp_layout(direct_message_name, icon)
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
        for sender in sender_list:
            self.ui.users_pict.pop(sender)

    def __diplay_coming_message_on_gui(self) -> None:
        """
        Callback to update gui with input messages
        """
        if not global_variables.comming_msg["message"]:
            return
        if global_variables.comming_msg["id"] != "server":
            self.last_message_id += 1
        message = MessageLayout(
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

        self.add_gui_for_mp_layout(
            dict_key,
            RoundedLabel(
                content=self.ui.users_pict[global_variables.comming_msg["id"]],
                status=AvatarStatus.DM,
            ),
        )
        self.ui.body_gui_dict[dict_key].main_layout.addLayout(message)
        self.ui.scroll_area.scrollToBottom()  # ? Not working
        (
            global_variables.comming_msg["id"],
            global_variables.comming_msg["receiver"],
            global_variables.comming_msg["message"],
        ) = ("", "", "")

    def __callback_routing_messages_on_ui(self) -> None:
        """
        Read messages comming from server
        """
        waiting_time = 0.1
        while self.ui.client.is_connected:
            header, payload = self.ui.client.read_data()
            if payload:
                self.__routing_coming_messages(header, payload)
            time.sleep(waiting_time)

    def __routing_coming_messages(self, header: int, payload: str) -> None:
        """
            Display message on gui and clear the entry
        Args:
            message (str): message to display
        """
        if ":" in payload:
            if header == Commands.CONN_NB.value:
                nb_of_users = payload.split(":")[1]
                self.ui.info_label.setText(f"Users online   |   {nb_of_users}")
            elif header == Commands.HELLO_WORLD.value:
                self.__add_sender_avatar(payload, global_variables.user_disconnect)
                # Return welcome to hello world
                self.ui.client.send_data(Commands.WELCOME, "")
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
                message: MessageLayout = self.messages_dict[int(message_id)]
                message.update_react(int(nb_reaction))
            else:
                id, receiver, message = payload.split(":")
                global_variables.comming_msg["id"] = id
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
        id_, _ = payload.split(":", 1)
        self.ui.users_connected[id_] = False
        self.clear_avatar("user_inline", f"{id_}_layout")
        self.api_controller.add_sender_picture(id_)
        user_disconnect[id_] = [user_connected[id_][0], False]
        self.ui.users_pict.pop(id_)

    def __add_sender_avatar(
        self, payload: str, user_disconnect: dict[str, List[Union[str, bool]]]
    ) -> None:
        id_, _ = payload.split(":", 1)
        self.ui.users_connected[id_] = True
        if id_ in user_disconnect:
            self.clear_avatar("user_offline", f"{id_}_layout_disconnected")
            user_disconnect.pop(id_)
        self.api_controller.add_sender_picture(id_)

    def update_user_icon(self) -> None:
        username = self.ui.client.user_name
        if self.ui.backend.send_user_icon(username, None):
            self.clear_avatar("user_inline", f"{username}_layout")
            self.api_controller.get_user_icon(update_personal_avatar=True)

    def __update_gui_with_connected_avatar(self) -> None:
        """
        Callback to update gui with input avatar
        """
        for user, data in global_variables.user_connected.items():
            if data[1] == False:
                global_variables.user_connected[user] = [data[0], True]
                user_layout = QHBoxLayout()
                user_layout.setSpacing(0)
                user_layout.setContentsMargins(0, 0, 0, 0)
                username = user
                content = data[0]
                user_layout.setObjectName(f"{username}_layout")
                user_pic, dm_pic = RoundedLabel(
                    content=content, status=AvatarStatus.ACTIVATED
                ), RoundedLabel(content=content, status=AvatarStatus.DM)
                user_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
                user_pic.setStyleSheet("border: 0px;")
                username_label = check_str_len(username)
                user_name = CustomQPushButton(username_label)
                user_name.clicked.connect(
                    partial(self.add_gui_for_mp_layout, username, dm_pic, True)
                )
                style_ = """
                QPushButton {{
                font-weight: bold;\
                border-radius: none;
                border: none;
                }} 
                QPushButton:hover {{
                text-decoration: underline;
                }}
                """
                user_name.setStyleSheet(style_.format())
                user_layout.addWidget(user_pic)
                user_layout.addWidget(user_name)
                self.ui.user_inline.addLayout(user_layout)

    def __update_gui_with_disconnected_avatar(self) -> None:
        """
        Callback to update gui with input avatar
        """
        for user, data in global_variables.user_disconnect.items():
            if data[1] == False:
                user_layout = QHBoxLayout()
                user_layout.setSpacing(0)
                user_layout.setContentsMargins(0, 0, 0, 0)
                username = user
                content = data[0]
                user_layout.setObjectName(f"{username}_layout_disconnected")
                user_pic, dm_pic = RoundedLabel(
                    content=content, status=AvatarStatus.DEACTIVATED
                ), RoundedLabel(content=content, status=AvatarStatus.DM)
                user_pic.set_opacity(0.2)
                user_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
                user_pic.setStyleSheet("border: 0px")
                username_label = check_str_len(username)
                user_name = CustomQPushButton(username_label)
                user_name.clicked.connect(
                    partial(self.add_gui_for_mp_layout, username, dm_pic, True)
                )
                style_ = """
                QPushButton {{
                font-weight: bold;\
                border-radius: none;
                border: none;
                }} 
                QPushButton:hover {{
                text-decoration: underline;
                }}
                """
                user_name.setStyleSheet(style_.format())
                user_layout.addWidget(user_pic)
                user_layout.addWidget(user_name)
                self.ui.user_offline.addLayout(user_layout)
                global_variables.user_disconnect[user] = [data[0], True]
        self.ui.info_disconnected_label.setText(
            f"Users offline   |   {len(global_variables.user_disconnect)}"
        )

    def clear(self) -> None:
        """
        Clear the entry
        """
        for i in reversed(range(self.ui.scroll_area.main_layout.count())):
            layout = self.ui.scroll_area.main_layout.itemAt(i).layout()
            if isinstance(layout, QLayout):
                for j in reversed(range(layout.count())):
                    layout.itemAt(j).widget().deleteLater()
        self.ui.scroll_area.main_layout.update()

    def clear_avatar(
        self, parent_layout, layout_name: Optional[Union[QHBoxLayout, None]] = None
    ) -> None:
        """
        Clear avatars
        """
        for i in reversed(range(getattr(self.ui, parent_layout).count())):
            if layout := getattr(self.ui, parent_layout).itemAt(i).layout():
                if (
                    layout_name
                    and layout_name == layout.objectName()
                    or not layout_name
                ):
                    for j in reversed(range(layout.count())):
                        layout.itemAt(j).widget().deleteLater()

        getattr(self.ui, parent_layout).update()

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
        self.ui.users_connected[self.ui.client.user_name] = True
        if self.tcp_controller.is_connected_to_server():
            self.__init_working_signals()
            self.ui.login_form = None
            self.clear()
            self.api_controller.get_user_icon(update_personal_avatar=update_avatar)
            self.ui.message_label.hide()
            self.ui.info_disconnected_label.show()
            self.fetch_all_users_username()
            self.display_older_messages()

    def hide_left_layouts_buttons(self) -> None:
        self.ui.show_left_nav_button.hide()
        self.ui.close_left_nav_button.hide()

    def show_left_layouts_buttons(self) -> None:
        self.ui.show_left_nav_button.show()
        self.ui.close_left_nav_button.show()

    def hide_right_layouts_buttons(self) -> None:
        self.ui.show_right_nav_button.hide()
        self.ui.close_right_nav_button.hide()

    def show_right_layouts_buttons(self) -> None:
        self.ui.show_right_nav_button.show()
        self.ui.close_right_nav_button.show()

    def hide_left_layout(self) -> None:
        self.ui.scroll_area_avatar.hide()
        self.ui.close_left_nav_button.hide()
        self.ui.show_left_nav_button.show()

    def show_left_layout(self) -> None:
        self.ui.scroll_area_avatar.show()
        self.ui.show_left_nav_button.hide()
        self.ui.close_left_nav_button.show()

    def hide_right_layout(self) -> None:
        self.ui.scroll_area_dm.hide()
        self.ui.close_right_nav_button.hide()
        self.ui.show_right_nav_button.show()

    def show_right_layout(self) -> None:
        self.ui.scroll_area_dm.show()
        self.ui.show_right_nav_button.hide()
        self.ui.close_right_nav_button.show()

    def show_footer_layout(self) -> None:
        self.ui.send_widget.show()

    def hide_footer_layout(self) -> None:
        self.ui.send_widget.hide()

    def logout(self) -> None:
        """
        Disconnect the client
        """
        # --------------------------- Socket disconnection --------------------------- #
        self.ui.client.close_connection()

        # -------------------------------- Dict clear -------------------------------- #
        global_variables.user_connected.clear()
        global_variables.user_disconnect.clear()
        self.ui.users_pict = {"server": ImageAvatar.SERVER.value}
        self.ui.users_connected.clear()
        self.ui.room_list.clear()

        # --------------------------------- UI update -------------------------------- #
        self.update_buttons()
        self.clear_avatar("user_inline")
        self.clear_avatar("user_offline")
        self.clear_avatar("direct_message_layout")
        # self.clear_avatar(self.ui.body_gui_dict["home"].main_layout.objectName())

        self.ui.message_label.show()
        self.ui.info_disconnected_label.hide()
        self.ui.upper_widget.hide()

        self.login()

    def update_buttons(self) -> None:
        if self.ui.client.is_connected:
            self._set_buttons_status(False, "Enter your message")
            username_label = check_str_len(self.ui.client.user_name)
            self.ui.user_name.setText(username_label)
        else:
            self._set_buttons_status(True, "Please login")
            self.ui.user_name.setText("User disconnected")
            self.ui.info_label.setText("Welcome")
            self.ui.user_picture.update_picture(
                status=AvatarStatus.DEACTIVATED, content=""
            )

    def _set_buttons_status(self, activate: bool, lock_message: str) -> None:
        self.ui.custom_user_button.setDisabled(activate)
        self.ui.logout_button.setDisabled(activate)
        self.ui.send_button.setDisabled(activate)
        self.ui.entry.setDisabled(activate)
        self.ui.entry.setPlaceholderText(lock_message)

    def add_gui_for_mp_layout(
        self, room_name: str, icon, switch_frame: Optional[bool] = False
    ) -> None:
        if room_name not in self.ui.room_list:
            direct_message_layout = QHBoxLayout()
            direct_message_layout.setSpacing(0)
            direct_message_layout.setContentsMargins(0, 0, 0, 0)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            partial_room_name = check_str_len(room_name)
            btn = CustomQPushButton(partial_room_name)
            btn.clicked.connect(partial(self.update_gui_for_mp_layout, room_name))
            style_ = """
            QPushButton {{
            font-weight: bold;\
            border-radius: none;
            border: none;
            }} 
            QPushButton:hover {{
            text-decoration: underline;
            }}
            """
            btn.setStyleSheet(style_.format())
            btn.update()
            btn.setContentsMargins(0, 0, 0, 0)
            direct_message_layout.addWidget(icon)
            direct_message_layout.addWidget(btn)
            self.ui.room_list[room_name] = direct_message_layout
            self.ui.direct_message_layout.addLayout(direct_message_layout)

            # --- Add Body Scroll Area --- #
            self.ui.body_gui_dict[room_name] = BodyScrollArea(name=room_name)
        if switch_frame:
            self.update_gui_for_mp_layout(room_name)

    def update_gui_for_mp_layout(self, room_name):
        old_widget = self.ui.scroll_area
        old_widget.hide()
        widget = self.ui.body_gui_dict[room_name]
        index = self.ui.body_layout.indexOf(old_widget)
        self.ui.body_layout.removeWidget(old_widget)
        self.ui.body_layout.insertWidget(index, widget)
        self.ui.frame_name.setText(
            f"{room_name}" if room_name != "home" else "🏠 home"
        )  # TODO: Get label text rather than frame name
        self.ui.scroll_area = widget
        self.ui.scroll_area.show()

    def fetch_all_users_username(self):
        usernames: List[str] = self.ui.backend.get_all_users_username()
        for username in usernames:
            self.api_controller.add_sender_picture(username)
