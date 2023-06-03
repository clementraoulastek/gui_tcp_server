from src.client.qt_gui import QtGui
from src.client.tk_gui import Gui
from src.tools.constant import DEFAULT_CLIENT_NAME
from src.tools.logger import setup_logger

if __name__ == "__main__":
    setup_logger("client.log")
    # tk_gui = Gui(title=DEFAULT_CLIENT_NAME)
    qt_gui = QtGui(title=DEFAULT_CLIENT_NAME)
    # Run the GUI Loop
    qt_gui.run()
    # tk_gui.start()
