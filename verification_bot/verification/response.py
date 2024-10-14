from telegram import Bot
from models import TelegramWebhook
import threading
from ..database import membership_dao, group_pairs_dao
from .verification_processor.handle_verification import handle

class VerificationBot:
    def __init__(self, bot: Bot, webhook_data: TelegramWebhook):
        self.bot = bot
        self.webhook_data = webhook_data
        self.update_message = webhook_data.message
        self.from_id = self.update_message['from']['id']
        
        threading.Thread(target=membership_dao.create_member_ship, kwargs={'group_info': self.update_message['chat']}).start()
        
    
    async def handle_verification(self):
        print("handling .............")
        print(self.update_message)
        group_id = self.update_message['chat']['id']
        user_id = self.update_message['from']['id']
        

        source_group_data = group_pairs_dao.get_source_group_data(group_id)        
        
        # if source_group_data:
        response = handle(self.update_message, source_group_data)
        
        if response:
            await self.bot.send_message(
                chat_id=group_id,
                text=response, 
                reply_to_message_id=self.update_message['message_id']
            )