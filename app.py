import os
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import admin, mirror_router, verification_roter
from config import Config
import logging
load_dotenv()

app = FastAPI()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin.router)
app.include_router(mirror_router.router)
app.include_router(verification_roter.router)

# @app.on_event("startup")
# async def startup_event():
#     if Config.WEB_HOOK_URL:
#         webhook_url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/setWebhook?url={Config.WEB_HOOK_URL}//mirror-bot"
#         async with httpx.AsyncClient() as client:
#             response = await client.get(webhook_url)
#             if response.status_code == 200:
#                 logger.info("Webhook registered successfully.")
#             else:
#                 logger.error(f"Failed to register webhook: {response.text}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.APP_HOST, port=Config.APP_PORT)