from enum import Enum, unique
from src.client.core.qt_core import (
    QPixmap,
    QLabel,
    QIcon,
    QSize,
    QColor,
    Qt,
    QPainter,
    QBrush,
    QPoint,
    QPen,
    QGraphicsOpacityEffect,
)


@unique
class AvatarStatus(Enum):
    DEACTIVATED = 0
    ACTIVATED = 1
    IDLE = 2
    DM = 3


class RoundedLabel(QLabel):
    def __init__(
        self,
        *args,
        content=None,
        height=40,
        width=40,
        color=None,
        status=AvatarStatus.IDLE
    ):
        super(RoundedLabel, self).__init__(*args)
        self.color = color
        self.height_ = height
        self.width_ = width
        self.content = content
        self.update_picture(status)

    def update_picture(self, status, content=None):
        if content:
            self.content = content
        if isinstance(self.content, str):
            p = QIcon(self.content).pixmap(QSize(self.height_, self.width_))
            if self.color:
                painter = QPainter(p)
                painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                painter.fillRect(p.rect(), QColor(self.color))
                painter.end()
            self.setPixmap(p)
        else:
            self.update_icon_status(status=status)

    def update_icon_status(self, status: AvatarStatus) -> None:
        pm = QPixmap()
        pm.loadFromData(self.content)
        icon_pixmap = QIcon(pm).pixmap(QSize(self.height_, self.width_))
        if status == AvatarStatus.IDLE:
            self.setPixmap(icon_pixmap)
            return

        painter = QPainter(icon_pixmap)
        painter.setRenderHint(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.drawPixmap(0, 0, icon_pixmap)

        if status == AvatarStatus.ACTIVATED:
            brush_color = self._update_circle_color(74, 160, 50)
        elif status == AvatarStatus.DEACTIVATED:
            brush_color = self._update_circle_color(255, 0, 0)
            self.setDisabled(True)
        elif status == AvatarStatus.DM:
            brush_color = self._update_circle_color(50, 88, 160)
        painter.setPen(QPen(Qt.NoPen))
        circle_radius = 5
        circle_center = QPoint(
            self.width_ - circle_radius, self.height_ - circle_radius
        )
        brush = QBrush(brush_color)
        painter.setBrush(brush)
        painter.drawEllipse(circle_center, circle_radius, circle_radius)

        painter.end()

        self.setPixmap(icon_pixmap)

    def _update_circle_color(self, r, g, b):
        return  QColor(r, g, b)
        
    def set_opacity(self, opacity):
        opacity_effect = QGraphicsOpacityEffect(self)
        opacity_effect.setOpacity(opacity)
        self.setGraphicsEffect(opacity_effect)