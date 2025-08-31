from typing import Dict
from google.oauth2.credentials import Credentials
from .services import drive_service

FOLDER_MIME = "application/vnd.google-apps.folder"

def _ensure_folder(svc, name: str, parent_id: str=None) -> str:
    q = f"mimeType='{FOLDER_MIME}' and name='{name}' and trashed=false"
    if parent_id:
        q += f" and '{parent_id}' in parents"
    res = svc.files().list(q=q, fields="files(id,name)").execute()
    if res.get("files"):
        return res["files"][0]["id"]
    body = {"name": name, "mimeType": FOLDER_MIME}
    if parent_id:
        body["parents"] = [parent_id]
    created = svc.files().create(body=body, fields="id").execute()
    return created["id"]

def ensure_user_structure(creds_json_path: str, fio: str) -> Dict[str, str]:
    creds = Credentials.from_authorized_user_file(creds_json_path, scopes=["https://www.googleapis.com/auth/drive.file"])
    svc = drive_service(creds)
    root = _ensure_folder(svc, "MiniBuh")
    user_root = _ensure_folder(svc, f"Users_{fio}", root)
    folders = {
        "ID": _ensure_folder(svc, "ID", user_root),
        "Contracts": _ensure_folder(svc, "Contracts", user_root),
        "Invoices": _ensure_folder(svc, "Invoices", user_root),
        "Acts": _ensure_folder(svc, "Acts", user_root),
        "TaxInvoices": _ensure_folder(svc, "TaxInvoices", user_root),
        "Counterparty": _ensure_folder(svc, "Counterparties", user_root),
        "Uploads": _ensure_folder(svc, "Uploads", user_root),
    }
    folders["__root__"] = user_root
    return folders
