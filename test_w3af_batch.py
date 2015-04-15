# coding: utf-8
import unittest
import threading as th
from time import time
from StringIO import StringIO
from Queue import Empty as EmptyQueue
from multiprocessing import Process
from multiprocessing import Queue
from threading import Event
from threading import Timer
from w3af_batch import run_starter
from w3af_batch import run_worker
from w3af_batch import run_pool


class Job(object):
    """Mock Job object."""

    def __init__(self, target=None, execution_time=0, ignore_stop=False):
        """Constructor for Job.
        
        :param target: each job is identified by its target
        :param execution_time: time of job execution
        :param ignore_stop: set this to test worker process termination
        """
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
        self._timer.start()
        self._timer.join()
    
    def stop(self):
        if self._ignore_stop:
            return
        self._timer.cancel()
        self._execute_job(self._execution_finished)

    def result(self):
        return (self._target, self._execution_finished.is_set())


class WorkerTest(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()
        self.targets_list = ['https://first.com/', 'https://second.com/']
        self.results = dict((t, True) for t in self.targets_list)

    def test_common_queue(self):
        """Test that two workers properly share common Queue."""
        kwargs = {'job': Job, 'report_queue': self.queue}
        for target in self.targets_list:
            target_kwargs = kwargs.copy()
            target_kwargs['target'] = target
            process = Process(target=run_worker, kwargs=target_kwargs)
            process.start()
            process.join()
        results = {}
        while True:
            try:
                target, result = self.queue.get(timeout=1)
            except EmptyQueue:
                break
            else:
                results[target] = result
        self.assertDictEqual(results, self.results)


class StarterTest(unittest.TestCase):
    execution_delta = 0.3

    def setUp(self):
        self.queue = Queue()

    def _run_starter(self, **kwargs):
        """
        Execute run_starter with predefined arguments. Calculate run time.
        All time periods are given in seconds.
        """
        start = time()
        run_starter(run_worker, job=Job, report_queue=self.queue, **kwargs)
        return time() - start

    def is_almost_equal(self, first, second):
        """*assertAlmostEqual* with special default delta."""
        self.assertAlmostEqual(first, second, delta=self.execution_delta)

    def test_starter_calls_executor(self):
        self._run_starter()
        self.assertIsInstance(self.queue.get(), tuple)

    def test_worker_lasts_execution_time(self):
        """Test mock Job object execution time."""
        execution_time = 1
        run_time = self._run_starter(execution_time=execution_time)
        self.is_almost_equal(run_time, execution_time)

    def test_worker_stops_after_timeout(self):
        execution_time = 2
        timeout = 1
        run_time = self._run_starter(
            execution_time=execution_time, timeout=timeout)
        self.is_almost_equal(run_time, timeout)

    def test_starter_terminates_worker_after_wait_timeout(self):
        execution_time = 2
        timeout = 0
        wait_timeout = 1
        run_time = self._run_starter(
            execution_time=execution_time, timeout=timeout,
            wait_timeout=wait_timeout, ignore_stop=True)
        self.is_almost_equal(run_time, wait_timeout)

    def test_common_queue(self):
        """Test that two starters properly share common Queue."""
        targets_list = ['https://first.com/', 'https://second.com/']
        targets_results = dict((t, True) for t in targets_list)
        kwargs = {'job': Job, 'report_queue': self.queue}
        for target in targets_list:
            target_kwargs = kwargs.copy()
            target_kwargs['target'] = target
            thread = th.Thread(
                target=run_starter,
                args=(run_worker,), kwargs=target_kwargs)
            thread.start()
            thread.join()
        results = {}
        while True:
            try:
                target, result = self.queue.get(timeout=1)
            except EmptyQueue:
                break
            else:
                results[target] = result
        self.assertDictEqual(results, targets_results)


class PoolTest(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()
        targets = ['https://first.com/', 'https://second.com/']
        self.targets = StringIO('\n'.join(targets))
        self.results = dict((t, True) for t in targets)

    def test_pool_processes_all_targets(self):
        run_pool(self.targets,
                 report_queue=self.queue,
                 job=Job,)
        results = {}
        while True:
            try:
                target, result = self.queue.get_nowait()
            except EmptyQueue:
                break
            else:
                results[target] = result
        self.assertDictEqual(results, self.results)
