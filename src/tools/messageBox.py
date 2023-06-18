from src.client.core.qt_core import QMessageBox


class CustomMessageBox(QMessageBox):
    def __init__(self, *args, title, text, **kwargs):
        super(CustomMessageBox, self).__init__(*args, **kwargs)

        self.setWindowTitle(title)
        self.setText(text)
        self.setIcon(QMessageBox.Icon.Information)
        self.exec_()
