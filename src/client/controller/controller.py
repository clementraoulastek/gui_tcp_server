import logging
from threading import Thread
import time
from typing import Union
from src.client.view.layout.message_layout import MessageLayout
from src.tools.commands import Commands
from src.client.core.qt_core import QHBoxLayout, QLabel, QThread, Signal, Qt
from src.client.view.customWidget.CustomQLabel import RoundedLabel
from src.client.view.layout.login_layout import LoginLayout
from src.tools.utils import ImageAvatar


class Worker(QThread):
    """Tricks to update the GUI with deamon thread

    Args:
        QThread (QThread): Thread
    """

    signal = Signal()

    def __init__(self, polling_interval=0.01):
        super(Worker, self).__init__()
        self._is_running = True
        self.polling_interval = polling_interval

    def run(self):
        if not self._is_running:
            self._is_running = True

        while self._is_running:
            self.signal.emit()
            time.sleep(self.polling_interval)

    def stop(self):
        self.terminate()
        self.exit()
        self._is_running = False


# Global variable to handle worker
comming_msg = {"id": "", "message": ""}
coming_user = {}
user_disconnect = {}


class Controller:
    def __init__(self, ui) -> None:
        self.ui = ui

    def send_messages(self, *args) -> None:
        """
            Send message to the server

        Args:
            signal (event): event coming from signal
        """
        if message := self.ui.entry.text():
            self.ui.client.send_data(Commands.MESSAGE, message)
            self._diplay_message_after_send(self.ui.client.user_name, message)

    def _diplay_message_after_send(self, id_sender: str, message: str) -> None:
        """
            Display message on gui and clear the entry

        Args:
            id_sender (str): id from the sender
            message (str): message to display
        """
        comming_msg = {"id": id_sender, "message": message}
        self.ui.scroll_widget.layout().addLayout(
            MessageLayout(
                comming_msg,
                content=self.ui.users_pict[id_sender],
                reversed_=self.ui.client.user_name == id_sender,
            )
        )

        self.ui.entry.clear()

    def parse_coming_message(self, header: int, payload: str):
        """
            Display message on gui and clear the entry

        Args:
            message (str): message to display
        """
        global comming_msg, user_disconnect, coming_user
        if ":" in payload:
            if header == Commands.CONN_NB.value:
                nb_of_users = payload.split(":")[1]
                self.ui.info_label.setText(f"Users inline - {nb_of_users}")
                return
            elif header == Commands.HELLO_WORLD.value:
                id_, _ = payload.split(":", 1)
                self.ui.users_connected[id_] = True
                if id_ in user_disconnect.keys():
                    self.clear_avatar("user_offline", f"{id_}_layout_disconnected")
                self.add_sender_picture(id_)
                # Return welcome to hello world
                self.ui.client.send_data(Commands.WELCOME, "")
                return
            elif header == Commands.WELCOME.value:
                id_, _ = payload.split(":", 1)
                self.ui.users_connected[id_] = True
                if id_ in user_disconnect.keys():
                    self.clear_avatar("user_offline", f"{id_}_layout_disconnected")
                self.add_sender_picture(id_)
                return
            elif header == Commands.GOOD_BYE.value:
                id_, _ = payload.split(":", 1)
                self.ui.users_connected[id_] = False
                self.clear_avatar("user_inline", f"{id_}_layout")
                self.add_sender_picture(id_)
                user_disconnect[id_] = [coming_user[id_][0], False]
                self.ui.users_pict.pop(id_)
                return
            comming_msg["id"], comming_msg["message"] = payload.split(":", 1)
        else:
            comming_msg["id"], comming_msg["message"] = "unknown", payload

    def update_gui_with_input_messages(self):
        """
        Callback to update gui with input messages
        """
        global comming_msg
        if comming_msg["message"]:
            self.ui.scroll_layout.addLayout(
                MessageLayout(
                    comming_msg, content=self.ui.users_pict[comming_msg["id"]]
                )
            )
            comming_msg["id"], comming_msg["message"] = "", ""

    def update_gui_with_input_avatar(self):
        """
        Callback to update gui with input avatar
        """
        global coming_user
        for user, data in coming_user.items():
            if data[1] == False:
                user_layout = QHBoxLayout()
                user_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
                username = user
                content = data[0]
                user_layout.setObjectName(f"{username}_layout")
                user_layout.addWidget(RoundedLabel(content=content))
                user_layout.addWidget(QLabel(username))
                self.ui.user_inline.addLayout(user_layout)
                coming_user[user] = [data[0], True]

    def update_gui_with_outdated_avatar(self):
        """
        Callback to update gui with input avatar
        """
        global user_disconnect
        for user, data in user_disconnect.items():
            if data[1] == False:
                user_layout = QHBoxLayout()
                user_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
                username = user
                content = data[0]
                user_layout.setObjectName(f"{username}_layout_disconnected")
                user_layout.addWidget(RoundedLabel(content=content))
                user_layout.addWidget(QLabel(username))
                self.ui.user_offline.addLayout(user_layout)
                user_disconnect[user] = [data[0], True]

    def read_messages(self):
        """
        Read message comming from server
        """
        while self.ui.client.is_connected:
            header, payload = self.ui.client.read_data()
            if payload:
                self.parse_coming_message(header, payload)
            time.sleep(0.1)

    def clear(self):
        """
        Clear the entry
        """
        for i in reversed(range(self.ui.scroll_layout.count())):
            layout = self.ui.scroll_layout.itemAt(i).layout()
            for j in reversed(range(layout.count())):
                layout.itemAt(j).widget().deleteLater()
        self.ui.scroll_layout.update()

    def clear_avatar(self, parent_layout, layout_name: Union[QHBoxLayout, None] = None):
        """
        Clear the entry
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
            self.ui.scroll_layout.addLayout(self.ui.login_form)
            self.ui.login_form.password_entry.returnPressed.connect(
                self.send_login_form
            )
            self.ui.login_form.send_button.clicked.connect(self.send_login_form)
            self.ui.login_form.register_button.clicked.connect(self.send_register_form)

        self.ui.clear_button.setDisabled(True)

    def send_login_form(self):
        """
        Backend request for login form
        """
        username = self.ui.login_form.username_entry.text().replace(" ", "")
        password = self.ui.login_form.password_entry.text().replace(" ", "")
        if not username or not password:
            return

        if self.ui.backend.send_login_form(username, password):
            if username:  # Check if username not empty
                self.ui.client.user_name = username

            self._clean_gui_and_connect(update_avatar=True)

    def send_register_form(self):
        """
        Backend request for register form
        """
        username = self.ui.login_form.username_entry.text().replace(" ", "")
        password = self.ui.login_form.password_entry.text().replace(" ", "")
        if not username or not password:
            return

        if self.ui.backend.send_register_form(username, password):
            if username:
                self.ui.client.user_name = username

            self._clean_gui_and_connect(update_avatar=False)

    def send_user_icon(self, picture_path=None):
        """
        Backend request for sending user icon
        """
        username = self.ui.client.user_name
        if self.ui.backend.send_user_icon(username, picture_path):
            self.get_user_icon(update_personal_avatar=True)

    def get_user_icon(self, username=None, update_personal_avatar=False):
        """
        Backend request for getting user icon
        """
        if not username:
            username = self.ui.client.user_name
        if content := self.ui.backend.get_user_icon(username):
            self.ui.users_pict[username] = content
            if update_personal_avatar:
                self.ui.user_picture.update_picture(content=content)
            if (
                username in self.ui.users_connected.keys()
                and self.ui.users_connected[username] == True
            ):
                global coming_user
                coming_user[username] = [content, False]
            else:
                self.ui.users_connected["username"] = False
                global user_disconnect
                user_disconnect[username] = [content, False]
        else:
            self.ui.users_pict[username] = ""

    def get_older_messages(self):
        """
        Create backend request to get older users messages
        """
        sender_list: list = []
        older_messages: dict = self.ui.backend.get_older_messages()
        messages_list = older_messages["messages"]
        for message in messages_list:
            sender, message = message["sender"], message["message"]
            if sender not in sender_list:
                sender_list.append(sender)
            self.add_sender_picture(sender)
            self._diplay_message_after_send(sender, message)
        # Reset dict to handle new avatar images from conn
        if self.ui.client.user_name in sender_list:
            sender_list.remove(self.ui.client.user_name)
        for sender in sender_list:
            self.ui.users_pict.pop(sender)

    def add_sender_picture(self, sender_id):
        """Add sender picture to the list of sender pictures

        Args:
            sender_id (str): sender identifier
        """
        if sender_id not in list(self.ui.users_pict.keys()):
            self.get_user_icon(sender_id)

    def _clean_gui_and_connect(self, update_avatar: bool) -> None:
        self.ui.users_connected[self.ui.client.user_name] = True
        if self.connect_to_server():
            self.ui.login_form = None
            self.ui.clear_button.setDisabled(False)
            self.clear()
            self.get_user_icon(update_personal_avatar=update_avatar)
            self.ui.message_label.hide()
            self.ui.info_disconnected_label.show()
            self.get_older_messages()

    def connect_to_server(self) -> bool:
        self.ui.client.init_connection()
        if self.ui.client.is_connected:
            # Worker for incoming messages
            self.read_worker = Worker()
            self.read_worker.signal.connect(self.update_gui_with_input_messages)
            self.read_worker.start()

            # Worker for incoming avatar
            self.read_avatar_worker = Worker()
            self.read_avatar_worker.signal.connect(self.update_gui_with_input_avatar)
            self.read_avatar_worker.start()

            # Worker for outdated avatar
            self.read_outdated_avatar_worker = Worker()
            self.read_outdated_avatar_worker.signal.connect(
                self.update_gui_with_outdated_avatar
            )
            self.read_outdated_avatar_worker.start()

            self.worker_thread = Thread(target=self.read_messages, daemon=True)
            self.worker_thread.start()
            self.update_buttons()
            return True
        else:
            self.ui.parse_coming_message("Server off")
            return False

    def hide_left_layout(self):
        self.ui.scroll_area_avatar.hide()
        self.ui.close_button.hide()
        self.ui.show_button.show()

    def show_left_layout(self):
        self.ui.scroll_area_avatar.show()
        self.ui.show_button.hide()
        self.ui.close_button.show()

    def logout(self) -> None:
        """
        Disconnect the client
        """
        global coming_user, user_disconnect
        self.ui.client.close_connection()
        self.update_buttons()
        self.clear_avatar("user_inline")
        coming_user.clear()
        user_disconnect.clear()
        self.clear_avatar("user_offline")
        self.ui.users_pict = {"server": ImageAvatar.SERVER.value}
        self.ui.users_connected.clear()
        self.ui.message_label.show()
        self.login()

    def config(self):
        """
        Display the config
        """
        config = f"User name = '{self.ui.client.user_name}' Client host = '{self.ui.client.host}' Client port = '{self.ui.client.port}'"
        comming_msg = {"id": "server", "message": config}
        self.ui.scroll_layout.addLayout(
            MessageLayout(comming_msg, content=ImageAvatar.SERVER.value)
        )

    def update_buttons(self):
        if self.ui.client.is_connected:
            self._set_buttons_status(True, False, "Enter your message")
            self.ui.user_name.setText(self.ui.client.user_name)
        else:
            self._set_buttons_status(False, True, "Please login")
            self.ui.user_name.setText("User disconnected")
            self.ui.info_label.setText("Please login")
            self.ui.user_picture.update_picture(content="")

    def _set_buttons_status(self, arg0, arg1, lock_message):
        self.ui.custom_user_button.setDisabled(arg1)
        self.ui.logout_button.setDisabled(arg1)
        self.ui.send_button.setDisabled(arg1)
        self.ui.entry.setDisabled(arg1)
        self.ui.entry.setPlaceholderText(lock_message)
