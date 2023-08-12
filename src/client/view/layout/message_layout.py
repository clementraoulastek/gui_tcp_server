from enum import Enum, unique
import datetime
from typing import Optional
from src.client.core.qt_core import (
    QHBoxLayout,
    QIcon,
    QLabel,
    QSize,
    Qt,
    QWidget,
    QVBoxLayout,
    QFrame,
    QSizePolicy,
)
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.tools.commands import Commands
from src.tools.utils import Color, Icon, QIcon_from_svg
from src.client.view.customWidget.CustomQLabel import RoundedLabel


@unique
class EnumReact(Enum):
    REMOVE = 0
    ADD = 1


class MessageLayout(QHBoxLayout):
    MAX_CHAR: int = 60

    def __init__(
        self,
        controller,
        coming_msg: dict,
        nb_react: Optional[int] = 0,
        content: Optional[None] = None,
        reversed_: Optional[bool] = False,
        message_id: Optional[None] = None,
    ):
        super(MessageLayout, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        self.controller = controller
        self.message_id = message_id
        self.is_reacted = False
        self.nb_react = nb_react

        main_widget = QWidget()

        main_widget.setFixedHeight(main_widget.maximumHeight())
        self.addWidget(main_widget)
        main_widget.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value};"
        )
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        left_widget = QWidget()
        left_widget.setMaximumWidth(80)
        left_widget.setMinimumWidth(80)
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        left_widget.setLayout(left_layout)

        class Contener(QFrame):
            def __init__(self):
                super(Contener, self).__init__()

            def enterEvent(self, event) -> None:
                if button_list := self.findChildren(CustomQPushButton):
                    button = button_list[0]
                    button.show()

            def leaveEvent(self, event) -> None:
                if button_list := self.findChildren(CustomQPushButton):
                    button = button_list[0]
                    button.hide()

        right_widget = Contener()

        right_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            border-radius: 15px;\
            border: 1px solid {Color.MIDDLE_GREY.value}; "
        )
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

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

        str_message = coming_msg["message"]
        sender = coming_msg["id"]

        sender_layout = QHBoxLayout()
        sender_layout.setAlignment(Qt.AlignCenter | Qt.AlignLeft)
        sender_label = QLabel(sender.capitalize())
        left_layout.addWidget(sender_label)
        
        def on_event_enter_user_label():
            sender_label.setStyleSheet(
                f"font-weight: bold; color: {Color.WHITE.value};\
                text-decoration: underline;\
                border: 0px"
            )

        def on_event_leave_user_label():
            sender_label.setStyleSheet(
                f"font-weight: bold;\
                color: {Color.WHITE.value};\
                border: 0px"
            )

        sender_label.enterEvent = lambda event: on_event_enter_user_label()
        sender_label.leaveEvent = lambda event: on_event_leave_user_label()

        sender_label.setStyleSheet(
            f"font-weight: bold;\
            color: {Color.WHITE.value}"
        )

        if message_id:
            self.react_buttton = CustomQPushButton(
                " Add react", bg_color=Color.GREY.value, radius=8
            )
            self.react_buttton.clicked.connect(self.add_react)
            sp_retain = self.react_buttton.sizePolicy()
            sp_retain.setRetainSizeWhenHidden(True)
            self.react_buttton.setSizePolicy(sp_retain)
            self.react_buttton.setAutoFillBackground(True)
            self.react_buttton.setFixedHeight(25)
            react_icon = QIcon(QIcon_from_svg(Icon.SMILEY.value))
            self.react_buttton.setIcon(react_icon)
            self.react_buttton.hide()

            emot_widget = QWidget()
            emot_widget.setStyleSheet("border: 0px;")
            emot_widget.setFixedWidth(50)
            emot_layout = QHBoxLayout(emot_widget)
            emot_layout.setSpacing(0)
            emot_layout.setContentsMargins(0, 0, 0, 0)

            self.react_emot = RoundedLabel(
                content=Icon.SMILEY.value,
                height=15,
                width=15,
                color=Color.LIGHT_GREY.value,
            )
            self.react_emot.hide()
            sp_retain = self.react_emot.sizePolicy()
            sp_retain.setRetainSizeWhenHidden(True)
            self.react_emot.setSizePolicy(sp_retain)

            self.react_emot.setStyleSheet("border: 0px")
            self.react_nb = QLabel("1")

            self.react_emot.setAlignment(Qt.AlignLeft)
            self.react_nb.setAlignment(Qt.AlignLeft)
            self.react_nb.setStyleSheet("font-weight: bold; border: 0px")
            self.react_nb.hide()
            
            emot_layout.addWidget(self.react_emot)
            emot_layout.addWidget(self.react_nb)

        date_time = str(datetime.datetime.now().strftime("%m/%d/%Y à %H:%M:%S"))
        date_label = QLabel(date_time)
        date_label.setStyleSheet("border: 0px")

        separator = QFrame()
        separator.setStyleSheet(f"background-color: {Color.LIGHT_GREY.value};")
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setFixedWidth(1)
        separator.setFixedHeight(12)

        sender_layout.addWidget(date_label)

        if message_id:
            sender_layout.addWidget(self.react_buttton)

        message_label = QLabel(str_message)
        message_label.setStyleSheet("border: 0px")
        message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        right_layout.addLayout(sender_layout)
        right_layout.addWidget(message_label)
        if message_id:
            right_layout.addWidget(emot_widget)
            self.update_react(self.nb_react)

    def add_react(self):
        if self.is_reacted:
            self.nb_react -= 1
            self.is_reacted = False
            self.react_buttton.setText(" Add react")
            self.controller.api_controller.send_emot_react(
                Commands.RM_REACT, self.message_id, self.nb_react
            )
        else:
            self.nb_react += 1
            self.is_reacted = True
            self.react_buttton.setText(" Remove react")
            self.controller.api_controller.send_emot_react(
                Commands.ADD_REACT, self.message_id, self.nb_react
            )

        self.react_nb.setText(f"{self.nb_react}")

        if self.nb_react == 0:
            self.react_emot.hide()
            self.react_nb.hide()
        else:
            self.react_emot.show()
            self.react_nb.show()

    def update_react(self, react_nb: int):
        self.nb_react = react_nb
        self.react_nb.setText(f"{self.nb_react}")
        if self.nb_react == 0:
            self.react_emot.hide()
            self.react_nb.hide()
        else:
            self.react_emot.show()
            self.react_nb.show()
