"""Module for storing stylesheets."""

scroll_bar_vertical_stylesheet = """
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin-left: 0px;
}}
QScrollBar::handle:vertical {{
    background: #171717;
    min-height: 25px;
    border-radius: 3px;
}}
QScrollBar::add-line:vertical {{
    border: none;
    background: transparent;
    height: 12px;
    border-bottom-left-radius: 3px;
    border-bottom-right-radius: 3px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
    margin-left: 0px;
}}
QScrollBar::sub-line:vertical {{
    border: none;
    background: transparent;
    height: 12px;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
    subcontrol-position: top;
    subcontrol-origin: margin;
    margin-left: 0px;
    border-radius: 3px;
}}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
    background: {_background_color};
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: {_background_color};
}}
"""

custom_line_edit_style = """
QLineEdit {{
	background-color: {_bg_color};
	border-radius: {_radius}px;
	border: {_border_size}px solid {_context_color};
	padding-left: 5px;
    padding-right: 5px;
	selection-background-color: {_context_color};
    color: {_color};
    margin-left: 0px;
    margin-right: 0px;
}}
QLineEdit:focus {{
	border: {_border_size}px solid {_context_color};
    background-color: {_bg_color_active};
}}
"""

custom_line_edit_style_rounded = """
QLineEdit {{
	background-color: {_bg_color};
	border-radius: {_radius}px;
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
	border: {_border_size}px solid {_context_color};
    border-bottom: 0px solid;
	padding-left: 5px;
    padding-right: 5px;
	selection-background-color: {_context_color};
    color: {_color};
}}
QLineEdit:focus {{
	border: {_border_size}px solid {_context_color};
    border-bottom: 0px solid;
    background-color: {_bg_color_active};
}}
"""


custom_liste_style = """
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

custom_button_style = """
QPushButton {{
	background-color: {_bg_color};
	border-radius: {_radius}px;
	border: {_border_size}px solid {_bg_color_active};
	selection-color: {_selection_color};
	selection-background-color: {_context_color};
    color: {_color};
}}
QPushButton:hover {{
	border: {_border_size}px solid {_color};
    background-color: {_bg_color_active};
}}
QPushButton:disabled {{
	border: {_border_size}px solid {_disabled_color};
    background-color: #313338;
}}
"""
