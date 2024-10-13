from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    MONGO_URL = os.getenv("MONGO_URL")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    APP_PORT = os.getenv("PORT")
    APP_HOST = os.getenv("APP_HOST")
    WEB_HOOK_URL = os.getenv("WEB_HOOK_URL")