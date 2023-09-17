from src.client.core.qt_core import (
    QIcon,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    Qt,
    QLineEdit,
)
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.view.customWidget.AvatarQLabel import AvatarLabel
from src.tools.constant import SOFT_VERSION, LANGUAGE
from src.tools.utils import Color, Icon, ImageAvatar, QIcon_from_svg


class FooterView:
    def __init__(self, controller, version_widget_width) -> None:
        self.controller = controller
        self.version_widget_width = version_widget_width
        self.set_footer_gui()

    def set_footer_gui(self) -> None:
        """
        Update the footer GUI
        """
        self.logout_button = CustomQPushButton()
        self.logout_button.setFixedHeight(30)
        self.logout_button.setFixedWidth(30)
        self.logout_button.clicked.connect(self.controller.logout)
        self.logout_icon = QIcon(QIcon_from_svg(Icon.LOGOUT.value))
        self.logout_button.setIcon(self.logout_icon)
        self.logout_button.setDisabled(True)

        self.send_widget = QWidget()
        self.send_layout = QHBoxLayout(self.send_widget)
        self.send_layout.setObjectName("send layout")
        self.send_layout.setContentsMargins(0, 0, 0, 0)
        self.send_layout.setSpacing(5)

        # --- Client information
        self.user_info_widget = QWidget()
        self.user_info_widget.setFixedWidth(250)
        self.client_information_dashboard_layout = QHBoxLayout(self.user_info_widget)
        self.client_information_dashboard_layout.setContentsMargins(0, 0, 0, 0)
        self.user_info_widget.setStyleSheet(
            f"background-color: {Color.LIGHT_BLACK.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 0px;\
            border: 0px;"
        )
        self.user_icon = QIcon(QIcon_from_svg(Icon.AVATAR.value))

        self.user_widget = QWidget()
        self.custom_user_button = CustomQPushButton("")
        self.custom_user_button.setFixedHeight(30)
        self.custom_user_button.setFixedWidth(30)

        self.user_picture = AvatarLabel(content="")
        self.user_picture.setStyleSheet("border: 0px")

        user_widget_status = QWidget()
        user_widget_status.setContentsMargins(0, 0, 0, 0)
        user_widget_status_layout = QVBoxLayout(user_widget_status)
        user_widget_status_layout.setSpacing(0)
        user_widget_status_layout.setContentsMargins(10, 0, 0, 0)

        self.user_name = QLabel("User disconnected")
        self.user_name.setStyleSheet(
            "font-weight: bold;\
            border: none;"
        )
        user_status = QLabel("Connected")
        user_status.setStyleSheet(
            "font-size: 10px;\
            border: none;"
        )
        user_widget_status_layout.addWidget(self.user_name)
        user_widget_status_layout.addWidget(user_status)

        self.custom_user_button.setIcon(self.user_icon)
        self.custom_user_button.clicked.connect(self.controller.update_user_icon)
        self.custom_user_button.setEnabled(False)

        avatar_layout = QHBoxLayout(self.user_widget)
        avatar_layout.setSpacing(5)

        avatar_layout.addWidget(self.user_picture)
        avatar_layout.addWidget(
            user_widget_status, stretch=1, alignment=Qt.AlignmentFlag.AlignLeft
        )
        avatar_layout.addWidget(self.custom_user_button)
        avatar_layout.addWidget(self.logout_button)

        self.client_information_dashboard_layout.addWidget(self.user_widget)

        self.entry = CustomQLineEdit(place_holder_text="Please login")
        self.entry.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.entry.setTextMargins(0, 0, 0, 0)
        self.entry.returnPressed.connect(self.controller.send_message_to_server)

        self.send_layout.addWidget(self.user_info_widget)
        self.send_layout.addWidget(self.entry)

        pipe_icon = QIcon(QIcon_from_svg(Icon.SEPARATOR.value, Color.LIGHT_GREY.value))
        send_icon = QIcon(QIcon_from_svg(Icon.SEND.value, Color.LIGHT_GREY.value))
        reply_icon = QIcon(QIcon_from_svg(Icon.CLOSE.value, Color.LIGHT_GREY.value))

        entry_action = self.entry.addAction(send_icon, QLineEdit.TrailingPosition)
        self.entry.addAction(pipe_icon, QLineEdit.TrailingPosition)
        entry_action.triggered.connect(self.controller.send_message_to_server)

        self.reply_entry_action = self.entry.addAction(
            reply_icon, QLineEdit.ActionPosition.LeadingPosition
        )
        self.reply_entry_action.setVisible(False)

        bottom_right_widget = QWidget()
        bottom_right_widget.setContentsMargins(0, 0, 0, 0)
        bottom_right_widget.setMinimumWidth(self.version_widget_width)
        bottom_right_widget.setStyleSheet(
            f"font-style: italic;\
            background-color: {Color.LIGHT_BLACK.value};\
            color: {Color.LIGHT_GREY.value}"
        )
        bottom_right_layout = QVBoxLayout(bottom_right_widget)
        bottom_right_layout.setContentsMargins(0, 0, 0, 0)
        bottom_right_layout.setSpacing(0)
        version_widget = QWidget()
        version_widget.setContentsMargins(10, 0, 0, 0)
        version_layout = QHBoxLayout(version_widget)
        version_layout.setContentsMargins(0, 0, 0, 0)
        version_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        version_layout.setSpacing(10)

        lang_widget = QWidget()
        lang_widget.setContentsMargins(10, 0, 0, 0)
        lang_layout = QHBoxLayout(lang_widget)
        lang_layout.setContentsMargins(0, 0, 0, 0)
        lang_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lang_layout.setSpacing(10)

        icon_soft = AvatarLabel(content=ImageAvatar.SERVER.value, height=20, width=20)
        lang_soft = AvatarLabel(content=ImageAvatar.EN.value, height=20, width=20)
        value = QLabel(f"Alpha, Version: {SOFT_VERSION}")
        language = QLabel(f"Language: {LANGUAGE}")

        language.setContentsMargins(0, 0, 0, 0)

        version_layout.addWidget(icon_soft)
        version_layout.addWidget(value)

        lang_layout.addWidget(lang_soft)
        lang_layout.addWidget(language)

        bottom_right_layout.addWidget(version_widget)
        bottom_right_layout.addWidget(lang_widget)

        self.send_layout.addWidget(bottom_right_widget)
