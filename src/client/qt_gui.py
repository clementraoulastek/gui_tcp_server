from functools import partial
import logging
import signal
import sys
from threading import Thread
import time
from src.client.gui.CustomQLineEdit import CustomQLineEdit
from src.client.gui.CustomQPushButton import CustomQPushButton
from src.client.qt_core import (
    QApplication,
    QLabel,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    Qt,
    QScrollArea,
    QIcon,
    QSize,
    QThread,
    Signal
)
from datetime import datetime
from src.tools.utils import Color, Icon, QIcon_from_svg
from src.client.client import Client
from src.tools.constant import IP_SERVER, PORT_NB

scroll_bar_vertical_stylesheet = '''
    QScrollArea {
        background: none;
        border: none;
    }
    QScrollBar:vertical {
        background: transparent;
    }
    QScrollBar::handle:vertical {
        background: #4986F7;
        min-height: 25px;
        border-radius: 7px
    }
    QScrollBar::add-line:vertical {
        border: none;
        background: transparent;
        height: 20px;
        border-bottom-left-radius: 7px;
        border-bottom-right-radius: 7px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:vertical {
        border: none;
        background: transparent;
        height: 20px;
        border-top-left-radius: 7px;
        border-top-right-radius: 7px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
        background: transparent;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: transparent;
    }
'''
class ReadWorker(QThread):
    
    signal = Signal()
    
    def __init__(self):
        super(ReadWorker, self).__init__()
        self._is_running = True

    def run(self):
        if not self._is_running:
            self._is_running = True

        while self._is_running:
            self.signal.emit()
            # Thread refreshing time
            time.sleep(0.1)

    def stop(self):
        self.terminate()
        self.exit()
        self._is_running = False
        
comming_msg = ""

class QtGui:
    def __init__(self, title):
        self.app = QApplication([])
        self.main_window = MainWindow(title)
        self.main_window.show()
        
    def run(self):
        sys.exit(self.app.exec())

class MainWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setFixedHeight(600)
        self.setFixedWidth(300)
        self.setWindowTitle(title)
        self.setup_gui()
        self.client = Client(IP_SERVER, PORT_NB, title)
        
    def setup_gui(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_widget.setStyleSheet("background-color: transparent;")
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_widget.setLayout(self.main_layout)
        
        self.set_header_gui()
        self.set_core_gui()
        self.set_footer_gui()
    
    def set_header_gui(self):
        server_status_widget = QWidget()
        server_status_widget.setStyleSheet(f"background-color: {Color.LIGHT_GREY.value};color: black")
        self.status_server_layout = QHBoxLayout(server_status_widget)
        self.status_server_layout.setContentsMargins(90, 0, 85, 0)
        self.status_server_icon = QIcon(QIcon_from_svg(Icon.STATUS.value)).pixmap(QSize(30, 30))
        self.icon_label = QLabel("")
        self.status_server_label = QLabel("Status Server")
        self.icon_label.setPixmap(self.status_server_icon)
        self.status_server_layout.addWidget(self.icon_label)
        self.status_server_layout.addWidget(self.status_server_label)
        self.main_layout.addWidget(server_status_widget)
        
    def set_core_gui(self):
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setObjectName(u"scroll layout")
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setMaximumHeight(400)
        self.scroll_area.setMinimumHeight(400)
        self.scroll_area.setMinimumWidth(295)
        self.scroll_widget = QWidget()
        self.scroll_widget.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.verticalScrollBar().setStyleSheet(scroll_bar_vertical_stylesheet)
        self.scroll_area.setStyleSheet("background-color: transparent;color: white")
        self.scroll_area.setObjectName(u"scroll_feature")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")

        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.main_layout.addWidget(self.scroll_area, Qt.AlignmentFlag.AlignCenter, Qt.AlignmentFlag.AlignCenter)
    
    def set_footer_gui(self):
        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName("button layout")
        self.button_layout.setSpacing(1)
        
        self.clear_button = CustomQPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)
        self.clear_icon = QIcon(QIcon_from_svg(Icon.CLEAR.value))
        self.clear_button.setIcon(self.clear_icon)
        
        self.login_button = CustomQPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.login_icon = QIcon(QIcon_from_svg(Icon.LOGIN.value))
        self.login_button.setIcon(self.login_icon)
        
        self.logout_button = CustomQPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        self.logout_icon = QIcon(QIcon_from_svg(Icon.LOGOUT.value))
        self.logout_button.setIcon(self.logout_icon)
        
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
        
        self.entry = CustomQLineEdit(place_holder_text="Enter your message")
        self.main_layout.addWidget(self.entry)

        self.send_button = CustomQPushButton("Send message")
        self.send_button.clicked.connect(self.send)
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)
        
        self.main_layout.addWidget(self.send_button)
        
    
    def close_connection(self, *args) -> None:
        """
        Close the socket and destroy the gui
        """
        # close the connection
        if hasattr(self.client, "sock"):
            self.client.sock.close()
            # close the socket
            logging.debug("Client disconnected")
        else:
            logging.debug("GUI closed")
            # destroy the gui
            self.destroy()
            sys.exit(0)

    def send(self, signal: int) -> None:
        """
            Send message to the server

        Args:
            signal (event): event coming from signal
        """
        if message := self.entry.text():
            self.client.send_data(message)
            date_time_now = datetime.now()
            dt_string = date_time_now.strftime("%d/%m/%Y %H:%M:%S")
            self._diplay_message_and_clear(
                "Date: ", dt_string, is_from_server=False
            )
            self._diplay_message_and_clear(
                "me: ", message, is_from_server=False, doubleReturn=True
            )

    def _diplay_message_and_clear(
        self,
        id_sender: str,
        message: str,
        is_from_server: bool,
        doubleReturn: bool = False,
    ) -> None:
        """
            Display message on gui and clear the entry

        Args:
            id_sender (str): id from the sender
            message (str): message to display
            is_from_server (bool): is msg coming from server
            doubleReturn (bool, optional): if double return needed. Defaults to False.
        """
        if id_sender != "Date: ":
            self.scroll_layout.addWidget(
                QLabel(f"{id_sender}"), Qt.AlignmentFlag.AlignLeft
            )
        self.scroll_layout.addWidget(
            QLabel(f"{message}\n\n" if doubleReturn else f"{message}\n"), Qt.AlignmentFlag.AlignLeft
        )
        self.entry.clear()

    def _display_message(self, message: str, is_from_server, doubleReturn=False):
        """
            Display message on gui and clear the entry

        Args:
            message (str): message to display
            is_from_server (bool): is msg coming from server
            doubleReturn (bool, optional): if double return needed. Defaults to False.
        """
        global comming_msg
        if ":" in message and "Date" not in message:
            id, message = message.split(":", 1)
            comming_msg = f"{id}: {message}"
            
        comming_msg = message + "\n\n" if doubleReturn else message + "\n"
        
    def update_gui_with_input_messages(self):
        global comming_msg
        if comming_msg:
            self.scroll_layout.addWidget(
                QLabel(f"{comming_msg}\n\n"), Qt.AlignmentFlag.AlignLeft
            )
            comming_msg = ""

    def read(self):
        """
        Read message comming from server
        """
        while self.client.is_connected:
            message, is_from_server = self.client.read_data()
            if message:
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                self._display_message(f"Date: {dt_string}", is_from_server=False)
                self._display_message(message, is_from_server, doubleReturn=True)
            time.sleep(0.1)
            
    def clear(self):
        """
        Clear the entry
        """
        self.scrolled_text.delete(1.0, tkinter.END)
        
    def login(self) -> None:
        """
        Init the connection to the server
        """
        self.client.init_connection()
        if self.client.is_connected:
            self.read_worker = ReadWorker()
            self.read_worker.signal.connect(self.update_gui_with_input_messages)
            self.read_worker.start()
            self.worker_thread = Thread(target=self.read, daemon=True)
            self.worker_thread.start()
        else:
            self._display_message("Server off", is_from_server=True, doubleReturn=True)

    def logout(self) -> None:
        """
        Disconnect the client
        """
        self.client.close_connection()

    def config(self):
        """
        Display the config
        """
        config = f"User name = '{self.client.user_name}'\nClient host = '{self.client.host}'\nClient port = '{self.client.port}'\n\n"
        self.scroll_layout.addWidget(
            QLabel(config), Qt.AlignmentFlag.AlignLeft
        )

