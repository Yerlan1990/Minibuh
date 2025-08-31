import os
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("BASE_URL","http://localhost:8000")
BOT_TOKEN = os.getenv("BOT_TOKEN","")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET","")
DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///data.db")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID","")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET","")
GOOGLE_REDIRECT_PATH = os.getenv("GOOGLE_REDIRECT_PATH","/auth/google/callback")

# Feature flags
USE_GOOGLE = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
