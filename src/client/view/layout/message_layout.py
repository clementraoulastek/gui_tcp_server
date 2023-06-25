import logging
import datetime
from src.client.core.qt_core import (
    QHBoxLayout,
    QIcon,
    QLabel,
    QSize,
    Qt,
    QWidget,
    QVBoxLayout,
    QFrame,
)
from src.tools.utils import Color, Icon, QIcon_from_svg
from src.client.view.customWidget.CustomQLabel import RoundedLabel


class MessageLayout(QHBoxLayout):
    MAX_CHAR = 60

    def __init__(self, coming_msg: dict, content=None, reversed_=False):
        super(MessageLayout, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
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
        left_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        left_widget.setLayout(left_layout)

        class Contener(QFrame):
            def __init__(self):
                super(Contener, self).__init__()

            def enterEvent(self, event) -> None:
                self.setStyleSheet(
                    "background-color: {background_color};".format(
                        background_color=Color.DARK_GREY.value
                    )
                )

            def leaveEvent(self, event) -> None:
                self.setStyleSheet(
                    "background-color: {background_color};".format(
                        background_color=Color.GREY.value
                    )
                )

        right_widget = Contener()

        right_widget.setStyleSheet(
            "background-color: {background_color};".format(
                background_color=Color.GREY.value
            )
        )
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        if reversed_:
            main_layout.addWidget(right_widget)
            main_layout.addWidget(left_widget)
        else:
            main_layout.addWidget(left_widget)
            main_layout.addWidget(right_widget)

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
        sender = coming_msg["id"]

        while len(message) > self.MAX_CHAR:
            message_list.append(message[: self.MAX_CHAR])
            message = message[self.MAX_CHAR :]
            print(message)
        message_list.append(message)

        str_message = "\n".join(message_list)

        sender_layout = QHBoxLayout()
        sender_layout.setAlignment(Qt.AlignCenter | Qt.AlignLeft)
        sender_label = QLabel(sender)
        sender_label.setStyleSheet(f"font-weight: bold; color: {Color.WHITE.value}")
        
        date_time = str(datetime.datetime.now().strftime("%m/%d/%Y à %H:%M:%S"))
        date_label = QLabel(date_time)
        sender_layout.addWidget(sender_label)
        sender_layout.addWidget(date_label)
        
        message_label = QLabel(str_message)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        right_layout.addLayout(sender_layout)
        right_layout.addWidget(message_label)
