"""Module for the left navigation bar."""

from src.client.core.qt_core import (
    QEasingCurve,
    QHBoxLayout,
    QLabel,
    QPropertyAnimation,
    QScrollArea,
    QSizePolicy,
    Qt,
    QVBoxLayout,
    QWidget,
)
from src.client.view.stylesheets.stylesheets import scroll_bar_vertical_stylesheet
from src.tools.utils import Icon, Themes, icon_from_svg


# pylint: disable=too-many-instance-attributes
class LeftNavView:
    """
    Left navigation widget class.
    """

    def __init__(self, width: int, theme: Themes) -> None:
        self.width = width
        self.theme = theme
        self.set_left_nav()

        self.slide_animation = None

    def set_left_nav(self) -> None:
        """
        Create a left navigation widget
        """
        # --- Left layout with scroll area
        self.left_nav_layout = QHBoxLayout()
        self.user_inline = QVBoxLayout()
        self.user_inline.setSpacing(5)

        self.user_offline = QVBoxLayout()
        self.user_offline.setSpacing(0)

        self.scroll_area_avatar = QScrollArea()
        self.scroll_area_avatar.setFixedWidth(self.width)

        self.max_width_geometry = self.scroll_area_avatar.geometry()
        self.animation = QPropertyAnimation(self.scroll_area_avatar, b"geometry")
        self.animation.finished.connect(self.on_animation_finished)
        self.animation.setDuration(150)  # Animation duration in milliseconds
        self.animation.setEasingCurve(
            QEasingCurve.OutCubic
        )  # Easing curve for smooth animation

        self.scroll_widget_avatar = QWidget()

        self.left_nav_layout.update()
        self.scroll_widget_avatar.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.scroll_widget_avatar.setFixedWidth(self.width)
        self.scroll_widget_avatar.setStyleSheet(
            f"font-weight: bold;\
            color: {self.theme.title_color};\
            background-color: {self.theme.inner_color};\
            border-radius: 0px;\
            border: 0px solid;\
            border-color: {self.theme.nav_color};\
            margin-bottom: 0px;\
            margin-left: 0px"
        )

        self.user_inline_layout = QVBoxLayout(self.scroll_widget_avatar)
        self.user_inline_layout.setSpacing(0)
        self.user_inline_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        self.scroll_area_avatar.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet.format(
                _background_color=self.theme.inner_color
            )
        )
        self.scroll_area_avatar.setStyleSheet(
            "background-color: transparent; border: 0px"
        )
        self.scroll_area_avatar.enterEvent = (
            lambda e: self.scroll_area_avatar.setVerticalScrollBarPolicy(
                Qt.ScrollBarAsNeeded
            )
        )
        self.scroll_area_avatar.leaveEvent = (
            lambda e: self.scroll_area_avatar.setVerticalScrollBarPolicy(
                Qt.ScrollBarAlwaysOff
            )
        )
        self.scroll_area_avatar.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_avatar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_avatar.setWidgetResizable(True)

        self.scroll_area_avatar.setWidget(self.scroll_widget_avatar)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.info_label.setContentsMargins(5, 5, 5, 5)
        self.info_label.setStyleSheet(
            f"font-weight: bold; color: {self.theme.title_color};\
            background-color: transparent;\
            border-radius: 0px;\
            margin-bottom: 0px;\
            margin-left: 0px;\
            border: 0px solid;"
        )

        self.user_inline.addWidget(self.info_label)
        self.user_inline_layout.addLayout(self.user_inline)

        self.info_disconnected_label = QLabel("")
        self.info_disconnected_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.info_disconnected_label.setContentsMargins(5, 5, 5, 5)
        disconnected_label = QLabel()
        disconnected_icon = icon_from_svg(
            Icon.USER_DISCONNECTED.value, color=self.theme.text_color
        ).pixmap(20, 20)
        disconnected_label.setPixmap(disconnected_icon)

        self.info_disconnected_label.hide()
        self.info_disconnected_label.setStyleSheet(
            f"font-weight: bold;\
            color: {self.theme.title_color};\
            background-color: transparent;\
            border-radius: 0px;\
            margin-bottom: 0px;\
            margin-top: 0px;\
            margin-left: 0px;\
            border: 0px solid"
        )

        self.user_offline.addWidget(self.info_disconnected_label)
        self.user_inline_layout.addLayout(self.user_offline)

        self.left_nav_layout.addWidget(self.scroll_area_avatar)

    def slide_out(self) -> None:
        """
        Slide out the left navigation bar
        """
        self.slide_animation = "out"
        self.scroll_area_avatar.show()
        current_geometry = self.scroll_area_avatar.geometry()
        target_geometry = self.max_width_geometry.translated(
            -current_geometry.width(), 0
        )
        self.animation.setEndValue(current_geometry)
        self.animation.setStartValue(target_geometry)
        self.animation.start()

    def slide_in(self) -> None:
        """
        Slide in the left navigation bar
        """
        self.slide_animation = "in"
        current_geometry = self.scroll_area_avatar.geometry()
        target_geometry = current_geometry.translated(
            -self.max_width_geometry.width(), 0
        )
        self.animation.setStartValue(current_geometry)
        self.animation.setEndValue(target_geometry)
        self.animation.start()

    def on_animation_finished(self) -> None:
        """
        Hide the scroll area when the animation is finished
        """
        self.scroll_area_avatar.updateGeometry()
        if self.slide_animation == "in":
            self.scroll_area_avatar.hide()
        else:
            self.scroll_area_avatar.show()
