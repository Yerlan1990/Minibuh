from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Регистрация"), KeyboardButton(text="Профиль")],
        [KeyboardButton(text="Сканировать счёт"), KeyboardButton(text="Помощь")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def google_auth_kb(base_url: str, tg_id: str):
    url = f"{base_url}/auth/google?telegram_id={tg_id}"
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Войти с Google", url=url)]])

def back_home_cancel():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("⬅️ Назад"), KeyboardButton("🏠 Домой"), KeyboardButton("✖️ Отмена"))
    return kb
