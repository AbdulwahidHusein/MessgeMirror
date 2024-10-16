import requests
import os
from dotenv import load_dotenv
from models import TelegramWebhook
import logging


load_dotenv()
BOT_TOKEN = os.getenv('MIRROR_BOT_TOKEN')
logger = logging.getLogger(__name__)

def normalize_username(username: str) -> str:
    """Normalize the username to always start with @ and handle URLs."""
    if not username:
        return None

    # Handle full URL starting with https:// or http://
    if username.startswith(('https://t.me/', 'http://t.me/')):
        username = username.split('/')[-1]

    # Ensure the username starts with an @ symbol
    if not username.startswith('@'):
        username = '@' + username
    
    return username

def get_group_info_by_username(username: str):
    """Fetch group info from Telegram API by username, handling various formats."""
    username = normalize_username(username)
    if not username:
        logger.warning("Username is None after normalization.")
        return None

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={username}"
    response = requests.get(url)

    if response.status_code == 200:
        group_data = response.json()
        return group_data
    else:
        logger.error(f"Failed to get group info: {response.status_code}, Response: {response.text}")
        return None

# Utility function to check if it's a group message
def is_group_message(webhook_data: TelegramWebhook) -> bool:
    if webhook_data is None:
        logger.warning("Webhook data is None.")
        return False

    message = webhook_data.message
    if message and message.get('chat'):
        return message['chat'].get('type') in ["group", "supergroup"]
    
    logger.warning("Webhook data does not contain valid message or chat info.")
    return False

# Utility function to check if it's a private message
def is_private_message(webhook_data: TelegramWebhook) -> bool:
    if webhook_data is None:
        logger.warning("Webhook data is None.")
        return False

    message = webhook_data.message
    if message and message.get('chat'):
        return message['chat'].get('type') == "private"
    
    return False

async def handle_error(e: Exception, context: str) -> None:
    logger.error(f"Error in {context}: {e}")
