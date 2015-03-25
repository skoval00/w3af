"""Tests for w3af_batch."""

import sys
import imp
import unittest
import mock
from mock import patch

from w3af.core.controllers.exceptions import BaseFrameworkException
from w3af_batch import execute_scan
from w3af_batch import ScanExecutor
from w3af_batch import STOPSCAN


class ScanExecutorBaseTest(unittest.TestCase):
    target = 'target'
    profile = 'profile'
    timeout = 1
    event_timeout = 1

    def setUp(self):
        """Mock used w3af modules."""
        w3afCore_module = imp.new_module('w3af.core.controllers.w3afCore')
        from w3af.core.controllers.w3afCore import w3afCore
        w3afCore_module.w3afCore = mock.MagicMock(spec=w3afCore)
        self.setUpW3afCore(w3afCore_module.w3afCore)
        sys.modules[w3afCore_module.__name__] = w3afCore_module
        self.executor = ScanExecutor(
            self.target, self.profile, self.timeout)
        self.executor.start()

    def setUpW3afCore(self, w3afCore):
        pass

    def tearDown(self):
        del sys.modules['w3af.core.controllers.w3afCore']


class W3afCoreSuccessTest(ScanExecutorBaseTest):
    """Successful run of w3afCore scan."""

    def test_success(self):
        """Test successful run."""
        self.assertTrue(self.executor.success.wait(self.event_timeout))
        self.assertFalse(self.executor.failure.is_set())


class W3afCoreInitExceptionTest(ScanExecutorBaseTest):
    """Raise exception in w3afCore init."""

    def setUpW3afCore(self, w3afCore):
        w3afCore.side_effect = BaseFrameworkException('failure')

    def test_w3af_init_failure(self):
        self.assertTrue(self.executor.failure.wait(self.event_timeout))
        self.assertFalse(self.executor.success.is_set())


class W3afCoreStartExceptionTest(ScanExecutorBaseTest):
    """Raise exception in w3afCore.start."""

    def setUp(self):
        w3afCore_module = imp.new_module('w3af.core.controllers.w3afCore')
        from w3af.core.controllers.w3afCore import w3afCore
        w3afCore_module.w3afCore = mock.MagicMock()
        w3afCore_module.w3afCore.start = mock.MagicMock(
            side_effect=BaseFrameworkException('failure'))
        sys.modules[w3afCore_module.__name__] = w3afCore_module
        self.executor = ScanExecutor(
            self.target, self.profile, self.timeout)
        self.executor.start()

    def setUpW3afCore(self, w3afCore):
        attrs = {'start.side_effect': BaseFrameworkException('failure')}
        w3afCore.configure_mock(**attrs)

    def test_w3af_start_failure(self):
        self.assertTrue(self.executor.failure.wait(self.event_timeout))
        self.assertFalse(self.executor.success.is_set())


@unittest.skip('')
class W3afCoreTimeoutTest(ScanExecutorBaseTest):
    def test_timeout(self):
        self.assertFalse(self.executor.success.is_set())
        self.assertFalse(self.executor.failure.is_set())
