#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


import os
import time
from typing import Dict, List

import cv2
from aifs_client.api.annotation_template_api import AnnotationTemplateApi
from aifs_client.api.data_view_api import DataViewApi
from loguru import logger
from tenacity import (retry, stop_after_attempt, stop_after_delay,
                      wait_exponential)
from torch.utils.data.dataset import Dataset as torchDataset

from data_client.dataset.value_object.image import ImageRawData
from data_client.utils import const, parser
from data_client.utils.client import get_aifs_client, get_s3_client
from data_client.utils.config import config as cfg
from data_client.utils.exception import InvalidArgument
from data_client.utils.retry import before_log, log_exception

from .dataset_config import DatasetConfig


class DatasetV1(torchDataset):  
    def __init__(self, data_view_id_list: List[str], config : DatasetConfig) -> None:
        logger.info("init process of dataset v1 starts")
        self.data_view_id_list = data_view_id_list
        self.config = config
        self.__init_value()
        self.__init_process()
    
    def __del__(self) -> None:
        logger.info("del process of dataset v1 starts")
        self.__release_resource()
    
    def __getitem__(self, index):
        """get raw data and annotation

        Args:
            index (int): the index of raw data list

        Returns:
            - raw_data: see __get_raw_data()
            - annotation: see __get_annotation()
        """
        raw_data_info = self.raw_data_list[index]
        anno_info_map = self.annotation_map.get(raw_data_info[const.DATA_ITEM_ID], {})
        
        t_start = time.time()
        raw_data = self.__get_raw_data(self.raw_data_type, raw_data_info)
        logger.debug("get raw data time cost {} s", time.time() - t_start)
        
        t_start = time.time()
        annotation = self.__get_annotation(anno_info_map)
        logger.debug("get annotation time cost {} s", time.time() - t_start)

        return raw_data, annotation
    
    def __len__(self):
        return len(self.raw_data_list)
    
    # public func ------------------------------
    
    def get_label_map(self):
        """
        Returns:
            dict: 
                key: annotation template id
                value (list): label list of the annotation template. The index number is used as input of model, the array item is the label name
        """
        return self.label_map
    def get_annotation_template_map(self):
        """
        get the annotation templates orginized in map struct related with annotation view passed to dataset

        Returns:
            dict:
                key: annotation template id
                value: annotation template details returned by aifs server
        """
        return self.anno_temp_map
    def get_word_list_map(self):
        """
        get the word list map of all annotation templates used in the dataset
        
        Returns:
            dict: the word list of annotation templates
                key: annotation template id
                value(list(str)): the word list of the annotation template
        """
        res = {}
        for anno_temp_id, anno_temp in self.anno_temp_map.items():
            if anno_temp.type == const.OCR:
                res[anno_temp_id] = anno_temp.word_list
        return res
    
    # private func -----------------------------
    def __init_value(self):
        self.dataset_dir = self.config.dataset_dir
        if not os.path.exists(self.dataset_dir):
            logger.info("create directory {}", self.dataset_dir)
            os.mkdir(self.dataset_dir)
        # prepare work dir
        self.raw_data_dir = os.path.join(self.dataset_dir, const.RAW_DATA)
        self.annotation_dir = os.path.join(self.dataset_dir, const.ANNOTATION)
        if not os.path.exists(self.raw_data_dir):
            logger.info("create directory {}", self.raw_data_dir)
            os.mkdir(self.raw_data_dir)
        if not os.path.exists(self.annotation_dir):
            logger.info("create directory {}", self.annotation_dir)
            os.mkdir(self.annotation_dir)
        
        self.raw_data_type = ""
        self.raw_data_view = []
        self.annotaion_view = []
        self.raw_data_list = []
        # annotation_map-> key: raw data id, value: annotation info map
        # annotation info map-> key: annotation template type, value: annotation data
        self.annotation_map : Dict[str, Dict] = {}
        # key: annotation template id; value: annotation template
        self.anno_temp_map = {}
        # key: annotation template id; value: category name list. ex: [rose, sunflower]
        self.label_map = {}
        # key: label id; value: index of the label in label list, int type.
        # (key, (key, val)) = (annotation_template_id, (label_id, index of the label in the label list))
        self.label_index_map = {}
        # (key, (key, val)) = (annotation_template_id), (word, index of the word in the word list)
        self.word_map = {}
        # init api client
        self.api_client = get_aifs_client()
        self.data_view_api = DataViewApi(self.api_client)
        self.anno_temp_api = AnnotationTemplateApi(self.api_client)
        
        self.s3_client = get_s3_client()
        
    def __init_process(self): 
        t_start = time.time()
        self.__get_data_view_info()
        logger.info("get data view info time cost {} s", time.time() - t_start)
        
        t_start = time.time()
        self.__get_raw_data_infos()
        logger.info("get raw data info time cost {} s", time.time() - t_start)
        
        t_start = time.time()
        self.__get_annotation_infos()
        logger.info("get annotation info time cost {} s", time.time() - t_start)
        
        self.__gen_label_list()
        self.__gen_word_map()
        self.__maybe_delete_data_with_no_annotatation()
    
    @retry(wait=wait_exponential(multiplier=1, min=const.MIN_BACKOFF_IN_S, max=const.MAX_BACKOFF_IN_S), reraise=True, stop=(stop_after_attempt(const.STOP_AFTER_ATTEMPT_TIMES) | stop_after_delay(const.STOP_AFTER_DELAY_IN_S)), before=before_log, after=log_exception)
    def __get_raw_data(self, raw_data_type, raw_data_info):
        """ read raw data from storage
            parse data according to its type(format)

        Args:
            raw_data_type (str): the type of the raw data
            raw_data_info (dict): the required meta data to read raw data

        Raises:
            InvalidArgument: can't handle raw data type currently

        Returns:
            raw_data_type, return data type
            - image, result of cv2.imread(img)
            - rgbd, RgbdRawData
        """
        bucket_name = cfg["s3"]["bucket_name"]     
        
        logger.debug(f'raw data info: {raw_data_info}')
        if not os.path.exists(raw_data_info[const.LOCAL_PATH]):
            logger.debug("raw data {} doesn't exist in {}, pull it from s3 {}-{}".format(raw_data_info[const.DATA_ITEM_ID], raw_data_info[const.LOCAL_PATH], bucket_name, raw_data_info[const.OBJECT_KEY]))
            self.s3_client.download_file(bucket_name, raw_data_info[const.OBJECT_KEY], raw_data_info[const.LOCAL_PATH])
            
        if raw_data_type == const.IMAGE:
            logger.debug("read raw data {} in {}".format(raw_data_info[const.DATA_ITEM_ID], raw_data_info[const.LOCAL_PATH]))
            return  ImageRawData(raw_data_info[const.DATA_ITEM_ID], cv2.imread(raw_data_info[const.LOCAL_PATH]))
        elif raw_data_type == const.RGBD:
            logger.debug("read raw data {} in {}".format(raw_data_info[const.DATA_ITEM_ID], raw_data_info[const.LOCAL_PATH]))
            return parser.parse_rgbd_raw_data(raw_data_info[const.LOCAL_PATH])
        elif raw_data_type == const.POINTS_3D:
            logger.debug("read raw data {} in {}".format(raw_data_info[const.DATA_ITEM_ID], raw_data_info[const.LOCAL_PATH]))
            return parser.parse_points_3d_raw_data(raw_data_info[const.LOCAL_PATH])
        else:
            err_msg = "can't handle data with data type {}".format(raw_data_type)
            logger.error(err_msg)
            raise InvalidArgument(err_msg)
    
    @retry(wait=wait_exponential(multiplier=1, min=const.MIN_BACKOFF_IN_S, max=const.MAX_BACKOFF_IN_S), reraise=True, stop=(stop_after_attempt(const.STOP_AFTER_ATTEMPT_TIMES) | stop_after_delay(const.STOP_AFTER_DELAY_IN_S)), before=before_log, after=log_exception)
    def __get_annotation(self, anno_info_map):
        """ read annotation from storage
            parse data according to its type(format)

        Args:
            anno_info_map (dict): the required meta data to read annotation

        Raises:
            InvalidArgument: can't handle annotation type currently

        Returns:
            annotation map (dict)
                key: annotation template id
                value: may return different types which depends on the annotation template type
                    annotation template type, return data type
                    - coco_type, CocoAnnotation
                    - rgbd, RgbdAnnotation
        """
        logger.debug(f'annotation info: {anno_info_map}')
        result = {}
        
        bucket_name = cfg["s3"]["bucket_name"]
        
        for anno_temp_id, anno_info in anno_info_map.items():
            anno_temp = self.anno_temp_map[anno_temp_id]
            
            if anno_temp.type == const.CATEGORY:
                result[anno_temp_id] = self.label_index_map[anno_temp_id][anno_info]
            elif anno_temp.type == const.OCR:
                result[anno_temp_id] = anno_info
            else:
                if not os.path.exists(anno_info[const.LOCAL_PATH]):
                    logger.debug("annotation doesn't exist in {}, pull it from s3 {}-{}".format(anno_info[const.LOCAL_PATH], bucket_name, anno_info[const.OBJECT_KEY]))
                    self.s3_client.download_file(bucket_name, anno_info[const.OBJECT_KEY], anno_info[const.LOCAL_PATH])
                
                # parse
                if anno_temp.type == const.COCO_TYPE:
                    logger.debug("read annotation [{}] from {}".format(const.COCO_TYPE, anno_info[const.LOCAL_PATH]))
                    result[anno_temp_id] = parser.parse_coco_annotation(anno_info[const.LOCAL_PATH], self.label_index_map[anno_temp_id])
                elif anno_temp.type == const.RGBD:
                    logger.debug("read annotation [{}] from {}".format(const.RGBD, anno_info[const.LOCAL_PATH]))
                    result[anno_temp_id] = parser.parse_rgbd_annotation(anno_info[const.LOCAL_PATH], self.label_index_map[anno_temp_id])
                elif anno_temp.type == const.SEGMENTATION_MASKS:
                    logger.debug("read annotation [{}] from {}".format(const.SEGMENTATION_MASKS, anno_info[const.LOCAL_PATH]))
                    result[anno_temp_id] = cv2.imread(anno_info[const.LOCAL_PATH], cv2.IMREAD_UNCHANGED)
                elif anno_temp.type == const.POINTS_3D:
                    logger.debug("read annotation [{}] from {}".format(const.POINTS_3D, anno_info[const.LOCAL_PATH]))
                    result[anno_temp_id] = parser.parse_points_3d_annotation(anno_info[const.LOCAL_PATH], self.label_index_map[anno_temp_id])
                else:
                    raise InvalidArgument("can't handle data with annotation template type {}".format(anno_temp.type))
        
        return result
                
    @retry(wait=wait_exponential(multiplier=1, min=const.MIN_BACKOFF_IN_S, max=const.MAX_BACKOFF_IN_S), reraise=True, stop=(stop_after_attempt(const.STOP_AFTER_ATTEMPT_TIMES) | stop_after_delay(const.STOP_AFTER_DELAY_IN_S)), before=before_log, after=log_exception)
    def __get_data_view_info(self):
        logger.debug("get data view info")  
        data_view_list = self.data_view_api.get_data_view_list(
            offset = 0, 
            limit = 50,
            data_view_id_list = ",".join(self.data_view_id_list),
        )
        
        for data_view in data_view_list:              
            if str(data_view.view_type) == const.RAW_DATA:
                self.raw_data_view.append(data_view)
                self.raw_data_type = str(data_view.raw_data_type)
            elif str(data_view.view_type) == const.ANNOTATION:
                self.annotaion_view.append(data_view)
            else:
                err_msg = "invalid data view type [{}]".format(data_view.view_type)
                logger.error(err_msg)
                raise InvalidArgument(err_msg)
                
        if len(self.raw_data_view) == 0 or len(self.annotaion_view) == 0:
            err_msg = "there are {} raw data view and {} annotation view, either of them should be zero".format(len(self.raw_data_view), len(self.annotaion_view))
            logger.error(err_msg)
            raise InvalidArgument(err_msg)
        
    @retry(wait=wait_exponential(multiplier=1, min=const.MIN_BACKOFF_IN_S, max=const.MAX_BACKOFF_IN_S), reraise=True, stop=(stop_after_attempt(const.STOP_AFTER_ATTEMPT_TIMES) | stop_after_delay(const.STOP_AFTER_DELAY_IN_S)), before=before_log, after=log_exception)
    def __get_raw_data_infos(self):
        logger.debug("get raw data info")  
        for data_view in self.raw_data_view:
            if str(data_view.raw_data_type) != self.raw_data_type:
                raise InvalidArgument("raw data view's raw data type should be consistent")
        for data_view in self.raw_data_view:
            locations = self.data_view_api.get_all_raw_data_locations_in_data_view(
                data_view_id=data_view.id
            )
            self.raw_data_list.extend(parser.parse_raw_data_locations(locations, self.raw_data_dir))
                
    @retry(wait=wait_exponential(multiplier=1, min=const.MIN_BACKOFF_IN_S, max=const.MAX_BACKOFF_IN_S), reraise=True, stop=(stop_after_attempt(const.STOP_AFTER_ATTEMPT_TIMES) | stop_after_delay(const.STOP_AFTER_DELAY_IN_S)), before=before_log, after=log_exception)           
    def __get_annotation_infos(self):
        logger.debug("get annotation info")  
        for data_view in self.annotaion_view:
            anno_temp_id = data_view.annotation_template_id
            
            if not anno_temp_id in self.anno_temp_map:
                anno_temp_details = self.anno_temp_api.get_anno_template_details(
                    annotation_template_id = anno_temp_id,
                )
                self.anno_temp_map[anno_temp_id] = anno_temp_details
            
            if self.anno_temp_map[anno_temp_id].type == const.CATEGORY:
                data_items = self.data_view_api.get_all_annotation_data_in_data_view(
                    data_view_id = data_view.id
                )
                for item in data_items[const.DATA_ITEMS].value:
                    self.annotation_map.setdefault(item[const.DATA_ITEM_ID], {})[anno_temp_id] = item.labels[0]
            elif self.anno_temp_map[anno_temp_id].type == const.OCR:
                data_items = self.data_view_api.get_all_annotation_data_in_data_view(
                    data_view_id = data_view.id
                )
                for item in data_items[const.DATA_ITEMS].value:
                    self.annotation_map.setdefault(item[const.DATA_ITEM_ID], {})[anno_temp_id] = item.text_data
            else:
                dir = os.path.join(self.annotation_dir, data_view.id)
                if not os.path.exists(dir):
                    os.mkdir(dir)

                locations = self.data_view_api.get_all_annotation_locations_in_data_view(
                    data_view_id=data_view.id
                )
                for location in locations[const.DATA_ITEMS].value:
                    anno_info = {}
                    anno_info[const.OBJECT_KEY] = location[const.OBJECT_KEY]
                    file_name = location[const.DATA_ITEM_ID] + os.path.splitext(location[const.DATA_NAME])[1]
                    anno_info[const.LOCAL_PATH] = os.path.join(dir, file_name)
                    
                    self.annotation_map.setdefault(location[const.DATA_ITEM_ID], {})[anno_temp_id] = anno_info
                    
    def __gen_label_list(self):
        for anno_temp_id, anno_temp in self.anno_temp_map.items():
            if not hasattr(anno_temp, "labels"):
                continue
            # sort by label id
            anno_temp.labels.sort(key=lambda label: label.id)
            
            label_list = []
            self.label_index_map[anno_temp_id] = {}
            for idx, label in enumerate(anno_temp.labels):
                label_list.append(label.name)
                self.label_index_map[anno_temp_id][label.id] = idx
            self.label_map[anno_temp_id] = label_list
            
    def __gen_word_map(self):
        for anno_temp_id, anno_temp in self.anno_temp_map.items():
            if not hasattr(anno_temp, "word_list"):
                continue
            self.word_map[anno_temp_id] = {}
            
            for idx, word in enumerate(anno_temp.word_list.value):
                self.word_map[anno_temp_id][word] = idx
    
    def __maybe_delete_data_with_no_annotatation(self):
        if self.config.delete_raw_data_with_no_annotation == False:
            return
        new_raw_data_list = []
        for raw_data_info in self.raw_data_list:
            if raw_data_info[const.DATA_ITEM_ID] in self.annotation_map:
                new_raw_data_list.append(raw_data_info)
        
        self.raw_data_list = new_raw_data_list
    
    def __release_resource(self):
        logger.info("close api client")
        self.api_client.close()
 

