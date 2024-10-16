from fastapi import APIRouter, HTTPException
from telegram import Bot
from telegram.error import TelegramError

from models import TelegramWebhook
from typing import Dict

from utils.helpers import is_group_message, is_private_message, handle_error
from mirror_bot.forwarding.forwarder import Forwarder
from mirror_bot.management.command_handler import SessionManager
from mirror_bot.management.call_back_queries import CallbackQueryHandler

from mirror_bot.db.admindb import is_admin
from config import Config

router = APIRouter()

bot = Bot(Config.MIRROR_BOT_TOKEN)
# bot.set_webhook(url=Config.WEB_HOOK_URL)

@router.post("/mirror-bot")
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
                if is_admin(username):
                    session_manager = SessionManager(bot, webhook_data)
                    await session_manager.handle_message()
        
        # Handle callback queries
        elif webhook_data.callback_query: 
            callback_handler = CallbackQueryHandler(bot)
            await callback_handler.handle(webhook_data)
 

        # Return a success response to Telegram
        return {"message": "ok"}
    
    except TelegramError as te:
        await handle_error(te, "Telegram API")
    
    except Exception as e:
        await handle_error(e, "Webhook processing") 
    
    return {"message": "ok"}