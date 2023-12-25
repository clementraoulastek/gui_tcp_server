import datetime
import functools
from enum import Enum, unique
from typing import Optional

import pytz
from tzlocal import get_localzone

from src.client.core.qt_core import (
    QColor,
    QEnterEvent,
    QEvent,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QIcon,
    QLabel,
    QSize,
    QSizePolicy,
    Qt,
    QTimer,
    QVBoxLayout,
    QWidget,
)
from src.client.view.custom_widget.custom_avatar_label import AvatarLabel, AvatarStatus
from src.client.view.custom_widget.custom_button import CustomQPushButton
from src.tools.commands import Commands
from src.tools.utils import Icon, Themes, check_str_len, icon_from_svg

theme = Themes()


@unique
class EnumReact(Enum):
    REMOVE = 0
    ADD = 1


class Contener(QFrame):
    def __init__(self):
        super(Contener, self).__init__()
        self.event_button = QWidget()

    def enterEvent(self, event) -> None:
        self.event_button.show()

    def leaveEvent(self, event) -> None:
        self.event_button.hide()


class MessageLayout(QHBoxLayout):
    def __init__(
        self,
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
        self.is_displayed = False
        self.timer = QTimer()
        self.timer.setSingleShot(True)

        # --- Main widget
        self.main_widget = QWidget()

        self.addWidget(self.main_widget)
        self.main_widget.setStyleSheet(
            f"color: {theme.title_color};\
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
        self.left_widget.setStyleSheet("padding: 0px; border: 0px;")
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

        icon_label, copy_icon = AvatarLabel(
            content=self.content,
            height=38,
            width=38,
        ), AvatarLabel(content=self.content, status=AvatarStatus.DM)
        icon_label.set_opacity(0.8)
        icon_label.graphicsEffect().setEnabled(False)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.str_message = coming_msg["message"]
        self.sender_ = coming_msg["id"]

        self.username_label = check_str_len(self.sender_)

        self.left_layout.addWidget(icon_label)

        self.sender_btn = CustomQPushButton(self.username_label)
        self.sender_btn.setFixedHeight(20)

        def hover(event: QEvent, user_widget):
            style_ = """
            font-weight: bold;
            background-color: transparent;
            border-radius: 4px;
            border: 0px solid transparent;
            text-align: center;
            """
            if isinstance(event, QEnterEvent):
                style_ += "text-decoration: underline;"

            user_widget.setStyleSheet(style_)

        if self.sender_ != self.controller.ui.client.user_name:
            self.sender_btn.clicked.connect(
                functools.partial(self.add_dm_layout, copy_icon)
            )
            icon_label.mousePressEvent = lambda e: functools.partial(
                self.add_dm_layout, copy_icon
            )()
            icon_label.leaveEvent = lambda e: functools.partial(
                icon_label.graphicsEffect().setEnabled, False
            )()
            icon_label.enterEvent = lambda e: functools.partial(
                icon_label.graphicsEffect().setEnabled, True
            )()

        if message_id and self.sender_ != self.controller.ui.client.user_name:
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
            right_widget.event_button = QWidget()
            right_widget.event_button.setStyleSheet(
                f"background-color: {theme.inner_color};\
                border: 1px solid {theme.nav_color};\
                border-radius: 6px;"
            )
            right_widget.event_button.setContentsMargins(0, 0, 0, 0)
            self.event_layout = QHBoxLayout(right_widget.event_button)
            self.event_layout.setSpacing(0)
            self.event_layout.setContentsMargins(1, 1, 1, 1)
            self.react_buttton = CustomQPushButton(
                "",
                bg_color=theme.inner_color,
                bg_color_active=theme.nav_color,
                radius=4,
            )
            self.react_buttton.setToolTip("React to this message")
            retain = self.react_buttton.sizePolicy()
            retain.setRetainSizeWhenHidden(True)
            self.react_buttton.setSizePolicy(retain)

            self.react_buttton.clicked.connect(self.add_react)
            self.react_buttton.setFixedHeight(20)
            self.react_buttton.setFixedWidth(20)

            react_icon = QIcon(
                icon_from_svg(Icon.SMILEY.value, color=theme.emoji_color)
            )

            self.react_buttton.setIcon(react_icon)
            self.event_layout.addWidget(self.react_buttton)

            self.reply_button = CustomQPushButton(
                "",
                bg_color=theme.inner_color,
                bg_color_active=theme.nav_color,
                radius=4,
            )
            self.reply_button.setToolTip("Reply to this message")

            self.reply_button.clicked.connect(self.add_reply)
            self.reply_button.setFixedSize(20, 20)
            response_icon = QIcon(
                icon_from_svg(Icon.REPLY.value, color=theme.emoji_color)
            )
            self.reply_button.setIcon(response_icon)
            self.event_layout.addWidget(self.reply_button)

            retain = right_widget.event_button.sizePolicy()
            retain.setRetainSizeWhenHidden(True)
            right_widget.event_button.setSizePolicy(retain)
            right_widget.event_button.hide()
            # ---------------------------------------------------------------------------- #

        # -------------------------------- React widget ------------------------------- #
        react_layout = QHBoxLayout()
        react_layout.setSpacing(0)
        react_layout.setContentsMargins(3, 2, 3, 2)
        self.react_widget = QWidget()
        self.react_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.react_widget.setStyleSheet(
            f"color: {theme.title_color};\
            background-color: {theme.inner_color};\
            border-radius: 6px;\
            font-weight: bold;\
            border: 1px solid {theme.nav_color};"
        )
        self.react_widget.setLayout(react_layout)
        self.react_emot = AvatarLabel(
            content=Icon.SMILEY.value,
            height=15,
            width=15,
            color=theme.emoji_color,
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
                icon_from_svg(Icon.CROWN.value, color=theme.emoji_color)
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
            date_time = local_dt_object.strftime("%d/%m/%Y at %H:%M:%S")

        date_label = QLabel(date_time)
        date_label.setContentsMargins(0, 0, 0, 0)
        date_label.setStyleSheet(
            f"border: 0px;\
            font-size: 8px;\
            color: {theme.rooms_color}"
        )
        top_layout.addWidget(date_label)

        message_label = QLabel(self.str_message)
        message_label.setStyleSheet(f"border: 0px; color: {theme.text_color};")
        message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
        message_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        top_layout.addWidget(
            right_widget.event_button, stretch=1, alignment=Qt.AlignmentFlag.AlignRight
        )

        # Add response model
        if response_model:
            icon_label.setStyleSheet("padding-top: 20px;")
            response_layout = QHBoxLayout()
            response_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            response_layout.setSpacing(0)

            model_icon = AvatarLabel(
                content=response_model.content,
                height=15,
                width=15,
            )
            icon_reply_label = QLabel()
            icon_reply = QIcon(
                icon_from_svg(Icon.LINK.value, color=theme.text_color)
            ).pixmap(QSize(15, 15))
            icon_reply_label.setPixmap(icon_reply)

            username_response = f"@{response_model.username_label}:"

            if len(response_model.str_message) > 60:
                model_message = f"{response_model.str_message[:50]}..."
            else:
                model_message = response_model.str_message

            model_username = QLabel(username_response)
            model_username.setContentsMargins(0, 0, 0, 0)
            model_username.setStyleSheet("font-weight: bold;")
            model_message = CustomQPushButton(
                model_message,
                color=theme.title_color,
            )
            model_message.setContentsMargins(0, 0, 0, 0)

            model_message.clicked.connect(
                functools.partial(self.controller.focus_in_message, response_model)
            )
            model_message.setFixedHeight(20)
            model_message.enterEvent = lambda e: model_message.setStyleSheet(
                f"color : {theme.rooms_color};"
            )
            model_message.leaveEvent = lambda e: model_message.setStyleSheet(
                f"color : {theme.title_color};"
            )
            response_layout.addWidget(
                icon_reply_label, alignment=Qt.AlignmentFlag.AlignHCenter
            )
            response_layout.addWidget(model_icon)
            response_layout.addWidget(model_username)
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
