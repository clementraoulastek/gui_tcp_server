from src.client.gui.qt_gui import QtGui
from src.tools.constant import DEFAULT_CLIENT_NAME
from src.tools.logger import setup_logger

if __name__ == "__main__":
    setup_logger("client.log")
    qt_gui = QtGui(title=DEFAULT_CLIENT_NAME)
    # Run the GUI Loop
    qt_gui.run()
