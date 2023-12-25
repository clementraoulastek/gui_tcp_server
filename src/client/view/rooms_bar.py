"""Module for RoomsBarWidget class."""

from src.client.core.qt_core import Qt, QVBoxLayout, QWidget
from src.tools.utils import Themes


# pylint: disable=too-few-public-methods
class RoomsBarWidget:
    """
    RoomsBarWidget class.
    """

    def __init__(self, theme: Themes):
        super().__init__()
        self.width_ = 60
        self.theme = theme
        self.main_widget = QWidget()
        self.main_widget.hide()
        self.main_layout = QVBoxLayout(self.main_widget)

        self.main_layout.setContentsMargins(0, 10, 0, 0)
        self.main_layout.setSpacing(0)

        # pylint: disable=line-too-long
        self.main_widget.setStyleSheet(
            f"background-color: {self.theme.rooms_color}; border: 0px solid; margin-top: 0px; padding: 0px"
        )
        self.main_widget.setFixedWidth(self.width_)

        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

    def _update_label_style(self, widget: QWidget) -> None:
        """
        Update the label style.

        Args:
            widget (QWidget): the widget to update
        """
        style_ = f"font-weight: bold;\
        color: {self.theme.title_color};\
        background-color: {self.theme.search_color};\
        border: 0px solid;\
        margin-bottom: 0px;\
        margin-top: 0px;"

        widget.setStyleSheet(style_)
