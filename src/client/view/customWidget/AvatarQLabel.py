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
    QGraphicsDropShadowEffect,
)


@unique
class AvatarStatus(Enum):
    DEACTIVATED = 0
    ACTIVATED = 1
    IDLE = 2
    DM = 3


class AvatarLabel(QLabel):
    def __init__(
        self,
        *args,
        content=None,
        height=40,
        width=40,
        color=None,
        status=AvatarStatus.IDLE
    ):
        super(AvatarLabel, self).__init__(*args)
        self.color = color
        self.height_ = height
        self.width_ = width
        self.content = content
        self.update_picture(status)
        self.setStyleSheet("border: none")

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
        icon_pixmap = self.__init_pixmap()
        if status == AvatarStatus.IDLE:
            self.setPixmap(icon_pixmap)
            return

        painter = self.__create_painter(icon_pixmap)
        if status == AvatarStatus.ACTIVATED:
            brush_color = self._update_circle_color(74, 160, 50)
        elif status == AvatarStatus.DEACTIVATED:
            painter.end()
            self.setPixmap(icon_pixmap)
            return
        elif status == AvatarStatus.DM:
            brush_color = self._update_circle_color(255, 0, 0)
        self.__create_ellipse(painter, brush_color, icon_pixmap)

    def _update_circle_color(self, r, g, b):
        return QColor(r, g, b)

    def widget_shadow(self) -> None:
        """
        Update shadow
        """
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 2)
        shadow.setBlurRadius(1)
        return shadow

    def set_opacity(self, opacity: int) -> None:
        """
        Update opacity

        Args:
            opacity (int): opacity value
        """
        opacity_effect = QGraphicsOpacityEffect(self)
        opacity_effect.setOpacity(opacity)
        self.setGraphicsEffect(opacity_effect)

    def update_pixmap(self, status: AvatarStatus) -> None:
        """
        Update pixmap of the icon

        Args:
            status (AvatarStatus): avatar status
        """
        icon_pixmap = self.__init_pixmap()
        painter = self.__create_painter(icon_pixmap)
        if status == AvatarStatus.ACTIVATED:
            brush_color = self._update_circle_color(74, 160, 50)
        elif status == AvatarStatus.DM:
            brush_color = self._update_circle_color(255, 0, 0)
        elif status == AvatarStatus.IDLE:
            painter.end()
            self.setPixmap(icon_pixmap)
            return

        self.__create_ellipse(painter, brush_color, icon_pixmap)

    def __create_painter(self, icon_pixmap: QPixmap) -> QPainter:
        result = QPainter(icon_pixmap)
        result.setRenderHint(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        result.drawPixmap(0, 0, icon_pixmap)
        return result

    def __init_pixmap(self) -> QPixmap:
        pm = QPixmap()
        pm.loadFromData(self.content)
        return QIcon(pm).pixmap(QSize(self.height_, self.width_))

    def __create_ellipse(
        self, painter: QPainter, brush_color: QColor, icon_pixmap: QPixmap
    ) -> None:
        painter.setPen(QPen(Qt.NoPen))
        circle_radius = 5
        circle_center = QPoint(
            self.width_ - 2*circle_radius, self.height_ - circle_radius
        )
        brush = QBrush(brush_color)
        painter.setBrush(brush)
        painter.drawEllipse(circle_center, circle_radius, circle_radius)
        painter.end()
        self.setPixmap(icon_pixmap)
