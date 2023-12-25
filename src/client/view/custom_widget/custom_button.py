"""Module for custom QPushButton class."""

# pylint: disable=duplicate-code
from src.client.core.qt_core import QColor, QGraphicsDropShadowEffect, QPushButton
from src.client.view.stylesheets.stylesheets import custom_button_style
from src.tools.utils import Themes

theme = Themes()


class CustomQPushButton(QPushButton):
    """
    Custom QPushButton class.

    Args:
        QPushButton (QPushButton): the QPushButton class
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        text="",
        radius=6,
        border_size=0,
        color=theme.title_color,
        selection_color="#000",
        bg_color="transparent",
        bg_color_active=theme.inner_color,
        context_color=theme.background_color,
        parent=None,
    ):
        super().__init__(parent)

        self.setText(text)
        self.setFixedHeight(40)
        disabled_color = theme.rooms_color
        self.set_stylesheet(
            radius,
            border_size,
            color,
            selection_color,
            bg_color,
            bg_color_active,
            context_color,
            disabled_color,
        )

    # pylint: disable=too-many-arguments
    def set_stylesheet(
        self,
        radius: int,
        border_size: int,
        color: str,
        selection_color: str,
        bg_color: str,
        bg_color_active: str,
        context_color: str,
        disabled_color: str,
    ):
        """
        Set the stylesheet.

        Args:
            radius (int): radius
            border_size (int): border size
            color (str): the color
            selection_color (str): selection color
            bg_color (str): background color
            bg_color_active (str): background color when active
            context_color (str): context color
            disabled_color (str): disabled color
        """
        style_format = custom_button_style.format(
            _radius=radius,
            _border_size=border_size,
            _color=color,
            _selection_color=selection_color,
            _bg_color=bg_color,
            _bg_color_active=bg_color_active,
            _context_color=context_color,
            _disabled_color=disabled_color,
        )
        self.setStyleSheet(style_format)

    def widget_shadow(self) -> None:
        """
        Set the shadow effect.
        """
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 2)
        shadow.setBlurRadius(1)
        self.setGraphicsEffect(shadow)
