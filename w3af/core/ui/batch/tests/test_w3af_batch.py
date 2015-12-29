# coding: utf-8
"""
test_w3af_batch.py

Copyright 2015 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
import os
import unittest
import multiprocessing as mp

from time import time
from time import sleep
from StringIO import StringIO
from Queue import Empty as EmptyQueue
from signal import SIGINT
from multiprocessing import Queue
from threading import Event
from threading import Timer

from w3af.core.ui.batch.main import Worker
from w3af.core.ui.batch.main import Manager
from w3af.core.ui.batch.main import Pool


def _send_interrupt(pid):
    os.kill(pid, SIGINT)


class Job(object):
    """Create Job object that lasts execution_time seconds.

    Do not cancel job if ignore_stop is set. It is used simulate hanging job.

    :author: https://github.com/skoval00
    """

    def __init__(self, target=None, execution_time=0, ignore_stop=False):
        self._target = target
        self._execution_time = execution_time
        self._execution_finished = Event()
        self._ignore_stop = ignore_stop
        self._timer = Timer(execution_time, self._execute_job,
                            args=(self._execution_finished,))

    @staticmethod
    def _execute_job(execution_finished):
        execution_finished.set()

    def start(self):
        """Start job execution."""
        self._timer.start()
        self._timer.join()
    
    def stop(self):
        """Cancel job execution."""
        if self._ignore_stop:
            return
        self._timer.cancel()
        self._execute_job(self._execution_finished)

    def result(self):
        """Return job id(target) and execution status."""
        return (self._target, self._execution_finished.is_set())


class BaseTest(unittest.TestCase):
    """Base class for Worker and Starter test classes.

    :author: https://github.com/skoval00
    """

    def setUp(self):
        self.queue = Queue()

    def tearDown(self):
        """Wait for child processes and threads to finish."""
        sleep(0.1)

    def assertAlmostEqual(self, first, second):
        """assertAlmostEqual with special delta.
        
        This delta fits our needs because we test integer periods.
        """
        super(BaseTest, self).assertAlmostEqual(first, second, delta=0.3)

    def _run_helper(self, **kwargs):
        """
        Execute test_class.run() with predefined arguments. Calculate run time.
        All time periods are given in seconds.
        """
        start = time()
        self.test_class.run(job=Job, report_queue=self.queue, **kwargs)
        return time() - start


class WorkerTest(BaseTest):
    test_class = Worker

    def test_worker_lasts_execution_time(self):
        """Test mock Job object execution time."""
        execution_time = 1
        run_time = self._run_helper(execution_time=execution_time)
        self.assertAlmostEqual(run_time, execution_time)

    def test_worker_stops_after_timeout(self):
        """Test if worker stops after timeout."""
        execution_time = 2
        timeout = 1
        run_time = self._run_helper(execution_time=execution_time,
                                    timeout=timeout)
        self.assertAlmostEqual(run_time, timeout)

    def test_worker_sends_result(self):
        self._run_helper(target='target')
        self.assertEqual(('target', True), self.queue.get(timeout=1))


class ManagerTest(BaseTest):
    test_class = Manager

    def test_manager_runs_worker(self):
        run_time = self._run_helper(target='target')
        self.assertEqual(('target', True), self.queue.get(timeout=1))

    def test_manager_terminates_worker_after_wait_timeout(self):
        execution_time = 2
        timeout = 0
        wait_timeout = 1
        run_time = self._run_helper(
            execution_time=execution_time, timeout=timeout,
            wait_timeout=wait_timeout, ignore_stop=True)
        self.assertAlmostEqual(run_time, wait_timeout)


class PoolTest(BaseTest):
    test_class = Pool

    def setUp(self):
        super(PoolTest, self).setUp()
        targets = ['https://first.com/', 'https://second.com/']
        self.targets = StringIO('\n'.join(targets))
        self.results = dict((t, True) for t in targets)

    def test_pool_processes_all_targets(self):
        self._run_helper(targets=self.targets)
        results = {}
        while True:
            try:
                target, result = self.queue.get_nowait()
            except EmptyQueue:
                break
            else:
                results[target] = result
        self.assertDictEqual(results, self.results)

    def test_interrupt_stops_execution(self):
        process = mp.Process(target=Pool.run,
                             args=(self.targets,),
                             kwargs={'job': Job, 'execution_time': 2})
        start = time()
        process.start()
        sender = Timer(1, _send_interrupt, (process.pid,))
        sender.start()
        process.join()
        sender.join()
        self.assertAlmostEqual(1, time() - start)
