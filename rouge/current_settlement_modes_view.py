"""Separate documented experience modes; no account or gameplay inputs."""
import json
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTabWidget, QPlainTextEdit
from . import current_settlement_modes_reference as model
from .ui_state import replace_text


class CurrentSettlementModesPanel(QWidget):
    def __init__(self, stage_id, parent=None, *, load=True):
        super().__init__(parent)
        self.stage_id = stage_id
        self.result = None
        layout = QVBoxLayout(self)
        self.notice = QLabel('基础与满级生命游戏分别列出，仅用于对照。入口与区域需要确认；这里不假定科技已点满，也不把参考值当实际领奖。')
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        bar = QHBoxLayout()
        self.entry = QComboBox()
        self.entry.setAccessibleName('结算分项入口声明')
        self.region = QComboBox()
        self.region.setAccessibleName('结算分项区域声明')
        for value, label in model.ENTRIES:
            self.entry.addItem(label, value)
        for value, label in model.REGIONS:
            self.region.addItem(label, value)
        self.refresh_button = QPushButton('重新核对结算分项')
        bar.addWidget(self.entry)
        bar.addWidget(self.region)
        bar.addWidget(self.refresh_button)
        layout.addLayout(bar)
        self.tabs = QTabWidget()
        self.player = QPlainTextEdit()
        self.technical = QPlainTextEdit()
        for widget, title in ((self.player, '经验、源石锭与条件'), (self.technical, '完整原值与来源')):
            widget.setReadOnly(True)
            self.tabs.addTab(widget, title)
        layout.addWidget(self.tabs, 1)
        self.entry.currentIndexChanged.connect(self.refresh_reference)
        self.region.currentIndexChanged.connect(self.refresh_reference)
        self.refresh_button.clicked.connect(self.refresh_reference)
        if load:
            self.refresh_reference()

    def clear_reference(self):
        self.result = None
        replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False)
        self.tabs.setCurrentIndex(0)

    def refresh_reference(self, *_):
        fresh = model.stage_reference(self.stage_id, self.entry.currentData(), self.region.currentData())
        if fresh is None:
            self.clear_reference()
            return False
        same = self.result is not None and self.result['source_identity'] == fresh['source_identity'] and self.result['stage_id'] == fresh['stage_id']
        self.result = fresh
        replace_text(self.player, model.player_text(fresh), preserve=same)
        replace_text(self.technical, json.dumps(fresh, ensure_ascii=False, indent=2), preserve=same)
        if not same:
            self.tabs.setCurrentIndex(0)
        return True
