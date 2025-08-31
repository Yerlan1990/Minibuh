from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db, User, CompanyProfile, Counterparty, Contract, Invoice, DocumentFile
from ..schemas import InvoiceIn
from ..workflows.doc_flows import reserve_number
from ..google.docs_ops import render_docx_from_context
import os

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.post("")
def create_invoice(telegram_id: str, body: InvoiceIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user or user.status != "active":
        raise HTTPException(403, "not active")
    company = db.query(CompanyProfile).filter_by(id=body.company_id, user_id=user.id).first()
    cp = db.query(Counterparty).filter_by(id=body.counterparty_id, user_id=user.id).first()
    if not company or not cp:
        raise HTTPException(400, "bad company/counterparty")
    contract = db.query(Contract).filter_by(id=body.contract_id, user_id=user.id).first() if body.contract_id else None

    service_name = body.service_name or (contract.service_name if contract else "")
    amount = body.amount or (contract.amount if contract else 0)
    vat = body.vat_rate if body.vat_rate is not None else (contract.vat_rate if contract else 12)

    number = reserve_number(db, company.id, "invoice") if body.reserve_number else ""
    inv = Invoice(user_id=user.id, company_id=company.id, counterparty_id=cp.id,
                  contract_id=contract.id if contract else None, number=number,
                  service_name=service_name, knp=body.knp, vat_rate=vat, amount=amount, due_days=body.due_days)
    db.add(inv); db.commit(); db.refresh(inv)

    context = {"Счет №": inv.number, "Исполнитель": company.name, "Покупатель": cp.name,
               "Услуга": service_name, "Сумма (тиын)": amount, "НДС %": vat, "Срок оплаты (дн.)": inv.due_days}
    payload = render_docx_from_context("Счет на оплату", context)
    out_dir = f"/mnt/data/docs/{telegram_id}/Invoices"
    os.makedirs(out_dir, exist_ok=True)
    file_path = f"{out_dir}/{inv.number or 'invoice'}.docx"
    open(file_path, "wb").write(payload)

    db.add(DocumentFile(user_id=user.id, doc_type="invoice", entity_id=inv.id, path=file_path))
    db.commit()
    return {"id": inv.id, "number": inv.number, "file": file_path}
