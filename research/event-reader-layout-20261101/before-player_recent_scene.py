"""One compact reading entry for recent battles and documented event candidates."""
from copy import deepcopy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QComboBox,QPlainTextEdit,QPushButton,QCheckBox
from .player_scene_battle import SceneBattlePanel
from . import current_event_directory as events

def event_candidates(content,reference=None):
    if not isinstance(content,dict)or content.get('kind')!='event':return []
    reference=events.reference()if reference is None else reference
    if reference is None:return []
    explicit=content.get('event_id')
    if 'event_id'in content and explicit is not None:
        if not isinstance(explicit,str)or not explicit.strip():return []
        return [r for r in reference['rows']if explicit in(r['id'],r['event_id'],*r['event']['scene_ids'])]
    title=content.get('title')
    if not isinstance(title,str)or not title.strip():return []
    return [r for r in reference['rows']if r['title']==title]

def event_excerpt(result,key):
    row=result['selected'];entry=next((e for e in row['entries']if e['key']==key),None)
    lines=[row['title']]
    if entry:
        lines+=['','【选项或结果原文】'+entry['title'],entry['description']]
        if entry['related_item_names']:lines+=['关联提示：'+'、'.join(entry['related_item_names'])]
        if entry['actual_game_button']is False or entry['presentation']=='outcome_reference':
            lines+=['这是文献中的结果参考，不是可点击的游戏选项。']
        lines+=['','可打开完整流程，或为这段资料写笔记。']
    else:
        lines+=['资料中的节点类别：'+('、'.join(row['node_types'])or'未确认'),
            '上方可以选择具体对话与选项，下面可打开完整流程。']
    lines+=['','这是固定资料，不代表当前阶段、可选资格或已经获得奖励。未列出的事件及条件仍可能存在。']
    return '\n'.join(lines)

class RecentScenePanel(SceneBattlePanel):
    def __init__(self,run,parent=None,*,historical=False):
        self.historical_reading=historical
        self.scene_run=run.state.get('id');self.event_key=None;self.event_result=None;self.event_dialog=None
        super().__init__(run,parent)
        self.event_body=QWidget();body=QVBoxLayout(self.event_body);body.setContentsMargins(0,0,0,0)
        self.event_choices=QComboBox();self.event_choices.setAccessibleName('最近读取事件的准确资料');body.addWidget(self.event_choices)
        self.event_entries=QComboBox();self.event_entries.setAccessibleName('事件中的对话与选项记录');body.addWidget(self.event_entries)
        self.event_text=QPlainTextEdit();self.event_text.setReadOnly(True);body.addWidget(self.event_text,1)
        self.event_more=QCheckBox('展开来源范围与尚未核验的条件');body.addWidget(self.event_more)
        self.event_open=QPushButton('打开这份事件的完整流程');body.addWidget(self.event_open)
        self.event_note=QPushButton('为这段准确资料写笔记');body.addWidget(self.event_note)
        self.layout().insertWidget(1,self.event_body,1)
        self.event_choices.currentIndexChanged.connect(self.select_event)
        self.event_entries.currentIndexChanged.connect(self.read_event_entry)
        self.event_more.toggled.connect(self.read_event_entry)
        self.event_open.clicked.connect(self.open_event);self.event_note.clicked.connect(self.write_event_note)
        self.refresh()

    def _close_event(self):
        if self.event_dialog is not None:
            self.event_dialog.close();self.event_dialog=None

    def refresh(self):
        if not hasattr(self,'event_body'):return super().refresh()
        run_changed=self.scene_run!=self.run.state.get('id')
        if run_changed:
            self.scene_run=self.run.state.get('id');self.context_key=None;self.event_key=None
            self.stages.setCurrentIndex(0);self._close_event()
        content=self.run.state.get('last_node_content');is_event=isinstance(content,dict)and content.get('kind')=='event'
        self.event_body.setVisible(is_event)
        for widget in(self.stages,self.tabs,self.detail,self.open_button,self.note_button):widget.setVisible(not is_event)
        if not is_event:
            if self.event_key is not None:
                self.event_key=None;self.event_result=None;self.event_text.clear();self.event_choices.clear();self.event_entries.clear();self._close_event()
            result=super().refresh()
            if self.historical_reading and not self.notice.text().startswith('历史记录：'):
                self.notice.setText('历史记录：'+self.notice.text().replace('最近读取：','当时读取：'))
            return result
        if self.dialog is not None:self.dialog.close();self.dialog=None
        self.result=None;self.enemies={};self.context_key=None
        reference=events.reference();rows=event_candidates(content,reference)if reference else[]
        key=(self.scene_run,repr({k:content.get(k)for k in('kind','title','event_id')}),reference['source_identity']if reference else None,repr([r['id']for r in rows]))
        if key==self.event_key:return
        self._close_event();self.event_key=key;self.event_result=None;self.event_more.blockSignals(True);self.event_more.setChecked(False);self.event_more.blockSignals(False)
        self.event_choices.blockSignals(True);self.event_choices.clear();self.event_choices.addItem('请选择要查阅的准确事件资料',None)
        for i,row in enumerate(rows,1):self.event_choices.addItem(row['title']+' · '+('、'.join(row['node_types'])or'类别未确认')+' · 资料'+str(i),row['id'])
        self.event_choices.setCurrentIndex(0);self.event_choices.blockSignals(False);self.select_event()
        prefix='历史记录：'if self.historical_reading else'最近读取：'
        self.notice.setText((prefix+str(content.get('title')or'事件')+'。请选择对应资料；没有判断本局阶段、可选选项或奖励。')if rows else prefix+'事件暂无可核对的准确资料；没有借用相似名称，旧入口已清除。')

    def select_event(self,*_):
        self._close_event();identity=self.event_choices.currentData()
        self.event_result=events.reference(identity)if identity else None
        self.event_entries.blockSignals(True);self.event_entries.clear();self.event_entries.addItem('事件概况与起始资料',None)
        if self.event_result:
            for entry in self.event_result['selected']['entries']:
                label=('结果参考：'if entry['actual_game_button']is False else'选项资料：')+entry['title']
                self.event_entries.addItem(label,entry['key'])
        self.event_entries.blockSignals(False);self.read_event_entry()

    def read_event_entry(self,*_):
        self._close_event();result=self.event_result
        self.event_open.setEnabled(result is not None)
        text=event_excerpt(result,self.event_entries.currentData())if result else'请选择准确事件资料。同名条目或实际阶段未核对时，不自动认定选项可用。'
        if result and self.event_more.isChecked():text+='\n\n'+events.player_text(result,self.event_entries.currentData())
        self.event_text.setPlainText(text)
        from .player_reference_notes import note_for
        target=events.resolve(result,self.event_entries.currentData())if result else None
        self.event_note.setEnabled(bool(target and note_for('scenes',target['scene_id'])))

    def _target(self):
        self.refresh()
        return events.resolve(self.event_result,self.event_entries.currentData())if self.event_result else None

    def open_event(self):
        target=self._target()
        if target is None:
            self.event_key=None;self.refresh();return False
        self._close_event()
        from .current_event_directory_view import make_event_dialog
        from .player_map_reader import readable
        self.event_dialog=readable(make_event_dialog(target,self))
        if self.event_dialog is None:
            self.event_key=None;self.refresh();return False
        self.event_dialog.show();return True

    def write_event_note(self):
        target=self._target()
        from .player_reference_notes import note_for
        content=note_for('scenes',target['scene_id'])if target else None
        if content is not None:self.noteRequested.emit(deepcopy(content))

    def hideEvent(self,event):
        self._close_event();super().hideEvent(event)

    def closeEvent(self,event):
        self._close_event();super().closeEvent(event)
