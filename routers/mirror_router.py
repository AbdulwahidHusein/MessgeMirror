from fastapi import APIRouter, Request
from telegram import Bot
from telegram.error import TelegramError

from models import TelegramWebhook
from typing import Dict

from utils.helpers import is_group_message, is_private_message, handle_error, services_enabled
from mirror_bot.forwarding.forwarder import Forwarder
from mirror_bot.management.handlers import register_handlers


from mirror_bot.db.admindb import is_admin
from mirror_bot.db.database import get_service_state
from config import Config
from telegram import Update
from telegram.ext import (ApplicationBuilder)



router = APIRouter()


 

bot_app = ( 
    ApplicationBuilder()
    .token(Config.MIRROR_BOT_TOKEN)
    .write_timeout(40) 
    .read_timeout(20)   
    .connection_pool_size(100) 
    .build() 
)





@router.post("/mirror-bot")
async def webhook(request: Request) -> Dict[str, str]:
    raw_data = await request.json()
    try:
        webhook_data = TelegramWebhook(**raw_data)
    except Exception as e:
        return {"error": str(e)}
    
    try:
        
        # Handle group messages
        if is_group_message(webhook_data) and services_enabled("MIRRORING_STATUS"):
            if get_service_state("MIRRORING_STATUS"):
                bot = Bot(Config.MIRROR_BOT_TOKEN)
                forwarder = Forwarder(bot, webhook_data)
                await forwarder.forward()
        
        # Handle private messages
        elif is_private_message(webhook_data) or webhook_data.callback_query:
            update_data = await request.json()
            update = Update.de_json(update_data, bot_app.bot)
            register_handlers.register(bot_app)
            await bot_app.initialize()
            await bot_app.process_update(update)

            # user = webhook_data.message['from'] 
            
            # if 'username' in user:
            #     username = user['username']
            #     if is_admin(username) or True:
            #         session_manager = SessionManager(bot, webhook_data)
            #         await session_manager.handle_message()
        

        return {"message": "ok"} 
     
    except TelegramError as te:
        await handle_error(te, "Telegram API")
    
    except Exception as e:
        await handle_error(e, "Webhook processing") 
     
    return {"message": "ok"}   