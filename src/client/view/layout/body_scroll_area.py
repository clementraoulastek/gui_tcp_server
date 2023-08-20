from src.client.core.qt_core import (
    QScrollArea,
    Qt,
    QVBoxLayout,
    QWidget,
    QLayout,
)
from src.client.view.stylesheets.stylesheets import scroll_bar_vertical_stylesheet


class BodyScrollArea(QScrollArea):
    def __init__(self, name: str):
        """
        Update the core GUI
        """
        super(BodyScrollArea, self).__init__()
        # ----------------- Main Layout ----------------- #
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setObjectName(f"{name}_layout")

        # ----------------- Scroll Area ----------------- #
        self.setMinimumWidth(600)
        self.verticalScrollBar().rangeChanged.connect(self.scrollToBottom)

        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumHeight(380)

        self.scroll_widget = QWidget()
        self.scroll_widget.setContentsMargins(0, 0, 10, 0)
        self.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet
        )
        self.setStyleSheet(
            "background-color: transparent;\
            color: white"
        )
        self.setObjectName(name)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.scroll_widget.setLayout(self.main_layout)
        self.setWidget(self.scroll_widget)
        if self.objectName() != "home_area":
            #self.hide()
            pass


    def scrollToBottom(self):
        """
        Update the scrollbar vertical position to the bottom
        """
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        )
