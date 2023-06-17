from src.client.core.qt_core import Qt, QPixmap, QLabel, QPainter, QPainter, QPainterPath

class RoundedLabel(QLabel):
    def __init__(self, *args, path=None, antialiasing=True, **kwargs):
        super(RoundedLabel, self).__init__(*args, **kwargs)
        self.update_picture(path, antialiasing)
        
    def update_picture(self, path, antialiasing=True):
        self.Antialiasing = antialiasing
        self.setMaximumSize(50, 50)
        self.setMinimumSize(50, 50)
        self.radius = 25 

        self.target = QPixmap(self.size())  
        self.target.fill(Qt.transparent)   

        p = QPixmap(path).scaled(  
            50, 50, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

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