import time
from src.tools.bot import Bot
from typing import List
import argparse


def parser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-nb", "--bot_number", help="Number of bot to connect", default=4, type=int
    )
    return argparser.parse_args()

if __name__ == "__main__":
    parser_ = parser()
    BOT_NUMBER: int = parser_.bot_number
    
    BOT_PASSWORD = "bot"
    
    bot_name_list = [
        "Passoah",
        "Greez",
        "Toutape",
        "Teazs",
        "MaxTheBird",
        "Yahnae",
        "Savounet",
        "Neuve",
        "Skwat",
        "Arkivana"
    ]
    bot_list: List[Bot] = []
    
    for i in range(BOT_NUMBER):
        bot_name = bot_name_list[i]
        bot = Bot(
            bot_name, 
            BOT_PASSWORD
        )
        bot_list.append(bot)
        bot.connect()
        time.sleep(1)
    
    while "Script is running":
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            for bot in bot_list:
                bot.disconnect()
                time.sleep(1)
            break
    