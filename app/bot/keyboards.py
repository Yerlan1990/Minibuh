# app/bot/keyboards.py
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)

def main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="📄 Загрузить счёт-фактуру")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="❓ Помощь")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True
    )

def inline_example() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть", callback_data="open")],
    ])

def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
