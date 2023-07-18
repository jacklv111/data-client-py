#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


import time
from typing import Callable


def wait_condition_timeout(
    condition: Callable[[], bool],
    timeout: int,
    interval: int = 1,
    message: str = 'Timeout'
) -> None:
    """
    Wait for condition to be true until timeout
    :param condition: condition to be checked
    :param timeout: timeout in seconds
    :param interval: interval in seconds
    :param message: message to be printed when timeout
    """
    wait_time = 0
    while wait_time < timeout:
        if condition():
            return
        time.sleep(interval)
        wait_time += interval
    raise TimeoutError(message)
