"""Exact current objects and their original activation/map references."""
from copy import deepcopy
from PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QPushButton,QTabWidget,QPlainTextEdit,QLineEdit
from . import current_stage_objects as model
from .current_map_position_view import FixedPositionPanel
from .boss_hunt_view import _technical_json
from .ui_state import replace_text
from .reference_copy import mechanism_copy

class CurrentObjectPositionPanel(FixedPositionPanel):
    def __init__(self, stage_id, key, parent=None, *, initial_reference=...):
        super().__init__(stage_id, model, parent)
        self.key = key
        self.refresh_reference(prepared_reference=initial_reference)

    def _read_position(self):
        reference = model.stage_reference(self.stage_id)
        return model.position_reference(reference, self.key) if reference else None

    def _render_position(self, fresh, keep):
        cell = fresh['cell']
        text=fresh['row']['name']+f" · 声明格：第{cell['row']+1}行第{cell['col']+1}列。\n这里只显示原声明格，不代表实际启用、当前存在或实际脚点。\n"
        text+=('该格有既有原图近似参考；误差与其它地块仍需核对。'if fresh['center']else'这个格尚无可用的原图校准；左侧可看格子，右侧保留原图，不猜标记。')
        replace_text(self.details,text,preserve=keep);replace_text(self.player,fresh['row']['name']+f" · 第{cell['row']+1}行，第{cell['col']+1}列。\n原图标记："+('参考位置。'if fresh['center']else'待校准。'),preserve=keep)

from .player_window_frame import PlayerDialog


class CurrentObjectPositionDialog(PlayerDialog):
    def __init__(self,stage_id,key,parent=None,*,initial_reference=...):
        super().__init__(parent);self.setWindowTitle('物件与机关 · 固定位置参考');layout=QVBoxLayout(self);self.panel=CurrentObjectPositionPanel(stage_id,key,self,initial_reference=initial_reference);layout.addWidget(self.panel)
        from .player_map_reader import prepare_reference_window
        prepare_reference_window(self,960,640)
    def done(self,result):self.panel.clear_reference();super().done(result)

class CurrentStageObjectsPanel(QWidget):
    actionSelected=Signal(str)
    sourceInvalidated=Signal()
    def __init__(self,stage_id,parent=None):
        super().__init__(parent);self.stage_id=stage_id;self.result=None;self._view_key=None;self.position_dialog=None;layout=QVBoxLayout(self);notice=QLabel('查看本关物件、机关和对应位置。');notice.setToolTip(model.NOTICE);notice.setWordWrap(True);layout.addWidget(notice)
        bar=QHBoxLayout();self.search=QLineEdit();self.search.setPlaceholderText('输入物件中文名');self.kind=QComboBox();self.link=QComboBox()
        for k,v in model.KINDS:self.kind.addItem(v,k)
        for k,v in model.LINKS:self.link.addItem(v,k)
        bar.addWidget(self.search,2);bar.addWidget(self.kind,1);bar.addWidget(self.link,1);layout.addLayout(bar)
        self.refresh_button=QPushButton('重新核对本关物件');layout.addWidget(self.refresh_button);self.entries=QComboBox();self.entries.setMinimumContentsLength(16);self.entries.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon);self.activations=QComboBox();layout.addWidget(self.entries);layout.addWidget(self.activations)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.technical=QPlainTextEdit()
        for w,n in((self.player,'作用与出现条件'),(self.technical,'完整原值与来源')):w.setReadOnly(True);self.tabs.addTab(w,n)
        layout.addWidget(self.tabs,1);bar=QHBoxLayout();self.action_button=QPushButton('查看所选启用条目');self.position_button=QPushButton('查看本物件声明位置');bar.addWidget(self.action_button);bar.addWidget(self.position_button);layout.addLayout(bar)
        self.search.textChanged.connect(self._filter_changed);self.kind.currentIndexChanged.connect(self._filter_changed);self.link.currentIndexChanged.connect(self._filter_changed);self.entries.currentIndexChanged.connect(self._entry_changed);self.activations.currentIndexChanged.connect(self.refresh_reference);self.refresh_button.clicked.connect(self.refresh_reference);self.action_button.clicked.connect(self.follow_action);self.position_button.clicked.connect(self.open_position);self.refresh_reference()
    @staticmethod
    def _fill(widget,rows,selected=None,placeholder='请选择一份声明'):
        blocked=widget.blockSignals(True);widget.clear();widget.addItem(placeholder,None)
        for label,key in rows:widget.addItem(label,key)
        widget.setCurrentIndex(max(0,widget.findData(selected)));widget.blockSignals(blocked)
    def close_children(self):
        if self.position_dialog is not None:self.position_dialog.close()
        self.position_dialog=None
    def clear_reference(self,*,notify=True):
        had=self.result is not None;self.close_children();self.result=None;self._view_key=None;self._fill(self.entries,[]);self._fill(self.activations,[]);self.entries.setEnabled(False);self.activations.setEnabled(False);self.action_button.setEnabled(False);self.position_button.setEnabled(False);replace_text(self.player,model.UNAVAILABLE,preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)
        if notify and had:self.sourceInvalidated.emit()
    def _filter_changed(self,*_):self.close_children();self._fill(self.entries,[]);self._fill(self.activations,[]);self.refresh_reference()
    def _entry_changed(self,*_):self.close_children();self._fill(self.activations,[]);self.refresh_reference()
    def selected(self):
        if self.result is None:return None
        key=self.entries.currentData()
        return next((r for r in self.result['entries']if r['key']==key),None)
    def selected_action(self,*,row=...):
        if row is ...:row=self.selected()
        if row is None:return None
        key=self.activations.currentData()
        return next((a for a in row['activation_actions']if a['key']==key),None)
    def refresh_reference(self,*_):
        fresh=model.stage_reference(self.stage_id)
        if fresh is None:self.clear_reference();return False
        keep=self.result is not None and fresh['source_identity']==self.result['source_identity']and fresh['stage_id']==self.result['stage_id'];key=self.entries.currentData()if keep else None;action_key=self.activations.currentData()if keep else None
        if not keep:self.close_children()
        query=self.search.text();kind=self.kind.currentData();link=self.link.currentData()
        self.result=fresh;rows=model.rows(fresh,query,kind,link);self._fill(self.entries,[(model.label(r),r['key'])for r in rows],key,'请选择一份物件或卡片声明'if rows else'此范围未找到声明');self.entries.setEnabled(bool(rows));row=self.selected();actions=row['activation_actions']if row else[];self._fill(self.activations,[(model.battle.action_label(a),a['key'])for a in actions],action_key,'请选择一条启用记录'if actions else'未找到直接启用记录');self.activations.setEnabled(bool(actions));action=self.selected_action(row=row)
        view=(deepcopy(fresh['source_identity']),query,kind,link,row['key']if row else None,action['key']if action else None);preserve=keep and view==self._view_key
        full_text=model.player_text(fresh,row,action);text=full_text.replace(f"资料中共{len(fresh['entries'])}条预置声明；这不是当前场上数量或本局实际持有数量。",f"预置物件与卡片：{len(fresh['entries'])}条。").replace('。这不证明当前可见或已经启用。','。').replace('；不据此绘制攻击或影响范围。','。');replace_text(self.player,mechanism_copy(text,model.NOTICE,extra_detail_headings=('【使用提醒】',))[0],preserve=preserve);replace_text(self.technical,_technical_json({'完整说明':full_text,'reference':fresh,'selected':row,'activation':action,'actual_active':None,'actual_reward':None}),preserve=preserve);self.action_button.setEnabled(action is not None);self.position_button.setEnabled(bool(row and row['kind']=='instance'and isinstance(row['raw'].get('position'),dict)))
        if not preserve:self.tabs.setCurrentIndex(0)
        if self.position_dialog is not None and self.position_dialog.isVisible():
            if row is None or self.position_dialog.panel.key!=row['key']or not self.position_dialog.panel.refresh_reference():self.close_children()
        self._view_key=view;return True
    def follow_action(self):
        row=self.selected();action=self.selected_action(row=row)
        if row is None or action is None:return False
        resolved=model.resolve(self.result,row['key'],action['key'])
        if resolved is None:self.clear_reference();return False
        self.actionSelected.emit(action['key']);return True
    def open_position(self):
        row=self.selected()
        if row is None or row['kind']!='instance':return False
        result=model.position_reference(self.result,row['key'])
        if result is None:self.clear_reference();return False
        from .battle_tool_readers import open_position
        opened=open_position(self,'object',(self.stage_id,row['key']),initial_reference=result)
        if opened is not None:return opened
        self.close_children();self.position_dialog=CurrentObjectPositionDialog(self.stage_id,row['key'],self,initial_reference=result)
        if self.position_dialog.panel.result is None:self.close_children();return False
        self.position_dialog.show();return True

class CurrentStageObjectsDialog(PlayerDialog):
    def __init__(self,stage_id,parent=None):
        super().__init__(parent);self.setWindowTitle('本关物件与机关');layout=QVBoxLayout(self);self.panel=CurrentStageObjectsPanel(stage_id,self);layout.addWidget(self.panel)
        from .player_map_reader import prepare_reference_window
        prepare_reference_window(self,760,600)
    def done(self,result):self.panel.clear_reference();super().done(result)
