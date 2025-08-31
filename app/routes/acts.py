from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db, User, CompanyProfile, Counterparty, Contract, Act, DocumentFile
from ..schemas import ActIn
from ..workflows.doc_flows import reserve_number
from ..google.docs_ops import render_docx_from_context
import os

router = APIRouter(prefix="/acts", tags=["Acts"])

@router.post("")
def create_act(telegram_id: str, body: ActIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user or user.status != "active":
        raise HTTPException(403, "not active")
    company = db.query(CompanyProfile).filter_by(id=body.company_id, user_id=user.id).first()
    cp = db.query(Counterparty).filter_by(id=body.counterparty_id, user_id=user.id).first()
    contract = db.query(Contract).filter_by(id=body.contract_id, user_id=user.id).first()
    if not all([company, cp, contract]):
        raise HTTPException(400, "bad company/counterparty/contract")

    number = reserve_number(db, company.id, "act") if body.reserve_number else ""
    act = Act(user_id=user.id, company_id=company.id, counterparty_id=cp.id,
              contract_id=contract.id, number=number, amount=body.amount, period=body.period)
    db.add(act); db.commit(); db.refresh(act)

    context = {"Акт №": act.number, "Исполнитель": company.name, "Заказчик": cp.name,
               "Сумма (тиын)": act.amount, "Период": act.period}
    payload = render_docx_from_context("Акт выполненных работ", context)
    out_dir = f"/mnt/data/docs/{telegram_id}/Acts"
    os.makedirs(out_dir, exist_ok=True)
    file_path = f"{out_dir}/{act.number or 'act'}.docx"
    open(file_path, "wb").write(payload)

    db.add(DocumentFile(user_id=user.id, doc_type="act", entity_id=act.id, path=file_path))
    db.commit()
    return {"id": act.id, "number": act.number, "file": file_path}
