from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def drive_service(creds: Credentials):
    return build("drive", "v3", credentials=creds, cache_discovery=False)

def docs_service(creds: Credentials):
    return build("docs", "v1", credentials=creds, cache_discovery=False)

def sheets_service(creds: Credentials):
    return build("sheets", "v4", credentials=creds, cache_discovery=False)
