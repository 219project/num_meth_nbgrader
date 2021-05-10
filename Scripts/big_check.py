import logging
import io
logging.basicConfig(filename='Scripts/log.txt', level=logging.DEBUG, filemode='w', format='%(asctime)s : %(levelname)s : %(message)s')

# скрипт для проверки заданий
from src.drive_api import Drive
from src.classroom_api import Classroom

from googleapiclient.http import MediaIoBaseDownload

print('Начинаем проверку заданий\n')


# надо скачать папку с гугл-диска
def download_folder():
    drive_service = Drive.create_service()
    classroom_service = Classroom.create_service()

    course_name = 'лёша'#input('Введите название курса: ')
    logging.debug(course_name)
    course_id = Classroom.get_courses(classroom_service, course_name, 'onlineeducation@miem.hse.ru')

    task_name = 'test'#input('Введите название задания: ')
    logging.debug(task_name)
    coursework_id = Classroom.get_coursework(classroom_service, task_name, course_id)
    
    submissions = Classroom.get_submissions(classroom_service, coursework_id, course_id)

    for s in submissions:

        request = drive_service.files().get_media(fileId=s.get('file_id'))
        user_name = s.get('user_email').split('@')[0]
        fh = io.FileIO(f'Scripts/output/{user_name}.{s.get("file_name").split(".")[-1]}', mode='wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))


download_folder()