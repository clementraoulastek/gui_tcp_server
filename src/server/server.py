import logging
import socket
import sys
from threading import Thread
from src.tools.backend import Backend

from src.tools.commands import Commands
from src.tools.constant import IP_API, PORT_API


class Server:
    def __init__(self, host: str, port: int, conn_nb: int = 2):
        self.backend = Backend(IP_API, PORT_API)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(conn_nb)
        self.conn_dict = {}
        Thread(target=self.launch).start()
        
        self.hello_world(host, port)
    
    def hello_world(self, hostname, port):
        logging.info(f"Server is running on hostname: {hostname}, port: {port}")

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
        raw_data: bytes = b""
        header, payload = None, None
        while "Empty message":
            chunk = conn.recv(1)
            if chunk not in [b"\n", b""]:
                raw_data += chunk
            else:
                break
        if raw_data:
            header, payload = raw_data[0], raw_data[1:].decode("utf-8")
        return header, payload

    def send_data(self, conn, header: Commands, payload: str, is_from_server=False):
        """
            Send data to the client

        Args:
            conn (socket): socket of the client
            data (str): data to send
            is_from_server (bool, optional): if msg come from server. Defaults to False.
        """
        message = f"server:{payload}\n" if is_from_server else f"{payload}\n"

        bytes_message = header.value.to_bytes(1, "big") + message.encode("utf-8")
        conn.send(bytes_message)

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
                header, payload = self.read_data(conn)
                if not payload:
                    raise ConnectionAbortedError
                self.send_message_to_backend(header, payload)
                for address in list(self.conn_dict.keys()):
                    if address != addr:
                        self.send_data(
                            self.conn_dict[address], Commands(header), payload
                        )
                logging.debug(f"Client {addr}: >> header: {header} payload: {payload}")
        except (ConnectionAbortedError, ConnectionResetError):
            self._display_disconnection(conn, addr)

    def send_message_to_backend(self, header: int, payload: str):
        if Commands(header) == Commands.MESSAGE:
            payload_list = payload.split(":")
            sender, message = payload_list[0], payload_list[1]
            self.backend.send_message(sender, message)
        elif Commands(header) in [Commands.ADD_REACT, Commands.RM_REACT]:
            self._update_reaction(payload)

    def _update_reaction(self, payload):
        payload_list = payload.split(":")
        sender, message = payload_list[0], payload_list[1]
        message_list = message.split(";")
        message_id, reaction_nb = message_list[0], message_list[1]
        logging.info(message)
        self.backend.update_reaction_nb(message_id, reaction_nb)

    def handle_new_connection(self, addr, conn):
        self.conn_dict[addr] = conn

        # Send data to new client
        self.send_data(
            conn, Commands.MESSAGE, "Welcome to the server 😀", is_from_server=True
        )

        # Send nb of conn
        message = f"{len(self.conn_dict)}"

        # Send to all connected clients
        for address in list(self.conn_dict.keys()):
            self.send_data(
                self.conn_dict[address], Commands.CONN_NB, message, is_from_server=True
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
                    message = f"{len(self.conn_dict)}"
                    self.send_data(
                        self.conn_dict[address],
                        Commands.CONN_NB,
                        message,
                        is_from_server=True,
                    )
