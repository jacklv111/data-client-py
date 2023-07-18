#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

from loguru import logger
from tenacity import RetryCallState
from tenacity import _utils as tenacity_util


def log_exception(retry_state : RetryCallState):
    if retry_state.attempt_number <= 1:
        return
    
    try:
        retry_state.outcome.result()
    except Exception as exception:
        logger.exception(exception)

def before_log(retry_state : RetryCallState):
    if retry_state.attempt_number > 1:
        logger.info(f"Starting call to '{tenacity_util.get_callback_name(retry_state.fn)}', "
            f"this is the {tenacity_util.to_ordinal(retry_state.attempt_number)} time calling it.")
