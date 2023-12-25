"""Module for global variables used in the client."""

from typing import List, Tuple

comming_msg: dict[str, str] = {
    "id": "",
    "receiver": "",
    "message": "",
    "reaction": "",
    "response_id": "",
    "message_id": "",
}

user_connected: dict[str, List[Tuple[bytes, bool]]] = {}

user_disconnect: dict[str, List[Tuple[bytes, bool]]] = {}

reply_id: str = ""
