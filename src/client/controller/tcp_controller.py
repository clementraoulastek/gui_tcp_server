"""Module for the TCP server controller."""


class TcpServerController:
    def __init__(self, ui) -> None:
        self.ui = ui

    def is_connected_to_server(self) -> bool:
        """
        Check if the client is connected to the server.

        Returns:
            bool: True if the client is connected to the server, False otherwise
        """
        self.ui.client.init_connection()
        return bool(self.ui.client.is_connected)
