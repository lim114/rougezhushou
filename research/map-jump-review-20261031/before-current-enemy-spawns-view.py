"""Player-facing direct spawn reverse lookup, owned by its exact battle page."""
from copy import deepcopy
from PySide6.QtCore import Qt,Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget,QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QPushButton,QTabWidget,QPlainTextEdit
from . import current_enemy_spawns as model
from .boss_hunt_view import _technical_json
from .ui_state import replace_text

class CurrentEnemySpawnsPanel(QWidget):
    actionSelected=Signal(str)
    actionPositionRequested=Signal(str)
    sourceInvalidated=Signal()
    def __init__(self,stage_id,enemy_key,parent=None):
        super().__init__(parent);self.stage_id=stage_id;self.enemy_key=enemy_key;self.result=None;self._view_key=None
        layout=QVBoxLayout(self);notice=QLabel(model.NOTICE);notice.setWordWrap(True);layout.addWidget(notice)
        bar=QHBoxLayout();self.kind=QComboBox()
        for k,v in model.KINDS:self.kind.addItem(v,k)
        self.refresh_button=QPushButton('重新核对对应条目');bar.addWidget(self.kind,1);bar.addWidget(self.refresh_button);layout.addLayout(bar)
        self.entries=QComboBox();self.entries.setMinimumContentsLength(16);self.entries.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon);layout.addWidget(self.entries)
        self.portrait=QLabel();self.portrait.setFixedHeight(76);self.portrait.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(self.portrait)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.technical=QPlainTextEdit()
        for w,n in((self.player,'出怪条目与条件'),(self.technical,'完整原值与来源')):w.setReadOnly(True);self.tabs.addTab(w,n)
        layout.addWidget(self.tabs,1);bar=QHBoxLayout();self.action_button=QPushButton('查看这条出怪条件');self.position_button=QPushButton('查看本条地图位置参考');bar.addWidget(self.action_button);bar.addWidget(self.position_button);layout.addLayout(bar)
        self.kind.currentIndexChanged.connect(self._filter_changed);self.entries.currentIndexChanged.connect(self.refresh_reference);self.refresh_button.clicked.connect(self.refresh_reference);self.action_button.clicked.connect(self.follow_action);self.position_button.clicked.connect(self.follow_position);self.refresh_reference()
    @staticmethod
    def _fill(widget,rows,selected=None):
        blocked=widget.blockSignals(True);widget.clear();widget.addItem('请选择一条对应记录'if rows else'此范围没有直接出怪记录',None)
        for row in rows:widget.addItem(row['label'],row['key'])
        widget.setCurrentIndex(max(0,widget.findData(selected)));widget.blockSignals(blocked)
    def clear_reference(self,*,notify=True):
        had=self.result is not None;self.result=None;self._view_key=None;self._fill(self.entries,[]);self.entries.setEnabled(False);self.portrait.clear();self.portrait.hide();self.action_button.setEnabled(False);self.position_button.setEnabled(False);replace_text(self.player,model.UNAVAILABLE,preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)
        if notify and had:self.sourceInvalidated.emit()
    def _filter_changed(self,*_):
        self._fill(self.entries,[]);return self.refresh_reference()
    def selected(self):
        return next((r for r in self.result['entries']if r['key']==self.entries.currentData()),None)if self.result else None
    def refresh_reference(self,*_):
        fresh=model.stage_reference(self.stage_id,self.enemy_key)
        if fresh is None:self.clear_reference();return False
        keep=self.result is not None and fresh['source_identity']==self.result['source_identity']and fresh['enemy_key']==self.result['enemy_key']and fresh['stage_id']==self.result['stage_id']
        key=self.entries.currentData()if keep else None;self.result=fresh;rows=model.rows(fresh,self.kind.currentData());self._fill(self.entries,rows,key);self.entries.setEnabled(bool(rows));row=self.selected();view=(deepcopy(fresh['source_identity']),self.kind.currentData(),row['key']if row else None);preserve=keep and view==self._view_key
        replace_text(self.player,model.player_text(fresh,row),preserve=preserve);replace_text(self.technical,_technical_json({'stage_id':fresh['stage_id'],'enemy_key':fresh['enemy_key'],'selected':row,'source_identity':fresh['source_identity'],'original_level_source':fresh['original_level_source'],'exact_enemy':fresh['enemy'],'all_corresponding_actions':fresh['entries'],'actual_occurrence':None,'actual_count':None,'absolute_time':None}),preserve=preserve)
        pix=QPixmap();raw=model.battle.picture_for_enemy(fresh['enemy']);self.portrait.show()
        if raw and pix.loadFromData(raw,'PNG'):self.portrait.setPixmap(pix.scaled(74,74,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        else:self.portrait.clear();self.portrait.setText('此精确引用未取得图片；不借用同名单位。')
        self.action_button.setEnabled(row is not None);self.position_button.setEnabled(row is not None)
        if not preserve:self.tabs.setCurrentIndex(0)
        self._view_key=view;return True
    def _resolve(self):
        row=self.selected()
        if row is None:return None
        resolved=model.resolve_action(self.result,row['key'])
        if resolved is None:self.clear_reference();return None
        return resolved
    def follow_action(self):
        selected=self._resolve()
        if selected is None:return False
        self.actionSelected.emit(selected['action_key']);return True
    def follow_position(self):
        selected=self._resolve()
        if selected is None:return False
        if model.position_reference(self.result,selected['action_key'])is None:self.clear_reference();return False
        self.actionPositionRequested.emit(selected['action_key']);return True

class CurrentEnemySpawnsDialog(QDialog):
    def __init__(self,stage_id,enemy_key,parent=None):
        super().__init__(parent);self.setWindowTitle('这个敌人的出怪条目与条件');self.resize(1040,780);layout=QVBoxLayout(self);self.panel=CurrentEnemySpawnsPanel(stage_id,enemy_key,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel.clear_reference();super().closeEvent(event)
    def done(self,result):self.panel.clear_reference();super().done(result)
