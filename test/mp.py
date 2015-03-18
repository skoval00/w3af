import unittest
import multiprocessing as mp
import multiprocessing.dummy as mpd
import threading as th
import time
import sys


class StoppableThread(th.Thread):
    def __init__(self, event, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.event = event

    def activity(self):
        pass

    def handler(self):
        if self.event.wait(1):
            raise Exception

    def run(self):
        t_handler = mpd.Process(target=self.handler)
        t_handler.start()
        t_activity = mpd.Process(target=self.activity)
        t_activity.start()
        t_activity.join()
        t_handler.join()


class PoolTest(unittest.TestCase):
    @unittest.skip('Failed')
    def test_event(self):
        self.event.set()
        self.second.join()
        self.assertEqual(0, self.process.exitcode)
        self.assertFalse(self.process.is_alive())


class ThreadedProcess(mp.Process):
    def __init__(self, pipe, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.pipe = pipe
        self.threads = set()

    def threadcount(self):
        return len(self.threads)

    def activity(self):
        message = (mp.current_process().pid,
                   th.current_thread().name)
        self.pipe.send(message)

    def start_thread(self, name=None):
        """Register thread with given name."""
        if name is None:
            thread = th.current_thread()
            name = thread.name
        else:
            thread = th.Thread(target=getattr(self, name), name=name)
            thread.start()
        self.threads.add(name)
        return thread

    def run(self):
        self.start_thread()
        thread = self.start_thread('activity')
        message = (mp.current_process().pid,
                   th.current_thread().name)
        self.pipe.send(message)
        thread.join()


class ThreadedChildTest(unittest.TestCase):
    def setUp(self):
        self.queue = mp.Queue()
        self.pipe, child = mp.Pipe()
        self.event = mp.Event()
        self.process = ThreadedProcess(pipe=child)
        self.process.start()
        self.second = SimpleThreadedProcess(event=self.event)
        self.second.start()

    def tearDown(self):
        self.process.join()

    def test_is_alive(self):
        self.assertTrue(self.process.is_alive())

    def test_pipe(self):
        threads = self.process.threads.copy()

        for _ in xrange(self.process.threadcount()):
            pid, tid = self.pipe.recv()
            self.assertEqual(pid, self.process.pid)
            threads.remove(tid)

        self.assertSetEqual(threads, set())
