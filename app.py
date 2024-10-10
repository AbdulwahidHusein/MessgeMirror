import os
from dotenv import load_dotenv
from typing import Optional, Dict

from fastapi import FastAPI, HTTPException
import logging
from telegram import Bot
from telegram.error import TelegramError
from command_handler import SessionManager
import call_back_queries
from model import TelegramWebhook
from forwarder import Forwarder

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGO_URL = os.getenv('MONGO_URL')

bot = Bot(BOT_TOKEN)

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility function to check if it's a group message
def is_group_message(webhook_data: TelegramWebhook) -> bool:
    return webhook_data.message and webhook_data.message.get('chat') and \
           webhook_data.message['chat'].get('type') in ["group", "supergroup"]

# Utility function to check if it's a private message
def is_private_message(webhook_data: TelegramWebhook) -> bool:
    return webhook_data.message and webhook_data.message['chat'].get('type') == "private"

async def handle_error(e: Exception, context: str) -> None:
    logger.error(f"Error in {context}: {e}")
    raise HTTPException(status_code=500, detail="An internal error occurred")

# Webhook endpoint for handling incoming Telegram messages
@app.post("/webhook")
async def webhook(webhook_data: TelegramWebhook) -> Dict[str, str]:
    try:
        # Handle group messages
        if is_group_message(webhook_data):
            forwarder = Forwarder(bot, webhook_data)
            await forwarder.forward()
        
        # Handle private messages
        elif is_private_message(webhook_data):
            session_manager = SessionManager(bot, webhook_data)
            await session_manager.handle_message()
        
        # Handle callback queries
        elif webhook_data.callback_query:
            await call_back_queries.handle_callback_query(bot, webhook_data)

        # Return a success response to Telegram
        return {"message": "ok"}
    
    except TelegramError as te:
        await handle_error(te, "Telegram API")
    
    except Exception as e:
        await handle_error(e, "Webhook processing")

# Health check endpoint
@app.get("/")
def index() -> Dict[str, str]:
    return {"message": "Hello World"}

