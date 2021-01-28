# сервисный аккаунт, который будет осуществлять действия в аккаунте
# credentials.json аккаунта должны лежать рядом со скриптом
teacher_mail = 'pmvinetskaya@miem.hse.ru'

# название курса как в классруме 
course_name = 'TestCourse'

# название задания в классруме
# внимание!!! задание должно быть создано с помощью файла make_assignment.py
assignment_name = 'Hello'

# здесь что-то типа почты ученика
student_mail = 'eburovskiy@miem.hse.ru'

# префикс в названии файла hw1-asshadrunov.ipynb
grade_name = 'hello'

# паттерны
student_file = f"hello_{student_mail.split(r'@')[0]}.pdf"
grade_file = f"hello_{student_mail.split(r'@')[0]}_graded.html"


