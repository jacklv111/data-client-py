#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

from aifs_client import ApiClient as AifsClient
from aifs_client import Configuration as ClientConfig
from boto3.session import Session

from data_client.utils.config import config


# aifs client ------------------------------------
def get_client_config() -> ClientConfig:
    res = ClientConfig(
        # openapi generator 自动生成的 client 没有包含 path prefix，只能在此添加 path prefix
        host=config["aifs"]["host"]
    )
    res.verify_ssl = config["aifs"].getboolean("verify_ssl")
    return res

def get_aifs_client() -> AifsClient:
    return AifsClient(
        configuration = get_client_config()
    )

# s3 client ---------------------------------------
def get_s3_client():
    session = Session(config["s3"]["ak"], config["s3"]["sk"])
    return session.client(
        region_name = config["s3"]["region"],
        endpoint_url = config["s3"]["endpoint"],
        use_ssl = config["s3"].getboolean("use_ssl"),
        service_name = config["s3"]["service_name"],
    )