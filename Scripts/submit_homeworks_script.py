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
        
        name, formatt = files.split('.')
        
        os.rename(sourse_path+ '/' +files, sourse_path+"/"+name.strip('\ ')+'.'+formatt)
        name = name.strip('\ ')
        
        notebook_id, student_id = name[:name.find('_')], name[name.find('_')+1:]
        
        initial_path = sourse_path + '/' + name + '.' + formatt
        timestamp = make_timestamp(initial_path)
        
        dir_name = destination_path + '/' + student_id + '+' + assignment_id + '+' + timestamp
        
        final_path = dir_name + '/' + notebook_id + '.' + formatt
        
        os.system('mkdir ' + '"' + dir_name + '"' )
        
        if os.path.exists(dir_name):
            benefit_dir+=1
        
        os.system('mv ' + initial_path + ' "' + final_path + '"')
        
        if os.path.exists(final_path):
            benefit_files+=1
    print('Made directories:', benefit_dir)
    print('Moved files:', benefit_files)
    

move_assignment(sys.argv[1], sys.argv[2])
