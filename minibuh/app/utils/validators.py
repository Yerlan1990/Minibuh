import re
def validate_phone_kz(raw: str) -> bool:
    return bool(re.fullmatch(r"\d{10}", raw))
def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10: return digits
    if len(digits) == 11 and digits.startswith(("7","8")): return digits[1:]
    return digits
def validate_tax_id(raw: str) -> bool:
    return bool(re.fullmatch(r"\d{12}", raw))
