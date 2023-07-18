#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


import os
from typing import List, Optional

from aifs_client.api.data_view_api import DataViewApi
from loguru import logger
from tenacity import (retry, stop_after_attempt, stop_after_delay,
                      wait_exponential)

from data_client.artifact.artifact_config import ArtifactConfig
from data_client.utils import const
from data_client.utils.client import get_aifs_client, get_s3_client
from data_client.utils.condition import wait_condition_timeout
from data_client.utils.config import config as cfg
from data_client.utils.exception import InvalidArgument
from data_client.utils.file import is_file_operated
from data_client.utils.retry import before_log, log_exception
from data_client.utils.task import Task, TaskManager

from .artifact_config import ArtifactConfig


@retry(wait=wait_exponential(multiplier=1, min=const.MIN_BACKOFF_IN_S, max=const.MAX_BACKOFF_IN_S), reraise=True, stop=(stop_after_attempt(const.STOP_AFTER_ATTEMPT_TIMES) | stop_after_delay(const.STOP_AFTER_DELAY_IN_S)), before=before_log, after=log_exception)
def upload_artifact_file(config: ArtifactConfig, file_path: str, client: DataViewApi):
    logger.info(f"begin to upload_model_file, data view id {config.data_view_id}, file path {file_path}")
    local_dir = config.local_dir
    
    files = []
    
    try:
        file_path = os.path.join(local_dir, file_path)
        # wait the file to be created for 600 seconds
        logger.info(f'waiting for file {file_path} to be created')
        wait_condition_timeout(lambda: os.path.exists(file_path), timeout=const.FILE_NOT_EXISTS_TIMEOUT, interval=1, message=f"file {file_path} not exists")
        # wait the file data is ready for 600 seconds
        logger.info(f'waiting for file {file_path} to be ready')
        wait_condition_timeout(lambda: not is_file_operated(file_path), timeout=const.FILE_BEING_OPERATED_TIMEOUT, interval=1, message=f"file {file_path} is being operated for more than {const.FILE_BEING_OPERATED_TIMEOUT}")
        
        file = open(file_path, 'rb')
        
        client.upload_file_to_data_view(data_view_id=config.data_view_id, x_file_name=os.path.basename(file_path), body=file)
    except TimeoutError as ex:
        logger.warning(f"time out warning {str(ex)}")
        pass
    finally:
        for file in files:
            file.close()
            
class ArtifactWorker(object):
    def __init__(self, config: List[ArtifactConfig]):
        self.config = config
        
        for cfg in self.config:
            if not os.path.exists(cfg.local_dir):
                logger.info("create directory {}", cfg.local_dir)
                os.mkdir(cfg.local_dir)
    
        self.aifs_client = get_aifs_client()
        self.data_view_api = DataViewApi(self.aifs_client)
        
        self.details = {}
        for cfg in self.config:
            self.details[cfg.data_view_id] = self.data_view_api.get_data_view_details(cfg.data_view_id)
            if str(self.details[cfg.data_view_id][const.VIEW_TYPE]) != const.ARTIFACT:
                self.__release_resource()
                raise InvalidArgument(f'data view {cfg.data_view_id} view type should be {const.ARTIFACT}, but found {self.details[cfg.data_view_id][const.VIEW_TYPE]}')
        
        self.s3_client = get_s3_client()
        
        
        self.task_manager = TaskManager()
        self.task_manager.start()
        
    def upload_artifact_file(self, config: ArtifactConfig, file_path: str = None):
        """upload artifact file to data view

        Args:
            config (ModelConfig): _description_
            file_path (str, optional): the file path. Defaults to None.
        """
        id = f'upload artifact file to data view id {config.data_view_id}, file path {file_path}'
        self.task_manager.add_task(id, Task(upload_artifact_file, args=[config, file_path, self.data_view_api]))

    def finish(self):
        logger.info("stop task manager")
        self.task_manager.stop()
        
        self.__release_resource()
    
       
    def pull(self, config: ArtifactConfig):
        """pull data from remote server to local directory
           
        Args:
            data_view_id (str): the data view to save artifact files
        """
      
        bucket_name = cfg["s3"]["bucket_name"]
        
        locations = self.data_view_api.get_artifact_locations_in_data_view(
            data_view_id=config.data_view_id
        )
        if not const.DATA_ITEMS in locations:
            return
        for location in locations[const.DATA_ITEMS].value:
            file_name = location[const.DATA_NAME]
            file_path = os.path.join(config.local_dir, file_name)
            object_key = location[const.OBJECT_KEY]
            self.s3_client.download_file(bucket_name, object_key, file_path)
        
    def __release_resource(self):
        logger.info("close api client")
        self.aifs_client.close()

# singleton
singleton: Optional[ArtifactWorker] = None