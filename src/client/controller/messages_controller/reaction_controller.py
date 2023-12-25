"""Reaction controller module."""

from src.client.controller import global_variables
from src.client.view.layout.message_layout import MessageLayout
from src.tools.commands import Commands


class ReactController:
    """
    Reaction controller class.
    """

    def __init__(self, parent, ui, messages_dict: dict) -> None:
        self.parent = parent
        self.ui = ui
        self.messages_dict = messages_dict

    def update_react_message_on_gui(self) -> None:
        """
        Callback to update gui with input messages
        """
        if not global_variables.comming_msg["reaction"]:
            return

        message_id, nb_reaction = (
            global_variables.comming_msg["message_id"],
            global_variables.comming_msg["reaction"],
        )

        if global_variables.comming_msg["receiver"] == "home":
            dict_name = "home"
        else:
            dict_name = (
                global_variables.comming_msg["receiver"]
                if global_variables.comming_msg["id"] == self.ui.client.user_name
                else global_variables.comming_msg["id"]
            )

        message: MessageLayout = self.messages_dict[dict_name][int(message_id)]
        message.update_react(int(nb_reaction))

        # Reset global variables
        (
            global_variables.comming_msg["reaction"],
            global_variables.comming_msg["id"],
            global_variables.comming_msg["receiver"],
            global_variables.comming_msg["message_id"],
        ) = ("", "", "", "")

    def handle_reaction(self, payload: str) -> None:
        """
        Get the message reaction and update global variables

        Args:
            payload (str): payload of the message with reaction number inside
        """
        payload_fields = payload.split(":")
        sender = payload_fields[0]
        receiver = payload_fields[1]
        message = payload_fields[2]
        payload = message.replace(" ", "")
        payload_list = payload.split(";")

        message_id, nb_reaction = payload_list[0], payload_list[1]

        global_variables.comming_msg["id"] = sender
        global_variables.comming_msg["receiver"] = receiver
        global_variables.comming_msg["message_id"] = message_id
        global_variables.comming_msg["reaction"] = nb_reaction

        self.parent.event_manager.event_react_message()

    def send_emot_react(self, cmd: Commands, message_id: int, react_nb: int) -> None:
        """
        Send emot message to the server

        Args:
            cmd (Commands): Commands.RM_REACT ou Commands.ADD_REACT
            messageId (int): id of the message
            react_nb (int): number of reaction
        """
        receiver: str = self.ui.scroll_area.objectName()

        self.ui.client.send_data(
            cmd,
            ";".join([str(message_id), str(react_nb)]),
            receiver=receiver,
        )
