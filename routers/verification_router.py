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


if Config.VERIFICATION_ENABLED:
    router = APIRouter()
    bot_app = ( 
        ApplicationBuilder()
        .token(Config.VERIFICATION_BOT_TOKEN)
        .write_timeout(40) 
        .read_timeout(20)   
        .connection_pool_size(100) 
        .build() 
    )

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
                #     print(username)
                #     if is_admin(username):
                #         vbot = ManagementBot(bot, webhook_data) 
                #         await vbot.handle_message()  
                
                # Handle callback queries
            # elif webhook_data.callback_query:
            #     callback_handler = CallbackQueryHandler(bot)
                
            #     await callback_handler.handle(webhook_data)
            #     # callback_handler = CallbackQueryHandler(bot)
            #     # await callback_handler.handle(webhook_data)
    

            # Return a success response to Telegram
            return {"message": "ok"}
        
        except TelegramError as te:
            await handle_error(te, "Telegram API")
        
        except Exception as e:
            await handle_error(e, "Webhook processing") 
        
        return {"message": "ok"}