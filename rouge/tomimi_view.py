"""Use the actual public website inside Qt's existing reference window."""
from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QToolButton, QStyle,QLineEdit
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
from .player_reference_window import ReferenceWindow, ToolPage
from .player_window_frame import PlayerDialog


class TomimiPanel(QWidget):
    def __init__(self, target, parent=None):
        super().__init__(parent)
        self.result = target
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0)
        # The view owns its page; the profile outlives that view in this layout.
        self.web = QWebEngineView(self)
        self.profile = QWebEngineProfile(self)
        if target.get('provider') == 'PRTS':
            self.profile.setHttpUserAgent('rougezhushou/0.70 (QtWebEngine; local desktop reference viewer)')
        page = QWebEnginePage(self.profile, self.web)
        page.setBackgroundColor(QColor('#262626'))
        self.web.setPage(page)
        self.navigation=QWidget();bar = self.navigation_bar = QHBoxLayout(self.navigation);bar.setContentsMargins(0,0,0,0)
        for action, title, icon in ((QWebEnginePage.WebAction.Back, '网页上一页', QStyle.StandardPixmap.SP_ArrowBack),
                                    (QWebEnginePage.WebAction.Forward, '网页下一页', QStyle.StandardPixmap.SP_ArrowForward),
                                    (QWebEnginePage.WebAction.Reload, '刷新网页', QStyle.StandardPixmap.SP_BrowserReload)):
            command=page.action(action);command.setText(title);command.setIcon(self.style().standardIcon(icon))
            button = QToolButton(); button.setDefaultAction(command)
            button.setToolTip(title); button.setAccessibleName(title); bar.addWidget(button)
        self.title = QLabel(target.get('provider','Tomimi')+' · '+target['name']); self.title.setWordWrap(True)
        bar.addWidget(self.title, 1)
        self.environment=QLabel('网页资料'if target.get('provider')=='PRTS'else'难度与藏品：网页内设置');bar.addWidget(self.environment)
        self.status = QLabel('正在载入…'); bar.addWidget(self.status)
        layout.addWidget(self.navigation); layout.addWidget(self.web, 1)
        self.address=QLineEdit(target['url']);self.address.setReadOnly(True);self.address.setAccessibleName('网页地址');layout.insertWidget(1,self.address)
        self.web.urlChanged.connect(lambda url:self.address.setText(url.toString()))
        self.web.titleChanged.connect(self.title.setText)
        self.web.loadFinished.connect(self._loaded)
        self.web.setUrl(QUrl(target['url']))

    def _loaded(self, ok):
        self.status.setText(self.web.url().host() if ok else '加载失败，点击刷新重试')

    def refresh_reference(self):
        # Parent qualification handles source changes; refresh preserves browser state.
        return self.result is not None

    def clear_reference(self):
        self.result = None
        self.web.stop()
        self.web.setUrl(QUrl('about:blank'))


class TomimiDialog(PlayerDialog):
    def __init__(self, target, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Tomimi · '+target['name'])
        layout = QVBoxLayout(self); self.panel = TomimiPanel(target, self); layout.addWidget(self.panel)
        from .player_map_reader import prepare_reference_window
        prepare_reference_window(self, 1000, 560)

    def done(self, result):
        self.panel.clear_reference()
        super().done(result)


def open_reference(parent, target):
    host = parent.window()
    if isinstance(host, ReferenceWindow):
        def create(owner):
            from .player_map_reader import REFERENCE_STYLE
            reader = TomimiPanel(target)
            page = ToolPage('Tomimi · '+target['name'], reader, owner,
                            object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
            page.panel = reader
            page.resize(1000, 560)
            return page
        return host.open_reference(parent, ('tomimi', target['stage_id']),
            lambda: None if parent.result is None else (parent.result['source_identity'], parent.stage_id), create)
    if parent.tomimi_dialog is None:
        parent.tomimi_dialog = TomimiDialog(target, parent)
    parent.tomimi_dialog.show()
    parent.tomimi_dialog.raise_()
    return True
