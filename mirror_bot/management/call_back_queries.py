from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from models import TelegramWebhook
from db.database import (
    delete_group_pair, 
    delete_whitelist_entry, 
    get_sessions_by_user_id, 
    get_member_shipgroup_by_id, 
    update_session, 
    has_group_pair, 
    create_group_pair, 
    delete_session,
    delete_old_message_pairs,
)
from db.admindb import load_admin_list
from .states import WAITING_FOR_SECOND_GROUP, WAITING_DELETE_OLD_MESSAGES_NUM_OF_DAYS

class CallbackQueryHandler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.user_id = None
        self.callback_data = None
        self.message = None

    async def handle(self, webhook_data: TelegramWebhook):
        # Set the state variables
        callback_query = webhook_data.callback_query
        self.user_id = callback_query['from']['id']
        self.callback_data = callback_query['data']
        self.message = callback_query.get('message', {})

        # Map callback actions to handler methods
        action = self.callback_data.split(":")[0]
        handlers = {
            "remove_pair": self.handle_remove_pair,
            "confirm_remove_pair": self.handle_confirm_remove_pair,
            "remove_from_whitelist": self.handle_remove_from_whitelist,  
            "add_pair_inline": self.handle_add_pair_inline,
            "get_admins": self.handle_get_admins,
            "delete_old_messages": self.handle_delete_old_messages,
            "delte_old_messages_confirm": self.handle_delete_old_messages_confirm,
        }

        if action in handlers:
            await handlers[action]()
        else:
            await self.bot.send_message(chat_id=self.user_id, text="No action was found.")
         
    async def handle_remove_pair(self):
        pair_id = self.callback_data.split(":")[1]
        await self.bot.send_message(
            chat_id=self.user_id,
            text="Are you sure you want to remove this group pair?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Yes", callback_data=f"confirm_remove_pair:{pair_id}"),
                 InlineKeyboardButton(text="No", callback_data="cancel")]
            ])
        )
        
    async def handle_get_admins(self):
        try:
            admin_list = load_admin_list()
        except Exception as e:
            await self.bot.send_message(chat_id=self.user_id, text=f"Error loading admin list: {e}")
            return

        if not admin_list:
            await self.bot.send_message(chat_id=self.user_id, text="No admins found.")
            return

        buttons = [[InlineKeyboardButton(text=f"@{username}", callback_data=f"admin_actions:{username}")] for username in admin_list]
        await self.bot.send_message(chat_id=self.user_id, text="Admins:", reply_markup=InlineKeyboardMarkup(buttons))
        
        await self.bot.delete_message(chat_id=self.user_id, message_id=self.message['message_id'])

    async def handle_confirm_remove_pair(self):
        try:
            pair_id = int(self.callback_data.split(":")[1])
            success = delete_group_pair(pair_id)
            if success:
                await self.bot.send_message(chat_id=self.user_id, text=f"Group pair with ID {pair_id} has been successfully removed.")
                await self.bot.delete_message(chat_id=self.user_id, message_id=self.message['message_id'])
            else:
                await self.bot.send_message(chat_id=self.user_id, text=f"Failed to remove the group pair with ID {pair_id}. It may not exist.")
            update_session(self.user_id, None, None)
        except (ValueError, IndexError):
            await self.bot.send_message(chat_id=self.user_id, text="Invalid group pair ID. Please try again.")

    async def handle_remove_from_whitelist(self):
        try:
            client_id = int(self.callback_data.split(":")[1])
        except (ValueError, IndexError):
            client_id = self.callback_data.split(":")[1]
        
        success = delete_whitelist_entry(client_id)
        if success:
            await self.bot.send_message(chat_id=self.user_id, text="User has been successfully removed from the whitelist.")
            await self.bot.delete_message(chat_id=self.user_id, message_id=self.message['message_id'])
        else:
            await self.bot.send_message(chat_id=self.user_id, text="Failed to remove user from the whitelist. The user may not be whitelisted.")
        update_session(self.user_id, None, None)

    async def handle_add_pair_inline(self):
        try:
            group_id = int(self.callback_data.split(":")[1])
        except (ValueError, IndexError):
            await self.bot.send_message(chat_id=self.user_id, text="Invalid group ID. Please select a valid group.")
            return

        if has_group_pair(group_id):
            await self.bot.send_message(chat_id=self.user_id, text="This group is already paired. Please select another group.")
            return

        session = get_sessions_by_user_id(self.user_id)
        group_info = get_member_shipgroup_by_id(group_id)

        if not group_info or 'group_data' not in group_info:
            await self.bot.send_message(chat_id=self.user_id, text="Failed to retrieve group information. Please try again.")
            return

        if session and session.get("previous_data") is None:
            await self.bot.send_message(chat_id=self.user_id, text="Now send me the username of the second group or add me to the group and send any message to the group, or select from the list of available groups.")
            update_session(self.user_id, WAITING_FOR_SECOND_GROUP, group_info['group_data'])
        elif session and session.get("previous_data") is not None:
            previous_data = session.get("previous_data")
            if previous_data.get("id") == group_id:
                await self.bot.send_message(chat_id=self.user_id, text="A group cannot be paired with itself. Please select a different group.")
                return

            create_group_pair(previous_data, group_info['group_data'])
            await self.bot.send_message(chat_id=self.user_id, text=f"Group pair created: {previous_data['title']} <> {group_info['group_data']['title']} successfully.")
            await self.bot.delete_message(chat_id=self.user_id, message_id=self.message['message_id'])
            delete_session(self.user_id)
        else:
            await self.bot.send_message(chat_id=self.user_id, text="Something went wrong! Please try again.")
            
    async def handle_delete_old_messages(self):
        await self.bot.send_message(
                chat_id=self.user_id, 
                text="This option is used to delete old messages in groups that are less likely to receive replies. This helps save storage and improve performance."
            )
        await self.bot.send_message(
            chat_id=self.user_id, 
            text="Please specify the number of days before which old messages should be deleted (this will delete all messages before that day):"
        )
        update_session(self.user_id, WAITING_DELETE_OLD_MESSAGES_NUM_OF_DAYS, None)

    async def handle_delete_old_messages_confirm(self):
        try:
            num_of_days = int(self.callback_data.split(":")[1])
        except (ValueError, IndexError):
            await self.bot.send_message(chat_id=self.user_id, text="Invalid input. Please enter a valid number of days.")
            return
        nums_of_days = int(num_of_days)
        success = delete_old_message_pairs(nums_of_days)
        if success:
            await self.bot.delete_message(chat_id=self.user_id, message_id=self.message['message_id'])
            await self.bot.send_message(chat_id=self.user_id, text=f"Successfully deleted {nums_of_days} days old messages.")
        else:
            await self.bot.send_message(chat_id=self.user_id, text="No matching messages Found.")
            