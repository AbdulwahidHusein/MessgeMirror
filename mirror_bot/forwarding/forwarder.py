from models import TelegramWebhook
from mirror_bot.db.database import has_group_pair, create_message_pair, get_forwarded_id, create_member_ship, is_whitelisted
from telegram import Bot
from telegram.error import TelegramError

class Forwarder:
    def __init__(self, bot: Bot, webhook_data: TelegramWebhook):
        self.bot = bot
        self.webhook_data = webhook_data
        self.message = webhook_data.message
        self.target_group_id = None
        self.status = None
        
        try:
            create_member_ship(self.message['chat']) 
            self.is_whitelisted = False 
            
            if is_whitelisted(int(self.message['from']['id'])):
                self.is_whitelisted = True
            if not self.is_whitelisted:
                if 'username' in self.message['from']:
                    self.is_whitelisted = is_whitelisted(self.message['from']['username'])
        except Exception as e:
            print(f"Error during initialization: {e}")

    def get_pair_group(self):
        try:
            return get_target_group_id(self.message['chat']['id'])
        except Exception as e:
            print(f"Error getting pair group: {e}")
            return None

    async def forward(self): 
        if not self.is_whitelisted:
            return 
        try:
            self.target_group_id = self.get_pair_group()
            if not self.target_group_id:
                print("No match found")
                return 
            await self.handle_message_forward()

            if self.status:
                create_message_pair(
                    from_group_id=self.message['chat']['id'],
                    to_group_id=self.target_group_id,
                    original_id=self.message['message_id'],
                    forwarded_id=self.status.message_id
                )
        except TelegramError as e:
            print(f"Telegram error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    async def handle_message_forward(self):
        reply_to_message = self.message.get('reply_to_message')
        if reply_to_message:
            corresponding_message_id = self.get_corresponding_message_id(reply_to_message)
            if corresponding_message_id:
                self.status = await self.bot.send_message(
                    chat_id=self.target_group_id, 
                    text=self.message['text'], 
                    reply_to_message_id=corresponding_message_id
                )
            else:
                await self.forward_as_reply_with_preview(reply_to_message)
        else:
            self.status = await self.bot.copy_message(self.target_group_id, self.message['chat']['id'], self.message['message_id'])

    def get_corresponding_message_id(self, reply_to_message):
        from_group_id = self.message['chat']['id']
        to_group_id = self.target_group_id

        corresponding_message_id = get_forwarded_id(
            from_group_id=from_group_id, 
            to_group_id=to_group_id, 
            original_id=reply_to_message['message_id']
        )
        if not corresponding_message_id:
            corresponding_message_id = get_forwarded_id(
                from_group_id=to_group_id, 
                to_group_id=from_group_id, 
                forwarded_id=reply_to_message['message_id']
            )
        return corresponding_message_id

    async def forward_as_reply_with_preview(self, reply_to_message):
        try:
            original_message_preview = reply_to_message.get('text', '')[:100]
            reply_message = (
                f"*🔄 {reply_to_message['from']['first_name']}*:\n"
                f"{original_message_preview}...\n\n"
            )
            self.status = await self.bot.send_message(
                chat_id=self.target_group_id,
                text=reply_message,
                parse_mode='Markdown'
            )
            self.status = await self.bot.copy_message(self.target_group_id, self.message['chat']['id'], self.message['message_id'], caption=reply_message)
        except Exception as e:
            print(f"Error forwarding as reply with preview: {e}")

def get_target_group_id(chat_id):
    try:
        return has_group_pair(chat_id)
    except Exception as e:
        print(f"Error getting target group ID: {e}")
        return None