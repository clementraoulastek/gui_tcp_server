import logging
import socket
import sys
from threading import Thread


class Server:
    def __init__(self, host: str, port: int, conn_nb: int = 2):
        # create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(conn_nb)
        self.conn_dict = {}

        Thread(target=self.launch).start()

    def launch(self):
        """
        Launch the server
        """
        try:
            while "Server connected":
                conn, addr = self.sock.accept()
                conn_thread = Thread(
                    target=self.create_connection,
                    args=(conn, addr),
                    name=f"{addr} thread",
                    daemon=True,
                )
                conn_thread.start()
        except (KeyboardInterrupt, ConnectionAbortedError):
            Thread(
                target=self.close_connection,
                name="Close Connection thread, no deamon thread",
            ).start()

    def close_connection(self, *args):
        """
        Close the connection
        """
        # close the socket
        logging.info("Server disconnected")
        self.sock.close()
        sys.exit(0)

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

        while "Empty message":
            chunk = conn.recv(1)
            if chunk not in [b"\n", b""]:
                raw_data += chunk
            else:
                break

        return raw_data.decode("utf-8")

    def send_data(self, conn, data: str, is_from_server=False):
        """
            Send data to the client

        Args:
            conn (socket): socket of the client
            data (str): data to send
            is_from_server (bool, optional): if msg come from server. Defaults to False.
        """
        message = f"from server:{data}\n" if is_from_server else f"{data}\n"
        conn.send(message.encode("utf-8"))

    def create_connection(self, conn, addr):
        """
            Create a new connection

        Args:
            conn (socket): Socket of the client
            addr (str): address of the client
        """
        self.handle_new_connection(addr, conn)

        logging.debug(f"Connected by {addr}")
        # receive the data in small chunks and retransmit it
        try:
            while "Client connected":
                data = self.read_data(conn)
                if not data:
                    raise ConnectionAbortedError
                already_connected = len(self.conn_dict) >= 2
                if already_connected:
                    for address in list(self.conn_dict.keys()):
                        if address != addr:
                            self.send_data(self.conn_dict[address], data)
                else:
                    return_message = (
                        "No client connected, your message go nowhere"
                    )
                    self.send_data(
                        self.conn_dict[addr], return_message, is_from_server=True
                    )
                logging.debug(f"Client {addr}: >> {data}")
        except (ConnectionAbortedError, ConnectionResetError):
            self._display_disconnection(conn, addr)

    def handle_new_connection(self, addr, conn):
        already_connected = len(self.conn_dict) >= 1
        self.conn_dict[addr] = conn

        # send data to client
        self.send_data(conn, "Welcome to the server 😀", is_from_server=True)

        if already_connected:
            inner_message = "A client is already connected 😀"
            outer_message = "A new client has joined the server 😀"
        else:
            inner_message = "You're alone in the server 😢"
            outer_message = None

        self.send_data(self.conn_dict[addr], inner_message, is_from_server=True)

        if outer_message and already_connected:
            for address in list(self.conn_dict.keys()):
                if address != addr:
                    self.send_data(
                        self.conn_dict[address], outer_message, is_from_server=True
                    )

    def _display_disconnection(self, conn, addr):
        """
            Display disconnection on gui

        Args:
            conn (socket): socket of the client
            addr (str): socket address of the client
        """
        logging.debug("Connection aborted by the client")
        conn.close()
        self.conn_dict.pop(addr)
        already_connected = len(self.conn_dict) >= 1
        if already_connected:
            for address in list(self.conn_dict.keys()):
                if address != addr:
                    data = "Other Client disconnected"
                    self.send_data(self.conn_dict[address], data, is_from_server=True)
