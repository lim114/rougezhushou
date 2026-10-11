"""Account-labelled manual technology references, separate from every run.

These records do not prove game identity, active buffs or prerequisite logic.
Loading never creates a file. Only explicit user actions request a save.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid

from .manual_scenario import parse_preview_object
from .technology import technology_node, technology_nodes

STATUS_LABELS = {'unknown': '未知', 'unlocked': '已解锁', 'locked': '未解锁'}


def _name(value):
    if not isinstance(value, str):
        raise ValueError('资料档案名称需要文字。')
    name = value.strip()
    if not 1 <= len(name) <= 60 or any(ord(c) < 32 or 0xd800 <= ord(c) <= 0xdfff for c in name):
        raise ValueError('资料档案名称需要1–60个可显示字符。')
    return name


def _timestamp(value):
    if not isinstance(value, str):
        return False
    try:
        stamp = datetime.fromisoformat(value)
        if stamp.utcoffset() is None:
            return False
        stamp.astimezone(timezone(timedelta(hours=8)))
        return True
    except (ValueError, OverflowError):
        return False


class TechnologyState:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else None
        self.known_ids = frozenset(node['buffId'] for node in technology_nodes())
        self._state = {'schema_version': 1, 'topic_id': 'rogue_6', 'selected_profile': 'default',
                       'profiles': {'default': {'name': '默认资料档案', 'nodes': {}}}}
        self._expected_hash = None
        self.preserve_original = False
        self.issue = None
        if self.path is None:
            return
        try:
            if self.path.is_symlink():
                raise ValueError('linked technology state')
            raw = self.path.read_bytes()
            decoded = parse_preview_object(raw.decode('utf-8'), '科技资料')
            self._validate(decoded)
        except FileNotFoundError:
            try:
                self.path.lstat()
            except FileNotFoundError:
                return
            except OSError:
                pass
            self._protect('原科技资料未能读取，已保留原路径。')
            return
        except (OSError, ValueError):
            self._protect('原科技资料不可用，已保留原文件。')
            return
        self._state = decoded
        self._expected_hash = hashlib.sha256(raw).hexdigest()

    def _validate(self, state):
        if type(state.get('schema_version')) is not int or state['schema_version'] != 1 or state.get('topic_id') != 'rogue_6':
            raise ValueError('unsupported technology schema or topic')
        profiles = state.get('profiles')
        selected = state.get('selected_profile')
        if not isinstance(profiles, dict) or not profiles or not isinstance(selected, str) or selected not in profiles:
            raise ValueError('invalid technology profiles')
        names = set()
        for identity, profile in profiles.items():
            if not identity or not isinstance(profile, dict) or not isinstance(profile.get('nodes'), dict):
                raise ValueError('invalid technology profile')
            name = _name(profile.get('name'))
            if name != profile['name'] or name in names:
                raise ValueError('ambiguous technology profile name')
            names.add(name)
            for node_id, record in profile['nodes'].items():
                if node_id not in self.known_ids:
                    continue  # Future identities are opaque and survive saves.
                if (not isinstance(record, dict) or type(record.get('status')) is not str or
                        record['status'] not in STATUS_LABELS or record.get('source') != 'manual' or
                        not _timestamp(record.get('updated_at'))):
                    raise ValueError('invalid manual technology record')

    def _protect(self, issue):
        self.preserve_original = True
        self.issue = issue

    @property
    def selected_profile(self):
        return self._state['selected_profile']

    @property
    def profile_name(self):
        return self._state['profiles'][self.selected_profile]['name']

    def profiles(self):
        return [{'id': key, 'name': profile['name']} for key, profile in self._state['profiles'].items()]

    def snapshot(self):
        return deepcopy(self._state)

    def view(self, node_id):
        technology_node(node_id)
        record = self._state['profiles'][self.selected_profile]['nodes'].get(node_id, {})
        return {'node_id': node_id, 'status': record.get('status', 'unknown'),
                'source': record.get('source'), 'updated_at': record.get('updated_at'),
                'actual_activation': None, 'game_account_identity_verified': False}

    def counts(self):
        counts = dict.fromkeys(STATUS_LABELS, 0)
        records = self._state['profiles'][self.selected_profile]['nodes']
        for node_id in self.known_ids:
            counts[records.get(node_id, {}).get('status', 'unknown')] += 1
        return counts

    def create_profile(self, name):
        name = _name(name)
        if any(profile['name'] == name for profile in self._state['profiles'].values()):
            raise ValueError('已有同名资料档案，请使用另一个名称。')
        identity = uuid.uuid4().hex
        self._state['profiles'][identity] = {'name': name, 'nodes': {}}
        self._state['selected_profile'] = identity
        self.save()
        return identity

    def select_profile(self, identity):
        if not isinstance(identity, str) or identity not in self._state['profiles']:
            raise ValueError('没有找到该科技资料档案。')
        if identity == self.selected_profile:
            return True
        self._state['selected_profile'] = identity
        return self.save()

    def set_status(self, node_id, status):
        technology_node(node_id)
        if type(status) is not str or status not in STATUS_LABELS:
            raise ValueError('科技状态需要为未知、已解锁或未解锁。')
        nodes = self._state['profiles'][self.selected_profile]['nodes']
        nodes[node_id] = {**nodes.get(node_id, {}), 'status': status,
                         'source': 'manual', 'updated_at': datetime.now(timezone.utc).isoformat()}
        return self.save()

    def persistence_notice(self):
        if self.issue:
            return self.issue + ' 新的手动记录仅在当前运行有效，本次不会覆盖原资料。'
        if self.path is None:
            return '当前为临时资料窗口，关闭后不保留手动记录。'
        return ''

    def describe(self, node_id):
        record = self.view(node_id)
        label = STATUS_LABELS[record['status']]
        lines = ['资料档案：' + self.profile_name,
                 '本档案手动记录：' + label + ('（用户记录）' if record['source'] == 'manual' else '（尚未记录）')]
        if record['updated_at']:
            stamp = datetime.fromisoformat(record['updated_at']).astimezone(timezone(timedelta(hours=8)))
            lines.append('记录时间：' + stamp.strftime('%Y-%m-%d %H:%M:%S') + '（北京时间）')
        lines.append('游戏账户自动读取尚未接入；当前实际启用与数值效果仍未知。')
        return '\n'.join(lines)

    def save(self):
        if self.preserve_original:
            return False
        if self.path is None:
            return True
        temporary = None
        try:
            self._validate(self._state)
            if self.path.is_symlink():
                raise ValueError('linked technology state')
            try:
                current = hashlib.sha256(self.path.read_bytes()).hexdigest()
            except FileNotFoundError:
                try:
                    self.path.lstat()
                except FileNotFoundError:
                    current = None
                else:
                    raise ValueError('unreadable existing technology path')
            if current != self._expected_hash:
                self._protect('科技资料已被其他窗口或程序修改，原文件已保留。')
                return False
            payload = (json.dumps(self._state, ensure_ascii=True, indent=2, allow_nan=False) + '\n').encode('utf-8')
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=self.path.parent, prefix='technology-', suffix='.tmp', delete=False) as output:
                temporary = Path(output.name)
                output.write(payload); output.flush(); os.fsync(output.fileno())
            os.replace(temporary, self.path)
            self._expected_hash = hashlib.sha256(payload).hexdigest()
            return True
        except (OSError, ValueError):
            self._protect('科技资料保存未完成。')
            return False
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass
