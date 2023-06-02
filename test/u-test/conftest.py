import pytest
from src.server.server import Server
from src.client.client import Client
from src.tools.constant import DEFAULT_CLIENT_NAME, IP_SERVER, PORT_NB
from src.tools.logger import setup_logger

setup_logger("test.log")

@pytest.fixture
def server():
    server=Server(IP_SERVER, PORT_NB)
    yield server
    server.close_connection()
    
@pytest.fixture
def client():
    client = Client(IP_SERVER, PORT_NB, DEFAULT_CLIENT_NAME)
    client.init_connection()
    yield client
    client.close_connection()


    
    

    
