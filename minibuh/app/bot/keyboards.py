from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🧾 Регистрация / Профиль"))
    kb.row(KeyboardButton("📝 Создать договор"), KeyboardButton("📄 Счёт на оплату"))
    kb.row(KeyboardButton("🧾 АВР и АОУ"), KeyboardButton("📑 Счёт-фактура"))
    kb.row(KeyboardButton("📂 Просмотреть документы"), KeyboardButton("📊 Аналитика"))
    kb.row(KeyboardButton("⚙️ Настройки"), KeyboardButton("🚪 Выйти"))
    return kb

def google_auth_kb(base_url: str, tg_id: str):
    url = f"{base_url}/auth/google?telegram_id={tg_id}"
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Войти с Google", url=url)]])

def back_home_cancel():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("⬅️ Назад"), KeyboardButton("🏠 Домой"), KeyboardButton("✖️ Отмена"))
    return kb
