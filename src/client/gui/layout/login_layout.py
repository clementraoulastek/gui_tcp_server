from src.client.gui.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.gui.customWidget.CustomQPushButton import CustomQPushButton

from src.client.core.qt_core import QHBoxLayout, QLabel, Qt, QWidget, QIcon
from src.tools.utils import Color, Icon, QIcon_from_svg


class LoginLayout(QHBoxLayout):
    MAX_CHAR = 80

    def __init__(self, parent=None):
        super(LoginLayout, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(20)
        self.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        main_widget = QWidget()
        main_widget.setMinimumWidth(main_widget.width() - 50)
        main_widget.setMaximumWidth(main_widget.width() - 50)
        main_widget.setMinimumHeight(50)
        self.addWidget(main_widget)
        main_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};color: {Color.LIGHT_GREY.value};border-radius: 14px"
        )
        layout = QHBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

        username_label = QLabel("Username: ")
        password_label = QLabel("Password: ")

        self.username_entry = CustomQLineEdit(place_holder_text="Enter your username")
        self.password_entry = CustomQLineEdit(place_holder_text="Enter your password")

        self.send_button = CustomQPushButton("")
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)

        self.register_button = CustomQPushButton("")
        self.register_icon = QIcon(QIcon_from_svg(Icon.LOGIN.value))
        self.register_button.setIcon(self.register_icon)

        layout.addWidget(username_label)
        layout.addWidget(self.username_entry)
        layout.addWidget(password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(self.send_button)
        layout.addWidget(self.register_button)
