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
    def __init__(self):
        super(LoginLayout, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        main_widget = QWidget()
        main_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        main_widget.setMinimumHeight(90)
        self.addWidget(main_widget)
        main_widget.setStyleSheet(
            f"background-color: {Color.DARK_GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 30px"
        )
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        username_layout = QHBoxLayout()
        username_layout.setContentsMargins(0, 0, 50, 0)
        username_layout.setSpacing(0)
        username_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 50, 0)
        password_layout.setSpacing(0)
        password_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)

        username_label = QLabel("Username: ")
        username_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        username_label.setStyleSheet("font-weight: bold")
        password_label = QLabel("Password: ")
        password_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        password_label.setStyleSheet("font-weight: bold")

        self.username_entry = CustomQLineEdit(
            place_holder_text="Enter your username", border_size=1
        )
        self.username_entry.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.password_entry = CustomQLineEdit(
            place_holder_text="Enter your password", border_size=1
        )
        self.password_entry.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.password_entry.setEchoMode(QLineEdit.Password)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 15, 50, 0)
        button_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        error_layout = QHBoxLayout()
        error_layout.setContentsMargins(0, 15, 50, 0)
        self.error_label = QLabel("Please login or register if you havn't account yet")
        self.error_label.setStyleSheet(f"color: {Color.LIGHT_GREY.value}")
        error_layout.addWidget(QLabel(""), 1)
        error_layout.addWidget(self.error_label, 2)
        
        layout.addLayout(error_layout)
        self.error_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        layout.addLayout(button_layout)

        self.send_button = CustomQPushButton(" Login")
        self.send_button.setFixedWidth(150)
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)

        self.register_button = CustomQPushButton(" Register")
        self.register_button.setFixedWidth(150)
        self.register_icon = QIcon(QIcon_from_svg(Icon.LOGIN.value))
        self.register_button.setIcon(self.register_icon)

        username_layout.addWidget(username_label, 1)
        username_layout.addWidget(self.username_entry, 2)
        password_layout.addWidget(password_label, 1)
        password_layout.addWidget(self.password_entry, 2)
        button_layout.addWidget(QLabel(""), 1, Qt.AlignCenter)
        button_layout.addWidget(self.send_button, 1, Qt.AlignRight)
        button_layout.addWidget(self.register_button, 1, Qt.AlignLeft)