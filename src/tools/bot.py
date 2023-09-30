from threading import Thread
import time
from src.client.client import Client
from src.tools.commands import Commands
from src.tools.backend import Backend
from src.tools.constant import IP_API, PORT_API, IP_SERVER, PORT_SERVER


class Bot:
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        
        self.client = Client(IP_SERVER, PORT_SERVER, "Default")
        self.backend = Backend(IP_API, PORT_API, self)
        
    def connect(self) -> None:
        status_code, is_connected = self.backend.send_login_form(self.username, self.password)

        # Check if the login is successful and if the user is not already connected
        if status_code != 200 or is_connected:
            raise Exception("Error while connecting to the server")
        
        self.client.user_name = self.username

        # Update login status to connected
        if self.backend.send_login_status(username=self.username, status=True):
            self.is_connected = True
        else:
            raise Exception("Error while connecting to the server")

        self.client.init_connection()
        self.client.send_data(Commands.HELLO_WORLD, Commands.HELLO_WORLD.name)
        
        routing_thread = Thread(target=self.__callback_routing_messages_on_ui, daemon=False)
        routing_thread.start()
        
    def disconnect(self) -> None:
        self.backend.send_login_status(username=self.username, status=False)
        self.client.close_connection()
        
    def send_message(self, message: str) -> None:
        self.client.send_data(Commands.MESSAGE, message)
        
    def __callback_routing_messages_on_ui(self) -> None:
        """
        Read messages comming from server
        """
        WAITING_TIME = 0.01
        
        while self.client.is_connected:
            header, payload = self.client.read_data()
            if payload:
                self.__routing_coming_messages(header, payload)
            else:
                break
            time.sleep(WAITING_TIME)
            
    def __routing_coming_messages(self, header: int, payload: str) -> None:
        """
        Update global variables with input messages

        Args:
            header (int): header of the message
            payload (str): payload of the message
        """
        if ":" in payload:
            if header == Commands.CONN_NB.value:
                pass
            elif header == Commands.HELLO_WORLD.value:
                self.client.send_data(Commands.WELCOME, Commands.WELCOME.name)
            elif header == Commands.WELCOME.value:
                pass
            elif header == Commands.GOOD_BYE.value:
                pass
            elif header in [Commands.ADD_REACT.value, Commands.RM_REACT.value]:
                pass
            else:
                pass
        elif header == Commands.LAST_ID.value:
            pass


        