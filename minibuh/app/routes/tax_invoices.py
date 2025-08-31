from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db, User, CompanyProfile, Counterparty, Contract, Invoice, TaxInvoice, DocumentFile
from ..schemas import TaxInvoiceIn
from ..workflows.doc_flows import reserve_number
from ..google.docs_ops import render_docx_from_context
import os

router = APIRouter(prefix="/tax-invoices", tags=["TaxInvoices"])

@router.post("")
def create_tax_invoice(telegram_id: str, body: TaxInvoiceIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user or user.status != "active":
        raise HTTPException(403, "not active")
    company = db.query(CompanyProfile).filter_by(id=body.company_id, user_id=user.id).first()
    cp = db.query(Counterparty).filter_by(id=body.counterparty_id, user_id=user.id).first()
    contract = db.query(Contract).filter_by(id=body.contract_id, user_id=user.id).first() if body.contract_id else None
    inv = db.query(Invoice).filter_by(id=body.invoice_id, user_id=user.id).first() if body.invoice_id else None
    if not company or not cp:
        raise HTTPException(400, "bad company/counterparty")

    amount = body.amount or (inv.amount if inv else 0)
    vat = body.vat_rate or (inv.vat_rate if inv else 12)

    number = reserve_number(db, company.id, "tax_invoice") if body.reserve_number else ""
    ti = TaxInvoice(user_id=user.id, company_id=company.id, counterparty_id=cp.id,
                    contract_id=contract.id if contract else None,
                    invoice_id=inv.id if inv else None, number=number, amount=amount, vat_rate=vat)
    db.add(ti); db.commit(); db.refresh(ti)

    context = {"Счет-фактура №": ti.number, "Поставщик": company.name, "Покупатель": cp.name,
               "Сумма (тиын)": amount, "НДС %": vat}
    payload = render_docx_from_context("Счет-фактура", context)
    out_dir = f"/mnt/data/docs/{telegram_id}/TaxInvoices"
    os.makedirs(out_dir, exist_ok=True)
    file_path = f"{out_dir}/{ti.number or 'tax_invoice'}.docx"
    open(file_path, "wb").write(payload)

    db.add(DocumentFile(user_id=user.id, doc_type="tax_invoice", entity_id=ti.id, path=file_path))
    db.commit()
    return {"id": ti.id, "number": ti.number, "file": file_path}
