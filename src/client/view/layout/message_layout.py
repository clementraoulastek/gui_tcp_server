from enum import Enum, unique
import datetime
import functools
import logging
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
    QStackedLayout,
    QLayout,
)
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.tools.commands import Commands
from src.tools.utils import Color, Icon, QIcon_from_svg, check_str_len
from src.client.view.customWidget.CustomQLabel import RoundedLabel
import copy


@unique
class EnumReact(Enum):
    REMOVE = 0
    ADD = 1


class UserMenu(QWidget):
    def __init__(self, user):
        super().__init__()
        self.setStyleSheet("background-color: red;")
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedWidth(170)

        self.layout_ = QVBoxLayout()
        self.layout_.setSpacing(0)
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignCenter)

        msg_icon = QIcon(QIcon_from_svg(Icon.MESSAGE.value))

        self.send_msg_btn = CustomQPushButton(" Send message")
        self.send_msg_btn.setIcon(msg_icon)
        list_buttons = [self.send_msg_btn]
        self.setFixedHeight(60 * len(list_buttons))
        self.setLayout(self.layout_)
        for widget in list_buttons:
            self.layout_.addWidget(widget)


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

        # --- Main widget
        main_widget = QWidget()
        self.addWidget(main_widget)
        main_widget.setStyleSheet(f"color: {Color.LIGHT_GREY.value};")

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Left widget
        self.left_layout = QVBoxLayout()
        self.left_layout.setSpacing(0)
        self.left_widget = QWidget()
        self.left_widget.setMaximumWidth(80)
        self.left_widget.setMinimumWidth(80)

        self.left_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.left_widget.setLayout(self.left_layout)
        main_layout.addWidget(self.left_widget)

        # --- Right widget
        right_widget = Contener()
        right_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            border-radius: 15px;\
            border: 1px solid {Color.MIDDLE_GREY.value}; "
        )
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        main_layout.addWidget(right_widget)

        right_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

        if not content:
            icon = QIcon(QIcon_from_svg(Icon.MESSAGE.value)).pixmap(QSize(15, 15))
            icon_label, copy_icon = QLabel(""), QLabel("")
            icon_label.setPixmap(icon)
            copy_icon.setPixmap(icon)
        else:
            icon_label, copy_icon = RoundedLabel(content=content), RoundedLabel(
                content=content
            )
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_layout.addWidget(icon_label)
        str_message = coming_msg["message"]
        sender = coming_msg["id"]

        sender_layout = QHBoxLayout()
        sender_layout.setAlignment(Qt.AlignCenter | Qt.AlignLeft)
        self.username_label = check_str_len(sender)

        self.sender_btn = CustomQPushButton(self.username_label)
        self.user_menu = UserMenu(self.username_label)

        self.user_menu.send_msg_btn.clicked.connect(
            functools.partial(self.add_dm_layout, copy_icon)
        )
        self.user_menu.hide()
        self.left_layout.addWidget(self.sender_btn)
        if message_id:
            self.sender_btn.clicked.connect(self.display_menu)
            main_layout.addChildWidget(self.user_menu)
            self.user_menu.move(
                self.user_menu.x() - 10, self.user_menu.y() + 40
            )
            style_ = """
            QPushButton {{
            font-weight: bold;
            border: 0px;
            color: {color};
            }} 
            QPushButton:hover {{
            text-decoration: underline;
            }}
            """
            self.user_menu.leaveEvent = lambda e: self.hide_menu()
        else:
            style_ = """
            QPushButton {{
            font-weight: bold;
            border: 0px;
            color: {color};
            }}
            """
        self.sender_btn.setStyleSheet(style_.format(color=Color.WHITE.value))

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
            self.react_nb.setStyleSheet(
                "font-weight: bold;\
                border: 0px"
            )
            self.react_nb.hide()

            emot_layout.addWidget(self.react_emot)
            emot_layout.addWidget(self.react_nb)

        date_time = datetime.datetime.now().strftime("%m/%d/%Y à %H:%M:%S")
        date_label = QLabel(date_time)
        date_label.setStyleSheet("border: 0px; text-decoration: ")

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

    def display_menu(self):
        if self.user_menu.isHidden():
            self.user_menu.show()
            self.user_menu.setFocus()

    def hide_menu(self):
        if not self.user_menu.isHidden():
            self.user_menu.hide()

    def add_dm_layout(self, icon_label):
        self.controller.add_gui_for_mp_layout(self.username_label, icon_label)
        self.hide_menu()
