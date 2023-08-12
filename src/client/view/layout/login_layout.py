from src.client.view.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton

from src.client.core.qt_core import (
    QHBoxLayout,
    QLabel,
    Qt,
    QWidget,
    QIcon,
    QVBoxLayout,
    QSizePolicy,
    QGridLayout,
    QLineEdit,
)
from src.tools.utils import Color, Icon, QIcon_from_svg


class LoginLayout(QHBoxLayout):
    def __init__(self, parent=None):
        super(LoginLayout, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        main_widget = QWidget()
        main_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        main_widget.setMinimumHeight(90)
        self.addWidget(main_widget)
        main_widget.setStyleSheet(
            f"background-color: {Color.DARK_GREY.value};color: {Color.LIGHT_GREY.value};border-radius: 30px"
        )
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        username_layout = QGridLayout()
        username_layout.setSpacing(50)
        username_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        password_layout = QGridLayout()
        password_layout.setSpacing(50)
        password_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)

        username_label = QLabel("Username: ")
        username_label.setStyleSheet("font-weight: bold")
        password_label = QLabel("Password: ")
        password_label.setStyleSheet("font-weight: bold")

        self.username_entry = CustomQLineEdit(
            place_holder_text="Enter your username", border_size=1
        )
        self.username_entry.setFixedWidth(300)
        self.password_entry = CustomQLineEdit(
            place_holder_text="Enter your password", border_size=1
        )
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setFixedWidth(300)
        self.password_entry.setContentsMargins(0, 0, 0, 0)

        button_layout = QGridLayout()
        button_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        button_layout.setContentsMargins(self.username_entry.width() / 2 - 20, 0, 0, 0)
        button_layout.setSpacing(5)
        layout.addLayout(button_layout)

        self.send_button = CustomQPushButton("Login")
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)

        self.register_button = CustomQPushButton("Register")
        self.register_icon = QIcon(QIcon_from_svg(Icon.LOGIN.value))
        self.register_button.setIcon(self.register_icon)

        username_layout.addWidget(username_label, 0, 0, Qt.AlignCenter)
        username_layout.addWidget(self.username_entry, 0, 1, Qt.AlignCenter)
        password_layout.addWidget(password_label, 0, 0, Qt.AlignCenter)
        password_layout.addWidget(self.password_entry, 0, 1, Qt.AlignCenter)
        button_layout.addWidget(self.send_button, 0, 0)
        button_layout.addWidget(self.register_button, 0, 1)
