from sqlalchemy.orm import Session
from ..db import Numerator
from datetime import datetime

def reserve_number(db: Session, company_id: int, doc_type: str, prefix: str = None) -> str:
    year = datetime.utcnow().year
    n = db.query(Numerator).filter_by(company_id=company_id, doc_type=doc_type, year=year).first()
    if not n:
        n = Numerator(user_id=None, company_id=company_id, doc_type=doc_type, prefix=(prefix or doc_type.upper()), year=year, counter=0)
        db.add(n); db.commit(); db.refresh(n)
    n.counter += 1
    db.commit()
    return f"{n.prefix}/{n.year}/{n.counter:05d}"
