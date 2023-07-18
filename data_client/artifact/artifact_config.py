#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

class ArtifactConfig:
    def __init__(self,
                 data_view_id: str,
                 local_dir: str
                 ):
        """data client artifact input parameters

        Args:
            data_view_id (str): the data view to save model data
            local_dir (str): the directory to save model data
        """
        self.data_view_id = data_view_id
        self.local_dir = local_dir
