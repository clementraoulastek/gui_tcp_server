"""This module contains the client class"""

import logging
import socket
from typing import Optional, Tuple, Union

from src.tools.commands import Commands


class Client:
    """
    Client class, handle socket connection
    """

    SPECIAL_CHAR = "$replaced$"

    def __init__(self, host: str, port: int, name: str) -> None:
        self.user_name = name
        self.port = port
        self.host = host
        self.is_connected = False
        self.sock = None

    # pylint: disable=broad-exception-caught
    def init_connection(self) -> None:
        """
        Init socket connection
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.is_connected = True
        except Exception as error:
            logging.error(error)
            self.is_connected = False

    # pylint: disable=unused-argument
    def close_connection(self, *args) -> None:
        """
        Socket disconection
        """
        # close the connection
        logging.debug("Sending Good Bye ...")
        self.send_data(Commands.GOOD_BYE, Commands.GOOD_BYE.name)
        logging.debug("Good Bye sended sucessfully")
        logging.debug("Closing client connection ...")
        self.sock.close()
        self.is_connected = False

    def read_data(self) -> Union[Tuple[str, str], Tuple[bool, bool]]:
        """
        Read data from the socket

        Returns:
            str, bool: return
        """
        raw_data = b""
        try:
            while self.is_connected:
                chunk = self.sock.recv(1)
                if chunk != b"\n":
                    raw_data += chunk
                else:
                    break
            header, payload = int(raw_data[0]), raw_data[1:].decode("utf-8")
            return header, payload
        except Exception:
            self.sock.close()
            logging.debug("Read data Thread closed")
            self.is_connected = False
            return (False, False)

    def send_data(
        self,
        header: Commands,
        payload: str,
        receiver: Optional[str] = "home",
        response_id: Optional[int] = None,
    ) -> None:
        """
            Send data to the socket

        Args:
            data (str): string data to send
        """
        payload = payload.replace(":", Client.SPECIAL_CHAR)
        message = f"{self.user_name}:{receiver}:{payload}"

        if response_id:
            message += f":{response_id}"

        message += "\n"

        bytes_message = header.value.to_bytes(1, "big") + message.encode("utf-8")
        self.sock.send(bytes_message)
