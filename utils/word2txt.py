#!/usr/bin/env python
import pypandoc
import os

for path, dir_list, file_list in os.walk('data/raw/baker'):
    for file_name in file_list:
        if '.docx' in file_name:
            nlist = file_name.split('.')
            out_name = nlist[-1]
            pypandoc.convert_file(os.path.join(
                path, file_name), 'textile', 'docx', outputfile='data/raw/cases/'+out_name+'.txt')
