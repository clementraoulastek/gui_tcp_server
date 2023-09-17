from src.client.core.qt_core import QGraphicsDropShadowEffect, QColor, QWidget


def widget_shadow(obj: QWidget) -> None:
    shadow = QGraphicsDropShadowEffect(obj)
    shadow.setColor(QColor(0, 0, 0, 150))
    shadow.setOffset(0, 1)
    shadow.setBlurRadius(1)
    obj.setGraphicsEffect(shadow)
