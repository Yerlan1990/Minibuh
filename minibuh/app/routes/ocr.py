from fastapi import APIRouter, UploadFile, File, HTTPException
from ..utils.ocr import extract_id_fields_from_pdf
import os, uuid

router = APIRouter(prefix="/ocr", tags=["OCR"])

@router.post("/id")
async def ocr_id(file: UploadFile = File(...)):
    os.makedirs("/mnt/data/uploads", exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1].lower() or ".pdf"
    path = f"/mnt/data/uploads/{uuid.uuid4().hex}{ext}"
    with open(path, "wb") as out:
        out.write(await file.read())
    if ext in [".pdf"]:
        data = extract_id_fields_from_pdf(path)
    else:
        data = {"fio":"", "iin":"", "dob":"", "expiry":"", "series":""}
    if not any(data.values()):
        raise HTTPException(422, "Не удалось распознать документ")
    return {"ok": True, "data": data, "path": path}
