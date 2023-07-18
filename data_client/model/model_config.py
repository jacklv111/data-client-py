#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


class ModelConfig:
    def __init__(self,
                 data_view_id: str,
                 model_dir: str
                 ):
        """data client model input parameters

        Args:
            data_view_id (str): the data view to save model data
            model_dir (str): the directory to save model data
        """
        self.data_view_id = data_view_id
        self.model_dir = model_dir
