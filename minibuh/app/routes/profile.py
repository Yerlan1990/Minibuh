from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from ..db import get_db, User
from ..utils.validators import validate_phone_kz, normalize_phone
from ..google.drive_ops import ensure_user_structure
import os

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.post("/register")
def register(telegram_id: str = Form(...), fio: str = Form(""), phone: str = Form(""), db: Session = Depends(get_db)):
    phone_norm = normalize_phone(phone) if phone else None
    if phone and not validate_phone_kz(phone_norm):
        raise HTTPException(400, "phone invalid, use 10 digits like 701XXXXXXX")
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, name=fio, phone=phone_norm, status="pending")
        db.add(user); db.commit()
    else:
        if fio: user.name = fio
        if phone_norm: user.phone = phone_norm
        db.commit()
    return {"ok": True, "status": user.status}

@router.post("/moderate")
def moderate(telegram_id: str, approve: bool, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user: raise HTTPException(404, "user not found")
    user.status = "approved" if approve else "rejected"
    db.commit()
    return {"ok": True, "status": user.status}

@router.post("/activate")
def activate(telegram_id: str, fio: str, db: Session = Depends(get_db)):
    # Создать структуру на Google после OAuth
    creds_path = f"/mnt/data/google_creds/{telegram_id}.json"
    if not os.path.exists(creds_path):
        raise HTTPException(400, "Google not connected")
    ensure_user_structure(creds_path, fio or "User")
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user: raise HTTPException(404, "user not found")
    user.status = "active"
    db.commit()
    return {"ok": True, "status": user.status}
