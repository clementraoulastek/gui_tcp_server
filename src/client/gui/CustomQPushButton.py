from src.client.qt_core import QPushButton, Signal
from src.tools.utils import Color

style = '''
QPushButton {{
	background-color: {_bg_color};
	border-radius: {_radius}px;
	border: {_border_size}px solid {_context_color};
	padding-left: 10px;
    padding-right: 5px;
	selection-color: {_selection_color};
	selection-background-color: {_context_color};
    color: {_color};
}}
QPushButton:pressed {{
	border: {_border_size}px solid {_bg_color_active};
    background-color: {_bg_color_active};
}}
'''

class CustomQPushButton(QPushButton):
    
    signal = Signal()
    
    def __init__(
        self,
        text = "",
        radius = 8,
        border_size = 2,
        color = "#000",
        selection_color = "#000",
        bg_color = Color.LIGHT_GREY.value,
        bg_color_active = Color.BLUE.value,
        context_color = Color.GREY.value
    ):
        super().__init__()
        
        self.setText(text)
        self.setFixedHeight(40)

        self.set_stylesheet(
            radius,
            border_size,
            color,
            selection_color,
            bg_color,
            bg_color_active,
            context_color
        )

    def set_stylesheet(
        self,
        radius,
        border_size,
        color,
        selection_color,
        bg_color,
        bg_color_active,
        context_color
    ):
        # APPLY STYLESHEET
        style_format = style.format(
            _radius = radius,
            _border_size = border_size,
            _color = color,
            _selection_color = selection_color,
            _bg_color = bg_color,
            _bg_color_active = bg_color_active,
            _context_color = context_color
        )
        self.setStyleSheet(style_format)
        
    def clicked(self):
        self.signal.emit()
