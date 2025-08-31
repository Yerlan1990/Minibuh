from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db, Numerator, ServiceCatalog, User

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.post("/numerator")
def set_numerator(telegram_id: str, company_id: int, doc_type: str, prefix: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user: return {"ok": False, "error": "user not found"}
    n = db.query(Numerator).filter_by(company_id=company_id, doc_type=doc_type, year=0).first()
    if not n:
        n = Numerator(user_id=user.id, company_id=company_id, doc_type=doc_type, prefix=prefix, year=0, counter=0)
        db.add(n)
    else:
        n.prefix = prefix
    db.commit()
    return {"ok": True}

@router.post("/services")
def add_service(telegram_id: str, name: str, knp: str | None = None, default_price: int = 0, quick: bool=False, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user: return {"ok": False, "error": "user not found"}
    svc = ServiceCatalog(user_id=user.id, name=name, knp=knp, default_price=default_price, is_quick=quick)
    db.add(svc); db.commit()
    return {"id": svc.id}

@router.get("/services")
def list_services(telegram_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    items = db.query(ServiceCatalog).filter_by(user_id=user.id, is_active=True).all()
    return [{"id":x.id,"name":x.name,"knp":x.knp,"default_price":x.default_price,"quick":x.is_quick} for x in items]
