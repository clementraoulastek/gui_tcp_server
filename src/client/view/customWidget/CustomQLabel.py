from src.client.core.qt_core import QPixmap, QLabel, QIcon, QSize


class RoundedLabel(QLabel):
    def __init__(self, *args, content=None, **kwargs):
        super(RoundedLabel, self).__init__(*args, **kwargs)
        self.update_picture(content)
        self.setStyleSheet("border-radius: 40px;")  # not working

    def update_picture(self, content):
        if isinstance(content, str):
            p = QIcon(content).pixmap(QSize(50, 50))
        else:
            pm = QPixmap()
            pm.loadFromData(content)
            p = QIcon(pm).pixmap(QSize(50, 50))
        self.setPixmap(p)
