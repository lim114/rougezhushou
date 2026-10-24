"""Manual form/document reading and an exact fixed-terrain child window."""
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QTabWidget, QPlainTextEdit)
from . import current_sun_boss as model
from .branch_choice import BranchChoice
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class CurrentSunBossPanel(QWidget):
    def __init__(self, stage_id, enemy_key=None, parent=None):
        super().__init__(parent)
        self.stage_id = stage_id; self.entry_key = enemy_key; self.result = None
        self.selected_key = None; self._view_key = None; self._initial = True; self.map_dialog = None
        layout = QVBoxLayout(self)
        self.notice = QLabel(model.NOTICE); self.notice.setWordWrap(True); layout.addWidget(self.notice)
        self.refresh_button = QPushButton('重新核对本关形态资料'); layout.addWidget(self.refresh_button)
        self.form_combo = QComboBox(); self.form_combo.setAccessibleName('同一首领的准确形态资料')
        self.forms = BranchChoice(self.form_combo, [], overview_label='总览（同一首领的资料）',
                                  placeholder='请选择形态资料；不代表本局当前形态')
        layout.addWidget(self.forms)
        self.portrait = QLabel(); self.portrait.setFixedHeight(70); self.portrait.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.portrait)
        bar = QHBoxLayout(); self.topic = QComboBox(); self.topic.setAccessibleName('形态机制阅读分支')
        for key, label in model.TOPICS: self.topic.addItem(label, key)
        self.related = QComboBox(); self.related.setAccessibleName('同一首领的其它准确形态资料')
        self.related_button = QPushButton('切换查阅的形态资料')
        bar.addWidget(self.topic, 1); bar.addWidget(self.related, 1); bar.addWidget(self.related_button); layout.addLayout(bar)
        self.card = QComboBox(); self.card.setAccessibleName('当前形态完整原招式与天赋'); layout.addWidget(self.card)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for area, label in ((self.player, '机制、条件与限制'), (self.technical, '完整原文与准确来源')):
            area.setReadOnly(True); self.tabs.addTab(area, label)
        layout.addWidget(self.tabs, 1)
        self.map_button = QPushButton('查看本关固定地形（不预测二阶段）'); layout.addWidget(self.map_button)
        self.status = QLabel(); self.status.setWordWrap(True); layout.addWidget(self.status)
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.form_combo.currentIndexChanged.connect(self._form_changed)
        self.topic.currentIndexChanged.connect(self._render)
        self.card.currentIndexChanged.connect(self._render)
        self.related_button.clicked.connect(self.follow_form)
        self.map_button.clicked.connect(self.open_map)
        self.refresh_reference()

    def _close_map(self):
        if self.map_dialog is not None:
            self.map_dialog.panel.clear_reference(); self.map_dialog.close()
        self.map_dialog = None

    def _map_finished(self, child):
        child.panel.clear_reference()
        if self.map_dialog is child: self.map_dialog = None

    def clear_reference(self):
        self._close_map(); self.result = None; self.selected_key = None; self._view_key = None
        self.entry_key = None; self._initial = False; self.forms.set_groups([], emit=False)
        for control in (self.card, self.related):
            block = control.blockSignals(True); control.clear(); control.blockSignals(block)
        block = self.topic.blockSignals(True); self.topic.setCurrentIndex(0); self.topic.blockSignals(block)
        self.topic.setEnabled(False); self.related.setEnabled(False)
        self.card.hide(); self.map_button.hide(); self.related_button.setEnabled(False)
        self.portrait.clear(); self.portrait.hide(); self.status.clear()
        replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0)

    def refresh_reference(self, *_):
        fresh = model.reference(self.stage_id, self.entry_key)
        if fresh is None: self.clear_reference(); return False
        keep = self.result is not None and self.result['source_identity'] == fresh['source_identity']
        key = self.form_combo.currentData() if keep else None
        if self._initial: key = self.entry_key; self._initial = False
        self.result = fresh
        self.topic.setEnabled(True); self.related.setEnabled(True)
        groups = []
        for kind, label in (('normal', '起始形态资料'), ('other', '转变形态资料（不是新增敌人）')):
            entries = []
            for row in fresh['rows']:
                if (row['form'] == 'normal') != (kind == 'normal'): continue
                icon = QIcon(); picture = QPixmap(); raw = model.battle.picture_bytes(row['enemy']['portrait'])
                if raw and picture.loadFromData(raw, 'PNG'): icon = QIcon(picture)
                entries.append((row['enemy']['name'], row['key'], icon))
            groups.append((label, entries))
        block = self.form_combo.blockSignals(True); self.forms.set_groups(groups, emit=False)
        if key is not None: self.forms.select_value(key, emit=False)
        else: self.form_combo.setCurrentIndex(0)
        self.form_combo.blockSignals(block); self._form_changed(preserve=keep)
        if self.map_dialog is not None:
            mapped = model.map_reference(fresh)
            if mapped is None: self._close_map(); self.status.setText('固定地图来源无法核对，旧地图窗口已关闭；机制文献仍可阅读。')
            elif not self.map_dialog.panel.refresh_reference(): self._close_map()
            elif self.map_dialog.panel.result != mapped['map']:
                self._close_map(); self.status.setText('地图重新读取的资料与本关不一致，旧地图已清除；机制文献仍可阅读。')
        return True

    def _form_changed(self, *_, preserve=False):
        key = self.form_combo.currentData(); keep = preserve and key == self.selected_key
        old_card = self.card.currentData() if keep else None
        old_related = self.related.currentData() if keep else None
        if key != self.selected_key:
            self._close_map(); block = self.topic.blockSignals(True); self.topic.setCurrentIndex(0); self.topic.blockSignals(block)
        self.selected_key = key
        for control in (self.card, self.related): control.blockSignals(True); control.clear()
        self.card.addItem('选择本形态的招式或天赋原项', None)
        for item in model.cards(self.result, key): self.card.addItem(item['title'], item['index'])
        self.card.setCurrentIndex(max(0, self.card.findData(old_card)))
        self.related.addItem('选择同一首领的其它形态资料', None)
        for request in model.related_forms(self.result, key): self.related.addItem(request['name'], request)
        self.related.setCurrentIndex(max(0, self.related.findData(old_related)))
        for control in (self.card, self.related): control.blockSignals(False)
        self.related_button.setEnabled(key is not None and self.related.count() > 1)
        row = model.entity(self.result, key); self.portrait.clear(); self.portrait.setVisible(row is not None)
        if row:
            picture = QPixmap(); raw = model.battle.picture_bytes(row['enemy']['portrait'])
            if raw and picture.loadFromData(raw, 'PNG'):
                self.portrait.setPixmap(picture.scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else: self.portrait.setText('这份准确形态资料没有可核对的图片，不替换为同名图。')
        self.status.clear(); self._render()

    def _render(self, *_):
        topic = self.topic.currentData(); index = self.card.currentData()
        self.card.setVisible(topic == 'skills' and self.selected_key is not None)
        self.map_button.setVisible(topic in ('terrain', 'altar') and self.selected_key is not None)
        self.map_button.setEnabled(self.result is not None)
        identity = (self.result['source_identity'], self.selected_key, topic, index) if self.result else None
        keep = identity == self._view_key
        replace_text(self.player, model.player_text(self.result, self.selected_key, topic, index), preserve=keep)
        row = model.entity(self.result, self.selected_key)
        technical = {'stage_id': self.stage_id, 'source_identity': self.result['source_identity'],
            'selected_current_reference': row,
            'complete_selected_document_card': model.card(self.result, self.selected_key, index),
            'complete_form_document': self.result['materials']['forms'].get(row['form']) if row else None,
            'declared_appearances': self.result['declared_appearances'],
            'linked_original_ids_without_independent_current_records': self.result['data']['missing_linked_ids'],
            'actual_form': None, 'actual_phase': None, 'actual_terrain': None,
            'actual_altar_cells': None, 'numeric_model_added': False} if self.result else {}
        replace_text(self.technical, _technical_json(technical), preserve=keep)
        if not keep: self.tabs.setCurrentIndex(0)
        self._view_key = identity

    def follow_form(self):
        target = model.resolve_form(self.result, self.selected_key, self.related.currentData())
        if target is None:
            self.clear_reference(); self.status.setText('形态入口无法重新核对，旧内容已清除；恢复后请手动选择。'); return False
        return self.forms.select_value(target['enemy_key'])

    def open_map(self):
        mapped = model.map_reference(self.result)
        self._close_map()
        if mapped is None:
            self.status.setText('这份准确固定地图暂时无法核对，旧地图已关闭；不借用同名熄日。'); return False
        from .current_map_position_view import CurrentMapPositionDialog
        child = CurrentMapPositionDialog(mapped['stage_id'], self)
        if child.panel.result is None or child.panel.result != mapped['map']:
            child.panel.clear_reference(); child.close(); return False
        child.finished.connect(lambda _result: self._map_finished(child))
        self.map_dialog = child; self.status.clear(); child.show(); return True

    def closeEvent(self, event):
        self.clear_reference(); super().closeEvent(event)


class CurrentSunBossDialog(QDialog):
    def __init__(self, stage_id, enemy_key=None, parent=None):
        super().__init__(parent); self.setWindowTitle('沉沦之人 · 形态、信仰与地形条件'); self.resize(1100, 850)
        layout = QVBoxLayout(self); self.panel = CurrentSunBossPanel(stage_id, enemy_key, self); layout.addWidget(self.panel)

    def done(self, result):
        self.panel.clear_reference(); super().done(result)

    def closeEvent(self, event):
        self.panel.clear_reference(); super().closeEvent(event)
