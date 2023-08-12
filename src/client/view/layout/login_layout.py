from src.client.view.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.customWidget.CustomQLabel import RoundedLabel

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
from src.tools.utils import Color, Icon, ImageAvatar, QIcon_from_svg


class LoginLayout(QHBoxLayout):
    def __init__(self):
        super(LoginLayout, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.main_widget = QWidget()
        self.main_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(self.main_widget)
        self.main_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 30px;\
            border: 1px solid {Color.MIDDLE_GREY.value};"
        )
        layout = QVBoxLayout(self.main_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignCenter)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 30)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_layout = QLabel("Login")
        self.title_layout.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value}; border: none; font-size: 36px; font-weight: bold"
        )
        title_layout.addWidget(self.title_layout)
        layout.addLayout(title_layout)

        error_layout = QHBoxLayout()
        error_layout.setContentsMargins(0, 0, 0, 15)
        error_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label = QLabel("Please login or register if you havn't account yet")
        self.error_label.setStyleSheet(f"color: {Color.LIGHT_GREY.value}; border: none")
        error_layout.addWidget(self.error_label)

        layout.addLayout(error_layout)

        username_layout = QHBoxLayout()
        username_layout.setContentsMargins(0, 0, 0, 0)
        username_layout.setSpacing(15)
        username_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(15)
        password_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(username_layout)
        layout.addLayout(password_layout)

        username_label = QLabel("Username: ")
        username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        username_label.setStyleSheet("font-weight: bold; border: none")
        password_label = QLabel("Password: ")
        password_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        password_label.setStyleSheet("font-weight: bold; border: none")

        self.username_entry = CustomQLineEdit(
            place_holder_text="Enter your username", border_size=1
        )
        self.username_entry.setContentsMargins(0, 0, 0, 0)

        self.password_entry = CustomQLineEdit(
            place_holder_text="Enter your password", border_size=1
        )
        self.password_entry.setContentsMargins(0, 0, 0, 0)
        self.password_entry.setEchoMode(QLineEdit.Password)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setContentsMargins(0, 15, 0, 0)

        layout.addLayout(button_layout)

        self.send_button = CustomQPushButton(" Login")
        self.send_button.setFixedWidth(150)
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)

        self.register_button = CustomQPushButton(" Register")
        self.register_button.setFixedWidth(150)
        self.register_icon = QIcon(QIcon_from_svg(Icon.LOGIN.value))
        self.register_button.setIcon(self.register_icon)

        username_layout.addWidget(self.username_entry)
        password_layout.addWidget(self.password_entry)
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.register_button)
