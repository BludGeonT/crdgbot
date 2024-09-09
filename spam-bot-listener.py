import logging
import mysql.connector
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
import config_surveyor  # Assuming config contains your bot token
import re

# Enable logging for verbosity
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Set the channel ID within the script
CHANNEL_ID = input("Enter the Telegram channel ID: ")

# Function to connect to MySQL
def connect_to_db():
    db_user = input("Enter MySQL username: ")
    db_password = getpass("Enter MySQL password: ")
    return mysql.connector.connect(
        host="localhost",
        user=db_user,
        password=db_password,
        database="blockfilters"
    )

# Function to increment 'times_used' in the database
def increment_times_used(triggered_value):
    db = connect_to_db()
    cursor = db.cursor()

    # Update the times_used value for the matching name
    cursor.execute("UPDATE filters SET times_used = times_used + 1 WHERE name = %s", (triggered_value,))
    if cursor.rowcount == 0:
        logger.info(f"No filter found for triggered value: {triggered_value}")
    else:
        logger.info(f"Incremented times_used for {triggered_value}")

    db.commit()
    cursor.close()
    db.close()

# Function to handle incoming messages and look for 'triggered:'
def handle_message(update: Update, context: CallbackContext):
    message_text = update.message.text
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    logger.info(f"Received message from {username} in chat {chat_id}: {message_text}")

    # Check if the message contains 'triggered:' and if it's from the correct channel
    if chat_id == int(CHANNEL_ID):
        match = re.search(r'triggered:\s*(.+)', message_text, re.IGNORECASE)
        if match:
            triggered_value = match.group(1).strip()
            logger.info(f"Detected triggered value: {triggered_value}")
            
            # Increment the times_used field in the database
            increment_times_used(triggered_value)
    else:
        logger.info(f"Ignored message from chat {chat_id} (not the target channel)")

# Main function to run the bot
def main():
    # Set up the Telegram bot
    updater = Updater(token=config.TELEGRAM_BOT_API_KEY, use_context=True)
    dispatcher = updater.dispatcher

    logger.info(f"Connecting to Telegram channel ID: {CHANNEL_ID}")
    
    # Add handler for text messages
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start polling for messages
    updater.start_polling()
    logger.info("Bot started and listening for messages...")
    
    updater.idle()

if __name__ == '__main__':
    main()