from src.client.view.customWidget.AvatarQLabel import AvatarLabel
from src.client.view.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from dotenv import load_dotenv
import os
from src.client.core.qt_core import (
    QHBoxLayout,
    QLabel,
    Qt,
    QWidget,
    QIcon,
    QVBoxLayout,
    QSizePolicy,
    QLineEdit,
)
from src.client.view.tools.graphical_effects import widget_shadow
from src.tools.utils import Color, Icon, ImageAvatar, QIcon_from_svg

load_dotenv()


class LoginLayout(QHBoxLayout):
    def __init__(self):
        super(LoginLayout, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)

        self.create_main_widget()
        self.create_main_layouts()

        self.create_title_widgets()
        self.create_username_widgets()
        self.create_password_widgets()
        self.create_error_widgets()
        self.create_button_widgets()

        self.main_layout.addLayout(self.title_layout)
        self.main_layout.addLayout(self.error_layout)
        self.main_layout.addLayout(self.username_layout)
        self.main_layout.addLayout(self.password_layout)
        self.main_layout.addLayout(self.button_layout)

    def create_main_widget(self):
        self.main_widget = QWidget()
        self.main_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 0px;\
            border: 1px solid {Color.MIDDLE_GREY.value};"
        )
        self.addWidget(self.main_widget)

    def create_main_layouts(self):
        # --- Main Layout --- #
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignCenter
        )

        # --- Title Layout --- #
        self.title_layout = QHBoxLayout()
        self.title_layout.setContentsMargins(0, 0, 0, 30)
        self.title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Error Layout --- #
        self.error_layout = QHBoxLayout()
        self.error_layout.setContentsMargins(0, 0, 0, 15)
        self.error_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Username Layout --- #
        self.username_layout = QHBoxLayout()
        self.username_layout.setContentsMargins(0, 0, 0, 0)
        self.username_layout.setSpacing(15)

        # --- Password Layout --- #
        self.password_layout = QHBoxLayout()
        self.password_layout.setContentsMargins(0, 0, 0, 0)
        self.password_layout.setSpacing(15)
        self.password_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Buttons Layout --- #
        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_layout.setContentsMargins(0, 15, 0, 0)

    def create_title_widgets(self):
        self.icon_soft = AvatarLabel(content=ImageAvatar.SERVER.value)
        self.icon_soft.setStyleSheet(
            "font-weight: bold;\
            border: none"
        )
        self.icon_soft.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        self.title_label = QLabel("Hello")
        self.title_label.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value};\
            border: none; font-size: 36px;\
            font-weight: bold;\
            font-style: italic"
        )
        self.title_layout.addWidget(self.icon_soft)
        self.title_layout.addWidget(self.title_label)

    def create_error_widgets(self):
        self.error_label = QLabel("Please login or register if you havn't account yet")
        self.error_label.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value};\
            border: none;\
            font-weight: bold"
        )
        self.error_layout.addWidget(self.error_label)

    def create_username_widgets(self):
        self.username_label = QLabel("Username: ")
        self.username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.username_label.setStyleSheet(
            "font-weight: bold;\
            border: none;"
        )
        self.username_entry = CustomQLineEdit(
            place_holder_text="Enter your username",
            text=os.environ["USERNAME"],
        )
        self.username_entry.setFixedWidth(300)
        self.username_entry.setContentsMargins(0, 0, 0, 0)

        self.username_layout.addWidget(self.username_entry)

    def create_password_widgets(self):
        self.password_label = QLabel("Password: ")
        self.password_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_label.setStyleSheet(
            "font-weight: bold;\
            border: none"
        )
        self.password_entry = CustomQLineEdit(
            place_holder_text="Enter your password",
            text=os.environ["PASSWORD"],
        )
        self.password_entry.setFixedWidth(300)
        self.password_entry.setTextMargins(30, 0, 0, 0)
        self.password_entry.setContentsMargins(0, 0, 0, 0)
        self.password_entry.setEchoMode(QLineEdit.Password)

        self.password_layout.addWidget(self.password_entry)

    def create_button_widgets(self):
        self.send_button = CustomQPushButton(" Login")
        self.send_button.setFixedWidth(120)
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)
        self.register_icon = QIcon(QIcon_from_svg(Icon.LOGIN.value))
        self.entry_action = self.password_entry.addAction(
            self.register_icon, QLineEdit.TrailingPosition
        )

        self.button_layout.addWidget(self.send_button)
