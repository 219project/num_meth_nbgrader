"""
запускать из корня репозитория
"""

import logging
import io
import os
import subprocess
import numpy as np
logging.basicConfig(filename='Scripts/log.txt', level=logging.INFO, filemode='w', format='%(asctime)s : %(levelname)s : %(message)s')

from src.drive_api import Drive
from src.classroom_api import Classroom
from googleapiclient.http import MediaIoBaseDownload

logging.info('Начинаем проверку заданий\n')


def download_from_assignment(course_name, task_name, service_mail, course_id, assignment_id, notebook_id):
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

    logging.info(f'course_name: {course_name} \ntask_name: {task_name} \nservice_mail: {service_mail} \ncourse_id: {course_id} \nnotebook_id: {notebook_id}')

    classroom_course_id = Classroom.get_courses(classroom_service, course_name, service_mail)
    coursework_id = Classroom.get_coursework(classroom_service, task_name, classroom_course_id)
    submissions = Classroom.get_submissions(classroom_service, coursework_id, classroom_course_id)

    logging.debug(f'we are here: {os.getcwd()}')

    soldiers = []
    benefit_dir = 0
    benefit_files = 0
    moved_files = {}
    students_list = []    

    for s in submissions:

        if not s.get('timestamp'):
            logging.warning(f'no history: {s}')
        elif not s.get('user_email') or '@' not in s.get('user_email'):
            logging.warning(f'invalid mail: {s}')
        elif not s.get('file_id'):
            logging.warning(f'invalid file: {s}')
        else:
            file_extension = s.get("file_name").split(".")[-1]
            student_id = s.get('user_email').split('@')[0]  # префикс почты студента
            
            if file_extension != 'ipynb':  # extension
                logging.warning(f'invalid extension {s.get("file_name").split(".")[-1]}, expected .ipynb: {s}')
                soldiers.append(student_id)

            else:
                request = drive_service.files().get_media(fileId=s.get('file_id'))

                dir_name = f'exchange/{course_id}/inbound/{student_id}+{assignment_id}+{s.get("timestamp")}'
                if not os.path.isdir(dir_name):
                    os.makedirs(dir_name)
                    benefit_dir += 1

                filename = os.path.join(dir_name, f'{notebook_id}.{file_extension}')
                fh = open(filename, mode='wb')
                downloader = MediaIoBaseDownload(fh, request)

                done = False
                while done is False:
                    done = downloader.next_chunk()
                    print('Downloaded')

                if os.path.exists(filename):
                    logging.info(f'downloaded: {filename}')
                    moved_files[student_id] = filename
                    benefit_files += 1
                    students_list.append(student_id)
                else:
                    logging.warning(f'not downloaded: {filename}')
                    soldiers.append(student_id)

        break

    logging.info(f'Made {benefit_dir} directories')
    logging.info(f'Copied {benefit_files} files')
    np.savetxt('Scripts/unknown_soldiers.csv', np.array(soldiers), fmt='%.20s')
    logging.info(f'Students: {np.array(students_list)}')
    np.savetxt('Scripts/students.csv', np.array(students_list),  fmt='%.20s')


def run_nbgrader(assignment_id, course_id):
    commands = [f"cd {course_id}; nbgrader generate_assignment {assignment_id}",
    f"cd {course_id}; nbgrader release_assignment {assignment_id}",
    f"cd {course_id}; nbgrader collect {assignment_id} # Теперь файлы студентов лежат в папке submitted",
    f"cd {course_id}; nbgrader autograde {assignment_id} # Процесс долгий, минут 10",
    f"cd {course_id}; nbgrader generate_feedback {assignment_id}"]
    for i in commands:
        s = subprocess.run(i, shell=True, capture_output=True)
        logging.info(f"{i} \n{s.stderr.decode('ascii')}")

# download_from_assignment(course_name='Численные методы 2020-2021', 
                        #  task_name='Задание А 10 : автопроверка [ode_ivp]', 
                        #  service_mail='pmvinetskaya@miem.hse.ru', 
                        #  course_id='TestCourse1', 
                        #  notebook_id='newton_iter')

run_nbgrader('ODE_IVP', 'TestCourse')
