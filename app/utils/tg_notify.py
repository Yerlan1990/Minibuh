from aiogram import Bot
async def notify(bot: Bot, chat_id: int, text: str):
    await bot.send_message(chat_id, text)
