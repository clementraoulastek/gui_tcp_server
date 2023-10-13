scroll_bar_vertical_stylesheet = '''
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
'''
