#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


import json
import os

from data_client.utils.file import get_all_file_abs_path

file_dict = get_all_file_abs_path(os.path.dirname(__file__))
def get_file_abs_path(file_name : str):
    return file_dict[file_name]

def get_dir() -> str:
    return os.path.abspath(os.path.dirname(__file__))

def get_json(file_name : str):
    with open(get_file_abs_path(file_name), 'r') as f:
        return json.load(f)