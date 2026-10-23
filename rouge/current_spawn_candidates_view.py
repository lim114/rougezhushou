"""Manual current candidate memberships with exact parent-owned action links."""
from copy import deepcopy
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QPushButton, QPlainTextEdit, QTabWidget)
from . import current_spawn_candidates as model
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class CurrentSpawnCandidatesPanel(QWidget):
    actionSelected = Signal(str)
    actionPositionRequested = Signal(str)
    sourceInvalidated = Signal()

    def __init__(self, stage_id, origin_action_key=None, parent=None):
        super().__init__(parent)
        self.stage_id = stage_id
        self.origin_action_key = origin_action_key
        self.result = None
        self._view_key = None
        layout = QVBoxLayout(self)
        notice = QLabel(model.NOTICE); notice.setWordWrap(True); layout.addWidget(notice)
        bar = QHBoxLayout()
        self.queue_kind = QComboBox()
        for name, key in [('总览（主波次与条件分支）', None), ('主波次', 'main'), ('条件分支', 'branch')]:
            self.queue_kind.addItem(name, key)
        self.relation_kind = QComboBox()
        for key, name in model.KINDS.items():
            self.relation_kind.addItem(name, key)
        self.refresh_button = QPushButton('重新核对候选资料')
        bar.addWidget(self.queue_kind, 1); bar.addWidget(self.relation_kind, 1)
        bar.addWidget(self.refresh_button); layout.addLayout(bar)
        self.relation_combo = QComboBox()
        self.relation_combo.setAccessibleName('本关候选组或关联条目')
        self.member_combo = QComboBox()
        self.member_combo.setAccessibleName('关系中的具体成员记录')
        for control in (self.relation_combo, self.member_combo):
            control.setMinimumContentsLength(12)
            control.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
            layout.addWidget(control)
        self.portrait = QLabel(); self.portrait.setFixedHeight(76)
        self.portrait.setAlignment(Qt.AlignmentFlag.AlignCenter); self.portrait.hide()
        layout.addWidget(self.portrait)
        self.tabs = QTabWidget()
        self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for control, name in ((self.player, '候选和出现条件'), (self.technical, '原始成员与来源')):
            control.setReadOnly(True); self.tabs.addTab(control, name)
        layout.addWidget(self.tabs, 1)
        buttons = QHBoxLayout()
        self.action_button = QPushButton('查看这条出怪或物件记录')
        self.position_button = QPushButton('查看本条已有地图参考')
        buttons.addWidget(self.action_button); buttons.addWidget(self.position_button)
        layout.addLayout(buttons)
        self.queue_kind.currentIndexChanged.connect(self._filter_changed)
        self.relation_kind.currentIndexChanged.connect(self._filter_changed)
        self.relation_combo.currentIndexChanged.connect(self._relation_changed)
        self.member_combo.currentIndexChanged.connect(self.refresh_reference)
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.action_button.clicked.connect(self.follow_action)
        self.position_button.clicked.connect(self.follow_position)
        self.refresh_reference()

    @staticmethod
    def _fill(control, rows, selected, placeholder):
        previous = control.blockSignals(True)
        try:
            control.clear(); control.addItem(placeholder, None)
            for label, key in rows:
                control.addItem(label, key)
            control.setCurrentIndex(max(0, control.findData(selected)))
        finally:
            control.blockSignals(previous)

    def clear_reference(self, *, notify=True):
        had_reference = self.result is not None or self._view_key is not None
        self.result = None; self._view_key = None
        self._fill(self.relation_combo, [], None, '资料无法核对')
        self._fill(self.member_combo, [], None, '请在资料恢复后重新选择')
        self.relation_combo.setEnabled(False); self.member_combo.setEnabled(False)
        self.portrait.clear(); self.portrait.hide()
        self.action_button.setEnabled(False); self.position_button.setEnabled(False)
        replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False)
        self.tabs.setCurrentIndex(0)
        if notify and had_reference:
            self.sourceInvalidated.emit()

    def set_reference(self, stage_id, origin_action_key=None):
        if (stage_id, origin_action_key) != (self.stage_id, self.origin_action_key):
            self.clear_reference()
        self.stage_id = stage_id; self.origin_action_key = origin_action_key
        return self.refresh_reference()

    def _filter_changed(self, *_):
        self._fill(self.relation_combo, [], None, '请选择一份关系资料')
        self._fill(self.member_combo, [], None, '请选择一条成员记录')
        return self.refresh_reference()

    def _relation_changed(self, *_):
        self._fill(self.member_combo, [], None, '请选择一条成员记录')
        return self.refresh_reference()

    def _selected(self):
        if self.result is None:
            return None, None
        rows = self.result['groups'] if self.relation_kind.currentData() == 'group' else self.result['packages']
        relation = next((r for r in rows if r['key'] == self.relation_combo.currentData()), None)
        member = next((m for m in relation['members'] if m['action_key'] == self.member_combo.currentData()), None) if relation else None
        return relation, member

    def _show_portrait(self, member):
        self.portrait.clear(); self.portrait.hide()
        if member is None or member['action_type'] != 'SPAWN':
            return
        rows = member['enemy_candidates']
        if not rows:
            return
        info = rows[0]['portrait']
        if info is None or any(r['portrait'] != info for r in rows):
            return
        raw = model.battle.picture_bytes(info); pixmap = QPixmap()
        self.portrait.show()
        if raw and pixmap.loadFromData(raw, 'PNG'):
            self.portrait.setPixmap(pixmap.scaled(74, 74, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation))
        else:
            self.portrait.setText('该精确引用的图片无法核对；不借用其它敌人图片。')

    def refresh_reference(self, *_):
        fresh = model.stage_reference(self.stage_id, self.origin_action_key)
        if fresh is None:
            self.clear_reference(); return False
        keep = (self.result is not None and self.result['stage_id'] == fresh['stage_id']
                and self.result['origin_action_key'] == fresh['origin_action_key']
                and self.result['source_identity'] == fresh['source_identity'])
        relation_key = self.relation_combo.currentData() if keep else None
        member_key = self.member_combo.currentData() if keep else None
        self.result = fresh
        kind = self.relation_kind.currentData(); queue = self.queue_kind.currentData()
        relations = fresh['groups'] if kind == 'group' else fresh['packages']
        relations = [r for r in relations if queue is None or r['queue']['kind'] == queue]
        self._fill(self.relation_combo, [(r['name'], r['key']) for r in relations], relation_key,
                   '请选择一份关系资料' if relations else '此范围没有这类固定记录')
        relation = next((r for r in relations if r['key'] == self.relation_combo.currentData()), None)
        members = relation['members'] if relation else []
        self._fill(self.member_combo, [(f"成员{i} · {m['type_label']} · {m['name']}", m['action_key'])
                                     for i, m in enumerate(members, 1)], member_key, '请选择一条成员记录')
        self.relation_combo.setEnabled(bool(relations)); self.member_combo.setEnabled(bool(members))
        relation, member = self._selected()
        key = (deepcopy(fresh['source_identity']), kind, queue,
               relation['key'] if relation else None, member['action_key'] if member else None)
        preserve = keep and key == self._view_key
        replace_text(self.player, model.player_text(fresh, relation, member), preserve=preserve)
        technical = {'stage_id': fresh['stage_id'], 'origin_action_key': fresh['origin_action_key'],
                     'source_identity': fresh['source_identity'], 'level_key': fresh['level_key'],
                     'original_level_source': fresh['source'], 'selected_relation': relation,
                     'selected_member': member, 'all_queue_scopes': fresh['scopes'],
                     'counts': {'groups': len(fresh['groups']), 'packages': len(fresh['packages'])},
                     'actual_selection': None, 'probabilities': None,
                     'notes': '组与包分别保留；原键仅在此页查看，引用等级不是普通/精英/领袖档次。'}
        replace_text(self.technical, _technical_json(technical), preserve=preserve)
        self._show_portrait(member)
        self.action_button.setEnabled(member is not None)
        self.position_button.setEnabled(bool(member and member['can_request_position']))
        if not preserve:
            self.tabs.setCurrentIndex(0)
        self._view_key = deepcopy(key)
        return True

    def _resolve_selected(self):
        relation, member = self._selected()
        if relation is None or member is None:
            return None
        resolved = model.resolve_member(self.result, relation['key'], member['action_key'])
        if resolved is None:
            self.clear_reference(); return None
        return resolved

    def follow_action(self):
        resolved = self._resolve_selected()
        if resolved is None:
            return False
        self.actionSelected.emit(resolved['member']['action_key'])
        return True

    def follow_position(self):
        resolved = self._resolve_selected()
        if resolved is None or not resolved['member']['can_request_position']:
            return False
        position = model.position_reference(self.result, resolved['relation']['key'],
                                            resolved['member']['action_key'])
        if position is None:
            self.clear_reference(); return False
        self.actionPositionRequested.emit(resolved['member']['action_key'])
        return True


class CurrentSpawnCandidatesDialog(QDialog):
    def __init__(self, stage_id, origin_action_key=None, parent=None):
        super().__init__(parent); self.setWindowTitle('出怪候选与关联条目')
        self.resize(1040, 780)
        layout = QVBoxLayout(self)
        self.panel = CurrentSpawnCandidatesPanel(stage_id, origin_action_key, self)
        layout.addWidget(self.panel)
