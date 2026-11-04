"""Exact saved-note references inside the retained player reference window."""
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel,QPlainTextEdit,QTabWidget
from .player_reference_window import ToolPage
from .player_map_reader import REFERENCE_STYLE,make_reader
from .player_reference_notes import model,reference_target
from .ui_state import replace_text


class NoteScenePanel(QWidget):
    def __init__(self,identity,parent=None):
        super().__init__(parent);self.identity=identity;self.result=model.detail('scenes',identity)
        layout=QVBoxLayout(self);self.title=QLabel();self.title.setWordWrap(True);layout.addWidget(self.title)
        self.tabs=QTabWidget();self.text=QPlainTextEdit();self.text.setReadOnly(True);self.details=QPlainTextEdit();self.details.setReadOnly(True)
        self.tabs.addTab(self.text,'情景原文');self.tabs.addTab(self.details,'资料说明');layout.addWidget(self.tabs,1)
        if self.result is not None:
            self.title.setText(self.result['row']['label']);replace_text(self.text,model._plain(self.result['row']['value'].get('description'))or'暂无对话原文')
            replace_text(self.details,self.result['player_text'])

    def refresh_reference(self):
        fresh=model.detail('scenes',self.identity)
        if fresh is None or fresh!=self.result:
            self.result=None;self.title.clear();self.text.clear();self.details.clear();return False
        return True


def open_shared(window,content,target):
    companion=window.compact_window
    if companion is None:return None
    host=companion.reference_window;current=host.pages.currentWidget()
    if current is None:return None
    if current is companion.note_library_page:source=companion.note_library
    elif current is companion.recent_notes_popup:source=current.panel
    else:return None
    def context():
        active=source.reference_context()
        return active if active==content and reference_target(active)==target else None
    category,identity=target
    from .documented_readers import reader_plan,make_flow_reader
    plan=reader_plan(category,identity)if category=='scenes'else None
    def create(owner):
        if category=='stages':
            return make_reader('battle',{'id':identity,'title':content['title']},source,historical=True,page_owner=owner)
        if plan is not None:return make_flow_reader(plan,source,page_owner=owner)
        panel=NoteScenePanel(identity)
        if panel.result is None:panel.deleteLater();return None
        page=ToolPage('事件情景 · '+content['title'],panel,owner,object_name='mapReferenceWindow',extra_style=REFERENCE_STYLE)
        page.panel=panel;page.resize(760,300);return page
    return host.open_reference(source,('note-source',category,identity,plan[0]if plan else'original'),context,create)
