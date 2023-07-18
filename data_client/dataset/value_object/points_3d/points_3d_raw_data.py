#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


from RawData.Points3D.Points3D import Points3D


class Points3DRawData:
    def __init__(self, raw_data_fb : Points3D):
        self.pos = []
        for i in range(raw_data_fb.PosLength()):
            self.pos.append([raw_data_fb.Pos(i).X(), raw_data_fb.Pos(i).Y(), raw_data_fb.Pos(i).Z()])
        self.rgb = []
        for i in range(raw_data_fb.RgbLength()):
            self.rgb.append([raw_data_fb.Rgb(i).R(), raw_data_fb.Rgb(i).G(), raw_data_fb.Rgb(i).B()])
        
        self.xmin = raw_data_fb.Xmin()
        self.xmax = raw_data_fb.Xmax()
        self.ymin = raw_data_fb.Ymin()
        self.ymax = raw_data_fb.Ymax()
        self.zmin = raw_data_fb.Zmin()
        self.zmax = raw_data_fb.Zmax()
        self.rmean = raw_data_fb.Rmean()
        self.gmean = raw_data_fb.Gmean()
        self.bmean = raw_data_fb.Bmean()
        self.rstd = raw_data_fb.Rstd()
        self.gstd = raw_data_fb.Gstd()
        self.bstd = raw_data_fb.Bstd()
        self.size = len(self.pos)
        
        