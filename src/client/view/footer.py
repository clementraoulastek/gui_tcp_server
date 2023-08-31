from src.client.core.qt_core import (
    QIcon,
    QWidget,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
    QColor,
    QLabel,
    Qt
)
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.customWidget.CustomQLineEdit import CustomQLineEdit
from src.client.view.customWidget.AvatarQLabel import AvatarLabel
from src.tools.constant import SOFT_VERSION
from src.tools.utils import Color, Icon, QIcon_from_svg
from src.client.view.tools.graphical_effects import widget_shadow


class FooterView:
    def __init__(self, controller, version_widget_width) -> None:
        self.controller = controller
        self.version_widget_width = version_widget_width
        self.set_footer_gui()  
        
    def set_footer_gui(self) -> None:
        """
        Update the footer GUI
        """
        self.logout_button = CustomQPushButton(" Logout")
        widget_shadow(self.logout_button)

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
        self.client_information_dashboard_layout = QHBoxLayout(self.user_info_widget)
        self.client_information_dashboard_layout.setContentsMargins(0, 0, 0, 0)
        self.user_info_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 12px;\
            border: 1px solid {Color.MIDDLE_GREY.value};\
            margin-bottom: 2px;"
        )
        self.user_icon = QIcon(QIcon_from_svg(Icon.AVATAR.value))

        self.user_widget = QWidget()
        shadow = QGraphicsDropShadowEffect(self.user_widget)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 2)
        shadow.setBlurRadius(1)
        self.user_widget.setGraphicsEffect(shadow)
        shadow.update()

        self.user_widget.setStyleSheet(
            f"border: 1px solid {Color.MIDDLE_GREY.value};"
        )
        self.custom_user_button = CustomQPushButton("")
        widget_shadow(self.custom_user_button)

        self.user_picture = AvatarLabel(content="")
        self.user_picture.setStyleSheet("border: 0px")
        self.user_name = QLabel("User disconnected")
        self.user_name.setStyleSheet(
            "font-weight: bold;\
            border: none;"
        )

        self.custom_user_button.setIcon(self.user_icon)
        self.custom_user_button.setFixedWidth(50)
        self.custom_user_button.clicked.connect(self.controller.update_user_icon)
        self.custom_user_button.setEnabled(False)

        avatar_layout = QHBoxLayout(self.user_widget)

        avatar_layout.addWidget(self.user_picture)
        avatar_layout.addWidget(self.user_name)
        avatar_layout.addWidget(self.custom_user_button)
        avatar_layout.addWidget(self.logout_button)

        self.client_information_dashboard_layout.addWidget(self.user_widget)

        self.entry = CustomQLineEdit(place_holder_text="Please login")
        self.entry.returnPressed.connect(self.controller.send_message_to_server)
        self.send_layout.addWidget(self.user_info_widget)
        self.send_layout.addWidget(self.entry)

        self.send_button = CustomQPushButton("")
        widget_shadow(self.send_button)
        self.send_button.clicked.connect(self.controller.send_message_to_server)
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)

        version_widget = QLabel(f"Version: {SOFT_VERSION}")
        version_widget.setStyleSheet(
            f"font-style: italic; color: {Color.LIGHT_GREY.value}"
        )
        version_widget.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        version_widget.setMinimumWidth(self.version_widget_width)

        self.send_layout.addWidget(self.send_button)
        self.send_layout.addWidget(version_widget)
        