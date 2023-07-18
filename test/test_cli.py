#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

import click.testing
import httpretty

from data_client.artifact.artifact_config import ArtifactConfig
from data_client.cli.main import config, download
from data_client.utils import naming
from data_client.utils.config import config as cfg


class MockS3Client:
    def __init__(self):
        pass
    def download_file(self, bucket_name, key, filepath):
        pass

class MockArtifact:
    def __init__(self):
        pass
    def pull(self):
        pass

class TestCli(unittest.TestCase):
    
    def setUp(self):
        cfg["aifs"]["host"] = "10.10.10.10:8080/api/open/v1"
        cfg["s3"]["bucket_name"] = "test_bucket"
        cfg["s3"]["ak"] = "aaa"
        cfg["s3"]["sk"] = "bbb"
        cfg["s3"]["endpoint"] = "http://example.com"
        cfg["s3"]["region"] = "ceph"
    def tearDown(self):
        pass
    
    @httpretty.activate
    @patch.object(MockS3Client, 'download_file')
    @patch('data_client.cli.main.get_s3_client', return_value=MockS3Client())
    def testDownloadZip(self, mock_get_s3_client, mock_download):
        aifs_host = cfg["aifs"]["host"]
        zip_view = {
            "id": "4a1b43bd-ea45-4bfb-b242-0d06be464400",
            "viewType": "dataset-zip",
            "createAt": 1680492917051,
            "zipFormat": "image-classification"
        }
        zip_view_id = zip_view["id"]
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/{zip_view_id}/details', body=json.dumps(zip_view), status=200)
        
        object_key = "for test obj key"
        data_item_id = "6f1ba5ec-fc6a-4056-8a8c-7f3840a33ff5"
        zip_location = {
            "dataViewId": "d6bc1923-f686-4705-9b9e-207c3b074128",
            "viewType": "dataset-zip",
            "dataItems": [
                {
                    "dataItemId": data_item_id,
                    "dataName": "ocr.zip",
                    "objectKey": object_key
                }
            ]
        }
        
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/{zip_view_id}/dataset-zip-location', body=json.dumps(zip_location), status=200)

        # check if it supports a tilde in the path
        local_dir = "~"
        file_path = os.path.join(Path(local_dir).expanduser().resolve(), data_item_id + ".zip")
        runner = click.testing.CliRunner()
        result = runner.invoke(download, ["--data_view_id", zip_view_id, "--local_dir", local_dir])

        mock_get_s3_client.assert_called_once_with()
        mock_download.assert_called_once_with(cfg["s3"]["bucket_name"], object_key, file_path)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), file_path)
        
    @httpretty.activate
    @patch.object(MockS3Client, 'download_file')
    @patch('data_client.cli.main.get_s3_client', return_value=MockS3Client())
    def testDownloadRawData(self, mock_get_s3_client, mock_download):
        aifs_host = cfg["aifs"]["host"]
        raw_data_view = {
            "id": "0ddec838-25eb-4d82-9926-dd3f2360d48a",
            "name": "flower-classification-val",
            "viewType": "raw-data",
            "createAt": 1679567694322,
            "itemCount": 958
        }
        raw_data_view_id = raw_data_view["id"]
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/{raw_data_view_id}/details', body=json.dumps(raw_data_view), status=200)
        
        raw_data_locations = {
            "dataViewId": "0ddec838-25eb-4d82-9926-dd3f2360d48a",
            "viewType": "raw-data",
            "rawDataType": "image",
            "dataItems": [
                {
                    "dataItemId": "0069a55f-fe03-47cc-9a0a-b46b17c58943",
                    "dataName": "Daisy (38).jpeg",
                    "objectKey": "raw-data/24ce76ad-71b9-4074-afb9-324c1345afc0/0069a55f-fe03-47cc-9a0a-b46b17c58943-image"
                },
                {
                    "dataItemId": "00e6ee9c-ad9b-4af8-9dc7-a0850e2c32f9",
                    "dataName": "Lily (164).jpeg",
                    "objectKey": "raw-data/24ce76ad-71b9-4074-afb9-324c1345afc0/00e6ee9c-ad9b-4af8-9dc7-a0850e2c32f9-image"
                },
                {
                    "dataItemId": "0135c91d-3016-4595-b649-2279f117de78",
                    "dataName": "Lily (90).jpeg",
                    "objectKey": "raw-data/24ce76ad-71b9-4074-afb9-324c1345afc0/0135c91d-3016-4595-b649-2279f117de78-image"
                },
            ]
        }
        
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/{raw_data_view_id}/raw-data-locations', body=json.dumps(raw_data_locations), status=200)

        # check if it supports a tilde in the path
        local_dir = "~"
        runner = click.testing.CliRunner()
        result = runner.invoke(download, ["--data_view_id", raw_data_view_id, "--local_dir", local_dir])
        mock_get_s3_client.assert_called_once_with()
        
        for dataItem in raw_data_locations["dataItems"]:
            file_name = dataItem["dataItemId"] + os.path.splitext(dataItem["dataName"])[1]
            file_path = os.path.join(Path(local_dir).expanduser().resolve(), file_name)
            mock_download.assert_any_call(cfg["s3"]["bucket_name"], dataItem["objectKey"], file_path)
            
        self.assertEqual(mock_download.call_count, len(raw_data_locations["dataItems"]))

        self.assertEqual(result.exit_code, 0)
    
    @httpretty.activate
    @patch.object(MockS3Client, 'download_file')
    @patch('data_client.cli.main.get_s3_client', return_value=MockS3Client())
    def testDownloadModel(self, mock_get_s3_client, mock_download):
        aifs_host = cfg["aifs"]["host"]
        model_view = {
            "id": "4a1b43bd-ea45-4bfb-b242-0d06be464400",
            "viewType": "model",
            "createAt": 1680492917051,
        }
        model_view_id = model_view["id"]
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/{model_view_id}/details', body=json.dumps(model_view), status=200)
        
        model_locations = {
            "dataViewId": "2897d7de-3d1e-446c-92e5-64f7c74d7afa",
            "viewType": "model",
            "dataItems": [
                {
                    "dataItemId": "18f7acfb-a576-42ca-af3d-16989cb34e7d",
                    "dataName": "fff.log",
                    "objectKey": "model/ae7f36d5-2b73-4e47-a358-b66ae42dcad42023-04-06-12:45:58/18f7acfb-a576-42ca-af3d-16989cb34e7d-fff.log"
                },
                {
                    "dataItemId": "1de0f0a3-3f42-4b8d-ae71-b508a4feffbd",
                    "dataName": "d.log",
                    "objectKey": "model/b844b64c-ddf2-45bd-8311-667ab341208c2023-04-06-12:22:14/1de0f0a3-3f42-4b8d-ae71-b508a4feffbd-d.log"
                },
                {
                    "dataItemId": "2c0368ad-651e-44a2-8d82-632cf94eb2ea",
                    "dataName": "ccc.log",
                    "objectKey": "model/ae7f36d5-2b73-4e47-a358-b66ae42dcad42023-04-06-12:45:58/2c0368ad-651e-44a2-8d82-632cf94eb2ea-ccc.log"
                },
                {
                    "dataItemId": "6c751879-7446-4db4-a99f-cf7cc84013d8",
                    "dataName": "a.log",
                    "objectKey": "model/8188aecc-587a-40d5-a860-c188900a47f82023-03-28-15:49:41/6c751879-7446-4db4-a99f-cf7cc84013d8-a.log"
                },
                {
                    "dataItemId": "6c8f0dc6-7047-40b4-975b-7686048f2b78",
                    "dataName": "model.onnx",
                    "objectKey": "model/1e98a87f-3604-4063-8c19-3b73c777c07b2023-03-24-12:06:04/6c8f0dc6-7047-40b4-975b-7686048f2b78-model.onnx"
                },
                {
                    "dataItemId": "6cc6fb72-6c41-44c5-aa12-379e735750b7",
                    "dataName": "b.log",
                    "objectKey": "model/8188aecc-587a-40d5-a860-c188900a47f82023-03-28-15:49:41/6cc6fb72-6c41-44c5-aa12-379e735750b7-b.log"
                },
                {
                    "dataItemId": "6d88d9cf-3f85-4ff7-9686-cf7103a57fbf",
                    "dataName": "c.log",
                    "objectKey": "model/8188aecc-587a-40d5-a860-c188900a47f82023-03-28-15:49:41/6d88d9cf-3f85-4ff7-9686-cf7103a57fbf-c.log"
                },
                {
                    "dataItemId": "a0e9b487-7db4-4778-888e-abd470d3249b",
                    "dataName": "lastPth",
                    "objectKey": "model/62ce71da-1736-4f97-bd99-4ff5815b01172023-03-24-12:23:11/a0e9b487-7db4-4778-888e-abd470d3249b-lastPth"
                },
                {
                    "dataItemId": "c27c1c37-3338-48fc-a39b-4ad364c5ff96",
                    "dataName": "www.pth",
                    "objectKey": "model/8891948b-9384-46ab-aa43-241e8d1e14a42023-03-24-12:12:57/c27c1c37-3338-48fc-a39b-4ad364c5ff96-www.pth"
                },
                {
                    "dataItemId": "d0e1a730-f4f6-4b5e-ac69-56a69556f31a",
                    "dataName": "best.pth",
                    "objectKey": "model/1e98a87f-3604-4063-8c19-3b73c777c07b2023-03-24-12:06:04/d0e1a730-f4f6-4b5e-ac69-56a69556f31a-best.pth"
                },
                {
                    "dataItemId": "d9e1eaf8-0631-4d4e-b792-44f94c121e11",
                    "dataName": "onnx",
                    "objectKey": "model/62ce71da-1736-4f97-bd99-4ff5815b01172023-03-24-12:23:11/d9e1eaf8-0631-4d4e-b792-44f94c121e11-onnx"
                },
                {
                    "dataItemId": "ffb2fc38-704c-4278-a656-1c13ecc7a040",
                    "dataName": "bestPth",
                    "objectKey": "model/7c84ea1a-38bb-4d8b-839d-cad94b1247ad2023-03-28-15:49:41/ffb2fc38-704c-4278-a656-1c13ecc7a040-bestPth"
                }
            ]
        }
        
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/{model_view_id}/model-data-locations', body=json.dumps(model_locations), status=200)

        # check if it supports a tilde in the path
        local_dir = "~"
        runner = click.testing.CliRunner()
        result = runner.invoke(download, ["--data_view_id", model_view_id, "--local_dir", local_dir])

        mock_get_s3_client.assert_called_once_with()
        
        for dataItem in model_locations["dataItems"]:
            file_name = naming.camel_to_under(dataItem["dataName"])
            file_path = os.path.join(Path(local_dir).expanduser().resolve(), file_name)
            mock_download.assert_any_call(cfg["s3"]["bucket_name"], dataItem["objectKey"], file_path)
            
        self.assertEqual(mock_download.call_count, len(model_locations["dataItems"]))

        self.assertEqual(result.exit_code, 0)
    
    @httpretty.activate
    @patch.object(MockArtifact, 'pull')
    @patch('data_client.cli.main.artifact.init', return_value=[MockArtifact()])
    def testDownloadArtifact(self, artifact_init, mock_pull):
        aifs_host = cfg["aifs"]["host"]
        artifact_view = {
            "id": "4a1b43bd-ea45-4bfb-b242-0d06be464400",
            "viewType": "artifact",
            "createAt": 1680492917051,
        }
        artifact_view_id = artifact_view["id"]
        
        httpretty.register_uri(httpretty.GET, f'http://{aifs_host}/data-views/{artifact_view_id}/details', body=json.dumps(artifact_view), status=200)

        # check if it supports a tilde in the path
        local_dir = "~"
        runner = click.testing.CliRunner()
        result = runner.invoke(download, ["--data_view_id", artifact_view_id, "--local_dir", local_dir])
        self.assertEqual(artifact_init.call_count, 1)
        mock_pull.assert_called_once_with()

        self.assertEqual(result.exit_code, 0)
        
    @patch('data_client.cli.main.save_config')
    def testConfig(self, save_config):
        aifs_ip = "test_ip"
        aifs_port = "test_port"
        s3_bucket_name = "test_bucket_name"
        s3_ak = "test ak"
        s3_sk = "test sk"
        s3_endpoint = "test endpoint"
        s3_region = "test region"
        
        runner = click.testing.CliRunner()
        result = runner.invoke(config, ["--aifs_ip", aifs_ip, "--aifs_port", aifs_port, "--s3_bucket_name", s3_bucket_name, "--s3_ak", s3_ak, "--s3_sk", s3_sk, "--s3_endpoint", s3_endpoint, "--s3_region", s3_region])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(aifs_ip, cfg["aifs"]["ip"])
        self.assertEqual(aifs_port, cfg["aifs"]["port"])
        self.assertEqual(s3_bucket_name, cfg["s3"]["bucket_name"])
        self.assertEqual(s3_ak, cfg["s3"]["ak"])
        self.assertEqual(s3_sk, cfg["s3"]["sk"])
        self.assertEqual(s3_endpoint, cfg["s3"]["endpoint"])
        self.assertEqual(s3_region, cfg["s3"]["region"])
        
        save_config.assert_called_once_with(cfg)
        
if __name__ == '__main__':
    unittest.main()