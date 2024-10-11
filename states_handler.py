from states import WAITING_FOR_FIRST_GROUP, WAITING_FOR_SECOND_GROUP, WAITING_FOR_BLACKLIST_USER, WAITING_DELETE_OLD_MESSAGES_NUM_OF_DAYS
from db.database import get_sessions_by_user_id, update_session, has_group_pair, create_group_pair, is_blacklisted, create_blacklist_entry
from utils import get_group_info_by_username
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from model import TelegramWebhook
from typing import Optional
from utils import normalize_username


class CommonMessageHandler:
    def __init__(self, bot: Bot, webhook_data: TelegramWebhook):
        self.bot = bot
        self.webhook_data = webhook_data
        self.update_message = webhook_data.message
        self.from_id = self.update_message['from']['id']
        self.user_session = get_sessions_by_user_id(self.from_id)

    async def handle_messages(self):
        session_name = self.user_session["session_name"]
        previous_data = self.user_session.get("previous_data")

        if session_name == WAITING_FOR_FIRST_GROUP:
            await self.handle_first_group()
        elif session_name == WAITING_FOR_SECOND_GROUP:
            await self.handle_second_group(previous_data)
        elif session_name == WAITING_FOR_BLACKLIST_USER:
            await self.handle_blacklist_user()
            
        elif session_name == WAITING_DELETE_OLD_MESSAGES_NUM_OF_DAYS:
            await self.handle_delete_old_messages()
        else:
            await self.bot.send_message(chat_id=self.from_id, text="Invalid request. Please use the provided buttons to interact with the bot.")

    async def handle_first_group(self):
        """Handle the logic when waiting for the first group's username."""
        group_username = self.update_message['text']
        group_info = get_group_info_by_username(group_username)

        if not group_info or not group_info.get("ok"):
            await self._send_invalid_username_message()
            return

        if has_group_pair(group_info['result']["id"]):
            await self._send_group_pair_exists_message()
            return

        # Store first group data in session
        first_group_data = {
            "id": group_info['result']["id"],
            "title": group_info['result']["title"],
            "username": group_info['result']["username"]
        }
        update_session(self.from_id, WAITING_FOR_SECOND_GROUP, first_group_data)
        await self.bot.send_message(chat_id=self.from_id, text="First group saved successfully! Now, please send me the username of the second group you'd like to pair.")

    async def handle_second_group(self, previous_data: Optional[dict]):
        """Handle the logic when waiting for the second group's username."""
        if not previous_data:
            await self._send_generic_error_message()
            return

        group_username = self.update_message['text']
        group_info = get_group_info_by_username(group_username)

        if not group_info or not group_info.get("ok"):
            await self._send_invalid_username_message()
            return

        if has_group_pair(group_info['result']["id"]):
            await self._send_group_pair_exists_message()
            return

        second_group_data = {
            "id": group_info['result']["id"],
            "title": group_info['result']["title"],
            "username": group_info['result']["username"]
        }

        if second_group_data["id"] == previous_data["id"]:
            await self.bot.send_message(chat_id=self.from_id, text="The second group cannot be the same as the first group. Please send the username of a different group.")
            return

        # Create group pair
        create_group_pair(previous_data, second_group_data)
        await self.bot.send_message(chat_id=self.from_id, text=f"Group pairing successful! The groups '{previous_data['title']}' and '{second_group_data['title']}' have been paired.")
        update_session(self.from_id, None, None)

    async def handle_blacklist_user(self):
        """Handle the logic when waiting to blacklist a user."""
        message = self.update_message
        if "forward_origin" in message and message['forward_origin']:
            await self._process_forwarded_user()
        elif "text" in message and message['text']:
            await self.process_blacklist_by_username()
        
        update_session(self.from_id, None, None)
        
    async def handle_delete_old_messages(self):
        num_of_days = self.update_message['text']
        
        if not num_of_days.isdigit():
            await self.bot.send_message(chat_id=self.from_id, text="Invalid input. Please enter a valid number of days.")
            return
        nums_of_days = int(num_of_days)
        await self.bot.send_message(chat_id=self.from_id, text=f"are you sure want to delete {nums_of_days} days old messages?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Yes", callback_data=f"delte_old_messages_confirm:{nums_of_days}"), InlineKeyboardButton(text="No", callback_data="cancel_delete_old_messages:no")]]))

    async def _process_forwarded_user(self):
        """Process the forwarded user details for blacklisting."""
        forward_origin = self.update_message["forward_origin"]
        sender_user = forward_origin.get("sender_user")

        if not sender_user:
            await self.bot.send_message(chat_id=self.from_id, text="The forwarded user has a private profile, and their information cannot be accessed. Please send their username directly.")
            return

        user_id = sender_user["id"]
        first_name = sender_user.get("first_name", "Unknown")
        last_name = sender_user.get("last_name")
        username = self.update_message["from"].get("username")

        if is_blacklisted(user_id):
            await self.bot.send_message(chat_id=self.from_id, text="This user is already in the blacklist. Please forward a message from a different user.")
            return

        success = create_blacklist_entry(user_id, first_name=first_name, last_name=last_name, username=username)
        if not success:
            await self._send_generic_error_message()
            return

        await self.bot.send_message(chat_id=self.from_id, text="User has been successfully blacklisted.")
        update_session(self.from_id, None, None)
        
    async def process_blacklist_by_username(self):
        username = self.update_message['text']
        if username.strip() == "":
            await self.bot.send_message(chat_id=self.from_id, text="invalid username.")
        normilized_username = normalize_username(username)[1:]
        if is_blacklisted(normilized_username):
            await self.bot.send_message(chat_id=self.from_id, text="This user is already in the blacklist.")
            return
        success = create_blacklist_entry(normilized_username)
        if not success:
            await self._send_generic_error_message()
            await self.bot.send_message(chat_id=self.from_id, text="An error occurred. Please try again later.")
            return

        await self.bot.send_message(chat_id=self.from_id, text="User has been successfully blacklisted.")
        update_session(self.from_id, None, None)
        
    async def _send_invalid_username_message(self):
        """Send a message to the user indicating the username is invalid."""
        await self.bot.send_message(chat_id=self.from_id, text="The username you provided is invalid. Please ensure the username is correct and try again.")
        update_session(self.from_id, None, None)

    async def _send_group_pair_exists_message(self):
        """Send a message to the user indicating the group pair already exists."""
        await self.bot.send_message(chat_id=self.from_id, text="This group is already part of an existing pair. Please provide a different group username.")
        update_session(self.from_id, None, None)

    async def _send_generic_error_message(self):
        """Send a generic error message to the user."""
        await self.bot.send_message(chat_id=self.from_id, text="An error occurred during the process. Please try again later.")
        update_session(self.from_id, None, None)
