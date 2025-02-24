from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, Application, ConversationHandler, MessageHandler, filters
from mirror_bot.db.admindb import load_admin_list, add_username_to_admin_list, is_admin, remove_from_admin_list
from mirror_bot.db.database import delete_old_message_pairs, get_service_state, add_or_update_service
from mirror_bot.management.states import *

async def handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the settings command."""
        if not is_admin(update.effective_user.username):
            await context.bot.send_message(chat_id=update.effective_user.id, text="You are not authorized to access settings.")
            return
            
        buttons = [
            [InlineKeyboardButton(text="Get Admins", callback_data="get_admins:null")],
            [InlineKeyboardButton(text="Add Admin", callback_data="add_admin:null")],
            [InlineKeyboardButton(text="Remove Admin", callback_data="remove_admin:null")],
            [InlineKeyboardButton(text="Delete Old Messages to save storage", callback_data="delete_old_messages:null")],
            [InlineKeyboardButton(text="Disable Mirroring", callback_data="disable_mirroring:null")],
            [InlineKeyboardButton(text="Enable Mirroring", callback_data="enable_mirroring:null")],
        ]
        await context.bot.send_message(chat_id=update.effective_user.id, text="Settings", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_get_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            admin_list = load_admin_list()
        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_user.id, text=f"Error loading admin list: {e}")
            return

        if not admin_list:
            await context.bot.send_message(chat_id=update.effective_user.id, text="No admins found.")
            return

        buttons = [[InlineKeyboardButton(text=f"@{username}", callback_data=f"admin_actions:{username}")] for username in admin_list]
        await context.bot.send_message(chat_id=update.effective_user.id, text="Admins:", reply_markup=InlineKeyboardMarkup(buttons))
        
        await context.bot.delete_message(chat_id=update.effective_user.id, message_id=update.message.message_id)



async def handle_delete_old_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
            chat_id=update._effective_user.id, 
            text="This option is used to delete old messages in groups that are less likely to receive replies. This helps save storage and improve performance."
        )
    await context.bot.send_message(
        chat_id=update._effective_user.id, 
        text="Please specify the number of days before which old messages should be deleted (this will delete all messages before that day):"
    )
    return WAITING_DELETE_OLD_MESSAGES_NUM_OF_DAYS


async def get_delete_numof_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    numofdays_str = update.message.text
    if not numofdays_str.isdigit():
        await context.bot.send_message(
            chat_id=update._effective_user.id, 
            text="Please specify the number of days before which old messages should be deleted (this will delete all messages before that day):"
        )
        return WAITING_DELETE_OLD_MESSAGES_NUM_OF_DAYS
    numofdays_int = int(numofdays_str)
    buttons = [[InlineKeyboardButton(text="Yes", callback_data=f"delete_messages:{numofdays_int}"), InlineKeyboardButton(text="No", callback_data="cancel_delete_old_messages:no")]]
    await context.bot.send_message(chat_id=update.effective_user.id, text=f"Are you sure you want to delete all {numofdays_int} days old messages?", reply_markup=InlineKeyboardMarkup(buttons))

    return WAITING_DELETE_OLD_MESSAGES_CONFIRM  
 

async def handle_delete_old_messages_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num_of_days = int(update.callback_query.data.split(":")[1])
    except (ValueError, IndexError):
        await update.callback_query.answer(text="Invalid input. Please enter a valid number of days.", show_alert=True)
        return
    success = delete_old_message_pairs(num_of_days)
    if success:
        await update.callback_query.answer(text=f"Successfully deleted {num_of_days} days old messages.", show_alert=True)
    else:
        await update.callback_query.answer(text="No matching messages Found.", show_alert=True)
    await update.callback_query.delete_message()
    return ConversationHandler.END

async def handle_disable_mirroring(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if get_service_state("MIRRORING_STATUS"):
            success = add_or_update_service("MIRRORING_STATUS", False)
            if success:
                await context.bot.send_message(chat_id=update.effective_user.id, text="Mirroring has been disabled successfully.")
            else:
                await context.bot.send_message(chat_id=update.effective_user.id, text="Failed to disable mirroring. Please try again later.")
        else:
            await context.bot.send_message(chat_id=update.effective_user.id, text="Mirroring is already disabled.")
  
async def handle_enable_mirroring(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    if not get_service_state("MIRRORING_STATUS"):
        success = add_or_update_service( "MIRRORING_STATUS", True)
        if success:
            await context.bot.send_message(chat_id=update.effective_user.id, text="Mirroring has been enabled successfully.")
        else:
            await context.bot.send_message(chat_id=update.effective_user.id, text="Failed to enable mirroring. Please try again later.")
    else:
        await context.bot.send_message(chat_id=update.effective_user.id, text="Mirroring is already enabled.") 

async def handle_add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the add admin button click."""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.username):
        await context.bot.send_message(chat_id=update.effective_user.id, text="You are not authorized to add admins.")
        return ConversationHandler.END
        
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Please send the username of the new admin (without @ symbol):"
    )
    return WAITING_FOR_NEW_ADMIN_USERNAME

async def handle_new_admin_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the new admin username input."""
    new_admin = update.message.text.strip()
    
    if not is_admin(update.effective_user.username):
        await context.bot.send_message(chat_id=update.effective_user.id, text="You are not authorized to add admins.")
        return ConversationHandler.END
        
    if new_admin.startswith('@'):
        new_admin = new_admin[1:]
        
    if is_admin(new_admin):
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"@{new_admin} is already an admin."
        )
    else:
        result = add_username_to_admin_list(new_admin)
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=result
        )
    return ConversationHandler.END

async def handle_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the remove admin button click."""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.username):
        await context.bot.send_message(chat_id=update.effective_user.id, text="You are not authorized to remove admins.")
        return ConversationHandler.END
        
    try:
        admin_list = load_admin_list()
        if len(admin_list) <= 1:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="Cannot remove the last admin. At least one admin must remain."
            )
            return ConversationHandler.END
            
        buttons = [[InlineKeyboardButton(text=f"@{username}", callback_data=f"remove_admin_confirm:{username}")] 
                  for username in admin_list if username != update.effective_user.username]
        
        if not buttons:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="No other admins to remove."
            )
            return ConversationHandler.END
            
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Select an admin to remove:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return WAITING_FOR_ADMIN_REMOVE_CONFIRM
        
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Error loading admin list: {e}"
        )
        return ConversationHandler.END

async def handle_remove_admin_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the admin removal confirmation."""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.username):
        await context.bot.send_message(chat_id=update.effective_user.id, text="You are not authorized to remove admins.")
        return ConversationHandler.END
        
    try:
        # Extract username from callback data
        admin_to_remove = query.data.split(":")[1].strip()
        
        # Check if trying to remove self
        if admin_to_remove == update.effective_user.username:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="You cannot remove yourself as admin."
            )
            return ConversationHandler.END
            
        # Try to remove the admin
        if remove_from_admin_list(admin_to_remove):
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"Successfully removed @{admin_to_remove} from admin list."
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"Failed to remove @{admin_to_remove} from admin list. They might already be removed."
            )
    except Exception as e:
        print(f"Error in remove_admin_confirm: {str(e)}")  # Debug log
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Error removing admin: {str(e)}"
        )
    
    try:
        await query.message.delete()
    except Exception:
        pass
        
    return ConversationHandler.END

def register(application: Application):
    application.add_handler(CommandHandler("settings", handle_settings))
    application.add_handler(CallbackQueryHandler(handle_get_admins, pattern="get_admins"))
    
    # Add admin conversation handler
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_add_admin, pattern="add_admin")],
        states={
            WAITING_FOR_NEW_ADMIN_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_admin_username)],
        },
        fallbacks=[],
        allow_reentry=True,
        per_message=True
    ))
    
    # Remove admin conversation handler
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_remove_admin, pattern="remove_admin")],
        states={
            WAITING_FOR_ADMIN_REMOVE_CONFIRM: [
                CallbackQueryHandler(handle_remove_admin_confirm, pattern=r"remove_admin_confirm:.*")
            ],
        },
        fallbacks=[],
        allow_reentry=True,
        per_message=True
    ))
    
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_delete_old_messages, pattern="delete_old_messages")],
        states={
            WAITING_DELETE_OLD_MESSAGES_NUM_OF_DAYS: [MessageHandler(filters.TEXT, get_delete_numof_days)],
            WAITING_DELETE_OLD_MESSAGES_CONFIRM: [CallbackQueryHandler(handle_delete_old_messages_confirm, pattern="delete_messages")]
        },
        fallbacks=[],
        per_message=True
    ))

    application.add_handler(CallbackQueryHandler(handle_disable_mirroring, pattern=r"^disable_mirroring"))
    application.add_handler(CallbackQueryHandler(handle_enable_mirroring, pattern=r"^enable_mirroring"))