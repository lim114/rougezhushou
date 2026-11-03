"""Plain Chinese current base-reward references with explicit entrance context."""
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QPushButton,QTabWidget,QPlainTextEdit
from . import current_settlement_reference as model
from .boss_hunt_view import _technical_json
from .ui_state import replace_text

class CurrentSettlementPanel(QWidget):
    def __init__(self,stage_id,parent=None):
        super().__init__(parent);self.stage_id=stage_id;self.result=None;layout=QVBoxLayout(self)
        notice=QLabel('这里只核对通关基础分项。入口和区域是用于对照的声明，不是自动读取或实际领奖；完整奖励仍未知。');notice.setWordWrap(True);layout.addWidget(notice)
        bar=QHBoxLayout();self.entry=QComboBox();self.entry.setAccessibleName('基础奖励的实际入口声明');self.region=QComboBox();self.region.setAccessibleName('基础奖励的区域声明')
        for value,label in model.ENTRIES:self.entry.addItem(label,value)
        for value,label in model.REGIONS:self.region.addItem(label,value)
        self.refresh_button=QPushButton('重新核对基础奖励');bar.addWidget(self.entry);bar.addWidget(self.region);bar.addWidget(self.refresh_button);layout.addLayout(bar)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.player.setReadOnly(True);self.technical=QPlainTextEdit();self.technical.setReadOnly(True);self.tabs.addTab(self.player,'基础分项与条件');self.tabs.addTab(self.technical,'完整来源');layout.addWidget(self.tabs,1)
        self.entry.currentIndexChanged.connect(self.refresh_reference);self.region.currentIndexChanged.connect(self.refresh_reference);self.refresh_button.clicked.connect(self.refresh_reference);self.refresh_reference()
    def clear_reference(self):
        self.result=None;replace_text(self.player,model.UNAVAILABLE,preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)
    def refresh_reference(self,*_):
        fresh=model.stage_reference(self.stage_id,self.entry.currentData(),self.region.currentData())
        if fresh is None:self.clear_reference();return False
        keep=self.result is not None and self.result['source_identity']==fresh['source_identity']and self.result['stage_id']==fresh['stage_id'];self.result=fresh
        replace_text(self.player,model.player_text(fresh),preserve=keep);replace_text(self.technical,_technical_json(fresh),preserve=keep)
        if not keep:self.tabs.setCurrentIndex(0)
        return True
