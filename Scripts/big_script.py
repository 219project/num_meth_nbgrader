from big_check import download_from_assignment
from big_check import run_nbgrader


import Scripts.big_params as big_params





download_from_assignment(course_name=big_params.course_name, 
                         task_name=big_params.task_classroom_name, 
                         service_mail=big_params.service_mail, 
                         course_id=big_params.course_id, 
                         notebook_id=big_params.notebook_id,
                         assignment_id=big_params.assignment_id)

run_nbgrader(assignment_id = big_params.assignment_id, course_id=big_params.course_id )

