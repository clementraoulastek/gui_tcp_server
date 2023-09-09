from enum import Enum, unique


@unique
class Commands(Enum):
    MESSAGE = 0x0000
    HELLO_WORLD = 0x0001
    WELCOME = 0x0002
    GOOD_BYE = 0x0003
    CONN_NB = 0x0004
    ADD_REACT = 0x0005
    RM_REACT = 0x0006
    LAST_ID = 0x0007
