#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

import cv2


class ImageRawData:
    def __init__(self, id: str, data: cv2.Mat):
        self.id = id
        # read by cv2
        self.data = data
