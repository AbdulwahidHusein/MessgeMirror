from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from config import Config
from mirror_bot.db.admindb import add_username_to_admin_list
from verification_bot.database.admin_dao import add_username_to_admin_list as add_verification_bot_admin
router = APIRouter()

@router.get("/add-morrorbot-admin", response_class=HTMLResponse)
async def add_admin_form():
    with open("templates/mirror_bot_admin.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@router.get("/add-verification_bot-admin", response_class=HTMLResponse)
async def add_admin_form():
    with open("templates/verification_bot_admin.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@router.post("/add-morrorbot-admin")
async def handle_admin_form(bot_token: str = Form(...), username: str = Form(...)):
    if bot_token == Config.MIRROR_BOT_TOKEN:
        message = add_username_to_admin_list(username)
        return {"message": message}
    
    return {"message": "Invalid bot token."}

@router.post("/add-verification_bot-admin")
async def handle_admin_form(bot_token: str = Form(...), username: str = Form(...)):
    if bot_token == Config.VERIFICATION_BOT_TOKEN:
        message = add_verification_bot_admin(username)
        return {"message": message}
    
    return {"message": "Invalid bot token."}