#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

import json


def write_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f)
