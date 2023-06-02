class TestClient:
    """ Test the client class
    """
    @staticmethod
    def test_init_client(server, client):
        pass
    
    @staticmethod
    def test_read_data(server, client):
        str_data, _ = client.read_data()
        
        assert str_data == "Welcome to the server 😀"
        
    @staticmethod
    def test_send_data(server, client):
        str_data = server.read_data(client.sock)
    
        assert str_data == "from server:Welcome to the server 😀"