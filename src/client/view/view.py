import logging
import sys
from typing import Dict, List
from src.client.client import Client
from src.client.controller.main_controller import MainController
from src.client.view.customWidget.AvatarQLabel import AvatarLabel
from src.client.view.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.footer import FooterView
from src.client.view.header import HeaderView
from src.client.view.layout.body_scroll_area import BodyScrollArea
from src.client.view.layout.message_layout import UserMenu
from src.client.view.left_nav import LeftNavView
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
        self.setCentralWidget(self.main_widget)

        # Main layout
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        
        # Header 
        self.header = HeaderView(self.controller)
        self.main_layout.addWidget(self.header.main_widget)
        self.main_layout.addLayout(self.header.button_layout)
        
        # Core widget
        self.core_widget = QWidget()
        self.core_widget.setContentsMargins(0, 0, 0, 0)
        
        # Core layout
        self.core_layout = QHBoxLayout(self.core_widget)
        self.core_layout.setContentsMargins(0, 0, 0, 0)
        
        # Update core layout
        self.left_nav_widget = LeftNavView(width=180)
        self.core_layout.addLayout(self.left_nav_widget.left_nav_layout)
        
        self.set_body_gui()
        
        self.right_nav_widget = RightNavView(self.controller, width=180)
        self.core_layout.addWidget(self.right_nav_widget.scroll_area_dm)
        
        self.main_layout.addWidget(self.core_widget)
        self.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        
        # Footer
        self.footer_widget = FooterView(
            self.controller,
            self.left_nav_widget.scroll_widget_avatar.width()
        )
        self.main_layout.addWidget(self.footer_widget.send_widget)
        
        # Show the login layout
        self.controller.login()


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
        widget_shadow(self.frame_title)
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



