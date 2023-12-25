"""Module for CustomQLineEdit class.""" ""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QLineEdit, QToolButton

from src.client.view.stylesheets.stylesheets import (
    custom_line_edit_style,
    custom_line_edit_style_rounded,
)
from src.tools.utils import Themes

theme = Themes()


class CustomQLineEdit(QLineEdit, QToolButton):
    """
    CustomQLineEdit class.

    Args:
        QLineEdit (QLineEdit): the QLineEdit class
        QToolButton (QToolButton): the QToolButton class
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        text="",
        place_holder_text="",
        radius=12,
        border_size=0,
        color=theme.title_color,
        bg_color=theme.inner_color,
        bg_color_active=theme.inner_color,
        context_color=theme.nav_color,
    ):
        super().__init__()

        if text:
            self.setText(text)
        if place_holder_text:
            self.setPlaceholderText(place_holder_text)

        self.setFixedHeight(45)

        self.set_stylesheet(
            radius,
            border_size,
            color,
            bg_color,
            bg_color_active,
            context_color,
        )

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # pylint: disable=too-many-arguments
    def set_stylesheet(
        self,
        radius: int,
        border_size: int,
        color: str,
        bg_color: str,
        bg_color_active: str,
        context_color: str,
    ) -> None:
        """
        Set the stylesheet.

        Args:
            radius (int): The radius
            border_size (int): The border size
            color (str): the color
            bg_color (str): the background color
            bg_color_active (str): the background color when active
            context_color (str): the context color
        """
        self.style_format = custom_line_edit_style.format(
            _radius=radius,
            _border_size=border_size,
            _color=color,
            _bg_color=bg_color,
            _bg_color_active=bg_color_active,
            _context_color=context_color,
        )
        self.setStyleSheet(self.style_format)

    def widget_shadow(self) -> None:
        """
        Add a shadow to the widget.
        """
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 2)
        shadow.setBlurRadius(1)
        self.setGraphicsEffect(shadow)

    def update_layout(self) -> None:
        """
        Update the layout.
        """
        style_format = custom_line_edit_style_rounded.format(
            _radius=12,
            _border_size=1,
            _color=theme.title_color,
            _bg_color=theme.search_color,
            _bg_color_active=theme.search_color,
            _context_color=theme.nav_color,
        )
        self.setStyleSheet(style_format)

    def reset_layout(self) -> None:
        """
        Reset the layout.
        """
        self.setStyleSheet(self.style_format)
