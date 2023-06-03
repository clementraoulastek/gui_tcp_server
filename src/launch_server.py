from src.server.server import Server
from src.tools.constant import PORT_NB
from src.tools.logger import setup_logger

if __name__ == "__main__":
    setup_logger("server.log")
    Server("", PORT_NB)
