"""AvatarQLabel module."""

# pylint: disable=duplicate-code
from enum import Enum, unique
from typing import Optional

from src.client.core.qt_core import (
    QBrush,
    QColor,
    QFont,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QIcon,
    QLabel,
    QPainter,
    QPen,
    QPixmap,
    QPoint,
    QRectF,
    QSize,
    Qt,
)
from src.tools.utils import Themes

theme = Themes()


@unique
class AvatarStatus(Enum):
    """
    Enumeration for avatar status

    Args:
        Enum (Enum): Enum class
    """

    DEACTIVATED = 0
    ACTIVATED = 1
    IDLE = 2
    DM = 3


class AvatarLabel(QLabel):
    """
    Avatar label class.

    Args:
        QLabel (QLabel): QLabel class
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        *args,
        content=None,
        height=30,
        width=30,
        color=None,
        status=AvatarStatus.IDLE,
        background_color=theme.rgb_background_color_actif,
    ):
        super().__init__(*args)
        self.color = color
        self.height_ = height
        self.width_ = width
        self.content = content
        self.status = None
        self.update_picture(status, background_color)
        self.setStyleSheet("border: none")

    def update_picture(
        self,
        status: AvatarStatus,
        background_color: Optional[QColor] = theme.rgb_background_color_actif,
        content: Optional[bytes] = None,
    ) -> None:
        # pylint: disable=line-too-long
        """
        Update the picture of the avatar

        Args:
            status (AvatarStatus): avatar status
            background_color (Optional[QColor], optional): the background color. Defaults to theme.rgb_background_color_actif.
            content (Optional[bytes], optional): content picture in bytes. Defaults to None.
        """
        # Update Avatar status
        self.status = status

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
            self.update_icon_status(status, background_color)

    def update_icon_status(
        self, status: AvatarStatus, background_color: QColor
    ) -> None:
        """
        Update the icon status

        Args:
            status (AvatarStatus): avatar status
            background_color (QColor): the background color
        """
        # Update Avatar status
        self.status = status

        icon_pixmap = self.__init_pixmap()
        if status == AvatarStatus.IDLE:
            self.setPixmap(icon_pixmap)
            return

        painter = self.__create_painter(icon_pixmap)
        if status == AvatarStatus.ACTIVATED:
            brush_color = self._update_circle_color(74, 160, 50)
        elif status == AvatarStatus.DEACTIVATED:
            brush_color = self._update_circle_color(154, 152, 147)
        elif status == AvatarStatus.DM:
            brush_color = self._update_circle_color(255, 0, 0)
        self.__create_ellipse(painter, background_color, brush_color, icon_pixmap)

    def _update_circle_color(self, r: int, g: int, b: int) -> QColor:
        """
        Update the circle color

        Args:
            r (int): red value
            g (int): green value
            b (int): blue value

        Returns:
            QColor: the color
        """
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

    def update_pixmap(
        self, status: AvatarStatus, background_color=theme.rgb_background_color_actif
    ) -> None:
        """
        Update pixmap of the icon

        Args:
            status (AvatarStatus): avatar status
        """
        # Update Avatar status
        self.status = status

        icon_pixmap = self.__init_pixmap()
        painter = self.__create_painter(icon_pixmap)

        if status == AvatarStatus.ACTIVATED:
            brush_color = self._update_circle_color(74, 160, 50)
        elif status == AvatarStatus.DM:
            brush_color = self._update_circle_color(255, 0, 0)
        elif status == AvatarStatus.DEACTIVATED:
            brush_color = self._update_circle_color(154, 152, 147)
        elif status == AvatarStatus.IDLE:
            painter.end()
            self.setPixmap(icon_pixmap)
            return

        self.__create_ellipse(painter, background_color, brush_color, icon_pixmap)

    def __create_painter(self, icon_pixmap: QPixmap) -> QPainter:
        """
        Create a painter

        Args:
            icon_pixmap (QPixmap): the icon pixmap

        Returns:
            QPainter: the painter
        """
        result = QPainter(icon_pixmap)
        result.setRenderHint(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        result.drawPixmap(0, 0, icon_pixmap)
        return result

    def __init_pixmap(self) -> QPixmap:
        """
        Init the pixmap

        Returns:
            QPixmap: the pixmap
        """
        pm = QPixmap()
        if not isinstance(self.content, str):
            pm.loadFromData(self.content)
        else:
            pm = self.content
        return QIcon(pm).pixmap(QSize(self.height_, self.width_))

    def __create_ellipse(
        self,
        painter: QPainter,
        outer_brush_color: QColor,
        inner_brush_color: QColor,
        icon_pixmap: QPixmap,
    ) -> None:
        """
        Create an ellipse

        Args:
            painter (QPainter): the painter
            outer_brush_color (QColor): outer brush color
            inner_brush_color (QColor): inner brush color
            icon_pixmap (QPixmap): the icon pixmap
        """
        painter.setPen(QPen(Qt.NoPen))
        circle_radius = 6 if self.height_ >= 30 else 3
        circle_center = QPoint(
            self.width_ - 1.1 * circle_radius, self.height_ - circle_radius * 1
        )

        # Outer circle
        self.__draw_ellipse(outer_brush_color, painter, circle_center, circle_radius)

        inner_radius = circle_radius / 1.5
        inner_center = circle_center

        # Inner circle
        self.__draw_ellipse(inner_brush_color, painter, inner_center, inner_radius)

        if inner_brush_color == QColor(255, 0, 0):
            self.__create_symbole(painter, inner_center, inner_radius)
        painter.end()
        self.setPixmap(icon_pixmap)

    def __create_symbole(
        self, painter: QPainter, inner_center: QPoint, inner_radius: int
    ) -> None:
        """
        Create a symbole

        Args:
            painter (QPainter): the painter
            inner_center (QPoint): the inner center
            inner_radius (int): the inner radius
        """
        # Draw "!" inside the circle
        painter.setPen(QPen(Qt.black))  # Set text color
        font = QFont()
        font.setPointSize(8)  # Adjust the font size as needed
        painter.setFont(font)
        text = "!"
        text_rect = QRectF(
            inner_center.x() - inner_radius,
            inner_center.y() - inner_radius,
            2 * inner_radius,
            2 * inner_radius,
        )
        painter.drawText(text_rect, Qt.AlignCenter, text)

    def __draw_ellipse(
        self, color: QColor, painter: QPainter, center: QPoint, radius: int
    ) -> None:
        """
        Draw an ellipse

        Args:
            arg0 (QColor): the color
            painter (QPainter): the painter
            center (QPoint): the center
            radius (int): the radius
        """
        outer_brush = QBrush(color)
        painter.setBrush(outer_brush)
        painter.drawEllipse(center, radius, radius)
