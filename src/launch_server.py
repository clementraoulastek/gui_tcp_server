from src.tools.constant import PORT_NB
from src.tools.logger import setup_logger
from src.server.server import Server

if __name__ == "__main__":
    setup_logger("server.log")
    Server("", PORT_NB)
