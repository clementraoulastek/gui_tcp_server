from src.client.core.qt_core import (
    QScrollArea,
    Qt,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
)
from src.client.view.stylesheets.stylesheets import scroll_bar_vertical_stylesheet
from src.tools.utils import Color, check_str_len


class BodyScrollArea(QScrollArea):
    def __init__(self, name: str):
        """
        Update the core GUI
        """
        super(BodyScrollArea, self).__init__()

        self.name = name

        # ----------------- Main Layout ----------------- #
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(15)
        self.main_layout.setObjectName(f"{name}_layout")

        self.partial_name = check_str_len(name)

        # ----------------- Scroll Area ----------------- #
        self.setMinimumWidth(600)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumHeight(380)

        self.verticalScrollBar().rangeChanged.connect(self.scrollToBottom)

        self.scroll_widget = QWidget()
        self.scroll_widget.setContentsMargins(0, 0, 0, 0)
        self.verticalScrollBar().setStyleSheet(scroll_bar_vertical_stylesheet)
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

    def scrollToBottom(self):
        """
        Update the scrollbar vertical position to the bottom
        """
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def def_upper_widget(self):
        self.upper_widget = QWidget()
        self.upper_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.upper_widget.setStyleSheet(
            f"background-color: {Color.GREY.value};\
            border-radius: 12px;\
            border: 1px solid {Color.MIDDLE_GREY.value}; "
        )
        upper_layout = QHBoxLayout()
        self.upper_widget.setLayout(upper_layout)

        frame_name = QLabel(f"#{self.name.capitalize()}")
        frame_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_name.setStyleSheet(
            f"color: {Color.LIGHT_GREY.value};\
            font-weight: bold;\
            border: none;"
        )
        upper_layout.addWidget(frame_name)
        self.main_layout.addWidget(self.upper_widget)
        if self.name == "home":
            self.upper_widget.hide()
