import logging
from other.constant import DEFAULT_CLIENT_NAME
from client.gui import Gui

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Update the log file
    file_handler = logging.FileHandler('../client.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # Update the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    # Create a GUI client
    gui = Gui(title=DEFAULT_CLIENT_NAME)
    
    # Create a second GUI client
    #Gui(title=DEFAULT_CLIENT_NAME, root=first_gui.root)
    
    # Run the GUI Loop
    gui.start()
    