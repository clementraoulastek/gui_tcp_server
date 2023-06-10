from datetime import datetime

from src.client.qt_core import QHBoxLayout, QIcon, QLabel, QSize, Qt, QWidget
from src.tools.utils import Color, Icon, QIcon_from_svg


class MessageLayout(QHBoxLayout):
    MAX_CHAR = 80

    def __init__(self, str_message: str, parent=None):
        super(MessageLayout, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(20)
        self.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        main_widget = QWidget()
        main_widget.setMinimumWidth(main_widget.width()-50)
        main_widget.setMaximumWidth(main_widget.width()-50)
        main_widget.setMinimumHeight(50)
        self.addWidget(main_widget)
        main_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};color: {Color.LIGHT_GREY.value};border-radius: 7px"
        )
        layout = QHBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        layout.setContentsMargins(5, 0, 0, 0)
        icon = QIcon(QIcon_from_svg(Icon.MESSAGE.value)).pixmap(QSize(30, 30))
        icon_label = QLabel("")
        icon_label.setMaximumWidth(80)

        message_list = []
        message = str_message

        while len(message) > self.MAX_CHAR:
            message_list.append(message[: self.MAX_CHAR])
            message = message[self.MAX_CHAR :]
            print(message)
        message_list.append(message)

        str_message = "\n".join(message_list)

        time_label = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        str_message = "\n".join([time_label, str_message])
        message_label = QLabel(str_message)

        icon_label.setPixmap(icon)
        layout.addWidget(icon_label)
        layout.addWidget(message_label)
