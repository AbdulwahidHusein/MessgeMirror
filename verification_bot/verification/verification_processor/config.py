from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    MONGO_URL = os.getenv("MONGO_URL")
    MIRROR_BOT_TOKEN = os.getenv("MIRROR_BOT_TOKEN")
    VERIFICATION_BOT_TOKEN = os.getenv("VERIFICATION_BOT_TOKEN")
    APP_PORT = os.getenv("PORT")
    APP_HOST = os.getenv("APP_HOST")
    WEB_HOOK_URL = os.getenv("WEB_HOOK_URL")
    
    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
    TELEGRAM_PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER")