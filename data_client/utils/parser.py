#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

import json
import os
import zlib
from cgi import parse_header
from email.parser import BytesParser
from io import BytesIO
from typing import List

from data_client.dataset.value_object.coco.coco_annotation import \
    CocoAnnotation
from data_client.dataset.value_object.points_3d.points_3d_annotation import \
    Points3DAnnotation
from data_client.dataset.value_object.points_3d.points_3d_raw_data import \
    Points3DRawData
from data_client.dataset.value_object.rgbd.rgbd_annotation import \
    RgbdAnnotation
from data_client.dataset.value_object.rgbd.rgbd_raw_data import RgbdRawData
from data_client.utils import const
from RawData.Points3D.Points3D import Points3D
from RawData.Rgbd.RgbdData import RgbdData

# annotation --------------------------------------------------------------

def parse_coco_annotation(filepath : str, label_index : dict) -> List[CocoAnnotation]:
    res = []
    with open(filepath, 'r') as file:
        json_data = json.load(file)["AnnoData"]
        for data in json_data:
            res.append(CocoAnnotation(json_data=data, label_index=label_index))
    return res


def parse_rgbd_annotation(filepath: str, label_index : dict) -> List[RgbdAnnotation]:
    res = []
    with open(filepath, 'r') as file:
        json_data = json.load(file)["BoundingBoxList"]
        for data in json_data:
            res.append(RgbdAnnotation(json_data=data, label_index=label_index))
    return res

def parse_points_3d_annotation(filepath: str, label_index : dict) -> Points3DAnnotation:
     with open(filepath, 'rb') as file:
        compressed_data = file.read()
        uncompressed_data = zlib.decompress(compressed_data)
        return Points3DAnnotation(uncompressed_data, label_index)

# raw data --------------------------------------------------------------

def parse_rgbd_raw_data(filepath: str) -> RgbdRawData:
    with open(filepath, 'rb') as file:
        buf = file.read()
        rgbdData = RgbdData.GetRootAsRgbdData(buf, 0)
        return RgbdRawData(rgbdData)
    
def parse_points_3d_raw_data(filepath: str) -> Points3DRawData:
    with open(filepath, 'rb') as file:
        buf = file.read()
        points3dData = Points3D.GetRootAsPoints3D(buf, 0)
        return Points3DRawData(points3dData)
    
def parse_multipart_form_data(request, boundary):
    content = request.body
    headers = f"Content-Type: multipart/form-data; boundary={boundary}\r\n\r\n"
    message = BytesParser().parse(BytesIO(headers.encode() + content))

    files = {}
    for part in message.walk():
        if part.get_content_maintype() == "multipart":
            continue

        # Get the content-disposition header and parse it
        header = part.get("Content-Disposition")
        _, params = parse_header(header)

        # Get the field name and value
        field_name = params.get("name")
        field_value = part.get_payload(decode=True)
        
        filename = params.get("filename")
        file_data = {
            "filename": filename,
            "content": field_value,
            "content_type": part.get_content_type(),
        }

        if field_name in files:
            files[field_name].append(file_data)
        else:
            files[field_name] = [file_data]

    return files

def parse_raw_data_locations(locations, raw_data_dir):
    raw_data_list = []
    for location in locations[const.DATA_ITEMS].value:
        raw_data_info = {}
        raw_data_info[const.DATA_ITEM_ID] = location[const.DATA_ITEM_ID]
        raw_data_info[const.OBJECT_KEY] = location[const.OBJECT_KEY]
        file_name = location[const.DATA_ITEM_ID] + os.path.splitext(location[const.DATA_NAME])[1]
        raw_data_info[const.LOCAL_PATH] = os.path.join(raw_data_dir, file_name)
        
        raw_data_list.append(raw_data_info)
    return raw_data_list