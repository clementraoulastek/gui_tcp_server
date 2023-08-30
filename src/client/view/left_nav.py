from src.client.core.qt_core import (
    QLabel,
    QWidget,
    QScrollArea,
    Qt,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
from src.client.view.tools.graphical_effects import widget_shadow
from src.tools.utils import Color
from src.client.view.stylesheets.stylesheets import scroll_bar_vertical_stylesheet

class LeftNavView(): 
    def __init__(self, width: int) -> None:
        self.width = width
        self.set_left_nav()
    
    def set_left_nav(self) -> None:
        # --- Left layout with scroll area
        self.left_nav_layout = QHBoxLayout()
        self.user_inline = QVBoxLayout()
        self.user_inline.setSpacing(15)

        self.user_offline = QVBoxLayout()
        self.user_offline.setSpacing(15)

        self.scroll_area_avatar = QScrollArea()
        self.scroll_area_avatar.setFixedWidth(self.width + 2)

        self.scroll_widget_avatar = QWidget()
        widget_shadow(self.scroll_widget_avatar)
        self.left_nav_layout.update()
        self.scroll_widget_avatar.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.scroll_widget_avatar.setFixedWidth(self.width)
        self.scroll_widget_avatar.setStyleSheet(
            f"font-weight: bold;\
            color: {Color.LIGHT_GREY.value};\
            background-color: {Color.GREY.value};\
            border-radius: 12px;\
            border: 1px solid;\
            border-color: {Color.MIDDLE_GREY.value};\
            margin-bottom: 2px;"
        )
        
        self.user_inline_layout = QVBoxLayout(self.scroll_widget_avatar)
        self.user_inline_layout.setSpacing(25)
        self.user_inline_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        self.scroll_area_avatar.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet
        )
        self.scroll_area_avatar.setStyleSheet("background-color: transparent;")
        self.scroll_area_avatar.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_avatar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_avatar.setWidgetResizable(True)

        self.scroll_area_avatar.setWidget(self.scroll_widget_avatar)

        self.info_label = QLabel("")
        widget_shadow(self.info_label)
        self.info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.info_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.message_label = QLabel("Login session")
        self.message_label.setStyleSheet("border: 0px")
        self.message_label.setWordWrap(True)
        self.info_label.setContentsMargins(5, 5, 5, 5)
        self.info_label.setStyleSheet(
            f"font-weight: bold; color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 6px;"
        )
        self.user_inline.addWidget(self.info_label)
        self.user_inline.addWidget(self.message_label)
        self.user_inline_layout.addLayout(self.user_inline)

        self.info_disconnected_label = QLabel("")
        widget_shadow(self.info_disconnected_label)
        self.info_disconnected_label.hide()
        self.info_disconnected_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.info_disconnected_label.setContentsMargins(5, 5, 5, 5)
        self.info_disconnected_label.setStyleSheet(
            f"font-weight: bold;\
            color: {Color.LIGHT_GREY.value};\
            background-color: {Color.DARK_GREY.value};\
            border-radius: 6px;"
        )
        self.user_offline.addWidget(self.info_disconnected_label)
        self.user_inline_layout.addLayout(self.user_offline)

        self.left_nav_layout.addWidget(self.scroll_area_avatar)
        