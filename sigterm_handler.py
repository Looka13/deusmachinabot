from telegram import bot

def sigterm_handler(signum, frame):
	bot.send_message(chat_id="@Looka13", text="SIGTERM signal received.")