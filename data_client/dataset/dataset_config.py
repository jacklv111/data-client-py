#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

from data_client.utils import const


class DatasetConfig:
    def __init__(self, delete_raw_data_with_no_annotation = True, 
                 # a working directory to put raw data and annotation data
                 dataset_dir = const.DEFAULT_DATASET_DIR,
                 ):
        self.delete_raw_data_with_no_annotation = delete_raw_data_with_no_annotation
        self.dataset_dir = dataset_dir