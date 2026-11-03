"""Manual history loading; never restore snapshots into the actual current run."""
from copy import deepcopy
from pathlib import Path
from PySide6.QtCore import Qt,QSize
from PySide6.QtWidgets import QLabel,QPushButton,QWidget,QVBoxLayout,QListWidget,QListWidgetItem
from .player_history_store import RunHistoryStore
from .player_replay import observation_time

def attach_history(panel,body):
    panel.history_store=RunHistoryStore(Path(panel.run.file).parent/'run-history');panel.archives={};panel.history_issues=[]
    panel.archive_page=QWidget();page=QVBoxLayout(panel.archive_page)
    panel.history_status=QLabel('历史只在打开或主动刷新时从本机读取；查看不会重置或恢复本局。');panel.history_status.setWordWrap(True);page.addWidget(panel.history_status)
    panel.session_cards=QListWidget();panel.session_cards.setObjectName('historySessionCards');panel.session_cards.setWordWrap(True);page.addWidget(panel.session_cards,1)
    panel.session_cards.setAccessibleName('本机已保存对局；清单不代表完整结算')
    panel.session_cards.setStyleSheet('#historySessionCards{background:#f5f5f7;border:0;} #historySessionCards::item{background:white;border:1px solid #dedee5;border-radius:13px;margin:5px;padding:12px;} #historySessionCards::item:selected{background:#e9f0f0;border:1px solid #94aba7;}')
    panel.cards_signature=None
    panel.reload_history_button=QPushButton('重新读取本机历史');page.addWidget(panel.reload_history_button)
    panel.sessions.hide()
    panel.history_list_button=QPushButton('查看对局列表');body.insertWidget(1,panel.history_list_button)
    panel.history_list_button.clicked.connect(lambda:panel.tabs.setCurrentWidget(panel.archive_page))
    def open_card(item):
        index=panel.sessions.findData(item.data(Qt.ItemDataRole.UserRole))
        if index>=0:
            panel.sessions.setCurrentIndex(index);panel.tabs.setCurrentWidget(panel.nodes)
            if panel.nodes.rows and panel.nodes.entries.currentItem()is None:
                panel.nodes.floors.setCurrentIndex(max(0,panel.nodes.floors.findData(panel.nodes.rows[-1]['zone_id'])))
                panel.nodes.entries.setCurrentRow(panel.nodes.entries.count()-1)
    panel.session_cards.itemClicked.connect(open_card);panel.session_cards.itemActivated.connect(open_card)
    panel.reload_history_button.clicked.connect(lambda:reload_history(panel));panel.sessions.currentIndexChanged.connect(panel.refresh)
    reload_history(panel,initial=True)
    from .player_personal_statistics import PersonalStatisticsPage
    panel.statistics=PersonalStatisticsPage(panel.history_store);panel.tabs.addTab(panel.statistics,'个人统计')
    panel.statistics.archiveRequested.connect(lambda binding:open_statistics_archive(panel,binding))
    panel.tabs.addTab(panel.archive_page,'对局列表')


def card_text(state,title):
    from .player_statistics_cohorts import cohort,UNREAD
    from .record_flags import active_record
    from .player_replay import history_rows
    group=cohort({'state':state})
    grade='保密等级未读到'if group['difficulty']==UNREAD else'保密等级'+str(group['difficulty'])
    relics=sum(isinstance(r,dict)and active_record(r,'held')for r in state.get('relics',{}).values())
    crew=sum(isinstance(r,dict)and active_record(r,'present')for r in state.get('operators',{}).values())
    return title+' · '+observation_time(state.get('started_at'))+'\n'+group['squad_name']+' · '+grade+'\n'+f'已确认藏品 {relics} 件 · 干员 {crew} 名 · {len(history_rows(state))} 条读取记录'+'\n清单可能不完整；胜负、结算分数与种子尚未确认。'


def refresh_cards(panel):
    rows=[('current',card_text(panel.run.state,'当前对局'))]+panel.archive_card_rows
    signature=tuple(rows)
    if signature==panel.cards_signature:
        for index,(identity,_)in enumerate(rows):
            if identity==panel.sessions.currentData():panel.session_cards.setCurrentRow(index)
        return
    panel.cards_signature=signature;scroll=panel.session_cards.verticalScrollBar().value()
    panel.session_cards.blockSignals(True);panel.session_cards.clear()
    for identity,text in rows:
        item=QListWidgetItem(text);item.setData(Qt.ItemDataRole.UserRole,identity);item.setToolTip(text)
        item.setSizeHint(QSize(0,panel.session_cards.fontMetrics().lineSpacing()*5+28));panel.session_cards.addItem(item)
        if identity==panel.sessions.currentData():panel.session_cards.setCurrentItem(item)
    panel.session_cards.verticalScrollBar().setValue(scroll);panel.session_cards.blockSignals(False)

def open_statistics_archive(panel,binding):
    from .player_statistics_samples import sample_binding
    canonical=sample_binding(binding)
    if canonical is None or canonical!=binding:return False
    reload_history(panel)
    identity='archive:'+binding['id'];record=panel.archives.get(identity)
    if record is None or record.get('state_sha256')!=binding['state_sha256']:
        panel.statistics.notice.setText('所选归档已更新或暂不可用，请重新读取统计后再选；没有用当前局或其它记录替代。');return False
    index=panel.sessions.findData(identity)
    if index<0:return False
    panel.sessions.setCurrentIndex(index);panel.tabs.setCurrentIndex(0);return True

def reload_history(panel,initial=False):
    old=panel.sessions.currentData();panel.archives={};error=None
    try:
        records,panel.history_issues=panel.history_store.records()
        panel.archives={'archive:'+row['state']['id']:row for row in records}
    except(OSError,ValueError,UnicodeError,TypeError,RecursionError)as problem:
        from .player_file_messages import file_issue
        panel.history_issues=[];error=file_issue(problem);panel.history_status.setToolTip(str(problem))
    else:panel.history_status.setToolTip('')
    panel.sessions.blockSignals(True);panel.sessions.clear();panel.sessions.addItem('当前对局 · 最近读取','current')
    for identity,row in panel.archives.items():panel.sessions.addItem('本机历史 · '+observation_time(row['state'].get('started_at')),identity)
    selected=panel.sessions.findData(old)
    if selected<0 and old not in(None,'current'):
        panel.sessions.addItem('此前历史暂不可用 · 请重新选择','unavailable');selected=panel.sessions.count()-1
    panel.sessions.setCurrentIndex(max(0,selected));panel.sessions.blockSignals(False)
    panel.history_status.setText(('本机历史暂时不可用：'+error+'；原件没有改动。')if error else f'读到{len(panel.archives)}局本机历史，另有{len(panel.history_issues)}份记录无法核对。归档不表示通关或完整结算，不上传。')
    panel.archive_card_rows=[(identity,card_text(row['state'],'本机历史'))for identity,row in panel.archives.items()]
    refresh_cards(panel)
    if not initial:
        panel.key=None;panel.refresh()
        if hasattr(panel,'statistics'):panel.statistics.refresh()

def selected_state(panel):
    identity=panel.sessions.currentData()
    if identity=='current':return deepcopy(panel.run.state)
    record=panel.archives.get(identity)
    return deepcopy(record['state'])if record else{'id':None,'history':[]}

def snapshot_notice(panel,count,state):
    identity=panel.sessions.currentData()
    if identity=='current':prefix='当前对局'
    elif identity in panel.archives:prefix='本机历史（不会回写到当前对局）'
    else:return '此前历史暂时不可用，旧内容已清除。请手动选择可读取记录；没有用当前对局冒充历史。'
    return f'{prefix} · 保存了{count}条读取记录。开始时间：'+observation_time(state.get('started_at'))+'。不是完整流程、胜负或结算；未读步骤保持未知。'

