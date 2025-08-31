from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db, CompanyProfile, User
from ..schemas import CompanyIn

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("")
def add_company(telegram_id: str, body: CompanyIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user: raise HTTPException(404, "user not found")
    p = CompanyProfile(user_id=user.id, **body.model_dump())
    if not db.query(CompanyProfile).filter_by(user_id=user.id).first():
        p.is_default = True
    db.add(p); db.commit(); db.refresh(p)
    return {"id": p.id}

@router.get("")
def list_companies(telegram_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user: raise HTTPException(404, "user not found")
    items = db.query(CompanyProfile).filter_by(user_id=user.id).all()
    return [{"id":x.id,"name":x.name,"is_default":x.is_default} for x in items]
