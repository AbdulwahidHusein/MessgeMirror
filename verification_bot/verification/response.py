from telegram import Bot
from models import TelegramWebhook
import threading
from ..database import membership_dao, group_pairs_dao
from .verification_processor import handle_verification
from .verification_processor.parse_request import contains_settlement_request
from verification_bot.database import whitelist_dao, settlement_request_dao
import asyncio


class VerificationBot:
    def __init__(self, bot: Bot, webhook_data: TelegramWebhook):
        self.bot = bot
        self.webhook_data = webhook_data
        self.update_message = webhook_data.message
        self.from_id = self.update_message['from']['id']
        
        
        threading.Thread(target=membership_dao.create_member_ship, kwargs={'group_info': self.update_message['chat']}).start()
    
    async def handle_verification(self):
        groupb_message = self.update_message['text']
        
        groupb_chat_id = self.update_message['chat']['id']
        groupb_message_id = self.update_message['message_id']
        
    
        
        is_settlment_request = contains_settlement_request(groupb_message)
        
        if is_settlment_request:
            source_group_data = group_pairs_dao.get_source_group_data(groupb_chat_id)        
            # print(source_group_data)
            if source_group_data:
                match_found, index, similar_messages, matching_message_object = await  handle_verification.handle(self.update_message, source_group_data['username'])
                
                if match_found:
                    
                    if settlement_request_dao.get_report_by_groupa(matching_message_object.chat_id, matching_message_object.id, index):
                        await self.bot.send_message(
                            chat_id=groupb_chat_id,
                            text="already verified",
                            reply_to_message_id = groupb_message_id
                        )
                        return
                    
                    is_sender_verified = False
                    
                    if matching_message_object.sender.id:
                        is_sender_verified = whitelist_dao.is_whitelisted(matching_message_object.sender.id)
                    if not is_sender_verified:
                        if  matching_message_object.sender.username:
                            is_sender_verified = whitelist_dao.is_whitelisted(matching_message_object.sender.username)
                    
                    
                    if not is_sender_verified:
                        report = {
                            "groupa_id": source_group_data['id'],
                            "groupb_id": groupb_chat_id,
                            "groupb_message_id": groupb_message_id,
                            "status": "Not Verified",
                            "index_on_groupa": index,
                        }
                        if matching_message_object:
                            report["groupb_message_id"] = matching_message_object.id
                            
                        
                        send_message_with_retry(
                            self.bot,
                            groupb_chat_id,
                            "Not Verified ❌",
                            reply_to_message_id=groupb_message_id
                        )
                        settlement_request_dao.create_settlement_request_report(**report)
 
                    elif is_sender_verified:
                        report  = {
                            "groupa_id": source_group_data['id'],
                            "groupb_id": groupb_chat_id,
                            "groupb_message_id": groupb_message_id,
                            "groupa_message_id": matching_message_object.id,
                            "status": "Verified",
                            "index_on_groupa": index,
                        }
                        
                        await send_message_with_retry(
                            self.bot,
                            chat_id=groupb_chat_id,
                            text="Verified ✅", 
                            reply_to_message_id=groupb_message_id
                        )
                        settlement_request_dao.create_settlement_request_report(**report)
                
                else:
                    report = {
                        "groupa_id": source_group_data['id'],
                        "groupb_id": groupb_chat_id,
                        "groupb_message_id": groupb_message_id,
                        "status": "Not Confirmed",
                        "index_on_groupa": index,
                        "groupa_similar_message_ids": [message.id for message in similar_messages],
                    }
                    
                    await send_message_with_retry(
                        self.bot,
                        groupb_chat_id,
                        "Not Confirmed ❌", 
                        groupb_message_id
                    )

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