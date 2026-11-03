"""Shop observations from a selected immutable reading snapshot, never live writes."""
from copy import deepcopy
from types import SimpleNamespace
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel
from .player_shop_memory import ShopMemoryPanel

class ShopReplayPage(QWidget):
    def __init__(self,source_panel=None,parent=None):
        super().__init__(parent)
        self.reading=SimpleNamespace(state={'id':None,'history':[]},save_issue=None)
        body=QVBoxLayout(self);self.notice=QLabel('这里只查看所选对局当时已读清单；不会恢复到当前局。未读名称、价格、交易和刷新次数不会补写。')
        self.notice.setWordWrap(True);body.addWidget(self.notice)
        self.panel=ShopMemoryPanel(self.reading,source_panel);body.addWidget(self.panel,1)
        self.panel.notice.hide();self.comparison_toggle=self.panel.comparison_toggle
        self.panel.entries.setMinimumHeight(150);self.panel.detail.setMinimumHeight(90)
        self.signature=None

    def refresh(self,state):
        signature=repr((state.get('id'),state.get('history')))
        if signature!=self.signature:
            self.signature=signature;self.reading.state=deepcopy(state)
        self.panel.refresh()

    def select_observation(self,index):
        target=self.panel.snapshots.findData(index)
        if target<0:return False
        self.panel.search.clear();self.panel.snapshots.setCurrentIndex(target)
        return self.panel.snapshots.currentData()==index
