#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import os
import sys

def restructure(source_path, final_path, submission):
    source_list = os.listdir(source_path)
    print('Found folders:', len(source_list))
    benefit_files = 0
    for file_name in source_list:
        print('Student_id', file_name, ':')
        initial_path = os.path.join(source_path, file_name, submission, submission + '.html')
        print(initial_path)
        if os.path.exists(initial_path):
            print('Feedback is found')
            final_file_path = os.path.join(final_path, submission + '_' + file_name + '.html')       
            os.system('cp ' + initial_path + ' ' + final_file_path)
            if os.path.exists(os.path.join(final_file_path)):
                benefit_files += 1
        else:
            print('Feedback is not found')
        
    print(benefit_files, 'files were moved successfully')
    
if __name__ == "__main__":
    restructure(sys.argv[1], sys.argv[2], sys.argv[3])
    
