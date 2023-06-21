from datetime import datetime

from src.client.core.qt_core import (
    QHBoxLayout,
    QIcon,
    QLabel,
    QSize,
    Qt,
    QWidget,
    QVBoxLayout,
)
from src.tools.utils import Color, Icon, QIcon_from_svg
from src.client.view.customWidget.CustomQLabel import RoundedLabel


class MessageLayout(QHBoxLayout):
    MAX_CHAR = 60

    def __init__(self, coming_msg: dict, content=None, reversed_=False):
        super(MessageLayout, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(20)
        self.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        main_widget = QWidget()
        main_widget.setFixedHeight(main_widget.maximumHeight())
        self.addWidget(main_widget)
        main_widget.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value};border-radius: 14px"
        )

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        left_widget = QWidget()
        left_widget.setMaximumWidth(80)
        left_widget.setMinimumWidth(80)
        left_layout = QHBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        left_widget.setLayout(left_layout)

        right_widget = QWidget()
        right_widget.setStyleSheet(f"background-color: {Color.GREY.value}")
        right_layout = QHBoxLayout()
        right_widget.setLayout(right_layout)

        if reversed_:
            main_layout.addWidget(right_widget)
            main_layout.addWidget(left_widget)
        else:
            main_layout.addWidget(left_widget)
            main_layout.addWidget(right_widget)

        right_layout.setSpacing(25)
        right_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

        if not content:
            icon = QIcon(QIcon_from_svg(Icon.MESSAGE.value)).pixmap(QSize(15, 15))
            icon_label = QLabel("")
            icon_label.setPixmap(icon)
            left_layout.addWidget(icon_label)
        else:
            label = RoundedLabel(content=content)
            left_layout.addWidget(label)

        message_list = []
        message = coming_msg["message"]

        while len(message) > self.MAX_CHAR:
            message_list.append(message[: self.MAX_CHAR])
            message = message[self.MAX_CHAR :]
            print(message)
        message_list.append(message)

        str_message = "\n".join(message_list)

        message_layout = QVBoxLayout()
        upper_layout = QHBoxLayout()
        message_layout.setSpacing(5)

        message_label = QLabel(str_message)
        message_layout.addLayout(upper_layout)
        message_layout.addWidget(message_label)
        right_layout.addLayout(message_layout)
