"""Entry point for the client application."""

# pylint: disable=import-error
from src.client.view.view import QtGui
from src.tools.constant import DEFAULT_CLIENT_NAME
from src.tools.logger import setup_logger

if __name__ == "__main__":
    setup_logger("client.log")
    qt_gui = QtGui(title=DEFAULT_CLIENT_NAME)
    qt_gui.run()
