import pickle, json, logging
import os.path
import os
import datetime
import time
import dateutil.parser
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from src.scopes import SCOPES

class Classroom:
    def create_service():  # service
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
        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        return service


    def get_courses(service, name, teacher_mail):  # course_id
        results = service.courses().list(teacherId = teacher_mail).execute()
        courses = results.get('courses', [])

        if not courses:
            print('No courses found.')
            return 404
        for course in courses:
            logging.debug(f"course found: {course['id'], course['name']}")
            if course['name'] == name:
                id = course['id']
                return id
        return 404

    
    def get_coursework(service, name, course_id):
        courseworks = service.courses().courseWork().list(courseId=course_id).execute().get('courseWork', [])
        for c in courseworks:
            logging.debug(f"coursework found: {c['id'], c['title']}")
            if name.casefold().strip() in c['title'].casefold().strip():
                return c['id']
        return 404

    
    def get_coursework_folder(service, course_id, coursework_id):
        coursework = service.courses().courseWork().get(courseId=course_id, id=coursework_id).execute()
        logging.debug(f"coursework: {coursework['id'], coursework['title']}")

        if coursework.get('assignment'):
            if coursework.get('assignment').get('studentWorkFolder'):
                logging.debug(f"folder: {coursework.get('assignment').get('studentWorkFolder')}")
                return coursework.get('assignment').get('studentWorkFolder').get('id')

        return 404

    def get_submissions(service, coursework_id, course_id):
        submissions = service.courses().courseWork().studentSubmissions().list(courseId=course_id, courseWorkId=coursework_id, states='TURNED_IN').execute()
        
        results = []
        
        for s in submissions.get('studentSubmissions', []):
            user_id = s.get('userId')
            user_email = service.userProfiles().get(userId=user_id).execute().get('emailAddress')
            submission_id = s.get('id')

            if s.get('submissionHistory'):
                for state in s.get('submissionHistory')[::-1]:
                    if state.get('stateHistory') and state.get('stateHistory').get('state') == 'TURNED_IN':
                        timestamp = state.get('stateHistory').get('stateTimestamp')
                        if timestamp:
                            timestamp = dateutil.parser.isoparse(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")

            if s.get('assignmentSubmission') and s.get('assignmentSubmission').get('attachments') and s.get('assignmentSubmission').get('attachments')[0].get('driveFile'):
                file = s.get('assignmentSubmission').get('attachments')[0].get('driveFile')
                file_id = file.get('id')
                file_name = file.get('title')
            
                logging.debug(f"submission: user_id {user_id}, user_email {user_email} id {submission_id}, file_id {file_id}, file_name {file_name}")
                
                results.append({
                    'user_id': user_id, 
                    'user_email': user_email,
                    'id': submission_id, 
                    'file_id': file_id, 
                    'file_name': file_name,
                    'timestamp': timestamp
                })
        return results


    def get_student_submission(service, course_id, coursework_id, user_id):
        """ Lists all student submissions for a given coursework. """

        response = service.courses().courseWork().studentSubmissions().list(
            courseId=course_id,
            courseWorkId=coursework_id,
            userId=user_id).execute()
        submissions = response.get('studentSubmissions', [])

        if not submissions:
            print('No student submissions found.')
            return 404

        if submissions[0]["state"] == "TURNED_IN":
            submission_id = submissions[0]['id']
            logging.debug(f'found submission: {submission_id}')
            return submission_id
        print('Error with submissions. Not turned in')
        return 404
            

    def add_file(service, course_id, coursework_id, submission_id, file_id):

        print('target: ', course_id, coursework_id, submission_id, file_id)
        request = {
            'addAttachments': [{"driveFile": {'id': file_id}}]
        }
        coursework = service.courses().courseWork()
        coursework.studentSubmissions().modifyAttachments(
            courseId=course_id,
            courseWorkId=coursework_id,
            id=submission_id,
            body=request).execute()


    def grade(service, course_id, coursework_id, submission_id, score):

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

        
    def return_submission(service, course_id, coursework_id, submission_id):

        print('target: ', course_id, coursework_id, submission_id)
        coursework = service.courses().courseWork()
        coursework.studentSubmissions().return_(
            courseId=course_id,
            courseWorkId=coursework_id,
            id=submission_id,
            body={}).execute()