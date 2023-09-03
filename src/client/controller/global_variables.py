from typing import List, Union
from threading import Lock

cst_lock = Lock()

with cst_lock:
    comming_msg: dict[str, str] = {
        "id": "",
        "receiver": "",
        "message": "",
        "reaction": "",
    }

with cst_lock:
    user_connected: dict[str, List[Union[str, bool]]] = {}

with cst_lock:
    user_disconnect: dict[str, List[Union[str, bool]]] = {}
