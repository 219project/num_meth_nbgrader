#!/usr/bin/env python
# coding: utf-8

from time import gmtime, strftime
import os
import sys


### DEBUG only
DEBUG = False
if DEBUG:
    os.system = print


def make_timestamp(source_path):    
        timestamp = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime(os.path.getctime(source_path)))
        return timestamp
    
def move_assignment(source_path, destination_path):
    source_list = os.listdir(source_path)
    print('Found files:', len(source_list))
    
    benefit_dir = 0
    benefit_files = 0
    moved_files = {}
    
    for fname in source_list:
      
        print('File', fname, ':')
        
        
        assignment_id = os.path.basename(source_path)
        
        # separate format
        name, formatt = fname[:fname.rfind('.')], fname[fname.rfind('.'):].strip()
        
        if formatt != '.ipynb':
            print(formatt , 'is inappropriate format. Expected .ipynb')
            
        elif name.find('(')!=-1:
            print('It is not the last commit. Skipping this file')
        
        else:
            
            # separate notebook_id
            notebook_id, student_id = name[:name.find('_')], name[name.find('_')+1:]

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
                
            moved_files[student_id] = final_path
            
    print('Done')
    print('Made directories:', benefit_dir)
    print('Copied files:', benefit_files)
    
    return moved_files

if __name__ == "__main__":
    move_assignment(sys.argv[1], sys.argv[2])