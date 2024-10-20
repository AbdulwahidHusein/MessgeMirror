from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from config import Config
from mirror_bot.db.admindb import (
    add_username_to_admin_list, 
    remove_from_admin_list as remove_mirror_bot_admin
)
from verification_bot.database.admin_dao import (
    add_username_to_admin_list as add_verification_bot_admin,
    remove_from_admin_list as remove_verification_bot_admin
)

router = APIRouter()

# Mirror Bot Add Admin Form
@router.get("/add-mirrorbot-admin", response_class=HTMLResponse)
async def add_mirrorbot_admin_form():
    with open("templates/mirror_bot_admin.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Verification Bot Add Admin Form
@router.get("/add-verificationbot-admin", response_class=HTMLResponse)
async def add_verificationbot_admin_form():
    with open("templates/verification_bot_admin.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Add Admin to Mirror Bot
@router.post("/add-mirrorbot-admin")
async def handle_add_mirrorbot_admin(bot_token: str = Form(...), username: str = Form(...)):
    if bot_token == Config.MIRROR_BOT_TOKEN:
        message = add_username_to_admin_list(username)
        return {"message": message}
    return {"message": "Invalid bot token."}

# Add Admin to Verification Bot
@router.post("/add-verificationbot-admin")
async def handle_add_verificationbot_admin(bot_token: str = Form(...), username: str = Form(...)):
    if bot_token == Config.VERIFICATION_BOT_TOKEN:
        message = add_verification_bot_admin(username)
        return {"message": message}
    return {"message": "Invalid bot token."}

# Mirror Bot Delete Admin Form
@router.get("/delete-mirrorbot-admin", response_class=HTMLResponse)
async def delete_mirrorbot_admin_form():
    with open("templates/delete_mirror_bot_admin.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Verification Bot Delete Admin Form
@router.get("/delete-verificationbot-admin", response_class=HTMLResponse)
async def delete_verificationbot_admin_form():
    with open("templates/delete_verification_bot_admin.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Delete Admin from Mirror Bot
@router.post("/delete-mirrorbot-admin")
async def handle_delete_mirrorbot_admin(bot_token: str = Form(...), username: str = Form(...)):
    if bot_token == Config.MIRROR_BOT_TOKEN:
        success = remove_mirror_bot_admin(username)
        if success:
            return {"message": f"Username '{username}' deleted."}
        return {"message": f"Username '{username}' not found."}
    return {"message": "Invalid bot token."}

# Delete Admin from Verification Bot
@router.post("/delete-verificationbot-admin")
async def handle_delete_verificationbot_admin(bot_token: str = Form(...), username: str = Form(...)):
    if bot_token == Config.VERIFICATION_BOT_TOKEN:
        success = remove_verification_bot_admin(username)
        if success:
            return {"message": f"Username '{username}' deleted."}
        return {"message": f"Username '{username}' not found."}
    return {"message": "Invalid bot token."}
