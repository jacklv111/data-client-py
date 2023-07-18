#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


import cv2
import numpy as np

from RawData.Rgbd.RgbdData import RgbdData


class RgbdRawData:
    def __init__(self, raw_data_fb : RgbdData):
        self.image = cv2.imdecode(raw_data_fb.ImageAsNumpy(), cv2.IMREAD_COLOR)
        self.depth = cv2.imdecode(raw_data_fb.DepthAsNumpy(), cv2.IMREAD_UNCHANGED)
        calib = raw_data_fb.Calib()
        extrinsics_vec = np.array([calib.Extrinsics(i) for i in range (0, 9)])
        intrinsics_vec = np.array([calib.Intrinsics(i) for i in range (0, 9)])
        self.extrinsics = extrinsics_vec.reshape((3,3)).T
        self.intrinsics = intrinsics_vec.reshape((3,3)).T
