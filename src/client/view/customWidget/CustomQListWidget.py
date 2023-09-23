from src.client.core.qt_core import (
    QListWidget
)
from src.tools.utils import Themes

style = """
QListWidget {{
	background-color: {_bg_color};
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
    border-bottom-left-radius: {_radius}px;
    border-bottom-right-radius: {_radius}px;
	border: {_border_size}px solid {_context_color};
    border-top: 0px solid;
	padding-left: 0px;
    padding-right: 0px;
	selection-color: {_selection_color};
	selection-background-color: {_context_color};
    color: {_color};
}}
QListWidget:focus {{
	border: {_border_size}px solid {_context_color};
    border-top: 0px solid;
    background-color: {_bg_color_active};
}}
QScrollBar:vertical {{
    background: transparent;
    width: 4px;
    margin-left: 0px;
}}
QScrollBar::handle:vertical {{
    background: #171717;
    min-height: 25px;
    border-radius: 1.5px;
}}
QScrollBar::add-line:vertical {{
    border: none;
    background: transparent;
    height: 12px;
    border-bottom-left-radius: 7px;
    border-bottom-right-radius: 7px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
    margin-left: 0px;
}}
QScrollBar::sub-line:vertical {{
    border: none;
    background: transparent;
    height: 12px;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    subcontrol-position: top;
    subcontrol-origin: margin;
    margin-left: 0px;
}}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
    background: transparent;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}
"""

theme = Themes()
class CustomQListWidget(QListWidget):
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
        
    def set_stylesheet(
        self,
        radius,
        border_size,
        color,
        selection_color,
        bg_color,
        bg_color_active,
        context_color,
    ):
        # APPLY STYLESHEET
        style_format = style.format(
            _radius=radius,
            _border_size=border_size,
            _color=color,
            _selection_color=selection_color,
            _bg_color=bg_color,
            _bg_color_active=bg_color_active,
            _context_color=context_color,
        )
        self.setStyleSheet(style_format)
        

    