from typing import Union
import requests
from src.client.core.qt_core import QFileDialog, QMainWindow


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
        return response.status_code == 200

    def send_register_form(self, username: str, password: str) -> bool:
        endpoint = f"http://{self.ip}:{self.port}/register"
        data = {"username": username, "password": password, "picture": ""}
        header = {"Accept": "application/json"}
        response = requests.post(url=endpoint, headers=header, json=data)
        return response.status_code == 200

    def send_user_icon(self, username: str, picture_path: str = None) -> bool:
        path = picture_path or QFileDialog.getOpenFileName(
            self.parent
        )  # TODO: To remove from here
        if not path:
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

    def get_older_messages(self):
        endpoint = f"http://{self.ip}:{self.port}/messages/"
        response = requests.get(
            url=endpoint,
        )
        if response.status_code == 200 and response.content:
            return response.json()
        else:
            return False

    def send_message(self, username: str, message: str):
        endpoint = f"http://{self.ip}:{self.port}/messages/"
        data = {"sender": username, "message": message}
        header = {"Accept": "application/json"}
        response = requests.post(url=endpoint, headers=header, json=data)
        return response.status_code
