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
    QEnterEvent,
    QTimer,
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
    ADD = 1


class Contener(QFrame):
    def __init__(self):
        super(Contener, self).__init__()

    def enterEvent(self, event) -> None:
        if button_list := self.findChildren(CustomQPushButton):
            for button in button_list[1:]:
                button.show()

    def leaveEvent(self, event) -> None:
        if button_list := self.findChildren(CustomQPushButton):
            for button in button_list[1:]:
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
        response_model=False,
    ):
        super(MessageLayout, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        
        # Attributes
        self.controller = controller
        self.message_id = message_id
        self.is_reacted = False
        self.nb_react = nb_react
        self.content = content
        self.timer = QTimer()
        self.timer.setSingleShot(True)

        # --- Main widget
        self.main_widget = QWidget()

        self.addWidget(self.main_widget)
        self.main_widget.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value};\
            margin-bottom: 1px;\
            margin-right: 2px;"
        )
        main_layout = QHBoxLayout(self.main_widget)
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
        right_widget.setContentsMargins(0, 0, 0, 0)
        right_widget.setStyleSheet(
            f"background-color: transparent;\
            border-radius: 0px;"
        )
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        right_widget.setLayout(right_layout)

        main_layout.addWidget(right_widget)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        if not self.content:
            icon = QIcon(QIcon_from_svg(Icon.MESSAGE.value)).pixmap(QSize(15, 15))
            icon_label, copy_icon = QLabel(""), QLabel("")
            icon_label.setPixmap(icon)
            copy_icon.setPixmap(icon)
        else:
            icon_label, copy_icon = AvatarLabel(content=self.content), AvatarLabel(
                content=self.content, status=AvatarStatus.DM
            )
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.str_message = coming_msg["message"]
        sender = coming_msg["id"]

        self.username_label = check_str_len(sender)

        self.left_layout.addWidget(icon_label)

        self.sender_btn = CustomQPushButton(self.username_label)
        self.sender_btn.setFixedHeight(20)

        def hover(event: QEvent, user_widget):
            color = (
                Color.DARK_GREY.value
                if isinstance(event, QEnterEvent)
                else "transparent"
            )
            style_ = """
            QWidget {{
            font-weight: bold;
            background-color: {color};
            border-radius: 8px;
            border: 0px solid transparent;
            text-align: center;
            }} 
            """
            user_widget.setStyleSheet(style_.format(color=color))

        if sender != self.controller.ui.client.user_name:
            self.sender_btn.clicked.connect(
                functools.partial(self.add_dm_layout, copy_icon)
            )
            icon_label.mousePressEvent = lambda e : functools.partial(self.add_dm_layout, copy_icon)()

        if message_id and sender != self.controller.ui.client.user_name:
            self.sender_btn.enterEvent = functools.partial(
                hover, user_widget=self.sender_btn
            )
            self.sender_btn.leaveEvent = functools.partial(
                hover, user_widget=self.sender_btn
            )
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
            self.event_button = QWidget()
            self.event_button.setContentsMargins(0, 0, 0, 0)
            self.event_layout = QHBoxLayout(self.event_button)
            self.event_layout.setSpacing(0)
            self.event_layout.setContentsMargins(0, 0, 0, 0)
            self.react_buttton = CustomQPushButton(
                "", bg_color=Color.GREY.value, radius=4
            )
            retain = self.react_buttton.sizePolicy()
            retain.setRetainSizeWhenHidden(True)
            self.react_buttton.setSizePolicy(retain)

            self.react_buttton.clicked.connect(self.add_react)
            self.react_buttton.setFixedHeight(20)
            self.react_buttton.setFixedWidth(20)

            react_icon = QIcon(
                QIcon_from_svg(Icon.SMILEY.value, color=Color.YELLOW.value)
            )

            self.react_buttton.setIcon(react_icon)
            self.react_buttton.hide()
            self.event_layout.addWidget(self.react_buttton)

            self.reply_button = CustomQPushButton(
                "Reply", bg_color=Color.GREY.value, radius=4
            )

            self.reply_button.clicked.connect(self.add_reply)
            self.reply_button.setFixedSize(100, 20)
            response_icon = QIcon(
                QIcon_from_svg(Icon.REPLY.value, color=Color.WHITE.value)
            )
            self.reply_button.setIcon(response_icon)
            self.reply_button.hide()
            self.event_layout.addWidget(self.reply_button)
            # ---------------------------------------------------------------------------- #

        # -------------------------------- React widget ------------------------------- #
        react_layout = QHBoxLayout()
        react_layout.setSpacing(0)
        react_layout.setContentsMargins(3, 2, 3, 2)
        self.react_widget = QWidget()
        self.react_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.react_widget.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 6px;\
            font-weight: bold;\
            border: 1px solid {Color.MIDDLE_GREY.value};"
        )
        self.react_widget.setLayout(react_layout)
        self.react_emot = AvatarLabel(
            content=Icon.SMILEY.value,
            height=15,
            width=15,
            color=Color.YELLOW.value,
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
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        top_layout.addWidget(self.sender_btn)

        if "admin" in self.username_label:  # TODO: must be a column for user tab
            crown_icon = QIcon(
                QIcon_from_svg(Icon.CROWN.value, color=Color.YELLOW.value)
            ).pixmap(QSize(15, 15))
            sender_icon = QLabel()
            sender_icon.setContentsMargins(0, 0, 0, 3)
            sender_icon.setPixmap(crown_icon)
            top_layout.addWidget(sender_icon)

        if not date:
            date_time = datetime.datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
        else:
            dt_object = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")
            local_timezone = get_localzone()
            local_dt_object = dt_object.replace(tzinfo=pytz.utc).astimezone(
                local_timezone
            )
            date_time = local_dt_object.strftime("%d/%m/%Y à %H:%M:%S")

        date_label = QLabel(date_time)
        date_label.setContentsMargins(0, 0, 0, 0)
        date_label.setStyleSheet(
            f"border: 0px;\
            font-size: 8px;\
            color: {Color.LIGHT_GREY.value}"
        )
        top_layout.addWidget(date_label)

        message_label = QLabel(self.str_message)
        message_label.setStyleSheet("border: 0px; color: white;")
        message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
        message_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        top_layout.addWidget(self.event_button)

        # Add response model
        if response_model:
            icon_label.setStyleSheet("padding-top: 20px;")
            response_layout = QHBoxLayout()
            response_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            response_layout.setSpacing(5)

            model_icon = AvatarLabel(
                content=response_model.content, height=15, width=15
            )
            icon_label = QLabel()
            icon_reply = QIcon(
                QIcon_from_svg(Icon.LINK.value, color=Color.WHITE.value)
            ).pixmap(QSize(15, 15))
            icon_label.setPixmap(icon_reply)

            if len(response_model.str_message) > 50:
                model_message = f"{response_model.str_message[:50]}..."
            else:
                model_message = response_model.str_message

            model_message = QLabel(f"{model_message}")

            response_layout.addWidget(icon_label)
            response_layout.addWidget(model_icon)
            response_layout.addWidget(model_message)
            right_layout.addLayout(response_layout)
        else:
            icon_label.setStyleSheet("padding-top: 10px;")

        right_layout.addLayout(top_layout)
        right_layout.addWidget(message_label)
        right_layout.addWidget(self.react_widget)

        if message_id:
            self.update_react(self.nb_react)

    def add_react(self):
        if self.is_reacted:
            self.nb_react -= 1
            self.is_reacted = False
            self.controller.send_emot_react(
                Commands.RM_REACT, self.message_id, self.nb_react
            )
        else:
            self.nb_react += 1
            self.is_reacted = True
            self.controller.send_emot_react(
                Commands.ADD_REACT, self.message_id, self.nb_react
            )

        self.react_nb.setText(f"{self.nb_react}")

        if self.nb_react == 0:
            self.react_widget.hide()
        else:
            self.react_widget.show()

    def add_reply(self):
        self.controller.reply_to_message(self)

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

    def widget_shadow(self, widget: QWidget) -> None:
        result = QGraphicsDropShadowEffect()
        result.setColor(QColor(0, 0, 0, 150))
        result.setOffset(0, 1)
        result.setBlurRadius(1)
        widget.setGraphicsEffect(result)
