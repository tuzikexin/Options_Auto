from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path
import os
import zipfile

# The folder ID in the URL when open the folder in Google Drive; it's the string after folders/.
GOODLE_FOLD_ID = {"vix":"1LhowxgyWvOZlyVnRBDwPeoefyUHPjWZ0",
                  "spx":"1p-Et5f3o91EASW69Bks0sHXUflqEWcRq",
                  "test":"1QYWfVQbqGiohqp8bgtUEThdeiMG7xiLu"}

# Get the absolute path of the current file
root_path = Path(os.path.abspath(__file__)).parent.parent
credentials_path = Path(root_path, 'credentials/yaofugui_permission_service_account.json')

def compress_folder(directory, zip_name):
    # Ensure the parent directory of the zip file exists
    os.makedirs(os.path.dirname(zip_name), exist_ok=True)
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                if file == ".DS_Store":
                    continue
                file_path = os.path.join(root, file)
                # Calculate the relative archive path
                archive_path = os.path.relpath(file_path, os.path.join(directory, '..'))
                zipf.write(file_path, archive_path)


def create_service():
    credentials = Credentials.from_service_account_file(
       credentials_path, scopes=['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=credentials)
    return service


def upload_single_file_to_folder(filename, filepath,  ticker:str):
    service = create_service()
    folder_id = GOODLE_FOLD_ID[ticker.strip().lower()]
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    media = MediaFileUpload(filepath)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return None
