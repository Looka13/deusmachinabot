import os
import telegram
import random
from telegram.ext import MessageHandler, Filters, CommandHandler
from datetime import datetime

TOKEN = os.environ.get('TOKEN')
PORT = int(os.environ.get('PORT', '8443'))
updater = telegram.ext.Updater(TOKEN)
dispatcher = updater.dispatcher
random.seed()

def processText(bot, update):
	s = random.randint(0, 3)
	if s == 0:
		text = "Ho ricevuto il tuo messaggio, ma al momento non so che farmene."
	elif s == 1:
		text = "Ho già un fidanzato."
	elif s == 2:
		now = datetime.now()
		t = now.strftime("%H:%M:%S")
		text = "Sono le " + t + "."
	else:
		text = "Hai perso."
	if "perso" in update.message.text.lower():
		text = "Ho perso di nuovo..."
	bot.send_message(chat_id=update.message.chat_id, text=text)

def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="The bot is not working yet!")

# add handlers
msg_handler = MessageHandler(Filters.text, processText)
dispatcher.add_handler(msg_handler)
start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)

updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
updater.bot.set_webhook("https://deusmachinabot.herokuapp.com/"+TOKEN)
updater.idle()
