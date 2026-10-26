"""Original fixed enemy itineraries, with separate unbound spawn references."""
from copy import deepcopy
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QPushButton,QTabWidget,QPlainTextEdit,QLineEdit,QSplitter
from . import current_route_itinerary as model
from .current_map_position_view import CurrentTileGrid,CurrentOriginalCenters
from .boss_hunt_view import _technical_json
from .ui_state import replace_text
class CurrentRouteStepPositionPanel(QWidget):
    def __init__(self,stage_id,route_key,step_key,parent=None):
        super().__init__(parent);self.stage_id=stage_id;self.route_key=route_key;self.step_key=step_key;self.result=None;self.image_raw=None;layout=QVBoxLayout(self);split=QSplitter();self.grid=CurrentTileGrid();self.original=CurrentOriginalCenters();split.addWidget(self.grid);split.addWidget(self.original);layout.addWidget(split,2);self.player=QPlainTextEdit();self.player.setReadOnly(True);layout.addWidget(self.player,1);self.refresh_reference()
    def clear_reference(self):self.result=None;self.image_raw=None;self.grid.set_result(None);self.original.set_image(None);replace_text(self.player,model.UNAVAILABLE,preserve=False)
    def refresh_reference(self):
        ref=model.stage_reference(self.stage_id);fresh=model.position_reference(ref,self.route_key,self.step_key)if ref else None;raw=model.battle.version.image_bytes(fresh['grid']['image'])if fresh else None
        if fresh is None or raw is None:self.clear_reference();return False
        keep=self.result is not None and model.same(fresh,self.result);self.result=fresh;self.image_raw=raw;cell=fresh['cell'];self.grid.set_result(fresh['grid'],(cell['row'],cell['col']))
        if not self.original.set_image(raw,fresh['center']):self.clear_reference();return False
        text=model.step_label(fresh['step'])+'\n这里只查看所选环节的名义格；不与前后格连接，不代表实际脚点、偏移或传送配对。\n'+('此格有既有原图近似参考；绝对误差与其它位置仍需核验。'if fresh['center']else'此格没有可用的原图校准；左侧保留格子，右侧不猜标记。');replace_text(self.player,text,preserve=keep);return True
class CurrentRouteStepPositionDialog(QDialog):
    def __init__(self,stage_id,route_key,step_key,parent=None):
        super().__init__(parent);self.setWindowTitle('行程环节 · 固定位置参考');self.resize(1150,760);layout=QVBoxLayout(self);self.panel=CurrentRouteStepPositionPanel(stage_id,route_key,step_key,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel.clear_reference();super().closeEvent(event)
    def done(self,result):self.panel.clear_reference();super().done(result)
class CurrentRouteItineraryPanel(QWidget):
    actionSelected=Signal(str)
    sourceInvalidated=Signal()
    def __init__(self,stage_id,parent=None):
        super().__init__(parent);self.stage_id=stage_id;self.result=None;self._view_key=None;self.position_dialog=None;layout=QVBoxLayout(self);notice=QLabel(model.NOTICE);notice.setWordWrap(True);layout.addWidget(notice)
        bar=QHBoxLayout();self.search=QLineEdit();self.search.setPlaceholderText('输入敌人中文名或路线名称');self.scope=QComboBox()
        for k,v in model.SCOPES:self.scope.addItem(v,k)
        self.refresh_button=QPushButton('重新核对完整行程');bar.addWidget(self.search,2);bar.addWidget(self.scope,1);bar.addWidget(self.refresh_button);layout.addLayout(bar)
        self.entries=QComboBox();self.steps=QComboBox();self.actions=QComboBox();self.unassigned=QComboBox()
        for w in(self.entries,self.steps,self.actions,self.unassigned):w.setMinimumContentsLength(14);w.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        layout.addWidget(QLabel('选择原路线及环节'));layout.addWidget(self.entries);layout.addWidget(self.steps);layout.addWidget(self.actions);layout.addWidget(QLabel('路线未确认的出怪（单独查阅，不归入上方路线）'));layout.addWidget(self.unassigned)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.technical=QPlainTextEdit()
        for w,n in((self.player,'完整行程与等待条件'),(self.technical,'原路线与准确来源')):w.setReadOnly(True);self.tabs.addTab(w,n)
        layout.addWidget(self.tabs,1);bar=QHBoxLayout();self.action_button=QPushButton('查看准确出怪条目');self.position_button=QPushButton('查看所选环节的地图参考');bar.addWidget(self.action_button);bar.addWidget(self.position_button);layout.addLayout(bar)
        self.search.textChanged.connect(self._filter_changed);self.scope.currentIndexChanged.connect(self._filter_changed);self.entries.currentIndexChanged.connect(self._route_changed);self.steps.currentIndexChanged.connect(self._step_changed);self.actions.currentIndexChanged.connect(self.refresh_reference);self.unassigned.currentIndexChanged.connect(self._unassigned_changed);self.refresh_button.clicked.connect(self.refresh_reference);self.action_button.clicked.connect(self.follow_action);self.position_button.clicked.connect(self.open_position);self.refresh_reference()
    @staticmethod
    def _fill(widget,rows,selected=None,placeholder='请手动选择'):
        blocked=widget.blockSignals(True);widget.clear();widget.addItem(placeholder,None)
        for label,key in rows:widget.addItem(label,key)
        widget.setCurrentIndex(max(0,widget.findData(selected)));widget.blockSignals(blocked)
    def close_children(self):
        if self.position_dialog is not None:self.position_dialog.panel.clear_reference();self.position_dialog.close()
        self.position_dialog=None
    def clear_reference(self,*,notify=True):
        had=self.result is not None;self.close_children();self.result=None;self._view_key=None
        for w in(self.entries,self.steps,self.actions,self.unassigned):self._fill(w,[]);w.setEnabled(False)
        self.action_button.setEnabled(False);self.position_button.setEnabled(False);replace_text(self.player,model.UNAVAILABLE,preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)
        if notify and had:self.sourceInvalidated.emit()
    def _filter_changed(self,*_):
        self.close_children()
        for w in(self.entries,self.steps,self.actions,self.unassigned):self._fill(w,[])
        self.refresh_reference()
    def _route_changed(self,*_):
        self.close_children()
        for w in(self.steps,self.actions,self.unassigned):self._fill(w,[])
        self.refresh_reference()
    def _step_changed(self,*_):self.close_children();self.refresh_reference()
    def _unassigned_changed(self,*_):
        self.close_children()
        if self.unassigned.currentData()is not None:
            for w in(self.entries,self.steps,self.actions):self._fill(w,[])
        self.refresh_reference()
    def selected_route(self):return next((r for r in self.result['entries']if r['key']==self.entries.currentData()),None)if self.result else None
    def selected_step(self):
        route=self.selected_route();return next((s for s in route['steps']if s['key']==self.steps.currentData()),None)if route else None
    def selected_action(self):
        route=self.selected_route()
        if route is not None:return next((a for a in route['actions']if a['key']==self.actions.currentData()),None)
        return next((a['action']for a in self.result['unassigned_actions']if a['action']['key']==self.unassigned.currentData()),None)if self.result else None
    def refresh_reference(self,*_):
        fresh=model.stage_reference(self.stage_id)
        if fresh is None:self.clear_reference();return False
        keep=self.result is not None and self.result['source_identity']==fresh['source_identity']and self.result['stage_id']==fresh['stage_id'];keys=[w.currentData()if keep else None for w in(self.entries,self.steps,self.actions,self.unassigned)]
        if not keep:self.close_children()
        self.result=fresh;routes=model.routes(fresh,self.search.text(),self.scope.currentData());self._fill(self.entries,[(r['label']+(' · '+' / '.join(r['enemy_names'])if r['enemy_names']else''),r['key'])for r in routes],keys[0],'请选择原路线'if routes else'此范围未找到原路线');self.entries.setEnabled(bool(routes));route=self.selected_route();steps=route['steps']if route else[];actions=route['actions']if route else[];self._fill(self.steps,[(model.step_label(s),s['key'])for s in steps],keys[1],'请选择一处行程环节');self.steps.setEnabled(bool(steps));self._fill(self.actions,[(model.battle.action_label(a),a['key'])for a in actions],keys[2],'请选择准确引用此基础路线的主波次出怪'if actions else'未取得准确绑定的主波次出怪');self.actions.setEnabled(bool(actions));self._fill(self.unassigned,[(model.battle.action_label(a['action'])+' · '+a['reason'],a['action']['key'])for a in fresh['unassigned_actions']],keys[3]if route is None else None,'请选择路线未确认的出怪');self.unassigned.setEnabled(bool(fresh['unassigned_actions']));step=self.selected_step();action=self.selected_action();unbound=route is None and action is not None
        view=(deepcopy(fresh['source_identity']),self.search.text(),self.scope.currentData(),route['key']if route else None,step['key']if step else None,action['key']if action else None,unbound);preserve=keep and view==self._view_key;replace_text(self.player,model.player_text(fresh,route,step,action,unbound),preserve=preserve);replace_text(self.technical,_technical_json({'stage_id':fresh['stage_id'],'source_identity':fresh['source_identity'],'original_level_source':fresh['original_level_source'],'selected_route':route,'selected_step':step,'selected_action':action,'unbound_action_selected':unbound,'route_count':len(fresh['entries']),'unassigned_action_count':len(fresh['unassigned_actions']),'actual_route':None,'actual_path':None,'absolute_time':None}),preserve=preserve);self.action_button.setEnabled(action is not None);self.position_button.setEnabled(bool(step and step['spatial_reference_permitted']))
        if not preserve:self.tabs.setCurrentIndex(0)
        if self.position_dialog is not None and self.position_dialog.isVisible():
            p=self.position_dialog.panel
            if route is None or step is None or(p.route_key,p.step_key)!=(route['key'],step['key'])or not p.refresh_reference():self.close_children()
        self._view_key=view;return True
    def follow_action(self):
        route=self.selected_route();action=self.selected_action()
        if action is None:return False
        selected=model.resolve(self.result,route['key']if route else None,action_key=action['key'])
        if selected is None:self.clear_reference();return False
        self.actionSelected.emit(action['key']);return True
    def open_position(self):
        route=self.selected_route();step=self.selected_step()
        if route is None or step is None or not step['spatial_reference_permitted']:return False
        ref=model.position_reference(self.result,route['key'],step['key'])
        if ref is None:self.clear_reference();return False
        self.close_children();self.position_dialog=CurrentRouteStepPositionDialog(self.stage_id,route['key'],step['key'],self)
        if self.position_dialog.panel.result is None:self.close_children();return False
        self.position_dialog.show();return True
class CurrentRouteItineraryDialog(QDialog):
    def __init__(self,stage_id,parent=None):
        super().__init__(parent);self.setWindowTitle('完整敌人行程与停留条件');self.resize(1100,820);layout=QVBoxLayout(self);self.panel=CurrentRouteItineraryPanel(stage_id,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel.clear_reference();super().closeEvent(event)
    def done(self,result):self.panel.clear_reference();super().done(result)
