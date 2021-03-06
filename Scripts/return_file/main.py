from __future__ import print_function
import pickle
import os.path
import params
import pandas as pnd
import numpy as np

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
SCOPES = ['https://www.googleapis.com/auth/classroom.coursework.students', 
          'https://www.googleapis.com/auth/classroom.courses.readonly',
          'https://www.googleapis.com/auth/drive']

def create_services():
    """ Creates Google services for classroom and drive """
    creds = None
    print('--- log into google --- ')
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    classroom_service = build('classroom', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    print('Done \n')
    return classroom_service, drive_service


def get_courses(service, name, teacher_mail):  # course_id
    """ Find course ID """
    print('--- search course --- ')
    print('target: ', name, teacher_mail)
    results = service.courses().list(teacherId = teacher_mail).execute()
    courses = results.get('courses', [])

    if not courses:
        print('Error in finding courses. No courses found.')
        return 404
    else:
        for course in courses:
            print(course['id'], course['name'])
            if course['name'] == name:
                id = course['id']
                print('Done \n')
                return id
        print('Error in finding course. Course name invalid.')
        return 404


def get_coursework(service, course_id, name):  # coursework_id
    """ Find Assignment ID """
    print('--- Search assignment --- ')
    print('target: ', name, course_id)
    res = service.courses().courseWork().list(courseId=course_id).execute()
    cv = res.get('courseWork', [])
    if not cv:
        print('No coursework found.')
        return 404, None
    else:
        print('Courseworks:')
        #print(cv)
        for i in cv:
            if i['title'].casefold() == name.casefold():
                coursework_id = i['id']
                folder_id = i['assignment']['studentWorkFolder']['id']
                folder_link = i['assignment']['studentWorkFolder']['alternateLink']
                print(i['id'], i['title'], folder_link)
                print('Done \n')
                return coursework_id, folder_id
        print('No coursework found.')
        return 404, None


def get_submissions(service, course_id, coursework_id, user_id):  # submission_id
    """ Lists all student submissions for a given coursework. """
    print('--- Search submission --- ')
    print('target: ', course_id, coursework_id, user_id)
    submissions = []

    coursework = service.courses().courseWork()
    response = coursework.studentSubmissions().list(
        courseId=course_id,
        courseWorkId=coursework_id,
        userId=user_id).execute()
    submissions = response.get('studentSubmissions', [])

    if not submissions:
        print('No student submissions found.')
        return 404
    else:
        if submissions[0]["state"] == "TURNED_IN":
            print('Student submission:')
            # print(submissions)
            submission_id = submissions[0]['id']
            attachment = submissions[0]["assignmentSubmission"]["attachments"]
            print(submission_id, attachment)
            print('Done \n')
            return submission_id
        print('Error with submissions. Not turned in')
        return 404


def search_file(drive_service, name, folder):
    """ Search file in Drive folder """
    print('--- Search file ---')
    print('target: ', name, folder)
    response = drive_service.files().list(q=f"name = '{name}' and '{folder}' in parents",
                                          spaces='drive'
                                         ).execute()
    for file in response.get('files', []):
        # Process change
        print('Found file: ', file.get('name'), file.get('id'))
        print('Done \n')
        return file.get('id')
    print('Error. File not found. ')
    return 404


def add_file(service, course_id, coursework_id, submission_id, file_id):
    """ Attach file to assessment """
    print('--- Attach file ---')
    print('target: ', course_id, coursework_id, submission_id, file_id)
    request = {
        'addAttachments': [
            {"driveFile": {'id': file_id}}
        ]
    }
    coursework = service.courses().courseWork()
    coursework.studentSubmissions().modifyAttachments(
        courseId=course_id,
        courseWorkId=coursework_id,
        id=submission_id,
        body=request).execute()
    print('Done \n')
    return 0


def return_submission(service, course_id, coursework_id, submission_id):
    """ Attach file to assessment """
    print('--- Return submission ---')
    print('target: ', course_id, coursework_id, submission_id)

    coursework = service.courses().courseWork()
    coursework.studentSubmissions().return_(
        courseId=course_id,
        courseWorkId=coursework_id,
        id=submission_id,
        body={}).execute()

    print('Done \n')
    return 0


def grade(service, course_id, coursework_id, submission_id, score):
    """ ?????????????????????? ???????????? """
    print('--- Grade student ---')
    print('target: ', course_id, coursework_id, submission_id, score)
    studentSubmission = {
        'assignedGrade': score,
        'draftGrade': score
    }
    results = service.courses().courseWork().studentSubmissions().patch(
        courseId=course_id,
        courseWorkId=coursework_id,
        id=submission_id,
        updateMask='assignedGrade,draftGrade',
        body=studentSubmission).execute()

    print('Done \n')
    return 0 


# -----------

service, drive_service = create_services()
# ???????? ????????
course_id = get_courses(service, params.course_name, params.teacher_mail)
# ???????? assignment ?? id ?????????? ?? ??????????????
coursework_id, folder_id = get_coursework(service, course_id, params.assignment_name)


if coursework_id != 404 and folder_id is not None:
    # ???????? ???????????? ????????????????

    #???????????? ?????????????????? ?????????????? ??????????????
    students = np.loadtxt('students.csv', dtype='str')
    #???????????? ??????????????:????????????(?????????? ???????? ???????????? ????????????????)
    students_and_grades = pnd.read_csv('grades.csv')
    students_and_grades = students_and_grades[students_and_grades['assignment']==params.grade_name]
    students_dict = pnd.Series(students_and_grades.raw_score.values, index=students_and_grades.student_id).to_dict()
    print(students_dict)
    

    for student in students:
        print('Student', student)
        if student in students_dict.keys():
            print('Homework is found')
            submission_id = get_submissions(service, course_id, coursework_id, student+'@miem.hse.ru')

            if submission_id != 404:
                # ?????????? ???????????????? ?????????? ???????????????? ?? ??????????-?????????? 
                student_file = params.grade_name+'_'+student+'.ipynb'
                grade_file = params.grade_name+'_'+student+'.html'
                print('Here', drive_service, student_file, folder_id)
                if search_file(drive_service, student_file, folder_id) != 404:
                    print('Student file found. Attaching grade file... \n')
                    # ???????? id ??????????-??????????
                    grade_file_id = search_file(drive_service, grade_file, folder_id)

                    if grade_file_id != 404:
                        # ?????????????????? ??????????-????????
                        add_file(service, course_id, coursework_id, submission_id, grade_file_id)

                        # ???????????? ????????????!!!
                        score = students_dict[student] # ???????? ?????????? ???? ??????????????, ???????? ???????? 10
                        grade(service, course_id, coursework_id, submission_id, score)

                        # ???????????????????? ??????????????
                        return_submission(service, course_id, coursework_id, submission_id)
                        print('Done. \n')

                    else:
                        print('Error. Grade file not found. \n')
                else:
                    print('Error. Student file not found. ')
            else:
                print('Error. Student submission not found. ')
        else:
            print('Homework is not found')
else:
    print('Error. Assignment name invalid or folder not found.  \n')


input("Press any key to continue...")

    








