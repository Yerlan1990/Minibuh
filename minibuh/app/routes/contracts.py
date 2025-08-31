from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db, User, CompanyProfile, Counterparty, Contract, DocumentFile
from ..schemas import ContractIn
from ..workflows.doc_flows import reserve_number
from ..google.docs_ops import render_docx_from_context
import os

router = APIRouter(prefix="/contracts", tags=["Contracts"])

@router.post("")
def create_contract(telegram_id: str, body: ContractIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user or user.status != "active":
        raise HTTPException(403, "not active")
    company = db.query(CompanyProfile).filter_by(id=body.company_id, user_id=user.id).first()
    cp = db.query(Counterparty).filter_by(id=body.counterparty_id, user_id=user.id).first()
    if not company or not cp:
        raise HTTPException(400, "bad company/counterparty")

    number = reserve_number(db, company.id, "contract") if body.reserve_number else ""
    c = Contract(user_id=user.id, company_id=company.id, counterparty_id=cp.id,
                 number=number, service_name=body.service_name, knp=body.knp,
                 vat_rate=body.vat_rate, amount=body.amount,
                 currency=body.currency, advance_percent=body.advance_percent)
    db.add(c); db.commit(); db.refresh(c)

    context = {"Договор №": c.number, "Исполнитель": company.name, "Заказчик": cp.name,
               "Услуга": c.service_name, "Сумма (тиын)": c.amount, "НДС %": c.vat_rate}
    payload = render_docx_from_context("Договор", context)
    out_dir = f"/mnt/data/docs/{telegram_id}/Contracts"
    os.makedirs(out_dir, exist_ok=True)
    file_path = f"{out_dir}/{c.number or 'contract'}.docx"
    open(file_path, "wb").write(payload)

    db.add(DocumentFile(user_id=user.id, doc_type="contract", entity_id=c.id, path=file_path))
    db.commit()
    return {"id": c.id, "number": c.number, "file": file_path}
