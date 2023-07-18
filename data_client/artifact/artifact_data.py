#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

from typing import List

from . import artifact_worker
from .artifact_config import ArtifactConfig


class ArtifactData(object):
    def __init__(self, config: ArtifactConfig):
        self.config = config
    
    def upload_file(self, file_path: str = None):
        artifact_worker.singleton.upload_artifact_file(self.config, file_path)
        
    def pull(self):
        artifact_worker.singleton.pull(self.config)
