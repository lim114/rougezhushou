"""Read-only run cards: confirmed records are never presented as complete inventory."""
from PySide6.QtWidgets import QWidget,QVBoxLayout,QGridLayout,QLabel,QPushButton,QHBoxLayout
from .record_flags import active_record
from .run_config import difficulty_value
from .player_resource_facts import inventory_summary

def overview_facts(state):
    config=state.get('config',{});grade=difficulty_value(config.get('difficulty'))
    squad=config.get('squad',{});zone=config.get('zone',{})
    crew=sum(active_record(row,'present') for row in state.get('operators',{}).values())
    inventory=inventory_summary(state);relics=inventory['relics']
    total=inventory['expected_relics'];complete=inventory['complete']
    return {'保密等级':str(grade)if grade is not None else'尚未确认',
        '分队':squad.get('name')or'尚未确认','当前区域':zone.get('name')or'尚未确认',
        '已确认干员':f'{crew}名','已读收藏品':f'{relics}件'+(f' / 共{total}件'if total is not None else'')
            +(f"（另已读{inventory['tools']}件道具）"if inventory['tools']else''),
        '收藏品完整性':'已核对完整'if complete else'尚未读全或未核对'}

class RunOverviewPanel(QWidget):
    def __init__(self,run,*,show_map,show_operators,show_items,parent=None):
        super().__init__(parent);self.run=run;body=QVBoxLayout(self)
        title=QLabel('本局概况');title.setStyleSheet('font-size:20px;font-weight:600');body.addWidget(title)
        grid=QGridLayout();self.cards={}
        for i,name in enumerate(overview_facts(run.state)):
            value=QLabel();value.setWordWrap(True);value.setAccessibleName(name)
            grid.addWidget(QLabel(name),i//3*2,i%3);grid.addWidget(value,i//3*2+1,i%3);self.cards[name]=value
        body.addLayout(grid);bar=QHBoxLayout()
        self.map_button=QPushButton('查看地图与节点');self.operators_button=QPushButton('查看干员与技能');self.items_button=QPushButton('查询藏品与零件')
        for button,slot in ((self.map_button,show_map),(self.operators_button,show_operators),(self.items_button,show_items)):
            button.clicked.connect(slot);bar.addWidget(button)
        body.addLayout(bar);self.notice=QLabel('展示同一局最近确认的信息；切换游戏页面不会清空记忆，未知项目不会按0处理。');self.notice.setWordWrap(True);body.addWidget(self.notice)
        self.refresh()
    def refresh(self):
        for name,value in overview_facts(self.run.state).items():self.cards[name].setText(value)
