"""A small always-on-top companion with assistant-only navigation."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QGridLayout,QLabel,QPushButton,QCheckBox
from .player_overview import overview_facts
from .player_context import recent_content
class CompactAssistant(QDialog):
    def __init__(self,owner):
        super().__init__(owner);self.owner=owner;self.setWindowTitle('黑流树海助手');self.setWindowFlag(Qt.WindowType.Tool,True)
        self.resize(440,530);body=QVBoxLayout(self)
        top=QGridLayout();self.pin=QCheckBox('保持置顶');self.pin.setChecked(True);self.pin.toggled.connect(self.set_pinned);top.addWidget(self.pin,0,0)
        self.expand=QPushButton('展开助手');self.expand.clicked.connect(self.open_full);top.addWidget(self.expand,0,1);body.addLayout(top)
        self.context=QLabel();self.context.setWordWrap(True);self.context.setStyleSheet('font-size:16px;font-weight:600');body.addWidget(self.context)
        grid=QGridLayout();self.cards={}
        for i,name in enumerate(overview_facts(owner.run.state)):
            label=QLabel(name);value=QLabel();value.setWordWrap(True);self.cards[name]=value
            grid.addWidget(label,i//2*2,i%2);grid.addWidget(value,i//2*2+1,i%2)
        body.addLayout(grid);actions=QGridLayout();self.buttons={}
        for i,(name,callback)in enumerate([
            ('地图与节点',lambda:self.open_full(owner.exploration_map_tab)),
            ('本局藏品',lambda:self.open_full(owner.inventory_panel)),
            ('干员与技能',self.open_operators),
            ('场景笔记',owner.open_scene_notes),
            ('节点统计',owner.open_public_statistics),
            ('聊天分析',self.open_chat)]):
            button=QPushButton(name);button.clicked.connect(callback);actions.addWidget(button,i//2,i%2);self.buttons[name]=button
        body.addLayout(actions);self.notice=QLabel('只显示本局最近确认的信息。节点与统计供查阅，不代替你选择路线。');self.notice.setWordWrap(True);body.addWidget(self.notice);body.addStretch(1)
        self.set_pinned(True);self.refresh()
    def set_pinned(self,value):
        visible=self.isVisible();self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,value)
        if visible:self.show()
    def refresh(self):
        title=recent_content(self.owner.run.state);self.context.setText('最近读取：'+title if title else'本局信息 · 等待读取节点详情')
        for key,value in overview_facts(self.owner.run.state).items():self.cards[key].setText(value)
        self.buttons['场景笔记'].setEnabled(bool(title))
    def open_full(self,page=None):
        # clicked(bool) is not a navigation target.
        if page is not None and not isinstance(page,bool):self.owner.centralWidget().setCurrentWidget(page)
        self.owner.show();self.owner.raise_();self.owner.activateWindow()
    def open_operators(self):
        ws=self.owner.centralWidget();ws.groups['干员计算'].setCurrentIndex(0);self.open_full(ws.groups['干员计算'])
    def open_chat(self):self.open_full(self.owner.centralWidget().groups['聊天'])
    def closeEvent(self,event):
        if not self.owner.closing:self.open_full()
        event.accept()
