import logging
import socket

from src.tools.commands import Commands


class Client:
    def __init__(self, host: str, port: int, name: str) -> None:
        self.user_name = name
        self.port = port
        self.host = host
        self.is_connected = False

    def init_connection(self) -> None:
        """
        Init socket connection
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.send_data(Commands.HELLO_WORLD, "")
            self.is_connected = True
        except Exception as error:
            logging.error(error)
            self.is_connected = False

    def close_connection(self, *args) -> None:
        """
        Socket disconection
        """
        # close the connection
        logging.debug("Closing client connection")
        self.send_data(Commands.GOOD_BYE, "")
        self.sock.close()
        self.is_connected = False

    def read_data(self):
        """
            Read data from the socket

        Returns:
            str, bool: return
        """
        raw_data = b""
        try:
            while "Server connected":
                chunk = self.sock.recv(1)
                if chunk != b"\n":
                    raw_data += chunk
                else:
                    break
            header, payload = int(raw_data[0]), raw_data[1:].decode("utf-8")
            return header, payload
        except Exception as error:
            logging.error(error)
            self.sock.close()
            logging.debug("Closing connection")
            self.is_connected = False
            return False, False

    def send_data(self, header: Commands, payload: str) -> None:
        """
            Send data to the socket

        Args:
            data (str): string data to send
        """
        message = f"{self.user_name}: {payload}\n"

        bytes_message = header.value.to_bytes(1, "big") + message.encode("utf-8")
        self.sock.send(bytes_message)
