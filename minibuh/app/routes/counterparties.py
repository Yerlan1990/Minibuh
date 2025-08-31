from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db, Counterparty, User
from ..schemas import CounterpartyIn

router = APIRouter(prefix="/counterparties", tags=["Counterparties"])

@router.post("")
def add_counterparty(telegram_id: str, body: CounterpartyIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user: raise HTTPException(404, "user not found")
    c = Counterparty(user_id=user.id, **body.model_dump())
    db.add(c); db.commit(); db.refresh(c)
    return {"id": c.id}

@router.get("")
def list_counterparties(telegram_id: str, q: str = "", db: Session = Depends(get_db)):
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user: raise HTTPException(404, "user not found")
    import sqlalchemy as sa
    qry = db.query(Counterparty).filter_by(user_id=user.id)
    if q:
        qry = qry.filter(sa.func.lower(Counterparty.name).like(f"%{q.lower()}%"))
    items = qry.order_by(Counterparty.name).all()
    return [{"id":x.id,"name":x.name,"tax_id":x.tax_id} for x in items]
