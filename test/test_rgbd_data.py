#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


import unittest
from test.test_data import rgbd_raw_data

import cv2
import numpy as np

from data_client.utils import parser


class TestRgbdData(unittest.TestCase):

    def test(self):
        bin_data = parser.parse_rgbd_raw_data(rgbd_raw_data.get_file_abs_path("000001.bin"))        
        self.assertTrue(np.all(bin_data.image == cv2.imread(rgbd_raw_data.get_file_abs_path("000001.jpg"))))
        self.assertTrue(np.all(bin_data.depth == cv2.imread(rgbd_raw_data.get_file_abs_path("000001.png"), cv2.IMREAD_UNCHANGED)))
      
        with open(rgbd_raw_data.get_file_abs_path("000001.txt")) as calib_file:
            extrinsics_vec = [float(st) for st in calib_file.readline().split(" ")]
            extrinsics_mat = np.array(extrinsics_vec).reshape((3,3)).T
            self.assertTrue(np.allclose(bin_data.extrinsics, extrinsics_mat))
            
            intrinsics_vec = [float(st) for st in calib_file.readline().split(" ")]
            intrinsics_mat = np.array(intrinsics_vec).reshape((3,3)).T
            self.assertTrue(np.allclose(bin_data.intrinsics, intrinsics_mat))

if __name__ == '__main__':
    unittest.main()
