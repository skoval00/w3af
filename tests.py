#!/usr/bin/env python
# encoding: utf-8

import logging
import unittest
import threading as th
from StringIO import StringIO
from mock import patch
from mock import Mock

from w3af.core.controllers.exceptions import BaseFrameworkException
from w3af_batch import execute_scan
from w3af_batch import ScanExecutor
from w3af_batch import STOPSCAN


class w3afCoreMock(Mock):
    pass


@patch('w3af.core.controllers.w3afCore.w3afCore', new=w3afCoreMock())
class ScanExecutorTest(unittest.TestCase):
    target = 'target'
    profile = 'profile'
    timeout = 1

    def setUp(self):
        self.log = StringIO()
        logging.basicConfig(stream=self.log,
                            level=logging.DEBUG,
                            format='%(message)s')
        self.thread = th.Thread(target=ScanExecutor(self.target,
                                                    self.profile,
                                                    self.timeout))
        self.thread.start()

    def test_child_started(self):
        self.assertEqual(self.log.getvalue(),
                         'Scan started: %s\n' % self.target)
                         

    def tearDown(self):
        self.thread.join()


class LoggerTest(unittest.TestCase):
    def setUp(self):
        self.log = StringIO()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(stream=self.log,
                            level=logging.DEBUG,
                            format='%(message)s')

    def test_stream_handler(self):
        self.logger.debug('Test')
        self.assertEqual('Test\n', self.log.getvalue())


@patch('w3af.core.controllers.w3afCore.w3afCore')
class w3afBatchTest(unittest.TestCase):
    def test_execute_scan_framework_exception(self, w3af):
        w3af.side_effect = BaseFrameworkException('w3af error')
        try:
            execute_scan('target', 'profile', 1)
        except BaseFrameworkException:
            pass
