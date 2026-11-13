"""Cooperative current-frame priority between bounded full-page readers."""
from contextlib import contextmanager
from threading import Condition, local


_reader_thread = local()


def yield_to_current():
    wait = getattr(_reader_thread, 'wait', None)
    if wait is not None:wait()


class ReadPriority:
    def __init__(self):
        self.condition = Condition()
        self.pending = {}

    def register(self, job_id, seq):
        with self.condition:
            self.pending[job_id] = seq

    @contextmanager
    def read(self, job_id):
        def wait():
            with self.condition:
                self.condition.wait_for(lambda: self.pending[job_id] == max(self.pending.values()))
        _reader_thread.wait = wait
        try:
            wait()
            yield
        finally:
            del _reader_thread.wait
            with self.condition:
                del self.pending[job_id]
                self.condition.notify_all()
