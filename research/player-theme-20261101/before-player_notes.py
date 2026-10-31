"""Local Markdown notes with context-bound automatic saving and conflict refusal."""
from hashlib import sha256
from pathlib import Path
import json,os,tempfile
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QPlainTextEdit,QPushButton,QHBoxLayout,QTabWidget,QCheckBox
from PySide6.QtCore import QTimer,Signal,QSignalBlocker
from .ui_state import replace_text
from .player_note_preview import NotePreview
from copy import deepcopy

def content_key(content):
    if not content or not isinstance(content.get('title'),str)or not content['title'].strip():return None
    kind=content.get('kind')or'content'
    identity=content.get('variant_id')or content.get('event_id')or content['title']
    return json.dumps([kind,identity],ensure_ascii=False,separators=(',',':'))

class NoteStore:
    def __init__(self,folder):self.folder=Path(folder);self.save_warning=None
    def path(self,key):return self.folder/(sha256(key.encode()).hexdigest()+'.md')
    def read(self,key):
        p=self.path(key)
        if p.is_symlink():raise ValueError('笔记文件为链接，请人工检查。')
        raw=p.read_bytes()if p.exists()else b''
        return raw.decode('utf8'),sha256(raw).hexdigest()
    def save(self,key,text,expected):
        from .persistence_install import record_save_lock
        raw=text.encode('utf8');self.save_warning=None;published=False
        self.folder.mkdir(parents=True,exist_ok=True)
        try:
            with record_save_lock(self.path(key)):
                _,current=self.read(key)
                if current!=expected:raise ValueError('笔记已被其他窗口或软件修改；为保留双方内容，本次未覆盖。')
                fd,name=tempfile.mkstemp(prefix='.note-',dir=self.folder)
                try:
                    with os.fdopen(fd,'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
                    # Other software may not participate in our save lock.
                    # Check again after preparing bytes; do not claim an OS-wide CAS.
                    if self.read(key)[1]!=expected:raise ValueError('笔记在保存期间被修改；本次未覆盖，编辑内容仍保留。')
                    os.replace(name,self.path(key));published=True
                finally:
                    try:Path(name).unlink(missing_ok=True)
                    except OSError:
                        if published:self.save_warning='内容已保存，但一份临时副本未能清理。'
        except OSError:
            if not published:raise
            self.save_warning='内容已保存，但保存占用标记未能清理；后续保存可能需要先处理占用。'
        return sha256(raw).hexdigest()

class NotesDialog(QDialog):
    openReference=Signal(object)
    def __init__(self,folder,parent=None):
        super().__init__(parent);self.store=NoteStore(folder);self.key=None;self.digest=None;self.dirty=False;self.content=None
        from .player_note_style import NOTE_STYLE
        self.setObjectName('sceneNotesEditor');self.setStyleSheet(NOTE_STYLE)
        self.setWindowTitle('本地场景笔记');self.resize(900,500);body=QVBoxLayout(self)
        self.context=QLabel();self.context.setWordWrap(True);body.addWidget(self.context)
        self.pages=QTabWidget();body.addWidget(self.pages,1)
        self.editor=QPlainTextEdit();self.editor.setPlaceholderText('记下这关的机制、注意事项或上次失误。可用#写标题，用-列要点。');self.pages.addTab(self.editor,'编辑文字')
        self.preview=NotePreview();self.pages.addTab(self.preview,'排版预览')
        self.preview_timer=QTimer(self);self.preview_timer.setSingleShot(True);self.preview_timer.setInterval(180);self.preview_timer.timeout.connect(self.refresh_preview)
        self.pages.currentChanged.connect(self.refresh_preview)
        self.preview.linkBlocked.connect(self.blocked_link)
        self.autosave=QCheckBox('自动保存在本机');self.autosave.setChecked(True);body.addWidget(self.autosave)
        self.autosave_timer=QTimer(self);self.autosave_timer.setSingleShot(True);self.autosave_timer.setInterval(900);self.autosave_timer.timeout.connect(self.save_pending);self.pending_key=None
        self.autosave.toggled.connect(self.set_autosave)
        self.status=QLabel('编辑停顿后自动保存在本机；不会上传或加入聊天。');self.status.setWordWrap(True);body.addWidget(self.status)
        bar=QHBoxLayout();self.save_button=QPushButton('保存笔记');self.discard_button=QPushButton('放弃未保存修改');bar.addWidget(self.save_button);bar.addWidget(self.discard_button);body.addLayout(bar)
        self.reference_button=QPushButton('查看笔记对应的固定资料（打开时核对）');bar.addWidget(self.reference_button);self.reference_button.hide()
        from .player_reference_notes import request_note_source
        self.reference_button.clicked.connect(lambda:request_note_source(self))
        self.export_button=QPushButton('导出当前文字');bar.addWidget(self.export_button);self.export_button.clicked.connect(self.export_current)
        self.editor.textChanged.connect(self.changed);self.save_button.clicked.connect(self.save);self.discard_button.clicked.connect(self.discard)
    def export_current(self):
        from .player_note_export_ui import export_editor
        return export_editor(self)
    def changed(self):
        self.dirty=True;self.status.setText('有未保存修改；仍绑定上方场景，不会随识别结果转移。')
        if self.autosave.isChecked()and self.key is not None:self.pending_key=self.key;self.autosave_timer.start()
        if self.pages.currentIndex()==1:self.preview_timer.start()
    def set_autosave(self,value):
        self.autosave_timer.stop();self.pending_key=None
        if value and self.dirty and self.key is not None:self.pending_key=self.key;self.autosave_timer.start()
    def save_pending(self):
        if self.autosave.isChecked()and self.dirty and self.key is not None and self.pending_key==self.key:
            if not self.save():
                self.autosave.setChecked(False);self.status.setText(self.status.text()+' 自动保存已暂停；编辑内容仍保留，请核对后手动处理。')
    def refresh_preview(self,*_):
        if self.pages.currentIndex()==1:self.preview.read_markdown(self.editor.toPlainText())
    def blocked_link(self):
        self.status.setText(('有未保存修改。'if self.dirty else'')+'预览中的链接不会自动打开；可回到编辑页复制使用。')
    def set_context(self,content):
        key=content_key(content)
        if key is None:return False
        if self.dirty and key!=self.key:self.status.setText('请先保存或放弃上方场景的修改，再打开另一个场景。');return False
        same=key==self.key
        if self.dirty:return True
        try:text,digest=self.store.read(key)
        except(OSError,ValueError,UnicodeError)as e:self.report_issue(e);return False
        if same and digest==self.digest:return True
        self.key=key;self.digest=digest;self.content=deepcopy({field:content[field]for field in('kind','title','variant_id','event_id')if field in content})
        with QSignalBlocker(self.editor):replace_text(self.editor,text,preserve=same)
        self.dirty=False
        scope='\n手选范围的通用笔记；不会自动套用为某个具体场景。'if content.get('kind')=='note-scope'else'\n手动选择的固定资料笔记，按准确条目和资料基准分别保存；不表示当前关卡。'if content.get('kind')in('reference-stage','reference-scene')else'\n同名且未确认变体时共用笔记；这不是当前位置声明。'
        self.context.setText('笔记对应：'+content['title']+scope)
        from .player_reference_notes import sync_note_source
        sync_note_source(self)
        self.status.setText('本地笔记已读取；新笔记尚未保存。'if not text else'本地已保存；不会上传。');self.refresh_preview();return True
    def save(self):
        self.autosave_timer.stop();self.pending_key=None
        if self.key is None:return False
        try:self.digest=self.store.save(self.key,self.editor.toPlainText(),self.digest)
        except(OSError,ValueError,UnicodeError)as e:self.report_issue(e);return False
        self.dirty=False;warning=self.store.save_warning or''
        try:
            from .player_note_library import NoteLibrary
            NoteLibrary(self.store.folder).record(self.content)
        except(OSError,ValueError,UnicodeError,TypeError):warning+='正文已保存，但场景标签未能更新；可继续从当前编辑页读取。'
        self.status.setText('已保存到本机；不会上传。'+warning);return True
    def discard(self):
        self.autosave_timer.stop();self.pending_key=None
        if self.key is None:return
        try:text,digest=self.store.read(self.key)
        except(OSError,ValueError,UnicodeError)as e:self.report_issue(e);return
        with QSignalBlocker(self.editor):replace_text(self.editor,text)
        self.digest=digest;self.dirty=False;self.status.setText('已恢复为本机保存的内容。');self.refresh_preview()
    def report_issue(self,error):
        from .player_file_messages import file_issue
        self.status.setText(file_issue(error));self.status.setToolTip(str(error))
    def closeEvent(self,event):
        if self.dirty and self.autosave.isChecked():self.save_pending()
        if self.dirty:self.status.setText('修改尚未保存，请保存或放弃后关闭。');event.ignore()
        else:self.autosave_timer.stop();event.accept()
    def reject(self):
        # Escape follows the same draft/conflict rule as the close button.
        self.close()
