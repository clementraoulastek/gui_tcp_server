import logging
import sys
from typing import Dict, List
from src.client.client import Client
from src.client.controller.main_controller import MainController
from src.client.view.customWidget.AvatarQLabel import AvatarLabel
from src.client.view.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.header import HeaderView
from src.client.view.layout.body_scroll_area import BodyScrollArea
from src.client.view.layout.message_layout import UserMenu
from src.client.view.right_nav import RightNavView
from src.client.view.stylesheets.stylesheets import scroll_bar_vertical_stylesheet
from src.client.core.qt_core import (
    QApplication,
    QHBoxLayout,
    QIcon,
    QLabel,
    QMainWindow,
    QScrollArea,
    Qt,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QLayout,
    QGraphicsDropShadowEffect,
    QColor,
)
from src.tools.backend import Backend
from src.tools.constant import IP_API, IP_SERVER, PORT_API, PORT_SERVER, SOFT_VERSION
from src.tools.utils import Color, Icon, ImageAvatar, QIcon_from_svg
from src.client.view.tools.graphical_effects import widget_shadow

class QtGui:
    def __init__(self, title):
        self.app = QApplication([])
        self.main_window = MainWindow(title)
        self.app.setWindowIcon(QIcon(ImageAvatar.SERVER.value))
        self.app.setApplicationName(title)
        self.main_window.show()
        
        self.app.aboutToQuit.connect(self.quit)
        
    def quit(self):
        # ? I don't know why but in a list comprehension it doesn't work
        if hasattr(self.main_window.controller.gui_controller, "read_worker"):
            
            if self.main_window.controller.api_controller.is_connected:
                self.main_window.controller.api_controller.send_login_status(
                    username=self.main_window.client.user_name, 
                    status=False
                )
                
            if self.main_window.client.is_connected:
                self.main_window.client.close_connection()
                
        logging.info("GUI killed successfully")
        sys.exit()

    def run(self):
        self.app.exec()


class MainWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        
        # self.showMaximized()
        self.setWindowTitle(title)

        # TODO: this attr should be in the controller
        self.users_pict = {"server": ImageAvatar.SERVER.value}
        self.users_connected = {}

        # Init controller
        self.controller = MainController(self)
        
        # Init client socket to the server
        self.client = Client(IP_SERVER, PORT_SERVER, "Default")
        
        # Init connection to the API
        self.backend = Backend(IP_API, PORT_API, self)

        # GUI settings
        self.setup_gui()
        
    def setup_gui(self) -> None:
        """
        Add elements to the main window
        """
        # Main widget
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet(f"background-color: {Color.DARK_GREY.value};")
        self.setCentralWidget(self.main_widget)

        # Main layout
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        
        # Header 
        self.header = HeaderView(self.controller)
        self.main_layout.addWidget(self.header.main_widget)
        
        # Core widget
        self.core_widget = QWidget()
        self.core_widget.setContentsMargins(0, 0, 0, 0)
        
        # Core layout
        self.core_layout = QHBoxLayout(self.core_widget)
        self.core_layout.setContentsMargins(0, 0, 0, 0)
        
        # Update core layout
        self.set_left_nav()
        self.set_body_gui()
        self.right_nav_widget = RightNavView(self.controller, width=300)
        self.core_layout.addWidget(self.right_nav_widget.scroll_area_dm)
        
        self.main_layout.addWidget(self.core_widget)
        self.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        
        # Footer
        self.set_footer_gui()
        
        # Show the login layout
        self.controller.login()

    def set_left_nav(self) -> None:
        # --- Left layout with scroll area
        self.left_nav_layout = QHBoxLayout()
        self.user_inline = QVBoxLayout()
        self.user_inline.setSpacing(15)

        self.user_offline = QVBoxLayout()
        self.user_offline.setSpacing(15)

        self.scroll_area_avatar = QScrollArea()
        self.scroll_area_avatar.setFixedWidth(self.scroll_area_avatar.width() / 4 + 2)

        self.scroll_widget_avatar = QWidget()
        widget_shadow(self.scroll_widget_avatar)
        self.left_nav_layout.update()
        self.scroll_widget_avatar.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.scroll_widget_avatar.setFixedWidth(self.scroll_widget_avatar.width() / 4)
        self.scroll_widget_avatar.setStyleSheet(
            f"font-weight: bold;\
            color: {Color.LIGHT_GREY.value};\
            background-color: {Color.GREY.value};\
            border-radius: 12px;\
            border: 1px solid;\
            border-color: {Color.MIDDLE_GREY.value};\
            margin-bottom: 2px;"
        )
        
        self.user_inline_layout = QVBoxLayout(self.scroll_widget_avatar)
        self.user_inline_layout.setSpacing(25)
        self.user_inline_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        self.scroll_area_avatar.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet
        )
        self.scroll_area_avatar.setStyleSheet("background-color: transparent;")
        self.scroll_area_avatar.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_avatar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_avatar.setWidgetResizable(True)

        self.scroll_area_avatar.setWidget(self.scroll_widget_avatar)

        self.info_label = QLabel("")
        widget_shadow(self.scroll_widget_avatar)
        self.info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.info_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.message_label = QLabel("Login session")
        self.message_label.setStyleSheet("border: 0px")
        self.message_label.setWordWrap(True)
        self.info_label.setContentsMargins(5, 5, 5, 5)
        self.info_label.setStyleSheet(
            f"font-weight: bold; color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 6px;"
        )
        self.user_inline.addWidget(self.info_label)
        self.user_inline.addWidget(self.message_label)
        self.user_inline_layout.addLayout(self.user_inline)

        self.info_disconnected_label = QLabel("")
        widget_shadow(self.scroll_widget_avatar)
        self.info_disconnected_label.hide()
        self.info_disconnected_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.info_disconnected_label.setContentsMargins(5, 5, 5, 5)
        self.info_disconnected_label.setStyleSheet(
            f"font-weight: bold;\
            color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 6px;"
        )
        self.user_offline.addWidget(self.info_disconnected_label)
        self.user_inline_layout.addLayout(self.user_offline)

        self.left_nav_layout.addWidget(self.scroll_area_avatar)
        self.core_layout.addLayout(self.left_nav_layout)

    def set_body_gui(self) -> None:
        """
        Update the core GUI
        """
        self.body_widget = QWidget()
        self.body_layout = QVBoxLayout(self.body_widget)
        self.body_layout.setContentsMargins(0, 0, 0, 0)

        self.upper_widget = QWidget()
        self.upper_widget.setContentsMargins(0, 0, 0, 0)
        self.upper_widget.hide()
        self.upper_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.upper_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            border-radius: 12px;\
            border: 1px solid {Color.MIDDLE_GREY.value};"
        )
        widget_shadow(self.upper_widget)
        upper_layout = QHBoxLayout(self.upper_widget)

        self.frame_title = QWidget()
        self.frame_title.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.frame_title.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 6px;\
            font-weight: bold;\
            border: 1px solid {Color.MIDDLE_GREY.value};"
        )
        self.frame_layout = QHBoxLayout(self.frame_title)
        self.frame_layout.setContentsMargins(10, 5, 10, 5)
        self.frame_layout.setSpacing(10)
        self.frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frame_icon = AvatarLabel(
            content=Icon.ROOM.value, color=Color.WHITE.value, height=15, width=15
        )
        self.frame_icon.setStyleSheet("border: none")
        self.frame_name = QLabel("home")
        widget_shadow(self.upper_widget)
        self.frame_name.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.frame_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frame_name.setStyleSheet("border: 0px")
        self.frame_layout.addWidget(self.frame_icon)
        self.frame_layout.addWidget(self.frame_name)
        upper_layout.addWidget(self.frame_title)

        self.body_layout.addWidget(self.upper_widget)

        self.body_gui_dict = {"home": BodyScrollArea(name="home")}
        self.scroll_area = self.body_gui_dict["home"]

        self.body_layout.addWidget(self.scroll_area)

        self.core_layout.addWidget(self.body_widget)

    def set_footer_gui(self) -> None:
        """
        Update the footer GUI
        """
        self.logout_button = CustomQPushButton(" Logout")
        self.logout_button.widget_shadow()
        self.logout_button.clicked.connect(self.controller.logout)
        self.logout_icon = QIcon(QIcon_from_svg(Icon.LOGOUT.value))
        self.logout_button.setIcon(self.logout_icon)
        self.logout_button.setDisabled(True)

        info_widget = QWidget()
        info_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            border-radius: 12px"
        )

        self.header.button_layout.addWidget(info_widget)

        self.main_layout.addLayout(self.header.button_layout)
        self.send_widget = QWidget()
        self.send_layout = QHBoxLayout(self.send_widget)
        self.send_layout.setObjectName("send layout")
        self.send_layout.setContentsMargins(0, 0, 0, 0)
        self.send_layout.setSpacing(5)

        # --- Client information
        self.user_info_widget = QWidget()
        self.client_information_dashboard_layout = QHBoxLayout(self.user_info_widget)
        self.client_information_dashboard_layout.setContentsMargins(0, 0, 0, 0)
        self.user_info_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 12px;\
            border: 1px solid {Color.MIDDLE_GREY.value};\
            margin-bottom: 2px;"
        )
        self.user_icon = QIcon(QIcon_from_svg(Icon.AVATAR.value))

        self.user_widget = QWidget()
        shadow = QGraphicsDropShadowEffect(self.user_widget)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 2)
        shadow.setBlurRadius(1)
        self.user_widget.setGraphicsEffect(shadow)
        shadow.update()

        self.user_widget.setStyleSheet(
            f"border: 1px solid {Color.MIDDLE_GREY.value};"
        )
        self.custom_user_button = CustomQPushButton("")
        self.custom_user_button.widget_shadow()

        self.user_picture = AvatarLabel(content="")
        self.user_picture.setStyleSheet("border: 0px")
        self.user_name = QLabel("User disconnected")
        self.user_name.setStyleSheet(
            "font-weight: bold;\
            border: none;"
        )

        self.custom_user_button.setIcon(self.user_icon)
        self.custom_user_button.setFixedWidth(50)
        self.custom_user_button.clicked.connect(self.controller.update_user_icon)
        self.custom_user_button.setEnabled(False)

        avatar_layout = QHBoxLayout(self.user_widget)

        avatar_layout.addWidget(self.user_picture)
        avatar_layout.addWidget(self.user_name)
        avatar_layout.addWidget(self.custom_user_button)
        avatar_layout.addWidget(self.logout_button)

        self.client_information_dashboard_layout.addWidget(self.user_widget)

        self.entry = CustomQLineEdit(place_holder_text="Please login")
        self.entry.returnPressed.connect(self.controller.send_message_to_server)
        self.send_layout.addWidget(self.user_info_widget)
        self.send_layout.addWidget(self.entry)

        self.send_button = CustomQPushButton("")
        self.send_button.widget_shadow()
        self.send_button.clicked.connect(self.controller.send_message_to_server)
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)

        version_widget = QLabel(f"Version: {SOFT_VERSION}")
        version_widget.setStyleSheet(
            f"font-style: italic; color: {Color.LIGHT_GREY.value}"
        )
        version_widget.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        version_widget.setMinimumWidth(self.scroll_widget_avatar.width())

        self.send_layout.addWidget(self.send_button)
        self.send_layout.addWidget(version_widget)
        self.main_layout.addWidget(self.send_widget)


