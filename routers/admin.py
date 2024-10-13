from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from config import Config
from db.admindb import add_username_to_admin_list

router = APIRouter()

@router.get("/add-admin", response_class=HTMLResponse)
async def add_admin_form():
    with open("templates/add_admin_form.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@router.post("/add-admin")
async def handle_admin_form(bot_token: str = Form(...), username: str = Form(...)):
    if bot_token == Config.BOT_TOKEN:
        message = add_username_to_admin_list(username)
        return {"message": message}
    
    return {"message": "Invalid bot token."}