import logging
import signal
import socket
from threading import Thread


class Server:
    def __init__(self, host, port, conn_nb=2):
        # create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(conn_nb)
        self.conn_dict = {}

        signal.signal(signal.SIGTERM, self.close_connection)
        self.launch()
    
    def launch(self):
        """
            Launch the server
        """
        while "Server connected":
            conn, addr = self.sock.accept()
            conn_thread = Thread(target=self.create_connection, args=(conn, addr), daemon=True)
            conn_thread.start()
    
    def close_connection(self, *args):
        """
            Close the connection
        """
        # close the socket
        logging.debug("Server disconnected")
        self.sock.close()
        
    def read_data(self, conn):
        """
            Read raw data from the client

        Args:
            conn (socket): socket of the client

        Raises:
            ConnectionAbortedError: raise error if the client disconnects

        Returns:
            str: return string of the received data
        """
        raw_data = b""
        while True:
            chunk = conn.recv(1)
            if chunk != b"\n":
                raw_data += chunk
            elif chunk == b"\n":
                break
            # In case of a client disconnecting, the response is empty
            if chunk == b"":
                raise ConnectionAbortedError
        return raw_data.decode('utf-8')
    
    def send_data(self, conn, data:str, is_from_server=False):
        """
            Send data to the client

        Args:
            conn (socket): socket of the client
            data (str): data to send
            is_from_server (bool, optional): if msg come from server. Defaults to False.
        """
        message = f"from server:{data}\n" if is_from_server else f"{data}\n"
        conn.send(message.encode('utf-8'))

    def create_connection(self, conn, addr):
        """
            Create a new connection

        Args:
            conn (socket): Socket of the client
            addr (str): address of the client
        """
        already_connected = len(self.conn_dict) == 1
        self.conn_dict[addr] = conn

        # send data to client
        self.send_data(conn, "Welcome to the server 😀", is_from_server=True)

        if already_connected:
            inner_message = "A client is already connected"
            outer_message = "A new client has joined the server"
        else:
            inner_message = "You're alone in the server"
            outer_message = None

        self.send_data(self.conn_dict[addr], inner_message, is_from_server=True)

        if outer_message and already_connected:
            for address in list(self.conn_dict.keys()):
                if address != addr:
                    self.send_data(self.conn_dict[address], outer_message, is_from_server=True)
                    break

        logging.debug(f'Connected by {addr}')
        # receive the data in small chunks and retransmit it
        try:
            while True:
                data = self.read_data(conn)
                already_connected = len(self.conn_dict) == 2
                if already_connected:
                    for address in list(self.conn_dict.keys()):
                        if address != addr:
                            self.send_data(self.conn_dict[address], data)
                            break
                else:
                    return_message = "No client connected, please try again!"
                    self.send_data(self.conn_dict[addr], return_message, is_from_server=True)
                logging.debug(f"Client {addr}: >> {data}")
        except ConnectionAbortedError:
            self._display_disconnection(conn, addr)

    def _display_disconnection(self, conn, addr):
        """
            Display disconnection on gui

        Args:
            conn (socket): socket of the client
            addr (str): socket address of the client
        """
        logging.debug('Connection aborted by the client')
        conn.close()
        self.conn_dict.pop(addr)
        already_connected = len(self.conn_dict) == 1
        if already_connected:
            for address in list(self.conn_dict.keys()):
                if address != addr:
                    data = "Other Client disconnected"
                    self.send_data(self.conn_dict[address], data, is_from_server=True)
                    break
                

