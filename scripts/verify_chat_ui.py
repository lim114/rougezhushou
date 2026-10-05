"""Exercise the Qt-to-Node path without opening or operating any foreground UI."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from rouge.app import MainWindow

app=QApplication([])
window=MainWindow()
try:
    window.desktop_request('refresh')
    deadline=time.monotonic()+50
    while time.monotonic()<deadline and window.desktop_request_busy:
        app.processEvents();time.sleep(.05)
    app.processEvents()
    assert window.desktop_snapshot and window.desktop_threads.count()>0
    assert all(t['kind']=='chatgpt' for t in window.desktop_snapshot['threads'] if t['id'] in [window.desktop_threads.itemData(i) for i in range(window.desktop_threads.count())])
    assert window.mode.currentIndex()==0 and not window.key.isEnabled()
    window.desktop_request('read')
    while time.monotonic()<deadline and window.desktop_request_busy:
        app.processEvents();time.sleep(.05)
    app.processEvents()
    assert '100700' in window.transcript.toPlainText()
    print('Qt → Node → native client: ordinary chats listed, bound reply displayed; no API key or foreground actions')
finally:window.close()
