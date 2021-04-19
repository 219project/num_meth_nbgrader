#!/usr/bin/env python
# coding: utf-8

from time import gmtime, strftime
import os
import sys
import numpy as np

### DEBUG only
DEBUG = False
if DEBUG:
    os.system = print


def make_timestamp(source_path):    
        timestamp = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime(os.path.getctime(source_path)))
        return timestamp
    
def move_assignment(source_path, destination_path, notebook_id):
    #Making log file
    os.system('touch unknown_soldiers.csv')
    soldiers = []
    
    source_list = os.listdir(source_path)
    print('Found files:', len(source_list))
    
    
    benefit_dir = 0
    benefit_files = 0
    moved_files = {}
    students_list = []

    for fname in source_list:
      
        print('File', fname, ':')
        
        
        assignment_id = os.path.basename(source_path)
        
        # separate format
        name, formatt = fname[:fname.rfind('.')], fname[fname.rfind('.'):].strip()
        
        # separate notebook_id
        student_id = name[name.rfind(notebook_id+'_')+len(notebook_id)+1:]
        
        if formatt != '.ipynb':
            print(formatt , 'is inappropriate format. Expected .ipynb')
            print('File', fname, "caused problems and wasn't copied")
            soldiers.append(student_id)
            
        elif name.find('(')!=-1:
            print('It is not the last commit. Skipping this file')
        
        else:
            students_list.append(student_id)
            print('name', name, 'notebook_id', notebook_id, 'student_id', student_id)
            initial_path = os.path.join(source_path, fname)
            timestamp = make_timestamp(initial_path)

            dir_name = os.path.join(destination_path, student_id + '+' + notebook_id + '+' + timestamp)

            final_path = os.path.join(dir_name, notebook_id + formatt)

            os.system('mkdir ' + '"' + dir_name + '"' )

            if os.path.exists(dir_name):
                print('Made directory', dir_name)
                benefit_dir+=1

            os.system('cp ' + initial_path.replace(' ', '\ ') + ' "' + final_path + '"')
            
            if os.path.exists(final_path):
                print('File', fname, 'successfully copied to', final_path)
                benefit_files+=1
            else:
                print('File', fname, "caused problems and wasn't copied")
                soldiers.append(student_id)
                
                
            moved_files[student_id] = final_path
            
    print('Done')
    print('Made directories:', benefit_dir)
    print('Copied files:', benefit_files)
    np.savetxt('unknown_soldiers.csv', np.array(soldiers), fmt='%.20s')
    print('Students:' , np.array(students_list))
    np.savetxt('students.csv', np.array(students_list),  fmt='%.20s')
    return moved_files

if __name__ == "__main__":
    move_assignment(sys.argv[1], sys.argv[2], sys.argv[3])
