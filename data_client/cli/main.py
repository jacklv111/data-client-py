#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

import os
from pathlib import Path

import click
from aifs_client.api.data_view_api import DataViewApi

from data_client.artifact import artifact
from data_client.artifact.artifact_config import ArtifactConfig
from data_client.utils import const, naming, parser
from data_client.utils.client import get_aifs_client, get_s3_client
from data_client.utils.config import config as cfg
from data_client.utils.config import save_config
from data_client.utils.exception import InvalidArgument


@click.group()
def aifsctl():
    """cli tool for data
    """

@aifsctl.command()
@click.option('--aifs_ip')
@click.option('--aifs_port')
@click.option('--s3_bucket_name')
@click.option('--s3_ak')
@click.option('--s3_sk')
@click.option('--s3_endpoint')
@click.option('--s3_region')
def config(aifs_ip, aifs_port, s3_bucket_name, s3_ak, s3_sk, s3_endpoint, s3_region):
    if aifs_ip is not None:
        cfg["aifs"]["ip"] = aifs_ip
    if aifs_port is not None:
        cfg["aifs"]["port"] = aifs_port
    if s3_bucket_name is not None:
        cfg["s3"]["bucket_name"] = s3_bucket_name
    if s3_ak is not None:
        cfg["s3"]["ak"] = s3_ak
    if s3_sk is not None:
        cfg["s3"]["sk"] = s3_sk
    if s3_endpoint is not None:
        cfg["s3"]["endpoint"] = s3_endpoint
    if s3_region is not None:
        cfg["s3"]["region"] = s3_region
    
    save_config(cfg)
    
@aifsctl.command()
@click.option('--data_view_id', prompt='choose data view to download')
@click.option('--local_dir', prompt='choose directory to save the file')
def download(data_view_id, local_dir):
    local_dir = Path(local_dir).expanduser().resolve()
    bucket_name = cfg["s3"]["bucket_name"]
    aifs_client = get_aifs_client()
    s3_client = get_s3_client()
    data_view_api = DataViewApi(aifs_client)
    details = data_view_api.get_data_view_details(data_view_id=data_view_id)
    data_view_type = str(details[const.VIEW_TYPE])
    if data_view_type == const.DATASET_ZIP:
        location = data_view_api.get_dataset_zip_location_in_data_view(data_view_id=data_view_id)[const.DATA_ITEMS].value[0]
        object_key = location[const.OBJECT_KEY]
        file_name = location[const.DATA_ITEM_ID] + os.path.splitext(location[const.DATA_NAME])[1]
        local_path = os.path.join(local_dir, file_name)
        s3_client.download_file(bucket_name, object_key, local_path)
        click.echo(local_path)
    elif data_view_type == const.MODEL:
        locations = data_view_api.get_model_data_locations_in_data_view(data_view_id=data_view_id)
        if not const.DATA_ITEMS in locations:
            return
        for location in locations[const.DATA_ITEMS].value:
            file_name = naming.camel_to_under(location[const.DATA_NAME])
            file_path = os.path.join(local_dir, file_name)
            object_key = location[const.OBJECT_KEY]
            s3_client.download_file(bucket_name, object_key, file_path)
    elif data_view_type == const.RAW_DATA:
        locations = data_view_api.get_all_raw_data_locations_in_data_view(
            data_view_id=data_view_id
        )
        if not const.DATA_ITEMS in locations:
            return
        raw_data_list = parser.parse_raw_data_locations(
            locations = locations, 
            raw_data_dir = local_dir
        )
        for raw_data_info in raw_data_list:
            s3_client.download_file(bucket_name, raw_data_info[const.OBJECT_KEY], raw_data_info[const.LOCAL_PATH])
    elif data_view_type == const.ARTIFACT:
        [arti] = artifact.init([ArtifactConfig(data_view_id=data_view_id, local_dir=local_dir)])
        arti.pull()
    else:
        raise InvalidArgument(f"it doesn't support to download {data_view_type} type now")

@aifsctl.command()
def showconfig():
    click.echo({section: dict(cfg[section]) for section in cfg.sections()})
