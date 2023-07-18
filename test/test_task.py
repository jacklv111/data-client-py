#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#


import unittest

from loguru import logger

from data_client.utils.task import Task, TaskManager


class TestModel(unittest.TestCase):
    """dataset unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass
        
    def testTaskManager(self):
        args = [self, "test", True, 10, 0]
        def fake_task(self, param1: str, param2: bool, param3: int, count: int):
            logger.info(f"fake_task called, param 1: {param1}, param 2: {param2}, param 3: {param3}")
            self.assertEqual(param1, args[1])
            self.assertEqual(param2, args[2])
            self.assertEqual(param3, args[3])
            args[4]+=1
        
        mgr = TaskManager(interval_s = 0.05)
        for _ in range(100):
            mgr.add_task("test_task", Task(fake_task, args))
        mgr.start()
        mgr.stop()
        self.assertIsNone(mgr.get_exception())
        # the task comes later will overwrite the previous one with the same name if it is not executing yet
        self.assertEqual(args[4], 1)
  
if __name__ == '__main__':
    unittest.main()
