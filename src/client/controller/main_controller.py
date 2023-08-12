from src.client.controller.api_controller import ApiController
from src.client.controller.gui_controller import GuiController
from src.client.controller.tcp_controller import TcpServerController
from src.client.view.layout.message_layout import MessageLayout
from src.tools.commands import Commands


class MainController:
    def __init__(self, ui) -> None:
        self.ui = ui
        self.messages_dict: dict[str, MessageLayout] = {}
        self.last_message_id: int = 0

        self.tcp_controller = TcpServerController(self.ui)
        self.api_controller = ApiController(self.ui)

        self.gui_controller = GuiController(
            self.ui,
            self.messages_dict,
            self.last_message_id,
            self.api_controller,
            self.tcp_controller,
        )

    def send_message_to_server(self, *args) -> None:
        """
            Send message to the server and update GUI
        Args:
            signal (event): event coming from signal
        """
        if message := self.ui.entry.text():
            self.ui.client.send_data(Commands.MESSAGE, message)
            self.gui_controller.diplay_self_message_on_gui(
                self.ui.client.user_name, message
            )

    def hide_left_layout(self) -> None:
        self.gui_controller.hide_left_layout()

    def show_left_layout(self) -> None:
        self.gui_controller.show_left_layout()

    def login(self) -> None:
        self.gui_controller.login()

    def logout(self) -> None:
        self.gui_controller.logout()

    def update_user_icon(self) -> None:
        self.gui_controller.update_user_icon()
