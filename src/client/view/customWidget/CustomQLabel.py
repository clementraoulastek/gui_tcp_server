from src.client.core.qt_core import QPixmap, QLabel, QIcon, QSize, QColor, Qt, QPainter


class RoundedLabel(QLabel):
    def __init__(
        self, *args, content=None, height=40, width=40, color=None, disabled=False
    ):
        super(RoundedLabel, self).__init__(*args)
        self.disabled = disabled
        self.color = color
        self.height_ = height
        self.width_ = width
        self.update_picture(content)
        self.setStyleSheet("border-radius: 40px;")  # not working

    def update_picture(self, content):
        if isinstance(content, str):
            p = QIcon(content).pixmap(QSize(self.height_, self.width_))

            if self.color:
                painter = QPainter(p)
                painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                painter.fillRect(p.rect(), QColor(self.color))
                painter.end()
        else:
            pm = QPixmap()
            pm.loadFromData(content)
            p = QIcon(pm).pixmap(QSize(self.height_, self.width_))
        self.setPixmap(p)

        self.setDisabled(self.disabled)
