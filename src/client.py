import socket

class Client:
    def __init__(self, host, port, name):
        # create a TCP/IP socket
        self.user_name = name
        self.port = port
        self.host = host
        self.is_connected = False
        
    def init_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.is_connected = True
      
    def close_connection(self, *args):
        # close the connection
        print("Closing connection")
        self.sock.close()
        self.is_connected = False
        
    def read_data(self):
        line = b""
        while True:
            part = self.sock.recv(1)
            if part != b"\n":
                line+=part
            else:
                break
        message = line.decode('utf-8')
        from_server = "from server" in message
        if from_server:
            message = message.replace("from server", "")
    
        return message, from_server
    
    def send_data(self, data:str, is_from_server=False):
        message = f"from server{self.user_name}: {data}\n" if is_from_server else f"{self.user_name}: {data}\n"
        self.sock.send(message.encode('utf-8'))

