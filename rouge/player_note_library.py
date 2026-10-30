"""Own local notes only, indexed by the existing exact content key."""
from pathlib import Path
from hashlib import sha256
import json,os,tempfile,re

def _regular(path):
    path=Path(path)
    if path.is_symlink():raise ValueError('笔记位置为链接，未自动读取或覆盖。')
    if any(p.is_symlink()for p in path.parents):raise ValueError('笔记目录为链接，未自动读取或覆盖。')
    return path

class NoteLibrary:
    def __init__(self,folder):self.folder=Path(folder);self.issues=[]
    def records(self):
        _regular(self.folder)
        if self.folder.exists()and not self.folder.is_dir():raise ValueError('笔记目录不可用，原件未改动。')
        notes={};self.issues=[]
        from .player_notes import content_key
        for path in sorted(self.folder.glob('*.meta.json')):
            try:
                value=json.loads(_regular(path).read_text('utf8'))
                if not isinstance(value,dict)or value.get('schema')!='player-note-context-v1':raise ValueError('场景标签格式无法核对。')
                content=value.get('content')
                if not isinstance(content,dict):raise ValueError('缺少场景标签。')
                key=content_key(content)
                if key is None or path.name!=sha256(key.encode()).hexdigest()+'.meta.json':raise ValueError('场景身份无法核对。')
                notes[key]={'content':content}
            except(OSError,ValueError,UnicodeError,TypeError):self.issues.append(path.name)
        return notes
    def record(self,content):
        from .player_notes import content_key
        if not isinstance(content,dict):raise ValueError('笔记场景未确认。')
        key=content_key(content)
        if key is None:raise ValueError('笔记场景未确认。')
        saved={k:content[k]for k in('kind','title','variant_id','event_id')if k in content}
        if content_key(saved)!=key:raise ValueError('笔记场景无法无损保存。')
        destination=_regular(self.folder/(sha256(key.encode()).hexdigest()+'.meta.json'))
        if destination.exists():
            prior=json.loads(destination.read_text('utf8'))
            if not isinstance(prior,dict)or prior.get('schema')!='player-note-context-v1'or not isinstance(prior.get('content'),dict)or content_key(prior['content'])!=key:raise ValueError('旧场景标签无法核对，未覆盖。')
        self.folder.mkdir(parents=True,exist_ok=True);_regular(self.folder);raw=(json.dumps({'schema':'player-note-context-v1','content':saved},ensure_ascii=False,indent=2)+'\n').encode()
        fd,name=tempfile.mkstemp(prefix='.index-',dir=self.folder)
        try:
            with os.fdopen(fd,'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
            _regular(destination)
            if destination.exists():os.replace(name,destination)
            else:os.link(name,destination)
        finally:
            if Path(name).exists():Path(name).unlink()
    def rows(self,query=''):
        indexed=self.records();result=[];seen=set();q=query.strip().casefold()
        for key,row in indexed.items():
            path=_regular(self.folder/(sha256(key.encode()).hexdigest()+'.md'))
            if not path.is_file():continue
            try:text=path.read_text('utf8')
            except(OSError,UnicodeError):self.issues.append(path.name);continue
            title=row['content']['title'];seen.add(path.name)
            if q not in(title+' '+text).casefold():continue
            result.append({'title':title,'key':key,'content':row['content'],'text':text,'path':path,'legacy':False})
        if self.folder.is_dir():
            for path in sorted(self.folder.glob('*.md')):
                if path.name in seen or not re.fullmatch(r'[0-9a-f]{64}\.md',path.name):continue
                try:_regular(path);text=path.read_text('utf8')
                except(OSError,ValueError,UnicodeError):self.issues.append(path.name);continue
                if q and q not in text.casefold():continue
                result.append({'title':'旧笔记（场景标签未记录）','key':None,'content':None,'text':text,'path':path,'legacy':True})
        return result

from PySide6.QtCore import Signal,Qt,QTimer
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QLineEdit,QListWidget,QListWidgetItem,QPlainTextEdit,QPushButton
class NoteLibraryDialog(QDialog):
    openContext=Signal(object)
    openReference=Signal(object)
    def __init__(self,folder,parent=None):
        super().__init__(parent);self.library=NoteLibrary(folder);self.rows=[];self.setWindowTitle('本机场景笔记');self.resize(680,560);body=QVBoxLayout(self)
        from .player_note_style import NOTE_STYLE
        self.setObjectName('sceneNotesLibrary');self.setStyleSheet(NOTE_STYLE)
        self.notice=QLabel('只查本机笔记；搜索不会上传，旧笔记缺少场景标签时不猜测关联。');self.notice.setWordWrap(True);body.addWidget(self.notice);self.search=QLineEdit();self.search.setPlaceholderText('搜索场景名称或笔记内容');body.addWidget(self.search);self.entries=QListWidget();body.addWidget(self.entries,1);self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1);self.open_button=QPushButton('打开这条笔记对应的编辑页');body.addWidget(self.open_button)
        self.reference_button=QPushButton('查看所选笔记对应的固定资料');body.addWidget(self.reference_button);self.reference_button.clicked.connect(self.open_reference)
        self.search_timer=QTimer(self);self.search_timer.setSingleShot(True);self.search_timer.setInterval(150);self.search_timer.timeout.connect(self.refresh)
        self.search.textChanged.connect(lambda _:self.search_timer.start());self.search.returnPressed.connect(self.refresh);self.entries.currentItemChanged.connect(self.selected);self.open_button.clicked.connect(self.open_selected);self.refresh()
    def refresh(self,*_):
        self.search_timer.stop()
        old=self.entries.currentItem();identity=old.data(Qt.ItemDataRole.UserRole)if old else None;offset=self.entries.verticalScrollBar().value()
        try:
            self.rows=self.library.rows(self.search.text());self.notice.setText('只查本机笔记，不会上传；旧笔记缺少场景标签时不猜关联。'+(f'另有{len(self.library.issues)}份文字或标签无法核对。'if self.library.issues else''))
        except(OSError,ValueError,UnicodeError)as error:self.rows=[];self.notice.setText(str(error))
        self.entries.blockSignals(True);self.entries.clear()
        for i,row in enumerate(self.rows):
            item=QListWidgetItem(row['title']);item.setData(Qt.ItemDataRole.UserRole,str(row['path']));item.setData(Qt.ItemDataRole.UserRole+1,i);self.entries.addItem(item)
            if str(row['path'])==identity:self.entries.setCurrentItem(item)
        self.entries.verticalScrollBar().setValue(offset);self.entries.blockSignals(False);self.selected()
    def selected(self,*_):
        item=self.entries.currentItem();row=self.rows[item.data(Qt.ItemDataRole.UserRole+1)]if item else None
        text=row['text']if row else'选择一条本机笔记。'
        if self.detail.toPlainText()!=text:self.detail.setPlainText(text)
        self.open_button.setEnabled(bool(row and row['content']))
        from .player_reference_notes import reference_target
        self.reference_button.setEnabled(bool(row and reference_target(row['content'])is not None))
    def open_reference(self):
        from .player_reference_notes import reference_target
        item=self.entries.currentItem();row=self.rows[item.data(Qt.ItemDataRole.UserRole+1)]if item else None
        if row and reference_target(row['content'])is not None:self.openReference.emit(row['content'])
        else:self.reference_button.setEnabled(False)
    def open_selected(self):
        item=self.entries.currentItem();row=self.rows[item.data(Qt.ItemDataRole.UserRole+1)]if item else None
        if row and row['content']:self.openContext.emit(row['content'])
    def hideEvent(self,event):self.search_timer.stop();super().hideEvent(event)
