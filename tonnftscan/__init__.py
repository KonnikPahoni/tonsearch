import json

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from tonnftscan.settings import FIREBASE_CREDENTIALS

service_account_creds = ServiceAccountCredentials.from_json_keyfile_dict(
    keyfile_dict=json.loads(FIREBASE_CREDENTIALS), scopes=["https://www.googleapis.com/auth/webmasters"]
)

searchconsole = build("searchconsole", "v1", credentials=service_account_creds)
