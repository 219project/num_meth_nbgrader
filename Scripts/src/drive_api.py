import pickle, json, logging, random
import os.path
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from src.scopes import SCOPES

class Drive:
    def create_service():  # service
        cwd = os.getcwd()
        print(cwd)
        creds = None
        if os.path.exists('Scripts/src/tocken.pickle'):
            with open('Scripts/src/tocken.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('Scripts/src/credentials.json', SCOPES)
                creds = flow.run_local_server()  # or run_console()
            with open('Scripts/src/tocken.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('drive', 'v3', credentials=creds, cache_discovery=False)
        return service


    def find_and_copy(name, parent_folder, service):
        logging.info(f'in classroom_class:find_and_copy - find {name}')
        files = service.files().list(q=f"name = '{name}' and '{parent_folder}' in parents").execute().get('files', [])
        logging.info(f'in classroom_class:find_and_copy - got {files}')
        file_id = files[0].get('id')
        copy_file_id = service.files().copy(fileId=file_id, body={'name': f'{name.split(".")[0]}{random.randint(1, 10000)}.{name.split(".")[1]}'}).execute().get('id', [])
        logging.info(f'in classroom_class:find_and_copy - copied {copy_file_id}')
        return copy_file_id
