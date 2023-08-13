import logging
import sys
from src.client.client import Client
from src.client.controller.main_controller import MainController
from src.client.view.customWidget.CustomQLabel import RoundedLabel
from src.client.view.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
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
        self.showMaximized()
        self.setWindowTitle(title)

        self.users_pict = {"server": ImageAvatar.SERVER.value}
        self.users_connected = {}

        self.controller = MainController(self)
        self.client = Client(IP_SERVER, PORT_SERVER, "Default")
        self.backend = Backend(IP_API, PORT_API, self)

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
        self.set_right_nav()
        self.set_footer_gui()

        self.controller.login()

    def set_header_gui(self):
        header_widget = QWidget()
        header_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 30px;\
            border: 1px solid;\
            border-color: {Color.MIDDLE_GREY.value}"
        )
        
        logo_layout = QVBoxLayout()
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
        
        status_server_label = QLabel(f"version: {SOFT_VERSION}")
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

    def set_right_nav(self):
        """
        Update the header GUI
        """
        # --- Background
        self.right_nav_widget = QWidget()
        self.right_nav_widget.setMinimumWidth(self.scroll_widget_avatar.width())
        self.right_nav_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 30px;\
            border: 1px solid;\
            border-color: {Color.MIDDLE_GREY.value}"
        )
        self.status_server_layout = QVBoxLayout(self.right_nav_widget)
        self.status_server_layout.setSpacing(10)
        self.status_server_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        top_label = QLabel("Room")
        top_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        top_label.setContentsMargins(15, 5, 15, 5)
        top_label.setStyleSheet(
            f"font-weight: bold;\
            color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 12px;\
            border: 0px"
        )
        room_label = QLabel("🏠 Home")
        room_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        room_label.setStyleSheet(
            "font-weight: bold;\
            border: none;"
        )

        # Adding widgets to the main layout
        self.status_server_layout.addWidget(top_label)
        self.status_server_layout.addWidget(room_label)
        self.core_layout.addWidget(self.right_nav_widget)

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
        self.user_inline_layout = QVBoxLayout()
        self.user_inline_layout.setSpacing(25)

        self.user_inline = QVBoxLayout()
        self.user_inline.setSpacing(10)

        self.user_offline = QVBoxLayout()
        self.user_offline.setSpacing(10)

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
            border-radius: 30px;\
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
        self.scroll_area_avatar.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_avatar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_avatar.setWidgetResizable(True)

        self.scroll_widget_avatar.setLayout(self.user_inline_layout)
        self.scroll_area_avatar.setWidget(self.scroll_widget_avatar)

        self.info_label = QLabel("Welcome")
        self.message_label = QLabel("Login session")
        self.message_label.setStyleSheet("border: 0px")
        self.message_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.info_label.setContentsMargins(5, 5, 5, 5)
        self.info_label.setStyleSheet(
            f"font-weight: bold; color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 12px;\
            border: 0px"
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
            border-radius: 12px;\
            border: 0px"
        )
        self.user_offline.addWidget(self.info_disconnected_label)
        self.user_inline_layout.addLayout(self.user_offline)

        # --- Right layout with scroll area
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setObjectName("scroll layout")

        self.scroll_area = QScrollArea()
        self.scroll_area.setMinimumWidth(600)
        self.scroll_area.verticalScrollBar().rangeChanged.connect(self.scrollToBottom)

        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setMinimumHeight(380)

        self.scroll_widget = QWidget()
        self.scroll_widget.setContentsMargins(0, 0, 10, 0)
        self.scroll_area.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet
        )
        self.scroll_area.setStyleSheet(
            "background-color: transparent;\
            color: white"
        )
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
        self.logout_button = CustomQPushButton(" Logout")
        self.logout_button.clicked.connect(self.controller.logout)
        self.logout_icon = QIcon(QIcon_from_svg(Icon.LOGOUT.value))
        self.logout_button.setIcon(self.logout_icon)
        self.logout_button.setDisabled(True)

        info_widget = QWidget()
        info_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            border-radius: 14px"
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
            border-radius: 30px;\
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

        self.send_button = CustomQPushButton(" Send")
        self.send_button.clicked.connect(self.controller.send_message_to_server)
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)
        self.send_button.setDisabled(True)

        self.main_layout.addWidget(self.send_widget)
        self.send_layout.addWidget(self.send_button)

    def set_buttons_nav_gui(self, header_layout):
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
