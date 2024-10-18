from telegram import Bot
from models import TelegramWebhook
import threading
from ..database import membership_dao, group_pairs_dao
from .verification_processor import handle_verification, response_types
from .verification_processor.parse_request import contains_settlement_request
from verification_bot.database import whitelist_dao, settlement_request_dao, group_pairs_dao
import asyncio


class VerificationBot:
    def __init__(self, bot: Bot, webhook_data: TelegramWebhook):
        self.bot = bot
        self.webhook_data = webhook_data
        self.update_message = webhook_data.message
        self.from_id = self.update_message['from']['id']
        
        if "new_chat_title" in self.update_message:
            threading.Thread(target = group_pairs_dao.update_group_title, kwargs={'group_id': self.update_message['chat']['id'], 'new_title': self.update_message["new_chat_title"]}).start()
    
        threading.Thread(target = membership_dao.create_member_ship, kwargs={'group_info': self.update_message['chat']}).start()
    
    async def handle_verification(self):
        groupb_message = self.update_message.get("text")

        groupb_chat_id = self.update_message['chat']['id']
        groupb_message_id = self.update_message['message_id']
    
        is_settlment_request = contains_settlement_request(groupb_message) 
        
        if is_settlment_request:
            source_group_data = group_pairs_dao.get_source_group_data(groupb_chat_id)        
            if source_group_data:
                response = await  handle_verification.handle(self.update_message, source_group_data['username'], source_group_data['title'])
                                
                if response and response.status:
                    
                    await send_message_with_retry(self.bot, groupb_chat_id, response.status, groupb_message_id)
                    
                    if response.status and response.status:
                        report = {
                            "groupa_id": source_group_data['id'],
                            "groupb_id": groupb_chat_id,
                            "groupb_message_id": groupb_message_id,
                            "status": response.status,
                        }
                        if  response.matching_message:
                            report["groupa_message_id"] = response.matching_message.id
                            
                        if response.matching_index and response.status == response_types.VERIFIED:
                            report["index_on_groupa"] = response.matching_index
                        
                        if response.similar_messages:
                            report['groupa_similar_message_ids'] = [m.id for m in response.similar_messages]
                        settlement_request_dao.create_settlement_request_report(**report)
                        
                    
async def send_message_with_retry(bot : Bot, chat_id, text, reply_to_message_id, retries=3, delay=2):
    for attempt in range(retries):
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=reply_to_message_id
            )
            return
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(delay)  
            else:
                raise e  