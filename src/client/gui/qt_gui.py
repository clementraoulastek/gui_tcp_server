import io
import logging
import sys
import time
from threading import Thread
from src.client.client import Client
from src.client.gui.customWidget.CustomQLabel import RoundedLabel
from src.client.gui.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.gui.customWidget.CustomQPushButton import CustomQPushButton
from src.client.gui.layout.login_layout import LoginLayout
from src.client.gui.layout.message_layout import MessageLayout
from src.client.gui.stylesheets import scroll_bar_vertical_stylesheet
from src.client.core.qt_core import (
    QApplication,
    QHBoxLayout,
    QIcon,
    QLabel,
    QMainWindow,
    QScrollArea,
    QSize,
    Qt,
    QThread,
    QVBoxLayout,
    QWidget,
    Signal
)
from src.tools.backend import Backend
from src.tools.constant import IP_API, IP_SERVER, PORT_API, PORT_NB, SOFT_VERSION
from src.tools.utils import Color, Icon, ImageAvatar, QIcon_from_svg
from PIL import Image

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
comming_msg = {
    "id": "",
    "message": "",
}
users_pict = {
    "server": ImageAvatar.SERVER.value,
}

class QtGui:
    def __init__(self, title):
        self.app = QApplication([])
        self.main_window = MainWindow(title)
        self.app.setWindowIcon(QIcon_from_svg(Icon.MESSAGE.value))
        self.main_window.show()

    def run(self):
        sys.exit(self.app.exec())


class MainWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        # GUI size
        self.setFixedHeight(600)
        self.setFixedWidth(600)
        self.setWindowTitle(title)
        
        # Create Client socket
        self.client = Client(IP_SERVER, PORT_NB, "Default")
        
        # Create backend conn
        self.backend = Backend(self, IP_API, PORT_API)
        
        # GUI settings
        self.setup_gui()
        self.check_client_connected_thread = Worker()
        self.check_client_connected_thread.signal.connect(self.check_client_connected)
        self.check_client_connected_thread.start()

    def setup_gui(self):
        """
        Add elements to the main window
        """
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_widget.setStyleSheet(f"background-color: {Color.DARK_GREY.value};")
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_widget.setLayout(self.main_layout)

        self.set_header_gui()
        self.set_core_gui()
        self.set_footer_gui()

    def check_client_connected(self):
        """
        Update the icon color depending on the connection status
        """
        if self.client.is_connected:
            self.icon_label.setPixmap(self.status_server_icon_on)
        else:
            self.icon_label.setPixmap(self.status_server_icon_off)

    def set_header_gui(self):
        """
        Update the header GUI
        """

        # --- Background
        server_status_widget = QWidget()
        server_status_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};color: {Color.LIGHT_GREY.value};border-radius: 14px"
        )
        self.status_server_layout = QHBoxLayout(server_status_widget)
        self.status_server_layout.setSpacing(20)
        self.status_server_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

        # --- Server information
        self.server_info_widget = QWidget()
        self.server_info_widget.setStyleSheet(
            f"background-color: {Color.DARK_GREY.value};color: {Color.LIGHT_GREY.value};border-radius: 14px"
        )
        self.server_information_dashboard_layout = QHBoxLayout(self.server_info_widget)
        self.status_server_icon_on = QIcon(
            QIcon_from_svg(Icon.STATUS.value, Color.GREEN.value)
        ).pixmap(QSize(30, 30))
        self.status_server_icon_off = QIcon(
            QIcon_from_svg(Icon.STATUS.value, Color.RED.value)
        ).pixmap(QSize(30, 30))
        self.icon_label = QLabel("")
        self.status_server_label = QLabel(f"TCP Client - version: {SOFT_VERSION}")

        self.icon_label.setPixmap(self.status_server_icon_off)

        # Adding widgets to the main layout
        self.server_information_dashboard_layout.addWidget(self.icon_label)
        self.server_information_dashboard_layout.addWidget(self.status_server_label)

        # --- Client information
        self.user_info_widget = QWidget()
        self.client_information_dashboard_layout = QHBoxLayout(self.user_info_widget)
        self.user_info_widget.setStyleSheet(
            f"background-color: {Color.DARK_GREY.value};color: {Color.LIGHT_GREY.value};border-radius: 14px"
        )
        self.user_icon = QIcon(QIcon_from_svg(Icon.USER_ICON.value)).pixmap(
            QSize(30, 30)
        )

        self.custom_user_button = CustomQPushButton(
            "Update user picture",
        )
        
        self.user_picture = RoundedLabel(path="")
        
        self.custom_user_button.setIcon(self.user_icon)
        self.custom_user_button.clicked.connect(self.send_user_icon)
        self.custom_user_button.setEnabled(False)
        self.client_information_dashboard_layout.addWidget(self.custom_user_button)
        self.client_information_dashboard_layout.addWidget(self.user_picture)

        self.status_server_layout.addWidget(self.server_info_widget)
        self.status_server_layout.addWidget(self.user_info_widget)

        self.main_layout.addWidget(server_status_widget)

    def scrollToBottom(self):
        """
        Update the scrollbar vertical position to the bottom
        """
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def set_core_gui(self):
        """
        Update the core GUI
        """
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setObjectName("scroll layout")

        self.scroll_area = QScrollArea()
        self.scroll_area.verticalScrollBar().rangeChanged.connect(self.scrollToBottom)

        self.scroll_area.setContentsMargins(0, 0, 90, 0)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setMaximumHeight(380)
        self.scroll_area.setMinimumHeight(380)

        self.scroll_widget = QWidget()
        self.scroll_widget.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet
        )
        self.scroll_area.setStyleSheet("background-color: transparent;color: white")
        self.scroll_area.setObjectName("scroll_feature")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")

        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

    def set_footer_gui(self):
        """
        Update the footer GUI
        """
        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        self.button_layout.setObjectName("button layout")
        self.button_layout.setSpacing(5)

        self.clear_button = CustomQPushButton("")
        self.clear_button.clicked.connect(self.clear)
        self.clear_icon = QIcon(QIcon_from_svg(Icon.CLEAR.value))
        self.clear_button.setIcon(self.clear_icon)
        self.clear_button.setDisabled(True)

        self.login_button = CustomQPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.login_icon = QIcon(QIcon_from_svg(Icon.LOGIN.value))
        self.login_button.setIcon(self.login_icon)

        self.logout_button = CustomQPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        self.logout_icon = QIcon(QIcon_from_svg(Icon.LOGOUT.value))
        self.logout_button.setIcon(self.logout_icon)
        self.logout_button.setDisabled(True)

        self.config_button = CustomQPushButton("")
        self.config_button.clicked.connect(self.config)
        self.settings_icon = QIcon(QIcon_from_svg(Icon.CONFIG.value))
        self.config_button.setFixedWidth(50)
        self.config_button.setIcon(self.settings_icon)

        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addWidget(self.login_button)
        self.button_layout.addWidget(self.logout_button)
        self.button_layout.addWidget(self.config_button)

        self.main_layout.addLayout(self.button_layout)

        self.send_layout = QHBoxLayout()
        self.send_layout.setObjectName("send layout")
        self.send_layout.setSpacing(5)

        self.entry = CustomQLineEdit(place_holder_text="Please login")
        self.entry.returnPressed.connect(self.send_messages)
        self.entry.setDisabled(True)
        self.send_layout.addWidget(self.entry)

        self.send_button = CustomQPushButton("")
        self.send_button.clicked.connect(self.send_messages)
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)
        self.send_button.setDisabled(True)

        self.send_layout.addWidget(self.send_button)
        self.main_layout.addLayout(self.send_layout)

    def close_connection(self, *args) -> None:
        """
        Close the socket and destroy the gui
        """
        if hasattr(self.client, "sock"):
            self.client.sock.close()
            logging.debug("Client disconnected")
        else:
            logging.debug("GUI closed")
            self.destroy()
            sys.exit(0)

    def send_messages(self, *args) -> None:
        """
            Send message to the server

        Args:
            signal (event): event coming from signal
        """
        if message := self.entry.text():
            self.client.send_data(message)
            self._diplay_message_after_send("me", message)

    def _diplay_message_after_send(self, id_sender: str, message: str) -> None:
        """
            Display message on gui and clear the entry

        Args:
            id_sender (str): id from the sender
            message (str): message to display
        """
        comming_msg = {
            "id": id_sender,
            "message": message
        }
        global users_pict
        self.scroll_layout.addLayout(MessageLayout(comming_msg, user_image_path=users_pict[self.client.user_name]))

        self.entry.clear()

    def _display_message_after_read(self, message: str):
        """
            Display message on gui and clear the entry

        Args:
            message (str): message to display
        """
        global comming_msg
        if ":" in message:
            comming_msg["id"], comming_msg["message"] = message.split(":", 1)
        else:
            comming_msg["id"], comming_msg["message"] = "unknown", message
            
            
    def update_gui_with_input_messages(self):
        """
        Callback to update gui with input messages
        """
        global comming_msg
        global users_pict
        if comming_msg["message"]:
            self.add_sender_picture(comming_msg["id"])
            self.scroll_layout.addLayout(
                MessageLayout(comming_msg, user_image_path=users_pict[comming_msg["id"]])
            )
            comming_msg["id"], comming_msg["message"] = "", ""

    def read_messages(self):
        """
        Read message comming from serve
        """
        while self.client.is_connected:
            if message := self.client.read_data():
                self._display_message_after_read(message)
            time.sleep(0.1)

    def clear(self):
        """
        Clear the entry
        """
        for i in reversed(range(self.scroll_layout.count())):
            layout = self.scroll_layout.itemAt(i).layout()
            for j in reversed(range(layout.count())):
                layout.itemAt(j).widget().deleteLater()
        self.scroll_layout.update()

    def login(self) -> None:
        """
        Display the login form
        """
        self.clear()
        if not hasattr(self, "login_form") or not self.login_form:
            self.login_form = LoginLayout()
            self.scroll_layout.addLayout(self.login_form)
            self.login_form.send_button.clicked.connect(self.send_login_form)
            self.login_form.register_button.clicked.connect(self.send_register_form)

        self.login_button.setDisabled(True)
        self.clear_button.setDisabled(True)

    def send_login_form(self):
        """
        Backend request for login form
        """
        username = self.login_form.username_entry.text()
        password = self.login_form.password_entry.text()
        
        if self.backend.send_login_form(username, password):
            if username: # Check if username not empty
                self.client.user_name = username
                self.get_user_icon(update_avatar=True)

            self._clean_gui_and_connect()
            
    def send_register_form(self):
        """
        Backend request for register form
        """
        username = self.login_form.username_entry.text()
        password = self.login_form.password_entry.text()
        
        if self.backend.send_register_form(username, password):
            self._clean_gui_and_connect()
            
    def send_user_icon(self):
        """
        Backend request for sending user icon
        """
        username = self.client.user_name
        if self.backend.send_user_icon(username):
            self.get_user_icon(update_avatar=True)
            
    def get_user_icon(self, username=None, update_avatar=False):
        """
        Backend request for getting user icon
        """
        if not username:
            username = self.client.user_name
        if content := self.backend.get_user_icon(username):
            picture = Image.open(io.BytesIO(content))
            picture_path = f"./resources/images/{self.client.user_name}_user_picture.png"
            picture.save(picture_path)
            global users_pict
            users_pict[username] = picture_path
            if update_avatar:
                self.user_picture.update_picture(path=picture_path)
        
    def add_sender_picture(self, sender_id):
        """Add sender picture to the list of sender pictures

        Args:
            sender_id (str): sender identifier
        """
        global users_pict
        if sender_id not in list(users_pict.keys()):
            logging.info(True)
            self.get_user_icon(sender_id)
            
        
    def _clean_gui_and_connect(self):
        self.clear()
        self.login_form = None
        self.connect_to_server()
        self.clear_button.setDisabled(False)
            

    def connect_to_server(self):
        self.client.init_connection()
        if self.client.is_connected:
            self.read_worker = Worker()
            self.read_worker.signal.connect(self.update_gui_with_input_messages)
            self.read_worker.start()
            self.worker_thread = Thread(target=self.read_messages, daemon=True)
            self.worker_thread.start()
            self.update_buttons()
        else:
            self._display_message_after_read("Server off")
    
    def logout(self) -> None:
        """
        Disconnect the client
        """
        self.client.close_connection()
        self.update_buttons()

    def config(self):
        """
        Display the config
        """
        config = f"User name = '{self.client.user_name}' Client host = '{self.client.host}' Client port = '{self.client.port}'"
        comming_msg = {
            "id": "server",
            "message": config
        }
        self.scroll_layout.addLayout(MessageLayout(comming_msg, user_image_path=ImageAvatar.SERVER.value))

    def update_buttons(self):
        if self.client.is_connected:
            self._set_buttons_status(True, False, "Enter your message")
        else:
            self._set_buttons_status(False, True, "Please login")

    def _set_buttons_status(self, arg0, arg1, lock_message):
        self.custom_user_button.setDisabled(arg1)
        self.login_button.setDisabled(arg0)
        self.logout_button.setDisabled(arg1)
        self.send_button.setDisabled(arg1)
        self.entry.setDisabled(arg1)
        self.entry.setPlaceholderText(lock_message)
