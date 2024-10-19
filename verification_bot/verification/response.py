import asyncio

from telegram import Bot
from models import TelegramWebhook
from ..database import membership_dao
from .verification_processor import handle_verification, response_types
from .verification_processor.parse_request import contains_settlement_request
from verification_bot.database import (
    whitelist_dao,
    settlement_request_dao,
    group_pairs_dao,
)


class VerificationBot:
    def __init__(self, bot: Bot, webhook_data: TelegramWebhook):
        self.bot = bot
        self.webhook_data = webhook_data   
        self.update_message = webhook_data.message
        self.from_id = self.update_message['from']['id']
        
    async def initialize(self):
        """Initialize group data asynchronously."""
        chat_info = self.update_message['chat']
        
        # Update group title if applicable
        if "new_chat_title" in self.update_message:
            await group_pairs_dao.update_group_title(
                group_id=chat_info['id'], 
                new_title=self.update_message["new_chat_title"]
            )
        
        # Create membership entry
        membership_dao.create_member_ship(group_info=chat_info)

    async def handle_verification(self):
        """Handle verification requests based on messages."""
        await self.initialize()  # Ensure initialization is completed
        
        group_message_text = self.update_message.get("text")
        group_chat_id = self.update_message['chat']['id']
        group_message_id = self.update_message['message_id']

        if contains_settlement_request(group_message_text):
            await self._process_settlement_request(group_chat_id, group_message_id)

    async def _process_settlement_request(self, group_chat_id, group_message_id):
        """Process the settlement request and send responses."""
        source_group_data = group_pairs_dao.get_source_group_data(group_chat_id)

        if source_group_data:
            source_identifier = self._get_source_identifier(source_group_data)

            response = await handle_verification.handle(
                self.update_message, 
                source_identifier, 
                source_group_data['title']
            )

            if response and response.status:
                await self._send_response_message(group_chat_id, response.status, group_message_id)
                await self._log_settlement_request(response, source_group_data, group_chat_id, group_message_id)

    def _get_source_identifier(self, source_group_data):
        """Get the identifier for the source group."""
        return (
            source_group_data.get('username') or 
            int(source_group_data['id'])
        )

    async def _send_response_message(self, chat_id, text, reply_to_message_id):
        """Send a message with retry logic."""
        await send_message_with_retry(self.bot, chat_id, text, reply_to_message_id)

    async def _log_settlement_request(self, response, source_group_data, group_chat_id, group_message_id):
        """Log the settlement request details."""
        report = {
            "groupa_id": source_group_data['id'],
            "groupb_id": group_chat_id,
            "groupb_message_id": group_message_id,
            "status": response.status,
            'issuer_id' : self.from_id
        }
        
        if response.matching_message:
            report["groupa_message_id"] = response.matching_message.id

        if response.matching_index is not None and response.status == response_types.VERIFIED:
            report["index_on_groupa"] = response.matching_index

        if response.similar_messages:
            report['groupa_similar_message_ids'] = [m.id for m in response.similar_messages]
            

        await settlement_request_dao.create_settlement_request_report(**report)


async def send_message_with_retry(bot: Bot, chat_id, text, reply_to_message_id, retries=3, delay=2):
    """Send a message with retries in case of failure."""
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
