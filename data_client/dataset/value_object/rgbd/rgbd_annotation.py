#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


class RgbdAnnotation:
    def __init__(self, json_data : dict, label_index : dict):
        self.label_id = label_index[json_data["LabelId"]]
        self.bounding_box_2d = [
            json_data["BoundingBox2D"]["X"],
            json_data["BoundingBox2D"]["Y"],
            json_data["BoundingBox2D"]["Width"],
            json_data["BoundingBox2D"]["Height"]
        ]
        self.bounding_box_3d = [
            json_data["BoundingBox3D"]["X"],
            json_data["BoundingBox3D"]["Y"],
            json_data["BoundingBox3D"]["Z"],
            json_data["BoundingBox3D"]["XSize"],
            json_data["BoundingBox3D"]["YSize"],
            json_data["BoundingBox3D"]["ZSize"],
            json_data["BoundingBox3D"]["YawX"],
            json_data["BoundingBox3D"]["YawY"],
            json_data["BoundingBox3D"]["YawZ"]
        ]
        