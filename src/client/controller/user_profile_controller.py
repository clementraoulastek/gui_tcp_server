"""Module for the user profile controller."""

import datetime

import pytz
from tzlocal import get_localzone

from src.client.core.qt_core import (
    QHBoxLayout,
    QIcon,
    QLabel,
    QPlainTextEdit,
    QSize,
    Qt,
    QVBoxLayout,
    QWidget,
)
from src.client.view.custom_widget.custom_avatar_label import AvatarLabel, AvatarStatus
from src.client.view.custom_widget.custom_button import CustomQPushButton
from src.tools.utils import GenericColor, Icon, icon_from_svg


class UserProfileController:
    """
    Class that handle the user profile.
    """

    def __init__(self, parent, ui):
        self.parent = parent
        self.ui = ui
        self.user_profile_widget = None
        self.status_widget = None

    def update_user_icon(self) -> None:
        """
        Update user icon
        """
        username = self.ui.client.user_name
        if self.ui.backend.send_user_icon(username, None):
            self.parent.avatar_controller.clear_avatar(
                "user_inline", self.ui.left_nav_widget, f"{username}_layout"
            )
            self.parent.api_controller.get_user_icon(update_personal_avatar=True)
            self.user_profile_widget.hide()

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    def show_user_profile(self) -> None:
        """
        Show user profile
        """
        if self.user_profile_widget and self.user_profile_widget.isVisible():
            return

        creation_date, description = self.parent.api_controller.get_user_creation_date(
            self.ui.client.user_name
        )
        local_timezone = get_localzone()
        dt_object = datetime.datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        local_dt_object = dt_object.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        date_time = local_dt_object.strftime("%d/%m/%Y at %H:%M:%S")
        self.user_profile_widget = QWidget()
        self.user_profile_widget.setStyleSheet(
            f"border-radius: 8px; border: 1px solid; border-color: {self.parent.theme.nav_color};"
        )
        height = 250
        self.user_profile_widget.move(
            self.ui.footer_widget.user_info_widget.x() + 15,
            self.ui.footer_widget.send_widget.y() - height,
        )
        self.user_profile_widget.setFixedSize(
            QSize(self.ui.footer_widget.user_info_widget.width() // 1.5, height)
        )
        user_profile_layout = QVBoxLayout(self.user_profile_widget)
        user_profile_layout.setSpacing(5)
        user_profile_layout.setContentsMargins(5, 5, 5, 5)

        # Add user avatar
        user_avatar = AvatarLabel(
            content=self.ui.users_pict[self.ui.client.user_name],
            status=AvatarStatus.ACTIVATED,
        )
        user_name = QLabel(self.ui.client.user_name)
        user_name.setStyleSheet(
            f"font-weight: bold;\
            border: 0px solid;\
            color: {self.parent.theme.text_color};"
        )

        user_info = QLabel(
            f"<strong>Creation date:</strong>\
            <br>\
            {date_time}\
            <br><br>\
            <strong>Description:</strong>"
        )
        user_info.setWordWrap(True)
        user_info.setStyleSheet(
            f"border: 0px solid;\
            color: {self.parent.theme.text_color};"
        )
        user_info.setContentsMargins(5, 5, 5, 5)

        self.status_widget = QPlainTextEdit()
        self.status_widget.setContentsMargins(5, 5, 5, 5)
        self.status_widget.setPlaceholderText(
            description or "Write your description here 🌈"
        )
        self.status_widget.setStyleSheet(
            f"background-color: {self.parent.theme.inner_color};\
            color: {self.parent.theme.text_color};"
        )
        self.status_widget.setFixedHeight(60)

        user_action_widget = QWidget()
        user_action_widget.setFixedHeight(40)
        user_action_widget.setStyleSheet(
            f"border: 0px solid; background-color: {self.parent.theme.search_color};"
        )
        user_action_layout = QHBoxLayout(user_action_widget)
        user_action_layout.setContentsMargins(0, 0, 0, 0)

        user_info_layout = QHBoxLayout()
        user_info_layout.setContentsMargins(10, 10, 10, 10)
        user_info_layout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        user_info_layout.setSpacing(10)

        # Add user update button
        update_button = CustomQPushButton(" Upload")
        update_button.setToolTip("Update Avatar")
        update_button.setFixedSize(QSize(80, 30))
        update_button.clicked.connect(self.update_user_icon)

        save_button = CustomQPushButton("")
        update_user_icon = QIcon(
            icon_from_svg(Icon.SAVE.value, color=self.parent.theme.text_color)
        )
        save_button.setIcon(update_user_icon)
        save_button.setFixedSize(QSize(30, 30))
        save_button.clicked.connect(self.update_user_description)

        close_btn = CustomQPushButton()
        close_btn.clicked.connect(self.user_profile_widget.hide)
        close_btn.setToolTip("Close")
        close_btn.setFixedSize(QSize(30, 30))

        update_user_icon = QIcon(
            icon_from_svg(Icon.FILE.value, color=self.parent.theme.text_color)
        )
        close_icon = QIcon(
            icon_from_svg(Icon.CLOSE.value, color=GenericColor.RED.value)
        )
        update_button.setIcon(update_user_icon)
        close_btn.setIcon(close_icon)

        user_info_layout.addWidget(
            user_avatar,
        )
        user_info_layout.addWidget(user_name)
        user_action_layout.addWidget(update_button)
        user_action_layout.addWidget(save_button)
        user_action_layout.addWidget(close_btn)

        user_profile_layout.addLayout(user_info_layout)
        user_profile_layout.addWidget(user_info, alignment=Qt.AlignmentFlag.AlignTop)
        user_profile_layout.addWidget(
            self.status_widget, alignment=Qt.AlignmentFlag.AlignTop
        )
        user_profile_layout.addWidget(user_action_widget)

        self.ui.main_layout.addChildWidget(self.user_profile_widget)
        self.user_profile_widget.setFocus()

    def update_user_description(self) -> None:
        """
        Update user description
        """
        self.parent.api_controller.update_user_description(
            self.ui.client.user_name, self.status_widget.toPlainText()
        )
        self.user_profile_widget.hide()
