"""Manual exchange reference reading; no inventory or game actions."""
from copy import deepcopy
import json
from PySide6.QtWidgets import (QComboBox,QDialog,QHBoxLayout,QLabel,QLineEdit,
    QPlainTextEdit,QTabWidget,QVBoxLayout,QWidget)
from . import relic_exchange_flow as model
from .player_node_information import _plain
from .ui_state import replace_text

EVENT='community_group_025'
ROLES={'display_option_reference':'选择参考','explanatory_text':'资料说明',
       'community_navigation_guide':'文献导航'}
STATES={True:'相符',False:'不符',None:'尚未确认'}


def player_text(value):
    return _plain(value).replace('251项可供出旗标为真、21项为假','其中251件记为可交出、21件记为不可交出').replace('原表可供出旗标只用于交换出去','这项记录只说明能否交出去')


def flow_label(row):
    scene=int(row['scene_key'].rsplit(':',1)[1])+1
    choice=int(row['choice_key'].rsplit(':',1)[1])+1
    return f'场景{scene} · {ROLES.get(row["presentation_role"],"资料条目")}{choice}：'+_plain(row['choice_title'])


def flow_text(row,packet):
    lines=['【交换流程资料】',*[player_text(t)for t in packet['flow_notices']]]
    if row is None:
        return '\n'.join(lines+['','请选择一条流程资料，查看对应条件、后续或退出结果。',
            '下拉列表中的“资料说明”和“文献导航”不是已核实的游戏按钮。'])
    lines+=['','【当前条目】',flow_label(row),'','【原文结果】',_plain(row['choice_description'])or'未另列结果。']
    if row.get('condition_text'):lines+=['','【条件或附注】',_plain(row['condition_text'])]
    for rule in row['documented_rules']:
        lines+=['','【'+_plain(rule['title'])+'】',_plain(rule['text'])]
    destinations=row.get('documented_destinations',[])
    if destinations:
        lines+=['','【PRTS流程导航记载的后续】']
        for destination in destinations:
            lines.append(_plain(destination['description']))
        lines.append('以上是资料页面的导航关系，不能证明本局实际进入了该后续。')
    if row.get('documented_result_text'):
        lines+=['','【文献补充的后续结果】',_plain(row['documented_result_text']),
                '这是文献流程的结果说明；相同的原场景记录仍有多个候选，未据编号认定实际入口。']
        if destinations and any(d['description']!=row['documented_result_text']for d in destinations):
            lines+=['','【两份资料的后续不一致】',
                    '上面保留了两种记载。目前不能确定游戏实际会出现哪一种后续；不将任一记载当作确定结果。']
    lines+=['','【本局仍待确认】','实际是否可选、已交换几次、交出或领取了什么，均未确认；这里不会扣除物品或修改本局。']
    return '\n'.join(lines)


def offer_text(result):
    item=result['item']
    allowed=result['can_offer_reference']
    state='允许作为提供物'if allowed else'不能作为提供物'
    lines=['【能否交出去】',item['name']+'：这份固定资料中'+state+'。',
           '此结论只用于提供物，不说明能否作为交换奖励得到。',
           '范围：固定本体272件资料；后续新增内容和本局实际可选情况不在此结论内。',
           '', '【本次查阅情形】',f'准备查看第{result["exchange_index"]}次交换。']
    for check in result['checks']:
        lines.append(STATES[check['matches']]+'：'+_plain(check.get('title')or check['text']))
        lines.append(player_text(check['text']))
    lines+=['','【收藏品作用】',_plain(item.get('usage'))or'资料未列。',
            '','【物品说明】',_plain(item.get('description'))or'资料未列。',
            '','【结果不能提前确定】',
            '本局持有、实际是否可选、实际消耗与奖励尚未确认；这里不会预扣物品。',
            '完整奖励池、奖励档次与数量仍未核实，不从提供物的稀有度推算奖励。']
    return '\n'.join(lines)


def same(left,right):
    return json.dumps(left,sort_keys=True,allow_nan=False)==json.dumps(right,sort_keys=True,allow_nan=False)


class RelicExchangeFlowPanel(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('回滚文明 · 收藏品交换与完整流程')
        self.setModal(False);self.resize(1080,850)
        self.event_id=self.scope_key=self.packet=None
        self._source_scope=self._flow_key=self._offer_key=None
        layout=QVBoxLayout(self)
        self.notice=QLabel('只读固定本体资料；查阅或声明不代表游戏中已选择、已持有或已交换。')
        self.notice.setWordWrap(True);layout.addWidget(self.notice)
        self.tabs=QTabWidget();layout.addWidget(self.tabs,1)
        flow=QWidget();fl=QVBoxLayout(flow)
        self.flow=QComboBox();self.flow.setAccessibleName('回滚文明完整流程资料')
        self.flow.setPlaceholderText('请选择流程资料；说明与导航不等于游戏按钮')
        fl.addWidget(self.flow)
        self.flow_reader=QPlainTextEdit();self.flow_reader.setReadOnly(True);fl.addWidget(self.flow_reader,1)
        self.tabs.addTab(flow,'交换流程与退出结果')
        offer=QWidget();ol=QVBoxLayout(offer)
        row=QHBoxLayout();self.search=QLineEdit();self.search.setPlaceholderText('按收藏品名称搜索')
        self.membership=QComboBox()
        for label,value in [('全部固定收藏品',None),('资料允许提供',True),('资料不能提供',False)]:self.membership.addItem(label,value)
        row.addWidget(self.search,2);row.addWidget(self.membership);ol.addLayout(row)
        self.catalogue_count=QLabel();self.catalogue_count.setWordWrap(True);ol.addWidget(self.catalogue_count)
        self.relic=QComboBox();self.relic.setAccessibleName('要查阅的交换提供物')
        self.relic.setPlaceholderText('请选择收藏品；不代表本局实际持有');ol.addWidget(self.relic)
        row=QHBoxLayout()
        self.exchange_index=QComboBox();self.exchange_index.addItem('第1次交换',1);self.exchange_index.addItem('第2次交换',2)
        self.owned=self.declaration('本次持有',('未确认持有','声明已持有','声明未持有'))
        self.palm=self.declaration('手掌',('手掌未确认','声明手掌已解锁','声明手掌未解锁'))
        self.first_type=QComboBox()
        for label,value in [('首次交换类型未确认',None),('首次为收藏品','RELIC'),('首次为零件','SCRAP')]:self.first_type.addItem(label,value)
        self.first_type.setAccessibleName('首次交换类型声明')
        for widget in(self.exchange_index,self.owned,self.palm,self.first_type):row.addWidget(widget)
        ol.addLayout(row)
        self.offer_reader=QPlainTextEdit();self.offer_reader.setReadOnly(True);ol.addWidget(self.offer_reader,1)
        self.tabs.addTab(offer,'收藏品能否提供')
        self.source_reader=QPlainTextEdit();self.source_reader.setReadOnly(True);self.tabs.addTab(self.source_reader,'资料与依据')
        self.flow.currentIndexChanged.connect(self.render)
        self.relic.currentIndexChanged.connect(self.render)
        for control in(self.exchange_index,self.owned,self.palm,self.first_type):control.currentIndexChanged.connect(self.render)
        self.search.textChanged.connect(self.refresh_reference)
        self.membership.currentIndexChanged.connect(self.refresh_reference)
        self.refresh_reference()

    @staticmethod
    def declaration(name,labels):
        combo=QComboBox();combo.setAccessibleName(name+'声明')
        for label,value in zip(labels,(None,True,False)):combo.addItem(label,value)
        return combo

    def _clear(self,message):
        self.packet=None;self._source_scope=self._flow_key=self._offer_key=None
        for control in(self.flow,self.relic):
            control.blockSignals(True);control.clear();control.setCurrentIndex(-1);control.blockSignals(False)
        self.catalogue_count.setText('资料暂不可用；不能把缺少资料当作没有物品。')
        for reader in(self.flow_reader,self.offer_reader,self.source_reader):replace_text(reader,message,preserve=False)

    def set_reference(self,event_id,*,scope_key=None):
        if (event_id,scope_key)!=(self.event_id,self.scope_key):
            self._clear('资料范围已切换，请重新选择。')
            controls=(self.search,self.membership,self.exchange_index,self.owned,self.palm,self.first_type)
            for control in controls:control.blockSignals(True)
            try:
                self.search.clear()
                for control in controls[1:]:control.setCurrentIndex(0)
                self.tabs.setCurrentIndex(0)
            finally:
                for control in controls:control.blockSignals(False)
        self.event_id,self.scope_key=event_id,deepcopy(scope_key)
        self.refresh_reference()

    def _repopulate(self,control,rows,selected,label,key):
        control.blockSignals(True)
        try:
            control.clear()
            for row in rows:control.addItem(label(row),row[key])
            control.setCurrentIndex(control.findData(selected)if type(selected)is str else-1)
        finally:control.blockSignals(False)

    def refresh_reference(self,*_):
        selected_flow,selected_relic=self.flow.currentData(),self.relic.currentData()
        try:
            packet=model.event_reference(self.event_id)
            if not packet or packet.get('source_valid')is not True or packet.get('status')!='documented_reference':raise ValueError('Source unavailable')
            if self._source_scope is not None and self._source_scope!=packet['scope_key']:
                selected_flow=selected_relic=None;self._flow_key=self._offer_key=None
            rows=packet['choices'];items=packet['catalogue']
            if len(rows)!=19 or len(items)!=272 or len({x['reference_id']for x in rows})!=19:raise ValueError('Incomplete source identity')
            if any(r['event_id']!=EVENT or r['reference_id']!=r['choice_key']for r in rows):raise ValueError('Foreign choice')
            self._repopulate(self.flow,rows,selected_flow,flow_label,'reference_id')
            needle=self.search.text().strip().casefold();flag=self.membership.currentData()
            filtered=[r for r in items if needle in r['name'].casefold()and(flag is None or r['canSacrifice']is flag)]
            labels=packet['rarity_labels']
            self._repopulate(self.relic,filtered,selected_relic,lambda r:r['name']+' · '+labels[r['rarity']],'item_id')
            self.catalogue_count.setText(f'固定本体资料272件：允许提供251件，不能提供21件。当前筛选显示{len(filtered)}件；后续新增内容不计入这里。')
            self.packet=packet;self._source_scope=packet['scope_key']
            self.render()
        except(OSError,ValueError,TypeError,KeyError):self._clear('交换资料未能重新核对；旧物品、流程和结果已清除，恢复后请手动重新选择。')

    def render(self,*_):
        second=self.exchange_index.currentData()==2
        self.palm.setVisible(second);self.first_type.setVisible(second)
        if self.packet is None:return
        try:
            # A manual selection also rechecks sources before using cached rows.
            current=model.event_reference(self.event_id)
            if not current or not current.get('source_valid')or not same(current,self.packet):raise ValueError('Source changed')
            chosen=self.flow.currentData();row=next((r for r in current['choices']if r['reference_id']==chosen),None)
            details=model.choice_details(EVENT,row['scene_key'],row['choice_key'])if row else None
            if details and(not details.get('source_valid')or not same(details.get('reference'),row)):raise ValueError('Choice changed')
            offered=self.relic.currentData()
            result=model.relic_offer_reference(offered,exchange_index=self.exchange_index.currentData(),
                first_exchange_item_type=self.first_type.currentData()if second else None,
                palm_unlocked=self.palm.currentData()if second else None,owned=self.owned.currentData())if offered else None
            if result and(result.get('source_valid')is not True or result.get('item_id')!=offered):raise ValueError('Item changed')
            flow_key=(self.event_id,self.scope_key,current['scope_key'],chosen)
            offer_key=(self.event_id,self.scope_key,current['scope_key'],offered,self.exchange_index.currentData(),
                       self.owned.currentData(),self.palm.currentData()if second else None,self.first_type.currentData()if second else None)
            replace_text(self.flow_reader,flow_text(row,current),preserve=flow_key==self._flow_key)
            replace_text(self.offer_reader,offer_text(result)if result else'请选择要查阅的收藏品；这里不会自动读取或改写本局持有。',preserve=offer_key==self._offer_key)
            source={'source_identity':current['source_identity'],'source':current['source'],
                    'catalogue_scope':current['catalogue_scope'],'selected_flow':details,'selected_offering':result}
            replace_text(self.source_reader,json.dumps(source,ensure_ascii=False,indent=2,allow_nan=False),preserve=(flow_key,offer_key)==(self._flow_key,self._offer_key))
            self._flow_key,self._offer_key=flow_key,offer_key
        except(OSError,ValueError,TypeError,KeyError):self._clear('所选物品或流程资料未能重新核对；旧说明已清除，恢复后请手动重新选择。')
