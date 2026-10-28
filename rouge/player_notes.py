"""Explicit local Markdown notes; no game state, network, or automatic overwrite."""
from hashlib import sha256
from pathlib import Path
import json,os,tempfile
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QPlainTextEdit,QPushButton,QHBoxLayout

def content_key(content):
    if not content or not isinstance(content.get('title'),str)or not content['title'].strip():return None
    kind=content.get('kind')or'content'
    identity=content.get('variant_id')or content.get('event_id')or content['title']
    return json.dumps([kind,identity],ensure_ascii=False,separators=(',',':'))

class NoteStore:
    def __init__(self,folder):self.folder=Path(folder)
    def path(self,key):return self.folder/(sha256(key.encode()).hexdigest()+'.md')
    def read(self,key):
        p=self.path(key)
        if p.is_symlink():raise ValueError('笔记文件为链接，请人工检查。')
        raw=p.read_bytes()if p.exists()else b''
        return raw.decode('utf8'),sha256(raw).hexdigest()
    def save(self,key,text,expected):
        _,current=self.read(key)
        if current!=expected:raise ValueError('笔记已被其他窗口或软件修改；为保留双方内容，本次未覆盖。')
        self.folder.mkdir(parents=True,exist_ok=True);raw=text.encode('utf8')
        fd,name=tempfile.mkstemp(prefix='.note-',dir=self.folder)
        try:
            with os.fdopen(fd,'wb')as f:f.write(raw)
            os.replace(name,self.path(key))
        finally:
            if Path(name).exists():Path(name).unlink()
        return sha256(raw).hexdigest()

class NotesDialog(QDialog):
    def __init__(self,folder,parent=None):
        super().__init__(parent);self.store=NoteStore(folder);self.key=None;self.digest=None;self.dirty=False
        self.setWindowTitle('本地场景笔记');self.resize(620,500);body=QVBoxLayout(self)
        self.context=QLabel();self.context.setWordWrap(True);body.addWidget(self.context)
        self.editor=QPlainTextEdit();self.editor.setPlaceholderText('记下这关的机制、注意事项或上次失误。支持保存为本地 Markdown 文本。');body.addWidget(self.editor)
        self.status=QLabel('笔记只保存在本机，点击保存后写入；不会上传或加入聊天。');self.status.setWordWrap(True);body.addWidget(self.status)
        bar=QHBoxLayout();self.save_button=QPushButton('保存笔记');self.discard_button=QPushButton('放弃未保存修改');bar.addWidget(self.save_button);bar.addWidget(self.discard_button);body.addLayout(bar)
        self.editor.textChanged.connect(self.changed);self.save_button.clicked.connect(self.save);self.discard_button.clicked.connect(self.discard)
    def changed(self):self.dirty=True;self.status.setText('有未保存修改；仍绑定上方场景，不会随识别结果转移。')
    def set_context(self,content):
        key=content_key(content)
        if key is None:return False
        if self.dirty and key!=self.key:self.status.setText('请先保存或放弃上方场景的修改，再打开另一个场景。');return False
        if key==self.key:return True
        try:text,digest=self.store.read(key)
        except(OSError,ValueError,UnicodeError)as e:self.status.setText(str(e));return False
        self.key=key;self.digest=digest;self.editor.blockSignals(True);self.editor.setPlainText(text);self.editor.blockSignals(False);self.dirty=False
        self.context.setText('笔记对应：'+content['title']+'\n同名且未确认变体时共用笔记；这不是当前位置声明。')
        self.status.setText('本地笔记已读取；新笔记尚未保存。'if not text else'本地已保存；不会上传。');return True
    def save(self):
        if self.key is None:return False
        try:self.digest=self.store.save(self.key,self.editor.toPlainText(),self.digest)
        except(OSError,ValueError,UnicodeError)as e:self.status.setText(str(e));return False
        self.dirty=False;self.status.setText('已保存到本机；不会上传。');return True
    def discard(self):
        if self.key is None:return
        try:text,digest=self.store.read(self.key)
        except(OSError,ValueError,UnicodeError)as e:self.status.setText(str(e));return
        self.editor.blockSignals(True);self.editor.setPlainText(text);self.editor.blockSignals(False);self.digest=digest;self.dirty=False;self.status.setText('已恢复为本机保存的内容。')
    def closeEvent(self,event):
        if self.dirty:self.status.setText('修改尚未保存，请保存或放弃后关闭。');event.ignore()
        else:event.accept()
