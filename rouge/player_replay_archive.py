"""Manual history loading; never restore snapshots into the actual current run."""
from copy import deepcopy
from pathlib import Path
from PySide6.QtWidgets import QLabel,QPushButton
from .player_history_store import RunHistoryStore
from .player_replay import observation_time

def attach_history(panel,body):
    panel.history_store=RunHistoryStore(Path(panel.run.file).parent/'run-history');panel.archives={};panel.history_issues=[]
    panel.history_status=QLabel('历史只在打开或主动刷新时从本机读取；查看不会重置或恢复本局。');panel.history_status.setWordWrap(True);body.insertWidget(2,panel.history_status)
    panel.reload_history_button=QPushButton('重新读取本机历史');body.insertWidget(3,panel.reload_history_button)
    panel.reload_history_button.clicked.connect(lambda:reload_history(panel));panel.sessions.currentIndexChanged.connect(panel.refresh)
    reload_history(panel,initial=True)

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
    if not initial:panel.key=None;panel.refresh()

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

