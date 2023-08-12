from src.tools.commands import Commands


class TcpServerController:
    def __init__(self, ui) -> None:
        self.ui = ui

    def is_connected_to_server(self) -> bool:
        self.ui.client.init_connection()
        return bool(self.ui.client.is_connected)
