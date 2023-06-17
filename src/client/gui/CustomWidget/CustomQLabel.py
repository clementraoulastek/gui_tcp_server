from src.client.core.qt_core import Qt, QPixmap, QLabel, QPainter, QPainter, QPainterPath, QImage

class RoundedLabel(QLabel):
    def __init__(self, *args, content=None, **kwargs):
        super(RoundedLabel, self).__init__(*args, **kwargs)
        self.update_picture(content)
        
    def update_picture(self, content, antialiasing=True):
        self.Antialiasing = antialiasing
        self.setMaximumSize(50, 50)
        self.setMinimumSize(50, 50)
        self.radius = 25 

        self.target = QPixmap(self.size())  
        self.target.fill(Qt.transparent)
        if isinstance(content, str):
            p = QPixmap(content)
        else:
            p = QPixmap()
            p.loadFromData(content)
        p=p.scaled(50, 50, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        painter = QPainter(self.target)
        if self.Antialiasing:
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        path = QPainterPath()
        path.addRoundedRect(
            0, 0, self.width(), self.height(), self.radius, self.radius)

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, p)
        self.setPixmap(self.target)    