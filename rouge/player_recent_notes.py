"""Follow the last read scene without ever rebinding or saving an editor."""
from copy import deepcopy
import time
from PySide6.QtCore import Signal,QTimer
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QCheckBox,QPushButton
from .player_notes import content_key
from .player_note_library import _regular
from .player_note_preview import NotePreview

NOTE_STYLE='''
QWidget#sceneNotesSurface QComboBox{background:#e6e6eb;color:#303139;border:1px solid #cdcdd5;border-radius:9px;padding:5px;}
QWidget#sceneNotesSurface QComboBox QAbstractItemView{background:white;color:#303139;selection-background-color:#cde5eb;selection-color:#25262b;}

QWidget#sceneNotesSurface,QDialog#sceneNotesEditor,QDialog#sceneNotesWindow{background:#f5f5f7;color:#25262b;}
QDialog#sceneNotesWindow{border:1px solid #dedee5;border-radius:12px;}
QDialog#sceneNotesWindow QPushButton#popoverCloseButton{padding:0;border:0;background:transparent;color:#303139;}
QDialog#sceneNotesWindow QPushButton#popoverCloseButton:hover{background:#e6e6eb;}
QWidget#sceneNotesSurface QLabel,QDialog#sceneNotesEditor QLabel,QDialog#sceneNotesWindow QLabel{color:#303139;background:transparent;}
QWidget#sceneNotesSurface QCheckBox,QDialog#sceneNotesEditor QTabWidget{color:#40414a;}
QWidget#sceneNotesSurface QTextBrowser,QDialog#sceneNotesEditor QPlainTextEdit,QDialog#sceneNotesEditor QTextBrowser{
 background:white;color:#25262b;border:1px solid #dedee5;border-radius:12px;padding:12px;selection-background-color:#cde5eb;selection-color:#25262b;}
QWidget#sceneNotesSurface QPushButton,QDialog#sceneNotesEditor QPushButton{
 background:#e6e6eb;color:#303139;border:0;border-radius:13px;padding:7px 14px;}
QWidget#sceneNotesSurface QPushButton:hover,QDialog#sceneNotesEditor QPushButton:hover{background:#d6e5e9;}
QWidget#sceneNotesSurface QPushButton:disabled,QDialog#sceneNotesEditor QPushButton:disabled{color:#92929b;}
QDialog#sceneNotesEditor QTabBar::tab{background:#e6e6eb;color:#484952;border:0;border-radius:12px;padding:6px 16px;margin:2px;}
QDialog#sceneNotesEditor QTabBar::tab:selected{background:#303438;color:white;}
QDialog#sceneNotesEditor QTabWidget::pane{border:0;}
'''

def scene_context(value):
    if not isinstance(value,dict):return None
    if value.get('kind')not in('battle','event'):return None
    if not isinstance(value.get('title'),str)or not value['title'].strip():return None
    for name in('variant_id','event_id'):
        if name in value and value[name]is not None and not isinstance(value[name],str):return None
    return deepcopy({name:value[name]for name in('kind','title','variant_id','event_id')if name in value})

class RecentNotesPanel(QWidget):
    editRequested=Signal(object)
    def __init__(self,run,store,parent=None):
        super().__init__(parent);self.run=run;self.store=store;self.context=None;self.key=None
        self._stamp=object();self._next_check=0.;self._run_id=run.state.get('run_id')
        self.setObjectName('sceneNotesSurface');self.setStyleSheet(NOTE_STYLE)
        body=QVBoxLayout(self);body.setContentsMargins(16,12,16,16);body.setSpacing(10)
        self.scene=QLabel();self.scene.setWordWrap(True);body.addWidget(self.scene)
        from .player_note_selector import SceneNoteSelector
        self.selector=SceneNoteSelector(self);self.selector.chosen.connect(self.select_context);body.addWidget(self.selector)
        bar=QHBoxLayout();self.follow=QCheckBox('跟随最近读取的场景');self.follow.setChecked(True);bar.addWidget(self.follow);bar.addStretch()
        self.reload=QPushButton('刷新笔记');bar.addWidget(self.reload);body.addLayout(bar)
        self.preview=NotePreview();self.preview.setMinimumHeight(180);body.addWidget(self.preview,1)
        self.status=QLabel();self.status.setWordWrap(True);body.addWidget(self.status)
        self.edit=QPushButton('编辑这份笔记');body.addWidget(self.edit)
        self.follow.toggled.connect(lambda _:self.refresh(force=True))
        self.reload.clicked.connect(lambda:self.refresh(force=True));self.edit.clicked.connect(self.request_edit)
        self.preview.linkBlocked.connect(lambda:self.status.setText('链接不会自动打开；可在编辑器中复制。笔记仍只保存在本机。'))
        self.timer=QTimer(self);self.timer.setInterval(1000);self.timer.timeout.connect(self._tick);self.timer.start()
        self.refresh(force=True)

    def _tick(self):
        if self.isVisible():self.refresh()

    def select_context(self,content):
        self.follow.setChecked(False);self.context=deepcopy(content);self.refresh(force=True)

    def refresh(self,*,force=False):
        current=scene_context(self.run.state.get('last_node_content'))
        reset=self._run_id!=self.run.state.get('run_id')
        if reset:self._run_id=self.run.state.get('run_id')
        target=current if self.follow.isChecked()or reset else self.context
        key=content_key(target);changed=key!=self.key
        if changed or reset:
            self.context=target;self.key=key;self._stamp=object();self._next_check=0
            self.preview.read_markdown('');self.preview.verticalScrollBar().setValue(0)
        self.edit.setEnabled(target is not None)
        if target is None:
            self.scene.setText('尚未读到可关联的场景')
            self.preview.read_markdown('')
            self.status.setText('读取到作战或事件名称后，这里会展示对应的本机笔记。');return
        self.context=target
        manual=target.get('kind')in('reference-stage','reference-scene')
        self.scene.setText(('手选固定资料：'if manual else'最近读取：'if self.follow.isChecked()else'已暂停跟随，正在阅读：')+target['title'])
        if not force and not changed and time.monotonic()<self._next_check:return
        self._next_check=time.monotonic()+1
        try:
            path=_regular(self.store.path(key));stat=path.stat()if path.exists()else None
            stamp=(stat.st_mtime_ns,stat.st_ctime_ns,stat.st_size,stat.st_ino)if stat else None
            if not force and stamp==self._stamp:return
            text,_=self.store.read(key)
        except(OSError,ValueError,UnicodeError)as error:
            from .player_file_messages import file_issue
            self.preview.read_markdown('');self._stamp=object();self.status.setText(file_issue(error));self.status.setToolTip(str(error));return
        self._stamp=stamp;self.preview.read_markdown(text);self.status.setToolTip('')
        scope='按准确固定资料分别保存；目录分类不证明本局出现。'if manual else'未确认变体时，同名场景共用笔记。'if not(target.get('variant_id')or target.get('event_id'))else'按已读场景身份分别关联。'
        self.status.setText(('本机已保存笔记。'if text else'还没有保存笔记，可点击下方按钮编写。')+scope+' 最近读取不表示当前所在位置；此处不自动保存。')

    def request_edit(self):
        # A scene may change between painting the button and receiving its click.
        self.refresh(force=True)
        if self.context is not None:self.editRequested.emit(deepcopy(self.context))
