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
from src.tools.constant import SOFT_VERSION
from src.tools.utils import GenericColor, Themes, Icon, ImageAvatar, QIcon_from_svg


class FooterView:
    def __init__(self, controller, version_widget_width, theme: Themes) -> None:
        self.controller = controller
        self.version_widget_width = version_widget_width
        self.theme = theme
        self.set_footer_gui()

    def set_footer_gui(self) -> None:
        """
        Update the footer GUI
        """
        self.logout_button = CustomQPushButton()
        self.logout_button.setToolTip("Logout")
        self.logout_button.setFixedHeight(30)
        self.logout_button.setFixedWidth(30)
        self.logout_button.clicked.connect(self.controller.logout)
        self.logout_icon = QIcon(QIcon_from_svg(Icon.LOGOUT.value, color=self.theme.text_color))
        self.logout_button.setIcon(self.logout_icon)
        self.logout_button.setDisabled(True)
        
        settings_btn = CustomQPushButton()
        settings_btn.setToolTip("Settings")
        settings_btn.setFixedHeight(30)
        settings_btn.setFixedWidth(30)
        settings_btn.clicked.connect(self.controller.gui_controller.show_user_profile)
        settings_icon = QIcon(QIcon_from_svg(Icon.CONFIG.value, color=self.theme.text_color))
        settings_btn.setIcon(settings_icon)

        self.send_widget = QWidget()
        self.send_layout = QHBoxLayout(self.send_widget)
        self.send_layout.setObjectName("send layout")
        self.send_layout.setContentsMargins(0, 0, 0, 0)
        self.send_layout.setSpacing(5)

        # --- Client information
        self.user_info_widget = QWidget()
        self.user_info_widget.setFixedWidth(310)
        self.client_information_dashboard_layout = QHBoxLayout(self.user_info_widget)
        self.client_information_dashboard_layout.setContentsMargins(0, 0, 0, 0)
        self.user_info_widget.setStyleSheet(
            f"background-color: {self.theme.search_color};\
            color: {self.theme.title_color};\
            border-radius: 0px;\
            border: 0px;"
        )
        self.user_icon = QIcon(QIcon_from_svg(Icon.AVATAR.value, color=self.theme.text_color))

        self.user_widget = QWidget()
        
        self.user_picture = AvatarLabel(content="")
        self.user_picture.setToolTip("Update your avatar")
        self.user_picture.enterEvent = lambda event: self.user_picture.graphicsEffect().setEnabled(True)
        self.user_picture.leaveEvent = lambda event: self.user_picture.graphicsEffect().setEnabled(False)
        self.user_picture.mousePressEvent = lambda e : self.controller.show_user_profile()
        self.user_picture.set_opacity(0.8)
        self.user_picture.graphicsEffect().setEnabled(False)
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

        avatar_layout = QHBoxLayout(self.user_widget)
        avatar_layout.setSpacing(5)

        avatar_layout.addWidget(self.user_picture)
        avatar_layout.addWidget(
            user_widget_status, stretch=1, alignment=Qt.AlignmentFlag.AlignLeft
        )
        avatar_layout.addWidget(settings_btn, stretch=2, alignment=Qt.AlignmentFlag.AlignLeft)
        avatar_layout.addWidget(self.logout_button)

        self.client_information_dashboard_layout.addWidget(self.user_widget)

        self.entry = CustomQLineEdit(place_holder_text="Please login", radius=4)
        self.entry.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.entry.setTextMargins(0, 0, 0, 0)
        self.entry.returnPressed.connect(self.controller.send_message_to_server)

        self.send_layout.addWidget(self.user_info_widget)
        self.send_layout.addWidget(self.entry, alignment=Qt.AlignmentFlag.AlignTop)

        pipe_icon = QIcon(QIcon_from_svg(Icon.SEPARATOR.value, self.theme.title_color))
        send_icon = QIcon(QIcon_from_svg(Icon.SEND.value, self.theme.title_color))
        reply_icon = QIcon(QIcon_from_svg(Icon.CLOSE.value, GenericColor.RED.value))
        file_icon = QIcon(QIcon_from_svg(Icon.FILE.value, self.theme.title_color))
        
        entry_action = self.entry.addAction(send_icon, QLineEdit.TrailingPosition)
        entry_action.setToolTip("Send message")
        self.entry.addAction(pipe_icon, QLineEdit.TrailingPosition)
        entry_action.triggered.connect(self.controller.send_message_to_server)
        
        self.file_action = self.entry.addAction(file_icon, QLineEdit.ActionPosition.LeadingPosition)
        self.file_action.setToolTip("Send file")
        
        self.reply_entry_action = self.entry.addAction(
            reply_icon, QLineEdit.ActionPosition.LeadingPosition
        )
        self.reply_entry_action.setVisible(False)

        self.bottom_right_widget = QWidget()
        self.bottom_right_widget.setContentsMargins(0, 5, 0, 5)
        self.bottom_right_widget.setMinimumWidth(self.version_widget_width)
        self.bottom_right_widget.setStyleSheet(
            f"background-color: {self.theme.search_color};\
            color: {self.theme.title_color};"
        )
        self.bottom_right_layout = QVBoxLayout(self.bottom_right_widget)
        self.bottom_right_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_right_layout.setSpacing(5)
        version_widget = QWidget()
        version_widget.setContentsMargins(10, 0, 0, 0)
        version_layout = QHBoxLayout(version_widget)
        version_layout.setContentsMargins(0, 0, 0, 0)
        version_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        version_layout.setSpacing(10)

        lang_widget = QWidget()
        lang_widget.setContentsMargins(10, 0, 0, 0)
        theme_layout = QHBoxLayout(lang_widget)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        theme_layout.setSpacing(10)

        icon_soft = AvatarLabel(content=ImageAvatar.SERVER.value, height=20, width=20)
        theme_label = QLabel()
        theme_color = QIcon(QIcon_from_svg(Icon.STATUS.value, color=self.theme.color))
        theme_label.setPixmap(theme_color.pixmap(20, 20))
        self.switch_theme_button = CustomQPushButton("")
        self.switch_theme_button.setToolTip("Switch theme")
        self.switch_theme_button.setFixedSize(20, 20)
        self.switch_theme_button.setIcon(QIcon(QIcon_from_svg(Icon.SWITCH_COLOR.value, color=self.theme.text_color)))
        self.switch_theme_button.clicked.connect(lambda: self.controller.gui_controller.display_theme_board())
        
        value = QLabel(f"Alpha <strong>{SOFT_VERSION}</strong>")
        theme_name = QLabel(f"<strong>{self.theme.theme_name}</strong")

        theme_name.setContentsMargins(0, 0, 0, 0)

        version_layout.addWidget(icon_soft)
        version_layout.addWidget(value)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(theme_name)
        theme_layout.addWidget(self.switch_theme_button)

        self.bottom_right_layout.addWidget(version_widget)
        self.bottom_right_layout.addWidget(lang_widget)

        self.send_layout.addWidget(self.bottom_right_widget)
