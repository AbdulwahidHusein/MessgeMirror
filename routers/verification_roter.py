from fastapi import APIRouter, HTTPException
from telegram import Bot
from telegram.error import TelegramError

from models import TelegramWebhook
from typing import Dict

from utils.helpers import is_group_message, is_private_message, handle_error

from verification_bot.management.bot import ManagementBot
from verification_bot.management.callback_queries import CallbackQueryHandler
from verification_bot.database.admin_dao import is_admin

from config import Config

from verification_bot.verification.response import VerificationBot

router = APIRouter()

bot = Bot(Config.VERIFICATION_BOT_TOKEN)

@router.post("/verification-bot")
async def webhook(webhook_data: TelegramWebhook) -> Dict[str, str]:

    try:
        # Handle group messages
        if is_group_message(webhook_data):
            verifier = VerificationBot(bot, webhook_data)
            if webhook_data.message.get("text"):
                await verifier.handle_verification()
        
        # Handle private messages
        elif is_private_message(webhook_data):
            user = webhook_data.message['from']
            if 'username' in user:
                username = user['username']
                if is_admin(username):
                    vbot = ManagementBot(bot, webhook_data) 
                    await vbot.handle_message()  
            
            # Handle callback queries
        elif webhook_data.callback_query:
            callback_handler = CallbackQueryHandler(bot)
            
            await callback_handler.handle(webhook_data)
            # callback_handler = CallbackQueryHandler(bot)
            # await callback_handler.handle(webhook_data)
 

        # Return a success response to Telegram
        return {"message": "ok"}
    
    except TelegramError as te:
        await handle_error(te, "Telegram API")
    
    except Exception as e:
        await handle_error(e, "Webhook processing") 
    
    return {"message": "ok"}