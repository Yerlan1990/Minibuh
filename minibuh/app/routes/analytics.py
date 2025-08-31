from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..db import get_db, Contract, Invoice, Act, TaxInvoice

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def summary(days: int = 30, db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=days)
    contracts = db.query(Contract).filter(Contract.created_at >= since).all()
    invoices = db.query(Invoice).filter(Invoice.created_at >= since).all()
    acts = db.query(Act).filter(Act.created_at >= since).all()
    tis = db.query(TaxInvoice).filter(TaxInvoice.created_at >= since).all()
    def total(items): return sum(x.amount for x in items)
    return {
        "period_days": days,
        "contracts_count": len(contracts), "contracts_sum": total(contracts),
        "invoices_count": len(invoices), "invoices_sum": total(invoices),
        "acts_count": len(acts), "acts_sum": total(acts),
        "tax_invoices_count": len(tis), "tax_invoices_sum": total(tis),
    }
