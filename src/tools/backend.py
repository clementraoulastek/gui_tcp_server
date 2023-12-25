"""Module for the backend controller."""

import logging
import os
from typing import Optional, Union

import requests

from src.client.core.qt_core import QFileDialog, QMainWindow
from src.tools.utils import round_image


class Backend:
    """
    Backend class.
    """

    def __init__(self, ip: str, port: str, parent: Union[QMainWindow, None] = None):
        self.parent = parent
        self.ip = ip
        self.port = port

    def send_login_form(self, username: str, password: str) -> bool:
        """
        Send the login form to the server

        Args:
            username (str): username
            password (str): password

        Returns:
            bool: True if the form has been sent
        """
        endpoint = f"http://{self.ip}:{self.port}/user/"
        response = requests.get(
            url=f"{endpoint}{username}?password={password}", timeout=10
        )
        is_connected: bool = False
        if response.status_code == 200 and response.content:
            is_connected: bool = response.json()["is_connected"]

        return response.status_code, is_connected

    def send_login_status(self, username: str, status: bool) -> bool:
        """
        Send the login status to the server

        Args:
            username (str): username
            status (bool): status

        Returns:
            bool: True if the status has been sent
        """
        endpoint = (
            f"http://{self.ip}:{self.port}/user/{username}/?is_connected={status}"
        )
        response = requests.patch(url=endpoint, timeout=10)

        return response.status_code == 200

    def send_register_form(self, username: str, password: str) -> bool:
        """
        Send the register form to the server

        Args:
            username (str): username
            password (str): password

        Returns:
            bool: True if the form has been sent
        """
        endpoint = f"http://{self.ip}:{self.port}/register"
        data = {
            "username": username,
            "password": password,
        }
        header = {"Accept": "application/json"}
        response = requests.post(url=endpoint, headers=header, json=data, timeout=10)
        
        return response.status_code, False

    def send_user_icon(self, username: str, picture_path: str = None) -> bool:
        """
        Send the user icon to the server

        Args:
            username (str): username
            picture_path (str, optional): the picture path. Defaults to None.

        Returns:
            bool: True if the icon has been sent
        """
        path = picture_path or QFileDialog.getOpenFileName(
            self.parent,
        )
        if not path[0]:
            return None
        rounded_image = round_image(path[0])
        temp_image_path = "./resources/images/temp_rounded_image.png"
        rounded_image.save(temp_image_path, "PNG")

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
        """
        Get the user icon

        Args:
            username (str): username

        Returns:
            Union[bool, bytes]: the icon
        """
        endpoint = f"http://{self.ip}:{self.port}/user/"
        response = requests.get(url=f"{endpoint}{username}/picture", timeout=10)
        if response.status_code == 200 and response.content:
            return response.content
        return False

    def get_all_users_username(self) -> Union[bool, bytes]:
        """
        Get all the users

        Returns:
            Union[bool, bytes]: the users
        """
        endpoint = f"http://{self.ip}:{self.port}/users"
        response = requests.get(url=f"{endpoint}/username", timeout=10)
        if response.status_code == 200 and response.content:
            return response.json()
        return False

    def get_all_dm_users_username(self, username: str) -> Union[bool, bytes]:
        """
        Get all the users that have a dm with the user

        Args:
            username (str): username

        Returns:
            Union[bool, bytes]: the users
        """
        endpoint = f"http://{self.ip}:{self.port}/dm"
        response = requests.get(url=f"{endpoint}?username={username}", timeout=10)
        if response.status_code == 200 and response.content:
            return response.json()
        return False

    def get_last_message_id(self) -> int:
        """
        Get the last message id

        Returns:
            int: the last message id
        """
        endpoint = f"http://{self.ip}:{self.port}/last_id"
        response = requests.get(url=endpoint, timeout=10)
        if response.status_code == 200 and response.content:
            return response.json()["last_id"]
        return False

    def get_first_message_id(self, user1: str, user2: str) -> int:
        """
        Get the first message id between two users

        Args:
            user1 (str): User 1
            user2 (str): User 2

        Returns:
            int: the first message id
        """
        endpoint = (
            f"http://{self.ip}:{self.port}/first_id" + f"?user1={user1}&user2={user2}"
        )
        response = requests.get(url=endpoint, timeout=10)
        if response.status_code == 200 and response.content:
            return response.json()["first_id"]
        return False

    def get_older_messages(
        self, start: int, number: int, user1: str, user2: str
    ) -> dict:
        """
        Get older messages

        Args:
            start (int): start message id
            number (int): number of messages
            user1 (str): User 1
            user2 (str): User 2

        Returns:
            dict: the messages
        """
        endpoint = (
            f"http://{self.ip}:{self.port}/messages/"
            + f"?message_id={start}&number={number}&user1={user1}&user2={user2}"
        )
        response = requests.get(url=endpoint, timeout=10)
        if response.status_code == 200 and response.content:
            return response.json()
        return False

    def get_older_message(self, message_id: int) -> Union[bool, dict]:
        """
        Get the older message

        Args:
            message_id (int): message id

        Returns:
            Union[bool, dict]: the message
        """
        endpoint = f"http://{self.ip}:{self.port}/messages/{message_id}"
        response = requests.get(url=endpoint, timeout=10)
        if response.status_code == 200 and response.content:
            return response.json()
        return False

    def send_message(
        self,
        username: str,
        receiver: str,
        message: str,
        response_id: Optional[int] = None,
    ) -> Union[None, dict]:
        """
        Send a message to the server

        Args:
            username (str): the username of the sender
            receiver (str): the username of the receiver
            message (str): the message
            response_id (Optional[int], optional): the response id. Defaults to None.

        Returns:
            Union[None, dict]: the response of the server
        """
        endpoint = f"http://{self.ip}:{self.port}/messages/"
        data = {
            "sender": username,
            "receiver": receiver,
            "message": message,
            "response_id": response_id,
        }
        header = {"Accept": "application/json"}
        response = requests.post(url=endpoint, headers=header, json=data, timeout=10)

        return response.json() if response.status_code == 200 else None

    def update_reaction_nb(self, message_id: int, reaction_nb: int) -> int:
        """
        Update the number of reaction of a message

        Args:
            message_id (int): message id
            reaction_nb (int): new number of reaction

        Returns:
            int: status code
        """
        # pylint: disable=line-too-long
        endpoint = f"http://{self.ip}:{self.port}/messages/{message_id}/reaction/?new_reaction_nb={reaction_nb}"
        response = requests.patch(url=endpoint, timeout=10)
        return response.status_code

    def update_is_readed_status(
        self, sender: str, receiver: str, is_readed: Optional[bool] = True
    ) -> int:
        """
        Update the is_readed status of a message

        Args:
            sender (str): sender username
            receiver (str): receiver username
            is_readed (Optional[bool], optional): If is readed. Defaults to True.

        Returns:
            int: status code
        """
        # pylint: disable=line-too-long
        endpoint = f"http://{self.ip}:{self.port}/messages/readed/?sender={sender}&receiver={receiver}&is_readed={is_readed}"
        response = requests.patch(url=endpoint, timeout=10)
        return response.status_code

    def get_user_creation_date(self, username: str) -> Union[bool, str]:
        """
        Get the creation date of a user

        Args:
            username (str): username

        Returns:
            Union[bool, str]: creation date
        """
        endpoint = f"http://{self.ip}:{self.port}/user/{username}/creation-date"
        response = requests.get(url=endpoint, timeout=10)
        if response.status_code == 200 and response.content:
            response = response.json()
            return response["register_date"], response["description"]
        return False

    def update_user_description(self, username: str, description: str) -> bool:
        """
        Update the user description

        Args:
            username (str): username
            description (str): new description

        Returns:
            bool: True if the description has been updated
        """
        endpoint = f"http://{self.ip}:{self.port}/user/{username}/description"
        endpoint += f"?description={description}"
        response = requests.patch(url=endpoint, timeout=10)
        return response.status_code == 200
