import os
import tracemalloc
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import admin, mirror_router, verification_router
from config import Config
import logging
from telegram import Bot
from fastapi.responses import JSONResponse

load_dotenv(override=True)



# Start memory tracking
tracemalloc.start()

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan function (setup and teardown)
async def lifespan(app: FastAPI):
    try: 
        if Config.MIRROR_ENABLED:
            # Initialize the mirror bot application
            await mirror_router.bot_app.initialize()
            await mirror_router.bot_app.bot.set_webhook(
                url=Config.MIRROR_WEB_HOOK_URI, 
                secret_token=Config.WEBHOOK_SECRET_TOKEN
            )
        
        if Config.VERIFICATION_ENABLED:
            # Initialize the verification bot application
            await verification_router.bot_app.initialize()
            await verification_router.bot_app.bot.set_webhook(
                url=Config.VERIFICATION_WEBHOOK_URI, 
                secret_token=Config.WEBHOOK_SECRET_TOKEN
            )
     
        logger.info("Bots initialized and webhooks set up successfully.")  
    except Exception as e:
        logger.error(f"Failed to initialize bots and set up webhooks: {e}") 
        raise
        
    yield
    
    # Cleanup on shutdown
    try:
        if Config.MIRROR_ENABLED:
            await mirror_router.bot_app.shutdown()
        if Config.VERIFICATION_ENABLED:
            await verification_router.bot_app.shutdown()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")  
          
    # yield
    # yield

app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin.router)

if Config.MIRROR_ENABLED:
    app.include_router(mirror_router.router)
if Config.VERIFICATION_ENABLED:
    app.include_router(verification_router.router)


@app.middleware("http")
async def verify_telegram_secret_token(request: Request, call_next):
    # Check if the request is targeting a Telegram webhook endpoint
    if request.url.path in ["/verification-bot", "/mirror-bot"]:
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        print("secret recieved: ",secret_token)
        
        # Validate the secret token
        if secret_token != Config.WEBHOOK_SECRET_TOKEN:
            logger.error(f"Unauthorized request: Invalid secret token")
            return JSONResponse(status_code=403, content={"detail": "Unauthorized request"})
     
    response = await call_next(request) 
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred. Please try again later."},
    )

# Log memory usage
def log_memory_usage():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")

    logger.info("[Top 10 Memory Usage]")
    for stat in top_stats[:10]:
        logger.info(stat)
 
 
if __name__ == "__main__": 
    import uvicorn 
    try:
        uvicorn.run(app, host=Config.APP_HOST, port=Config.APP_PORT)
    except Exception as e:
        logger.error(f"Error occurred while running the app: {e}")
    finally:
        log_memory_usage()