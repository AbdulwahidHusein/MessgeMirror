import asyncio
from datetime import datetime, timedelta
import pytz  
from telethon import TelegramClient
from config import Config

API_ID = Config.TELEGRAM_API_ID           
API_HASH = Config.TELEGRAM_API_HASH
PHONE_NUMBER = Config.TELEGRAM_PHONE_NUMBER

client = TelegramClient('session_name', API_ID, API_HASH)

async def get_similar_messages(group_username, account_number, HOURS_BACK = 3):
    messages = []
    await client.start(phone=PHONE_NUMBER)  

    group = await client.get_entity(group_username)
    tz = pytz.UTC  

    cutoff_time = datetime.now(tz) - timedelta(hours=HOURS_BACK)

    async for message in client.iter_messages(group, search=account_number):
        if message.date.tzinfo is None:
            message.date = message.date.replace(tzinfo=tz)  # Set timezone if naive

        # Stop if the message is older than the cutoff time
        if message.date < cutoff_time:
            break
        messages.append(message)
    
    return messages
        

async def run_search(group_username, account_number, hours_back = 3):
    return await get_similar_messages(group_username, account_number, hours_back)

# Example entry point for testing
if __name__ == '__main__':
    async def main():
        result = await run_search("@ababababnl", "67304733674")
        if result:
            print(result[0].text)
        else:
            print("No messages found.")

    asyncio.run(main())