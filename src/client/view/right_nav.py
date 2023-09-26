from typing import Dict
from src.client.core.qt_core import (
    QLabel,
    QWidget,
    QScrollArea,
    Qt,
    QVBoxLayout,
)
from src.tools.utils import Themes, Icon, QIcon_from_svg
from src.client.view.stylesheets.stylesheets import scroll_bar_vertical_stylesheet


class RightNavView:
    def __init__(self, controller, width: int, theme: Themes) -> None:
        self.width = width
        self.controller = controller
        self.theme = theme
        self.set_right_nav()

    def set_right_nav(self) -> None:
        """
        Create a right navigation widget
        """
        # Scroll area
        self.scroll_area_dm = QScrollArea()
        self.scroll_area_dm.setFixedWidth(self.width)
        self.scroll_area_dm.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet.format(_background_color=self.theme.inner_color)
        )

        self.scroll_area_dm.setStyleSheet("background-color: transparent; border: 0px")
        self.scroll_area_dm.enterEvent = lambda e: self.scroll_area_dm.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_dm.leaveEvent = lambda e: self.scroll_area_dm.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_dm.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_dm.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_dm.setWidgetResizable(True)

        # Background
        self.right_nav_widget = QWidget()
        self.right_nav_widget.setFixedWidth(self.width)
        self.right_nav_widget.setStyleSheet(
            f"background-color: {self.theme.inner_color};\
            color: {self.theme.title_color};\
            border-radius: 0px;\
            border: 0px solid;\
            border-color: {self.theme.nav_color};\
            margin-bottom: 0px;"
        )
        self.direct_message_layout = QVBoxLayout(self.right_nav_widget)
        self.direct_message_layout.setSpacing(0)
        self.direct_message_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        dm_label = QLabel("Messages")
        dm_label.setContentsMargins(5, 5, 5, 5)
        self._update_label_style(dm_label)
        dm_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        dm_icon = QLabel()
        dm_icon.setStyleSheet("border: 0px")
        dm_icon.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

        dm_QIcon = QIcon_from_svg(Icon.MESSAGE_DM.value, color=self.theme.text_color).pixmap(20, 20)
        dm_icon.setPixmap(dm_QIcon)

        self.room_list: Dict[str, QWidget] = {}

        # Adding widgets to the main layout
        self.direct_message_layout.addWidget(dm_label)

        self.scroll_area_dm.setWidget(self.right_nav_widget)

    def _update_label_style(self, widget: QWidget):
        style_ = f"font-weight: bold;\
        color: {self.theme.title_color};\
        background-color: transparent;\
        border: 0px solid;\
        border-radius: 0px;\
        padding-left: 0px;\
        padding-right: 0px;"

        widget.setStyleSheet(style_)
