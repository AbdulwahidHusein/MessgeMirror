from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, Application, ConversationHandler, MessageHandler, filters
from mirror_bot.db.admindb import load_admin_list, add_username_to_admin_list, is_admin, remove_from_admin_list
from mirror_bot.db.database import delete_old_message_pairs, get_service_state, add_or_update_service
from mirror_bot.management.states import *

async def handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the settings command."""
    if not is_admin(update.effective_user.username):
        await update.message.reply_text("You are not authorized to access settings.")
        return
    
    buttons = [
        [InlineKeyboardButton(text="Get Admins", callback_data="get_admins")],
        [InlineKeyboardButton(text="Add Admin", callback_data="add_admin")],
        [InlineKeyboardButton(text="Remove Admin", callback_data="remove_admin")],
        [InlineKeyboardButton(text="Delete Old Messages", callback_data="delete_old_messages")],
        [InlineKeyboardButton(text="Disable Mirroring", callback_data="disable_mirroring")],
        [InlineKeyboardButton(text="Enable Mirroring", callback_data="enable_mirroring")],
    ]
    await update.message.reply_text(
        "Settings Menu:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_get_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the get admins button click."""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="You are not authorized to view admins."
        )
        return

    try:
        admin_list = load_admin_list()
        if not admin_list:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="No admins found."
            )
            return

        admin_text = "Current Admins:\n" + "\n".join([f"• @{admin}" for admin in admin_list])
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=admin_text
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Error loading admin list: {str(e)}"
        )

async def handle_add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the add admin button click."""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="You are not authorized to add admins."
        )
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
        await update.message.reply_text("You are not authorized to add admins.")
        return ConversationHandler.END
        
    if new_admin.startswith('@'):
        new_admin = new_admin[1:]
        
    result = add_username_to_admin_list(new_admin)
    await update.message.reply_text(result)
    return ConversationHandler.END

async def handle_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the remove admin button click."""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="You are not authorized to remove admins."
        )
        return ConversationHandler.END
        
    try:
        admin_list = load_admin_list()
        if len(admin_list) <= 1:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="Cannot remove the last admin. At least one admin must remain."
            )
            return ConversationHandler.END
            
        buttons = []
        for username in admin_list:
            if username != update.effective_user.username:
                callback_data = f"remove_admin_confirm:{username}"
                print(f"Creating button with callback_data: {callback_data}")  # Debug log
                buttons.append([InlineKeyboardButton(
                    text=f"@{username}",
                    callback_data=callback_data
                )])
        
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
            text=f"Error loading admin list: {str(e)}"
        )
        return ConversationHandler.END

async def handle_remove_admin_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the admin removal confirmation."""
    query = update.callback_query
    await query.answer()
    
    print(f"Received callback data: {query.data}")  # Debug log
    
    if not is_admin(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="You are not authorized to remove admins."
        )
        return ConversationHandler.END
        
    try:
        admin_to_remove = query.data.split(":")[1].strip()
        print(f"Attempting to remove admin: {admin_to_remove}")  # Debug log
        
        if admin_to_remove == update.effective_user.username:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="You cannot remove yourself as admin."
            )
            return ConversationHandler.END
            
        if remove_from_admin_list(admin_to_remove):
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"Successfully removed @{admin_to_remove} from admin list."
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"Failed to remove @{admin_to_remove}. They might already be removed."
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Error removing admin: {str(e)}"
        )
        print(f"Error in handle_remove_admin_confirm: {str(e)}")  # Debug log
    
    try:
        await query.message.delete()
    except Exception:
        pass
        
    return ConversationHandler.END

async def handle_delete_old_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the delete old messages button click."""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="You are not authorized to delete messages."
        )
        return ConversationHandler.END
        
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="This option will delete old messages to save storage space.\n\nPlease enter the number of days (messages older than this will be deleted):"
    )
    return WAITING_DELETE_OLD_MESSAGES_NUM_OF_DAYS

async def handle_delete_old_messages_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the delete old messages confirmation."""
    query = update.callback_query
    await query.answer()
    
    try:
        days = int(query.data.split(":")[1])
        if delete_old_message_pairs(days):
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"Successfully deleted messages older than {days} days."
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="No messages found to delete."
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Error deleting messages: {str(e)}"
        )
    
    return ConversationHandler.END

async def handle_disable_mirroring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the disable mirroring button click."""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="You are not authorized to change mirroring settings."
        )
        return
        
    if get_service_state("MIRRORING_STATUS"):
        if add_or_update_service("MIRRORING_STATUS", False):
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="Message mirroring has been disabled."
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="Failed to disable mirroring. Please try again."
            )
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Message mirroring is already disabled."
        )

async def handle_enable_mirroring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the enable mirroring button click."""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="You are not authorized to change mirroring settings."
        )
        return
        
    if not get_service_state("MIRRORING_STATUS"):
        if add_or_update_service("MIRRORING_STATUS", True):
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="Message mirroring has been enabled."
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="Failed to enable mirroring. Please try again."
            )
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Message mirroring is already enabled."
        )

async def get_delete_numof_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the input for number of days for message deletion."""
    try:
        days = int(update.message.text.strip())
        if days <= 0:
            await update.message.reply_text("Please enter a positive number of days.")
            return WAITING_DELETE_OLD_MESSAGES_NUM_OF_DAYS
            
        buttons = [[InlineKeyboardButton(
            text=f"Confirm Delete Messages Older Than {days} Days",
            callback_data=f"delete_messages:{days}"
        )]]
        
        await update.message.reply_text(
            f"Are you sure you want to delete messages older than {days} days?",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return WAITING_DELETE_OLD_MESSAGES_CONFIRM
        
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return WAITING_DELETE_OLD_MESSAGES_NUM_OF_DAYS

def register(application: Application):
    """Registers all settings-related handlers."""
    # Main settings command and simple callbacks
    application.add_handler(CommandHandler("settings", handle_settings))
    application.add_handler(CallbackQueryHandler(handle_get_admins, pattern=r"^get_admins$"))
    application.add_handler(CallbackQueryHandler(handle_disable_mirroring, pattern=r"^disable_mirroring$"))
    application.add_handler(CallbackQueryHandler(handle_enable_mirroring, pattern=r"^enable_mirroring$"))
    
    # Add admin conversation
    application.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(handle_add_admin, pattern=r"^add_admin$")],
            states={
                WAITING_FOR_NEW_ADMIN_USERNAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_admin_username)
                ],
            },
            fallbacks=[CommandHandler("exit", lambda u, c: ConversationHandler.END)],
            allow_reentry=True,
            per_chat=True,
            per_user=True
        )
    )
    
    # Remove admin conversation
    application.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(handle_remove_admin, pattern=r"^remove_admin$")],
            states={
                WAITING_FOR_ADMIN_REMOVE_CONFIRM: [
                    CallbackQueryHandler(handle_remove_admin_confirm, pattern=r"^remove_admin_confirm:")
                ],
            },
            fallbacks=[CommandHandler("exit", lambda u, c: ConversationHandler.END)],
            allow_reentry=True,
            per_chat=True,
            per_user=True
        )
    )
    
    # Delete old messages conversation
    application.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(handle_delete_old_messages, pattern=r"^delete_old_messages$")],
            states={
                WAITING_DELETE_OLD_MESSAGES_NUM_OF_DAYS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_delete_numof_days)
                ],
                WAITING_DELETE_OLD_MESSAGES_CONFIRM: [
                    CallbackQueryHandler(handle_delete_old_messages_confirm, pattern=r"^delete_messages:")
                ],
            },
            fallbacks=[CommandHandler("exit", lambda u, c: ConversationHandler.END)],
            allow_reentry=True,
            per_chat=True,
            per_user=True
        )
    )