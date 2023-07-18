#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


from typing import Callable, List

from loguru import logger

from data_client.utils.exception import ArtifactError

from . import artifact_worker
from .artifact_config import ArtifactConfig
from .artifact_data import ArtifactData


def empty_func():
     raise ArtifactError("call model.init() to initialize")

finish: Callable = empty_func

def init(config: List[ArtifactConfig]) -> List[ArtifactData]:
    logger.info('artifact init')
    global finish

    artifact_worker.singleton = artifact_worker.ArtifactWorker(config)
    finish = artifact_worker.singleton.finish

    artifact_list = []
    for cfg in config:
        artifact_list.append(ArtifactData(cfg))
    return artifact_list