#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


from typing import Callable, List

from data_client.model import model_worker
from data_client.model.model_config import ModelConfig
from data_client.model.model_data import ModelData
from data_client.utils.exception import ModelError


def empty_func():
     raise ModelError("call model.init() to initialize")

finish: Callable = empty_func
update_progress: Callable = empty_func
get_progress: Callable = empty_func
is_completed:Callable = empty_func

def init(config: List[ModelConfig]) -> List[ModelData]:
     global finish
     global update_progress
     global get_progress
     global is_completed
     
     model_worker.singleton = model_worker.ModelWorker(config)
     finish = model_worker.singleton.finish
     update_progress = model_worker.singleton.update_progress
     get_progress = model_worker.singleton.get_progress
     is_completed = model_worker.singleton.is_completed
     
     model_data_list = []
     for cfg in config:
          model_data_list.append(ModelData(cfg))
     return model_data_list
