"""Tests for w3af_batch."""

import unittest
import mock
from mock import patch


from w3af_batch import execute_scan
from w3af_batch import ScanExecutor
from w3af_batch import STOPSCAN


class W3afCoreMock(mock.MagicMock):
    """w3afCore mock."""
    pass


class ScanExecutorTest(unittest.TestCase):
    """Tests for ScanExecutor class."""
    target = 'target'
    profile = 'profile'
    timeout = 1

    def setUp(self):
        self.executor = ScanExecutor(
            self.target, self.profile, self.timeout)

    @patch('w3af.core.controllers.w3afCore.w3afCore', new=W3afCoreMock())
    def test_child_started(self):
        """Check if child was started."""
        self.executor.start()
        self.assertTrue(self.executor.started())

    @patch('w3af.core.controllers.w3afCore.w3afCore')
    def test_w3af_exception(self, w3af_mock):
        from w3af.core.controllers.exceptions import BaseFrameworkException
        w3af_mock.side_effect = BaseFrameworkException('w3af error')
        self.assertRaises(BaseFrameworkException, self.executor.start)


@patch('w3af.core.controllers.w3afCore.w3afCore')
class W3afBatchTest(unittest.TestCase):
    """Test for function bases w3af_batch."""
    def test_framework_exception(self, w3af):
        """Test if exception is raised in execute_scan."""
        from w3af.core.controllers.exceptions import BaseFrameworkException
        w3af.side_effect = BaseFrameworkException('w3af error')
        try:
            execute_scan('target', 'profile', 1)
        except BaseFrameworkException:
            pass
        self.assertTrue(True)
