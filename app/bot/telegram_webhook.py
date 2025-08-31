from fastapi import APIRouter, Request, HTTPException
from aiogram.types import Update
from ..config import WEBHOOK_SECRET
from .bot_main import bot, dp

router = APIRouter(tags=["Telegram"])

@router.post("/telegram/webhook/{secret}")
async def telegram_webhook(secret: str, request: Request):
    if secret != WEBHOOK_SECRET:
        raise HTTPException(403, "bad secret")
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@router.get("/telegram/ping")
def ping():
    return {"ok": True}
