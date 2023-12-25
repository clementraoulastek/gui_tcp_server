"""BodyScrollArea Layout Module."""

from src.client.core.qt_core import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    Qt,
    QTimer,
    QVBoxLayout,
    QWidget,
)
from src.client.view.stylesheets.stylesheets import scroll_bar_vertical_stylesheet
from src.tools.utils import Themes, check_str_len

theme = Themes()


class BodyScrollArea(QScrollArea):
    """
    BodyScrollArea widget class.

    Args:
        QScrollArea (QScrollArea): the scroll area widget
    """

    def __init__(self, name: str, gui_controller):
        """
        Update the core GUI
        """
        super(BodyScrollArea, self).__init__()

        self.name = name
        self.gui_controller = gui_controller
        self.nb_message_displayed = 0
        self.is_adding_older_messages = False
        self.scrolling_timer = QTimer()
        self.scrolling_timer.setSingleShot(True)

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

        self.scroll_widget = QWidget()
        self.scroll_widget.setContentsMargins(0, 10, 0, 10)
        self.verticalScrollBar().setStyleSheet(
            scroll_bar_vertical_stylesheet.format(_background_color=theme.search_color)
        )
        self.setStyleSheet(
            "background-color: transparent;\
            color: white;\
            border: 0px"
        )
        self.setObjectName(name)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.is_auto_scroll_ = True
        self.verticalScrollBar().actionTriggered.connect(self.is_auto_scroll)
        self.verticalScrollBar().actionTriggered.connect(
            self.add_older_messages_on_scroll
        )
        self.verticalScrollBar().rangeChanged.connect(self.update_scrollbar)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.scroll_widget.setLayout(self.main_layout)
        self.setWidget(self.scroll_widget)

    def is_auto_scroll(self) -> None:
        """
        Check if the scrollbar is at the bottom
        """
        self.is_auto_scroll_ = (
            self.verticalScrollBar().value() == self.verticalScrollBar().maximum()
        )

    def add_older_messages_on_scroll(self) -> None:
        """
        Add older messages when the scrollbar is at the top
        """
        if (
            not self.scrolling_timer.isActive()
            and self.verticalScrollBar().value() == self.verticalScrollBar().minimum()
        ):
            self.gui_controller.add_older_messages_on_scroll()
            self.scrolling_timer.start(100)

    def update_scrollbar(self) -> None:
        """
        If the scrollbar is at the bottom, update it to the bottom
        """
        if self.is_auto_scroll_:
            self.scrollToBottom()

    def scrollToBottom(self) -> None:
        """
        Update the scrollbar vertical position to the bottom
        """
        scroll_bar = self.verticalScrollBar()
        scroll_bar.updateGeometry()
        scroll_bar.setValue(scroll_bar.maximum())

    def def_upper_widget(self) -> None:
        """
        Define the upper widget
        """
        self.upper_widget = QWidget()
        self.upper_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.upper_widget.setStyleSheet(
            f"background-color: {self.theme.background_color};\
            border-radius: 0px;\
            border: 0px solid {self.theme.nav_color}; "
        )
        upper_layout = QHBoxLayout()
        self.upper_widget.setLayout(upper_layout)

        frame_name = QLabel(f"#{self.name.capitalize()}")
        frame_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_name.setStyleSheet(
            f"color: {self.theme.title_color};\
            font-weight: bold;\
            border: 0px solid;"
        )
        upper_layout.addWidget(frame_name)
        self.main_layout.addWidget(self.upper_widget)
        if self.name == "home":
            self.upper_widget.hide()
