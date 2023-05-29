import signal
import socket
from threading import Thread

class Server:
    def __init__(self, host, port):
        # create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(2)
        self.conn_dict = {}

        signal.signal(signal.SIGTERM, self.close_connection)
        self.launch()
    
    def launch(self):
        while True:
            conn, addr = self.sock.accept()
            conn_thread = Thread(target=self.create_connection, args=(conn, addr), daemon=True)
            conn_thread.start()
    
    def close_connection(self, *args):
        # close the socket
        print("Server disconnected")
        self.sock.close()
        
    def read_data(self, conn):
        line = b""
        while True:
            part = conn.recv(1)
            if part != b"\n":
                line+=part
            elif part == b"\n":
                break
            if part == b"":
                raise ConnectionAbortedError
        return line.decode('utf-8')
    
    def send_data(self, conn, data:str, is_from_server=False):
        message = f"from server{data}\n" if is_from_server else f"{data}\n"
        conn.send(message.encode('utf-8'))

    def create_connection(self, conn, addr):
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

        print('Connected by', addr)
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
                print(f"Client {addr}: >> {data}")
        except ConnectionAbortedError:
            self._display_disconnection(conn, addr)

    def _display_disconnection(self, conn, addr):
        print('Connection aborted by the client')
        conn.close()
        self.conn_dict.pop(addr)
        already_connected = len(self.conn_dict) == 1
        if already_connected:
            for address in list(self.conn_dict.keys()):
                if address != addr:
                    data = "Other Client disconnected"
                    self.send_data(self.conn_dict[address], data, is_from_server=True)
                    break
                

