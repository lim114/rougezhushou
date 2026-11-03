"""Independent read-only upgrade-voucher directory; no operator/run writes."""
from copy import deepcopy
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QLineEdit, QListWidget, QListWidgetItem,
                              QTabWidget, QPlainTextEdit, QPushButton, QSplitter)
from . import current_upgrade_tickets as model
from .ui_state import replace_text


class CurrentUpgradeTicketsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_identity = self.result = self.ticket_id = self.source_dialog = None
        self.recruit_dialog = None
        layout = QVBoxLayout(self)
        notice = QLabel(model.NOTICE); notice.setWordWrap(True); layout.addWidget(notice)
        bar = QHBoxLayout()
        self.profession = QComboBox(); self.profession.addItem('总览：全部职业', None)
        for value, label in model.PROFESSIONS: self.profession.addItem(label, value)
        self.kind = QComboBox(); self.kind.addItem('总览：全部进阶券', None)
        for value, label in model.KINDS: self.kind.addItem(label, value)
        self.star = QComboBox(); self.star.addItem('总览：券种全部星级', None)
        for star in range(1, 7): self.star.addItem(str(star)+'★（仅对照券范围）', star)
        self.profession.setAccessibleName('进阶券适用职业')
        self.kind.setAccessibleName('进阶券种与明确来源')
        self.star.setAccessibleName('进阶券原始星级范围，不是实际可选干员')
        self.search = QLineEdit(); self.search.setPlaceholderText('按券名或对应新典训名称搜索')
        self.refresh_button = QPushButton('重新核对资料')
        for control in (self.profession, self.kind, self.star, self.search, self.refresh_button): bar.addWidget(control)
        layout.addLayout(bar)
        self.count = QLabel(); self.count.setWordWrap(True); layout.addWidget(self.count)
        splitter = QSplitter(); self.entries = QListWidget()
        self.entries.setAccessibleName('18份进阶券原项目录，同名券分别保留')
        splitter.addWidget(self.entries)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for control in (self.player, self.technical): control.setReadOnly(True)
        self.tabs.addTab(self.player, '用途、范围与取得说明')
        self.tabs.addTab(self.technical, '完整原值与来源')
        splitter.addWidget(self.tabs); splitter.setSizes([340, 780]); layout.addWidget(splitter, 1)
        actions = QHBoxLayout()
        self.source_button = QPushButton('查看准确来源原文'); self.source_button.hide()
        self.recruit_button = QPushButton('另查招募券：用途、留存与取出')
        actions.addWidget(self.source_button); actions.addWidget(self.recruit_button); layout.addLayout(actions)
        for combo in (self.profession, self.kind, self.star): combo.currentIndexChanged.connect(self._filter_changed)
        self.search.textChanged.connect(self._filter_changed)
        self.entries.currentItemChanged.connect(self._selected)
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.source_button.clicked.connect(self.open_source)
        self.recruit_button.clicked.connect(self.open_recruit)
        self.refresh_reference()

    def _filters(self):
        return {'profession': self.profession.currentData(), 'kind': self.kind.currentData(),
                'star': self.star.currentData(), 'query': self.search.text()}

    def close_children(self):
        for child in (self.source_dialog, self.recruit_dialog):
            if child is not None: child.close()
        self.source_dialog = self.recruit_dialog = None

    def _unavailable(self):
        self.close_children(); self.source_identity = self.result = self.ticket_id = None
        blocked = self.entries.blockSignals(True)
        try: self.entries.clear()
        finally: self.entries.blockSignals(blocked)
        replace_text(self.player, '', preserve=False); replace_text(self.technical, '', preserve=False)
        self.source_button.hide(); self.source_button.setEnabled(False); self.recruit_button.setEnabled(False)
        self.count.setText(model.UNAVAILABLE)

    def _filter_changed(self, *_): self._populate(preserve=False)

    def _populate(self, *, preserve):
        fresh = model.reference(**self._filters())
        if fresh is None: self._unavailable(); return False
        same = self.source_identity == fresh['source_identity']
        identity = self.ticket_id if same and preserve else None
        if not same: self.close_children()
        self.source_identity = fresh['source_identity']
        blocked = self.entries.blockSignals(True)
        try:
            self.entries.clear()
            for row in fresh['rows']:
                item = QListWidgetItem(row['label']); item.setData(Qt.ItemDataRole.UserRole, row['id'])
                self.entries.addItem(item)
                if row['id'] == identity: self.entries.setCurrentItem(item)
        finally: self.entries.blockSignals(blocked)
        self.count.setText('当前筛选列出'+str(len(fresh['rows']))+'份原记录；同名券按来源保留。不是本局券数或可进阶人数。')
        self.recruit_button.setEnabled(True)
        current = self.entries.currentItem()
        if current is None:
            keep = same and preserve and self.ticket_id is None
            self.ticket_id = None
            if not keep: self.close_children()
            self._show(fresh, preserve=keep)
            if keep: self._refresh_children()
        else: self._selected(current, preserve=same and preserve)
        return True

    def refresh_reference(self): return self._populate(preserve=True)

    def _show(self, fresh, *, preserve):
        self.result = deepcopy(fresh)
        replace_text(self.player, model.player_text(fresh), preserve=preserve)
        replace_text(self.technical, json.dumps(fresh, ensure_ascii=False, indent=2), preserve=preserve)
        link = model.destination(self.ticket_id) if self.ticket_id else None
        self.source_button.setVisible(link is not None); self.source_button.setEnabled(link is not None)
        if link:
            self.source_button.setText('查看'+link['name']+'完整原文' if link['reader'] == 'relic' else '查看安全角落：查看无人机原文')
        if not preserve: self.tabs.setCurrentIndex(0)

    def _refresh_children(self):
        for child in (self.source_dialog, self.recruit_dialog):
            if child is not None and child.isVisible(): child.panel.refresh_reference()

    def _selected(self, item, *_, preserve=False):
        identity = item.data(Qt.ItemDataRole.UserRole) if item else None
        fresh = model.reference(identity, **self._filters())
        if fresh is None or fresh['source_identity'] != self.source_identity: self._unavailable(); return
        keep = preserve and identity == self.ticket_id
        if not keep: self.close_children()
        self.ticket_id = identity; self._show(fresh, preserve=keep)
        if keep: self._refresh_children()

    def _fresh_selection(self):
        if self.result is None: return False
        fresh = model.reference(self.ticket_id, **self._filters())
        if fresh is None or fresh != self.result: self._unavailable(); return False
        return True

    def open_source(self):
        if not self.ticket_id or not self._fresh_selection(): return False
        link = model.destination(self.ticket_id)
        if link is None: return False
        self.close_children()
        if link['reader'] == 'rest':
            from .current_rest_travel_view import CurrentRestTravelDialog
            child = CurrentRestTravelDialog('金色凝滞', link['target'], self)
        elif link['reader'] == 'relic':
            from .expansion_view import ExpansionUpdatePanel
            child = QDialog(self); child.setWindowTitle(link['name']+' · 完整收藏品原文'); child.resize(1050, 790)
            child.panel = ExpansionUpdatePanel(child, categories=('relics',), full_catalog=True)
            QVBoxLayout(child).addWidget(child.panel)
            child.finished.connect(lambda *_: child.panel.close_children())
            for index in range(child.panel.entries.count()):
                item = child.panel.entries.item(index)
                if item.data(Qt.ItemDataRole.UserRole) == link['key']:
                    child.panel.entries.setCurrentItem(item); break
            else:
                child.close(); return False
        else: return False
        self.source_dialog = child
        if child.panel.result is None: self.close_children(); return False
        child.show(); return True

    def open_recruit(self):
        if not self._fresh_selection(): return False
        from .current_recruit_tickets_view import CurrentRecruitTicketsDialog
        self.close_children(); self.recruit_dialog = CurrentRecruitTicketsDialog(self)
        if self.recruit_dialog.panel.result is None: self.close_children(); return False
        self.recruit_dialog.show(); return True

    def closeEvent(self, event):
        self.close_children(); super().closeEvent(event)


class CurrentUpgradeTicketsDialog(QDialog):
    def __init__(self, parent=None, *, target=None):
        super().__init__(parent); self.setWindowTitle('进阶券 · 职业、星级与准确来源'); self.resize(1150, 830)
        self.panel = CurrentUpgradeTicketsPanel(self); QVBoxLayout(self).addWidget(self.panel)
        if target is not None:
            request = target.get('source_request') if isinstance(target, dict) else None
            fresh = model.locate(request.get('category'), request.get('key')) if isinstance(request, dict) else None
            if fresh != target or fresh is None:
                self.panel._unavailable(); return
            item = next((self.panel.entries.item(i) for i in range(self.panel.entries.count())
                         if self.panel.entries.item(i).data(Qt.ItemDataRole.UserRole) == fresh['ticket_id']), None)
            if item is None: self.panel._unavailable()
            else: self.panel.entries.setCurrentItem(item)

    def closeEvent(self, event):
        self.panel.close_children(); super().closeEvent(event)
