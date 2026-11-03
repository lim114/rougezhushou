"""Manual fixed-battle entry reading. No live game or qualification actions."""
from copy import deepcopy
import json
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
    QPushButton,QPlainTextEdit,QTabWidget,QWidget)
from . import battle_event_references as events
from .stage_entry_reference import stage_entry_reference
from .player_node_information import _plain
from .ui_state import replace_text

NOTICE='这里只查阅这张固定战斗地图的关联入口；不表示本局已出现、已进入或一定能进入。'

def entry_packet(stage_id):
    result=events.stage_event_references(stage_id)
    if result is not None:return {'kind':'event','result':result}
    result=stage_entry_reference(stage_id)
    return {'kind':'configuration','result':result} if result is not None else None

def configuration_text(result):
    lines=[_plain(result['stage_name'])+' · 关联的节点标记',NOTICE,'',
        '【原始资料列出的关联节点】']
    for row in result['rows']:
        floor=row['main_floor_reference']
        label=f'第{floor}层普通作战' if type(floor) is int else '原资料称“假层”的普通作战（主层归属未确认）'
        lines.append('• '+label+'：关联狼兽主标记“'+_plain(result['marker']['item']['name'])+'”。')
    lines+=['这些记录并未说明标记在本局何时生成、会落在哪个节点；也不保证每层都有一场。',
        '“假层”只保留原资料称呼，不能据此归到第4层或秘境。','',
        '【社区资料中的进入说明】',_plain(result['community_reference']['text']),
        '其中的“未持有”条件来自这段资料；当前是否满足、标记是否已生效与实际领取仍未确认。','',
        '【标记说明原文】',_plain(result['marker']['item'].get('usage')),'']
    for key in ('beacon_item','not_hold_item'):
        item=result[key]['item']
        lines += ['【相关藏品：'+_plain(item['name'])+'】',_plain(item.get('usage')),'']
    lines += ['持有相关藏品不能直接证明本局已经生成这个标记。',
        '本关全部进入方式、完整来源层数、出现数量和本局节点位置：尚未确认。']
    return '\n'.join(lines)

def event_reference_text(packet,row):
    stage=packet['stage_reference'];difficulty={'NORMAL':'普通','FOUR_STAR':'紧急'}.get(stage['difficulty'],'难度未确认')
    lines=[_plain(stage['name'])+' · '+difficulty,NOTICE,'',
        '以下列的是资料明确连接到这个关卡版本的具体选项，不代表完整的所有入口。']
    if packet.get('excluded_rows'):
        lines.append('明确要求紧急作战的选项不作为这个普通版本的入口；对应原文可在“资料与依据”查看。')
    if row is None:
        return '\n'.join(lines+['','请在上方选择事件与完整选项，再点击“阅读对应事件选项”。',
            '未选择任何游戏选项，也不会自动跳转。'])
    floors='、'.join(f'第{x}层' for x in row['event_documented_main_floors']) or '未确认'
    lines += ['', '【对应的事件选项】',_plain(row['event_title'])+' · 场景'+str(row['scene_number']),
        _plain(row['choice_title']),_plain(row['choice_description'])]
    if row.get('conditional_text'):lines += ['选项原注：'+_plain(row['conditional_text'])]
    lines += ['', '【适用范围】','该事件资料记录的主层：'+floors+'。',
        '这些层数只属于这条事件入口，不能当作该战斗所有来源的完整层数。',
        '事件是否出现、按钮是否可选、实际进入哪个关卡版本：仍未确认。',
        '点击“阅读对应事件选项”只会打开助手中的事件资料，并定位到这份完整场景和选项。']
    return '\n'.join(lines)

class BattleEntryReferencePanel(QDialog):
    eventReferenceSelected=Signal(object)
    def __init__(self,parent=None):
        super().__init__(parent);self.setWindowTitle('战斗对应的节点与进入方式');self.setModal(False);self.resize(900,680)
        self.stage_id=None;self.packet=None;self._view_key=None
        layout=QVBoxLayout(self);self.notice=QLabel(NOTICE);self.notice.setWordWrap(True);layout.addWidget(self.notice)
        self.event_bar=QWidget();row=QHBoxLayout(self.event_bar);row.setContentsMargins(0,0,0,0)
        self.event_choice=QComboBox();self.event_choice.setAccessibleName('对应固定战斗的完整事件选项')
        self.event_choice.setPlaceholderText('请选择要阅读的事件与完整选项')
        self.open_event_button=QPushButton('阅读对应事件选项');self.open_event_button.setEnabled(False)
        row.addWidget(self.event_choice,1);row.addWidget(self.open_event_button);layout.addWidget(self.event_bar)
        self.reading_tabs=QTabWidget();self.reference_text=QPlainTextEdit();self.source_text=QPlainTextEdit()
        for reader,label in ((self.reference_text,'进入方式说明'),(self.source_text,'资料与依据')):
            reader.setReadOnly(True);reader.setAccessibleName('战斗入口 · '+label);self.reading_tabs.addTab(reader,label)
        layout.addWidget(self.reading_tabs,1)
        self.event_choice.currentIndexChanged.connect(self.refresh_reference)
        self.open_event_button.clicked.connect(self.open_selected_event)
        self.refresh_reference()

    def _populate(self,rows,selected):
        self.event_choice.blockSignals(True)
        try:
            self.event_choice.clear()
            for row in rows:
                label=f"{_plain(row['event_title'])} · 场景{row['scene_number']} · {_plain(row['choice_title'])}"
                if row.get('conditional_text'):label+='（'+_plain(row['conditional_text'])+'）'
                self.event_choice.addItem(label,row['reference_id'])
            self.event_choice.setCurrentIndex(self.event_choice.findData(selected) if type(selected) is str else -1)
        finally:self.event_choice.blockSignals(False)

    def _invalidate(self,message):
        self.packet=None;self._view_key=None;self._populate([],None);self.open_event_button.setEnabled(False)
        for reader in (self.reference_text,self.source_text):replace_text(reader,message,preserve=False)

    def set_stage(self,stage_id):
        if stage_id!=self.stage_id:
            self._invalidate('尚未选择入口；请选择资料后阅读。');self.reading_tabs.setCurrentIndex(0)
        self.stage_id=stage_id;self.refresh_reference()

    def refresh_reference(self,*_):
        selected=self.event_choice.currentData()
        try:packet=entry_packet(self.stage_id)
        except (OSError,ValueError,KeyError,TypeError):packet=None
        kind=packet['kind'] if packet else None;self.event_bar.setVisible(kind=='event')
        if not packet or packet['result'].get('status')!='documented_reference':
            self._invalidate('进入方式资料暂时无法核对；旧条目与说明已清除，请稍后重新选择。');return
        self.packet=packet;result=packet['result']
        if kind=='event':
            self._populate(result['rows'],selected)
            chosen=next((r for r in result['rows'] if r['reference_id']==self.event_choice.currentData()),None)
            key=(self.stage_id,kind,chosen['reference_id'] if chosen else None)
            self.open_event_button.setEnabled(chosen is not None)
            text=event_reference_text(result,chosen)
        else:
            self._populate([],None);self.open_event_button.setEnabled(False);key=(self.stage_id,kind)
            text=configuration_text(result)
        same=key==self._view_key
        replace_text(self.reference_text,text,preserve=same)
        replace_text(self.source_text,json.dumps(result,ensure_ascii=False,indent=2),preserve=same)
        self._view_key=key

    def open_selected_event(self):
        if not self.packet or self.packet['kind']!='event':return
        selected=self.event_choice.currentData()
        row=next((r for r in self.packet['result']['rows'] if r['reference_id']==selected),None)
        if not row:return
        try:resolved=events.resolve_stage_event_reference(self.stage_id,row['token'])
        except (OSError,ValueError,KeyError,TypeError):resolved=None
        if not resolved:
            self._invalidate('所选入口未能重新核对；旧条目已清除，请重新选择。');return
        self.refresh_reference()
        if self.event_choice.currentData()!=selected:return
        self.eventReferenceSelected.emit(deepcopy(resolved['token']))
