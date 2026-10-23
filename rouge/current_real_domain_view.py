"""Player-facing real-domain directory; every manual condition stays local."""
from copy import deepcopy
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QDialog,QVBoxLayout,QHBoxLayout,QGridLayout,
    QLabel,QComboBox,QSpinBox,QLineEdit,QListWidget,QListWidgetItem,QPlainTextEdit,
    QTabWidget,QPushButton,QSplitter)
from . import current_real_domain as model
from .ui_state import replace_text


class CurrentRealDomainPanel(QWidget):
    def __init__(self,target=None,parent=None):
        super().__init__(parent)
        self.result=None;self.row_id=None;self.source_identity=None;self.event_dialog=None;self.source_request=None
        layout=QVBoxLayout(self)
        self.notice=QLabel(model.NOTICE);self.notice.setWordWrap(True);layout.addWidget(self.notice)
        self.source_banner=QLabel();self.source_banner.setWordWrap(True);self.source_banner.hide();layout.addWidget(self.source_banner)
        filters=QHBoxLayout();self.kind=QComboBox()
        for label,value in(('总览：理念与方针',None),('理念：节点内的核心影响','idea'),('方针：途经节点的附加影响','policy')):self.kind.addItem(label,value)
        self.type_filter=QComboBox();self.type_filter.addItem('全部名称',None)
        self.search=QLineEdit();self.search.setPlaceholderText('按游戏内中文名称搜索')
        self.refresh_button=QPushButton('重新核对资料')
        for widget in(self.kind,self.type_filter,self.search,self.refresh_button):filters.addWidget(widget)
        layout.addLayout(filters);self.count=QLabel();layout.addWidget(self.count)
        self.conditions=QWidget();grid=QGridLayout(self.conditions);grid.setContentsMargins(0,0,0,0)
        self.mode=QComboBox()
        for label,value in(('模式未知',None),('常规探索','NORMAL'),('其它模式（不套常规门槛）','OTHER')):self.mode.addItem(label,value)
        self.difficulty=QSpinBox();self.difficulty.setRange(-1,16);self.difficulty.setSpecialValueText('未知');self.difficulty.setValue(-1)
        self.floor=QSpinBox();self.floor.setRange(0,6);self.floor.setSpecialValueText('未知或特殊区域');self.floor.setValue(0)
        self.affected=QComboBox()
        for label,value in(('是否受影响未知',None),('本页声明：受影响',True),('本页声明：不受影响',False)):self.affected.addItem(label,value)
        self.action=QComboBox()
        for label,value in(('行为未知',None),('进入内部，经过结算另核','enter'),('只途经，不进入内部','pass'),('途经并进入内部','both')):self.action.addItem(label,value)
        self.squad=QComboBox();self.squad.addItem('分队或档位未知',None)
        for label,key in(('文明开化：原基础档','rogue_6_band_15'),('文明开化：免疫方针档','rogue_6_band_16'),('文明开化：四藏品免疫档','rogue_6_band_25')):self.squad.addItem(label,key)
        self.paired=QComboBox();self.paired.addItem('另一效果未知',None)
        self.labels={}
        for index,(key,label)in enumerate((('mode','本页模式'),('difficulty','保密等级'),('affected','该节点是否受影响'),('action','本页对照的行为'),('floor','所在主层'),('squad','文明开化原档位'),('paired','同处的另一类效果'))):
            lab=QLabel(label);self.labels[key]=lab;widget=getattr(self,key);widget.setAccessibleName('仅本页对照：'+label)
            row,column=divmod(index,2);grid.addWidget(lab,row,column*2);grid.addWidget(widget,row,column*2+1)
        layout.addWidget(self.conditions)
        split=QSplitter();self.entries=QListWidget();self.entries.setAccessibleName('实托邦理念三档与方针目录');split.addWidget(self.entries)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.technical=QPlainTextEdit()
        for widget in(self.player,self.technical):widget.setReadOnly(True)
        self.tabs.addTab(self.player,'影响、条件与例外');self.tabs.addTab(self.technical,'完整原项与来源');split.addWidget(self.tabs);split.setSizes([320,780]);layout.addWidget(split,1)
        self.origin_row=QWidget();actions=QHBoxLayout(self.origin_row);actions.setContentsMargins(0,0,0,0)
        self.origins=QComboBox();self.open_button=QPushButton('查看对应事件原文');actions.addWidget(self.origins,1);actions.addWidget(self.open_button);layout.addWidget(self.origin_row)
        self.kind.currentIndexChanged.connect(self._filter_changed);self.type_filter.currentIndexChanged.connect(self._filter_changed);self.search.textChanged.connect(self._filter_changed)
        for combo in(self.mode,self.affected,self.action,self.squad,self.paired):combo.currentIndexChanged.connect(self.refresh_reference)
        self.difficulty.valueChanged.connect(self.refresh_reference);self.floor.valueChanged.connect(self.refresh_reference)
        self.entries.currentItemChanged.connect(self._selected);self.refresh_button.clicked.connect(self.refresh_reference);self.open_button.clicked.connect(self.open_origin)
        self.origins.currentIndexChanged.connect(lambda:self.open_button.setEnabled(self.origins.currentData()is not None))
        self.refresh_reference()
        if target is not None:
            fresh=model.locate(target.get('source_category'),target.get('source_id'))if type(target)is dict else None
            if fresh==target:
                self.source_request=deepcopy(target)
                self.kind.setCurrentIndex(self.kind.findData(target['kind']));self.type_filter.setCurrentIndex(self.type_filter.findData(target['type_id']))

    def _filters(self):return {'kind':self.kind.currentData(),'type_id':self.type_filter.currentData(),'query':self.search.text()}
    def _context(self):return {'mode':self.mode.currentData(),'difficulty':None if self.difficulty.value()<0 else self.difficulty.value(),
        'floor':None if self.floor.value()==0 else self.floor.value(),'affected':self.affected.currentData(),
        'action':self.action.currentData(),'squad':self.squad.currentData(),'paired':self.paired.currentData()}

    def close_children(self):
        if self.event_dialog is not None:self.event_dialog.close()
        self.event_dialog=None

    def _unavailable(self):
        self.close_children();self.source_identity=None;self.result=None;self.row_id=None;self.source_request=None;self.source_banner.clear();self.source_banner.hide()
        blocked=self.entries.blockSignals(True)
        try:self.entries.clear()
        finally:self.entries.blockSignals(blocked)
        replace_text(self.player,'',preserve=False);replace_text(self.technical,'',preserve=False)
        self.conditions.hide();self.origin_row.hide();self.open_button.setEnabled(False);self.count.setText(model.UNAVAILABLE)

    def _filter_changed(self,*_):self._populate(preserve=False)

    def _populate(self,*,preserve):
        base=model.reference(kind=self.kind.currentData())
        if base is None:self._unavailable();return False
        oldtype=self.type_filter.currentData();blocked=self.type_filter.blockSignals(True)
        try:
            self.type_filter.clear();self.type_filter.addItem('全部名称',None)
            seen=set()
            for row in base['rows']:
                if row['type']in seen:continue
                seen.add(row['type']);self.type_filter.addItem(row['name'],row['type'])
            self.type_filter.setCurrentIndex(max(0,self.type_filter.findData(oldtype)))
        finally:self.type_filter.blockSignals(blocked)
        fresh=model.reference(**self._filters(),**self._context())
        if fresh is None:self._unavailable();return False
        selected=self.row_id if preserve and self.source_identity==fresh['source_identity']else None
        self.source_identity=fresh['source_identity'];blocked=self.entries.blockSignals(True)
        try:
            self.entries.clear()
            for row in fresh['rows']:
                item=QListWidgetItem(row['name']+(' · '+row['level_name']if row['kind']=='idea'else' · 方针'))
                item.setData(Qt.ItemDataRole.UserRole,row['id']);self.entries.addItem(item)
                if row['id']==selected:self.entries.setCurrentItem(item)
        finally:self.entries.blockSignals(blocked)
        self.count.setText('当前筛选列出'+str(len(fresh['rows']))+'份原项；同一理念的早、中、晚期分别保留，不是同时叠加。')
        if self.entries.currentItem()is None:
            self.entries.setCurrentRow(-1);self.row_id=None;self.close_children();self._show(fresh,preserve=False)
        else:self._selected(self.entries.currentItem(),preserve=True)
        return True

    def refresh_reference(self,*_):return self._populate(preserve=True)

    def _selected(self,item,*_,preserve=False):
        identity=item.data(Qt.ItemDataRole.UserRole)if item else None
        context=self._context()
        if identity!=self.row_id:context['paired']=None
        fresh=model.reference(identity,**self._filters(),**context)
        if fresh is None or fresh['source_identity']!=self.source_identity:self._unavailable();return
        keep=preserve and identity==self.row_id
        if not keep:
            self.close_children();row=fresh['selected'];old=self.result['selected']if self.result else None
            previous=self.paired.currentData()if row and old and row['type']==old['type']else None
            blocked=self.paired.blockSignals(True)
            try:
                self.paired.clear();self.paired.addItem('另一效果未知',None)
                wanted='idea'if row and row['kind']=='policy'else'policy'
                seen=set()
                for source in fresh['data']['rows']:
                    if source['kind']==wanted and source['type']not in seen:
                        seen.add(source['type']);self.paired.addItem(source['name'],source['type'])
                self.paired.setCurrentIndex(max(0,self.paired.findData(previous)))
            finally:self.paired.blockSignals(blocked)
            fresh=model.reference(identity,**self._filters(),**self._context())
            if fresh is None:self._unavailable();return
        self.row_id=identity;self._show(fresh,preserve=keep)
        if keep and self.event_dialog is not None and self.event_dialog.isVisible():self.event_dialog.panel.refresh_reference()

    def _show(self,result,*,preserve):
        self.result=deepcopy(result);row=result['selected'];self.conditions.setVisible(row is not None)
        for key in('floor','squad','paired'):
            visible=bool(row and((key=='floor'and row['type']=='rogue_6_weather_1')or(key=='squad'and row['kind']=='policy')or(key=='paired'and(row['kind']=='policy'or row['type']==model.HOPE))))
            self.labels[key].setVisible(visible);getattr(self,key).setVisible(visible)
        if self.source_request:
            name='呼吸的红苔相关原文'if self.source_request['type_id']==model.HOPE else'安眠一隅原场景'
            self.source_banner.setText('最初由'+name+'打开；这里只筛出相关理念，具体档位、实际触发和当前节点仍未知。')
        self.source_banner.setVisible(self.source_request is not None)
        replace_text(self.player,model.player_text(result),preserve=preserve);replace_text(self.technical,json.dumps({'reference':result,'opening_source':self.source_request},ensure_ascii=False,indent=2),preserve=preserve)
        if not preserve:self.tabs.setCurrentIndex(0)
        old=self.origins.currentData();blocked=self.origins.blockSignals(True)
        try:
            self.origins.clear();self.origins.addItem('请选择一条相关事件原文',None)
            for link in result['related_origins']:self.origins.addItem(link['label'],link['key'])
            self.origins.setCurrentIndex(max(0,self.origins.findData(old)))
        finally:self.origins.blockSignals(blocked)
        self.origin_row.setVisible(bool(result['related_origins']));self.open_button.setEnabled(self.origins.currentData()is not None)

    def open_origin(self):
        key=self.origins.currentData()
        if self.result is None or key is None:return False
        fresh=model.reference(self.row_id,**self._filters(),**self._context())
        if fresh is None or fresh!=self.result:self._unavailable();return False
        link=model.destination(key)
        if link is None or link not in fresh['related_origins']:return False
        self.close_children();target=link['target']
        if link['reader']=='vine':
            from .current_vine_events_view import CurrentVineEventsDialog
            self.event_dialog=CurrentVineEventsDialog(target['event_id'],target['scene_id'],target['choice_id'],self)
        elif link['reader']=='resting':
            from .current_resting_view import CurrentRestingDialog
            self.event_dialog=CurrentRestingDialog(target,self)
        else:return False
        if self.event_dialog.panel.result is None:self.close_children();return False
        self.event_dialog.show();return True

    def closeEvent(self,event):self.close_children();super().closeEvent(event)


class CurrentRealDomainDialog(QDialog):
    def __init__(self,target=None,parent=None):
        super().__init__(parent);self.setWindowTitle('实托邦 · 理念、方针与条件');self.resize(1100,820)
        layout=QVBoxLayout(self);self.panel=CurrentRealDomainPanel(target,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel.close_children();super().closeEvent(event)
