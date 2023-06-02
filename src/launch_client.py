from src.client.gui import Gui
from src.tools.constant import DEFAULT_CLIENT_NAME
from src.tools.logger import setup_logger

if __name__ == "__main__":
    setup_logger("client.log")
    gui = Gui(title=DEFAULT_CLIENT_NAME)

    # Run the GUI Loop
    gui.start()
