import os
import sqlite3
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from telegram import Bot, Update
from telegram.error import TelegramError
from telegram.ext import CommandHandler, CallbackContext


# Configure logging to output all request details
logging.basicConfig(level=logging.INFO)

# SQLite Database setup
DATABASE = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Create tables if they don't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_a_username TEXT,
        group_b_username TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS whitelist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Pydantic model for handling incoming webhook data
class TelegramWebhook(BaseModel):
    update_id: int
    message: Optional[dict] = None


async def next_step(command, chat_id, bot):
    try:
        if command == "/start":
            await send_welcome_message(chat_id)
        elif command == "/add-pair":
            await ask_for_pair_usernames(chat_id)
        elif command == "/remove-pair":
            await ask_for_removal(chat_id)
        elif command == "/list-pairs":
            await list_pairs(chat_id)
        elif command == "/help":
            await send_help_message(chat_id)
        elif command == "add-whitelist":
            await ask_for_whitelist_username(chat_id)
        elif command == "remove-whitelist":
            await ask_for_whitelist_removal(chat_id)
        else:
            await bot.send_message(chat_id, "Unknown command. Type /help for available commands.")
    except Exception as e:
        logging.error(f"Error processing command: {e}")
        await bot.send_message(chat_id, "An error occurred while processing your request.")
    
    return {"message": "ok"}

async def send_welcome_message(chat_id, bot):
    await bot.send_message(chat_id, "Welcome! Use /help to see available commands.")

async def send_help_message(chat_id, bot):
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/add-pair - Add a username pair\n"
        "/remove-pair - Remove a username pair\n"
        "/list-pairs - List all username pairs\n"
        "/add-whitelist - Add a username to whitelist\n"
        "/remove-whitelist - Remove a username from whitelist\n"
    )
    await bot.send_message(chat_id, help_text)

async def ask_for_pair_usernames(chat_id, bot):
    await bot.send_message(chat_id, "Please send the username of Group A.")
    # You can set a state here to wait for the next message for Group B's username

async def ask_for_whitelist_username(chat_id, bot):
    await bot.send_message(chat_id, "Please send the username to add to the whitelist.")

async def list_pairs(chat_id, bot):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT group_a_username, group_b_username FROM pairs")
    pairs = cursor.fetchall()
    conn.close()

    if pairs:
        pairs_text = "\n".join([f"{a} ↔ {b}" for a, b in pairs])
        await bot.send_message(chat_id, f"Current pairs:\n{pairs_text}")
    else:
        await bot.send_message(chat_id, "No pairs found.")

async def ask_for_removal(chat_id, bot):
    await bot.send_message(chat_id, "Please send the username of the pair to remove.")

async def ask_for_whitelist_removal(chat_id, bot):
    await bot.send_message(chat_id, "Please send the username to remove from the whitelist.")


