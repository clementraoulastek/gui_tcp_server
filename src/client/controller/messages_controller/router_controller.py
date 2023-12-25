"""Module dedicated to routing messages comming from the server"""

import logging
import time

from src.client.controller import global_variables
from src.tools.commands import Commands


class RouterController:
    """
    Router controller class.
    """

    def __init__(self, parent, ui):
        self.ui = ui
        self.parent = parent

    def callback_routing_messages_on_ui(self) -> None:
        """
        Read messages comming from server
        """
        waiting_time = 0.01

        while self.ui.client.is_connected:
            header, payload = self.ui.client.read_data()
            if payload:
                self.routing_coming_messages(header, payload)
            else:
                break
            time.sleep(waiting_time)

        logging.debug("Connection lost with the server")

    def routing_coming_messages(self, header: int, payload: str) -> None:
        """
        Update global variables with input messages

        Args:
            header (int): header of the message
            payload (str): payload of the message
        """
        if ":" in payload:
            if header == Commands.CONN_NB.value:
                nb_of_users = payload.split(":")[1]
                self.ui.left_nav_widget.info_label.setText(
                    f"Users online   |   {nb_of_users}"
                )
            elif header == Commands.HELLO_WORLD.value:
                self.parent.avatar_controller.add_sender_avatar(
                    payload, global_variables.user_disconnect
                )
                # Return welcome to hello world
                self.ui.client.send_data(Commands.WELCOME, Commands.WELCOME.name)
            elif header == Commands.WELCOME.value:
                self.parent.avatar_controller.add_sender_avatar(
                    payload, global_variables.user_disconnect
                )
            elif header == Commands.GOOD_BYE.value:
                self.parent.avatar_controller.remove_sender_avatar(
                    payload,
                    global_variables.user_connected,
                    global_variables.user_disconnect,
                )
            elif header in [Commands.ADD_REACT.value, Commands.RM_REACT.value]:
                self.parent.react_controller.handle_reaction(payload)
            else:
                self.parent.messages_controller.handle_message(payload)
