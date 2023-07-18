#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


import unittest
from test.test_data import points_3d_data

from data_client.utils import parser


class TestPoints3dData(unittest.TestCase):

    def test(self):
        bin_data = parser.parse_points_3d_raw_data(points_3d_data.get_file_abs_path("test.bin"))
        self.assertEqual(bin_data.pos, [[1.628999948501587, 1.9670000076293945, 0.017000000923871994], [1.6330000162124634, 1.8389999866485596, 0.01899999938905239], [1.6039999723434448, 1.86899995803833, 0.017999999225139618]])
        self.assertEqual(bin_data.xmin, 1.6039999723434448)
        self.assertEqual(bin_data.xmax, 1.6330000162124634)
        self.assertEqual(bin_data.ymin, 1.8389999866485596)
        self.assertEqual(bin_data.ymax, 1.9670000076293945)
        self.assertEqual(bin_data.zmin, 0.017000000923871994)
        self.assertEqual(bin_data.zmax, 0.01899999938905239)
        self.assertEqual(bin_data.rmean, 118.33333587646484)
        self.assertEqual(bin_data.gmean, 130.0)
        self.assertEqual(bin_data.bmean, 126.0)
        self.assertEqual(bin_data.rstd, 0.9428090453147888)
        self.assertEqual(bin_data.gstd, 1.4142135381698608)
        self.assertEqual(bin_data.bstd, 1.4142135381698608)
        self.assertEqual(bin_data.size, 3)
        
        anno_data = parser.parse_points_3d_annotation(points_3d_data.get_file_abs_path("annotation"), {'d08bf87b-32b7-4d00-b3f5-f32556e76269' : 0, '240f550a-bf60-4a56-ab5d-92c5050717e3' : 1})
        self.assertEqual(anno_data.label, [0, 0, 1])

if __name__ == '__main__':
    unittest.main()
