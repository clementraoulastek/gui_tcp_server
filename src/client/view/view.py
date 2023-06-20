import logging
import sys
import time
from threading import Thread
from typing import Union
from src.client.client import Client
from src.client.controller.controller import Controller
from src.client.view.customWidget.CustomQLabel import RoundedLabel
from src.client.view.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.layout.login_layout import LoginLayout
from src.client.view.layout.message_layout import MessageLayout
from src.client.view.stylesheets.stylesheets import scroll_bar_vertical_stylesheet
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
    Signal,
)
from src.tools.backend import Backend
from src.tools.constant import IP_API, IP_SERVER, PORT_API, PORT_NB, SOFT_VERSION
from src.tools.utils import Color, Icon, ImageAvatar, QIcon_from_svg
from src.tools.commands import Commands



class QtGui:
    def __init__(self, title):
        self.app = QApplication([])
        self.main_window = MainWindow(title)
        self.app.setWindowIcon(QIcon(ImageAvatar.SERVER.value))
        self.app.setApplicationName(title)
        self.main_window.show()

    def run(self):
        sys.exit(self.app.exec())


class MainWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        # GUI size
        self.setFixedHeight(600)
        self.setFixedWidth(850)
        self.setWindowTitle(title)

        self.users_pict = {"server": ImageAvatar.SERVER.value}
        
        # Create Controller
        self.controller = Controller(self)

        # Create Client socket
        self.client = Client(IP_SERVER, PORT_NB, "Default")

        # Create backend conn
        self.backend = Backend(self, IP_API, PORT_API)

        # GUI settings
        self.setup_gui()

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

        self.controller.login()

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
        self.status_server_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        # --- Server information
        self.server_info_widget = QWidget()
        self.server_info_widget.setStyleSheet(
            f"background-color: {Color.DARK_GREY.value};color: {Color.LIGHT_GREY.value};border-radius: 14px"
        )
        self.server_information_dashboard_layout = QHBoxLayout(self.server_info_widget)

        icon_soft = RoundedLabel(content=ImageAvatar.SERVER.value)
        status_server_label = QLabel(f"version: {SOFT_VERSION}")

        # Adding widgets to the main layout
        self.server_information_dashboard_layout.addWidget(icon_soft)
        self.server_information_dashboard_layout.addWidget(status_server_label)

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

        self.user_picture = RoundedLabel(content="")
        self.user_name = QLabel("User disconnected")

        self.user_name.setStyleSheet("font-weight: bold")

        self.custom_user_button.setIcon(self.user_icon)
        self.custom_user_button.clicked.connect(self.controller.send_user_icon)
        self.custom_user_button.setEnabled(False)

        self.client_information_dashboard_layout.addWidget(self.custom_user_button)
        self.client_information_dashboard_layout.addWidget(self.user_name)
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
        self.core_layout = QHBoxLayout()
        
        # --- Left layout with scroll area
        self.info_layout = QVBoxLayout()
        self.info_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.scroll_area_avatar = QScrollArea()
        self.scroll_area_avatar.setFixedWidth(self.scroll_area_avatar.width()/3 +13)

        self.scroll_widget_avatar = QWidget()
        self.scroll_widget_avatar.setFixedWidth(self.scroll_widget_avatar.width() / 3)
        self.scroll_widget_avatar.setStyleSheet(
            f"font-weight: bold; color: {Color.LIGHT_GREY.value};background-color: {Color.GREY.value};border-radius: 14px"
        )
        
        self.scroll_area_avatar.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet
        )
        self.scroll_area_avatar.setStyleSheet("background-color: transparent;color: white")
        self.scroll_area_avatar.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_avatar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_avatar.setWidgetResizable(True)

        self.scroll_widget_avatar.setLayout(self.info_layout)
        self.scroll_area_avatar.setWidget(self.scroll_widget_avatar)
        
        
        self.info_label = QLabel("Please login")
        self.info_label.setContentsMargins(10, 5, 10, 5)
        self.info_label.setStyleSheet(
            f"font-weight: bold; color: {Color.LIGHT_GREY.value};background-color: {Color.DARK_GREY.value};border-radius: 8px"
        )
        self.info_layout.addWidget(self.info_label)

        
        # --- Right layout with scroll area
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setObjectName("scroll layout")

        self.scroll_area = QScrollArea()
        self.scroll_area.verticalScrollBar().rangeChanged.connect(self.scrollToBottom)

        self.scroll_area.setContentsMargins(0, 0, 90, 0)
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
        
        self.core_layout.addWidget(self.scroll_area_avatar)
        self.core_layout.addWidget(self.scroll_area)

        self.main_layout.addLayout(self.core_layout)
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
        self.clear_button.clicked.connect(self.controller.clear)
        self.clear_icon = QIcon(QIcon_from_svg(Icon.CLEAR.value))
        self.clear_button.setIcon(self.clear_icon)
        self.clear_button.setDisabled(True)

        self.login_button = CustomQPushButton("Login")
        self.login_button.clicked.connect(self.controller.login)
        self.login_icon = QIcon(QIcon_from_svg(Icon.LOGIN.value))
        self.login_button.setIcon(self.login_icon)

        self.logout_button = CustomQPushButton("Logout")
        self.logout_button.clicked.connect(self.controller.logout)
        self.logout_icon = QIcon(QIcon_from_svg(Icon.LOGOUT.value))
        self.logout_button.setIcon(self.logout_icon)
        self.logout_button.setDisabled(True)

        self.config_button = CustomQPushButton("")
        self.config_button.clicked.connect(self.controller.config)
        self.settings_icon = QIcon(QIcon_from_svg(Icon.CONFIG.value))
        self.config_button.setFixedWidth(50)
        self.config_button.setIcon(self.settings_icon)

        info_widget = QWidget()
        info_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};border-radius: 14px"
        )

        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addWidget(self.login_button)
        self.button_layout.addWidget(self.logout_button)
        self.button_layout.addWidget(self.config_button)
        self.button_layout.addWidget(info_widget)

        self.main_layout.addLayout(self.button_layout)

        self.send_layout = QHBoxLayout()
        self.send_layout.setObjectName("send layout")
        self.send_layout.setSpacing(5)

        self.entry = CustomQLineEdit(place_holder_text="Please login")
        self.entry.returnPressed.connect(self.controller.send_messages)
        self.entry.setDisabled(True)
        self.send_layout.addWidget(self.entry)

        self.send_button = CustomQPushButton("")
        self.send_button.clicked.connect(self.controller.send_messages)
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)
        self.send_button.setDisabled(True)

        self.send_layout.addWidget(self.send_button)
        self.main_layout.addLayout(self.send_layout)

    def closeEvent(self, event) -> None:
        """
        Close the socket and destroy the gui
        """
        if hasattr(self.client, "sock"):
            logging.debug("Client disconnecting...")
            self.client.close_connection()
            logging.debug("Client disconnected")
        logging.debug("GUI closing ...")
        self.destroy()
        sys.exit(0)