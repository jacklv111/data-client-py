#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

import os

file_list = os.listdir(os.path.abspath(os.path.dirname(__file__)))
file_dict = {}
root_path = os.path.abspath(os.path.dirname(__file__))
for file in file_list:
    file_dict[file] = os.path.join(root_path, file)

def get_file_abs_path(file_name : str):
    return file_dict[file_name]
