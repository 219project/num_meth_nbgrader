"""
запускать из корня репозитория
"""

import logging
import io
import os
import subprocess
import numpy as np
import pandas as pnd

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
    :param assignment_id: эсайнмент: nb_course_id/feedback/префикс_почты/nb_assignment_id/файл.html
    :param notebook_id: это часть файла *notebook_id*_pmvinetskaya.ipynb
    """
    
    drive_service = Drive.create_service()
    classroom_service = Classroom.create_service()
    logging.info(f'1 этап: скачивание работ из Google Classroom \n{"-"*70}')
    logging.info(f'\ncourse_name: {course_name} \ntask_name: {task_name} \nservice_mail: {service_mail} \ncourse_id: {course_id} \nnotebook_id: {notebook_id}')

    classroom_course_id = Classroom.get_courses(classroom_service, course_name, service_mail)
    coursework_id = Classroom.get_coursework(classroom_service, task_name, classroom_course_id)
    logging.info(f'запрашиваем решения, ожидайте...')
    submissions = Classroom.get_submissions(classroom_service, coursework_id, classroom_course_id)

    logging.debug(f'we are here: {os.getcwd()}')

    soldiers = []
    benefit_dir = 0
    benefit_files = 0
    moved_files = {}
    students_list = []    
    
    logging.info(f'Будет загружено {len(submissions)} работ в папку \"exchange/{course_id}/inbound\"\n')

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

                if os.path.exists(filename):
                    logging.info(f'downloaded: {filename}')
                    moved_files[student_id] = filename
                    benefit_files += 1
                    students_list.append(student_id)
                else:
                    logging.warning(f'not downloaded: {filename}')
                    soldiers.append(student_id)


    logging.info(f'Made {benefit_dir} directories')
    logging.info(f'Copied {benefit_files} files')
    np.savetxt('Scripts/unknown_soldiers.csv', np.array(soldiers), fmt='%.20s')
    logging.info(f'Students: {np.array(students_list)}')
    np.savetxt('Scripts/students.csv', np.array(students_list),  fmt='%.20s')


def run_nbgrader(assignment_id, course_id):
    """
    команды для работы nbgrader


    :param course_id: название курса в nbgrader
    :param assignment_id: эсайнмент: nb_course_id/feedback/префикс_почты/nb_assignment_id/файл.html
    """

    logging.info(f'\n\n2 этап: проверка работ в nbgrader \n{"-"*70}')

    commands = [f"cd {course_id}; nbgrader generate_assignment {assignment_id}",
    f"cd {course_id}; nbgrader release_assignment {assignment_id}",
    f"cd {course_id}; nbgrader collect {assignment_id} # Теперь файлы студентов лежат в папке submitted",
    f"cd {course_id}; nbgrader autograde {assignment_id} # Процесс долгий, минут 10",
    f"cd {course_id}; nbgrader generate_feedback {assignment_id}",
    f"cd {course_id}; nbgrader export"    ]
    for i in commands:
        s = subprocess.run(i, shell=True, capture_output=True)
        logging.info(f"{i} \n{s.stderr.decode('ascii')}")




def send_feedback_to_classroom(course_classroom_name, task_classroom_name, service_mail, nb_course_id, nb_assignment_id, nb_notebook_id):
    """
    выгружает фидбеки и оценки в классрум
    из папки nb_course_id/feedback/префикс_почты/nb_assignment_id/файл.html
    к файлу студента

    :param course_classroom_name: название курса в классруме
    :param task_classroom_name: название задания в классруме
    :param service_mail: почта сервисного аккаунта в классруме
    :param nb_course_id: название курса в nbgrader
    :param nb_assignment_id: эсайнмент: nb_course_id/feedback/префикс_почты/nb_assignment_id/файл.html
    :param nb_notebook_id: название файла с фидбеком
    """

    logging.info(f'\n\n3 этап: загрузка фидбэка и оценки в Google Classroom \n{"-"*70}')

    grades_path = os.path.join(nb_course_id, 'grades.csv')  # путь к файлу с оценками
    students_downloaded = np.loadtxt('Scripts/students.csv', dtype='str')  # список студентов, сдавших задание
    logging.debug(f"студенты, сдавшие задание {nb_assignment_id}: \n{students}")

    p = pnd.read_csv(grades_path)
    s = p[p['assignment'] == nb_assignment_id]
    students_dict_score = pnd.Series(s.raw_score.values, index=s.student_id).to_dict()
    logging.debug(f"оценки за {nb_assignment_id}: \n{students_dict_score}")

    drive_service = Drive.create_service()
    classroom_service = Classroom.create_service()

    logging.info(f'course_name: {course_classroom_name} \ntask_name: {task_classroom_name} \nservice_mail: {service_mail} \ncourse_id: {nb_course_id} \nnotebook_id: {nb_assignment_id}')

    classroom_course_id = Classroom.get_courses(classroom_service, course_classroom_name, service_mail)
    classroom_coursework_id = Classroom.get_coursework(classroom_service, task_classroom_name, classroom_course_id)
    classroom_folder_id = Classroom.get_coursework_folder(classroom_service, classroom_course_id, classroom_coursework_id)
    logging.debug(f"все id: {classroom_course_id, classroom_coursework_id, classroom_coursework_id}")

    for student in students_downloaded:

        logging.info(f'Student: {student}')
        if student in students_dict_score.keys():
            print('Homework is found')
            submission_id = Classroom.get_student_submission(classroom_service, classroom_course_id, classroom_coursework_id, student+'@miem.hse.ru')
            if submission_id != 404:

                # загружаем файл на гугл диск
                feedback_path = os.path.join(nb_course_id, 'feedback', student, nb_assignment_id, nb_notebook_id)
                file_id = Drive.upload_html(drive_service, nb_assignment_id+'.html', feedback_path, classroom_folder_id)

                # прикрепляем файл в классрум
                Classroom.add_file(classroom_service, classroom_course_id, classroom_coursework_id, submission_id, file_id)

                # ставим оценку
                score = students_dict_score[student]
                Classroom.grade(classroom_service, classroom_course_id, classroom_coursework_id, submission_id, score)

                # возвращаем задание
                Classroom.return_submission(classroom_service, classroom_course_id, classroom_coursework_id, submission_id)

                logging.info(f'завершён студент: {student, file_id, score}')
