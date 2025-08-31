from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session
from ..config import BASE_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_PATH
from ..db import SessionLocal, User
import os

router = APIRouter(prefix="/auth/google", tags=["GoogleAuth"])

def flow_instance():
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "project_id": "minibuh",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uris": [BASE_URL + GOOGLE_REDIRECT_PATH],
        }
    }
    scopes = ["openid", "https://www.googleapis.com/auth/drive.file"]
    return Flow.from_client_config(client_config, scopes=scopes, redirect_uri=BASE_URL+GOOGLE_REDIRECT_PATH)

@router.get("")
def auth_start(telegram_id: str):
    flow = flow_instance()
    auth_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent")
    os.makedirs("/mnt/data/state", exist_ok=True)
    open(f"/mnt/data/state/{state}", "w").write(telegram_id)
    return RedirectResponse(auth_url)

@router.get("/callback")
def auth_callback(request: Request):
    state = request.query_params.get("state")
    if not state:
        raise HTTPException(400, "missing state")
    tg_id = open(f"/mnt/data/state/{state}").read().strip()
    flow = flow_instance()
    flow.fetch_token(authorization_response=str(request.url))
    creds: Credentials = flow.credentials
    os.makedirs("/mnt/data/google_creds", exist_ok=True)
    creds_path = f"/mnt/data/google_creds/{tg_id}.json"
    open(creds_path, "w").write(creds.to_json())

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=tg_id).first()
        if not user:
            user = User(telegram_id=tg_id, status="approved")
            db.add(user)
        user.google_connected = True
        db.commit()
    finally:
        db.close()
    return HTMLResponse("<h3>Google подключен. Вернитесь в Telegram.</h3>")
