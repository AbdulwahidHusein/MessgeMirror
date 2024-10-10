import os
from dotenv import load_dotenv
from pymongo import MongoClient
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, 
    ReplyKeyboardMarkup
)
from telegram.ext import CallbackContext
from utils import *
from states import *
from states_handler import CommonMessageHandler
from model import TelegramWebhook
from database import (
     get_group_pairs, get_blacklist, get_sessions_by_user_id, update_session, delete_session, get_member_ship_groups
)

# Load environment variables
load_dotenv()

class UserSession:
    def __init__(self, user_id: int, session_name: str):
        self.user_id = user_id
        self.session_name = session_name

class SessionManager:
    def __init__(self, bot: Bot, webhook_data: TelegramWebhook):
        self.bot = bot
        self.update_message = webhook_data.message
        self.from_id = self.update_message['from']['id']
        self.user_session = get_sessions_by_user_id(self.from_id)
        self.webhook_data = webhook_data
        self.message_handler = CommonMessageHandler(bot, webhook_data)

    async def handle_message(self):
        text = self.update_message['text']
        handlers = {
            '/start': self.start,
            'Add Pair': self.handle_add_pair,
            'Remove Pair': self.handle_remove_pair,
            'Add to Blacklist': self.handle_add_to_blacklist,
            'Remove From Blacklist': self.handle_remove_from_blacklist,
            'Get Pairs': self.handle_get_pairs,
            'Get Blacklist': self.handle_get_blacklist,
            'Help': self.handle_help,
            'Exit': self.handle_exit,
        }
        
        handler = handlers.get(text)
        if handler:
            await handler()
        else:
            await self.message_handler.handle_messages()

    async def start(self):
        """Starts the bot by displaying available options with buttons."""
        await self._send_message_with_keyboard(
            chat_id=self.from_id,
            text="Please select an option from the menu below:",
            options=[
                ["Add Pair", "Remove Pair"],
                ["Add to Blacklist", "Remove From Blacklist"],
                ["Get Pairs", "Get Blacklist"],
                ["Help", "Exit"],
                
            ]
        )

    async def handle_add_pair(self):
        """Handles adding a pair of groups."""
        membership_groups = get_member_ship_groups()
        
        await self.bot.send_message(chat_id=self.from_id, text="Please provide the username of the first group, or add me to the group and send any message in the group. You can also select from the list of groups I'm already a member of below:")

        buttons = [[InlineKeyboardButton(text=f"{group['group_data']['title']}", callback_data=f"add_pair_inline:{group['group_data']['id']}")] for group in membership_groups]

        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="Select a group to add:", buttons=buttons)
        update_session(self.from_id, WAITING_FOR_FIRST_GROUP, None)

    async def handle_remove_pair(self):
        """Handles removing a pair of groups."""
        pairs = get_group_pairs()
        if not pairs:
            await self.bot.send_message(chat_id=self.from_id, text="No group pairs found.")
            return

        buttons = [[InlineKeyboardButton(text=f"{pair['group1_data']['title']} <> {pair['group2_data']['title']}", callback_data=f"remove_pair:{pair['group1_data']['id']}")] for pair in pairs]
        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="Select a group pair to remove:", buttons=buttons)

    async def handle_add_to_blacklist(self):
        """Handles adding a user to the blacklist."""
        await self.bot.send_message(chat_id=self.from_id, text="Please forward a message from the user you wish to blacklist.")
        update_session(self.from_id, WAITING_FOR_BLACKLIST_USER)

    async def handle_remove_from_blacklist(self):
        """Handles removing a user from the blacklist."""
        blacklists = get_blacklist()
        if not blacklists:
            await self.bot.send_message(chat_id=self.from_id, text="No users are currently blacklisted.")
            return

        buttons = [self._create_blacklist_button(user) for user in blacklists]
        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="Select a user to remove from the blacklist:", buttons=buttons)
        update_session(self.from_id, WAITING_FOR_REMOVE_BLACKLIST_USER, None)

    async def handle_get_pairs(self):
        """Displays the list of all group pairs."""
        pairs = get_group_pairs()
        if not pairs:
            await self.bot.send_message(chat_id=self.from_id, text="No group pairs found.")
            return

        buttons = [self._create_group_pair_button(pair) for pair in pairs]
        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="Here is a list of all group pairs:", buttons=buttons)

    async def handle_get_blacklist(self):
        """Displays the list of all blacklisted users."""
        blacklisted_users = get_blacklist()
        if not blacklisted_users:
            await self.bot.send_message(chat_id=self.from_id, text="No users have been blacklisted yet.")
            return

        buttons = [self._create_blacklist_button(user) for user in blacklisted_users]
        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="Here is a list of all blacklisted users:", buttons=buttons)

    async def handle_help(self):
        """Sends a help message with a list of available commands."""
        help_message = """
    *🛠️ Available Commands:*

    1. *🔄 /start:* Start the bot and display available options.
    2. *➕ Add Group Pair:* Add a pair of groups. You can select from a list of groups the bot is a member of or provide a group username.
    3. *❌ Remove Group Pair:* Remove an existing group pair. You will be prompted to select among existing pairs to delete.
    4. *🚫 Add to Blacklist:* Add a user to the blacklist so that their messages will not be mirrored.
    5. *✅ Remove from Blacklist:* Remove a user from the blacklist so that their messages will be mirrored again.
    6. *📜 List Group Pairs:* List all group pairs.
    7. *⛔️ Show Blacklist:* List all blacklisted users.
    8. *🚪 Exit:* End the current session and close the bot.

    """
        
        await self.bot.send_message(chat_id=self.from_id, text=help_message, parse_mode='Markdown')

    async def handle_exit(self):
        """Ends the current session and sends a session exit message."""
        await self.bot.send_message(chat_id=self.from_id, text="Your session has been successfully closed.")
        delete_session(self.from_id)

    async def _send_message_with_keyboard(self, chat_id: int, text: str, options: list):
        """Helper method to send a message with a custom reply keyboard."""
        await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=options,
                one_time_keyboard=False,
                resize_keyboard=True
            )
        )

    async def _send_message_with_inline_keyboard(self, chat_id: int, text: str, buttons: list):
        """Helper method to send a message with inline keyboard buttons."""
        reply_markup = InlineKeyboardMarkup(buttons)
        await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

    def _create_blacklist_button(self, user: dict) -> list:
        """Helper method to create a button for each blacklisted user."""
        button_text = ""
        if user.get("first_name") is not None:
            button_text += f"{user.get('first_name', '')} "
        if user.get("last_name") is not None:
            button_text += f"{user.get('last_name', '')} "
        if len(button_text.strip()) == 0:
            if user.get("username") is not None:
                button_text += f"@{user.get('username', '')}"
        button_text = f"{button_text} (Click to remove from blacklist)".strip() or str(user['userid'])
        return [InlineKeyboardButton(text=button_text, callback_data=f"remove_from_blacklist:{user['userid']}")]

    def _create_group_pair_button(self, pair: dict) -> list:
        """Helper method to create a button for each group pair."""
        group1_title = pair.get("group1_data", {}).get('title', 'Unknown Group 1')
        group2_title = pair.get("group2_data", {}).get('title', 'Unknown Group 2')
        button_text = f"{group1_title} <> {group2_title}"
        return [InlineKeyboardButton(text=button_text, callback_data='some_callback_data')]
