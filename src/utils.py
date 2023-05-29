from enum import Enum, unique
import logging
from PIL import Image, ImageTk, PngImagePlugin
from cairosvg import svg2png
import re

LM_USE_SVG = 1
ICON_PATH = "../resources/"

@unique
class Icon(Enum):
   CLEAR = f"{ICON_PATH}clear.svg"
   LOGIN = f"{ICON_PATH}login.svg"
   LOGOUT = f"{ICON_PATH}logout.svg"
   SEND = f"{ICON_PATH}send.svg"
   CONFIG = f"{ICON_PATH}config.svg"
   STATUS = f"{ICON_PATH}status.svg"
   
@unique 
class Color(Enum):
   GREY = "#313338"
   LIGHT_GREY = "#B6BAC0"
   WHITE = "#FFFFFF"
   BLUE = "#4986F7"
   
def image_from_svg(filename = "", size = 0):
   # open svg
   if LM_USE_SVG == 1:
      if size == 0:
         # unscaled
         svg2png(url=filename, write_to="/tmp/example_temp_image.png")
      else:
         svg2png(url=filename, write_to="/tmp/example_temp_image.png", parent_width = size,parent_height = size)
      photo = Image.open("/tmp/example_temp_image.png")
   else:
      photo = Image.new("RGBA",[size,size])
   return photo

def empty_photoimage(size=40):
   photo = Image.new("RGBA",[size,size])
   return ImageTk.PhotoImage(image=photo)

def get_scaled_icon(iconfilename, size = 20):
   try:
      # try an svg
      if re.compile(".*\.svg").match(iconfilename):
         photo = image_from_svg(filename=iconfilename, size=size)
      else:
         photo = Image.open(iconfilename)
   except Exception as f:
      logging.error("Error with icon file:", f)
      return empty_photoimage()

   if size != 0 and (type(photo) is Image or type(photo) is PngImagePlugin.PngImageFile):
      photo.thumbnail(size=[size, size])

   if not type(photo) is ImageTk.PhotoImage:
      try:
         photo = ImageTk.PhotoImage(photo)
      except Exception as error:
         logging.error(f"Error: {error}")
   return photo