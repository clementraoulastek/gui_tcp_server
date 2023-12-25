"""Module for messages controller"""

import logging
from functools import partial
from typing import List, Optional, OrderedDict, Union

from PySide6.QtCore import QTimer

from src.client.client import Client
from src.client.controller import global_variables
from src.client.view.custom_widget.custom_avatar_label import AvatarLabel, AvatarStatus
from src.client.view.layout.message_layout import MessageLayout
from src.tools.utils import GenericColor


class MessagesController:
    """
    Messages controller class.
    """

    def __init__(self, parent, ui, messages_dict: dict) -> None:
        self.parent = parent
        self.ui = ui
        self.messages_dict = messages_dict

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    def diplay_self_message_on_gui(
        self,
        sender: str,
        message: str,
        frame_name: Optional[Union[str, None]] = None,
        message_id: Optional[Union[int, None]] = None,
        nb_react: Optional[int] = 0,
        date: Optional[str] = "",
        response_model: Optional[Union[MessageLayout, None]] = None,
        display: Optional[bool] = True,
        reverse: Optional[bool] = False,
    ) -> None:
        """
        Display message on gui and clear the message entry

        Args:
            sender (str): username
            message (str): message
            frame_name (Optional[Union[str, None]], optional): layout name. Defaults to None.
            messsage_id (Optional[Union[int, None]], optional): message id. Defaults to None.
            nb_react (Optional[int], optional): number of reactions. Defaults to 0.
            date (Optional[str], optional): date to display. Defaults to "".
            response_model (Optional[Union[MessageLayout, None]]): Defaults to None.
        """
        comming_msg: dict[str, str] = {"id": sender, "message": message}

        # Init dict key
        if frame_name not in self.messages_dict.keys():
            self.messages_dict[frame_name] = OrderedDict()

        # Avoid to re-create the same message from an older request from a response model
        if message_id not in self.messages_dict[frame_name].keys():
            message = MessageLayout(
                self.parent,
                comming_msg,
                content=self.ui.users_pict[sender],
                message_id=message_id,
                nb_react=nb_react,
                date=date,
                response_model=response_model,
            )
            # Update the dict
            self.messages_dict[frame_name][message_id] = message

            if response_model and response_model.sender_ == self.ui.client.user_name:
                self.parent.update_stylesheet_with_focus_event(
                    message, border_color=self.parent.theme.emoji_color
                )
        else:
            message = self.messages_dict[frame_name][message_id]

        # Display message on gui on the frame
        if display:
            if reverse:
                self.ui.body_gui_dict[frame_name].main_layout.insertLayout(0, message)
            else:
                self.ui.body_gui_dict[frame_name].main_layout.addLayout(message)
            message.is_displayed = True

        self.ui.footer_widget.entry.clear()

        # Avoid gui troubles on scroll
        if not reverse:
            QTimer.singleShot(0, self.parent.update_scroll_bar)

    def display_older_messages(
        self,
        older_messages: dict,
        display: Optional[bool] = True,
        reverse: Optional[bool] = False,
    ) -> None:
        """
        Update gui with older messages
        """
        sender_list: list[str] = []

        for message in older_messages:
            (
                message_id,
                sender,
                receiver,
                message,
                reaction_nb,
                date,
                is_readed,
                response_id,
            ) = (
                message["message_id"],
                message["sender"],
                message["receiver"],
                message["message"],
                message["reaction_nb"],
                message["created_at"],
                message["is_readed"],
                message["response_id"],
            )
            if (
                receiver != "home"
                and sender != self.ui.client.user_name
                and receiver != self.ui.client.user_name
            ):
                continue

            if receiver == "home":
                dict_name = "home"
            else:
                dict_name = receiver if sender == self.ui.client.user_name else sender

            # Add new room to the messages dict
            if dict_name not in self.messages_dict.keys():
                self.messages_dict[dict_name] = OrderedDict()

            if response_id and response_id not in self.messages_dict[dict_name]:
                older_message = self.parent.api_controller.get_older_message(
                    response_id
                )
                self.display_older_messages(older_message, display=False, reverse=True)

            message_model = (
                self.messages_dict[dict_name][response_id] if response_id else None
            )

            # Add a special char to handle the ":" in the message
            message = message.replace(Client.SPECIAL_CHAR, ":")

            # Add sender to a list to avoid multiple avatar update
            if sender not in sender_list:
                sender_list.append(sender)

            # Display message on gui on the home frame
            if receiver == "home":
                self.diplay_self_message_on_gui(
                    sender,
                    message,
                    frame_name="home",
                    message_id=message_id,
                    nb_react=int(reaction_nb),
                    date=date,
                    response_model=message_model,
                    display=display,
                    reverse=reverse,
                )
            # Display message on gui on the direct message frame
            elif self.ui.client.user_name in (sender, receiver):
                direct_message_name = (
                    receiver if sender == self.ui.client.user_name else sender
                )
                icon = AvatarLabel(
                    content=self.ui.users_pict[direct_message_name],
                    status=AvatarStatus.DEACTIVATED,
                )
                self.parent.add_gui_for_mp_layout(direct_message_name, icon)

                # Update avatar status with DM circle popup
                if is_readed is False and self.ui.client.user_name == receiver:
                    self.parent.avatar_controller.update_pixmap_avatar(
                        direct_message_name, AvatarStatus.DM
                    )

                self.diplay_self_message_on_gui(
                    sender,
                    message,
                    frame_name=direct_message_name,
                    message_id=message_id,
                    nb_react=int(reaction_nb),
                    date=date,
                    response_model=message_model,
                    display=display,
                    reverse=reverse,
                )

        # Reset dict to handle new avatar images from conn
        if self.ui.client.user_name in sender_list:
            sender_list.remove(self.ui.client.user_name)

    def diplay_coming_message_on_gui(self) -> None:
        """
        Callback to update gui with input messages
        """
        if not global_variables.comming_msg["message"]:
            return None

        message_id = global_variables.comming_msg["message_id"]

        message_model = None
        message = global_variables.comming_msg["message"]

        receiver = global_variables.comming_msg["receiver"]

        if response_id := global_variables.comming_msg["response_id"]:
            response_id = int(response_id)
            if receiver == self.ui.client.user_name:
                response_model_receiver = global_variables.comming_msg["id"]
            else:
                response_model_receiver = receiver

            if (
                response_id
                and response_id not in self.messages_dict[response_model_receiver]
            ):
                older_message = self.parent.api_controller.get_older_message(
                    response_id
                )
                self.display_older_messages(older_message, display=False, reverse=True)
            message_model = self.messages_dict[response_model_receiver][response_id]

        message = MessageLayout(
            self.parent,
            global_variables.comming_msg,
            content=self.ui.users_pict[global_variables.comming_msg["id"]],
            message_id=message_id
            if global_variables.comming_msg["id"] != "server"
            else None,
            response_model=message_model,
        )
        if message_model and message_model.sender_ == self.ui.client.user_name:
            self.parent.update_stylesheet_with_focus_event(
                message, border_color=self.parent.theme.emoji_color
            )
            if global_variables.comming_msg["receiver"] == "home":
                self.parent.room_icon.update_pixmap(
                    AvatarStatus.DM,
                    background_color=self.parent.theme.rgb_background_color_rooms,
                )

        # Revert sender and receiver for DM if the sender is the user
        if receiver == self.ui.client.user_name:
            receiver = global_variables.comming_msg["id"]
            update_avatar = True
        else:
            update_avatar = False

        if receiver not in {"home", self.ui.client.user_name}:
            self.parent.add_gui_for_mp_layout(
                receiver,
                AvatarLabel(
                    content=self.ui.users_pict[global_variables.comming_msg["id"]],
                    status=AvatarStatus.DM,
                ),
            )

        if update_avatar:
            # Update avatar status with DM circle popup
            self.parent.dm_avatar_dict[receiver].update_pixmap(
                AvatarStatus.DM,
                background_color=self.parent.theme.rgb_background_color_actif,
            )

        # Init dict key
        if receiver not in self.messages_dict.keys():
            self.messages_dict[receiver] = OrderedDict()

        self.messages_dict[receiver][message_id] = message

        self.ui.body_gui_dict[receiver].main_layout.addLayout(message)
        message.is_displayed = True

        # Clear the dict values
        global_variables.comming_msg = dict.fromkeys(global_variables.comming_msg, "")
        return None

    def add_older_messages_on_scroll(self) -> None:
        """
        Add older messages on scroll
        """
        # To avoid multiple scroll event, fetch the first message id
        first_id = self.parent.api_controller.get_first_message_id(
            self.ui.scroll_area.name, self.ui.client.user_name
        )
        try:
            message_id_list = list(
                self.messages_dict[self.ui.scroll_area.name].values()
            )
        except KeyError:
            logging.debug("No messages to display")
            return True

        message_id_list.sort(key=lambda x: x.message_id)

        last_message_id = next(
            (message.message_id for message in message_id_list if message.is_displayed)
        )

        # If the first id is the same as the last message id,
        # it means that we have reached the end of the messages
        if first_id == last_message_id:
            return True

        self.parent.fetch_older_messages(
            last_message_id, 4, self.ui.scroll_area.name, display=True
        )
        return None

    def handle_message(self, payload: str) -> None:
        """
        Get the message and update global variables

        Args:
            payload (str): payload of the message
        """
        payload_fields = payload.split(":")

        message_id = payload_fields[0]
        sender = payload_fields[1]
        receiver = payload_fields[2]
        message = payload_fields[3]

        if len(payload_fields) == 5:
            response_id = payload_fields[4]
            global_variables.comming_msg["response_id"] = response_id

        global_variables.comming_msg["message_id"] = int(message_id)
        global_variables.comming_msg["id"] = sender
        global_variables.comming_msg["receiver"] = receiver.replace(" ", "")
        global_variables.comming_msg["message"] = message.replace("$replaced$", ":")

        self.parent.event_manager.event_coming_message()

    def get_all_dm_users_username(self) -> dict[str, list[str]]:
        """
        Get all dm users username
        """
        return self.parent.api_controller.get_all_dm_users_username(
            self.ui.client.user_name
        )

    def fetch_older_messages(
        self, start: int, number: int, username: str, display=True
    ) -> None:
        """
        Fetch older messages from the server

        Args:
            start (int): start offset
            number (int): number of messages
        """
        older_messages_list: List = self.parent.api_controller.get_older_messages(
            start, number, self.ui.client.user_name, username
        )

        self.display_older_messages(older_messages_list, display, reverse=True)

    def reply_to_message(self, message: MessageLayout) -> None:
        """
        Reply to a message

        Args:
            message_id (int): message id
        """
        # Update reply entry
        self.ui.footer_widget.reply_entry_action.triggered.emit()

        style_sheet_main = message.main_widget.styleSheet()
        style_sheet_left = message.left_widget.styleSheet()

        self.parent.update_stylesheet_with_focus_event(
            message, border_color=GenericColor.RED.value
        )

        def callback(
            message: MessageLayout,
            older_room_name: str,
            style_sheet_main_: str,
            style_sheet_left_: str,
        ):
            message.main_widget.setStyleSheet(style_sheet_main_)
            message.left_widget.setStyleSheet(style_sheet_left_)
            global_variables.reply_id = ""
            older_room_name = older_room_name.replace("\n", "")
            self.ui.footer_widget.entry.setPlaceholderText(older_room_name)
            self.ui.footer_widget.reply_entry_action.setVisible(False)

        older_room_name = f"Enter your message to {self.ui.frame_name.text()}"
        self.ui.footer_widget.entry.setPlaceholderText(
            f"Reply to {message.username_label}"
        )
        self.ui.footer_widget.entry.setFocus()
        self.ui.footer_widget.reply_entry_action.triggered.connect(
            partial(
                callback, message, older_room_name, style_sheet_main, style_sheet_left
            )
        )
        global_variables.reply_id = f"#{message.message_id}/"

        self.ui.footer_widget.reply_entry_action.setVisible(True)
