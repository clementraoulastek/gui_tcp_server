from typing import Union
import requests
from src.client.core.qt_core import QFileDialog, QMainWindow

class Backend:
    def __init__(self, parent: QMainWindow, ip: str, port: str):
        self.parent = parent
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
        data = {
            "username": username,
            "password": password,
        }
        header = {"Accept": "application/json"}
        response = requests.post(url=endpoint, headers=header, json=data)
        return response.status_code == 200
            
    def send_user_icon(self, username: str) -> bool:
        path = QFileDialog.getOpenFileName(self.parent)
        if not path:
            return
        endpoint = f"http://{self.ip}:{self.port}/user/{username}"

        files = {'file': open(path[0], 'rb')}
        response = requests.put(
            url=endpoint,
            files=files
        )
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
