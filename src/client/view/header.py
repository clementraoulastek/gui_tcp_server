"""Header view module."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLayout, QLineEdit, QWidget

from src.client.view.custom_widget.custom_avatar_label import AvatarLabel
from src.client.view.custom_widget.custom_button import CustomQPushButton
from src.client.view.custom_widget.custom_line_edit import CustomQLineEdit
from src.client.view.custom_widget.custom_list import CustomQListWidget
from src.tools.constant import DEFAULT_CLIENT_NAME
from src.tools.utils import Icon, ImageAvatar, Themes, icon_from_svg


# pylint: disable=too-many-instance-attributes
class HeaderView:
    """
    Header widget class.
    """

    def __init__(self, controller, parent: QWidget, theme: Themes) -> None:
        self.controller = controller
        self.parent = parent
        self.theme = theme
        self.close_users = None
        self.close_dm = None
        self.button_layout = None
        self.close_left_nav_button = None
        self.close_right_nav_button = None
        self.set_header_gui()

    # pylint: disable=too-many-statements
    def set_header_gui(self) -> None:
        """
        Set the header GUI
        """
        # Header widget
        self.main_widget = QWidget()

        self.main_widget.setStyleSheet(
            f"background-color: {self.theme.background_color};\
            color: {self.theme.title_color};\
            border-radius: 0px;\
            border: 0px solid;\
            margin-bottom: 0px;\
            border-color: {self.theme.nav_color};"
        )

        # Header layout
        self.header_layout = QHBoxLayout(self.main_widget)
        self.header_layout.setContentsMargins(10, 0, 10, 0)

        # Logo widget
        logo_widget = QWidget()
        logo_widget.setStyleSheet("border-bottom: 1px solid")

        # Logo layout
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setSpacing(10)
        logo_widget.setStyleSheet("border: 0px solid")
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        icon_soft = AvatarLabel(content=ImageAvatar.SERVER.value, height=20, width=20)
        icon_soft.setStyleSheet(
            "font-weight: bold;\
            border: none"
        )

        # Server Name
        status_server_label = QLabel(DEFAULT_CLIENT_NAME.upper())
        status_server_label.setStyleSheet(
            f"font-weight: bold;\
            border: 0px solid;\
            font-style: italic;\
            border-color: {self.theme.nav_color};"
        )
        separator_icon = QIcon(
            icon_from_svg(Icon.SEPARATOR.value, color=self.theme.title_color)
        )
        self.separator = QLabel()
        self.separator.hide()
        self.separator.setPixmap(separator_icon.pixmap(20, 20))
        self.separator.setStyleSheet("border: 0px solid")

        self.welcome_label = QLabel("")
        self.welcome_label.setStyleSheet("font-weight: bold")
        self.welcome_label.hide()

        # Frame research
        self.frame_research = CustomQLineEdit(
            place_holder_text="Search users",
            bg_color=self.theme.search_color,
            bg_color_active=self.theme.search_color,
        )
        self.frame_research.setFixedHeight(30)
        self.frame_research.setFixedWidth(200)
        self.frame_research.setTextMargins(0, 0, 0, 0)
        self.frame_research.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Frame research list
        self.frame_research_list = CustomQListWidget()
        self.parent.layout().addChildWidget(self.frame_research_list)
        self.frame_research_list.hide()

        self.frame_research_list.setContentsMargins(0, 0, 0, 0)
        self.frame_research_list.setSpacing(10)
        self.frame_research_list.setFixedWidth(200)

        search_icon = QIcon(
            icon_from_svg(Icon.SEARCH.value, color=self.theme.title_color)
        )
        self.search_action = self.frame_research.addAction(
            search_icon, QLineEdit.ActionPosition.TrailingPosition
        )

        logo_layout.addWidget(icon_soft, alignment=Qt.AlignmentFlag.AlignLeft)
        logo_layout.addWidget(status_server_label, alignment=Qt.AlignmentFlag.AlignLeft)

        lang_layout = AvatarLabel(content=ImageAvatar.EN.value, height=20, width=20)
        lang_label = QLabel("<strong>EN</strong>")
        lang_label.setStyleSheet("border: 0px solid")

        # Adding widgets to the main layout
        self.header_layout.addWidget(logo_widget)

        self.header_layout.addWidget(self.separator)
        self.avatar = AvatarLabel()
        self.header_layout.addWidget(self.avatar)
        self.header_layout.addWidget(self.welcome_label)
        self.header_layout.addWidget(
            lang_layout, stretch=1, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.header_layout.addWidget(lang_label)

        # Set the header buttons
        self.set_buttons_nav_gui(self.header_layout)
        self.header_layout.addWidget(self.frame_research)

        self.frame_research.hide()

    def set_buttons_nav_gui(self, header_layout: QLayout) -> None:
        """
        Set the header buttons GUI

        Args:
            header_layout (QLayout): Layout to display the buttons
        """
        self.close_users = QIcon(
            icon_from_svg(Icon.CLOSE_USERS.value, color=self.theme.text_color)
        )
        self.close_dm = QIcon(
            icon_from_svg(Icon.CLOSE_DM.value, color=self.theme.text_color)
        )

        # --- Button horizontal layout
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        self.button_layout.setObjectName("button layout")
        self.button_layout.setSpacing(5)

        # --- Close left nav button
        self.close_left_nav_button = CustomQPushButton("", radius=8)
        self.close_left_nav_button.setToolTip("Close users panel")
        self.close_left_nav_button.clicked.connect(self.controller.hide_left_layout)
        self.close_left_nav_button.setIcon(self.close_users)
        self.close_left_nav_button.setFixedWidth(30)
        self.close_left_nav_button.setFixedHeight(30)

        # --- Close right nav button
        self.close_right_nav_button = CustomQPushButton("", radius=8)
        self.close_right_nav_button.setToolTip("Close messages panel")
        self.close_right_nav_button.clicked.connect(self.controller.hide_right_layout)
        self.close_right_nav_button.setIcon(self.close_dm)
        self.close_right_nav_button.setFixedWidth(30)
        self.close_right_nav_button.setFixedHeight(30)

        header_layout.addWidget(self.close_left_nav_button)
        header_layout.addWidget(self.close_right_nav_button)

        info_widget = QWidget()
        info_widget.setStyleSheet(
            f"background-color: {self.theme.background_color};\
            border-radius: 12px"
        )

        self.button_layout.addWidget(info_widget)
