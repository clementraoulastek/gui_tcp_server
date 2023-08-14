import logging
import os
import re
from enum import Enum, unique

from cairosvg import svg2png
from PIL import Image, ImageTk, PngImagePlugin

from resources.icon.icon_path import ICON_PATH
from src.client.core.qt_core import (
    QColor,
    QIcon,
    QPainter,
    QPixmap,
)

LM_USE_SVG = 1

# set PIL.PngImagePlugin logger off
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.INFO)


@unique
class Icon(Enum):
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
    AVATAR = f"{ICON_PATH}/avatar_update.svg"
    SMILEY = f"{ICON_PATH}/smiley.svg"


@unique
class Color(Enum):
    GREY = "#383A3F"
    MIDDLE_GREY = "#2A2C2F"
    LIGHT_GREY = "#B6BAC0"
    DARK_GREY = "#313338"
    WHITE = "#FFFFFF"
    BLUE = "#4986F7"
    RED = "#811919"
    GREEN = "#305C0A"
    BLACK = "#171717"


@unique
class ImageAvatar(Enum):
    SERVER = "./resources/images/server_picture.png"


def image_from_svg(filename="", size=0):
    if LM_USE_SVG != 1:
        return Image.new("RGBA", [size, size])
    if size == 0:
        # unscaled
        svg2png(url=filename, write_to="/tmp/example_temp_image.png")
    else:
        svg2png(
            url=filename,
            write_to="/tmp/example_temp_image.png",
            parent_width=size,
            parent_height=size,
        )
    return Image.open("/tmp/example_temp_image.png")


def empty_photoimage(size=40):
    photo = Image.new("RGBA", [size, size])
    return ImageTk.PhotoImage(image=photo)


def get_scaled_icon(iconfilename, size=20):
    try:
        # try an svg
        if re.compile(".*\.svg").match(iconfilename):
            photo = image_from_svg(filename=iconfilename, size=size)
        else:
            photo = Image.open(iconfilename)
    except Exception as f:
        logging.error("Error with icon file:", f)
        return empty_photoimage()

    if size != 0 and (
        type(photo) is Image or type(photo) is PngImagePlugin.PngImageFile
    ):
        photo.thumbnail(size=[size, size])

    if type(photo) is not ImageTk.PhotoImage:
        try:
            photo = ImageTk.PhotoImage(photo)
        except Exception as error:
            logging.error(f"Error: {error}")
    return photo


def QIcon_from_svg(svg_name, color=Color.WHITE.value):
    path = ICON_PATH
    pixmap = QPixmap(os.path.join(path, svg_name))
    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    if color:
        painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return QIcon(pixmap)

def check_str_len(intput_str: str) -> str:
    intput_str.capitalize()
    LEN = 10
    return f"{intput_str[:6]}..." if len(intput_str) >= LEN else intput_str