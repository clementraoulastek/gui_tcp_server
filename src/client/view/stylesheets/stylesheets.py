scroll_bar_vertical_stylesheet = """
    QScrollArea {
        background: transparent;
        border: none;
    }
    QScrollBar:vertical {
        background: transparent;
        width: 4px;
        margin-left: 0px;
    }
    QScrollBar::handle:vertical {
        background: #171717;
        min-height: 25px;
        border-radius: 1.5px;
    }
    QScrollBar::add-line:vertical {
        border: none;
        background: transparent;
        height: 12px;
        border-bottom-left-radius: 7px;
        border-bottom-right-radius: 7px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
        margin-left: 0px;
    }
    QScrollBar::sub-line:vertical {
        border: none;
        background: transparent;
        height: 12px;
        border-top-left-radius: 7px;
        border-top-right-radius: 7px;
        subcontrol-position: top;
        subcontrol-origin: margin;
        margin-left: 0px;
    }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
        background: transparent;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: transparent;
    }
"""
