"""Module for the main controller of the client application"""

import re

from src.client.controller import global_variables
from src.client.controller.api_controller import ApiController
from src.client.controller.event_manager import EventManager
from src.client.controller.gui_controller import GuiController
from src.client.controller.tcp_controller import TcpServerController
from src.client.view.layout.message_layout import MessageLayout
from src.tools.commands import Commands
from src.tools.utils import Themes


class MainController:
    """
    Main controller of the client application
    """

    def __init__(self, ui, theme: Themes) -> None:
        self.ui = ui
        self.messages_dict: dict[str, MessageLayout] = {}

        self.event_manager = EventManager()

        self.tcp_controller = TcpServerController(self.ui)
        self.api_controller = ApiController(self.ui, self.event_manager)

        self.gui_controller = GuiController(
            self.ui,
            self.messages_dict,
            self.api_controller,
            self.tcp_controller,
            self.event_manager,
            theme,
        )

    # pylint: disable=unused-argument
    def send_message_to_server(self, *args) -> None:
        """
        Send message to the server and update GUI

        Args:
            signal (event): event coming from signal
        """
        receiver: str = self.ui.scroll_area.objectName()
        if message := self.ui.footer_widget.entry.text():
            # pylint: disable=anomalous-backslash-in-string
            if message_id := re.findall("#(\w+)/", global_variables.reply_id):
                message_id = int(message_id[0])
                global_variables.reply_id = ""

            self.ui.client.send_data(
                Commands.MESSAGE,
                message,
                receiver=receiver,
                response_id=message_id or None,
            )
            self.ui.footer_widget.reply_entry_action.triggered.emit()
            self.ui.footer_widget.entry.clear()
            self.ui.footer_widget.entry.clearFocus()

    def hide_left_layout(self) -> None:
        """
        Hide the left layout
        """
        self.gui_controller.hide_left_layout()

    def hide_right_layout(self) -> None:
        """
        Hide the right layout
        """
        self.gui_controller.hide_right_layout()

    def show_left_layout(self) -> None:
        """
        Show the left layout
        """
        self.gui_controller.show_left_layout()

    def show_right_layout(self) -> None:
        """
        Show the right layout
        """
        self.gui_controller.show_right_layout()

    def show_footer_layout(self) -> None:
        """
        Show the footer layout
        """
        self.gui_controller.show_footer_layout()

    def hide_footer_layout(self) -> None:
        """
        Hide the footer layout
        """
        self.gui_controller.hide_footer_layout()

    def login(self) -> None:
        """
        Login to the server
        """
        self.gui_controller.connection_controller.login()
        self._hide()

    def logout(self) -> None:
        """
        Logout from the server
        """
        self.gui_controller.connection_controller.logout()
        self._hide()

    def _hide(self):
        """
        Hide the components
        """
        self.gui_controller.ui.left_nav_widget.scroll_area_avatar.hide()
        self.gui_controller.ui.right_nav_widget.scroll_area_dm.hide()
        self._hide_components()

    def _hide_components(self) -> None:
        """
        Hide the components
        """
        self.gui_controller.hide_footer_layout()
        self.gui_controller.hide_left_layouts_buttons()
        self.gui_controller.hide_right_layouts_buttons()

    def update_user_icon(self) -> None:
        """
        Update the user icon
        """
        self.gui_controller.user_profile_controller.update_user_icon()

    def show_user_profile(self) -> None:
        """
        Show the user profile
        """
        self.gui_controller.user_profile_controller.show_user_profile()
