#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

import concurrent.futures
import threading
import time
from typing import Dict

from loguru import logger

from data_client.utils import const

from .task import Task


class TaskManager(threading.Thread):
    def __init__(self, interval_s: float = 1):
        super(TaskManager, self).__init__()
        self._stop_event = threading.Event()
        self.tasks: Dict[str, Task] = {}
        self.executor: concurrent.futures.ThreadPoolExecutor = concurrent.futures.ThreadPoolExecutor(max_workers=const.MAX_WORKERS)
        self.futures = {}
        # protect tasks
        self._lock = threading.Lock()
        self.interval_s = interval_s
        self.exception = None

    def run(self):
        # stop when all tasks are done and stop event is set
        while not self._stop_event.is_set() or len(self.tasks) > 0 or len(self.futures) > 0:
            if self._stop_event.is_set():
                logger.debug(f"stop event is set, stop task manager, tasks: {self.tasks.keys()}, futures: {self.futures.keys()}")
            with self._lock:
                self._exec_new_tasks()
            self._maintain_futures()
            time.sleep(self.interval_s)
        
        logger.info("shutdown executor")
        self.executor.shutdown()
        
    def add_task(self, task_id: str, task: Task):
        with self._lock:
            self.tasks[task_id] = task
            
    def _exec_new_tasks(self):
        delete_keys = []
        for task_id, task in self.tasks.items():
            if task_id not in self.futures:
                self.futures[task_id] = self.executor.submit(task.func, *task.args, **task.kwargs)
                delete_keys.append(task_id)
                
        for key in delete_keys:
            del self.tasks[key]
            
    def _maintain_futures(self):
        delete_keys = []
        for task_id, future in self.futures.items():
            if future.done():
                delete_keys.append(task_id)
            if future.exception() is not None:
                self.exception = future.exception()
        for key in delete_keys:
            del self.futures[key]
    
    def stop(self):
        self._stop_event.set()
        self.join()
        
    def get_exception(self):
        return self.exception