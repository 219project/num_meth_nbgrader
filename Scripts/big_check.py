import logging
import io
import os
logging.basicConfig(filename='Scripts/log.txt', level=logging.DEBUG, filemode='w', format='%(asctime)s : %(levelname)s : %(message)s')

# скрипт для проверки заданий
from src.drive_api import Drive
from src.classroom_api import Classroom

from googleapiclient.http import MediaIoBaseDownload

print('Начинаем проверку заданий\n')


def download_from_assignment(course_name, task_name, service_mail, course_id, notebook_id):
    """
    скачивает все прикреплённые студентами задания
    в папку exchange/*course_id*/inbound
    с именем *notebook_id*_*префикс почты*.py

    :param course_name: название курса в классруме
    :param task_name: название задания в классруме
    :param service_mail: почта сервисного аккаунта в классруме
    :param course_id: для nbgrader: destination_path(это exchange/*course_id*/inbound)
    :param notebook_id: это часть файла *notebook_id*_pmvinetskaya.py
    """
    
    drive_service = Drive.create_service()
    classroom_service = Classroom.create_service()

    logging.debug(f'course_name: {course_name} \ntask_name: {task_name} \nservice_mail: {service_mail} \ncourse_id: {course_id} \nnotebook_id: {notebook_id}')

    course_id = Classroom.get_courses(classroom_service, course_name, service_mail)
    coursework_id = Classroom.get_coursework(classroom_service, task_name, course_id)
    submissions = Classroom.get_submissions(classroom_service, coursework_id, course_id)

    for s in submissions:

        request = drive_service.files().get_media(fileId=s.get('file_id'))
        user_name = s.get('user_email').split('@')[0]  # префикс почты студента
        logging.debug(f'we are here: {os.getcwd()}')

        if not os.path.isdir(f'../exchange/{course_id}/inbound'):
            os.makedirs(f'../exchange/{course_id}/inbound')
        filename = f'../exchange/{course_id}/inbound/{notebook_id}_{user_name}.{s.get("file_name").split(".")[-1]}'
        fh = io.FileIO(filename, mode='wb')
        MediaIoBaseDownload(fh, request)
        logging.debug(f'downloaded: {filename}')


download_from_assignment(course_name='лёша', task_name='test', service_mail='onlineeducation@miem.hse.ru', 
                         course_id='testcourse', notebook_id='testnotebook')