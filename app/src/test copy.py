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

def create_service():
    # Get the absolute path of the current file
    root_path = Path(os.path.abspath(__file__)).parent.parent
    credentials_path = Path(root_path, 'credentials/yaofugui_permission_service_account.json')
    credentials = Credentials.from_service_account_file(
       credentials_path, 
       scopes=['https://www.googleapis.com/auth/drive'])
    
    # import httplib2
    # import googleapiclient.discovery
    # proxy_info = httplib2.ProxyInfo(proxy_type=httplib2.socks.PROXY_TYPE_HTTP, proxy_host="127.0.0.1", proxy_port=51743)
    # http = httplib2.Http(timeout=10, proxy_info=proxy_info, disable_ssl_certificate_validation=False)

    service = build('drive', 'v3', credentials=credentials)
    return service

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

def upload_single_file_to_folder(filename, filepath,  ticker:str):
    service = create_service()
    folder_id = GOODLE_FOLD_ID[ticker.strip().lower()]
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    media = MediaFileUpload(filepath)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return None

def create_folder(folder_name, parent_folder_id=None):
    """Create a folder in Google Drive and return its ID."""
    folder_metadata = {
        'name': folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        'parents': [parent_folder_id] if parent_folder_id else []
    }
    drive_service = create_service()
    created_folder = drive_service.files().create(
        body=folder_metadata,
        fields='id'
    ).execute()

    print(f'Created Folder ID: {created_folder["id"]}')
    return created_folder["id"]


create_folder('sdf')

# upload_single_file_to_folder('VIX_opt_2024-05-23 09-04-42.zip',
#                              '/Users/kexin/workspace/yaofugui/Options_Auto/data/raw_data/20240523/VIX_opt_2024-05-23 09-04-42.zip',
#                              'test')







# ================
# import io
# import os
# import pickle
# import shutil
# from mimetypes import MimeTypes

# import requests
# from google.auth.transport.requests import Request
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
# from pathlib import Path

# class Drive:
#     SCOPES = ["https://www.googleapis.com/auth/drive"]
#     root_path = Path(os.path.abspath(__file__)).parent.parent
#     credentials_path = Path(root_path, 'credentials/client_secret_option_upload_web_client_1.apps.googleusercontent.com.json')
    
#     def __init__(self):
#         self.creds = None
#         print(self.credentials_path)

#         if os.path.exists("token.pickle"):
#             with open("token.pickle", "rb") as token:
#                 self.creds = pickle.load(token)
#         if not self.creds or not self.creds.valid:
#             if self.creds and self.creds.expired and self.creds.refresh_token:
#                 self.creds.refresh(Request())
#             else:
#                 flow = InstalledAppFlow.from_client_secrets_file(
#                     self.credentials_path, self.SCOPES
#                 )
#                 self.creds = flow.run_local_server(host="127.0.0.1", port=8000)
#             with open("token.pickle", "wb") as token:
#                 pickle.dump(self.creds, token)
#         self.service = build("drive", "v3", credentials=self.creds)
#         results = (
#             self.service.files()
#             .list(
#                 pageSize=100,
#                 fields="files(id, name)",
#             )
#             .execute()
#         )
#         items = results.get("files", [])

#         print("Here's a list of files: \n")
#         print(*items, sep="\n", end="\n\n")

#     def download(self, file_id, file_name):
#         request = self.service.files().get_media(fileId=file_id)
#         fh = io.BytesIO()

#         downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
#         done = False

#         try:
#             while not done:
#                 status, done = downloader.next_chunk()

#             fh.seek(0)

#             with open(file_name, "wb") as f:
#                 shutil.copyfileobj(fh, f)

#             print("File Downloaded")
#             return True
#         except:
#             print("Something went wrong.")
#             return False

#     def upload(self, filepath):
#         name = filepath.split("/")[-1]
#         mimetype = MimeTypes().guess_type(name)[0]

#         file_metadata = {"name": name}

#         try:
#             media = MediaFileUpload(filepath, mimetype=mimetype)

#             file = (
#                 self.service.files()
#                 .create(body=file_metadata, media_body=media, fields="id")
#                 .execute()
#             )

#             print("File Uploaded.")

#         except:
#             raise UploadError("Can't Upload File.")
        

# d = Drive()
