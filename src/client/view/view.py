import logging
import sys
from typing import Dict, List
from src.client.client import Client
from src.client.controller.main_controller import MainController
from src.client.view.customWidget.CustomQLabel import RoundedLabel
from src.client.view.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.layout.body_scroll_area import BodyScrollArea
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
)
from src.tools.backend import Backend
from src.tools.constant import IP_API, IP_SERVER, PORT_API, PORT_SERVER, SOFT_VERSION
from src.tools.utils import Color, Icon, ImageAvatar, QIcon_from_svg


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
        # self.showMaximized()
        self.setWindowTitle(title)

        self.users_pict = {"server": ImageAvatar.SERVER.value}
        self.users_connected = {}

        self.controller = MainController(self)
        self.client = Client(IP_SERVER, PORT_SERVER, "Default")
        self.backend = Backend(IP_API, PORT_API, self)

        # GUI settings
        self.setup_gui()

    def setup_gui(self) -> None:
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
        self.core_layout = QHBoxLayout()
        self.set_left_nav()
        self.set_body_gui()
        self.set_right_nav()
        self.main_layout.addLayout(self.core_layout)
        self.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        self.set_footer_gui()

        self.controller.login()

    def set_header_gui(self) -> None:
        header_widget = QWidget()
        header_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 12px;\
            border: 1px solid;\
            border-color: {Color.MIDDLE_GREY.value}"
        )

        logo_layout = QHBoxLayout()
        logo_widget = QWidget()
        logo_widget.setStyleSheet("border: none")
        logo_widget.setLayout(logo_layout)
        logo_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        icon_soft = RoundedLabel(content=ImageAvatar.SERVER.value)
        icon_soft.setStyleSheet(
            "font-weight: bold;\
            border: none"
        )
        icon_soft.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        status_server_label = QLabel("Robot Messenger")
        status_server_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        status_server_label.setStyleSheet(
            "font-weight: bold;\
            border: none"
        )
        header_layout = QHBoxLayout(header_widget)

        self.set_buttons_nav_gui(header_layout)

        logo_layout.addWidget(icon_soft)
        logo_layout.addWidget(status_server_label)

        header_layout.addWidget(logo_widget)

        header_layout.addWidget(self.show_right_nav_button)
        header_layout.addWidget(self.close_right_nav_button)

        self.main_layout.addWidget(header_widget)

    def set_right_nav(self) -> None:
        """
        Update the header GUI
        """
        # --- Background
        self.right_nav_widget = QWidget()
        self.right_nav_widget.setMinimumWidth(self.scroll_widget_avatar.width())
        self.right_nav_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 12px;\
            border: 1px solid;\
            border-color: {Color.MIDDLE_GREY.value}"
        )
        self.direct_message_layout = QVBoxLayout(self.right_nav_widget)
        self.direct_message_layout.setSpacing(15)
        self.direct_message_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        rooms_label = QLabel("Rooms")
        rooms_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        rooms_label.setContentsMargins(15, 5, 15, 5)
        rooms_label.setStyleSheet(
            f"font-weight: bold;\
            color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 6px;"
        )

        dm_label = QLabel("Direct messages")
        dm_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        dm_label.setContentsMargins(15, 5, 15, 5)
        dm_label.setStyleSheet(
            f"font-weight: bold;\
            color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 6px;"
        )
        room_btn = CustomQPushButton("🏠 Home")
        room_btn.clicked.connect(self.show_home_layout)
        style_ = """
            QPushButton {{
            font-weight: bold;
            text-align: center;
            border: none;
            }} 
            QPushButton:hover {{
            text-decoration: underline;
            }}
            """
        room_btn.setStyleSheet(style_.format())
        self.room_list: Dict[str, QWidget] = {}
        # Adding widgets to the main layout
        self.direct_message_layout.addWidget(rooms_label)
        self.direct_message_layout.addWidget(room_btn)
        self.direct_message_layout.addWidget(dm_label)
        self.core_layout.addWidget(self.right_nav_widget)

    def set_left_nav(self) -> None:
        # --- Left layout with scroll area
        self.left_nav_layout = QHBoxLayout()
        self.user_inline_layout = QVBoxLayout()
        self.user_inline_layout.setSpacing(25)

        self.user_inline = QVBoxLayout()
        self.user_inline.setSpacing(15)

        self.user_offline = QVBoxLayout()
        self.user_offline.setSpacing(15)

        self.user_inline_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.scroll_area_avatar = QScrollArea()
        self.scroll_area_avatar.setFixedWidth(self.scroll_area_avatar.width() / 4 + 15)

        self.scroll_widget_avatar = QWidget()
        self.scroll_widget_avatar.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.scroll_widget_avatar.setFixedWidth(self.scroll_widget_avatar.width() / 4)
        self.scroll_widget_avatar.setStyleSheet(
            f"font-weight: bold; color: {Color.LIGHT_GREY.value};\
            background-color: {Color.GREY.value};\
            border-radius: 12px;\
            border: 1px solid;\
            border-color: {Color.MIDDLE_GREY.value}"
        )

        self.scroll_area_avatar.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet
        )
        self.scroll_area_avatar.setStyleSheet(
            "background-color: transparent;\
            color: white"
        )
        self.scroll_area_avatar.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_avatar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_avatar.setWidgetResizable(True)

        self.scroll_widget_avatar.setLayout(self.user_inline_layout)
        self.scroll_area_avatar.setWidget(self.scroll_widget_avatar)

        self.info_label = QLabel("Welcome")
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
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_widget.setLayout(self.body_layout)

        self.upper_widget = QWidget()
        self.upper_widget.setContentsMargins(0, 0, 0, 0)
        self.upper_widget.hide()
        self.upper_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.upper_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            border-radius: 12px;\
            border: 1px solid {Color.MIDDLE_GREY.value};"
        )
        upper_layout = QHBoxLayout()
        self.upper_widget.setLayout(upper_layout)

        self.frame_name = QLabel("🏠 home")
        self.frame_name.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.frame_name.setContentsMargins(15, 5, 15, 5)
        self.frame_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frame_name.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 6px;\
            font-weight: bold;\
            border: 1px solid {Color.MIDDLE_GREY.value};"
        )
        upper_layout.addWidget(self.frame_name)
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
        self.logout_button.clicked.connect(self.controller.logout)
        self.logout_icon = QIcon(QIcon_from_svg(Icon.LOGOUT.value))
        self.logout_button.setIcon(self.logout_icon)
        self.logout_button.setDisabled(True)

        info_widget = QWidget()
        info_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            border-radius: 12px"
        )
        self.button_layout.addWidget(info_widget)

        self.main_layout.addLayout(self.button_layout)
        self.send_widget = QWidget()

        self.send_layout = QHBoxLayout()
        self.send_widget.setLayout(self.send_layout)
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
            border: 1px solid {Color.MIDDLE_GREY.value}"
        )
        self.user_icon = QIcon(QIcon_from_svg(Icon.AVATAR.value))

        self.user_widget = QWidget()
        self.user_widget.setStyleSheet(
            f"border: 1px solid;\
            border: 1px solid {Color.MIDDLE_GREY.value}"
        )
        self.custom_user_button = CustomQPushButton("")

        self.user_picture = RoundedLabel(content="")
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

        avatar_layout = QHBoxLayout()
        self.user_widget.setLayout(avatar_layout)

        avatar_layout.addWidget(self.user_picture)
        avatar_layout.addWidget(self.user_name)
        avatar_layout.addWidget(self.custom_user_button)
        avatar_layout.addWidget(self.logout_button)

        self.client_information_dashboard_layout.addWidget(self.user_widget)

        self.entry = CustomQLineEdit(place_holder_text="Please login")
        self.entry.returnPressed.connect(self.controller.send_message_to_server)
        self.entry.setDisabled(True)
        self.send_layout.addWidget(self.user_info_widget)
        self.send_layout.addWidget(self.entry)

        self.send_button = CustomQPushButton("")
        self.send_button.clicked.connect(self.controller.send_message_to_server)
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)
        self.send_button.setDisabled(True)

        version_widget = QLabel(f"Version: {SOFT_VERSION}")
        version_widget.setStyleSheet("font-style: italic")
        version_widget.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        version_widget.setMinimumWidth(self.scroll_widget_avatar.width())

        self.main_layout.addWidget(self.send_widget)
        self.send_layout.addWidget(self.send_button)
        self.send_layout.addWidget(version_widget)

    def set_buttons_nav_gui(self, header_layout: QLayout) -> None:
        self.show_icon = QIcon(QIcon_from_svg(Icon.RIGHT_ARROW.value))
        self.close_icon = QIcon(QIcon_from_svg(Icon.LEFT_ARROW.value))

        # --- Button horizontal layout
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(5, 0, 0, 0)
        self.button_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        self.button_layout.setObjectName("button layout")
        self.button_layout.setSpacing(5)

        # --- Close left nav button
        self.close_left_nav_button = CustomQPushButton("")
        self.close_left_nav_button.clicked.connect(self.controller.hide_left_layout)
        self.close_left_nav_button.setIcon(self.close_icon)
        self.close_left_nav_button.setFixedWidth(50)

        # --- Close right nav button
        self.close_right_nav_button = CustomQPushButton("")
        self.close_right_nav_button.clicked.connect(self.controller.hide_right_layout)
        self.close_right_nav_button.setIcon(self.show_icon)
        self.close_right_nav_button.setFixedWidth(50)

        # --- Show left button
        self.show_left_nav_button = CustomQPushButton("")
        self.show_left_nav_button.clicked.connect(self.controller.show_left_layout)
        self.show_left_nav_button.setIcon(self.show_icon)
        self.show_left_nav_button.setFixedWidth(50)
        self.show_left_nav_button.hide()

        # --- Show right button
        self.show_right_nav_button = CustomQPushButton("")
        self.show_right_nav_button.clicked.connect(self.controller.show_right_layout)
        self.show_right_nav_button.setIcon(self.close_icon)
        self.show_right_nav_button.setFixedWidth(50)
        self.show_right_nav_button.hide()

        header_layout.addWidget(self.close_left_nav_button)
        header_layout.addWidget(self.show_left_nav_button)

    def show_home_layout(self) -> None:
        self.controller.gui_controller.update_gui_for_mp_layout("home")

    def closeEvent(self, event) -> None:
        """
        Close the socket and destroy the gui
        """
        if hasattr(self.client, "sock"):
            logging.debug("Client disconnecting...")
            self.client.close_connection()
            logging.debug("Client disconnected")
        logging.debug("GUI closing ...")
