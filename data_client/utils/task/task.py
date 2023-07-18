#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

from typing import Callable, Dict, List


class Task(object):
    def __init__(self, func: Callable, args: List = [], kwargs: Dict = {}):
        self.func = func
        self.args = args
        self.kwargs = kwargs