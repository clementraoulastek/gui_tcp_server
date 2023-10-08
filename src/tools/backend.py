import logging
import os
from typing import Optional, Union
import requests
from src.client.core.qt_core import QFileDialog, QMainWindow
from src.tools.commands import Commands
from src.tools.utils import round_image

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
        data = {   
                "username": username, 
                "password": password,
            }
        header = {"Accept": "application/json"}
        response = requests.post(url=endpoint, headers=header, json=data)
        return response.status_code == 200

    def send_user_icon(self, username: str, picture_path: str = None) -> bool:
        path = picture_path or QFileDialog.getOpenFileName(
            self.parent,
        )  # TODO: To remove from here
        if not path[0]:
            return
        rounded_image = round_image(path[0])
        temp_image_path = './resources/images/temp_rounded_image.png'
        rounded_image.save(temp_image_path, 'PNG')
        
        endpoint = f"http://{self.ip}:{self.port}/user/{username}"
        
        with open(temp_image_path, "rb") as file:
            files = {"file": file}
            response = requests.put(url=endpoint, files=files)
            
        try:
            os.remove(temp_image_path)
        except OSError:
            logging.error("Error while deleting file temp_rounded_image.png")
        
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
    
    def get_all_dm_users_username(self, username) -> Union[bool, bytes]:
        endpoint = f"http://{self.ip}:{self.port}/dm"
        response = requests.get(
            url=f"{endpoint}?username={username}",
        )
        if response.status_code == 200 and response.content:
            return response.json()
        else:
            return False
        
    def get_last_message_id(self) -> int:
        endpoint = f"http://{self.ip}:{self.port}/last_id"
        response = requests.get(
            url=endpoint,
        )
        if response.status_code == 200 and response.content:
            return response.json()["last_id"]
        else:
            return False
        
    def get_first_message_id(self, user1: str, user2: str) -> int:
        endpoint = f"http://{self.ip}:{self.port}/first_id" + f"?user1={user1}&user2={user2}"
        response = requests.get(
            url=endpoint,
        )
        if response.status_code == 200 and response.content:
            return response.json()["first_id"]
        else:
            return False


    def get_older_messages(self, start: int, number: int, user1: str, user2: str) -> dict:
        endpoint = f"http://{self.ip}:{self.port}/messages/" + f"?message_id={start}&number={number}&user1={user1}&user2={user2}"
        response = requests.get(
            url=endpoint,
        )
        if response.status_code == 200 and response.content:
            return response.json()
        else:
            return False
        
    def get_older_message(self, message_id: int):
        endpoint = f"http://{self.ip}:{self.port}/messages/{message_id}"
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
        
        if response.status_code == 200:
            return response.json()
        

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

    def get_user_creation_date(self, username: str) -> Union[bool, bytes]:
        endpoint = f"http://{self.ip}:{self.port}/user/{username}/creation-date"
        response = requests.get(
            url=endpoint,
        )
        if response.status_code == 200 and response.content:
            response = response.json()
            return response["register_date"], response["description"]
        else:
            return False
        
    def update_user_description(self, username: str, description: str) -> bool:
        endpoint = f"http://{self.ip}:{self.port}/user/{username}/description"
        endpoint += f"?description={description}"
        response = requests.patch(url=endpoint)
        return response.status_code == 200