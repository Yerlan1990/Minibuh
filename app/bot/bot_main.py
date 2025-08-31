import os
import httpx
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.client.session.aiohttp import AiohttpSession

from ..config import BOT_TOKEN, BASE_URL
from .keyboards import main_menu, google_auth_kb, back_home_cancel

router = Router(name="minibuh")

class RegStates(StatesGroup):
    waiting_id = State()
    waiting_phone = State()

class ContractStates(StatesGroup):
    company = State()
    counterparty = State()
    service = State()
    vat = State()
    amount = State()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Добро пожаловать в Мини Бухгалтерию!", reply_markup=main_menu())

@router.message(F.text == "🏠 Домой")
async def home(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu())

@router.message(F.text == "✖️ Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено. Что дальше?", reply_markup=main_menu())

@router.message(F.text == "🧾 Регистрация / Профиль")
async def profile_gate(message: Message, state: FSMContext):
    tg_id = str(message.from_user.id)
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as c:
        r = await c.post("/profile/register", data={"telegram_id": tg_id, "fio": message.from_user.full_name})
        status = r.json().get("status", "pending")
    if status != "active":
        await message.answer("Регистрация: шаг 1 — пришлите PDF удостоверения личности.", reply_markup=back_home_cancel())
        await state.set_state(RegStates.waiting_id)
    else:
        await message.answer("Профиль активен ✅", reply_markup=main_menu())

@router.message(RegStates.waiting_id, F.document)
async def handle_id_doc(message: Message, state: FSMContext):
    if not message.document.file_name.lower().endswith(".pdf"):
        await message.answer("Пожалуйста, пришлите PDF.")
        return
    file_info = await message.bot.get_file(message.document.file_id)
    file_bytes = await message.bot.download_file(file_info.file_path)
    import tempfile
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(file_bytes.read()); tmp.close()

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as c:
        with open(tmp.name, "rb") as f:
            r = await c.post("/ocr/id", files={"file": ("id.pdf", f, "application/pdf")})
    if r.status_code >= 400:
        await message.answer("Не удалось распознать. Попробуйте еще раз.")
        return
    await message.answer("Шаг 2 — отправьте номер телефона БЕЗ +7 и БЕЗ 8, ровно 10 цифр (например 701XXXXXXX).")
    await state.set_state(RegStates.waiting_phone)

@router.message(RegStates.waiting_phone, F.text.regexp(r"^\d{10}$"))
async def handle_phone(message: Message, state: FSMContext):
    phone = message.text
    tg_id = str(message.from_user.id)
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as c:
        await c.post("/profile/register", data={"telegram_id": tg_id, "phone": phone})
        await c.post("/profile/moderate", params={"telegram_id": tg_id, "approve": True})
    await message.answer("Регистрация одобрена ✅ Подключите Google Drive:", reply_markup=google_auth_kb(BASE_URL, tg_id))

@router.message(F.text == "📝 Создать договор")
async def create_contract_start(message: Message, state: FSMContext):
    await message.answer("Введите ИД компании-исполнителя (или 0 — если по умолчанию).", reply_markup=back_home_cancel())
    await state.set_state(ContractStates.company)

@router.message(ContractStates.company, F.text.regexp(r"^\d+$"))
async def step_company(message: Message, state: FSMContext):
    await state.update_data(company_id=int(message.text))
    await message.answer("Введите ИД контрагента.")
    await state.set_state(ContractStates.counterparty)

@router.message(ContractStates.counterparty, F.text.regexp(r"^\d+$"))
async def step_counterparty(message: Message, state: FSMContext):
    await state.update_data(counterparty_id=int(message.text))
    await message.answer("Введите наименование услуги.")
    await state.set_state(ContractStates.service)

@router.message(ContractStates.service)
async def step_service(message: Message, state: FSMContext):
    await state.update_data(service_name=message.text)
    await message.answer("Введите ставку НДС (например 12).")
    await state.set_state(ContractStates.vat)

@router.message(ContractStates.vat, F.text.regexp(r"^\d+$"))
async def step_vat(message: Message, state: FSMContext):
    await state.update_data(vat_rate=int(message.text))
    await message.answer("Введите сумму в тиынах (целое число).")
    await state.set_state(ContractStates.amount)

@router.message(ContractStates.amount, F.text.regexp(r"^\d+$"))
async def step_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    data["amount"] = int(message.text)
    tg_id = str(message.from_user.id)
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as c:
        r = await c.post("/contracts", params={"telegram_id": tg_id}, json={
            "company_id": data["company_id"],
            "counterparty_id": data["counterparty_id"],
            "service_name": data["service_name"],
            "vat_rate": data["vat_rate"],
            "amount": data["amount"],
            "currency": "KZT",
            "advance_percent": 0,
            "reserve_number": True
        })
    if r.status_code >= 400:
        await message.answer(f"Ошибка: {r.text}")
    else:
        res = r.json()
        await message.answer(f"Готово. Договор № {res.get('number')} создан. Файл: {res.get('file')}")
    await state.clear()
    await message.answer("Что дальше?", reply_markup=main_menu())

session = AiohttpSession()
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()
dp.include_router(router)

import os
from aiogram import Bot
from aiohttp import ClientSession

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
if not BOT_TOKEN or ":" not in BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing or invalid. Set it in Railway → Variables.")

session = ClientSession()
bot = Bot(token=BOT_TOKEN, session=session)

