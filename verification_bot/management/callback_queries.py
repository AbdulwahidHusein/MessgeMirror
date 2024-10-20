from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from models import TelegramWebhook
from verification_bot.database import whitelist_dao, group_pairs_dao, session_management_dao, membership_dao, admin_dao
from .states import WAITING_FOR_DEST_GROUP


class CallbackQueryHandler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.user_id = None
        self.callback_data = None
        self.message = None
        
    async def handle(self, webhook_data: TelegramWebhook):
        callback_query = webhook_data.callback_query
        self.user_id = callback_query['from']['id']
        self.callback_data = callback_query['data']
        self.message = callback_query.get('message', {})
        
        action = self.callback_data.split(":")[0]
        
        handlers = {
            "remove_from_whitelist": self.handle_remove_from_whitelist,
            "remove_pair" : self.handle_remove_pair,
            'add_pair_inline' : self.handle_add_pair_inline,
            "get_admins" : self.handle_get_admins,
        }
        
        if action in handlers:
            await handlers[action]()
        
        
    async def handle_remove_from_whitelist(self):
        try:
            user_id = int(self.callback_data.split(":")[1])
            removed = whitelist_dao.remove_from_whitelist(user_id)  
            if removed:
                await self.bot.send_message(chat_id=self.user_id, text="user deleted from whitelist ssuccesfully! ")
            else:
                await self.bot.send_message(chat_id = self.user_id, text = "something went wrong please try again.")
        except (ValueError, IndexError):
            username = self.callback_data.split(":")[1]
            removed = whitelist_dao.remove_from_whitelist(username)
            if removed:
                await self.bot.send_message(chat_id=self.user_id, text="user deleted from whitelist ssuccesfully! ")
            else:
                await self.bot.send_message(chat_id = self.user_id, text = "something went wrong please try again.")

    async def handle_remove_pair(self):
        try:
            pair_id = int(self.callback_data.split(":")[1])
            removed = group_pairs_dao.delete_group_pair(pair_id)  
            if removed:
                await self.bot.send_message(chat_id=self.user_id, text="group pair deleted succesfully! ")
            else:
                await self.bot.send_message(chat_id = self.user_id, text = "something went wrong please try again.")
        except (ValueError, IndexError):
            await self.bot.send_message(chat_id = self.user_id, text = "something went wrong please try again.")
    
    
    async def handle_add_pair_inline(self):
        try:
            group_id = int(self.callback_data.split(":")[1])
        except (ValueError, IndexError):
            await self.bot.send_message(chat_id=self.user_id, text="Invalid group ID. Please select a valid group.")
            return

        if group_pairs_dao.has_group_pair(group_id):
            await self.bot.send_message(chat_id=self.user_id, text="This group is already paired. Please select another group.")
            return

        session = session_management_dao.get_sessions_by_user_id(self.user_id)
        group_info = membership_dao.get_member_shipgroup_by_id(group_id)

        if not group_info or 'group_data' not in group_info:
            await self.bot.send_message(chat_id=self.user_id, text="Failed to retrieve group information. Please try again.")
            return

        if session and session.get("previous_data") is None:
            await self.bot.send_message(chat_id=self.user_id, text="Now send me the username of the second group or add me to the group and send any message to the group, or select from the list of available groups.")
            session_management_dao.update_session(self.user_id, WAITING_FOR_DEST_GROUP, group_info['group_data'])
            
        elif session and session.get("previous_data") is not None:
            previous_data = session.get("previous_data")
            if previous_data.get("id") == group_id:
                await self.bot.send_message(chat_id=self.user_id, text="A group cannot be paired with itself. Please select a different group.")
                return

            success = group_pairs_dao.create_group_pair(previous_data, group_info['group_data'])
            if success:
                await self.bot.send_message(chat_id=self.user_id, text=f"Group pair created: {previous_data['title']} <> {group_info['group_data']['title']} successfully.")
                await self.bot.delete_message(chat_id=self.user_id, message_id=self.message['message_id'])
            else:
                await self.bot.send_message(chat_id=self.user_id, text="Failed to create group pair. Please try again.")
            session_management_dao.delete_session(self.user_id)
        else:
            await self.bot.send_message(chat_id=self.user_id, text="Something went wrong! Please try again.")
            session_management_dao.delete_session(self.user_id)
            
            
    async def handle_get_admins(self):
        try:
            admin_list = admin_dao.load_admin_list()
        except Exception as e:
            await self.bot.send_message(chat_id=self.user_id, text=f"Error loading admin list: {e}")
            return

        if not admin_list:
            await self.bot.send_message(chat_id=self.user_id, text="No admins found.")
            return

        buttons = [[InlineKeyboardButton(text=f"@{username}", callback_data=f"admin_actions:{username}")] for username in admin_list]
        await self.bot.send_message(chat_id=self.user_id, text="Admins:", reply_markup=InlineKeyboardMarkup(buttons))
        
        await self.bot.delete_message(chat_id=self.user_id, message_id=self.message['message_id'])
            