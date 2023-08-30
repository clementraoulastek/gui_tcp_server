from typing import Dict
from src.client.core.qt_core import (
    QLabel,
    QWidget,
    QScrollArea,
    Qt,
    QVBoxLayout,
    QSizePolicy,
    QIcon
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
            f"background-color: {Color.GREY.value};\
            color: {Color.LIGHT_GREY.value};\
            border-radius: 12px;\
            border: 1px solid;\
            border-color: {Color.MIDDLE_GREY.value};\
            margin-bottom: 2px"
        )
        self.direct_message_layout = QVBoxLayout(self.right_nav_widget)
        self.direct_message_layout.setSpacing(15)
        self.direct_message_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        rooms_label = QLabel("Rooms")
        widget_shadow(rooms_label)
        rooms_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._update_label_style(rooms_label)
        dm_label = QLabel("Messages")
        widget_shadow(dm_label)
        self._update_label_style(dm_label)
        self.room_btn = CustomQPushButton("home")
        self.room_icon = QIcon(QIcon_from_svg(Icon.ROOM.value))
        self.room_btn.setIcon(self.room_icon)
        self.room_btn.clicked.connect(self.show_home_layout)
        style_ = """
            QPushButton {{
            font-weight: bold;
            text-align: center;
            border: none;
            }} 
            QPushButton:hover {{
            text-decoration: underline;
            }}
            """
        self.room_btn.setStyleSheet(style_.format())
        self.room_list: Dict[str, QWidget] = {}
        
        # Adding widgets to the main layout
        self.direct_message_layout.addWidget(rooms_label)
        self.direct_message_layout.addWidget(self.room_btn)
        self.direct_message_layout.addWidget(dm_label)

        self.scroll_area_dm.setWidget(self.right_nav_widget)

    def _update_label_style(self, label: QLabel):
        label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        label.setContentsMargins(15, 5, 15, 5)
        label.setStyleSheet(
            f"font-weight: bold;\
            color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 6px;"
        )
    
    def show_home_layout(self) -> None:
        self.controller.gui_controller.update_gui_for_mp_layout("home")