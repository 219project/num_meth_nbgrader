#!/usr/bin/env python
# coding: utf-8

from time import gmtime, strftime
import os
import sys

def make_timestamp(sourse_path):    
        timestamp = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime(os.path.getctime(sourse_path)))
        return timestamp
    
def move_assignment(sourse_path, destination_path):
    source_list = os.listdir(sourse_path)
    print('Found files:', len(source_list))
    
    benefit_dir = 0
    benefit_files = 0
    
    for files in source_list:
        
        assignment_id = os.path.basename(sourse_path)
        
        name, formatt = files.__repr__()[1:-1].split('.')
        
        notebook_id, exercise, student_id = name.split('_')
        
        initial_path = sourse_path + '/' + files.__repr__()[1:-1]
        timestamp = make_timestamp(initial_path)
        
        dir_name = destination_path + '/' + student_id + '+' + assignment_id + '+' + timestamp
        newname = ''.join(name.split('_' + student_id))
        final_path = dir_name + '/' + newname + '.' + formatt
        
        os.system('mkdir ' + '"' + dir_name + '"' )
        
        if os.path.exists(dir_name):
            benefit_dir+=1
    
        os.system('mv ' + initial_path + ' "' + final_path + '"')
        
        if os.path.exists(final_path):
            benefit_files+=1
    print('Made directories:', benefit_dir)
    print('Moved files:', benefit_files)
    

move_assignment(sys.argv[1], sys.argv[2])