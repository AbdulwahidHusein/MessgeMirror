from states import WAITING_FOR_FIRST_GROUP, WAITING_FOR_SECOND_GROUP, WAITING_FOR_BLACKLIST_USER
from mongo import get_sessions_by_user_id, update_session, has_group_pair, create_group_pair, is_blacklisted, create_blacklist_entry
from utils import get_group_info_by_username
from telegram import Bot
from model import TelegramWebhook
from typing import Optional


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
        else:
            await self.bot.send_message(chat_id=self.from_id, text="Invalid Request Youse Buttons to ineract.")

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
        await self.bot.send_message(chat_id=self.from_id, text="Please send me the username of the Second Group")

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
            await self.bot.send_message(chat_id=self.from_id, text="You cannot pair a group with itself. Please send a different group.")
            return

        # Create group pair
        create_group_pair(previous_data, second_group_data)
        await self.bot.send_message(chat_id=self.from_id, text=f"Pair created: {previous_data['title']} and {second_group_data['title']} successfully.")
        update_session(self.from_id, None, None)

    async def handle_blacklist_user(self):
        """Handle the logic when waiting to blacklist a user."""
        message = self.update_message
        if "forward_origin" in message and message['forward_origin']:
            await self._process_forwarded_user()
        elif "text" in message and message['text']:
            await self.bot.send_message(chat_id=self.from_id, text="Please forward a message from the user to be blacklisted.")

    async def _process_forwarded_user(self):
        """Process the forwarded user details for blacklisting."""
        forward_origin = self.update_message["forward_origin"]
        sender_user = forward_origin.get("sender_user")

        if not sender_user:
            await self.bot.send_message(chat_id=self.from_id, text="This profile is private. I can't access their profile. Please try sending their username.")
            return

        user_id = sender_user["id"]
        first_name = sender_user.get("first_name", "Unknown")
        last_name = sender_user.get("last_name")
        username = self.update_message["from"].get("username")

        if is_blacklisted(user_id):
            await self.bot.send_message(chat_id=self.from_id, text="User already blacklisted. Please forward a message from another user.")
            return

        success = create_blacklist_entry(user_id, first_name=first_name, last_name=last_name, username=username)
        if not success:
            await self._send_generic_error_message()
            return

        await self.bot.send_message(chat_id=self.from_id, text="User blacklisted successfully.")
        update_session(self.from_id, None, None)

    async def _send_invalid_username_message(self):
        """Send a message to the user indicating the username is invalid."""
        await self.bot.send_message(chat_id=self.from_id, text="Invalid username. Please try again.")
        update_session(self.from_id, None, None)

    async def _send_group_pair_exists_message(self):
        """Send a message to the user indicating the group pair already exists."""
        await self.bot.send_message(chat_id=self.from_id, text="Group pair already exists. Please try again.")
        update_session(self.from_id, None, None)

    async def _send_generic_error_message(self):
        """Send a generic error message to the user."""
        await self.bot.send_message(chat_id=self.from_id, text="Something went wrong, please try again.")
        update_session(self.from_id, None, None)
