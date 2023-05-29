from server import Server
from gui import Gui

if __name__ == "__main__":
    # Create a GUI client
    first_gui = Gui(title="Client 1")
    
    # # Create a second GUI client
    # second_gui = Gui(title="Client 2", root=first_gui.root)
    
    # Run the GUI Loop
    first_gui.start()
    