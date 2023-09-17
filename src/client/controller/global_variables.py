from typing import List, Union
from threading import Lock

user_disconnect_lock = Lock()
user_connected_lock = Lock()


comming_msg: dict[str, str] = {
    "id": "",
    "receiver": "",
    "message": "",
    "reaction": "",
    "response_id": "",
}

user_connected: dict[str, List[Union[str, bool]]] = {}

user_disconnect: dict[str, List[Union[str, bool]]] = {}

reply_id: str = ""
