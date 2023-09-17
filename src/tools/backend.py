from typing import Optional, Union
import requests
from src.client.core.qt_core import QFileDialog, QMainWindow
from src.tools.commands import Commands


class Backend:
    def __init__(self, ip: str, port: str, parent: Union[QMainWindow, None] = None):
        self.parent = parent  # TODO: To remove from here
        self.ip = ip
        self.port = port

    def send_login_form(self, username: str, password: str) -> bool:
        endpoint = f"http://{self.ip}:{self.port}/user/"
        response = requests.get(
            url=f"{endpoint}{username}?password={password}",
        )
        is_connected: bool = False
        if response.status_code == 200 and response.content:
            is_connected: bool = response.json()["is_connected"]

        return response.status_code, is_connected

    def send_login_status(self, username: str, status: bool) -> bool:
        endpoint = (
            f"http://{self.ip}:{self.port}/user/{username}/?is_connected={status}"
        )
        response = requests.patch(url=endpoint)

        return response.status_code == 200

    def send_register_form(self, username: str, password: str) -> bool:
        endpoint = f"http://{self.ip}:{self.port}/register"
        data = {"username": username, "password": password}
        header = {"Accept": "application/json"}
        response = requests.post(url=endpoint, headers=header, json=data)
        return response.status_code == 200

    def send_user_icon(self, username: str, picture_path: str = None) -> bool:
        path = picture_path or QFileDialog.getOpenFileName(
            self.parent
        )  # TODO: To remove from here
        if not path[0]:
            return
        endpoint = f"http://{self.ip}:{self.port}/user/{username}"

        files = {"file": open(path[0], "rb")}
        response = requests.put(url=endpoint, files=files)
        return response.status_code == 200

    def get_user_icon(self, username: str) -> Union[bool, bytes]:
        endpoint = f"http://{self.ip}:{self.port}/user/"
        response = requests.get(
            url=f"{endpoint}{username}/picture",
        )
        if response.status_code == 200 and response.content:
            return response.content
        else:
            return False

    def get_all_users_username(self) -> Union[bool, bytes]:
        endpoint = f"http://{self.ip}:{self.port}/users"
        response = requests.get(
            url=f"{endpoint}/username",
        )
        if response.status_code == 200 and response.content:
            return response.json()
        else:
            return False

    def get_older_messages(self):
        endpoint = f"http://{self.ip}:{self.port}/messages/"
        response = requests.get(
            url=endpoint,
        )
        if response.status_code == 200 and response.content:
            return response.json()
        else:
            return False

    def send_message(
        self,
        username: str,
        receiver: str,
        message: str,
        response_id: Optional[int] = None,
    ):
        endpoint = f"http://{self.ip}:{self.port}/messages/"
        data = {
            "sender": username,
            "receiver": receiver,
            "message": message,
            "response_id": response_id,
        }
        header = {"Accept": "application/json"}
        response = requests.post(url=endpoint, headers=header, json=data)
        return response.status_code

    def update_reaction_nb(self, message_id: int, reaction_nb: int):
        endpoint = f"http://{self.ip}:{self.port}/messages/{message_id}/reaction/?new_reaction_nb={reaction_nb}"
        response = requests.patch(url=endpoint)
        return response.status_code

    def update_is_readed_status(
        self, sender: str, receiver: str, is_readed: Optional[bool] = True
    ):
        endpoint = f"http://{self.ip}:{self.port}/messages/readed/?sender={sender}&receiver={receiver}&is_readed={is_readed}"
        response = requests.patch(url=endpoint)
        return response.status_code
