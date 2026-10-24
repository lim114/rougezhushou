"""Player-facing reverse lookup with exact stage/enemy navigation."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QComboBox, QListWidget, QListWidgetItem,
                              QPlainTextEdit, QTabWidget, QPushButton, QSplitter)
from . import current_enemy_stage_index as model
from . import current_stage_directory as directory
from . import current_battle_reference as battle
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class CurrentEnemyStageIndexPanel(QWidget):
    def __init__(self, parent=None, *, stage_id=None, enemy_key=None):
        super().__init__(parent)
        self.reference = None; self.result = None; self.battle_dialog = None
        self.source_identity = None; self.selected_key = None
        layout = QVBoxLayout(self)
        notice = QLabel(model.NOTICE); notice.setWordWrap(True); layout.addWidget(notice)
        bar = QHBoxLayout(); self.search = QLineEdit(); self.search.setPlaceholderText('输入敌人中文名，例如：鸭爵、空植体、坎诺特')
        self.search.setAccessibleName('按敌人中文名搜索'); bar.addWidget(self.search, 1)
        self.tier = QComboBox(); self.tier.setAccessibleName('敌人类别分支')
        for value, name in model.TIERS: self.tier.addItem(name, value)
        bar.addWidget(self.tier)
        self.refresh_button = QPushButton('重新核对资料'); bar.addWidget(self.refresh_button); layout.addLayout(bar)
        bar = QHBoxLayout(); self.floor = QComboBox(); self.floor.setAccessibleName('关联关卡层数')
        for value, name in directory.FLOORS: self.floor.addItem(name, value)
        self.kind = QComboBox(); self.kind.setAccessibleName('关联关卡来源')
        for value, name in directory.KINDS: self.kind.addItem(name, value)
        self.scope = QComboBox(); self.scope.setAccessibleName('关联记录范围')
        for value, name in model.SCOPES: self.scope.addItem(name, value)
        for widget in (self.floor, self.kind, self.scope): bar.addWidget(widget)
        layout.addLayout(bar); self.count = QLabel(); self.count.setWordWrap(True); layout.addWidget(self.count)
        split = QSplitter(); layout.addWidget(split, 1)
        self.entries = QListWidget(); self.entries.setAccessibleName('敌人对应的精确关卡记录'); split.addWidget(self.entries)
        right = QWidget(); body = QVBoxLayout(right); split.addWidget(right); split.setSizes([490, 620])
        self.portrait = QLabel(); self.portrait.setMinimumHeight(90); self.portrait.setAlignment(Qt.AlignmentFlag.AlignCenter); body.addWidget(self.portrait)
        self.open_button = QPushButton('打开对应关卡并定位这条敌人资料'); body.addWidget(self.open_button)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.player.setReadOnly(True)
        self.technical = QPlainTextEdit(); self.technical.setReadOnly(True)
        self.tabs.addTab(self.player, '关联关卡与适用范围'); self.tabs.addTab(self.technical, '完整原值与来源'); body.addWidget(self.tabs, 1)
        self.search.textChanged.connect(self._filter_changed)
        for widget in (self.tier, self.floor, self.kind, self.scope): widget.currentIndexChanged.connect(self._filter_changed)
        self.entries.currentItemChanged.connect(self._selected)
        self.refresh_button.clicked.connect(self.refresh_reference); self.open_button.clicked.connect(self.open_battle)
        self.refresh_reference()
        if stage_id is not None or enemy_key is not None: self.select_target(stage_id, enemy_key)

    def _clear_battle(self, child):
        for name in ('position_dialog', 'action_position_dialog'):
            mapped = getattr(child.panel, name, None)
            if mapped is not None: mapped.panel.clear_reference()
        child.panel._clear()

    def _battle_finished(self, child):
        self._clear_battle(child)
        if self.battle_dialog is child: self.battle_dialog = None

    def close_owned(self):
        if self.battle_dialog is not None:
            child = self.battle_dialog; self.battle_dialog = None
            self._clear_battle(child); child.close()

    def _clear_detail(self, text=None):
        self.close_owned(); self.result = None; self.selected_key = None; self.open_button.setEnabled(False)
        blocked = self.entries.blockSignals(True); self.entries.setCurrentRow(-1); self.entries.blockSignals(blocked)
        self.portrait.clear(); replace_text(self.player, text or model.player_text(None), preserve=False)
        replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0)

    def _unavailable(self):
        self.reference = None; self.source_identity = None
        blocked = self.entries.blockSignals(True); self.entries.clear(); self.entries.blockSignals(blocked)
        self._clear_detail(model.UNAVAILABLE); self.count.setText(model.UNAVAILABLE)

    def clear_reference(self):
        self._unavailable()

    def _owned_battle_matches(self, child):
        result = child.panel.result
        if type(result) is not dict or self.reference is None or self.result is None: return False
        try:
            row, stage = self.result['row'], self.result['stage']
            # packet() fixes the composite identity order: manifest, battle, directory, version.
            return (child.panel.stage_id == row['stage_id'] and result['id'] == row['stage_id']
                    and result['source_identity'] == self.reference['source_identity'][1]
                    and result['level_key'] == stage['level_key']
                    and model.digest(result['level']) == stage['original_level_sha256']
                    and model.digest(result['stage']) == stage['original_stage_sha256'])
        except (KeyError, TypeError, ValueError, IndexError):
            return False

    def _filter_changed(self, *_):
        self._populate(preserve=False)

    def _populate(self, *, preserve):
        if self.reference is None:
            self._unavailable(); return False
        selected = self.selected_key if preserve else None
        visible = model.rows(self.search.text(), self.tier.currentData(), self.scope.currentData(),
                             self.floor.currentData(), self.kind.currentData(), reference=self.reference)
        blocked = self.entries.blockSignals(True); self.entries.clear()
        for row in visible:
            item = QListWidgetItem(model.label(row, self.reference))
            key = (row['stage_id'], row['enemy_key']); item.setData(Qt.ItemDataRole.UserRole, key)
            self.entries.addItem(item)
            if key == selected: self.entries.setCurrentItem(item)
        self.entries.blockSignals(blocked)
        unique_stages = len({r['stage_id'] for r in visible})
        self.count.setText(f'找到 {len(visible)} 条资料记录，涉及 {unique_stages} 份关卡配置。包含同名变体；不是实际出场数量，也不保证本局会出现。')
        if self.entries.currentItem() is None:
            self.entries.setCurrentRow(-1); self._clear_detail()
        else:
            self._selected(self.entries.currentItem(), preserve=preserve)
        return True

    def refresh_reference(self):
        fresh = model.packet()
        if fresh is None:
            self._unavailable(); return False
        keep = self.source_identity == fresh['source_identity'] and self.reference is not None
        if not keep: self._clear_detail()
        self.reference = fresh; self.source_identity = fresh['source_identity']
        self._populate(preserve=keep)
        if keep and self.battle_dialog is not None:
            if not self.battle_dialog.panel.refresh_reference(): self.close_owned()
            elif not self._owned_battle_matches(self.battle_dialog): self.close_owned()
        return True

    def select_target(self, stage_id, enemy_key):
        if self.reference is None:
            self._unavailable(); return False
        row = model.locate(stage_id, enemy_key, reference=self.reference)
        if row is None:
            self._clear_detail('指定的敌人与关卡记录无法核对，请重新选择；不会继续打开之前的目标。'); return False
        for widget in (self.search, self.tier, self.scope, self.floor, self.kind): widget.blockSignals(True)
        self.search.setText(row['name'])
        for widget in (self.tier, self.scope, self.floor, self.kind): widget.setCurrentIndex(widget.findData(None))
        for widget in (self.search, self.tier, self.scope, self.floor, self.kind): widget.blockSignals(False)
        self._populate(preserve=False)
        for i in range(self.entries.count()):
            item = self.entries.item(i)
            if tuple(item.data(Qt.ItemDataRole.UserRole)) == (stage_id, enemy_key):
                self.entries.setCurrentItem(item); return True
        self._clear_detail('指定记录未出现在当前列表，请重新选择。'); return False

    def _selected(self, item, *_, preserve=False):
        value = item.data(Qt.ItemDataRole.UserRole) if item else None
        key = tuple(value) if type(value) in (tuple, list) and len(value) == 2 and all(type(part) is str for part in value) else None
        info = model.detail(*key, reference=self.reference) if key is not None else None
        if info is None:
            self._clear_detail(); return
        keep = preserve and self.selected_key == key
        if not keep: self.close_owned()
        self.selected_key = key; self.result = info; self.open_button.setEnabled(True)
        replace_text(self.player, model.player_text(info), preserve=keep)
        replace_text(self.technical, _technical_json(info), preserve=keep)
        self.portrait.clear(); pix = QPixmap(); raw = battle.picture_bytes(info['row']['portrait'])
        if raw and pix.loadFromData(raw, 'PNG'):
            self.portrait.setPixmap(pix.scaled(92, 92, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else: self.portrait.setText('此精确引用未取得可核对的图片。')
        if not keep: self.tabs.setCurrentIndex(0)

    def open_battle(self):
        target = model.exact_target(self.result)
        if target is None or self.selected_key != (target['stage_id'], target['enemy_key']):
            self._unavailable(); return False
        self.close_owned()
        from .current_battle_view import CurrentBattleDialog
        child = CurrentBattleDialog(target['stage_id'], self); self.battle_dialog = child
        child.finished.connect(lambda _result: self._battle_finished(child))
        if child.panel.result != target['battle'] or not child.panel.enemy_choices.select_value(target['enemy_key'], emit=True):
            self._unavailable(); return False
        selected = next((e for e in child.panel.result['enemies'] if e['key'] == child.panel.enemy_combo.currentData()), None)
        if (selected is None or child.panel.enemy_key != target['enemy_key']
                or child.panel.enemy_combo.currentData() != target['enemy_key']
                or model.digest(selected['raw_binding']) != target['binding_sha256']):
            self._unavailable(); return False
        child.panel.tabs.setCurrentIndex(1); child.show(); return True

    def closeEvent(self, event):
        self.clear_reference(); super().closeEvent(event)


class CurrentEnemyStageIndexDialog(QDialog):
    def __init__(self, parent=None, *, stage_id=None, enemy_key=None):
        super().__init__(parent); self.setWindowTitle('按敌人查找关卡'); self.resize(1180, 850)
        layout = QVBoxLayout(self); self.panel = CurrentEnemyStageIndexPanel(self, stage_id=stage_id, enemy_key=enemy_key); layout.addWidget(self.panel)

    def done(self, result):
        self.panel.clear_reference(); super().done(result)

    def closeEvent(self, event):
        self.panel.clear_reference(); super().closeEvent(event)
