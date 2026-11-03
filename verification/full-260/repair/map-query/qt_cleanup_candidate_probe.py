"""Real Qt worker delivery and object-destruction check of optional cleanup."""
import faulthandler
import importlib.util
import json
from pathlib import Path
import threading

faulthandler.enable(all_threads=True)
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QApplication, QWidget
import shiboken6

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('candidate_qt_cleanup', HERE / 'candidate/scripts/qt_verification_cleanup.py')
cleanup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup)
app = QApplication([])
widgets = [QWidget() for _ in range(3)]
for widget in widgets: widget.show()
done = threading.Event()
delivered = []

class Signals(QObject):
    finished = Signal(str)

class Worker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = Signals()
    def run(self):
        done.set()
        self.signals.finished.emit('literal-public-work-completed')

worker = Worker()
worker.signals.finished.connect(delivered.append)
QThreadPool.globalInstance().start(worker)
report = cleanup.shutdown_verification_qt()
assert done.is_set()
assert delivered == ['literal-public-work-completed'], delivered
assert not any(shiboken6.isValid(widget) for widget in widgets)
assert QApplication.instance() is None
assert cleanup.shutdown_verification_qt()['application_present'] is False
print(json.dumps({'cleanup_report': report, 'worker_completed': done.is_set(),
                  'queued_result_delivered_before_destroy': delivered,
                  'all_test_widgets_destroyed': True, 'second_no_application_call': True}), flush=True)
