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
from src.tools.utils import Color, Icon, QIcon_from_svg
from src.client.view.stylesheets.stylesheets import scroll_bar_vertical_stylesheet

class LeftNavView(): 
    def __init__(self, width: int) -> None:
        self.width = width
        self.set_left_nav()
    
    def set_left_nav(self) -> None:
        # --- Left layout with scroll area
        self.left_nav_layout = QHBoxLayout()
        self.user_inline = QVBoxLayout()
        self.user_inline.setSpacing(5)

        self.user_offline = QVBoxLayout()
        self.user_offline.setSpacing(5)

        self.scroll_area_avatar = QScrollArea()
        self.scroll_area_avatar.setFixedWidth(self.width)

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
            background-color: {Color.DARK_GREY.value};\
            border-radius: 0px;\
            border: 1px solid;\
            border-color: {Color.MIDDLE_GREY.value};\
            margin-bottom: 10px;\
            margin-left: 0px"
        )
        
        self.user_inline_layout = QVBoxLayout(self.scroll_widget_avatar)
        self.user_inline_layout.setSpacing(5)
        self.user_inline_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        self.scroll_area_avatar.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet
        )
        self.scroll_area_avatar.setStyleSheet("background-color: transparent;")
        self.scroll_area_avatar.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_avatar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_avatar.setWidgetResizable(True)

        self.scroll_area_avatar.setWidget(self.scroll_widget_avatar)

        connected_widget = QWidget()
        connected_widget.setStyleSheet("border: none;")
        connected_layout = QHBoxLayout(connected_widget)
        connected_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        connected_layout.setContentsMargins(0, 0, 0, 0)
        
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        connected_label = QLabel()
        connected_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        connected_icon = QIcon_from_svg(Icon.USER_CONNECTED.value).pixmap(20, 20)
        connected_label.setPixmap(connected_icon)
        widget_shadow(self.info_label)
        self.info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.info_label.setContentsMargins(5, 5, 5, 5)
        self.info_label.setStyleSheet(
            f"font-weight: bold; color: {Color.LIGHT_GREY.value};\
            background-color: transparent;\
            border-radius: 0px;\
            margin-bottom: 10px;\
            margin-left: 0px;\
            border: 0px;"
        )
        connected_layout.addWidget(connected_label)
        connected_layout.addWidget(self.info_label)
        
        self.user_inline.addWidget(connected_widget)
        self.user_inline_layout.addLayout(self.user_inline)

        disconnected_widget = QWidget()
        disconnected_widget.setStyleSheet("border: none;")
        disconnected_widget.setContentsMargins(0, 0, 0, 0)
        disconnected_layout = QHBoxLayout(disconnected_widget)
        disconnected_layout.setAlignment(Qt.AlignCenter)
        disconnected_layout.setContentsMargins(0, 0, 0, 0)
        self.info_disconnected_label = QLabel("")
        self.info_disconnected_label .setAlignment(Qt.AlignCenter)
        self.info_disconnected_label.setContentsMargins(0, 0, 0, 0)
        disconnected_label = QLabel()
        disconnected_icon = QIcon_from_svg(Icon.USER_DISCONNECTED.value).pixmap(20, 20)
        disconnected_label.setPixmap(disconnected_icon)
        
        widget_shadow(self.info_disconnected_label)
        self.info_disconnected_label.hide()
        self.info_disconnected_label.setAlignment(Qt.AlignCenter)
        self.info_disconnected_label.setContentsMargins(5, 5, 5, 5)
        self.info_disconnected_label.setStyleSheet(
            f"font-weight: bold;\
            color: {Color.LIGHT_GREY.value};\
            background-color: transparent;\
            border-radius: 0px;\
            margin-bottom: 10px;\
            margin-top: 0px;\
            margin-left: 0px;\
            border: 0px"
        )
        disconnected_layout.addWidget(disconnected_label)
        disconnected_layout.addWidget(self.info_disconnected_label)
        
        self.user_offline.addWidget(disconnected_widget)
        self.user_inline_layout.addLayout(self.user_offline)

        self.left_nav_layout.addWidget(self.scroll_area_avatar)
        