#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


from configparser import ConfigParser

from data_client.utils import const

from .config_file import get_file_abs_path

config = ConfigParser()
config.read(get_file_abs_path(const.CONFIG_FILE), encoding='UTF-8')

def save_config(config: ConfigParser):
    """write the config to config file

    Args:
        config (ConfigParser): current config data
    """
    with open(get_file_abs_path(const.CONFIG_FILE), mode='w', encoding='UTF-8') as config_file:
        config.write(config_file)
