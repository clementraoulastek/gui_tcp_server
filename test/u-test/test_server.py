import pytest

class TestServer:
    """ Test the server class
    """
    @staticmethod
    def test_init_server(server):
        pass
    
    @staticmethod
    def test_read_data(server, client):
        str_data= server.read_data(client.sock)
        
        assert str_data == "from server:Welcome to the server 😀"
    
    @staticmethod
    def test_send_data(server, client):
        str_data, _ = client.read_data()
    
        assert str_data == "Welcome to the server 😀"