from telegram import Update
from telegram.ext import ContextTypes, Application, ConversationHandler, CommandHandler



async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a detailed help message with a list of available commands and their explanations."""
    help_message = """
📚 *Welcome to Message Mirror Bot Help Center!*

This bot helps you mirror messages between paired Telegram groups. Here's everything you need to know:

🔰 *Getting Started:*
• Type /start to begin using the bot
• The bot needs to be a member in both groups you want to pair
• Only admins can manage group pairs and settings

📋 *Main Commands:*

1️⃣ *Managing Group Pairs:*
• `/addpair` - Connect two groups for message mirroring
  _Example: Messages from Group A will appear in Group B and vice versa_
  _Steps:_
  - Click /addpair
  - Select the first group from list of groups or send its username
  - Select the second group from list of groups or send its username
  - Done! Messages will now be mirrored between these groups

• `/removepair` - Disconnect a pair of groups
  _Steps:_
  - Click /removepair
  - Select the pair you want to disconnect
  - Confirm your choice

• `/GetPairs` - See all currently connected group pairs
  _Shows you which groups are currently mirroring messages to each other_

2️⃣ *Managing Message Filtering:*
• `/addwhitelist` - Stop mirroring messages from specific users
  _Useful for:_
  - Bot commands
  - Administrative messages
  - Private announcements
  _Steps:_
  - Click /addwhitelist
  - Send the username or user ID of the person
  - Their messages won't be mirrored anymore

• `/removewhitelist` - Resume mirroring messages from whitelisted users
  _Steps:_
  - Click /removewhitelist
  - Select the user from the list
  - Their messages will be mirrored again

• `/Getwhitelist` - View all users whose messages aren't being mirrored

3️⃣ *Settings and Configuration:*
• `/settings` - Access advanced bot settings
  _Options available:_
  - View admin list
  - Delete old messages to save storage
  - Enable/Disable message mirroring
  - Manage bot configuration

4️⃣ *Other Commands:*
• `/help` - Show this help message
• `/exit` - End your current session with the bot

💡 *Tips:*
• Always ensure the bot has proper admin rights in both groups
• Use the whitelist for bots and announcement messages
• Regular users can't see or access admin commands
• Messages are mirrored instantly when sent

⚠️ *Important Notes:*
• The bot must be an added to both groups to work
• Whitelisted users' messages won't be mirrored
• Media messages (photos, videos, etc.) are also mirrored
• Reply chains are preserved across groups

❓ *Need More Help?*
If you need additional assistance or have questions, please contact the bot administrator.

🔒 *Privacy & Security:*
• The bot only mirrors messages between paired groups
• Private messages are never mirrored
• Admin commands are protected
• Message history is stored securely
"""
    
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=help_message,
        parse_mode='Markdown'
    )


async def handle_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ends the current session and sends a session exit message."""
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Your session has been successfully closed. Type /start to begin a new session."
    )
    context.user_data.clear()
    return ConversationHandler.END


def register(application:Application):
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(CommandHandler('exit', handle_exit))
