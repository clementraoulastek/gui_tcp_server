from functools import partial
from typing import Dict
from src.client.core.qt_core import (
    QLabel,
    QWidget,
    QScrollArea,
    Qt,
    QVBoxLayout,
    QSizePolicy,
    QIcon,
    QEvent,
    QEnterEvent,
    QHBoxLayout,
)
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.tools.utils import Color, Icon, QIcon_from_svg
from src.client.view.stylesheets.stylesheets import scroll_bar_vertical_stylesheet


class RightNavView:
    def __init__(self, controller, width: int) -> None:
        self.width = width
        self.controller = controller
        self.set_right_nav()

    def set_right_nav(self) -> None:
        """
        Create a right navigation widget
        """
        # Scroll area
        self.scroll_area_dm = QScrollArea()
        self.scroll_area_dm.setFixedWidth(self.width)
        self.scroll_area_dm.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet
        )

        self.scroll_area_dm.setStyleSheet("background-color: transparent;")
        self.scroll_area_dm.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_dm.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_dm.setWidgetResizable(True)

        # Background
        self.right_nav_widget = QWidget()
        self.right_nav_widget.setFixedWidth(self.width)
        self.right_nav_widget.setStyleSheet(
            f"background-color: {Color.DARK_GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 0px;\
            border: 0px solid;\
            border-color: {Color.MIDDLE_GREY.value};\
            margin-bottom: 0px"
        )
        self.direct_message_layout = QVBoxLayout(self.right_nav_widget)
        self.direct_message_layout.setSpacing(5)
        self.direct_message_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.rooms_widget = QWidget()
        self.rooms_widget.setStyleSheet("border: none;")
        self.rooms_layout = QVBoxLayout(self.rooms_widget)
        self.rooms_layout.setContentsMargins(0, 0, 0, 0)

        rooms_label = QLabel("Rooms")
        self._update_label_style(rooms_label, is_top_label=False)
        rooms_label.setContentsMargins(0, 0, 0, 0)
        rooms_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        rooms_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        dm_label = QLabel("Messages")
        self._update_label_style(dm_label, is_top_label=True)
        dm_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        dm_icon = QLabel()
        dm_icon.setStyleSheet("border: 0px")
        dm_icon.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

        dm_QIcon = QIcon_from_svg(Icon.MESSAGE_DM.value).pixmap(20, 20)
        dm_icon.setPixmap(dm_QIcon)

        self.room_list: Dict[str, QWidget] = {}

        # Adding widgets to the main layout
        self.direct_message_layout.addWidget(rooms_label)
        self.direct_message_layout.addWidget(self.rooms_widget)
        self.direct_message_layout.addWidget(dm_label)

        self.scroll_area_dm.setWidget(self.right_nav_widget)

    def _update_label_style(self, widget: QWidget, is_top_label: bool = False):
        style_ = f"font-weight: bold;\
        color: {Color.LIGHT_GREY.value};\
        background-color: transparent;\
        border: 0px solid;\
        border-radius: 6px;\
        margin-bottom: 0px;\
        margin-top: 0px;"
        if not is_top_label:
            style_ += "margin-top: 0px"

        widget.setStyleSheet(style_)
