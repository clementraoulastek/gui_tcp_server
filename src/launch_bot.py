import json
import time
import random
from src.tools.bot import Bot
from typing import List
import argparse
import lorem

bot_name_list = [
    "Admin12",
    "Admin13",
    "Admin14",
    "Admin15",
    "Admin16",
    "Admin17",
    "Admin18",
]

receiver_list = [
    "home",
    "Admin"
]
    
def parser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-nb", "--bot_number", help="Number of bot to connect", default=len(bot_name_list), type=int
    )
    return argparser.parse_args()

if __name__ == "__main__":
    parser_ = parser()
    BOT_NUMBER: int = parser_.bot_number
    BOT_PASSWORD = "admin"
    
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
            # Random Bot
            random_index = random.randint(0, BOT_NUMBER - 1)
            bot = bot_list[random_index]
            
            # Random Receiver
            random_index = random.randint(0, len(receiver_list) - 1)
            receiver = receiver_list[random_index]
            
            bot.send_message(
                lorem.paragraph(),
                receiver=receiver
                )
            
            time.sleep(1)      
        except KeyboardInterrupt:
            for bot in bot_list:
                bot.disconnect()
                time.sleep(1)
            break
    