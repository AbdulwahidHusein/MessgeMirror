from fastapi import APIRouter, Request
from telegram import Bot, Update
from telegram.error import TelegramError
from models import TelegramWebhook
from typing import Dict
from utils.helpers import is_group_message, is_private_message, handle_error
from verification_bot.database.admin_dao import is_admin
from config import Config
from verification_bot.verification.response import VerificationBot
from telegram.ext import ApplicationBuilder
from verification_bot.management.handlers import register_handlers

router = APIRouter()

# Initialize bot application once
bot_app = ( 
    ApplicationBuilder()
    .token(Config.VERIFICATION_BOT_TOKEN)
    .write_timeout(40) 
    .read_timeout(20)   
    .connection_pool_size(100) 
    .build() 
)

# Register handlers once at startup
register_handlers.register(bot_app)

@router.post("/verification-bot")
async def webhook(request: Request) -> Dict[str, str]:
    raw_data = await request.json()
    try:
        webhook_data = TelegramWebhook(**raw_data)
    except Exception as e:
        return {"error": str(e)}
    
    try:
        # Handle group messages
        if is_group_message(webhook_data):
            bot = Bot(Config.VERIFICATION_BOT_TOKEN)
            verifier = VerificationBot(bot, webhook_data)
            if webhook_data.message.get("text"):
                await verifier.handle_verification()
        
        # Handle private messages and callbacks
        elif is_private_message(webhook_data) or webhook_data.callback_query:
            update = Update.de_json(raw_data, bot_app.bot)
            await bot_app.process_update(update)

        return {"message": "ok"}
    
    except TelegramError as te:
        await handle_error(te, "Telegram API")
    except Exception as e:
        await handle_error(e, "Webhook processing") 
    
    return {"message": "ok"}