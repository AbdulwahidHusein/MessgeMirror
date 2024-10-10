import os
from dotenv import load_dotenv
from typing import Dict

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

import logging
from telegram import Bot
from telegram.error import TelegramError
from command_handler import SessionManager
import call_back_queries
from model import TelegramWebhook
from forwarder import Forwarder

from db.admindb import add_username_to_admin_list, is_admin

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGO_URL = os.getenv('MONGO_URL')
OWNER_TELEGRAM_ID = os.getenv('OWNER_TELEGRAM_ID')

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
            user = webhook_data.message['from']
            
            if 'username' in user:
                username = user['username']
                if is_admin(username) or username == "cl168888_pg" or username == "AbdulwahidHussen":
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
    


@app.get("/add-admin", response_class=HTMLResponse)
async def add_admin_form():
    with open("add_admin_form.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Step 2: Handle the form submission
@app.post("/add-admin")
async def handle_admin_form(bot_token: str = Form(...), username: str = Form(...)) -> Dict[str, str]:
    if bot_token == BOT_TOKEN:
        messsage = add_username_to_admin_list(username)
        return {"message": messsage}
    
    return {"message": "Invalid bot token."}