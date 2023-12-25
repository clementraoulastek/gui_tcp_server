"""Module for graphical effects."""

from src.client.core.qt_core import QColor, QGraphicsDropShadowEffect, QWidget


def widget_shadow(obj: QWidget) -> None:
    """
    Add a shadow effect to a widget.

    Args:
        obj (QWidget): the widget to add the shadow effect
    """
    shadow = QGraphicsDropShadowEffect(obj)
    shadow.setColor(QColor(0, 0, 0, 150))
    shadow.setOffset(0, 1)
    shadow.setBlurRadius(1)
    obj.setGraphicsEffect(shadow)
