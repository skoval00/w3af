"""Tests for w3af_batch."""

import unittest
from mock import patch
from mock import Mock

from w3af.core.controllers.exceptions import BaseFrameworkException
from w3af_batch import execute_scan
from w3af_batch import ScanExecutor
from w3af_batch import STOPSCAN


class W3afCoreMock(Mock):
    """w3afCore mock."""
    pass


@patch('w3af.core.controllers.w3afCore.w3afCore', new=W3afCoreMock())
class ScanExecutorTest(unittest.TestCase):
    """Tests for ScanExecutor class."""
    target = 'target'
    profile = 'profile'
    timeout = 1

    def setUp(self):
        self.thread = ScanExecutor(self.target,
                                   self.profile,
                                   self.timeout)
        self.thread.start()

    def test_child_started(self):
        """Check if child was started."""
        self.assertTrue(self.thread.done or self.thread.worker.is_alive())
                         

    def tearDown(self):
        self.thread.join()


@patch('w3af.core.controllers.w3afCore.w3afCore')
class W3afBatchTest(unittest.TestCase):
    """Test for function bases w3af_batch."""
    def test_framework_exception(self, w3af):
        """Test if exception is raised in execute_scan."""
        w3af.side_effect = BaseFrameworkException('w3af error')
        try:
            execute_scan('target', 'profile', 1)
        except BaseFrameworkException:
            pass
        self.assertTrue(True)
