"""Module for the right navigation widget"""

from typing import Dict

from src.client.core.qt_core import (
    QEasingCurve,
    QLabel,
    QPropertyAnimation,
    QScrollArea,
    Qt,
    QVBoxLayout,
    QWidget,
)
from src.client.view.stylesheets.stylesheets import scroll_bar_vertical_stylesheet
from src.tools.utils import Icon, Themes, icon_from_svg


# pylint: disable=too-many-instance-attributes
class RightNavView:
    """
    Right navigation widget class.
    """

    def __init__(self, controller, width: int, theme: Themes) -> None:
        self.width = width
        self.controller = controller
        self.theme = theme
        self.max_width_geometry = None
        self.slide_animation = None
        self.set_right_nav()

    def set_right_nav(self) -> None:
        """
        Create a right navigation widget
        """
        # Scroll area
        self.scroll_area_dm = QScrollArea()
        self.scroll_area_dm.setFixedWidth(self.width)

        self.max_width_geometry = self.scroll_area_dm.geometry()
        self.animation = QPropertyAnimation(self.scroll_area_dm, b"geometry")
        self.animation.finished.connect(self.on_animation_finished)
        self.animation.setDuration(150)  # Animation duration in milliseconds
        self.animation.setEasingCurve(
            QEasingCurve.OutCubic
        )  # Easing curve for smooth animation

        self.scroll_area_dm.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet.format(
                _background_color=self.theme.inner_color
            )
        )

        self.scroll_area_dm.setStyleSheet("background-color: transparent; border: 0px")
        self.scroll_area_dm.enterEvent = (
            lambda e: self.scroll_area_dm.setVerticalScrollBarPolicy(
                Qt.ScrollBarAsNeeded
            )
        )
        self.scroll_area_dm.leaveEvent = (
            lambda e: self.scroll_area_dm.setVerticalScrollBarPolicy(
                Qt.ScrollBarAlwaysOff
            )
        )
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

        dm_q_icon = icon_from_svg(
            Icon.MESSAGE_DM.value, color=self.theme.text_color
        ).pixmap(20, 20)
        dm_icon.setPixmap(dm_q_icon)

        self.room_list: Dict[str, QWidget] = {}

        # Adding widgets to the main layout
        self.direct_message_layout.addWidget(dm_label)

        self.scroll_area_dm.setWidget(self.right_nav_widget)

    def _update_label_style(self, widget: QWidget) -> None:
        """
        Update the label style.

        Args:
            widget (QWidget): the widget to update
        """
        style_ = f"font-weight: bold;\
        color: {self.theme.title_color};\
        background-color: transparent;\
        border: 0px solid;\
        border-radius: 0px;\
        padding-left: 0px;\
        padding-right: 0px;"

        widget.setStyleSheet(style_)

    def slide_out(self) -> None:
        """
        Slide out the right navigation widget
        """
        self.max_width_geometry = self.scroll_area_dm.geometry()
        self.slide_animation = "out"
        self.scroll_area_dm.show()
        current_geometry = self.scroll_area_dm.geometry()
        target_geometry = self.max_width_geometry.translated(
            current_geometry.width(), 0
        )
        self.animation.setEndValue(current_geometry)
        self.animation.setStartValue(target_geometry)
        self.animation.start()

    def slide_in(self) -> None:
        """
        Slide in the right navigation widget
        """
        self.slide_animation = "in"
        current_geometry = self.scroll_area_dm.geometry()
        target_geometry = current_geometry.translated(
            self.max_width_geometry.width(), 0
        )
        self.animation.setStartValue(current_geometry)
        self.animation.setEndValue(target_geometry)
        self.animation.start()

    def on_animation_finished(self) -> None:
        """
        Hide the right navigation widget when the animation is finished
        """
        if self.slide_animation == "in":
            self.scroll_area_dm.hide()
        else:
            self.scroll_area_dm.show()
