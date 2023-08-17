from src.client.core.qt_core import (
    QScrollArea,
    Qt,
    QVBoxLayout,
    QWidget,
    QLayout,
)
from src.client.view.stylesheets.stylesheets import scroll_bar_vertical_stylesheet

class BodyLayout(QVBoxLayout):
    def __init__(self, core_layout: QLayout, name: str):
        """
        Update the core GUI
        """
        super(BodyLayout, self).__init__()
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setContentsMargins(0, 0, 0, 0)
        self.setObjectName(name)

        # ----------------- Scroll Area ----------------- #
        self.scroll_area = QScrollArea()
        self.scroll_area.setMinimumWidth(600)
        self.scroll_area.verticalScrollBar().rangeChanged.connect(self.scrollToBottom)

        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setMinimumHeight(380)

        self.scroll_widget = QWidget()
        self.scroll_widget.setContentsMargins(0, 0, 10, 0)
        self.scroll_area.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet
        )
        self.scroll_area.setStyleSheet(
            "background-color: transparent;\
            color: white"
        )
        self.scroll_area.setObjectName("scroll_feature")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")

        self.scroll_widget.setLayout(self)
        self.scroll_area.setWidget(self.scroll_widget)
        #

        core_layout.addWidget(self.scroll_area)

    def scrollToBottom(self):
        """
        Update the scrollbar vertical position to the bottom
        """
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )