#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

class CocoAnnotation:
    """coco data annotation of one instance on one raw data
    """
    def __init__(self, json_data, label_index):
        self.id = json_data["Id"]
        self.segmentation = json_data["Segmentation"]
        self.label_id = label_index[json_data["LabelId"]]
        self.is_crowd = json_data["IsCrowd"]
        self.num_key_points = json_data["NumKeyPoints"]
        self.key_points = json_data["KeyPoints"]
        self.bounding_box = json_data["Bbox"]
        self.area = json_data["Area"]
