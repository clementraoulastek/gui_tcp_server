from src.client.core.qt_core import (
    QLabel,
    QWidget,
    QScrollArea,
    Qt,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
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
            border: 0px solid;\
            border-color: {Color.MIDDLE_GREY.value};\
            margin-bottom: 0px;\
            margin-left: 0px"
        )
        
        self.user_inline_layout = QVBoxLayout(self.scroll_widget_avatar)
        self.user_inline_layout.setSpacing(5)
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
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.info_label.setContentsMargins(0, 0, 0, 0)
        self.info_label.setStyleSheet(
            f"font-weight: bold; color: {Color.LIGHT_GREY.value};\
            background-color: transparent;\
            border-radius: 6px;\
            margin-bottom: 0px;\
            margin-left: 0px;\
            border: 0px solid;"
        )
        
        self.user_inline.addWidget(self.info_label)
        self.user_inline_layout.addLayout(self.user_inline)

        self.info_disconnected_label = QLabel("")
        self.info_disconnected_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.info_disconnected_label.setContentsMargins(0, 0, 0, 0)
        disconnected_label = QLabel()
        disconnected_icon = QIcon_from_svg(Icon.USER_DISCONNECTED.value).pixmap(20, 20)
        disconnected_label.setPixmap(disconnected_icon)
        
        self.info_disconnected_label.hide()
        self.info_disconnected_label.setStyleSheet(
            f"font-weight: bold;\
            color: {Color.LIGHT_GREY.value};\
            background-color: transparent;\
            border-radius: 6px;\
            margin-bottom: 0px;\
            margin-top: 0px;\
            margin-left: 0px;\
            border: 0px solid"
        )
        
        self.user_offline.addWidget(self.info_disconnected_label)
        self.user_inline_layout.addLayout(self.user_offline)

        self.left_nav_layout.addWidget(self.scroll_area_avatar)
        