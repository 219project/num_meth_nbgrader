"""
Модуль используется для взаимодействия с Google Drive
"""

import pickle, json, logging, random
import os.path
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

from src.scopes import SCOPES

class Drive:
    """
    класс содержит методы для работы с Google Drive
    """
    def create_service():  # service
        """
        Метод создаёт сервис drive -- объект, через который осуществляется взаимодействие.
        Для этого пользователь должен авторизоваться в Google от лица необходимого аккаунта.

        :return: функция возвращает сервис drive
        """
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

    
    def upload_html(service, file_name, file_path, folder_id):
        """
        Метод загружает файл с фидбэком в папку на Google Drive

        :param service: classroom сервис
        :param file_name: имя создаваемого файла
        :type file_name: str
        :param file_path: путь к файлу
        :type file_path: str
        :param folder_id: id папки, в которую загружается файл
        :type folder_id: str
        :return: функция возвращает id файла
        :rtype: str
        """
    
        media = MediaFileUpload(file_path, mimetype='text/html')
        file = service.files().create(
            body={
                'name': file_name, 
                'parents': [folder_id]
                },
                media_body=media,
                fields='id').execute()
        file_id = file.get('id')
        return file_id