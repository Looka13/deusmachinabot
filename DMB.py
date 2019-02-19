import os
import telegram
import psycopg2
import random
from telegram.ext import MessageHandler, Filters, CommandHandler
from datetime import datetime

TOKEN = os.environ.get('TOKEN')
PORT = int(os.environ.get('PORT', '8443'))
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
DATABASE_URL = os.environ.get('DATABASE_URL')

def sigterm_handler(signum, frame):
	updater.bot.send_message(chat_id=ADMIN_ID, text="SIGTERM signal received.")

updater = telegram.ext.Updater(token=TOKEN, user_sig_handler=sigterm_handler)
dispatcher = updater.dispatcher
random.seed()

try:
	conn = psycopg2.connect(DATABASE_URL, sslmode="require")
	cursor = conn.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS memory (id INT PRIMARY KEY, name TEXT NOT NULL, value TEXT)")
	conn.commit()
except:
	pass
finally:
	if (conn):
		cursor.close()
		conn.close()

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

def save(bot, update, args):
	if (len(args) > 0):
		try:
			conn = psycopg2.connect(DATABASE_URL, sslmode="require")
			cursor = conn.cursor()
			cursor.execute("SELECT EXISTS(SELECT 1 FROM memory WHERE name = %s)", ("prova",))
			result = cursor.fetchone()
			if (result[0]):
				cursor.execute("UPDATE memory SET value = %s WHERE name = %s", (str(args[0]), "prova"))
			else:
				cursor.execute("INSERT INTO memory (name, value) VALUES (%s, %s)", ("prova", str(args[0])))
			conn.commit()
			bot.send_message(chat_id=update.message.chat_id, text="Value saved.")
		except psycopg2.Error as e:
			bot.send_message(chat_id=update.message.chat_id, text="Saving was unsuccessful. {0}", e.pgerror)
		finally:
			if (conn):
				cursor.close()
				conn.close()
	else:
		bot.send_message(chat_id=update.message.chat_id, text="You need to pass an argument to this command.")

def retrieve(bot, update):
	try:
		conn = psycopg2.connect(DATABASE_URL, sslmode="require")
		cursor = conn.cursor()
		cursor.execute("SELECT EXISTS(SELECT 1 FROM memory WHERE name = %s)", ("prova",))
		result = cursor.fetchone()
		if (result[0]):
			cursor.execute("SELECT * FROM memory WHERE name = %s", ("prova",))
			result = cursor.fetchone()
			if (result[2]):
				bot.send_message(chat_id=update.message.chat_id, text="Retrieved value: {0}".format(result[2]))
			else:
				bot.send_message(chat_id=update.message.chat_id, text="Value saved but empty.")
		else:
			bot.send_message(chat_id=update.message.chat_id, text="No value saved.")
	except:
		bot.send_message(chat_id=update.message.chat_id, text="An error occured during retrieving.")
	finally:
		if (conn):
			cursor.close()
			conn.close()
	
# add handlers
msg_handler = MessageHandler(Filters.text, processText)
dispatcher.add_handler(msg_handler)
start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)
save_handler = CommandHandler("save", save, pass_args=True)
dispatcher.add_handler(save_handler)
retrieve_handler = CommandHandler("retrieve", retrieve)
dispatcher.add_handler(retrieve_handler)

updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
#updater.bot.set_webhook("https://deusmachinabot.herokuapp.com/"+TOKEN)
updater.idle()
