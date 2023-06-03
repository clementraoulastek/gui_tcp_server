from src.client.qt_core import QHBoxLayout, QWidget, QIcon, QSize, QLabel, Qt
from src.tools.utils import Color, Icon, QIcon_from_svg


class MessageLayout(QHBoxLayout):
    MAX_CHAR = 30
    def __init__(self, str_message: str, parent=None):
        super(MessageLayout, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        main_widget = QWidget()
        main_widget.setMinimumWidth(250)
        main_widget.setMaximumWidth(250)
        main_widget.setMinimumHeight(80)
        self.addWidget(main_widget)
        main_widget.setStyleSheet(
            f"background-color: {Color.LIGHT_GREY.value};color: black;border-radius: 7px"
        )
        layout = QHBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        layout.setContentsMargins(5, 0, 5, 0)
        icon = QIcon(QIcon_from_svg(Icon.MESSAGE.value)).pixmap(QSize(30, 30))
        icon_label = QLabel("")
        icon_label.setMaximumWidth(80)
        
        # Add /n for each n character in the message
        
        message_list = []
        message = str_message
        
        while len(message) > self.MAX_CHAR:
            message_list.append(str_message[:self.MAX_CHAR])
            message = str_message[self.MAX_CHAR:]
        message_list.append(message)
                
        str_message = "\n".join(message_list)
        
        layout.addWidget(icon_label)
        message_label = QLabel(str_message)

        message_label.setMinimumWidth(180)
        message_label.setMaximumWidth(180)

        icon_label.setPixmap(icon)
        layout.addWidget(icon_label)
        layout.addWidget(message_label)
