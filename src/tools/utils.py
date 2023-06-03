import logging
import os
import re
from enum import Enum, unique

from cairosvg import svg2png
from PIL import Image, ImageTk, PngImagePlugin

from resources.icon.icon_path import ICON_PATH
from src.client.qt_core import QColor, QIcon, QPainter, QPixmap

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
    STATUS = f"{ICON_PATH}/status.svg"
    MESSAGE = f"{ICON_PATH}/message.svg"


@unique
class Color(Enum):
    GREY = "#313338"
    LIGHT_GREY = "#B6BAC0"
    WHITE = "#FFFFFF"
    BLUE = "#4986F7"


def image_from_svg(filename="", size=0):
    # open svg
    if LM_USE_SVG == 1:
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
        photo = Image.open("/tmp/example_temp_image.png")
    else:
        photo = Image.new("RGBA", [size, size])
    return photo


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

    if not type(photo) is ImageTk.PhotoImage:
        try:
            photo = ImageTk.PhotoImage(photo)
        except Exception as error:
            logging.error(f"Error: {error}")
    return photo


def QIcon_from_svg(svg_name, color=Color.BLUE.value):
    path = ICON_PATH
    pixmap = QPixmap(os.path.join(path, svg_name))
    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    if color:
        painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return QIcon(pixmap)
