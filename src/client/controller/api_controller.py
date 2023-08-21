from typing import Optional
from src.client.view.customWidget.CustomQLabel import AvatarStatus
from src.tools.commands import Commands
import src.client.controller.global_variables as global_variables


class ApiController:
    def __init__(self, ui) -> None:
        self.ui = ui

    def send_login_form(self) -> bool:
        """
        Backend request for login form
        """
        username = self.ui.login_form.username_entry.text().replace(" ", "")
        password = self.ui.login_form.password_entry.text().replace(" ", "")
        if not username or not password:
            return False

        if self.ui.backend.send_login_form(username, password):
            self.ui.client.user_name = username
            return True

    def send_register_form(self) -> bool:
        """
        Backend request for register form
        """
        username = self.ui.login_form.username_entry.text().replace(" ", "")
        password = self.ui.login_form.password_entry.text().replace(" ", "")
        if not username or not password:
            return False

        if self.ui.backend.send_register_form(username, password):
            self.ui.client.user_name = username
            return True

    def send_emot_react(self, cmd: Commands, messageId: int, react_nb: int) -> None:
        """
        Send emot message to the server
        """
        self.ui.client.send_data(cmd, ";".join([str(messageId), str(react_nb)]))

    def get_user_icon(
        self,
        username: Optional[bool] = None,
        update_personal_avatar: Optional[bool] = False,
    ) -> None:
        """
        Backend request for getting user icon
        """
        if not username:
            username = self.ui.client.user_name
        if content := self.ui.backend.get_user_icon(username):
            self.ui.users_pict[username] = content
            if update_personal_avatar:
                self.ui.user_picture.update_picture(status=AvatarStatus.ACTIVATED, content=content)
            if (
                username in self.ui.users_connected.keys()
                and self.ui.users_connected[username] == True
            ):
                global_variables.user_connected[username] = [content, False]
            else:
                self.ui.users_connected["username"] = False
                global_variables.user_disconnect[username] = [content, False]
        else:
            self.ui.users_pict[username] = ""

    def get_older_messages(self) -> dict:
        older_messages: dict = self.ui.backend.get_older_messages()
        return older_messages["messages"]

    def add_sender_picture(self, sender_id: str) -> None:
        """Add sender picture to the list of sender pictures

        Args:
            sender_id (str): sender identifier
        """
        if sender_id not in list(self.ui.users_pict.keys()):
            self.get_user_icon(sender_id)
