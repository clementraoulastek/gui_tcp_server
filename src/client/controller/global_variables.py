from typing import List, Union

comming_msg: dict[str, str] = {
    "id": "",
    "receiver": "",
    "message": "",
    "reaction": "",
}

user_connected: dict[str, List[Union[str, bool]]] = {}

user_disconnect: dict[str, List[Union[str, bool]]] = {}
