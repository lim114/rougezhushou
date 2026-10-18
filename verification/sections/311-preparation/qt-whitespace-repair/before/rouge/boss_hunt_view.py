"""Manual documentary reading for three exact subjects in the fixed ro6_b_4 stage."""
from copy import deepcopy
import json

from PySide6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, QPlainTextEdit, QTabWidget, QVBoxLayout

from . import boss_hunt_reference as model
from .ui_state import replace_text
from .view_catalog import SubjectPicture


PICTURES = (
    ('boss_picture', 'enemy_2145_cadejo', '卡德霍，黑流之源'),
    ('avatar_picture', 'enemy_2146_cadesd', '痛楚化身'),
    ('hound_picture', 'enemy_2137_shsdgo', '猎犬proto'),
)


def target_identity(identity):
    return (type(identity) is tuple and len(identity) == 3
            and type(identity[0]) is str and type(identity[1]) is str
            and type(identity[2]) is int and identity in model.TARGETS)


def _matches_identity(value, identity):
    return (type(value) is dict and type(value.get('stage_id')) is str
            and type(value.get('enemy_id')) is str and type(value.get('level')) is int
            and (value['stage_id'], value['enemy_id'], value['level']) == identity)


def _validated(result, identity):
    if (not target_identity(identity) or not _matches_identity(result, identity)
            or result.get('source_valid') is not True or result.get('status') != 'documented_reference'):
        return False
    reference = result.get('reference')
    source = result.get('source_identity')
    if not _matches_identity(reference, identity) or type(source) is not dict:
        return False
    if type(reference.get('entry_name')) is not str or not reference['entry_name'].strip():
        return False
    for field in ('manifest_sha256', 'data_sha256'):
        digest = source.get(field)
        if (type(digest) is not str or len(digest) != 64
                or any(c not in '0123456789abcdefABCDEF' for c in digest)):
            return False
    topics = reference.get('topics')
    if type(topics) is not list or not topics:
        return False
    ids = set()
    for topic in topics:
        if (type(topic) is not dict or type(topic.get('id')) is not str or not topic['id'].strip()
                or type(topic.get('name')) is not str or not topic['name'].strip() or topic['id'] in ids):
            return False
        ids.add(topic['id'])
    return True


class BossHuntReferencePanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(False)
        self.resize(1060, 780)
        self.identity = self.scope_key = self.result = self._view_key = None
        layout = QVBoxLayout(self)
        self.notice = QLabel()
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        header = QHBoxLayout()
        for attribute, _, _ in PICTURES:
            picture = SubjectPicture()
            setattr(self, attribute, picture)
            header.addWidget(picture)
        layout.addLayout(header)
        layout.addWidget(QLabel('选择要查看的机制说明'))
        self.topic = QComboBox()
        self.topic.setAccessibleName('卡德霍与相关敌人机制说明；总览或手动选择')
        layout.addWidget(self.topic)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)
        self.player = QPlainTextEdit()
        self.player.setReadOnly(True)
        self.technical = QPlainTextEdit()
        self.technical.setReadOnly(True)
        self.tabs.addTab(self.player, '招式、休整与退场条件')
        self.tabs.addTab(self.technical, '技术详情与完整来源')
        self.topic.currentIndexChanged.connect(self._topic_changed)
        self.clear_reference()

    def clear_reference(self, notice='请先选中相关敌人，再手动打开机制资料。'):
        self.identity = self.scope_key = self.result = self._view_key = None
        blocked = self.topic.blockSignals(True)
        self.topic.clear()
        self.topic.setEnabled(False)
        self.topic.blockSignals(blocked)
        for attribute, _, _ in PICTURES:
            getattr(self, attribute).set_subject(None, None, '')
        replace_text(self.player, '', preserve=False)
        replace_text(self.technical, '', preserve=False)
        self.tabs.setCurrentIndex(0)
        self.notice.setText(notice)
        self.setWindowTitle('卡德霍与相关敌人机制资料')

    def _query(self, identity):
        try:
            return model.hunt_reference(*identity)
        except (OSError, ValueError, TypeError, KeyError):
            return None

    @staticmethod
    def _scope(identity, result):
        return identity, json.dumps(result['source_identity'], sort_keys=True, separators=(',', ':'))

    def _render(self, topic_id, *, preserve):
        self._view_key = self.scope_key, topic_id
        replace_text(self.player, model.reference_text(self.result, topic_id=topic_id), preserve=preserve)
        source = {'result': deepcopy(self.result), 'selected_topic_id': topic_id,
                  'selection_is_documentary_not_actual_hunt_state': True}
        replace_text(self.technical, json.dumps(source, ensure_ascii=False, indent=2), preserve=preserve)

    def set_reference(self, identity, result=None):
        if not target_identity(identity):
            self.clear_reference('已更换关卡或敌人，旧机制资料和图片已清除。')
            return False
        if result is None:
            result = self._query(identity)
        if not _validated(result, identity):
            self.clear_reference('机制资料暂时无法核对，旧内容与图片已清除。')
            return False
        scope = self._scope(identity, result)
        keep = self.identity == identity and self.scope_key == scope
        selected = self.topic.currentData() if keep else None
        topics = result['reference']['topics']
        if selected is not None and not any(row['id'] == selected for row in topics):
            self.clear_reference('所选主题与当前资料不一致，旧内容已清除；请重新打开。')
            return False
        if not keep:
            self.clear_reference()
        self.identity = identity
        self.scope_key = scope
        self.result = deepcopy(result)
        blocked = self.topic.blockSignals(True)
        self.topic.clear()
        self.topic.addItem('总览：相关敌人的招式、休整与退场条件', None)
        for row in topics:
            self.topic.addItem(row['name'], row['id'])
        self.topic.setCurrentIndex(self.topic.findData(selected))
        self.topic.setEnabled(True)
        self.topic.blockSignals(blocked)
        self.notice.setText('三张固定原图分别对应卡德霍、痛楚化身与猎犬proto。本说明仅适用“永无安宁”，不表示本局当前状态。')
        self.setWindowTitle(result['reference']['entry_name'] + ' · 招式、休整与退场条件')
        for attribute, enemy_id, name in PICTURES:
            getattr(self, attribute).set_subject('enemy', enemy_id, name + '（固定原图，不代表当前状态）')
        self._render(selected, preserve=keep)
        return True

    def _topic_changed(self, *_):
        identity = self.identity
        if identity is None:
            return False
        selected = self.topic.currentData()
        result = self._query(identity)
        if not _validated(result, identity):
            self.clear_reference('资料暂时无法核对，旧内容与图片已清除。')
            return False
        scope = self._scope(identity, result)
        if scope != self.scope_key:
            self.clear_reference('资料版本已变化，旧选择已清除；请重新手动打开。')
            return False
        if selected is not None and not any(row['id'] == selected for row in result['reference']['topics']):
            self.clear_reference('无法核对所选主题，旧内容已清除。')
            return False
        keep = self._view_key == (scope, selected)
        self.result = deepcopy(result)
        self._render(selected, preserve=keep)
        if not keep:
            self.tabs.setCurrentWidget(self.player)
        return True

    def refresh_reference(self):
        # Losing source validity discards identity; recovery alone cannot refill this window.
        if self.identity is None:
            return False
        result = self._query(self.identity)
        if not _validated(result, self.identity):
            self.clear_reference('机制资料暂时无法核对，旧内容与图片已清除。')
            return False
        if self._scope(self.identity, result) != self.scope_key:
            self.clear_reference('资料版本已变化，旧选择已清除；请重新手动打开。')
            return False
        return self.set_reference(self.identity, result)
