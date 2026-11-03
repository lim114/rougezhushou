"""Private, local-only snapshots created solely before a user's manual new run."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import math
import os
import tempfile
import time
from .player_history_codec import bytes_for,encode,decode

SCHEMA = 'player-run-history-v1'

def canonical_state(state):
    if not isinstance(state, dict) or not isinstance(state.get('id'), str) or not state['id']:
        raise ValueError('对局身份缺失，未归档或重置。')
    for field in ('operators', 'relics', 'maps', 'resources', 'config'):
        if not isinstance(state.get(field, {}), dict):
            raise ValueError('对局记录格式不完整，未归档或重置。')
    if not isinstance(state.get('history', []), list):
        raise ValueError('对局读取记录格式不完整。')
    return bytes_for(state)

def regular_path(path):
    path = Path(path)
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError('本机历史位置为链接，未自动读取或覆盖。')
    return path

def observed_state(state):
    return bool(state.get('history') or state.get('last_read') is not None or
                any(state.get(field) for field in ('operators', 'relics', 'maps', 'resources')))

class RunHistoryStore:
    def __init__(self, folder):
        self.folder = Path(folder)

    def archive(self, state):
        snapshot = deepcopy(state)
        raw = canonical_state(snapshot)
        if not observed_state(snapshot):
            return None
        state_hash = sha256(raw).hexdigest()
        identity_hash = sha256(bytes_for(snapshot['id'])).hexdigest()
        destination = self.folder / (identity_hash + '-' + state_hash + '.json')
        regular_path(destination)
        if destination.exists():
            existing = self.read(destination)
            if existing['state_sha256'] != state_hash:
                raise ValueError('已有历史记录与名称不符，未覆盖或重置。')
            return destination
        self.folder.mkdir(parents=True, exist_ok=True)
        record = {'schema': SCHEMA, 'created_at': time.time(),
                  'reason': 'manual_new_run', 'outcome': None,
                  'state_sha256': state_hash, 'state_encoding':'typed-json-v1', 'state_payload':encode(snapshot)}
        content = (json.dumps(record, ensure_ascii=True, indent=2, allow_nan=False) + '\n').encode('ascii')
        descriptor, name = tempfile.mkstemp(prefix='.run-history-', dir=self.folder)
        try:
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            regular_path(destination)
            # Atomic publication of complete bytes; never replace older history.
            os.link(name, destination)
        finally:
            Path(name).unlink(missing_ok=True)
        return destination

    def read(self, path):
        path = regular_path(path)
        if path.parent.resolve() != self.folder.resolve():
            raise ValueError('所选记录不在本机历史目录中。')
        record = json.loads(path.read_text('utf8'))
        if not isinstance(record, dict) or record.get('schema') != SCHEMA:
            raise ValueError('历史记录格式无法核对，原件未改动。')
        if record.get('state_encoding')!='typed-json-v1':raise ValueError('历史内容编码无法核对。')
        state=decode(record.get('state_payload'))
        raw = canonical_state(state)
        digest = sha256(raw).hexdigest()
        identity = sha256(bytes_for(state['id'])).hexdigest()
        if record.get('state_sha256') != digest or path.name != identity + '-' + digest + '.json':
            raise ValueError('历史内容或身份核对失败，未安装到本局。')
        created = record.get('created_at')
        try:
            valid_time = type(created) in (int, float) and math.isfinite(created)
        except OverflowError:
            valid_time = False
        if not valid_time:
            raise ValueError('历史归档时间无法核对。')
        if record.get('reason') != 'manual_new_run' or record.get('outcome') is not None:
            raise ValueError('历史范围无法核对，不将归档视为已通关。')
        return {**{key:value for key,value in record.items()if key!='state_payload'},'state':state}

    def records(self):
        regular_path(self.folder)
        if not self.folder.exists():
            return [], []
        if not self.folder.is_dir():
            raise ValueError('本机历史目录不可用，原件未改动。')
        records = {}
        issues = []
        for path in sorted(self.folder.glob('*.json')):
            try:
                record = self.read(path)
            except (OSError, ValueError, UnicodeError, TypeError, RecursionError) as error:
                issues.append({'file': path.name, 'message': str(error)})
                continue
            key = record['state']['id']
            prior = records.get(key)
            if prior is None or record['created_at'] > prior['created_at']:
                records[key] = {**record, 'path': path}
        return sorted(records.values(), key=lambda row: row['created_at'], reverse=True), issues

def archive_before_manual_reset(run, folder):
    """Snapshot only. The caller alone decides whether to invoke existing reset."""
    # A failed persistence session may not start another IO attempt. Preserve
    # the original explicit-reset and retained-original behavior unchanged.
    if getattr(run,'save_issue',None)or getattr(run,'preserve_unreadable',False):return None
    return RunHistoryStore(folder).archive(run.state)
