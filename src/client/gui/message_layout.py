from datetime import datetime

from src.client.qt_core import (
    QHBoxLayout,
    QIcon,
    QLabel,
    QSize,
    Qt,
    QWidget,
    QVBoxLayout
)
from src.tools.utils import Color, Icon, QIcon_from_svg
from src.client.gui.CustomQLabel import RoundedLabel

class MessageLayout(QHBoxLayout):
    MAX_CHAR = 60
    background_bool = False

    def __init__(self, str_message: str, user_image_path=None):
        super(MessageLayout, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(20)
        self.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        main_widget = QWidget()
        main_widget.setMinimumWidth(main_widget.width() - 50)
        main_widget.setMaximumWidth(main_widget.width() - 50)
        main_widget.setMinimumHeight(60)
        self.addWidget(main_widget)
        main_widget.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value};border-radius: 14px"
        )
        MessageLayout.background_bool = not MessageLayout.background_bool

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        left_widget = QWidget()
        left_widget.setMaximumWidth(80)
        left_widget.setMinimumWidth(80)
        left_widget.setMaximumHeight(60)
        left_widget.setMinimumHeight(60)
        #left_widget.setStyleSheet(f"background-color: {Color.GREY.value}")
        left_layout = QHBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget)

        right_widget = QWidget()
        right_widget.setMinimumHeight(60)
        right_widget.setStyleSheet(f"background-color: {Color.GREY.value}")
        right_layout = QHBoxLayout()
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget)

        right_layout.setSpacing(25)
        right_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        
        if not user_image_path:
            icon = QIcon(QIcon_from_svg(Icon.MESSAGE.value)).pixmap(QSize(30, 30))
            icon_label = QLabel("")
            icon_label.setPixmap(icon)
            left_layout.addWidget(icon_label)
        else:
            label = RoundedLabel(path=user_image_path)
            left_layout.addWidget(label)

        message_list = []
        message = str_message

        while len(message) > self.MAX_CHAR:
            message_list.append(message[: self.MAX_CHAR])
            message = message[self.MAX_CHAR :]
            print(message)
        message_list.append(message)

        str_message = "\n".join(message_list)

        message_layout = QVBoxLayout()
        message_layout.setSpacing(5)
        time_label = QLabel(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        message_label = QLabel(str_message)

        message_layout.addWidget(time_label)
        message_layout.addWidget(message_label)
        right_layout.addLayout(message_layout)
        
