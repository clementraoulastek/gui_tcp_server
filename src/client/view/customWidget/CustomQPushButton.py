from src.client.core.qt_core import (
    QPushButton,
    Signal,
    QGraphicsDropShadowEffect,
    QColor,
)
from src.tools.utils import Color

style = """
QPushButton {{
	background-color: {_bg_color};
	border-radius: {_radius}px;
	border: {_border_size}px solid {_bg_color_active};
	padding-left: 5px;
    padding-right: 5px;
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


class CustomQPushButton(QPushButton):
    signal = Signal()

    def __init__(
        self,
        text="",
        radius=6,
        border_size=1,
        color=Color.LIGHT_GREY.value,
        selection_color="#000",
        bg_color=Color.DARK_GREY.value,
        bg_color_active=Color.GREY.value,
        context_color=Color.GREY.value,
        parent=None
    ):
        super().__init__(parent)

        self.setText(text)
        self.setFixedHeight(40)
        disabled_color = Color.BLACK.value
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

    def set_stylesheet(
        self,
        radius,
        border_size,
        color,
        selection_color,
        bg_color,
        bg_color_active,
        context_color,
        disabled_color,
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
            _disabled_color=disabled_color,
        )
        self.setStyleSheet(style_format)

    def clicked(self):
        self.signal.emit()

    def widget_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 2)
        shadow.setBlurRadius(1)
        self.setGraphicsEffect(shadow)
