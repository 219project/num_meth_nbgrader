import numpy as np
import params
import pandas as pnd
#dt = np.dtype([('assignment_id', np.unicode_, 25), ('duedate_and_timestamp', np.unicode_, (2, 16)), ('student_id', np.unicode_, 25),  ('about', np.unicode_, (3, 16)), raw_score,late_submission_penalty,score,max_score('grades', np.float64, (2,))])
#dt = np.dtype([('%.25s'),'','','%.25s','%.2f','%.2f','%.2f','%.2f'])
#a = np.loadtxt('grades.csv', skiprows=1, dtype=dt)
#Список студентов сдавших задание
students = np.loadtxt('students.csv', dtype='str')
#Список студент:оценка(могут быть лишние студенты)
students_and_grades = pnd.read_csv('grades.csv')
students_and_grades = students_and_grades[students_and_grades['assignment']==params.assignment_name]
students_dict = pnd.Series(students_and_grades.raw_score.values, index=students_and_grades.student_id).to_dict()
print(students_dict)
