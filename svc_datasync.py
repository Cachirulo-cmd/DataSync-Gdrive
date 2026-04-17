import os
import shutil
import hashlib
import logging
import socket

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# =============================================================================
# CONFIGURACIÓN — Rellena estos valores antes de ejecutar el script
# Sigue los pasos del README.md para obtener cada uno
# =============================================================================

# ID de la carpeta de Google Drive donde se subirán los backups
# Obtenerlo desde la URL: drive.google.com/drive/folders/<FOLDER_ID>
DRIVE_FOLDER_ID = "TU_FOLDER_ID_AQUI"

# Valores obtenidos al ejecutar obtener_token.py
CLIENT_ID     = "TU_CLIENT_ID_AQUI"
CLIENT_SECRET = "TU_CLIENT_SECRET_AQUI"
REFRESH_TOKEN = "TU_REFRESH_TOKEN_AQUI"

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# =============================================================================

logging.basicConfig(
    filename='sync_service.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_credentials():
    """Genera credenciales OAuth2 a partir del refresh token embebido."""
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES
    )
    # Refresca el access token automáticamente
    creds.refresh(Request())
    return creds

def calculate_checksum(file_path):
    """Genera un hash SHA-256 para verificar la integridad del paquete."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def upload_to_drive(archive_path):
    """Sube el archivo zip a Google Drive usando OAuth2."""
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': os.path.basename(archive_path),
        'parents': [DRIVE_FOLDER_ID]
    }

    media = MediaFileUpload(archive_path, mimetype='application/zip', resumable=True)

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name'
    ).execute()

    return uploaded.get('id'), uploaded.get('name')

def execute_sync():
    home_dir = os.path.expanduser('~')
    source_folder = os.path.join(home_dir, 'Documents')

    hostname = socket.gethostname()
    local_archive = f"backup_{hostname}_delta"

    archive_path = None
    try:
        logging.info(f"Iniciando backup desde: {source_folder}")
        archive_path = shutil.make_archive(local_archive, 'zip', source_folder)
        file_size = os.path.getsize(archive_path)
        file_hash = calculate_checksum(archive_path)
        logging.info(f"Paquete creado: {os.path.basename(archive_path)} ({file_size} bytes) | SHA-256: {file_hash}")

        logging.info("Subiendo a Google Drive...")
        file_id, file_name = upload_to_drive(archive_path)
        logging.info(f"Subida exitosa: '{file_name}' (ID: {file_id})")

        os.remove(archive_path)
        logging.info("Archivo local eliminado. Sincronización completada.")

    except Exception as e:
        logging.error(f"Fallo en el ciclo de sincronización: {str(e)}")
    finally:
        if archive_path and os.path.exists(archive_path):
            try:
                os.remove(archive_path)
            except Exception:
                pass

if __name__ == "__main__":
    execute_sync()
