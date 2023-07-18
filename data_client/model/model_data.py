#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


from typing import List

from data_client.model import model_worker

from .model_config import ModelConfig


class ModelData(object):
    def __init__(self, config: ModelConfig):
        self.config = config
    
    def upload_model_data(self, model_file_key: str, model_file_path: str = None):
        model_worker.singleton.upload_model_file(self.config, model_file_key, model_file_path)
        
    def pull(self, model_file_list: List[str]):
        model_worker.singleton.pull(self.config, model_file_list)
