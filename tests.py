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


class W3afCoreMock(mock.MagicMock):
    """w3afCore mock."""
    pass


class ScanExecutorBaseTest(unittest.TestCase):
    target = 'target'
    profile = 'profile'
    timeout = 1

    def setUp(self):
        kb = imp.new_module('w3af.core.data.kb.knowledge_base')
        kb.kb = mock.MagicMock()
        sys.modules[kb.__name__] = kb
        self.executor = ScanExecutor(
            self.target, self.profile, self.timeout)


class ScanExecutorRunTest(ScanExecutorBaseTest):
    """Tests for ScanExecutor class."""

    def setUp(self):
        w3afCore = imp.new_module('w3af.core.controllers.w3afCore')
        w3afCore.w3afCore = mock.MagicMock()
        sys.modules[w3afCore.__name__] = w3afCore
        super(self.__class__, self).setUp()

    def test_child_started(self):
        """Check if child was started."""
        self.assertFalse(self.executor.started.is_set())
        self.executor.start()
        self.assertTrue(self.executor.started.wait())


class ScanExecutorExceptionTest(ScanExecutorBaseTest):
    """Docstring for ScanExecutorExceptionTest. """

    def setUp(self):
        w3afCore = imp.new_module('w3af.core.controllers.w3afCore')
        w3afCore.w3afCore = mock.MagicMock(side_effect=BaseFrameworkException)
        sys.modules[w3afCore.__name__] = w3afCore
        super(self.__class__, self).setUp()

    def test_w3af_exception(self):
        self.assertRaises(BaseFrameworkException, self.executor.start)


@unittest.skip('Obsolete')
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
