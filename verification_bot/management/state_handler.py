
from typing import Any
from telegram import Bot
from models import TelegramWebhook
from ..database import session_management_dao, group_pairs_dao, whitelist_dao
from .states import WAITING_FOR_SOURCE_GROUP, WAITING_FOR_DEST_GROUP, WAITING_FOR_WHITELIST, WAITING_FOR_WHITELIST_CHECK  
from utils.helpers import get_group_info_by_username, normalize_username

  
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

    async def handle_source_group(self):
        """Handle the logic when waiting for the first group's username."""
        group_username = self.update_message['text']
        group_info = get_group_info_by_username(group_username)

        if not group_info or not group_info.get("ok"):
            await self.bot.send_message(chat_id=self.from_id, text="Invalid username. Please try again. If the error persists, please contact the bot admin.")
            return

        if group_pairs_dao.has_group_pair(group_info['result']["id"]):
            await self.bot.send_message(chat_id=self.from_id, text="Group pair already exists. Please choose another group.")
            return

        # Store first group data in session
        first_group_data = {
            "id": group_info['result']["id"],
            "title": group_info['result']["title"],
            "username": group_info['result']["username"]
        }
        session_management_dao.update_session(self.from_id, WAITING_FOR_DEST_GROUP, first_group_data)
        await self.bot.send_message(chat_id=self.from_id, text="First group saved successfully! Now, please send me the username of the destination group you'd like to pair.")
        

    async def handle_dest_group(self, previous_data: Any):
        """Handle the logic when waiting for the second group's username."""
        if not previous_data:
            await self.bot.send_message(chat_id=self.from_id, text="Invalid request. Please use the provided buttons to interact with the bot.")
            return

        group_username = self.update_message['text']
        group_info = get_group_info_by_username(group_username)

        if not group_info or not group_info.get("ok"):
            await self.bot.send_message(chat_id=self.from_id, text="Invalid username. Please try again. If the error persists, please contact the bot admin.")
            return

        if group_pairs_dao.has_group_pair(group_info['result']["id"]):
            await self.bot.send_message(chat_id=self.from_id, text="Group pair already exists. Please choose another group.")
            return

        second_group_data = {
            "id": group_info['result']["id"],
            "title": group_info['result']["title"],
            "username": group_info['result']["username"]
        }
        
        success = group_pairs_dao.create_group_pair(previous_data, second_group_data)
        if success:
            await self.bot.send_message(chat_id=self.from_id, text="Group pair created successfully!")
            session_management_dao.update_session(self.from_id, WAITING_FOR_WHITELIST, second_group_data)
        else:
            await self.bot.send_message(chat_id=self.from_id, text="Failed to create group pair. Please try again.")
            

    async def handle_whitelist_user(self):
        """Handle the logic when waiting to blacklist a user."""
        message = self.update_message
        if "forward_origin" in message and message['forward_origin']:
            await self._process_forwarded_user()
        elif "text" in message and message['text']:
            await self.process_whitelist_by_username()
            
            
    async def _process_forwarded_user(self):
        """Process the forwarded user details for white listing."""
        forward_origin = self.update_message["forward_origin"]
        sender_user = forward_origin.get("sender_user")

        if not sender_user:
            await self.bot.send_message(chat_id=self.from_id, text="The forwarded user has a private profile, and their information cannot be accessed. Please send their username directly.")
            return

        user_id = sender_user["id"]
        if whitelist_dao.is_whitelisted(user_id):
            await self.bot.send_message(chat_id=self.from_id, text="This user is already whitelisted.")
            return

        success = whitelist_dao.add_to_whitelist(sender_user)
        if not success:
            await self.bot.send_message(chat_id=self.from_id, text="Failed to add user to whitelist. Please try again.")
            return

        await self.bot.send_message(chat_id=self.from_id, text="User has been successfully whitelisted.")
        session_management_dao.update_session(self.from_id, None, None)
    
    async def process_whitelist_by_username(self):
        """user username for whitelisting."""
        username = self.update_message['text']
        if username.strip() == "":
            await self.bot.send_message(chat_id=self.from_id, text="invalid username.")
        normilized_username = normalize_username(username)[1:]
        if whitelist_dao.is_whitelisted(normilized_username):
            await self.bot.send_message(chat_id=self.from_id, text="This user is already in the whitelist.")
            return
        success = whitelist_dao.add_to_whitelist_by_username(normilized_username)
        if not success:
            await self.bot.send_message(chat_id=self.from_id, text="An error occurred. Please try again later.")
            return

        await self.bot.send_message(chat_id=self.from_id, text="User has been successfully whitelisted.")
        session_management_dao.update_session(self.from_id, None, None)
        
    async def handle_whitelist_check(self):
        """Handle the logic when waiting to check if a user is whitelisted."""
        message = self.update_message
        
        username = None
        userid = None
        if "forward_origin" in message and message['forward_origin']:
            
            if 'sender_user' in message['forward_origin']:
                userid = message['forward_origin']['sender_user']['id']
            if 'username' in message['forward_origin']:
                username = message['forward_origin']['username']
        elif "text" in message and message['text']:
            username = message['text']

        if username:
            username_whitelisted = whitelist_dao.is_whitelisted('@' + username)
            if username_whitelisted:
                await self.bot.send_message(chat_id=self.from_id, text="This user is whitelisted.")
                session_management_dao.update_session(self.from_id, None, None)
                return
        if userid:
            userid_whitelisted = whitelist_dao.is_whitelisted(userid)
            if userid_whitelisted:
                await self.bot.send_message(chat_id=self.from_id, text="This user is whitelisted.")
                session_management_dao.update_session(self.from_id, None, None)
                return
        await self.bot.send_message(chat_id=self.from_id, text="This user is not whitelisted.")
        session_management_dao.update_session(self.from_id, None, None)