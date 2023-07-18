#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

import time


class const(object):
    class ConstError(TypeError): 
        pass
    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__.keys():
            raise self.ConstError("can't change const.%s" % name)
        if not name.isupper():
            raise self.ConstCaseError("const name '%s' is not all uppercase" % name)

        self.__dict__[name] = value

import sys

sys.modules[__name__] = const()

# timeout
const.FILE_NOT_EXISTS_TIMEOUT = 60 * 10
const.FILE_BEING_OPERATED_TIMEOUT = 60 * 30

# model worker --------------------------------------------------------------------
const.MAX_WORKERS = 4

# config file name
const.CONFIG_FILE = "config.ini"

# retry config --------------------------------------------------------------------
const.STOP_AFTER_ATTEMPT_TIMES = 100
const.STOP_AFTER_DELAY_IN_S = 3600
const.MIN_BACKOFF_IN_S = 5
const.MAX_BACKOFF_IN_S = 60

# dataset const --------------------------------------------------------------------
# work directory
const.DEFAULT_DATASET_DIR = "./dataset"

# data view type
const.RAW_DATA = "raw-data"
const.ANNOTATION = "annotation"
const.MODEL = "model"
const.DATASET_ZIP = "dataset-zip"
const.ARTIFACT = "artifact"

# field name
const.ID = "id"
const.DATA_ITEMS = "data_items"
const.DATA_ITEM_ID = "data_item_id"
const.OBJECT_KEY = "object_key"
const.DATA_NAME = "data_name"
const.LOCAL_PATH = "local_path"
const.ANNO_TEMP_ID = "annotation_template_id"
const.VIEW_TYPE = "view_type"

# raw data type
const.IMAGE = "image"
const.POINTS_3D = "points-3d"

# annotation template type
const.CATEGORY = "category"
const.COCO_TYPE = "coco-type"
const.OCR = "ocr"
const.RGBD = "rgbd"
const.SEGMENTATION_MASKS = "segmentation-masks"

# model const --------------------------------------------------------------------
# work directory
const.DEFAULT_MODEL_DIR = "./model"

# scheduler
const.DEFAULT_UPLOAD_INTERVAL_IN_SECOND = 60 * 10

# model meta
const.COMMIT_ID = "commit_id"
const.PROGRESS = "progress"

# model file begin
const.ONNX = "model.onnx"
const.DYNAMIC_ONNX = "model.dynamic_onnx"
const.CONFIG_PY = "config.py"
const.BEST_PTH = "best.pth"
const.LAST_PTH = "last.pth"
const.MODEL_JIT = "model.jit"
const.OUTPUT_TEMPLATE = "output_template.json"
# all the files with ".log" extend name
const.LOGS = ".log"
# model file end

# model file map should be consistent with const defination
# it defines the key of multipart form
const.MODEL_FILE_KEY_MAP = {
    const.ONNX : 'onnx',
    const.DYNAMIC_ONNX : 'dynamic_onnx',
    const.CONFIG_PY : 'config_py',
    const.BEST_PTH : 'best_pth',
    const.LAST_PTH : 'last_pth',
    const.MODEL_JIT : 'model_jit',
    const.OUTPUT_TEMPLATE : 'output_template',
    const.LOGS : "logs"
}
