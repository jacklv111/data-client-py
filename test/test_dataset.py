#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

import faulthandler
import json
import os
import shutil
import sys
import tempfile
import unittest
from test.test_data import dataset as ds_test
from unittest.mock import patch

import cv2
import httpretty
import numpy as np
import torch.utils.data as Data
from loguru import logger
from tqdm import tqdm

from data_client.dataset import DatasetConfig, DatasetV1
from data_client.dataset.value_object.rgbd.rgbd_annotation import \
    RgbdAnnotation
from data_client.utils.config import config as cfg
from data_client.utils.json import write_json

class ClassificationDataset(DatasetV1):
    def __getitem__(self, index):
        raw_data, anno_map = super().__getitem__(index)
        img = raw_data.data
        resized_img = cv2.resize(
            src = img,
            dsize = (100, 100),
            interpolation=cv2.INTER_LINEAR
        ).astype(np.uint8)
        anno = list(anno_map.values())[0]
        logger.info(f'classification annotation {anno}')
        return resized_img ,anno

class CocoDataset(DatasetV1):
    def __getitem__(self, index):
        img, anno_map = super().__getitem__(index)
        logger.debug(f"raw data id: {img.id}")
        resized_img = cv2.resize(
            src = img.data,
            dsize = (100, 100),
            interpolation=cv2.INTER_LINEAR
        ).astype(np.uint8)
        anno = list(anno_map.values())[0]
        logger.debug(f'len of anno {len(anno)}')
        logger.debug("id: {}, kpt {}, area {}".format(anno[0].id, anno[0].key_points, anno[0].area))
        return resized_img ,1

class OcrDataset(DatasetV1):
    def __getitem__(self, index):
        raw_data, anno_map = super().__getitem__(index)
        img = raw_data.data
        resized_img = cv2.resize(
            src = img,
            dsize = (100, 100),
            interpolation=cv2.INTER_LINEAR
        ).astype(np.uint8)
        anno : list[RgbdAnnotation] = list(anno_map.values())[0]
        logger.info(f'ocr annotation {anno}')
        return resized_img ,1

class RgbdDataset(DatasetV1):
    def __getitem__(self, index):
        raw_data, anno_map = super().__getitem__(index)
        logger.debug(raw_data.image)
        logger.debug(raw_data.depth)
        logger.debug(raw_data.extrinsics)
        logger.debug(raw_data.intrinsics)
        anno = list(anno_map.values())[0]
        if (len(anno) > 0):
            logger.debug(anno[0].__dict__)
        return 1 ,1
    
class SegMasksDataset(DatasetV1):
    def __getitem__(self, index):
        raw_data, anno_map = super().__getitem__(index)
        anno = list(anno_map.values())[0]
        logger.debug(f'raw data: {raw_data.data}')
        logger.info(f'raw data shape: {raw_data.data.shape}')
        logger.debug(f'annotation: {anno}')
        logger.debug(f'anno is zero: {np.all(anno == 0)}')
        return 1 ,1

class Points3DDataset(DatasetV1):
    def __getitem__(self, index):
        raw_data, anno_map = super().__getitem__(index)
        anno = list(anno_map.values())[0]
        logger.debug(f'raw data: {raw_data.__dict__}')
        logger.debug(f'annotation: {anno.__dict__}')
        return 1 ,1

class MockS3Client:
    def __init__(self):
        pass
    def download_file(self, bucket_name, key, filepath):
        pass

def coco_fake_download(self, bucket_name, key, filepath):
    if key.startswith("raw-data"):
        raw_data_file = ds_test.get_file_abs_path("coco_fake_raw_data.jpg")
        shutil.copy(raw_data_file, filepath)
    elif key.startswith("annotation"):
        anno = ds_test.get_json("coco_fake_annotation.json")
        raw_data_id = os.path.splitext(os.path.basename(filepath))[0]
        anno["RawDataId"] = raw_data_id
        write_json(file_path=filepath, data=anno)
    else:
        raise Exception("invalid arguments")

def rgbd_fake_download(self, bucket_name, key, filepath):
    if key.startswith("raw-data"):
        raw_data_file = ds_test.get_file_abs_path("rgbd_fake_raw_data")
        shutil.copy(raw_data_file, filepath)
    elif key.startswith("annotation"):
        anno = ds_test.get_json("rgbd_fake_annotation.json")
        raw_data_id = os.path.splitext(os.path.basename(filepath))[0]
        anno["RawDataId"] = raw_data_id
        write_json(file_path=filepath, data=anno)
    else:
        raise Exception("invalid arguments")

def seg_masks_fake_download(self, bucket_name, key, filepath):
    if key.startswith("raw-data"):
        raw_data_file = ds_test.get_file_abs_path("seg_masks_fake_raw_data")
        shutil.copy(raw_data_file, filepath)
    elif key.startswith("annotation"):
        anno_file = ds_test.get_file_abs_path("seg_masks_fake_annotation")
        shutil.copy(anno_file, filepath)
    else:
        raise Exception("invalid arguments")

def points_3d_fake_download(self, bucket_name, key, filepath):
    if key.startswith("raw-data"):
        raw_data_file = ds_test.get_file_abs_path("points_3d_raw_data.bin")
        shutil.copy(raw_data_file, filepath)
    elif key.startswith("annotation"):
        anno_file = ds_test.get_file_abs_path("points_3d_annotation")
        shutil.copy(anno_file, filepath)
    else:
        raise Exception("invalid arguments")

def classification_fake_download(self, bucket_name, key, filepath):
    if key.startswith("raw-data"):
        raw_data_file = ds_test.get_file_abs_path("classification_fake_raw_data.jpeg")
        shutil.copy(raw_data_file, filepath)
    else:
        raise Exception("invalid arguments")
    
def ocr_fake_download(self, bucket_name, key, filepath):
    if key.startswith("raw-data"):
        raw_data_file = ds_test.get_file_abs_path("ocr_fake_raw_data.jpg")
        shutil.copy(raw_data_file, filepath)
    else:
        raise Exception("invalid arguments")

class TestDataset(unittest.TestCase):
    """dataset unit test stubs"""

    def setUp(self):
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    def tearDown(self):
        pass

    @unittest.skip("reason for skipping")
    def testFlowerClassification(self):
        faulthandler.enable()
        logger.remove()
        logger.add(sys.stderr, level="INFO")
        
        """Test DatasetV1"""
        dataset_config = DatasetConfig(
            delete_raw_data_with_no_annotation = True
        )
        # dataset = FlowerDataset(["16bdffd9-1b78-4b2f-b26c-fb3c703e1a29", "0ba6899f-2c6b-48ab-8b0e-7c47e5f04cc6"])
        dataset = ClassificationDataset(
            data_view_id_list = ["6b21b10e-4c8d-476b-898e-de2760d8c4c7", "61610fb8-55cb-45bd-90c1-9926b1150361"], 
            config = dataset_config
        )
       
        print(dataset.get_label_map())
        loader = Data.DataLoader(
            dataset=dataset,
            batch_size=10,
            shuffle=True,
            num_workers=0,
        )
        for epoch in range(1):
            num = 0
            for raw_data, annotation in loader:
                num = num + 1
                # print('Epoch: {} | num: {} | raw_data: {} | annotation: {}'.format(epoch,num, raw_data, annotation))
    
    @httpretty.activate
    @patch.object(MockS3Client, 'download_file', new=classification_fake_download)
    @patch('data_client.dataset.dataset_v1.get_s3_client', return_value=MockS3Client())
    def testClassificationDataset2(self, mock_get_s3_client):
        # mock config
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "aaa"
        cfg["s3"]["sk"] = "bbb"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "ceph"
        
        aifs_host = cfg["aifs"]["host"]
        
        # mock aifs response
        data_view_list = ds_test.get_json("classification_data_view_list.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views?offset=0&limit=50&dataViewIdList=6b21b10e-4c8d-476b-898e-de2760d8c4c7,61610fb8-55cb-45bd-90c1-9926b1150361', body=json.dumps(data_view_list), status=200)
        
        raw_data_locations = ds_test.get_json("classification_raw_data_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/6b21b10e-4c8d-476b-898e-de2760d8c4c7/raw-data-locations', body=json.dumps(raw_data_locations), status=200)
        
        anno_temp_details = ds_test.get_json("classification_annotation_template_details.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/annotation-templates/d2d5d4c1-3286-49eb-acf8-677885776fc2/details', body=json.dumps(anno_temp_details), status=200)
        
        annotations = ds_test.get_json("classification_annotations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/61610fb8-55cb-45bd-90c1-9926b1150361/annotation-data', body=json.dumps(annotations), status=200)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # initialize dataset
            dataset_config = DatasetConfig(
                delete_raw_data_with_no_annotation = True,
                dataset_dir = temp_dir
            )
            
            dataset = ClassificationDataset(
                data_view_id_list = ["6b21b10e-4c8d-476b-898e-de2760d8c4c7", "61610fb8-55cb-45bd-90c1-9926b1150361"], 
                config = dataset_config
            )
            
            loader = Data.DataLoader(
                dataset=dataset,
                batch_size=10,
                shuffle=True,
                num_workers=0,
            )
            
            for raw_data, annotation in loader:
                #print(raw_data, annotation)
                pass
        
        mock_get_s3_client.assert_called_once_with()

    @httpretty.activate
    @patch.object(MockS3Client, 'download_file', new=classification_fake_download)
    @patch('data_client.dataset.dataset_v1.get_s3_client', return_value=MockS3Client())
    def testClassificationDataset2RawDataView1AnnotationView(self, mock_get_s3_client):
        # mock config
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "test_ak"
        cfg["s3"]["sk"] = "test_sk"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "test_region"
        
        aifs_host = cfg["aifs"]["host"]
        
        # mock aifs response
        
        data_view_list = ds_test.get_json("classification_data_view_list.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views?offset=0&limit=50&dataViewIdList=6b21b10e-4c8d-476b-898e-de2760d8c4c7,61610fb8-55cb-45bd-90c1-9926b1150361', body=json.dumps(data_view_list), status=200)
        
        data_view_list_2 = ds_test.get_json("classification_data_view_list_2.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views?offset=0&limit=50&dataViewIdList=6b21b10e-4c8d-476b-898e-de2760d8c4c7,2221b10e-4c8d-476b-898e-de2760d8c4c7,61610fb8-55cb-45bd-90c1-9926b1150361', body=json.dumps(data_view_list_2), status=200)
        
        raw_data_locations = ds_test.get_json("classification_raw_data_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/6b21b10e-4c8d-476b-898e-de2760d8c4c7/raw-data-locations', body=json.dumps(raw_data_locations), status=200)
        
        raw_data_locations = ds_test.get_json("classification_raw_data_locations_2.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/2221b10e-4c8d-476b-898e-de2760d8c4c7/raw-data-locations', body=json.dumps(raw_data_locations), status=200)
        
        anno_temp_details = ds_test.get_json("classification_annotation_template_details.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/annotation-templates/d2d5d4c1-3286-49eb-acf8-677885776fc2/details', body=json.dumps(anno_temp_details), status=200)
        
        annotations = ds_test.get_json("classification_annotations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/61610fb8-55cb-45bd-90c1-9926b1150361/annotation-data', body=json.dumps(annotations), status=200)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # initialize dataset
            dataset_config_1 = DatasetConfig(
                delete_raw_data_with_no_annotation = True,
                dataset_dir = temp_dir + "/1"
            )
            
            dataset_config_2 = DatasetConfig(
                delete_raw_data_with_no_annotation = True,
                dataset_dir = temp_dir + "/2"
            )
            
            dataset_1 = ClassificationDataset(
                data_view_id_list = ["6b21b10e-4c8d-476b-898e-de2760d8c4c7", "2221b10e-4c8d-476b-898e-de2760d8c4c7", "61610fb8-55cb-45bd-90c1-9926b1150361"], 
                config = dataset_config_1
            )
            
            dataset_2 = ClassificationDataset(
                data_view_id_list = ["6b21b10e-4c8d-476b-898e-de2760d8c4c7", "61610fb8-55cb-45bd-90c1-9926b1150361"], 
                config = dataset_config_2
            )
            
            self.assertEqual(len(dataset_1), len(dataset_2))
        
    @httpretty.activate
    @patch.object(MockS3Client, 'download_file', new=classification_fake_download)
    @patch('data_client.dataset.dataset_v1.get_s3_client', return_value=MockS3Client())
    def testClassificationDataset2RawDataView1AnnotationView(self, mock_get_s3_client):
        # mock config
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "test_ak"
        cfg["s3"]["sk"] = "test_sk"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "test_region"
        
        aifs_host = cfg["aifs"]["host"]
        
        # mock aifs response
        data_view_list = ds_test.get_json("classification_data_view_list_2.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views?offset=0&limit=50&dataViewIdList=6b21b10e-4c8d-476b-898e-de2760d8c4c7,2221b10e-4c8d-476b-898e-de2760d8c4c7,61610fb8-55cb-45bd-90c1-9926b1150361', body=json.dumps(data_view_list), status=200)
        
        raw_data_locations = ds_test.get_json("classification_raw_data_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/6b21b10e-4c8d-476b-898e-de2760d8c4c7/raw-data-locations', body=json.dumps(raw_data_locations), status=200)
        
        raw_data_locations = ds_test.get_json("classification_raw_data_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/2221b10e-4c8d-476b-898e-de2760d8c4c7/raw-data-locations', body=json.dumps(raw_data_locations), status=200)
        
        anno_temp_details = ds_test.get_json("classification_annotation_template_details.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/annotation-templates/d2d5d4c1-3286-49eb-acf8-677885776fc2/details', body=json.dumps(anno_temp_details), status=200)
        
        annotations = ds_test.get_json("classification_annotations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/61610fb8-55cb-45bd-90c1-9926b1150361/annotation-data', body=json.dumps(annotations), status=200)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # initialize dataset
            dataset_config_1 = DatasetConfig(
                delete_raw_data_with_no_annotation = True,
                dataset_dir = temp_dir + "/1"
            )
            
            dataset_config_2 = DatasetConfig(
                delete_raw_data_with_no_annotation = True,
                dataset_dir = temp_dir + "/2"
            )
            
            dataset_1 = ClassificationDataset(
                data_view_id_list = ["6b21b10e-4c8d-476b-898e-de2760d8c4c7", "2221b10e-4c8d-476b-898e-de2760d8c4c7", "61610fb8-55cb-45bd-90c1-9926b1150361"], 
                config = dataset_config_1
            )
            
            dataset_2 = ClassificationDataset(
                data_view_id_list = ["6b21b10e-4c8d-476b-898e-de2760d8c4c7", "61610fb8-55cb-45bd-90c1-9926b1150361"], 
                config = dataset_config_2
            )
            
            self.assertEqual(len(dataset_1), len(dataset_2))
                
    @httpretty.activate
    @patch.object(MockS3Client, 'download_file', new=coco_fake_download)
    @patch('data_client.dataset.dataset_v1.get_s3_client', return_value=MockS3Client())
    def testCocodataset2(self, mock_get_s3_client):
        # mock config
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "test_ak"
        cfg["s3"]["sk"] = "test_sk"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "test_region"
        
        aifs_host = cfg["aifs"]["host"]
        
        # mock aifs response
        data_view_list = ds_test.get_json("coco_data_view_list.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views?offset=0&limit=50&dataViewIdList=38dc1190-d1d1-46c4-b617-178b024fc10d,cf11dc76-0193-4694-a02a-aa112050fbec', body=json.dumps(data_view_list), status=200)
        
        raw_data_locations = ds_test.get_json("coco_raw_data_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/cf11dc76-0193-4694-a02a-aa112050fbec/raw-data-locations', body=json.dumps(raw_data_locations), status=200)
        
        anno_temp_details = ds_test.get_json("coco_annotation_template_details.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/annotation-templates/c6d4f469-3477-4332-a6e8-605d0739ec9e/details', body=json.dumps(anno_temp_details), status=200)
        
        annotation_locations = ds_test.get_json("coco_annotation_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/38dc1190-d1d1-46c4-b617-178b024fc10d/annotation-locations', body=json.dumps(annotation_locations), status=200)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # initialize dataset
            dataset_config = DatasetConfig(
                delete_raw_data_with_no_annotation = True,
                dataset_dir = temp_dir
            )
            
            dataset = CocoDataset(
                data_view_id_list = ["38dc1190-d1d1-46c4-b617-178b024fc10d","cf11dc76-0193-4694-a02a-aa112050fbec"], 
                config = dataset_config
            )
            
            loader = Data.DataLoader(
                dataset=dataset,
                batch_size=10,
                shuffle=True,
                num_workers=0,
            )
            
            for raw_data, annotation in loader:
                #print(raw_data, annotation)
                pass
        
        mock_get_s3_client.assert_called_once_with()

    @unittest.skip("reason for skipping")
    def testCocodataset(self):
        faulthandler.enable()
        logger.remove()
        logger.add(sys.stderr, level="INFO")
        
        dataset_config = DatasetConfig(
            delete_raw_data_with_no_annotation = True
        )
        
        dataset = CocoDataset(
            #train
            #data_view_id_list = ["b3518774-b0bb-4581-b31f-29a3ace7b085", "02eabb5c-d458-4eb6-b704-06673101917f"], 
            #valid
            data_view_id_list = ["03ffeed3-a694-4e9a-b2a9-0c37c7fa4bdd", "ce26ea46-639c-47a8-9652-d2adfe319b2b"], 
            config = dataset_config
        )
        print(dataset.get_label_map())
        print(dataset.get_annotation_template_map())
        loader = Data.DataLoader(
            dataset=dataset,
            batch_size=10,
            shuffle=True,
            num_workers=0,
        )
        for epoch in range(1):
            num = 0
            for raw_data, annotation in loader:
                num = num + 1
                #print('Epoch: {} | num: {} | raw_data: {} | annotation: {}'.format(epoch,num, raw_data, annotation))
    
    @httpretty.activate
    @patch.object(MockS3Client, 'download_file', new=ocr_fake_download)
    @patch('data_client.dataset.dataset_v1.get_s3_client', return_value=MockS3Client())
    def testOcrDataset2(self, mock_get_s3_client):
        # mock config
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "test_ak"
        cfg["s3"]["sk"] = "test_sk"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "test_region"
        
        aifs_host = cfg["aifs"]["host"]
        
        # mock aifs response
        data_view_list = ds_test.get_json("ocr_data_view_list.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views?offset=0&limit=50&dataViewIdList=4a5a48b3-f44b-4e30-9300-a86512535779,800c4a0d-1d9a-4975-91df-3ce5df74d395', body=json.dumps(data_view_list), status=200)
        
        raw_data_locations = ds_test.get_json("ocr_raw_data_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/4a5a48b3-f44b-4e30-9300-a86512535779/raw-data-locations', body=json.dumps(raw_data_locations), status=200)
        
        anno_temp_details = ds_test.get_json("ocr_annotation_template_details.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/annotation-templates/5537b392-8ca3-40e1-b549-f79ccf252609/details', body=json.dumps(anno_temp_details), status=200)
        
        annotations = ds_test.get_json("ocr_annotations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/800c4a0d-1d9a-4975-91df-3ce5df74d395/annotation-data', body=json.dumps(annotations), status=200)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # initialize dataset
            dataset_config = DatasetConfig(
                delete_raw_data_with_no_annotation = True,
                dataset_dir = temp_dir
            )
            
            dataset = ClassificationDataset(
                data_view_id_list = ["4a5a48b3-f44b-4e30-9300-a86512535779", "800c4a0d-1d9a-4975-91df-3ce5df74d395"], 
                config = dataset_config
            )
            
            loader = Data.DataLoader(
                dataset=dataset,
                batch_size=10,
                shuffle=True,
                num_workers=0,
            )
            
            for raw_data, annotation in loader:
                #print(raw_data, annotation)
                pass
        
        mock_get_s3_client.assert_called_once_with()
    
    @unittest.skip("reason for skipping")
    def testOcrdataset(self):
        faulthandler.enable()
        logger.remove()
        logger.add(sys.stderr, level="INFO")
        
        dataset_config = DatasetConfig(
            delete_raw_data_with_no_annotation = True
        )
        
        dataset = OcrDataset(
            # train
            #data_view_id_list = ["35552fdc-1f04-4f7d-bf0b-86b156410af7", "3db85b65-3515-476b-8126-7b51845c706a"], 
            # val
            data_view_id_list = ["4a5a48b3-f44b-4e30-9300-a86512535779", "800c4a0d-1d9a-4975-91df-3ce5df74d395"], 
            config = dataset_config
        )
        print(dataset.get_word_list_map())
        loader = Data.DataLoader(
            dataset=dataset,
            batch_size=10,
            shuffle=True,
            num_workers=0,
        )
        for epoch in range(1):
            num = 0
            for raw_data, annotation in loader:
                num = num + 1
                #print('Epoch: {} | num: {} | raw_data: {} | annotation: {}'.format(epoch,num, raw_data, annotation))

    @httpretty.activate
    @patch.object(MockS3Client, 'download_file', new=rgbd_fake_download)
    @patch('data_client.dataset.dataset_v1.get_s3_client', return_value=MockS3Client())
    def testRgbdDataset2(self, mock_get_s3_client):
        # mock config
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "test_ak"
        cfg["s3"]["sk"] = "test_sk"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "test_region"
        
        aifs_host = cfg["aifs"]["host"]
        
        # mock aifs response
        data_view_list = ds_test.get_json("rgbd_data_view_list.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views?offset=0&limit=50&dataViewIdList=12160eac-179d-4f2a-8055-e79f8ccbba26,04550946-3add-47a2-9011-a329a0c2b6aa', body=json.dumps(data_view_list), status=200)
        
        raw_data_locations = ds_test.get_json("rgbd_raw_data_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/12160eac-179d-4f2a-8055-e79f8ccbba26/raw-data-locations', body=json.dumps(raw_data_locations), status=200)
        
        anno_temp_details = ds_test.get_json("rgbd_annotation_template_details.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/annotation-templates/d2db565b-3e50-42df-bc89-3be956c3de60/details', body=json.dumps(anno_temp_details), status=200)
        
        annotation_locations = ds_test.get_json("rgbd_annotation_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/04550946-3add-47a2-9011-a329a0c2b6aa/annotation-locations', body=json.dumps(annotation_locations), status=200)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # initialize dataset
            dataset_config = DatasetConfig(
                delete_raw_data_with_no_annotation = True,
                dataset_dir = temp_dir
            )
            
            dataset = RgbdDataset(
                data_view_id_list = ["12160eac-179d-4f2a-8055-e79f8ccbba26", "04550946-3add-47a2-9011-a329a0c2b6aa"], 
                config = dataset_config
            )
            
            loader = Data.DataLoader(
                dataset=dataset,
                batch_size=10,
                shuffle=True,
                num_workers=0,
            )
            
            for raw_data, annotation in loader:
                #print(raw_data, annotation)
                pass
        
        mock_get_s3_client.assert_called_once_with()
    
    @unittest.skip("reason for skipping")
    def testRgbddataset(self):
        faulthandler.enable()
        logger.remove()
        logger.add(sys.stderr, level="INFO")
        
        dataset_config = DatasetConfig(
            delete_raw_data_with_no_annotation = True
        )
        
        dataset = RgbdDataset(
            # train
            #data_view_id_list = ["2c39143e-918c-4377-b1ca-1e34618a7f4d", "dda8bb8c-3eda-4bfb-9488-6f5f5c19ead6"], 
            # val
            data_view_id_list = ["12160eac-179d-4f2a-8055-e79f8ccbba26", "04550946-3add-47a2-9011-a329a0c2b6aa"], 
            config = dataset_config
        )
        loader = Data.DataLoader(
            dataset=dataset,
            batch_size=10,
            shuffle=True,
            num_workers=0,
        )
        for epoch in range(1):
            num = 0
            for raw_data, annotation in tqdm(loader):
                num = num + 1
                #print('Epoch: {} | num: {} | raw_data: {} | annotation: {}'.format(epoch,num, raw_data, annotation))
    
    @httpretty.activate
    @patch.object(MockS3Client, 'download_file', new=seg_masks_fake_download)
    @patch('data_client.dataset.dataset_v1.get_s3_client', return_value=MockS3Client())
    def testSegMasksDataset2(self, mock_get_s3_client):
        # mock config
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "test_ak"
        cfg["s3"]["sk"] = "test_sk"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "test_region"
        
        aifs_host = cfg["aifs"]["host"]
        
        # mock aifs response
        data_view_list = ds_test.get_json("seg_masks_data_view_list.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views?offset=0&limit=50&dataViewIdList=1da7e802-15d6-4bec-9d69-1d0feb09315b,0f87a257-10ab-4763-b8d4-d70138cb51d3', body=json.dumps(data_view_list), status=200)
        
        raw_data_locations = ds_test.get_json("seg_masks_raw_data_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/1da7e802-15d6-4bec-9d69-1d0feb09315b/raw-data-locations', body=json.dumps(raw_data_locations), status=200)
        
        anno_temp_details = ds_test.get_json("seg_masks_annotation_template_details.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/annotation-templates/85b8a2b9-762c-4a3d-be53-95744d11f85c/details', body=json.dumps(anno_temp_details), status=200)
        
        annotation_locations = ds_test.get_json("seg_masks_annotation_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/0f87a257-10ab-4763-b8d4-d70138cb51d3/annotation-locations', body=json.dumps(annotation_locations), status=200)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # initialize dataset
            dataset_config = DatasetConfig(
                delete_raw_data_with_no_annotation = True,
                dataset_dir = temp_dir
            )
            
            dataset = SegMasksDataset(
                data_view_id_list = ["1da7e802-15d6-4bec-9d69-1d0feb09315b", "0f87a257-10ab-4763-b8d4-d70138cb51d3"], 
                config = dataset_config
            )
            
            loader = Data.DataLoader(
                dataset=dataset,
                batch_size=10,
                shuffle=True,
                num_workers=0,
            )
            
            for raw_data, annotation in loader:
                #print(raw_data, annotation)
                pass
        
        mock_get_s3_client.assert_called_once_with()
    
    @unittest.skip("reason for skipping")
    def testSegMasksdataset(self):
        faulthandler.enable()
        logger.remove()
        logger.add(sys.stderr, level="INFO")
        
        dataset_config = DatasetConfig(
            delete_raw_data_with_no_annotation = False
        )
        
        dataset = SegMasksDataset(
            # train
            data_view_id_list = ["8384e1b9-16ec-42ff-8141-8368973b2e5c", "8faaa853-a5a8-4e6f-9f27-a10abffbce1b"], 
            # val
            #data_view_id_list = ["1da7e802-15d6-4bec-9d69-1d0feb09315b", "0f87a257-10ab-4763-b8d4-d70138cb51d3"], 
            config = dataset_config
        )
        loader = Data.DataLoader(
            dataset=dataset,
            batch_size=10,
            shuffle=True,
            num_workers=0,
        )
        for epoch in range(1):
            num = 0
            for raw_data, annotation in tqdm(loader):
                num = num + 1
                #print('Epoch: {} | num: {} | raw_data: {} | annotation: {}'.format(epoch,num, raw_data, annotation))
    
    @httpretty.activate
    @patch.object(MockS3Client, 'download_file', new=points_3d_fake_download)
    @patch('data_client.dataset.dataset_v1.get_s3_client', return_value=MockS3Client())
    def testPoints3DDataset2(self, mock_get_s3_client):
        # mock config
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "test_ak"
        cfg["s3"]["sk"] = "test_sk"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "test_region"
        
        aifs_host = cfg["aifs"]["host"]
        
        # mock aifs response
        data_view_list = ds_test.get_json("points_3d_data_view_list.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views?offset=0&limit=50&dataViewIdList=7f39a40e-d207-47ad-a768-873f946d8056,fbcd9cbe-2dcc-42b7-9ca2-c1c3f0581027', body=json.dumps(data_view_list), status=200)
        
        raw_data_locations = ds_test.get_json("points_3d_raw_data_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/fbcd9cbe-2dcc-42b7-9ca2-c1c3f0581027/raw-data-locations', body=json.dumps(raw_data_locations), status=200)
        
        anno_temp_details = ds_test.get_json("points_3d_annotation_template_details.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/annotation-templates/79f5dd28-7e5a-4331-bd1c-e51eeb40ed3b/details', body=json.dumps(anno_temp_details), status=200)
        
        annotation_locations = ds_test.get_json("points_3d_annotation_locations.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/7f39a40e-d207-47ad-a768-873f946d8056/annotation-locations', body=json.dumps(annotation_locations), status=200)
        
        with tempfile.TemporaryDirectory() as temp_dir: 
            # initialize dataset
            dataset_config = DatasetConfig(
                delete_raw_data_with_no_annotation = True,
                dataset_dir = temp_dir
            )
            
            dataset = Points3DDataset(
                data_view_id_list = ["7f39a40e-d207-47ad-a768-873f946d8056", "fbcd9cbe-2dcc-42b7-9ca2-c1c3f0581027"], 
                config = dataset_config
            )
            
            loader = Data.DataLoader(
                dataset=dataset,
                batch_size=10,
                shuffle=True,
                num_workers=0,
            )
            
            for raw_data, annotation in loader:
                logger.info(f"points 3d raw data: {raw_data}, annotation: {annotation}")
        
        mock_get_s3_client.assert_called_once_with()
    
if __name__ == '__main__':
    unittest.main()
