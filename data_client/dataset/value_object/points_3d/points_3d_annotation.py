#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


import io
from typing import List


class Points3DAnnotation:
    def __init__(self, anno_bytes: bytes, label_index : dict):
        str_io = io.TextIOWrapper(io.BytesIO(anno_bytes), encoding="utf-8")

        # Read a line of text from the BytesIO object.
        label_id_list = str_io.readlines()
        
        # int label value in [0, n), n is the total number of labels
        self.label = []
        for label_id in label_id_list:
            self.label.append(label_index[label_id.strip()])
            