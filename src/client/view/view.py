"""Module dedicated to the GUI of the client."""

import logging
import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.client.client import Client
from src.client.controller.main_controller import MainController
from src.client.view.custom_widget.custom_button import CustomQPushButton
from src.client.view.custom_widget.custom_line_edit import CustomQLineEdit
from src.client.view.footer import FooterView
from src.client.view.header import HeaderView
from src.client.view.layout.body_scroll_area import BodyScrollArea
from src.client.view.left_nav import LeftNavView
from src.client.view.right_nav import RightNavView
from src.client.view.rooms_bar import RoomsBarWidget
from src.tools.backend import Backend
from src.tools.constant import IP_API, IP_SERVER, PORT_API, PORT_SERVER
from src.tools.utils import Icon, ImageAvatar, Themes, icon_from_svg


class QtGui:
    """
    Main GUI class.
    """

    def __init__(self, title):
        self.app = QApplication([])
        self.main_window = MainWindow(title)
        self.app.setWindowIcon(QIcon(ImageAvatar.SERVER.value))
        self.app.setApplicationName(title)
        self.main_window.show()

        self.app.aboutToQuit.connect(self.quit)

    # pylint: disable=unused-argument
    def quit(self, *args) -> None:
        """
        Quit the GUI
        """
        if self.main_window.controller.api_controller.is_connected:
            self.main_window.controller.api_controller.send_login_status(
                username=self.main_window.client.user_name, status=False
            )

            if self.main_window.client.is_connected:
                self.main_window.client.close_connection()

        logging.info("GUI killed successfully")
        sys.exit()

    def run(self) -> None:
        """
        Run the GUI
        """
        self.app.exec()


# pylint: disable=too-many-instance-attributes
class MainWindow(QMainWindow):
    """
    Main window of the GUI

    Args:
        QMainWindow (QMainWindow): the main window to inherit from
    """

    def __init__(self, title):
        super().__init__()
        self.theme = Themes()
        self.showMaximized()
        self.setWindowTitle(title)

        self.users_pict = {}
        self.users_connected = {}

        self.body_widget = None
        self.body_layout = None
        self.upper_widget = None
        self.frame_title = None
        self.frame_layout = None
        self.frame_icon = None
        self.frame_icon_button = None
        self.frame_name = None
        self.frame_research = None
        self.search_action = None
        self.body_gui_dict = None
        self.scroll_area = None

        # Init controller
        self.controller = MainController(self, self.theme)

        # Init client socket to the server
        self.client = Client(IP_SERVER, PORT_SERVER, "Default")

        # Init connection to the API
        self.backend = Backend(IP_API, PORT_API, self)

        # GUI settings
        self.setup_gui()

        # pylint: disable=invalid-name
        self.resizeEvent = self.resize_event

    def setup_gui(self) -> None:
        """
        Add elements to the main window
        """
        # Main widget
        self.main_widget = QWidget()
        self.main_widget.setContentsMargins(0, 0, 0, 0)
        self.main_widget.setStyleSheet(
            f"background-color: {self.theme.background_color}"
        )
        self.setCentralWidget(self.main_widget)

        # Main layout
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header
        self.header = HeaderView(self.controller, parent=self, theme=self.theme)
        self.main_layout.addWidget(self.header.main_widget)
        self.main_layout.addLayout(self.header.button_layout)

        # Core widget
        self.core_widget = QWidget()
        self.core_widget.setContentsMargins(0, 0, 0, 0)
        self.core_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Core layout
        self.core_layout = QHBoxLayout(self.core_widget)
        self.core_layout.setSpacing(0)
        self.core_layout.setContentsMargins(0, 0, 0, 0)

        # Update core layout
        self.rooms_widget = RoomsBarWidget(theme=self.theme)
        self.left_nav_widget = LeftNavView(width=250, theme=self.theme)

        self.core_layout.addLayout(self.left_nav_widget.left_nav_layout)
        self.core_layout.addWidget(self.rooms_widget.main_widget)
        self.set_body_gui()

        self.right_nav_widget = RightNavView(
            self.controller, width=250, theme=self.theme
        )
        self.core_layout.addWidget(self.right_nav_widget.scroll_area_dm)
        self.main_layout.addWidget(self.core_widget)

        # Footer
        self.footer_widget = FooterView(
            self.controller,
            self.left_nav_widget.scroll_widget_avatar.width(),
            theme=self.theme,
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
        self.body_layout.setSpacing(5)

        self.upper_widget = QWidget()
        self.upper_widget.setContentsMargins(0, 0, 0, 0)
        self.upper_widget.hide()

        self.upper_widget.setStyleSheet(
            f"background-color: {self.theme.inner_color};\
            border-radius: 4px;\
            border: 0px solid {self.theme.nav_color};\
            margin-left: 5px;\
            margin-right: 5px;"
        )
        upper_layout = QHBoxLayout(self.upper_widget)
        upper_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        upper_layout.setContentsMargins(10, 5, 15, 5)

        self.frame_title = QWidget()
        self.frame_title.setStyleSheet(
            f"color: {self.theme.title_color};\
            background-color: transparent;\
            border: 0px solid"
        )
        self.frame_layout = QHBoxLayout(self.frame_title)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_layout.setSpacing(5)

        self.frame_icon = QIcon(
            icon_from_svg(Icon.DOWN_ARROW.value, color=self.theme.title_color)
        )
        self.frame_icon_button = CustomQPushButton(
            "",
            bg_color_active=self.theme.background_color,
        )
        self.frame_icon_button.setFixedSize(QSize(40, 40))
        self.frame_icon_button.setIcon(self.frame_icon)

        self.frame_name = QLabel("Rooms \n| home")
        self.frame_name.setStyleSheet(
            "font-weight: bold;\
            border: 0px solid;\
            margin: 0px;"
        )
        self.frame_research = CustomQLineEdit(
            place_holder_text="Search in Rooms | home",
            bg_color=self.theme.search_color,
            bg_color_active=self.theme.search_color,
            color=self.theme.title_color,
        )
        self.frame_research.setFixedHeight(30)
        self.frame_research.setFixedWidth(200)
        self.frame_research.setTextMargins(0, 0, 0, 0)
        self.frame_research.setAlignment(Qt.AlignmentFlag.AlignLeft)
        search_icon = QIcon(
            icon_from_svg(Icon.SEARCH.value, color=self.theme.title_color)
        )

        self.search_action = self.frame_research.addAction(
            search_icon, QLineEdit.ActionPosition.TrailingPosition
        )

        self.frame_layout.addWidget(self.frame_icon_button)
        self.frame_layout.addWidget(
            self.frame_name, alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.frame_layout.addWidget(
            self.frame_research, stretch=1, alignment=Qt.AlignmentFlag.AlignRight
        )
        upper_layout.addWidget(self.frame_title)

        self.body_layout.addWidget(self.upper_widget)

        self.body_gui_dict = {
            "home": BodyScrollArea(
                name="home", gui_controller=self.controller.gui_controller
            )
        }
        self.scroll_area = self.body_gui_dict["home"]
        self.frame_icon_button.clicked.connect(self.scroll_area.scrollToBottom)

        self.body_layout.addWidget(self.scroll_area)

        self.core_layout.addWidget(self.body_widget)

    # pylint: disable=unused-argument
    def resize_event(self, event) -> None:
        """
        Override the resize event

        Args:
            event (QEvent): the resize event
        """
        self.header.frame_research_list.hide()
        self.header.frame_research.clear()
        self.header.frame_research.clearFocus()
        self.header.frame_research.reset_layout()

        if hasattr(self.controller.gui_controller, "theme_board"):
            self.controller.gui_controller.theme_board.hide()
        if hasattr(self.controller.gui_controller, "user_profile_widget"):
            self.controller.gui_controller.user_profile_widget.hide()
