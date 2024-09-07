#!/usr/bin/env python3

from datetime import datetime

from telegram import Bot

with open("/home/bludgeont/TelegramBots/crdg_bot/crdg_bot.apikey", "r") as crdgBotToken:
    crdgBot = crdgBotToken.read().rstrip()
    print("CRDG Bot Initialized...")

# Variables
bot = Bot(token=crdgBot)

# Get the current date and time at the top of the hour every hour

# Current date and time
CurrDate = datetime.now().strftime('IT IS %m%d%Y-%H%M PDT')

#print("Twin is typing...")
print("The Time Is: ", CurrDate)

bot.send_message(chat_id="-1002185873551", text=CurrDate)
bot.send_message(chat_id="-1001486900270", text=CurrDate)

#bot.send_message(chat_id="-1001486900270", text="/ban 7300260465 08252024|SPAM|url shortener")

#bot.send_message(chat_id="-1001486900270", text="##### IT IS 16:00 PDT #####")
