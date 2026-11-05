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
            except(OSError,ValueError):self.issues.append(path.name)
        return notes
    def record(self,content):
        from .player_notes import content_key
        if not isinstance(content,dict):raise ValueError('笔记场景未确认。')
        key=content_key(content)
        if key is None:raise ValueError('笔记场景未确认。')
        saved={k:content[k]for k in('kind','title','variant_id','event_id')if k in content}
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
            Path(name).unlink(missing_ok=True)
    def rows(self,query=''):
        indexed=self.records();result=[];seen=set();q=query.strip().casefold()
        for key,row in indexed.items():
            path=_regular(self.folder/(sha256(key.encode()).hexdigest()+'.md'))
            if not path.is_file():continue
            seen.add(path.name)
            try:text=path.read_text('utf8')
            except(OSError,UnicodeError):self.issues.append(path.name);continue
            title=row['content']['title']
            if q and q not in(title+' '+text).casefold():continue
            result.append({'title':title,'key':key,'content':row['content'],'text':text,'path':path,'legacy':False})
        if self.folder.is_dir():
            for path in sorted(self.folder.glob('*.md')):
                if path.name in seen or not re.fullmatch(r'[0-9a-f]{64}\.md',path.name):continue
                try:_regular(path);text=path.read_text('utf8')
                except(OSError,ValueError):self.issues.append(path.name);continue
                if q and q not in text.casefold():continue
                result.append({'title':'旧笔记（场景标签未记录）','key':None,'content':None,'text':text,'path':path,'legacy':True})
        return result

from PySide6.QtCore import Signal,Qt,QTimer
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel,QLineEdit,QListWidget,QListWidgetItem,QPushButton,QSplitter
class NoteLibraryPanel(QWidget):
    openContext=Signal(object)
    openReference=Signal(object)
    def __init__(self,folder,parent=None,*,defer_population=False):
        super().__init__(parent);self.library=NoteLibrary(folder);self.rows=[];body=QVBoxLayout(self)
        from .player_note_style import NOTE_STYLE
        from .player_theme import apply_theme
        self.setObjectName('sceneNotesLibrary');apply_theme(self,extra=NOTE_STYLE)
        self.notice=QLabel('本机场景笔记');self.notice.setWordWrap(True);body.addWidget(self.notice);self.search=QLineEdit();self.search.setPlaceholderText('搜索场景名称或笔记内容');body.addWidget(self.search)
        from .player_note_preview import NotePreview
        self.split=QSplitter(Qt.Orientation.Horizontal);self.entries=QListWidget();self.entries.setMinimumWidth(130);self.split.addWidget(self.entries);self.detail=NotePreview(folder=self.library.folder);self.detail_key=None;self.split.addWidget(self.detail);self.split.setStretchFactor(1,2);self.split.setChildrenCollapsible(False);body.addWidget(self.split,1)
        from .flow_layout import FlowLayout
        actions=QWidget();row=FlowLayout(actions);self.open_button=QPushButton('编辑笔记');row.addWidget(self.open_button);self.reference_button=QPushButton('查看对应资料');row.addWidget(self.reference_button);body.addWidget(actions);self.reference_button.clicked.connect(self.open_reference)
        for action in (self.open_button,self.reference_button):action.setAutoDefault(False)
        self.search_timer=QTimer(self);self.search_timer.setSingleShot(True);self.search_timer.setInterval(150);self.search_timer.timeout.connect(self.refresh)
        self.search.textChanged.connect(lambda _:self.search_timer.start());self.search.returnPressed.connect(self.refresh);self.entries.currentItemChanged.connect(self.selected);self.open_button.clicked.connect(self.open_selected)
        if not defer_population:self.refresh()
    def refresh(self,*_):
        self.search_timer.stop()
        old=self.entries.currentItem();identity=old.data(Qt.ItemDataRole.UserRole)if old else None;offset=self.entries.verticalScrollBar().value()
        query=self.search.text()
        try:
            self.rows=self.library.rows(query)
        except(OSError,ValueError)as error:self.rows=[];self.notice.setText(str(error))
        else:self.notice.setText(f'共{len(self.rows)}条笔记'+(f' · {len(self.library.issues)}份文件读取异常'if self.library.issues else''))
        from .player_note_selector import catalogue_snapshot
        from .player_notes import content_key
        labels={content_key(row['context']):row for row in catalogue_snapshot()['rows']}if self.rows else{}
        self.entries.blockSignals(True);self.entries.clear()
        for i,row in enumerate(self.rows):
            reference=labels.get(row['key']);label=reference['label']if reference and reference['context']==row['content']else row['title']
            path=str(row['path']);item=QListWidgetItem(label);item.setData(Qt.ItemDataRole.UserRole,path);item.setData(Qt.ItemDataRole.UserRole+1,i);self.entries.addItem(item)
            if path==identity:self.entries.setCurrentItem(item)
        self.entries.verticalScrollBar().setValue(offset);self.entries.blockSignals(False);self.selected()
        return True
    def selected(self,*_):
        item=self.entries.currentItem();row=self.rows[item.data(Qt.ItemDataRole.UserRole+1)]if item else None
        text=row['text']if row else'选择一条本机笔记。'
        key=str(row['path'])if row else None
        self.detail.read_markdown(text,preserve=key==self.detail_key);self.detail_key=key
        self.open_button.setEnabled(bool(row and row['content']))
        from .player_reference_notes import reference_target
        self.reference_button.setEnabled(bool(row and reference_target(row['content'])is not None))
    def open_reference(self):
        from .player_reference_notes import reference_target
        content=self.reference_context()
        if reference_target(content)is not None:self.openReference.emit(content)
        else:self.reference_button.setEnabled(False)
    def open_selected(self):
        content=self.reference_context()
        if content:self.openContext.emit(content)
    def reference_context(self):
        item=self.entries.currentItem();row=self.rows[item.data(Qt.ItemDataRole.UserRole+1)]if item else None
        return row['content']if row else None
    def hideEvent(self,event):self.search_timer.stop();super().hideEvent(event)
