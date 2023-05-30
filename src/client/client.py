import logging
import socket


class Client:
    def __init__(self, host, port, name):
        self.user_name = name
        self.port = port
        self.host = host
        self.is_connected = False
        
    def init_connection(self):
        """
            Init socket connection
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.is_connected = True
      
    def close_connection(self, *args):
        """
            Socket disconection  
        """
        # close the connection
        logging.debug("Closing connection")
        self.sock.close()
        self.is_connected = False
        
    def read_data(self):
        """
            Read data from the socket

        Returns:
            str, bool: return 
        """
        raw_data = b""
        while True:
            chunk = self.sock.recv(1)
            if chunk != b"\n":
                raw_data+=chunk
            else:
                break
        str_message = raw_data.decode('utf-8')
        from_server = "from server:" in str_message
        if from_server:
            str_message = str_message.replace("from server:", "")
    
        return str_message, from_server
    
    def send_data(self, data:str, is_from_server=False):
        """
            Send data to the socket

        Args:
            data (str): string data to send
            is_from_server (bool, optional): if msg coming from server. Defaults to False.
        """
        message = f"from server:{data}\n" if is_from_server else f"{self.user_name}: {data}\n"
        
        logging.debug(message)

        self.sock.send(message.encode('utf-8'))

