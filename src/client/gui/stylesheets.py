scroll_bar_vertical_stylesheet = """
    QScrollArea {
        background: none;
        border: none;
    }
    QScrollBar:vertical {
        background: transparent;
    }
    QScrollBar::handle:vertical {
        background: #383A3F;
        min-height: 25px;
        border-radius: 7px
    }
    QScrollBar::add-line:vertical {
        border: none;
        background: transparent;
        height: 20px;
        border-bottom-left-radius: 7px;
        border-bottom-right-radius: 7px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:vertical {
        border: none;
        background: transparent;
        height: 20px;
        border-top-left-radius: 7px;
        border-top-right-radius: 7px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
        background: transparent;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: transparent;
    }
"""
