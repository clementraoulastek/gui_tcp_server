import sys
from src.client.gui.CustomQLineEdit import CustomQLineEdit
from src.client.gui.CustomQPushButton import CustomQPushButton
from src.client.qt_core import (
    QApplication,
    QLabel,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    Qt,
    QScrollArea,
    QIcon,
    QSize
)
from src.tools.utils import Color, Icon, QIcon_from_svg

class QtGui:
    def __init__(self, title):
        self.app = QApplication([])
        self.main_window = MainWindow(title)
        self.main_window.show()
        
    def run(self):
        sys.exit(self.app.exec())

class MainWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setFixedHeight(600)
        self.setFixedWidth(300)
        self.setWindowTitle(title)
        self.setup_gui()
        
    def setup_gui(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_widget.setStyleSheet("background-color: transparent;")
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_widget.setLayout(self.main_layout)
        
        self.set_header_gui()
        self.set_core_gui()
        self.set_footer_gui()
    
    def set_header_gui(self):
        server_status_widget = QWidget()
        server_status_widget.setStyleSheet(f"background-color: {Color.LIGHT_GREY.value};color: black")
        self.status_server_layout = QHBoxLayout(server_status_widget)
        self.status_server_layout.setContentsMargins(90, 0, 85, 0)
        self.status_server_icon = QIcon(QIcon_from_svg(Icon.STATUS.value)).pixmap(QSize(30, 30))
        self.icon_label = QLabel("")
        self.status_server_label = QLabel("Status Server")
        self.icon_label.setPixmap(self.status_server_icon)
        self.status_server_layout.addWidget(self.icon_label)
        self.status_server_layout.addWidget(self.status_server_label)
        self.main_layout.addWidget(server_status_widget)
        
    def set_core_gui(self):
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setObjectName(u"scroll layout")
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setMaximumHeight(400)
        self.scroll_area.setMinimumHeight(400)
        self.scroll_area.setMinimumWidth(200)
        self.scroll_widget = QWidget()
        self.scroll_area.setStyleSheet("background-color: transparent;")
        self.scroll_area.setObjectName(u"scroll_feature")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")

        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.main_layout.addWidget(self.scroll_area, Qt.AlignmentFlag.AlignCenter, Qt.AlignmentFlag.AlignCenter)
    
    def set_footer_gui(self):
        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName("button layout")
        self.button_layout.setSpacing(1)
        
        self.clear_button = CustomQPushButton("Clear")
        self.clear_icon = QIcon(QIcon_from_svg(Icon.CLEAR.value))
        self.clear_button.setIcon(self.clear_icon)
        
        self.login_button = CustomQPushButton("Login")
        self.login_icon = QIcon(QIcon_from_svg(Icon.LOGIN.value))
        self.login_button.setIcon(self.login_icon)
        
        self.logout_button = CustomQPushButton("Logout")
        self.logout_icon = QIcon(QIcon_from_svg(Icon.LOGOUT.value))
        self.logout_button.setIcon(self.logout_icon)
        
        self.settings_button = CustomQPushButton("")
        self.settings_icon = QIcon(QIcon_from_svg(Icon.CONFIG.value))
        self.settings_button.setFixedWidth(50)
        self.settings_button.setIcon(self.settings_icon)
        
        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addWidget(self.login_button)
        self.button_layout.addWidget(self.logout_button)
        self.button_layout.addWidget(self.settings_button)
        
        self.main_layout.addLayout(self.button_layout)
        
        self.entry_message = CustomQLineEdit(place_holder_text="Enter your message")

        self.main_layout.addWidget(self.entry_message)

        self.send_button = CustomQPushButton("Send message")
        self.send_icon = QIcon(QIcon_from_svg(Icon.SEND.value))
        self.send_button.setIcon(self.send_icon)
        
        self.main_layout.addWidget(self.send_button)
        
        
        
        
        
        