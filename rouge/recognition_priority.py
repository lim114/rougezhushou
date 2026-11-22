"""Cooperative current-frame priority between bounded full-page readers."""
from contextlib import contextmanager
from contextvars import ContextVar
from threading import Condition


_current_wait = ContextVar('rouge_reader_wait', default=None)


def yield_to_current():
    wait = _current_wait.get()
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
        token = _current_wait.set(wait)
        try:
            wait()
            yield
        finally:
            _current_wait.reset(token)
            with self.condition:
                del self.pending[job_id]
                self.condition.notify_all()
