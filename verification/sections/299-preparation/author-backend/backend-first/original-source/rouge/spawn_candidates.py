"""Exact fixed main-queue member reading, never RNG or live game selection."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
from . import battle_preview

ROOT = Path(__file__).resolve().parents[1]
DATA = 'rouge/data/spawn-candidates.json'
MANIFEST = 'research/p3-spawn-candidates-299/source-manifest.json'
MANIFEST_SHA256 = '7cba1db922459fea7eddd86a12ad37998bf93e5616ac63e46aa83fc6b6fab08c'
DATA_SHA256 = 'aaef1b86a73613ce833a4a5fe2ce39abb6241c0dcc2457fcc00a5b51fd61fbd2'
STAGE_IDS = ('ro6_n_1_1', 'ro6_n_1_2', 'ro6_n_1_3', 'ro6_n_1_4', 'ro6_n_2_1', 'ro6_n_2_2', 'ro6_n_2_3', 'ro6_n_2_4', 'ro6_n_2_5', 'ro6_n_3_1', 'ro6_n_3_2', 'ro6_n_3_3', 'ro6_n_3_4', 'ro6_n_3_5', 'ro6_n_3_6', 'ro6_n_4_1', 'ro6_n_4_2', 'ro6_n_4_3', 'ro6_n_4_4', 'ro6_n_4_5', 'ro6_n_4_6', 'ro6_n_4_7', 'ro6_n_5_1', 'ro6_n_5_2', 'ro6_n_5_3', 'ro6_n_5_4', 'ro6_n_5_5', 'ro6_n_5_6', 'ro6_n_5_7', 'ro6_n_6_1', 'ro6_n_6_2', 'ro6_b_2_b', 'ro6_b_6', 'ro6_t_2', 'ro6_t_12', 'ro6_duel_1', 'ro6_duel_2', 'ro6_c_2', 'ro6_e_1_1', 'ro6_e_1_2', 'ro6_e_1_3', 'ro6_e_1_4', 'ro6_e_2_1', 'ro6_e_2_2', 'ro6_e_2_3', 'ro6_e_2_4', 'ro6_e_2_5', 'ro6_e_3_1', 'ro6_e_3_2', 'ro6_e_3_3', 'ro6_e_3_4', 'ro6_e_3_5', 'ro6_e_3_6', 'ro6_e_4_1', 'ro6_e_4_2', 'ro6_e_4_3', 'ro6_e_4_4', 'ro6_e_4_5', 'ro6_e_4_6', 'ro6_e_4_7', 'ro6_e_5_1', 'ro6_e_5_2', 'ro6_e_5_3', 'ro6_e_5_4', 'ro6_e_5_5', 'ro6_e_5_6', 'ro6_e_5_7', 'ro6_e_6_1', 'ro6_e_6_2')
NOTICE = '这里只查阅固定资料中的候选与关联包，不会选择游戏结果。原键相同不证明同时出现、唯一入选或互斥次数；不提供概率，也不把单条数量相加为实际敌人数。'
_CACHE = {}
TOKEN_KEYS = {'kind', 'stage_id', 'scope_key', 'origin_action_id', 'relation_id',
              'relation_kind', 'queue_id', 'relation_key', 'action_id',
              'member_reference_id', 'source_identity'}

def _sha(raw): return sha256(raw).hexdigest()
def _str(value): return type(value) is str and bool(value) and bool(value.strip())
def _same(value, expected):
    if type(value) is not type(expected): return False
    if type(expected) is dict:
        return value.keys() == expected.keys() and all(type(k) is str and _same(value[k], expected[k]) for k in expected)
    if type(expected) is list:
        return len(value) == len(expected) and all(_same(a, b) for a, b in zip(value, expected))
    return value == expected

def _path(name):
    if not _str(name) or Path(name).is_absolute() or '..' in Path(name).parts or '\\' in name: raise ValueError('Unsafe public path')
    path = ROOT / name
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT.resolve()): raise ValueError('Missing fixed public file')
    return path

def _bound(name, pins):
    pin = pins[name]
    raw = _path(name).read_bytes()
    if type(pin) is not dict or type(pin.get('bytes')) is not int or len(raw) != pin['bytes'] or _sha(raw) != pin['sha256']:
        raise ValueError('Fixed public bytes differ')
    return raw

def _packet(stage_id):
    """Fresh file guards per query; full selected legacy stage is also checked."""
    try:
        manifest_raw = _path(MANIFEST).read_bytes()
        if _sha(manifest_raw) != MANIFEST_SHA256: return None
        manifest = json.loads(manifest_raw)
        if (manifest['schema'] != 'spawn_candidates_source_manifest_v1' or manifest['data_file'] != DATA
                or manifest['data_sha256'] != DATA_SHA256 or manifest['runtime_reads_primary_character_table'] is not False): return None
        blobs = {name: _bound(name, manifest['files']) for name in manifest['global_files']}
        level_file = manifest['stage_files'][stage_id]
        level_raw = _bound(level_file, manifest['files'])
        key = (MANIFEST_SHA256, stage_id, _sha(level_raw))
        if key not in _CACHE:
            data = json.loads(blobs[DATA])
            battle = json.loads(blobs['rouge/data/battle-previews.json'])
            if (type(data['schema_version']) is not int or data['schema_version'] != 1
                    or data['reference_kind'] != 'fixed_main_queue_group_and_package_membership'
                    or tuple(data['stages']) != STAGE_IDS
                    or data['counts'] != {'stages': 69, 'original_levels': 38, 'groups': 285, 'packages': 215}
                    or _sha(blobs[DATA]) != DATA_SHA256): return None
            stage = data['stages'][stage_id]
            expected = battle['stages'][stage_id]
            level = json.loads(level_raw)
            if (stage['original_level_file'] != level_file or stage['original_level'] != expected['level_source']
                    or stage['original_level']['sha256'] != _sha(level_raw)
                    or stage['stage_name'] != expected['name'] or stage['difficulty'] != expected['difficulty']): return None
            if (level['mapData']['map'] != expected['map'] or level['mapData']['tiles'] != expected['tiles']
                    or (level.get('routes') or []) != expected['routes']
                    or ((level.get('predefines') or {}).get('tokenInsts') or []) != expected['predefined_objects']): return None
            if len(level['waves']) != len(expected['waves']): return None
            for original_wave, built_wave in zip(level['waves'], expected['waves']):
                if len(original_wave['fragments']) != len(built_wave['fragments']): return None
                for original_fragment, built_fragment in zip(original_wave['fragments'], built_wave['fragments']):
                    if not _same(original_fragment['actions'], [r['action'] for r in built_fragment['actions']]): return None
            _CACHE.clear()
            _CACHE[key] = {'data': data, 'stage': stage, 'battle': battle, 'expected_stage': expected,
                           'manifest': manifest, 'level': level}
        packet = _CACHE[key]
        actual = battle_preview.battle_data()
        if (not _same(actual['source'], packet['battle']['source'])
                or not _same(actual['stages'][stage_id], packet['expected_stage'])): return None
        return packet
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError):
        return None

def _identity(packet):
    return {'manifest_sha256': MANIFEST_SHA256,
            'battle_previews_sha256': packet['manifest']['files']['rouge/data/battle-previews.json']['sha256'],
            'data_sha256': DATA_SHA256,
            'level_sha256': packet['stage']['original_level']['sha256']}

def _scope(packet):
    raw = json.dumps([packet['stage']['stage_id'], _identity(packet)], sort_keys=True, separators=(',', ':')).encode()
    return 'spawn-candidates:' + _sha(raw)

def _actions(packet):
    for wave in packet['expected_stage']['waves']:
        for fragment in wave['fragments']:
            wi, fi = wave['index'], fragment['index']
            for ordinal, action in enumerate(fragment['actions']):
                yield {'action_id': action['id'], 'queue_id': f'w{wi}.f{fi}', 'wave': wi, 'fragment': fi,
                       'raw_action': action['action'],
                       'source_selector': f'$.waves[{wi-1}].fragments[{fi-1}].actions[{ordinal}]'}

def _relations(packet, origin):
    rows = packet['stage']['groups'] + packet['stage']['packages']
    return rows if origin is None else [r for r in rows if any(m['action_id'] == origin for m in r['members'])]

def _token(packet, origin, relation, member):
    return {'kind': 'fixed_spawn_candidate_member', 'stage_id': packet['stage']['stage_id'],
            'scope_key': _scope(packet), 'origin_action_id': origin,
            'relation_id': relation['reference_id'], 'relation_kind': relation['kind'],
            'queue_id': relation['queue_id'],
            'relation_key': relation['group_key'] if relation['kind'] == 'group' else relation['package_key'],
            'action_id': member['action_id'], 'member_reference_id': member['reference_id'],
            'source_identity': _identity(packet)}

def _decorate(packet, origin, relation):
    result = deepcopy(relation)
    for member in result['members']:
        member['token'] = _token(packet, origin, relation, member)
    return result

def _unavailable(stage_id):
    return {'status': 'source_unavailable', 'source_valid': False, 'stage_id': stage_id,
            'stage_name': None, 'scope_key': None, 'origin_action_id': None, 'selected_action': None,
            'groups': [], 'packages': [], 'source_identity': None, 'source': None, 'source_file': None,
            'notice': '固定候选资料来源未通过核对，旧成员、位置和敌人入口已停用；不借用其他关卡或分支。',
            'actual_selection': None, 'probabilities': None}

def _reference(packet, origin):
    selected = next((a for a in _actions(packet) if a['action_id'] == origin), None) if origin is not None else None
    if origin is not None and selected is None: return None
    rows = _relations(packet, origin)
    return {'status': 'documented_reference', 'source_valid': True,
            'stage_id': packet['stage']['stage_id'], 'stage_name': packet['stage']['stage_name'],
            'scope_key': _scope(packet), 'origin_action_id': origin, 'selected_action': deepcopy(selected),
            'groups': [_decorate(packet, origin, r) for r in rows if r['kind'] == 'group'],
            'packages': [_decorate(packet, origin, r) for r in rows if r['kind'] == 'package'],
            'source_identity': _identity(packet), 'source': deepcopy(packet['stage']['original_level']),
            'source_file': packet['stage']['original_level_file'], 'notice': NOTICE,
            'actual_selection': None, 'probabilities': None}

def stage_reference(stage_id):
    """Complete fixed groups/packages for one admitted stage; no selection."""
    if not _str(stage_id) or stage_id not in STAGE_IDS: return None
    packet = _packet(stage_id)
    return _unavailable(stage_id) if packet is None else _reference(packet, None)

def action_reference(stage_id, action_id):
    """A full main action identity, never a branch or a similarly named group."""
    if not _str(stage_id) or stage_id not in STAGE_IDS or not _str(action_id) or action_id.startswith('branch:'): return None
    packet = _packet(stage_id)
    return _unavailable(stage_id) if packet is None else _reference(packet, action_id)

def member_token(stage_id, origin_action_id, member_action_id, relation_id):
    """Only identities may be supplied; values/levels/coordinates are not inputs."""
    if (not _str(stage_id) or stage_id not in STAGE_IDS
            or origin_action_id is not None and not _str(origin_action_id)
            or not _str(member_action_id) or not _str(relation_id)): return None
    packet = _packet(stage_id)
    if packet is None: return None
    if origin_action_id is not None and not any(a['action_id'] == origin_action_id for a in _actions(packet)): return None
    relation = next((r for r in _relations(packet, origin_action_id) if r['reference_id'] == relation_id), None)
    if relation is None: return None
    member = next((m for m in relation['members'] if m['action_id'] == member_action_id), None)
    return None if member is None else deepcopy(_token(packet, origin_action_id, relation, member))

def resolve_reference(token):
    """Fresh source/stage/relation/origin checks precede any parent reading link."""
    if type(token) is not dict or token.keys() != TOKEN_KEYS: return None
    sid, origin = token.get('stage_id'), token.get('origin_action_id')
    if not _str(sid) or sid not in STAGE_IDS or origin is not None and not _str(origin): return None
    packet = _packet(sid)
    if packet is None: return None
    if origin is not None and not any(a['action_id'] == origin for a in _actions(packet)): return None
    relation = next((r for r in _relations(packet, origin) if r['reference_id'] == token.get('relation_id')), None)
    if relation is None: return None
    member = next((m for m in relation['members'] if m['action_id'] == token.get('action_id')), None)
    if member is None or not _same(token, _token(packet, origin, relation, member)): return None
    result_member = deepcopy(member); result_member['token'] = deepcopy(token)
    return {'stage_id': sid, 'scope_key': _scope(packet), 'origin_action_id': origin,
            'relation': {k: deepcopy(v) for k, v in relation.items() if k != 'members'},
            'member': result_member, 'token': deepcopy(token), 'source_identity': _identity(packet),
            'source': deepcopy(packet['stage']['original_level']), 'source_file': packet['stage']['original_level_file'],
            'actual_selection': None}
