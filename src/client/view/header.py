
from src.client.core.qt_core import (
    QWidget,
    QHBoxLayout,
    Qt,
    QLabel,
    QLayout,
    QIcon
)
from src.client.view.customWidget.AvatarQLabel import AvatarLabel
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.tools.graphical_effects import widget_shadow
from src.tools.constant import DEFAULT_CLIENT_NAME
from src.tools.utils import Color, Icon, ImageAvatar, QIcon_from_svg

class HeaderView:
    def __init__(self, controller) -> None:
        self.controller = controller
        self.set_header_gui()
    
    def set_header_gui(self) -> None:
        """
        Set the header GUI
        """
        # Header widget
        self.main_widget = QWidget()

        self.main_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 0px;\
            border: 1px solid;\
            border-color: {Color.MIDDLE_GREY.value};"
        )
        
        # Header layout
        header_layout = QHBoxLayout(self.main_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        # Logo widget
        logo_widget = QWidget()
        
        # Logo layout
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setSpacing(10)
        logo_widget.setStyleSheet("border: none")
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        icon_soft = AvatarLabel(content=ImageAvatar.SERVER.value, height=20, width=20)
        icon_soft.setStyleSheet(
            "font-weight: bold;\
            border: none"
        )
        
        # Status server label
        status_server_label = QLabel(DEFAULT_CLIENT_NAME.upper())
        status_server_label.setStyleSheet(
            "font-weight: bold;\
            border: none;\
            font-style: italic"
        )

        # Set the header buttons
        self.set_buttons_nav_gui(header_layout)

        logo_layout.addWidget(icon_soft)
        logo_layout.addWidget(status_server_label)

        # Adding widgets to the main layout
        header_layout.addWidget(logo_widget)
        

        
    def set_buttons_nav_gui(self, header_layout: QLayout) -> None:
        self.close_users = QIcon(QIcon_from_svg(Icon.CLOSE_USERS.value))
        self.close_dm = QIcon(QIcon_from_svg(Icon.CLOSE_DM.value))

        # --- Button horizontal layout
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        self.button_layout.setObjectName("button layout")
        self.button_layout.setSpacing(5)

        # --- Close left nav button
        self.close_left_nav_button = CustomQPushButton("", radius=8)
        self.close_left_nav_button.widget_shadow()
        self.close_left_nav_button.clicked.connect(self.controller.hide_left_layout)
        self.close_left_nav_button.setIcon(self.close_users)
        self.close_left_nav_button.setFixedWidth(30)
        self.close_left_nav_button.setFixedHeight(30)

        # --- Close right nav button
        self.close_right_nav_button = CustomQPushButton("", radius=8)
        self.close_right_nav_button.widget_shadow()
        self.close_right_nav_button.clicked.connect(self.controller.hide_right_layout)
        self.close_right_nav_button.setIcon(self.close_dm)
        self.close_right_nav_button.setFixedWidth(30)
        self.close_right_nav_button.setFixedHeight(30)

        header_layout.addWidget(self.close_left_nav_button)
        header_layout.addWidget(self.close_right_nav_button)
        
        info_widget = QWidget()
        info_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            border-radius: 12px"
        )

        self.button_layout.addWidget(info_widget)