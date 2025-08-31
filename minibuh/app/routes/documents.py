from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db, DocumentFile

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("")
def list_docs(doc_type: str | None = None, db: Session = Depends(get_db)):
    items = db.query(DocumentFile).all()
    if doc_type: items = [x for x in items if x.doc_type == doc_type]
    return [{"type":x.doc_type, "entity_id":x.entity_id, "path":x.path, "drive":x.drive_id} for x in items]
