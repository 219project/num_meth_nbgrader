"""
запускать из корня репозитория
"""

import logging
import big_params

logging.basicConfig(filename='Scripts/log.txt', level=big_params.log_level, filemode='w', format='%(asctime)s : %(levelname)s : %(message)s')

import os
from big_check import download_from_assignment
from big_check import run_nbgrader
from big_check import send_feedback_to_classroom


print(os.getcwd())

download_from_assignment(course_name=big_params.course_classroom_name, 
                         task_name=big_params.task_classroom_name, 
                         service_mail=big_params.service_mail, 
                         course_id=big_params.course_id, 
                         notebook_id=big_params.notebook_id,
                         assignment_id=big_params.assignment_id)

run_nbgrader(assignment_id=big_params.assignment_id, 
             course_id=big_params.course_id)

send_feedback_to_classroom(course_classroom_name=big_params.course_classroom_name,
                           task_classroom_name=big_params.task_classroom_name,
                           service_mail=big_params.service_mail,
                           nb_course_id=big_params.course_id,
                           nb_assignment_id=big_params.assignment_id,
                           nb_notebook_id=big_params.notebook_id)
