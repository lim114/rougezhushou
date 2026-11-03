"""Explicit historical diagnostics fixture constructor; normal public UI/API only."""
import atexit
import hashlib
import json
import os
import sys
from pathlib import Path

ACTIVE=[]


def install(root, out):
    if sys.platform != 'win32':
        raise RuntimeError('This fixture bootstrap requires actual Windows')
    root=Path(root).resolve();out=Path(out).resolve()
    import rouge.app as module
    from PySide6.QtWidgets import QApplication
    import win32gui
    original=module.MainWindow
    records=[]
    restored=False

    class HistoricalDiagnostics275(original):
        def __init__(self, *args, **kwargs):
            if 'include_historical_route_diagnostics' in kwargs and kwargs['include_historical_route_diagnostics'] is not True:
                raise ValueError('The complete historical validation fixture must explicitly enable historical diagnostics')
            kwargs['include_historical_route_diagnostics']=True
            super().__init__(*args, **kwargs)
            app=QApplication.instance()
            row={'kind':'normal_public_constructor',
                 'include_historical_route_diagnostics':True,
                 'product_default_edited':False,'qt_platform':app.platformName() if app else None}
            records.append(row)
            if row['qt_platform']!='windows' or self.include_historical_route_diagnostics is not True:
                raise RuntimeError('Historical fixture did not construct a real Windows Qt window')

        def show(self):
            returned=super().show()
            visible=bool(win32gui.IsWindowVisible(int(self.winId())))
            records.append({'kind':'normal_public_show', 'real_win32_window_visible':visible,
                            'qt_visible':bool(self.isVisible()), 'return_value_preserved':True})
            if not visible or not self.isVisible():
                raise RuntimeError('Actual native fixture window is not visible')
            return returned

    module.MainWindow=HistoricalDiagnostics275

    def restore():
        nonlocal restored
        if restored:
            return
        if module.MainWindow is not HistoricalDiagnostics275:
            raise AssertionError('Owned fixture class reference was replaced unexpectedly')
        module.MainWindow=original
        restored=True

    def write_ledger():
        out.mkdir(parents=True,exist_ok=True)
        record={'kind':'SECTION275_EXPLICIT_NATIVE_HISTORICAL_CONSTRUCTOR_LEDGER',
                'pid':os.getpid(),'host_platform':sys.platform,
                'bootstrap_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'records':records,'original_class_reference_restored':restored,
                'production_source_edited':False,'game_api_mocked':False,
                'calculation_input_or_result_rewritten':False,'assertions_modified':False,
                'scope':'Explicit historical diagnostics parameter on the normal public constructor only; no default product recommendation',
                'native_windows_history_verified':False,'game_or_chat_verified':False}
        (out/'native275-constructor-ledger.json').write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))

    # Restore first at interpreter exit; the ledger then records actual restoration.
    atexit.register(write_ledger)
    atexit.register(restore)
    ACTIVE.append((restore,write_ledger))
    return restore,write_ledger


def finish_all():
    for restore,write_ledger in reversed(ACTIVE):
        restore();write_ledger()
