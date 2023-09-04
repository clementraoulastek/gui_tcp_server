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
    QGraphicsDropShadowEffect,
    QColor,
    QPoint,
    QEvent,
    QEnterEvent
)
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.tools.graphical_effects import widget_shadow
from src.tools.commands import Commands
from src.tools.utils import Color, Icon, QIcon_from_svg, check_str_len
from src.client.view.customWidget.AvatarQLabel import AvatarLabel
from src.client.view.customWidget.AvatarQLabel import AvatarStatus
import pytz
from tzlocal import get_localzone


@unique
class EnumReact(Enum):
    REMOVE = 0
    ADD    = 1

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
    def __init__(
        self,
        parent: QWidget,
        controller,
        coming_msg: dict,
        nb_react: Optional[int] = 0,
        content: Optional[None] = None,
        message_id: Optional[None] = None,
        date: Optional[str] = "",
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
        main_widget.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value};\
            margin-bottom: 1px;\
            margin-right: 2px;"
        )
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Left widget
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)
        self.left_widget = QWidget()
        self.left_widget.setStyleSheet("padding: 0px;")
        self.left_widget.setMaximumWidth(80)
        self.left_widget.setMinimumWidth(80)

        self.left_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.left_widget.setLayout(self.left_layout)
        main_layout.addWidget(self.left_widget)

        # --- Right widget
        right_widget = Contener()
        shadow = self.widget_shadow(right_widget)
        right_widget.setStyleSheet(
            f"background-color: transparent;\
            border-radius: 12px;"
        )
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        right_widget.setLayout(right_layout)

        main_layout.addWidget(right_widget)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        if not content:
            icon = QIcon(QIcon_from_svg(Icon.MESSAGE.value)).pixmap(QSize(15, 15))
            icon_label, copy_icon = QLabel(""), QLabel("")
            icon_label.setPixmap(icon)
            copy_icon.setPixmap(icon)
        else:
            icon_label, copy_icon = AvatarLabel(content=content), AvatarLabel(
                content=content, status=AvatarStatus.DM
            )
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            widget_shadow(icon_label)
        
        str_message = coming_msg["message"]
        sender = coming_msg["id"]
        
        self.username_label = check_str_len(sender)
        if "admin" in self.username_label:
            crown_icon = QIcon(QIcon_from_svg(Icon.CROWN.value, color=Color.YELLOW.value)).pixmap(QSize(15, 15))
            sender_icon = QLabel()
            sender_icon.setPixmap(crown_icon)
            self.left_layout.addWidget(sender_icon, alignment=Qt.AlignCenter)
            
        self.left_layout.addWidget(icon_label)
        sender_layout = QHBoxLayout()
        sender_layout.setSpacing(10)
        sender_layout.setAlignment(Qt.AlignCenter | Qt.AlignLeft)

        self.sender_btn = CustomQPushButton(self.username_label)
        self.sender_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        def hover(event: QEvent, user_widget):
            if isinstance(event, QEnterEvent):
                color = Color.GREY.value
            else:
                color = "transparent"
            style_ = """
            QWidget {{
            font-weight: bold;
            background-color: {color};
            border-radius: none;
            border: 0px solid;
            }} 
            """
            user_widget.setStyleSheet(style_.format(color=color))
        
        self.sender_btn.clicked.connect(
            functools.partial(self.add_dm_layout, copy_icon)
        )
        self.left_layout.addWidget(self.sender_btn)

        if message_id and sender != self.controller.ui.client.user_name:
            self.sender_btn.enterEvent = functools.partial(hover, user_widget=self.sender_btn)
            self.sender_btn.leaveEvent = functools.partial(hover, user_widget=self.sender_btn)
            style_ = """
            QPushButton {{
            font-weight: bold;
            }} 
            """
        else:
            style_ = """
            QPushButton {{
            font-weight: bold;
            border: 0px;
            }}
            """
        self.sender_btn.setStyleSheet(style_.format())

        if message_id:
            # ------------------------------- React Button ------------------------------- #
            self.react_buttton = CustomQPushButton(
                "", bg_color=Color.GREY.value, radius=4
            )
            widget_shadow(self.react_buttton)
            self.react_buttton.clicked.connect(self.add_react)
            self.react_buttton.setFixedHeight(13)
            self.react_buttton.setFixedWidth(13)
            self.react_buttton.setContentsMargins(0, 0, 0, 0)
            react_icon = QIcon(QIcon_from_svg(Icon.SMILEY.value))

            self.react_buttton.setIcon(react_icon)
            self.react_buttton.hide()
            # ---------------------------------------------------------------------------- #

        # -------------------------------- React widget ------------------------------- #
        react_layout = QHBoxLayout()
        react_layout.setSpacing(5)
        react_layout.setContentsMargins(3, 2, 3, 2)
        self.react_widget = QWidget()
        self.react_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        shadow = self.widget_shadow(self.react_widget)
        self.react_widget.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 6px;\
            font-weight: bold;\
            border: 1px solid {Color.MIDDLE_GREY.value};"
        )
        self.react_widget.setGraphicsEffect(shadow)
        self.react_widget.setLayout(react_layout)
        self.react_emot = AvatarLabel(
            content=Icon.SMILEY.value,
            height=15,
            width=15,
            color=Color.WHITE.value,
        )
        self.react_emot.setContentsMargins(0, 0, 0, 0)
        self.react_emot.setStyleSheet("border: 0px;")
        self.react_nb = QLabel("1")

        self.react_emot.setAlignment(Qt.AlignLeft)
        self.react_nb.setAlignment(Qt.AlignLeft)
        self.react_nb.setStyleSheet("border: 0px")
        react_layout.addWidget(self.react_emot)
        react_layout.addWidget(self.react_nb)
        # ---------------------------------------------------------------------------- #

        if not date:
            date_time = datetime.datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
        else:
            dt_object = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")
            local_timezone = get_localzone()
            local_dt_object = dt_object.replace(tzinfo=pytz.utc).astimezone(local_timezone) 
            date_time = local_dt_object.strftime("%d/%m/%Y à %H:%M:%S")
            
        date_label = QLabel(date_time)
        date_label.setStyleSheet(
            "border: 0px;\
            font-style: italic;\
            font-size: 10px;"
        )
        sender_layout.addWidget(date_label)

        if message_id:
            sender_layout.addWidget(self.react_buttton)

        message_label = QLabel(str_message)
        message_label.setStyleSheet("border: 0px; color: white;")
        message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
        message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        right_layout.addLayout(sender_layout)
        right_layout.addWidget(message_label)
        right_layout.addWidget(self.react_widget)
        
        if message_id:
            self.update_react(self.nb_react)

    def add_react(self):
        if self.is_reacted:
            self.nb_react -= 1
            self.is_reacted = False
            self.controller.api_controller.send_emot_react(
                Commands.RM_REACT, self.message_id, self.nb_react
            )
        else:
            self.nb_react += 1
            self.is_reacted = True
            self.controller.api_controller.send_emot_react(
                Commands.ADD_REACT, self.message_id, self.nb_react
            )

        self.react_nb.setText(f"{self.nb_react}")

        if self.nb_react == 0:
            self.react_widget.hide()
        else:
            self.react_widget.show()

    def update_react(self, react_nb: int):
        self.nb_react = react_nb
        if self.nb_react == 0:
            self.react_widget.hide()
        else:
            self.react_widget.show()
        self.react_widget.update()
        self.react_nb.setText(f"{self.nb_react}")


    def add_dm_layout(self, icon_label):
        self.controller.add_gui_for_mp_layout(
            self.username_label, icon_label, switch_frame=True
        )

    def widget_shadow(self, widget):
        result = QGraphicsDropShadowEffect(widget)
        result.setColor(QColor(0, 0, 0, 150))
        result.setOffset(0, 1)
        result.setBlurRadius(1)
        return result
