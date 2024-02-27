from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path
import os
import zipfile

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

def upload_single_file_to_folder(filename, filepath,  folder_id='1LhowxgyWvOZlyVnRBDwPeoefyUHPjWZ0'):
    service = create_service()
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    media = MediaFileUpload(filepath)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

def upload_file_to_google(directory_to_zip):    
    # Compressed file 
    folder_name = os.path.basename(directory_to_zip)
    zip_file_name = f'{folder_name}.zip'
    zip_file_path = Path(str(Path(directory_to_zip).parent), zip_file_name)
    compress_folder(directory_to_zip, zip_file_path)

    # The folder ID in the URL when open the folder in Google Drive; it's the string after folders/.
    drive_folder_id = '1LhowxgyWvOZlyVnRBDwPeoefyUHPjWZ0'

    # Then, upload the ZIP file
    upload_single_file_to_folder(zip_file_name, zip_file_path, drive_folder_id)

# def test():
#     p = Path('/Users/kexin/Desktop/xiaoyu/app/data/raw_data/20240226')
#     upload_file_to_google(p)
