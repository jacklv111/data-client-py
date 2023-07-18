#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

import json
import os
import shutil
import tempfile
import unittest
from test.basic.request_callback import create_request_callback
from test.test_data.artifact import get_dir as get_artifact_dir
from test.test_data.artifact import \
    get_file_abs_path as get_artifact_file_abs_path
from test.test_data.artifact import get_json as get_artifact_data_json
from unittest.mock import patch

import httpretty
from aifs_client.api.data_view_api import DataViewApi
from loguru import logger

from data_client.artifact import artifact
from data_client.artifact.artifact_config import ArtifactConfig
from data_client.artifact.artifact_worker import upload_artifact_file
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
    if key.startswith("artifact"):
        file = get_artifact_file_abs_path("fake_data")
        shutil.copy(file, filepath)
    else:
        raise Exception("invalid arguments")

class TestArtifact(unittest.TestCase):
    """dataset unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    @unittest.skip("reason for skipping")
    def testUploadFileReal(self):
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "aaa"
        cfg["s3"]["sk"] = "bbb"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "ceph"
        
        artifact_config = ArtifactConfig(
            local_dir = get_artifact_dir(),
            data_view_id = 'b2b6fcaa-1930-487a-b5b3-28455cddb600',
        )
        [arti] = artifact.init([artifact_config])
        arti.upload_file("fake_data")
        artifact.finish()

    @unittest.skip("reason for skipping")
    def testDownloadReal(self):
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = ""
        cfg["s3"]["ak"] = ""
        cfg["s3"]["sk"] = ""
        cfg["s3"]["endpoint"] = ""
        cfg["s3"]["region"] = ""
        artifact_config = ArtifactConfig(
            local_dir = os.path.join(get_artifact_dir(), "test"),
            data_view_id = 'b2b6fcaa-1930-487a-b5b3-28455cddb600',
        )
        [arti] = artifact.init([artifact_config])
        arti.pull()
        artifact.finish()
        
    @httpretty.activate 
    def testUploadFile(self):
        # mock config
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "test_ak"
        cfg["s3"]["sk"] = "test_sk"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "test_region"
        
        aifs_host = cfg["aifs"]["host"]
        
        aifs_client = get_aifs_client()
        data_view_api = DataViewApi(aifs_client)
        config = ArtifactConfig('2897d7de-3d1e-446c-92e5-64f7c74d7afa', get_artifact_dir())
        
        httpretty.register_uri(httpretty.POST, f'http://{aifs_host}/data-views/2897d7de-3d1e-446c-92e5-64f7c74d7afa/artifact', body=create_request_callback(self, ["file"], ["a_best.pth"]))
        upload_artifact_file.__wrapped__(config, 'a_best.pth', data_view_api)
        
        httpretty.register_uri(httpretty.POST, f'http://{aifs_host}/data-views/2897d7de-3d1e-446c-92e5-64f7c74d7afa/artifact', body=create_request_callback(self, ["file"], ["111_last.pth"]))
        upload_artifact_file.__wrapped__(config, '111_last.pth', data_view_api)
    
    @httpretty.activate 
    @patch.object(MockS3Client, 'download_file', new=fake_download)
    @patch('data_client.artifact.artifact_worker.get_s3_client', return_value=MockS3Client())
    def testPull(self, mock_get_s3_client):
        # mock config
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "test_ak"
        cfg["s3"]["sk"] = "test_sk"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "test_region"
        
        aifs_host = cfg["aifs"]["host"]
        
        artifact_file_locations_1 = get_artifact_data_json("artifact_locations_1.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/eeed2ea5-72d3-40a8-a286-44cbe22a0948/artifact-locations', body=json.dumps(artifact_file_locations_1), status=200)
        
        artifact_file_locations_2 = get_artifact_data_json("artifact_locations_2.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/2897d7de-3d1e-446c-92e5-64f7c74d7afa/artifact-locations', body=json.dumps(artifact_file_locations_2), status=200)
        
        data_view_details_1 = get_artifact_data_json("artifact_details_1.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/eeed2ea5-72d3-40a8-a286-44cbe22a0948/details', body=json.dumps(data_view_details_1), status=200)
        
        data_view_details_2 = get_artifact_data_json("artifact_details_2.json")
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/2897d7de-3d1e-446c-92e5-64f7c74d7afa/details', body=json.dumps(data_view_details_2), status=200)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_config_1 = ArtifactConfig(
                local_dir = os.path.join(temp_dir, 'artifact1'),
                data_view_id = 'eeed2ea5-72d3-40a8-a286-44cbe22a0948',
            )
            artifact_config_2 = ArtifactConfig(
                local_dir = os.path.join(temp_dir, 'artifact2'),
                data_view_id = '2897d7de-3d1e-446c-92e5-64f7c74d7afa',
            )
            [artifact1, artifact2] = artifact.init([artifact_config_1, artifact_config_2])
            
            artifact1.pull()
            artifact2.pull()
            
            artifact.finish()
            
            file_set_1 = set([os.path.basename(filepath) for filepath in get_files_recursive(artifact_config_1.local_dir)])
            self.assertTrue(set(["words.txt"]).issubset(file_set_1))
            
            file_set_2 = set([os.path.basename(filepath) for filepath in get_files_recursive(artifact_config_2.local_dir)])
            self.assertTrue(set(["a.bin", "b.bin"]).issubset(file_set_2))
        
        mock_get_s3_client.assert_called_once_with()
  
if __name__ == '__main__':
    unittest.main()
