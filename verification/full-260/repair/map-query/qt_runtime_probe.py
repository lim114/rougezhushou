"""Run original245 Qt-named classes, preserving failures and normal process exit."""
import faulthandler
import json
from pathlib import Path
import sys
import unittest

faulthandler.enable(all_threads=True)
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_full_available import AvailableResult
selectors = json.loads((ROOT / 'verification/full-245/linux.json').read_text(encoding='utf-8'))['selectors']
loaded = unittest.defaultTestLoader.loadTestsFromNames(selectors)

def cases(suite):
    for value in suite:
        if isinstance(value, unittest.TestSuite): yield from cases(value)
        else: yield value

qt_cases = [case for case in cases(loaded)
            if any(word in type(case).__name__ for word in ('View', 'Widget', 'Window', 'Panel', 'Dialog'))]
print(json.dumps({'source_selectors': 'verification/full-245/linux.json',
                  'total_original_selectors': len(selectors), 'qt_named_cases': len(qt_cases),
                  'full_scope_replaced': False}), flush=True)
result = unittest.TextTestRunner(verbosity=1, resultclass=AvailableResult).run(unittest.TestSuite(qt_cases))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, QEvent, QThreadPool
import shiboken6
app = QApplication.instance()
widgets = list(app.topLevelWidgets()) if app else []
print(json.dumps({'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
                  'top_level_widgets_before_shutdown': len(widgets),
                  'valid_wrappers_before_shutdown': sum(shiboken6.isValid(widget) for widget in widgets),
                  'active_pool_threads': QThreadPool.globalInstance().activeThreadCount()}), flush=True)
if '--shutdown' in sys.argv and app:
    for widget in widgets:
        widget.close()
        widget.deleteLater()
    app.processEvents()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    if not QThreadPool.globalInstance().waitForDone(5000):
        raise RuntimeError('Qt worker pool did not finish; shutdown failed.')
    app.shutdown()
    print(json.dumps({'qt_application_destroyed': QApplication.instance() is None,
                      'valid_widget_wrappers_after_shutdown': sum(shiboken6.isValid(widget) for widget in widgets)}), flush=True)
sys.exit(0 if result.wasSuccessful() else 1)
