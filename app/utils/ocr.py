import pdfplumber
from typing import Dict

def extract_id_fields_from_pdf(path: str) -> Dict[str, str]:
    data = {"fio":"", "iin":"", "dob":"", "expiry":"", "series":""}
    try:
        with pdfplumber.open(path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        import re
        fio = re.search(r"ФИО[:\s]+(.+)", text)
        if fio: data["fio"] = fio.group(1).strip()
        iin = re.search(r"ИИН[:\s]+(\d{12})", text)
        if iin: data["iin"] = iin.group(1)
    except Exception:
        pass
    return data
