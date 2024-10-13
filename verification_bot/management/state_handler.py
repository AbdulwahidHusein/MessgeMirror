
from typing import Any
from telegram import Bot
from models import TelegramWebhook
from ..database import session_management_dao
from .states import WAITING_FOR_SOURCE_GROUP, WAITING_FOR_DEST_GROUP, WAITING_FOR_WHITELIST, WAITING_FOR_WHITELIST_CHECK    
class StateHandler:
    def __init__(self, bot: Bot, webhook_data: TelegramWebhook):
        self.bot = bot
        self.webhook_data = webhook_data
        self.update_message = webhook_data.message
        self.from_id = self.update_message['from']['id']
        self.user_session = session_management_dao.get_sessions_by_user_id(self.from_id)

    async def handle_messages(self):
        session_name = self.user_session["session_name"]
        previous_data = self.user_session.get("previous_data")

        if session_name == WAITING_FOR_SOURCE_GROUP:
            await self.handle_source_group()
            
        elif session_name == WAITING_FOR_DEST_GROUP:
            await self.handle_dest_group(previous_data)
            
        elif session_name == WAITING_FOR_WHITELIST:
            await self.handle_whitelist_user()
            
        elif session_name == WAITING_FOR_WHITELIST_CHECK:
            await self.handle_whitelist_check()
        else:
            await self.bot.send_message(chat_id=self.from_id, text="Invalid request. Please use the provided buttons to interact with the bot.")
