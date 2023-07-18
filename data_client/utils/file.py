#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


import os
from typing import List

import psutil


def is_file_operated(file_path: str) -> bool:
    if not os.path.exists(file_path):
        return False
    for proc in psutil.process_iter():
        try:
            for file in proc.open_files():
                if file.path == file_path:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def get_files_with_suffix_recursive(dir_path: str, suffix: str) -> List[str]:
    files = []
    for root, dirs, file_names in os.walk(dir_path):
        for file_name in file_names:
            if file_name.endswith(suffix):
                files.append(os.path.join(root, file_name))
        for dir in dirs:
            files.extend(get_files_with_suffix_recursive(dir, suffix))
    return files

def get_files_recursive(dir_path: str) -> List[str]:
    return get_files_with_suffix_recursive(dir_path, "")

def get_all_file_abs_path(dir):
    file_list = os.listdir(os.path.abspath(dir))
    file_dict = {}
    root_path = os.path.abspath(dir)
    for file in file_list:
        file_dict[file] = os.path.join(root_path, file)
    return file_dict
