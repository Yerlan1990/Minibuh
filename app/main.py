from fastapi import FastAPI
from .db import init_db
from .google.oauth import router as google_auth_router
from .routes.profile import router as profile_router
from .routes.companies import router as companies_router
from .routes.counterparties import router as counterparties_router
from .routes.contracts import router as contracts_router
from .routes.invoices import router as invoices_router
from .routes.acts import router as acts_router
from .routes.tax_invoices import router as tax_invoices_router
from .routes.documents import router as documents_router
from .routes.analytics import router as analytics_router
from .routes.settings import router as settings_router
from .routes.ocr import router as ocr_router
from .bot.telegram_webhook import router as tg_router

app = FastAPI(title="MiniBuh")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(google_auth_router)
app.include_router(profile_router)
app.include_router(companies_router)
app.include_router(counterparties_router)
app.include_router(contracts_router)
app.include_router(invoices_router)
app.include_router(acts_router)
app.include_router(tax_invoices_router)
app.include_router(documents_router)
import os
from fastapi import FastAPI

app = FastAPI(title="Minibuh API")

# Подключаем Telegram только если есть токен
if os.getenv("BOT_TOKEN"):
    from .bot.telegram_webhook import router as tg_router
    app.include_router(tg_router, prefix="/telegram")
else:
    print("BOT_TOKEN is not set – Telegram router disabled", flush=True)

@app.get("/")
def health():
    return {"ok": True, "service": "minibuh"}



app.include_router(analytics_router)
app.include_router(settings_router)
app.include_router(ocr_router)
app.include_router(tg_router)
