"""Manual investment-reference controls; the account and game are never touched."""
import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QSpinBox, QListWidget, QListWidgetItem, QPlainTextEdit,
                               QTabWidget, QPushButton)

from . import current_bank_reference as model
from .ui_state import replace_text


def _reader_tabs():
    tabs = QTabWidget()
    player = QPlainTextEdit()
    technical = QPlainTextEdit()
    for widget, title in ((player, '条件与用途'), (technical, '完整原值与来源')):
        widget.setReadOnly(True)
        tabs.addTab(widget, title)
    return tabs, player, technical


class CurrentBankItemPanel(QWidget):
    def __init__(self, reward_id='bank_reward_4', parent=None):
        super().__init__(parent)
        self.reward_id = reward_id
        self.result = None
        self.image_raw = None
        layout = QVBoxLayout(self)
        self.icon = QLabel()
        self.icon.setFixedSize(96, 96)
        self.icon.setAccessibleName('投资解锁对应收藏品图片')
        self.name = QLabel()
        self.name.setWordWrap(True)
        heading = QHBoxLayout()
        heading.addWidget(self.icon)
        heading.addWidget(self.name, 1)
        layout.addLayout(heading)
        self.tabs, self.player, self.technical = _reader_tabs()
        layout.addWidget(self.tabs, 1)
        self.refresh_reference()

    def clear_reference(self):
        self.result = None
        self.image_raw = None
        self.icon.clear()
        self.name.clear()
        replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False)
        self.tabs.setCurrentIndex(0)

    def refresh_reference(self):
        fresh = model.item_reference(self.reward_id)
        raw = model.icon_bytes() if fresh else None
        if fresh is None or raw is None:
            self.clear_reference()
            return False
        pixmap = QPixmap()
        if not pixmap.loadFromData(raw):
            self.clear_reference()
            return False
        same = self.result is not None and self.result['source_identity'] == fresh['source_identity']
        self.result = fresh
        self.image_raw = raw
        self.name.setText(fresh['item']['name'] + ' · 投资解锁说明，实际获得未知')
        self.icon.setPixmap(pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation))
        replace_text(self.player, model.item_player_text(fresh), preserve=same)
        replace_text(self.technical, json.dumps(fresh, ensure_ascii=False, indent=2), preserve=same)
        return True


class CurrentBankItemDialog(QDialog):
    def __init__(self, reward_id='bank_reward_4', parent=None):
        super().__init__(parent)
        self.setWindowTitle('金酒之杯 · 投资解锁对应资料')
        self.resize(920, 690)
        layout = QVBoxLayout(self)
        self.panel = CurrentBankItemPanel(reward_id, self)
        layout.addWidget(self.panel)


class CurrentBankPanel(QWidget):
    def __init__(self, target=None, parent=None):
        super().__init__(parent)
        self.result = None
        self.item_dialog = None
        layout = QVBoxLayout(self)
        self.notice = QLabel(model.NOTICE)
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        cumulative_row = QHBoxLayout()
        cumulative_row.addWidget(QLabel('仅本页：历史累计投资额'))
        self.cumulative = QSpinBox()
        self.cumulative.setRange(-1, 2147483647)
        self.cumulative.setSpecialValueText('未知')
        self.cumulative.setValue(-1)
        self.cumulative.setSuffix(' 源石锭')
        self.cumulative.setAccessibleName('历史累计投资额（不是余额或本局源石锭）')
        cumulative_row.addWidget(self.cumulative, 1)
        self.refresh_button = QPushButton('重新核对资料')
        cumulative_row.addWidget(self.refresh_button)
        layout.addLayout(cumulative_row)
        self.entries = QListWidget()
        self.entries.setAccessibleName('五档投资奖赏')
        self.entries.setMaximumHeight(155)
        layout.addWidget(self.entries)
        self.peak_row = QWidget()
        peak_layout = QHBoxLayout(self.peak_row)
        peak_layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel('仅对照金酒之杯旧文案：历史最高投资余额')
        label.setWordWrap(True)
        peak_layout.addWidget(label)
        self.peak_balance = QSpinBox()
        self.peak_balance.setRange(-1, 2147483647)
        self.peak_balance.setSpecialValueText('未知')
        self.peak_balance.setValue(-1)
        self.peak_balance.setSuffix(' 源石锭')
        self.peak_balance.setAccessibleName('历史最高投资余额（与累计投资独立）')
        peak_layout.addWidget(self.peak_balance, 1)
        layout.addWidget(self.peak_row)
        self.peak_row.hide()
        self.item_button = QPushButton('查看金酒之杯：效果与原解锁说明')
        self.item_button.hide()
        layout.addWidget(self.item_button)
        self.tabs, self.player, self.technical = _reader_tabs()
        layout.addWidget(self.tabs, 1)
        self.entries.currentItemChanged.connect(self._selected)
        self.cumulative.valueChanged.connect(self.refresh_reference)
        self.peak_balance.valueChanged.connect(self.refresh_reference)
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.item_button.clicked.connect(self.open_item)
        self.refresh_reference()
        if target is not None:
            valid = model.locate('relics', model.ITEM_ID)
            if type(target) is dict and valid is not None and target == valid:
                self.select_reward(target['reward_id'])

    def values(self):
        return {name: None if getattr(self, name).value() < 0 else getattr(self, name).value()
                for name in ('cumulative', 'peak_balance')}

    def selected_id(self):
        item = self.entries.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item is not None else None

    def select_reward(self, reward_id):
        if type(reward_id) is not str or self.result is None:
            return False
        for n in range(self.entries.count()):
            if self.entries.item(n).data(Qt.ItemDataRole.UserRole) == reward_id:
                self.entries.setCurrentRow(n)
                return True
        return False

    def _close_item(self):
        if self.item_dialog is not None:
            self.item_dialog.panel.clear_reference()
            self.item_dialog.close()
        self.item_dialog = None

    def clear_reference(self):
        self._close_item()
        self.result = None
        blocked = self.entries.blockSignals(True)
        try:
            self.entries.clear()
        finally:
            self.entries.blockSignals(blocked)
        self.peak_row.hide()
        self.item_button.hide()
        self.item_button.setEnabled(False)
        self.cumulative.setEnabled(False)
        replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False)
        self.tabs.setCurrentIndex(0)

    def refresh_reference(self, *_):
        fresh = model.reference(**self.values())
        if fresh is None:
            self.clear_reference()
            return False
        same = self.result is not None and self.result['source_identity'] == fresh['source_identity']
        selected = self.selected_id() if same else None
        if not same:
            self._close_item()
        self.result = fresh
        self.cumulative.setEnabled(True)
        blocked = self.entries.blockSignals(True)
        try:
            self.entries.clear()
            for row in fresh['rows']:
                item = QListWidgetItem(str(row['threshold']) + ' 源石锭 · ' + row['original']['desc'])
                item.setData(Qt.ItemDataRole.UserRole, row['id'])
                self.entries.addItem(item)
                if row['id'] == selected:
                    self.entries.setCurrentItem(item)
            if selected is None:
                self.entries.setCurrentRow(-1)
        finally:
            self.entries.blockSignals(blocked)
        self._render(selected, preserve=same)
        if same and self.item_dialog is not None and self.item_dialog.isVisible():
            if not self.item_dialog.panel.refresh_reference():
                self.clear_reference()
                return False
        return True

    def _render(self, reward_id, *, preserve):
        if self.result is None:
            return
        row = next((r for r in self.result['rows'] if r['id'] == reward_id), None)
        if reward_id is not None and row is None:
            self.clear_reference()
            return
        is_item = bool(row and row['item_target'])
        self.peak_row.setVisible(is_item)
        self.item_button.setVisible(is_item)
        self.item_button.setEnabled(is_item)
        replace_text(self.player, model.player_text(self.result, reward_id), preserve=preserve)
        replace_text(self.technical, json.dumps({'selected': row, 'reference': self.result},
                     ensure_ascii=False, indent=2), preserve=preserve)

    def _selected(self, item, *_):
        self._close_item()
        self._render(item.data(Qt.ItemDataRole.UserRole) if item is not None else None, preserve=False)

    def open_item(self):
        reward_id = self.selected_id()
        fresh = model.reference(**self.values())
        if self.result is None or fresh is None or fresh != self.result:
            self.clear_reference()
            return False
        item = model.item_reference(reward_id)
        if item is None or item['source_identity'] != self.result['source_identity']:
            self._close_item()
            return False
        if self.item_dialog is not None and self.item_dialog.isVisible():
            if not self.item_dialog.panel.refresh_reference():
                self.clear_reference()
                return False
            self.item_dialog.raise_()
            return True
        self._close_item()
        dialog = CurrentBankItemDialog(reward_id, self)
        if dialog.panel.result is None or dialog.panel.result['target'] != item['target']:
            dialog.close()
            self.clear_reference()
            return False
        self.item_dialog = dialog
        dialog.show()
        return True

    def closeEvent(self, event):
        self._close_item()
        super().closeEvent(event)


class CurrentBankDialog(QDialog):
    def __init__(self, target=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('前瞻性投资 · 五档解锁与口径说明')
        self.resize(1050, 820)
        layout = QVBoxLayout(self)
        self.panel = CurrentBankPanel(target, self)
        layout.addWidget(self.panel)

    def closeEvent(self, event):
        self.panel._close_item()
        super().closeEvent(event)
