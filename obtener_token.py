from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.file']

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',  # El archivo JSON descargado de Google Cloud Console
    SCOPES
)

creds = flow.run_local_server(port=0)

print("\n========== COPIA ESTOS VALORES EN svc_datasync.py ==========\n")
print(f"REFRESH TOKEN : {creds.refresh_token}")
print(f"CLIENT ID     : {creds.client_id}")
print(f"CLIENT SECRET : {creds.client_secret}")
print("\n=============================================================\n")
