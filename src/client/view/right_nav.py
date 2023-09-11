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
    QHBoxLayout
)
from src.client.view.customWidget.CustomQPushButton import CustomQPushButton
from src.client.view.tools.graphical_effects import widget_shadow
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
        widget_shadow(self.right_nav_widget)
        self.right_nav_widget.setFixedWidth(self.width)
        self.right_nav_widget.setStyleSheet(
            f"background-color: {Color.DARK_GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 0px;\
            border: 1px solid;\
            border-color: {Color.MIDDLE_GREY.value};\
            margin-bottom: 2px"
        )
        self.direct_message_layout = QVBoxLayout(self.right_nav_widget)
        self.direct_message_layout.setSpacing(5)
        self.direct_message_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.rooms_widget = QWidget()
        self.rooms_widget.setStyleSheet("border: none;")
        self.rooms_layout = QVBoxLayout(self.rooms_widget)
        self.rooms_layout.setContentsMargins(0, 0, 0, 0)
        
        rooms_widget = QWidget()
        self._update_label_style(rooms_widget, is_top_label=True)
        rooms_layout = QHBoxLayout(rooms_widget)
        rooms_layout.setContentsMargins(10, 0, 0, 0)
        rooms_label = QLabel("Rooms")
        rooms_label.setStyleSheet("border: none;")
        rooms_label.setContentsMargins(0, 0, 0, 0)
        rooms_label.setAlignment(Qt.AlignLeft)
        
        rooms_icon = QLabel()
        rooms_icon.setStyleSheet("border: 0px")
        rooms_icon.setAlignment(Qt.AlignLeft)
        
        QIcon = QIcon_from_svg(Icon.ROOM.value).pixmap(20, 20)
        rooms_icon.setPixmap(QIcon)
        
        widget_shadow(rooms_widget)
        
        rooms_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        rooms_layout.addWidget(rooms_icon)
        rooms_layout.addWidget(rooms_label)

        dm_widget = QWidget()
        dm_widget.setStyleSheet("margin-left: 0px")
        widget_shadow(dm_widget)
        self._update_label_style(dm_widget, is_top_label=False)
        dm_layout = QHBoxLayout(dm_widget)
        dm_layout.setContentsMargins(0, 0, 0, 0)
        dm_label = QLabel("Messages")
        dm_label.setStyleSheet("border: 0px;margin-left: 0px")
        dm_label.setAlignment(Qt.AlignLeft)
        dm_icon = QLabel()
        dm_icon.setStyleSheet("border: 0px")
        dm_icon.setAlignment(Qt.AlignLeft)
        
        dm_QIcon = QIcon_from_svg(Icon.MESSAGE_DM.value).pixmap(20, 20)
        dm_icon.setPixmap(dm_QIcon)
        
        dm_layout.addWidget(dm_icon)
        dm_layout.addWidget(dm_label)

        self.room_list: Dict[str, QWidget] = {}
        
        # Adding widgets to the main layout
        self.direct_message_layout.addWidget(rooms_widget)
        self.direct_message_layout.addWidget(self.rooms_widget)
        self.direct_message_layout.addWidget(dm_widget)

        self.scroll_area_dm.setWidget(self.right_nav_widget)

    def _update_label_style(self, widget: QWidget, is_top_label: bool = False):
        widget.setContentsMargins(15, 5, 15, 5)
        style_ = f"font-weight: bold;\
            color: {Color.LIGHT_GREY.value};\
            background-color: transparent;\
            border: 0px;\
            border-radius: 6px;\
            margin-bottom: 10px;"
        if not is_top_label:
            style_ += "margin-top: 10px"
            
        widget.setStyleSheet(
            style_
        )
    