"""Module for CustomQListWidget class."""

from PySide6.QtWidgets import QListWidget

from src.client.view.stylesheets.stylesheets import custom_liste_style
from src.tools.utils import Themes

theme = Themes()


# pylint: disable=too-few-public-methods
class CustomQListWidget(QListWidget):
    """
    Custom QListWidget class.

    Args:
        QListWidget (QListWidget): the QListWidget class
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        radius=12,
        border_size=1,
        color=theme.title_color,
        selection_color="#FFF",
        bg_color=theme.search_color,
        bg_color_active=theme.inner_color,
        context_color=theme.nav_color,
    ) -> None:
        super().__init__()

        self.set_stylesheet(
            radius,
            border_size,
            color,
            selection_color,
            bg_color,
            bg_color_active,
            context_color,
        )

        self.setContentsMargins(0, 0, 0, 0)

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
    ):
        """
        Set the stylesheet.

        Args:
            radius (int): The radius
            border_size (int): The border size
            color (str): the color
            selection_color (str): the selection color
            bg_color (str): the background color
            bg_color_active (str): the background color when active
            context_color (str): the context color
        """
        style_format = custom_liste_style.format(
            _radius=radius,
            _border_size=border_size,
            _color=color,
            _selection_color=selection_color,
            _bg_color=bg_color,
            _bg_color_active=bg_color_active,
            _context_color=context_color,
        )
        self.setStyleSheet(style_format)
