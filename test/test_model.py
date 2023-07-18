#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

import json
import os
import random
import shutil
import sys
import tempfile
import time
import unittest
from test.basic.request_callback import create_request_callback
from test.test_data.model import get_dir as get_model_dir
from test.test_data.model import get_file_abs_path as get_model_file_abs_path
from test.test_data.model import get_json as get_model_data_json
from unittest.mock import patch

import httpretty
from aifs_client.api.data_view_api import DataViewApi
from loguru import logger

from data_client.model import model
from data_client.model.model_config import ModelConfig
from data_client.model.model_worker import upload_model_file
from data_client.utils import const
from data_client.utils.client import get_aifs_client
from data_client.utils.config import config as cfg
from data_client.utils.file import get_files_recursive


class MockS3Client:
    def __init__(self):
        pass
    def download_file(self, bucket_name, key, filepath):
        pass

def fake_download(self, bucket_name, key, filepath):
    if key.startswith("model"):
        model_file = get_model_file_abs_path("fake_data")
        shutil.copy(model_file, filepath)
    else:
        raise Exception("invalid arguments")

class TestModel(unittest.TestCase):
    """dataset unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skip("reason for skipping")
    def testSaveModelData(self):
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
        
        model_config_1 = ModelConfig(
            model_dir='/Users/lvyubin/work/data-client-work-dir/model',
            data_view_id='eeed2ea5-72d3-40a8-a286-44cbe22a0948'
        )
        model_config_2 = ModelConfig(
            model_dir='/Users/lvyubin/work/data-client-work-dir/model2',
            data_view_id='2897d7de-3d1e-446c-92e5-64f7c74d7afa'
        )
        model1, model2 = model.init([model_config_1, model_config_2])
        model1.upload_model_data(const.BEST_PTH, 'aaa.pth')
        model1.upload_model_data(const.LAST_PTH, 'bbb.pth')
        model2.upload_model_data(const.BEST_PTH, 'bbb.pth')
        model2.upload_model_data(const.LOGS)
        
        time.sleep(2)
        # no such file
        model1.upload_model_data(const.BEST_PTH, 'xxxx.pth')
        time.sleep(2)
        # remove job and add a new one
        model1.upload_model_data(const.BEST_PTH, 'aaa.pth')
        
        time.sleep(10)    
        model.finish()
    
    @unittest.skip("reason for skipping")
    def testModelProgress(self):
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
        
        model_config_1 = ModelConfig(
            model_dir='/Users/lvyubin/work/data-client-work-dir/model',
            data_view_id='eeed2ea5-72d3-40a8-a286-44cbe22a0948'
        )
        model_config_2 = ModelConfig(
            model_dir='/Users/lvyubin/work/data-client-work-dir/model2',
            data_view_id='2897d7de-3d1e-446c-92e5-64f7c74d7afa'
        )
        model1, model2 = model.init([model_config_1, model_config_2])
        
        start_time = time.time()
        while True:
            time.sleep(3)
            print(model.get_progress())
            new_progress = float(random.randint(1,99))
            print(f'new progress {new_progress}')
            model.update_progress(new_progress)
            if time.time() - start_time > 30:
                break
        model.finish()
    
    @unittest.skip("reason for skipping")
    def testModelPull(self):
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
        
        model_config_1 = ModelConfig(
            model_dir='/Users/lvyubin/work/data-client-work-dir/model4',
            data_view_id='eeed2ea5-72d3-40a8-a286-44cbe22a0948',
        )
        model_config_2 = ModelConfig(
            model_dir='/Users/lvyubin/work/data-client-work-dir/model3',
            data_view_id='2897d7de-3d1e-446c-92e5-64f7c74d7afa',
        )
        model1, model2 = model.init([model_config_1, model_config_2])
        
        model1.pull(model_file_list = [const.LOGS, const.ONNX, const.BEST_PTH, const.LAST_PTH])
        model2.pull(model_file_list = [const.LOGS, const.ONNX, const.BEST_PTH, const.LAST_PTH])
        
        time.sleep(3)
        model.finish()

    
    @unittest.skip("reason for skipping")
    def testIsCompleted(self):
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
        
        model_config_1 = ModelConfig(
            model_dir='/Users/lvyubin/work/data-client-work-dir/model4',
            data_view_id='eeed2ea5-72d3-40a8-a286-44cbe22a0948'        
        )
        model_config_2 = ModelConfig(
            model_dir='/Users/lvyubin/work/data-client-work-dir/model3',
            data_view_id='2897d7de-3d1e-446c-92e5-64f7c74d7afa'
        )
        model1, model2 = model.init([model_config_1, model_config_2])
        
        model.update_progress(100.0)
        time.sleep(3)
        self.assertTrue(model.is_completed())
        model.finish()
    
    @httpretty.activate 
    def testUploadModelFile(self):
        # mock config
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "aaa"
        cfg["s3"]["sk"] = "bbb"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "test_region"
        
        aifs_host = cfg["aifs"]["host"]
        
        aifs_client = get_aifs_client()
        data_view_api = DataViewApi(aifs_client)
        model_config = ModelConfig('2897d7de-3d1e-446c-92e5-64f7c74d7afa', get_model_dir())
        
        httpretty.register_uri(httpretty.POST, f'http://{aifs_host}/data-views/2897d7de-3d1e-446c-92e5-64f7c74d7afa/model', body=create_request_callback(self, ["bestPth"], ["a_best.pth"]))
        upload_model_file.__wrapped__(model_config, const.BEST_PTH, 'a_best.pth', data_view_api)
        
        httpretty.register_uri(httpretty.POST, f'http://{aifs_host}/data-views/2897d7de-3d1e-446c-92e5-64f7c74d7afa/model', body=create_request_callback(self, ["lastPth"], ["111_last.pth"]))
        upload_model_file.__wrapped__(model_config, const.LAST_PTH, '111_last.pth', data_view_api)
        
        httpretty.register_uri(httpretty.POST, f'http://{aifs_host}/data-views/2897d7de-3d1e-446c-92e5-64f7c74d7afa/model', body=create_request_callback(self, ["logs"], ["a.log", "b.log"]))
        upload_model_file.__wrapped__(model_config, const.LOGS, '', data_view_api)
        
    @httpretty.activate 
    @patch.object(MockS3Client, 'download_file', new=fake_download)
    @patch('data_client.model.model_worker.get_s3_client', return_value=MockS3Client())
    def testPullModelFile(self, mock_get_s3_client):
        # mock config
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "test_ak"
        cfg["s3"]["sk"] = "test_sk"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "test_region"
        
        aifs_host = cfg["aifs"]["host"]
        
        model_data_locations_1 = get_model_data_json("model_data_locations_1.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/eeed2ea5-72d3-40a8-a286-44cbe22a0948/model-data-locations', body=json.dumps(model_data_locations_1), status=200)
        
        model_data_locations_2 = get_model_data_json("model_data_locations_2.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/2897d7de-3d1e-446c-92e5-64f7c74d7afa/model-data-locations', body=json.dumps(model_data_locations_2), status=200)
        
        data_view_details_1 = get_model_data_json("model_view_details_1.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/eeed2ea5-72d3-40a8-a286-44cbe22a0948/details', body=json.dumps(data_view_details_1), status=200)
        
        data_view_details_2 = get_model_data_json("model_view_details_2.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/2897d7de-3d1e-446c-92e5-64f7c74d7afa/details', body=json.dumps(data_view_details_2), status=200)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            model_config_1 = ModelConfig(
                model_dir = os.path.join(temp_dir, 'model1'),
                data_view_id = 'eeed2ea5-72d3-40a8-a286-44cbe22a0948',
            )
            model_config_2 = ModelConfig(
                model_dir = os.path.join(temp_dir, 'model2'),
                data_view_id = '2897d7de-3d1e-446c-92e5-64f7c74d7afa',
            )
            model1, model2 = model.init([model_config_1, model_config_2])
            
            model1.pull(model_file_list = [const.LOGS, const.ONNX, const.BEST_PTH, const.LAST_PTH])
            model2.pull(model_file_list = [const.LOGS, const.ONNX, const.BEST_PTH, const.LAST_PTH])
            
            model.finish()
            
            file_set_1 = set([os.path.basename(filepath) for filepath in get_files_recursive(model_config_1.model_dir)])
            self.assertTrue(set([const.BEST_PTH, const.LAST_PTH]).issubset(file_set_1))
            
            file_set_2 = set([os.path.basename(filepath) for filepath in get_files_recursive(model_config_2.model_dir)])
            self.assertTrue(set([const.BEST_PTH, const.LAST_PTH, const.ONNX, "c.log", "fff.log", "d.log", "ccc.log", "a.log", "b.log"]).issubset(file_set_2))
        
        mock_get_s3_client.assert_called_once_with()
  
if __name__ == '__main__':
    unittest.main()
