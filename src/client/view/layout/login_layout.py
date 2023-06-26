from src.client.view.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton

from src.client.core.qt_core import QHBoxLayout, QLabel, Qt, QWidget, QIcon, QVBoxLayout
from src.tools.utils import Color, Icon, QIcon_from_svg


class LoginLayout(QHBoxLayout):
    def __init__(self, parent=None):
        super(LoginLayout, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(20)
        self.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        main_widget = QWidget()
        main_widget.setMinimumHeight(90)
        self.addWidget(main_widget)
        main_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};color: {Color.LIGHT_GREY.value};border-radius: 14px"
        )
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

        info_layout = QHBoxLayout()
        layout.addLayout(info_layout)

        username_label = QLabel("Username: ")
        username_label.setStyleSheet("font-weight: bold")
        password_label = QLabel("Password: ")
        password_label.setStyleSheet("font-weight: bold")

        self.username_entry = CustomQLineEdit(place_holder_text="Enter your username")
        self.password_entry = CustomQLineEdit(place_holder_text="Enter your password")

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        button_layout.setSpacing(25)
        layout.addLayout(button_layout)

        self.send_button = CustomQPushButton("Login")
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)

        self.register_button = CustomQPushButton("Register")
        self.register_icon = QIcon(QIcon_from_svg(Icon.LOGIN.value))
        self.register_button.setIcon(self.register_icon)

        info_layout.addWidget(username_label)
        info_layout.addWidget(self.username_entry)
        info_layout.addWidget(password_label)
        info_layout.addWidget(self.password_entry)
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.register_button)
