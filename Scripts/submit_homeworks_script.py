#!/usr/bin/env python
# coding: utf-8

from time import gmtime, strftime
import os
import sys

def make_timestamp(source_path):    
        timestamp = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime(os.path.getctime(source_path)))
        return timestamp
    
def move_assignment(source_path, destination_path):
    source_list = os.listdir(source_path)
    print('Found files:', len(source_list))
    
    benefit_dir = 0
    benefit_files = 0
    
    for file in source_list:
        print('File', file, ':')
        assignment_id = os.path.basename(source_path)
        
        name, formatt = file[:file.rfind('.')], file[file.rfind('.')+1:]#separate format
        
        if formatt != 'ipynb':
            print(formatt , 'is inappropriate format. Expected .ipynb')
            
        elif name.find('(')!=-1:
            print('It is not the last commit. Skipping this file')
        
        else:
            os.rename(source_path+ '/' +file, source_path+"/"+name.strip('\ ')+'.'+formatt)#delete spases in the end
            name = name.strip('\ ')

            notebook_id, student_id = name[:name.find('_')], name[name.find('_')+1:]#separate notebook_id

            initial_path = source_path + '/' + name + '.' + formatt
            timestamp = make_timestamp(initial_path)

            dir_name = destination_path + '/' + student_id + '+' + assignment_id + '+' + timestamp

            final_path = dir_name + '/' + notebook_id + '.' + formatt

            os.system('mkdir ' + '"' + dir_name + '"' )

            if os.path.exists(dir_name):
                print('Made directory', dir_name)
                benefit_dir+=1

            os.system('mv ' + initial_path + ' "' + final_path + '"')

            if os.path.exists(final_path):
                print('File', file, 'successfully moved to', final_path)
                benefit_files+=1
    print('Done')
    print('Made directories:', benefit_dir)
    print('Moved files:', benefit_files)
    

move_assignment(sys.argv[1], sys.argv[2])
