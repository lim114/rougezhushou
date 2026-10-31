"""Explicit old-layout diagnostic workspace; never the ordinary player default.

This actual native layout preserves historical physical control/geometry checks.
Its results do not prove the normal five-group/compact presentation.
"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTabWidget
from .player_workspace import PAGE_GROUP, DEVELOPER_PAGES
import atexit
import json
import os
from pathlib import Path

OBSERVATIONS = []

def record_layout(window, phase):
    """Only explicit diagnostic runs produce these non-content observations."""
    from PySide6.QtWidgets import QApplication
    observation = {'phase': phase, 'process_id': os.getpid(),
                   'diagnostic_layout': window.diagnostic_layout,
                   'workspace_class': type(window.centralWidget()).__name__,
                   'include_historical_route_diagnostics': window.include_historical_route_diagnostics,
                   'qpa': QApplication.instance().platformName(),
                   'product_default_layout_claimed': False}
    if phase == 'show' and observation['qpa'] == 'windows':
        import win32gui
        import win32process
        handle = int(window.winId())
        observation.update(handle=handle, actual_owned_window_visible=bool(win32gui.IsWindowVisible(handle)),
                           actual_window_process_id=win32process.GetWindowThreadProcessId(handle)[1])
    OBSERVATIONS.append(observation)

def _write_observations():
    destination = os.environ.get('ROUGE_DIAGNOSTIC_OUTPUT')
    if not destination or not OBSERVATIONS:
        return
    folder = Path(destination)
    if not folder.is_absolute() or folder.is_symlink() or not folder.is_dir():
        raise ValueError('Explicit regular diagnostic output folder required.')
    record = {'schema': 'native_diagnostic_layout_v1', 'process_id': os.getpid(),
              'scope': 'Actual opt-in old-layout compatibility only; not complete default five-group/compact coverage.',
              'game_state_or_private_contents_recorded': False, 'observations': OBSERVATIONS}
    with (folder / ('diagnostic-layout-' + str(os.getpid()) + '.json')).open('xb') as stream:
        stream.write((json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode('utf8'))

atexit.register(_write_observations)

class DiagnosticWorkspace(QTabWidget):
    activePageChanged = Signal(object)
    backAvailable = Signal(bool)

    def __init__(self, parent=None, **_):
        super().__init__(parent)
        self.setAccessibleName('历史布局诊断（非默认玩家界面）')
        self.pages = {}
        self._history = []
        self._last_page = None
        self._going_back = False
        self.currentChanged.connect(self._announce)

    def addTab(self, page, label):
        self.pages[page] = ('developer' if label in DEVELOPER_PAGES else PAGE_GROUP.get(label, ('资料查询', label))[0], label)
        return super().addTab(page, label)

    def combine_map_and_node(self, *_):
        # The old physical layout keeps the two actual readers separate.
        return None

    def setCurrentWidget(self, page):
        if self.indexOf(page) < 0:
            return False
        super().setCurrentWidget(page)
        self._announce()
        return True

    def show_group(self, name):
        page = next((page for page, (group, _) in self.pages.items() if group == name), None)
        return self.setCurrentWidget(page) if page is not None else False

    def _announce(self, *_):
        page = self.currentWidget()
        if page is self._last_page:
            return
        if self._last_page in self.pages and not self._going_back:
            self._history.append(self._last_page)
            self._history = self._history[-30:]
        self._last_page = page
        self.activePageChanged.emit(page)
        self.backAvailable.emit(bool(self._history))

    def go_back(self):
        while self._history:
            page = self._history.pop()
            if page not in self.pages or page is self.currentWidget():
                continue
            self._going_back = True
            try:
                result = self.setCurrentWidget(page)
            finally:
                self._going_back = False
            self.backAvailable.emit(bool(self._history))
            return result
        self.backAvailable.emit(False)
        return False

    def close_developer_tools(self):
        pass
