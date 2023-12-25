"""Module for utils functions"""

import configparser
import logging
import os
import sys
from enum import Enum, unique
from typing import List, Tuple

from PIL import Image, ImageDraw
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap

from resources.icon.icon_path import ICON_PATH

LM_USE_SVG = 1

# set PIL.PngImagePlugin logger off
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.INFO)


@unique
class Icon(Enum):
    """
    All icons used in the application.

    Args:
        Enum (Enum): Enum class
    """

    CLEAR = f"{ICON_PATH}/clear.svg"
    LOGIN = f"{ICON_PATH}/login.svg"
    LOGOUT = f"{ICON_PATH}/logout.svg"
    SEND = f"{ICON_PATH}/send.svg"
    CONFIG = f"{ICON_PATH}/config.svg"
    STATUS = f"{ICON_PATH}/status_user_conn.svg"
    MESSAGE = f"{ICON_PATH}/message.svg"
    USER_ICON = f"{ICON_PATH}/default_user_icon.svg"
    LEFT_ARROW = f"{ICON_PATH}/left_arrow.svg"
    RIGHT_ARROW = f"{ICON_PATH}/right_arrow.svg"
    DOWN_ARROW = f"{ICON_PATH}/down_arrow.svg"
    ARROW_RIGHT = f"{ICON_PATH}/arrow_right.svg"
    AVATAR = f"{ICON_PATH}/avatar_update.svg"
    SMILEY = f"{ICON_PATH}/smiley.svg"
    ROOM = f"{ICON_PATH}/home.svg"
    SEPARATOR = f"{ICON_PATH}/separator.svg"
    SEPARATOR_HORIZ = f"{ICON_PATH}/separator_ho.svg"
    CROWN = f"{ICON_PATH}/crown.svg"
    REPLY = f"{ICON_PATH}/reply.svg"
    REPLY_ROTATED = f"{ICON_PATH}/reply_rotated.svg"
    CLOSE_USERS = f"{ICON_PATH}/close_users.svg"
    CLOSE_DM = f"{ICON_PATH}/close_dm.svg"
    LINK = f"{ICON_PATH}/link.svg"
    MESSAGE_DM = f"{ICON_PATH}/icon.svg"
    USER_CONNECTED = f"{ICON_PATH}/user_connected.svg"
    USER_DISCONNECTED = f"{ICON_PATH}/user_disconnected.svg"
    CLOSE = f"{ICON_PATH}/close.svg"
    FILE = f"{ICON_PATH}/file.svg"
    SEARCH = f"{ICON_PATH}/search.svg"
    SWITCH_COLOR = f"{ICON_PATH}/switch_color.svg"
    SAVE = f"{ICON_PATH}/save.svg"


@unique
class BlackColor(Enum):
    """
    All colors used in the application in Black theme.

    Args:
        Enum (Enum): Enum class
    """

    GREY = "#383A3F"
    MIDDLE_GREY = "#2A2C2F"
    LIGHT_GREY = "#B6BAC0"
    DARK_GREY = "#313338"
    LIGHT_BLACK = "#232328"
    WHITE = "#FFFFFF"
    BLACK = "#1C1D1F"
    YELLOW = "#F6DF91"


@unique
class WhiteColor(Enum):
    """
    All colors used in the application in White theme.

    Args:
        Enum (Enum): Enum class
    """

    WHITE = "#FFFFFF"
    BLACK = "#000000"
    LIGHT_GREY = "#e4e4e4"
    DARK_GREY = "#A6A6A7"
    GREY = "#CFCFD0"
    BLUE = "#1D87E5"


@unique
class GenericColor(Enum):
    """
    All colors used in the application.

    Args:
        Enum (Enum): Enum class
    """

    RED = "#E03232"


# pylint: disable=too-many-instance-attributes
class Themes:
    """
    Theme class

    Raises:
        NotImplementedError: Theme not found
    """

    class ThemeColor(Enum):
        """
        Theme color

        Args:
            Enum (Enum): Enum class
        """

        BLACK = 0
        WHITE = 1
        CUSTOM = 2

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./config.ini")

        self.theme_name = self.config["THEME"]["theme"]
        self.list_colors = [
            "text_color",
            "title_color",
            "inner_color",
            "background_color",
            "nav_color",
            "search_color",
            "rooms_color",
            "emoji_color",
        ]

        if self.theme_name == Themes.ThemeColor.BLACK.name:
            self.color = BlackColor.BLACK.value
            self.text_color = BlackColor.WHITE.value
            self.title_color = BlackColor.LIGHT_GREY.value
            self.inner_color = BlackColor.DARK_GREY.value
            self.background_color = BlackColor.GREY.value
            self.rgb_background_color_innactif = QColor(
                *self.hex_to_rgb(self.background_color)
            )
            self.rgb_background_color_actif = QColor(*self.hex_to_rgb(self.inner_color))
            self.nav_color = BlackColor.MIDDLE_GREY.value
            self.search_color = BlackColor.LIGHT_BLACK.value
            self.rgb_background_color_actif_footer = QColor(
                *self.hex_to_rgb(self.search_color)
            )
            self.rooms_color = BlackColor.BLACK.value
            self.rgb_background_color_rooms = QColor(*self.hex_to_rgb(self.rooms_color))
            self.emoji_color = BlackColor.YELLOW.value
        elif self.theme_name == Themes.ThemeColor.WHITE.name:
            self.color = WhiteColor.WHITE.value
            self.text_color = WhiteColor.BLACK.value
            self.title_color = WhiteColor.BLACK.value
            self.inner_color = WhiteColor.LIGHT_GREY.value
            self.background_color = WhiteColor.WHITE.value
            self.rgb_background_color_innactif = QColor(
                *self.hex_to_rgb(self.background_color)
            )
            self.rgb_background_color_actif = QColor(*self.hex_to_rgb(self.inner_color))
            self.nav_color = WhiteColor.WHITE.value
            self.search_color = WhiteColor.GREY.value
            self.rgb_background_color_actif_footer = QColor(
                *self.hex_to_rgb(self.search_color)
            )
            self.rooms_color = WhiteColor.DARK_GREY.value
            self.rgb_background_color_rooms = QColor(*self.hex_to_rgb(self.rooms_color))
            self.emoji_color = WhiteColor.BLACK.value
        elif self.theme_name == Themes.ThemeColor.CUSTOM.name:
            self.color = self.config["THEME"]["inner_color"]
            self.text_color = self.config["THEME"]["text_color"]
            self.title_color = self.config["THEME"]["title_color"]
            self.inner_color = self.config["THEME"]["inner_color"]
            self.background_color = self.config["THEME"]["background_color"]
            self.rgb_background_color_innactif = QColor(
                *self.hex_to_rgb(self.background_color)
            )
            self.rgb_background_color_actif = QColor(*self.hex_to_rgb(self.inner_color))
            self.nav_color = self.config["THEME"]["nav_color"]
            self.search_color = self.config["THEME"]["search_color"]
            self.rgb_background_color_actif_footer = QColor(
                *self.hex_to_rgb(self.search_color)
            )
            self.rooms_color = self.config["THEME"]["rooms_color"]
            self.rgb_background_color_rooms = QColor(*self.hex_to_rgb(self.rooms_color))
            self.emoji_color = self.config["THEME"]["emoji_color"]
        else:
            raise NotImplementedError("Theme not found")

    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color to rgb color

        Args:
            hex_color (str): hex color

        Returns:
            Tuple[int, int, int]: rgb color
        """
        hex_color = hex_color.lstrip("#")
        hlen = len(hex_color)
        return tuple(
            int(hex_color[i : i + hlen // 3], 16) for i in range(0, hlen, hlen // 3)
        )

    def switch_theme(self, controller, theme: ThemeColor) -> None:
        """
        Switch theme
        """
        self.config["THEME"]["theme"] = theme.name
        with open("./config.ini", "w", encoding="utf-8") as configfile:
            self.config.write(configfile)

        # Restart the app
        controller.connection_controller.logout()
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

    def create_custom_theme(self, controller, list_theme_line_edit: List) -> None:
        """
        Create custom theme

        Args:
            controller (GuiController): the controller of the GUI
            list_theme_line_edit (List[CustomQLineEdit]): list of CustomQLineEdit
        """
        for line_edit, color_name in zip(list_theme_line_edit, self.list_colors):
            color = line_edit.text()
            if not color or color[0] != "#" or len(color) != 7:
                return
            self.config["THEME"][color_name] = color

        self.switch_theme(controller, Themes.ThemeColor.CUSTOM)


@unique
class ImageAvatar(Enum):
    """
    All images used in the application.

    Args:
        Enum (Enum): Enum class
    """

    SERVER = "./resources/images/server_picture.png"
    ROOM = "./resources/images/room_picture.png"
    EN = "./resources/images/en.png"


def icon_from_svg(svg_name: str, color: str) -> QIcon:
    """
    Create QIcon from svg

    Args:
        svg_name (str): the name of the svg
        color (str): the color of the svg

    Returns:
        QIcon: the QIcon
    """
    path = ICON_PATH
    pixmap = QPixmap(os.path.join(path, svg_name))
    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    if color:
        painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return QIcon(pixmap)


def check_str_len(intput_str: str) -> str:
    """
    Check the length of the string

    Args:
        intput_str (str): the string to check

    Returns:
        str: the string checked
    """
    intput_str.capitalize()
    len_ = 15
    return f"{intput_str[:13]}.." if len(intput_str) >= len_ else intput_str


def round_image(picture_path: str) -> Image:
    """
    Round the image

    Args:
        picture_path (str): the path of the image

    Returns:
        Image: the rounded image
    """
    image = Image.open(picture_path)
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    width, height = image.size
    draw.ellipse((0, 0, width, height), fill=255)

    # Apply the mask to the image
    rounded_image = Image.new("RGBA", image.size)
    rounded_image.paste(image, mask=mask)

    return rounded_image
