from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    MONGO_URL = os.getenv("MONGO_URL")
    MIRROR_BOT_TOKEN = os.getenv("MIRROR_BOT_TOKEN")
    VERIFICATION_BOT_TOKEN = os.getenv("VERIFICATION_BOT_TOKEN")
    APP_PORT = os.getenv("PORT")
    APP_HOST = os.getenv("APP_HOST")
    MIRROR_WEB_HOOK_URI = os.getenv("MIRROR_WEB_HOOK_URL")
    VERIFICATION_WEBHOOK_URI= os.getenv("VERIFICATION_WEBHOOK_URL")
    WEBHOOK_SECRET_TOKEN=os.getenv("WEBHOOK_SECRET_TOKEN")

    MIRROR_ENABLED = os.getenv("MIRROR_ENABLED").lower() == "true"
    VERIFICATION_ENABLED = os.getenv("VERIFICATION_ENABLED").lower() == "true"
    
    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID") 
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
    TELEGRAM_PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER")