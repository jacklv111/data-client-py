#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


import os
import subprocess
from typing import List, Optional

from aifs_client.api.data_view_api import DataViewApi
from loguru import logger
from tenacity import (retry, stop_after_attempt, stop_after_delay,
                      wait_exponential)

from data_client.model.model_config import ModelConfig
from data_client.utils import const, naming
from data_client.utils.client import get_aifs_client, get_s3_client
from data_client.utils.condition import wait_condition_timeout
from data_client.utils.config import config as cfg
from data_client.utils.exception import InvalidArgument
from data_client.utils.file import (get_files_with_suffix_recursive,
                                    is_file_operated)
from data_client.utils.retry import before_log, log_exception
from data_client.utils.task import Task, TaskManager


@retry(wait=wait_exponential(multiplier=1, min=const.MIN_BACKOFF_IN_S, max=const.MAX_BACKOFF_IN_S), reraise=True, stop=(stop_after_attempt(const.STOP_AFTER_ATTEMPT_TIMES) | stop_after_delay(const.STOP_AFTER_DELAY_IN_S)), before=before_log, after=log_exception)
def save_commit_id(data_view_id: str, client: DataViewApi):
    logger.info(f"begin to save code commit id, data view id {data_view_id}")
    status, commit_id = subprocess.getstatusoutput("git rev-parse HEAD")
    if status == 0:
        client.upload_model_data_to_data_view(data_view_id=data_view_id, _content_type='multipart/form-data', commit_id=commit_id)

@retry(wait=wait_exponential(multiplier=1, min=const.MIN_BACKOFF_IN_S, max=const.MAX_BACKOFF_IN_S), reraise=True, stop=(stop_after_attempt(const.STOP_AFTER_ATTEMPT_TIMES) | stop_after_delay(const.STOP_AFTER_DELAY_IN_S)), before=before_log, after=log_exception)
def update_progress(data_view_id: str, progress: float, client: DataViewApi):
    logger.info(f"begin to write progress, data view id {data_view_id}")
    client.upload_model_data_to_data_view(data_view_id=data_view_id, _content_type='multipart/form-data', progress=str(progress))

@retry(wait=wait_exponential(multiplier=1, min=const.MIN_BACKOFF_IN_S, max=const.MAX_BACKOFF_IN_S), reraise=True, stop=(stop_after_attempt(const.STOP_AFTER_ATTEMPT_TIMES) | stop_after_delay(const.STOP_AFTER_DELAY_IN_S)), before=before_log, after=log_exception)
def save_model_data(config: ModelConfig, client: DataViewApi):
    logger.info(f"begin to save model data, data view id {config.data_view_id}")
    upload_data = {"_content_type": 'multipart/form-data'}
    files = []
    try:
        for model_file_key, form_key in const.MODEL_FILE_KEY_MAP.items():
            file_name = config.get_alias(model_file_key, model_file_key)
            model_dir = config.model_dir
            
            file_path = os.path.join(model_dir, file_name)
            if not os.path.exists(file_path):
                continue
            file = open(file_path, 'rb')
            upload_data[form_key] = file
            files.append(file)
            
        # 对以 ".log" 为后缀的文件特殊处理
        log_files = []
        for file_name in os.listdir(model_dir):
            if not file_name.endswith(const.LOGS):
                continue
            file_path = os.path.join(model_dir, file_name)
            file = open(file_path, 'rb')
            log_files.append(file)
        
        if len(log_files) > 0:
            upload_data[const.MODEL_FILE_KEY_MAP[const.LOGS]] = log_files
            files.extend(log_files)
            
        # no file need to upload
        if len(upload_data) == 1:
            return
        
        client.upload_model_data_to_data_view(config.data_view_id, **upload_data)
    finally:
        for file in files:
            file.close()

@retry(wait=wait_exponential(multiplier=1, min=const.MIN_BACKOFF_IN_S, max=const.MAX_BACKOFF_IN_S), reraise=True, stop=(stop_after_attempt(const.STOP_AFTER_ATTEMPT_TIMES) | stop_after_delay(const.STOP_AFTER_DELAY_IN_S)), before=before_log, after=log_exception)
def upload_model_file(config: ModelConfig, model_file_key: str, model_file_path: str, client: DataViewApi):
    logger.info(f"begin to upload_model_file, data view id {config.data_view_id}, model file key {model_file_key}, model file path {model_file_path}")
    model_dir = config.model_dir
    upload_data = {"_content_type": 'multipart/form-data'}
    files = []
    
    try:
        # special for logs
        if model_file_key == const.LOGS:
            # 对以 ".log" 为后缀的文件特殊处理
            log_files = []
            for file_path in get_files_with_suffix_recursive(model_dir, const.LOGS):
                file = open(file_path, 'rb')
                log_files.append(file)
            
            if len(log_files) > 0:
                upload_data[const.MODEL_FILE_KEY_MAP[const.LOGS]] = log_files
                files.extend(log_files)
                
        else:
            file_path = os.path.join(model_dir, model_file_path)
            # wait the file to be created for 600 seconds
            logger.info(f'waiting for file {model_file_path} to be created')
            wait_condition_timeout(lambda: os.path.exists(file_path), timeout=const.FILE_NOT_EXISTS_TIMEOUT, interval=1, message=f"file {file_path} not exists")
            # wait the file data is ready for 600 seconds
            logger.info(f'waiting for file {model_file_path} to be ready')
            wait_condition_timeout(lambda: not is_file_operated(file_path), timeout=const.FILE_BEING_OPERATED_TIMEOUT, interval=1, message=f"file {file_path} is being operated for more than {const.FILE_BEING_OPERATED_TIMEOUT}")
            
            file = open(file_path, 'rb')
            upload_data[const.MODEL_FILE_KEY_MAP[model_file_key]] = file
            files.append(file)
        
        # no file need to upload
        if len(upload_data) == 1:
            return
        client.upload_model_data_to_data_view(config.data_view_id, **upload_data)
    except TimeoutError as ex:
        logger.warning(f"time out warning {str(ex)}")
        pass
    finally:
        for file in files:
            file.close()
        
class ModelWorker(object):
    def __init__(self, config: List[ModelConfig]):
        self.config = config
        
        for cfg in self.config:
            if not os.path.exists(cfg.model_dir):
                logger.info("create directory {}", cfg.model_dir)
                os.mkdir(cfg.model_dir)
    
        self.aifs_client = get_aifs_client()
        self.data_view_api = DataViewApi(self.aifs_client)
        
        self.details = {}
        for cfg in self.config:
            self.details[cfg.data_view_id] = self.data_view_api.get_data_view_details(cfg.data_view_id)
            if str(self.details[cfg.data_view_id][const.VIEW_TYPE]) != const.MODEL:
                self.__release_resource()
                raise InvalidArgument(f'data view {cfg.data_view_id} view type should be {const.MODEL}, but found {self.details[cfg.data_view_id][const.VIEW_TYPE]}')
        
        self.s3_client = get_s3_client()
        
        
        self.task_manager = TaskManager()
        self.task_manager.start()
        
        for cfg in self.config:
            if not hasattr(self.details[cfg.data_view_id], const.COMMIT_ID):
                id = f'save commit id to data view {cfg.data_view_id}'
                self.task_manager.add_task(id, Task(save_commit_id, args=[cfg.data_view_id, self.data_view_api]))
        
    def upload_model_file(self, config: ModelConfig, model_file_key: str, model_file_path: str = None):
        """upload model file to data view

        Args:
            config (ModelConfig): _description_
            model_file_key (str): _description_
            model_file_path (str, optional): the model file path. Defaults to None. If model file is logs, model file path should be None.
        """
        id = f'upload model data to data view id {config.data_view_id}, model file key {model_file_key}'
        self.task_manager.add_task(id, Task(upload_model_file, args=[config, model_file_key, model_file_path, self.data_view_api]))

    def finish(self):
        logger.info("stop task manager")
        self.task_manager.stop()
        
        self.__release_resource()
        
    def update_progress(self, progress: float):
        """update the progress of model trainning

        Args:
            progress (float): the value should be in [0, 100]

        Raises:
            InvalidArgument: progress < 0 or progress > 100
        """
        if progress < 0 or progress > 100:
            raise InvalidArgument(f"progress should be [0, 100], the input progress is {progress}")
        for cfg in self.config:
            id = f'update progress to data view id {cfg.data_view_id}'
            self.task_manager.add_task(id, Task(update_progress, args=[cfg.data_view_id, progress, self.data_view_api]))

    def get_progress(self) -> float:
        details = self.data_view_api.get_data_view_details(self.config[0].data_view_id)
        progress_str = details.get(const.PROGRESS, "0.0")
        return float(progress_str)

    def is_completed(self) -> bool:
        progress = self.get_progress()
        if progress + 1e-8 > 100.0:
            return True
        return False
   
    def pull(self, config: ModelConfig, model_files: List[str] = []):
        """pull data from remote server to local model directory
           
        Args:
            config (ModelConfig): _desc_
            model_files (List[str]): the model files you want to pull. See more in model file schema.
        """
        if len(model_files) == 0:
            return
        
        bucket_name = cfg["s3"]["bucket_name"]
        
        model_file_key_set = set(const.MODEL_FILE_KEY_MAP[file] for file in model_files)
        model_key_name_map = {val: key for key, val in const.MODEL_FILE_KEY_MAP.items()}
        locations = self.data_view_api.get_model_data_locations_in_data_view(config.data_view_id)
        # no data
        if not const.DATA_ITEMS in locations:
            return
        for location in locations[const.DATA_ITEMS].value:
            file_key = naming.camel_to_under(location[const.DATA_NAME])
            if file_key in model_file_key_set:
                file_path = os.path.join(config.model_dir, model_key_name_map[file_key])
                object_key = location[const.OBJECT_KEY]
                self.s3_client.download_file(bucket_name, object_key, file_path)
            elif const.MODEL_FILE_KEY_MAP[const.LOGS] in model_file_key_set and file_key.endswith('.log'):
                file_path = os.path.join(config.model_dir, location[const.DATA_NAME])
                object_key = location[const.OBJECT_KEY]
                self.s3_client.download_file(bucket_name, object_key, file_path)
        
    def __release_resource(self):
        logger.info("close api client")
        self.aifs_client.close()

# singleton
singleton: Optional[ModelWorker] = None
