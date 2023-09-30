from typing import List, Tuple, Union

comming_msg: dict[str, str] = {
    "id": "",
    "receiver": "",
    "message": "",
    "reaction": "",
    "response_id": "",
}

user_connected: dict[str, List[Tuple[bytes, bool]]] = {}

user_disconnect: dict[str, List[Tuple[bytes, bool]]]  = {}

reply_id: str = ""
