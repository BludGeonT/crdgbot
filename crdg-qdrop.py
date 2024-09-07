import logging
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
import config  # Import your config file for credentials
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to capture screenshot of the entire webpage
def capture_full_page_screenshot(url, save_path):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service("/usr/local/bin/chromedriver")  # Path to chromedriver

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    
    # Set window size to capture the entire page
    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(1920, total_height)
    
    driver.save_screenshot(save_path)
    driver.quit()

# Function to handle incoming messages
def handle_message(update: Update, context: CallbackContext):
    message_text = update.message.text
    username = update.message.from_user.username
    print(f"{datetime.now().strftime('%H:%M:%S')} From User: {username} - Received '{message_text}'")

    if message_text.startswith('qdrop'):
        try:
            query = message_text.split(' ', 1)[1]
            if query.startswith('#'):
                number = int(query[1:])
                if 1 <= number <= 4966:
                    url = f"https://qalerts.pub/?n={number}"
                else:
                    update.message.reply_text("Error: Number out of range. Please enter a number between 1 and 4966.")
                    return
            elif ':' in query:  # Handles time format
                url = f"https://qalerts.pub/?q={quote_plus(query)}"
            else:
                url = f"https://qalerts.pub/?q={quote_plus(query)}"

            screenshot_path = f"screenshot_{username}_{int(time.time())}.png"
            capture_full_page_screenshot(url, screenshot_path)
            context.bot.send_photo(chat_id=update.message.chat_id, photo=open(screenshot_path, 'rb'))
        except IndexError:
            update.message.reply_text("Invalid format. Use 'qdrop <query>' or 'qdrop #<number>'")
    else:
        update.message.reply_text("Unknown command. Please use 'qdrop' followed by your query or number.")

# Function to send a heartbeat message to the console every X minutes
def heartbeat(interval):
    while True:
        print(f"{datetime.now().strftime('%H:%M:%S')} - Heartbeat: Bot is running.")
        time.sleep(interval * 60)

def main():
    # Use the API key and channel ID from config.py
    updater = Updater(token=config.TELEGRAM_BOT_API_KEY, use_context=True)
    dispatcher = updater.dispatcher

    print(f"{datetime.now().strftime('%H:%M:%S')} Connecting to Telegram group {config.CHANNEL_ID} with bot token.")
    
    # Add a handler to process messages
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the heartbeat in a separate thread (adjust interval as needed)
    import threading
    heartbeat_thread = threading.Thread(target=heartbeat, args=(10,), daemon=True)
    heartbeat_thread.start()

    # Start polling Telegram for updates
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()