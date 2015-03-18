#!/usr/bin/env python
# encoding: utf-8

import logging
import unittest
import multiprocessing.dummy as mpd
from Queue import Empty


class PoolTestCase(unittest.TestCase):
    def setUp(self):
        def activity(queue):
            queue.put_nowait(mpd.current_process())
        self.workers = 2
        self.queue = mpd.Queue()
        self.pool = mpd.Pool(self.workers, activity, (self.queue,))

    def tearDown(self):
        self.pool.close()
        self.pool.join()

    def test_active_childern_quantity(self):
        """Number of workers in pool."""
        self.assertEqual(self.workers, len(mpd.active_children()))

    def test_active_children_entity(self):
        """Class of active children."""
        for worker in mpd.active_children():
            self.assertIsInstance(worker, mpd.DummyProcess)

    def test_current_process_name(self):
        self.assertEqual(mpd.current_process().getName(), 'MainThread')

    def test_pool_queue(self):
        self.assertEqual(self.queue.qsize(), self.workers)
        for _ in xrange(self.workers):
            item = self.queue.get_nowait()
            self.assertIsInstance(item, mpd.DummyProcess)
            self.assertTrue(item.isAlive())
        self.assertRaises(Empty, self.queue.get_nowait)
