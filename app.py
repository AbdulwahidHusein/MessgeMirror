import os
import tracemalloc
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import admin, mirror_router, verification_roter
from config import Config
import logging
from fastapi.responses import JSONResponse

load_dotenv()

# Start memory tracking
tracemalloc.start()

app = FastAPI()

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(admin.router)
app.include_router(mirror_router.router)
app.include_router(verification_roter.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred. Please try again later."},
    )


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
