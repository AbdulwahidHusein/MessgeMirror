
from telegram import (
     InlineKeyboardButton, InlineKeyboardMarkup, Bot, 
    ReplyKeyboardMarkup
)
from .states import *
from .state_handler  import StateHandler
from models import TelegramWebhook
# from db.admindb import load_admin_list

from ..database import (
     group_pairs_dao, group_pairs_dao, membership_dao, session_management_dao, whitelist_dao
)


class ManagementBot:
    def __init__(self, bot: Bot, webhook_data: TelegramWebhook):
        self.bot = bot
        self.update_message = webhook_data.message
        self.from_id = self.update_message['from']['id']
        self.user_session = session_management_dao.get_sessions_by_user_id(self.from_id)
        self.webhook_data = webhook_data
        self.message_handler = StateHandler(bot, webhook_data)
        


    async def handle_message(self):
        text = self.update_message['text']
        handlers = {
            '/start': self.start,
            'Add Group Pair': self.handle_add_pair,
            'Remove Group Pair': self.handle_remove_pair,
            'Add user to Whitelist': self.handle_add_to_whitelist,
            'Remove User From Whitelist': self.handle_remove_from_whitelist,
            'Get Group Pairs': self.handle_get_pairs,
            'Check Whitelisted user': self.check_whitelist,
            'settings': self.handle_settings,
            'Exit': self.handle_exit
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
                ["Add Group Pair", "Remove Group Pair"],
                ["Add user to Whitelist", "Remove User From Whitelist"],
                ["Get Group Pairs", "Check Whitelisted user"],
                ["settings", "Exit"],
                
            ]
        )
    
    async def handle_add_pair(self):
        """Handles adding a pair of groups."""
        membership_groups = membership_dao.get_member_ship_groups()
        
        await self.bot.send_message(chat_id=self.from_id, text="Please provide the username of the source group, or add me to the group and send any message in the group. You can also select from the list of groups I'm already a member of below:")
        # print(membership_groups)
        buttons = [[InlineKeyboardButton(text=f"{group['group_data']['title']}", callback_data=f"add_pair_inline:{group['group_data']['id']}")] for group in membership_groups if 'group_data' in group]

        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="Select a group to add:", buttons=buttons)
        session_management_dao.update_session(self.from_id, WAITING_FOR_SOURCE_GROUP, None)
    
    async def handle_remove_pair(self):
        """Handles removing a pair of groups."""
        pairs = group_pairs_dao.get_group_pairs()
        if not pairs:
            await self.bot.send_message(chat_id=self.from_id, text="No group pairs found.")
            return

        buttons = [[InlineKeyboardButton(text=f"From {pair['source_group_data']['title']} <to> {pair['dest_group_data']['title']}", callback_data=f"remove_pair:{pair['source_group_data']['id']}")] for pair in pairs]
        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="Select a group pair to remove:", buttons=buttons)
        session_management_dao.update_session(self.from_id, None, None)
        
        
    async def handle_add_to_whitelist(self):
        """Handles adding a user to the whitelists."""
        await self.bot.send_message(chat_id=self.from_id, text="Please forward a message from the user you wish to whitelist. or Enter username")
        session_management_dao.update_session(self.from_id, WAITING_FOR_WHITELIST, None)
    
    async def handle_remove_from_whitelist(self):
        """Handles removing a user from the whitelist."""
        whitelists = whitelist_dao.get_whitelisted_users()
        if not whitelists:
            await self.bot.send_message(chat_id=self.from_id, text="No users are currently whitelisted.")
            return

        buttons = [self._create_whitelist_button(user) for user in whitelists]
        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="Select a user to remove from the whitelist:", buttons=buttons)
        session_management_dao.update_session(self.from_id, WAITING_FOR_REMOVE_WHITELIST, None)
    
    
    async def handle_get_pairs(self):
        """Displays the list of all group pairs."""
        pairs = group_pairs_dao.get_group_pairs()
        if not pairs:
            await self.bot.send_message(chat_id=self.from_id, text="No group pairs found.")
            return

        buttons = [self._create_group_pair_button(pair) for pair in pairs]
        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="Here is a list of all group pairs:", buttons=buttons)
        session_management_dao.update_session(self.from_id, None, None)
        
    async def check_whitelist(self):
        await self.bot.send_message(chat_id=self.from_id, text="Please forward a message from the user you wish to check. or Enter username")
        session_management_dao.update_session(self.from_id, WAITING_FOR_WHITELIST_CHECK, None)
        
    
    
        
        
        
    def _create_whitelist_button(self, user: dict) -> list:
        """Helper method to create a button for each whitelisted user."""
        button_text = ""
        if user.get("first_name") is not None:
            button_text += f"{user.get('first_name', '')} "
        if user.get("last_name") is not None:
            button_text += f"{user.get('last_name', '')} "
        if len(button_text.strip()) == 0:
            if user.get("username") is not None:
                button_text += f"@{user.get('username', '')}"
        if button_text.strip() == "":
            button_text = str(user['user_id'])
        button_text = f"{button_text} (Click to remove from whitelist)".strip() or str(user['user_id'])
        return [InlineKeyboardButton(text=button_text, callback_data=f"remove_from_whitelist:{user['user_id']}")]
    
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
        
    def _create_group_pair_button(self, pair: dict) -> list:
        """Helper method to create a button for each group pair."""
        group1_title = pair.get("source_group_data", {}).get('title', 'Unknown Group 1')
        group2_title = pair.get("dest_group_data", {}).get('title', 'Unknown Group 2')
        button_text = f"{group1_title} <> {group2_title}"
        return [InlineKeyboardButton(text=button_text, callback_data='some_callback_data')]
    
    async def handle_settings(self):
        """Handles the settings command."""
        buttons = [
            [InlineKeyboardButton(text="View Admins", callback_data="get_admins:null")],
        ]
        await self.bot.send_message(chat_id=self.from_id, text="Settings", reply_markup=InlineKeyboardMarkup(buttons))
    
    async def handle_exit(self):
        """Ends the current session and sends a session exit message."""
        session_management_dao.delete_session(self.from_id)
        await self.bot.send_message(chat_id=self.from_id, text="Session ended.")

        