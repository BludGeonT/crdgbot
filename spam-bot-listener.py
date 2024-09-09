import logging
import mysql.connector
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
import config_surveyor  # Assuming config_surveyor contains your bot token
import re
from getpass import getpass

# Enable logging for verbosity
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Set the channel ID within the script
CHANNEL_ID = input("Enter the Telegram channel ID: ")

# Prompt for MySQL credentials once
db_user = input("Enter MySQL username: ")
db_password = getpass("Enter MySQL password: ")

# Function to connect to MySQL (credentials cached)
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user=db_user,
        password=db_password,
        database="blockfilters"
    )

# Function to clean up the triggered value while preserving / and *
def clean_triggered_value(triggered_value):
    # Allow only alphanumeric characters, dots, dashes, slashes, and asterisks
    cleaned_value = re.sub(r'[^a-zA-Z0-9./*-]', '', triggered_value)
    return cleaned_value

# Function to increment 'times_used' in the database and show before/after values
def increment_times_used(triggered_value):
    db = connect_to_db()
    cursor = db.cursor()

    # Fetch the current times_used value
    cursor.execute("SELECT times_used FROM filters WHERE name = %s", (triggered_value,))
    result = cursor.fetchone()

    if result:
        times_used_before = result[0]
        logger.info(f"Before increment: {triggered_value} has been triggered {times_used_before} times.")

        # Increment the times_used value
        cursor.execute("UPDATE filters SET times_used = times_used + 1 WHERE name = %s", (triggered_value,))
        db.commit()

        # Fetch the updated times_used value
        cursor.execute("SELECT times_used FROM filters WHERE name = %s", (triggered_value,))
        times_used_after = cursor.fetchone()[0]
        logger.info(f"After increment: {triggered_value} has been triggered {times_used_after} times.")
    else:
        logger.info(f"No filter found for triggered value: {triggered_value}")

    cursor.close()
    db.close()

# Function to handle incoming messages and check 'Triggered:' in channel posts
def handle_message(update: Update, context: CallbackContext):
    # Log the entire update object to understand the structure
    logger.info(f"Full update object: {update}")
    
    # Check if it's a channel post and extract the message from there
    if update.channel_post and update.channel_post.text:
        message_text = update.channel_post.text
        chat_id = update.channel_post.chat.id
        logger.info(f"Received channel post in chat {chat_id}: {message_text}")

        # Check if the message contains 'Triggered:' (case-insensitive) and if it's from the correct channel
        if chat_id == int(CHANNEL_ID):
            match = re.search(r'triggered:\s*(.+)', message_text, re.IGNORECASE)
            if match:
                triggered_value = match.group(1).strip()
                logger.info(f"Detected triggered value before cleaning: {triggered_value}")
                
                # Clean the triggered value but retain / and *
                cleaned_triggered_value = clean_triggered_value(triggered_value)
                logger.info(f"Cleaned triggered value: {cleaned_triggered_value}")
                
                # Increment the times_used field in the database
                increment_times_used(cleaned_triggered_value)
            else:
                logger.info(f"Channel post did not contain 'Triggered:'")
        else:
            logger.info(f"Ignored channel post from chat {chat_id} (not the target channel)")
    else:
        logger.info("Received a non-text message or empty message. Skipping.")

# Main function to run the bot
def main():
    # Set up the Telegram bot
    updater = Updater(token=config_surveyor.TELEGRAM_BOT_API_KEY, use_context=True)
    dispatcher = updater.dispatcher

    logger.info(f"Connecting to Telegram channel ID: {CHANNEL_ID}")
    
    # Add handler for all messages and channel posts
    dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command, handle_message))

    # Start polling for messages
    updater.start_polling()
    logger.info("Bot started and listening for messages...")
    
    updater.idle()

if __name__ == '__main__':
    main()