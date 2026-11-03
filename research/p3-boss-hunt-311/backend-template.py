"""Source-bound normal-stage hunt reading; no live combat or numerical model."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-boss-hunt-311'
DATA = 'rouge/data/boss-hunt-reference.json'
MANIFEST = PACK + '/source-manifest.json'
SELECTED = PACK + '/runtime-selected-authority.json'
TARGETS = (('ro6_b_4', 'enemy_2145_cadejo', 0), ('ro6_b_4', 'enemy_2146_cadesd', 0),
           ('ro6_b_4', 'enemy_2137_shsdgo', 0))
RELATED_ENEMIES = ('enemy_2145_cadejo', 'enemy_2146_cadesd', 'enemy_2137_shsdgo',
                   'enemy_2146_cadesd_2', 'enemy_2146_cadesd_3')
REFERENCE_STAGES = ('ro6_b_4', 'ro6_b_4_b')
DATA_SHA256 = '__DATA_SHA__'
MANIFEST_SHA256 = '__MANIFEST_SHA__'
RUNTIME_FILES = __RUNTIME_FILES__
ACTUAL_FIELDS = ('actual_boss_form', 'actual_avatar_form', 'actual_hounds', 'actual_rest_gate',
                 'actual_skill', 'actual_transition', 'actual_elapsed_time', 'actual_target',
                 'actual_route', 'phase_stats', 'actual_damage')
FALSE_FIELDS = ('current_server_verified', 'numerical_phase_model_added', 'run_state_updated',
                'inventory_updated', 'modifiers_changed', 'maps_changed')
UNAVAILABLE = '围猎与休整资料暂时无法核对；旧说明与条目选择已清除，恢复后请重新选择。'


def _unknown():
    return {**{key: None for key in ACTUAL_FIELDS}, **{key: False for key in FALSE_FIELDS}}


def _same(one, two):
    if type(one) is not type(two):
        return False
    if type(one) is dict:
        return one.keys() == two.keys() and all(type(key) is str and _same(one[key], two[key]) for key in two)
    if type(one) is list:
        return len(one) == len(two) and all(_same(a, b) for a, b in zip(one, two))
    return one == two


def _file(name):
    if type(name) is not str:
        raise ValueError('Public source path required')
    relative = PurePosixPath(name)
    if (relative.is_absolute() or '..' in relative.parts or '\\' in name or ':' in name
            or relative.as_posix() != name):
        raise ValueError('Unsafe public source path')
    path = ROOT.joinpath(*relative.parts)
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Regular public source required')
    for parent in path.parents:
        if parent == ROOT:
            break
        if parent.is_symlink():
            raise ValueError('Linked source parent refused')
    return path


def _packet():
    try:
        raw = _file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw)
        if (manifest['schema'] != 'boss_hunt_source_manifest_v1'
                or manifest['data_file'] != DATA or manifest['data_sha256'] != DATA_SHA256
                or manifest['runtime_full_database_hashing'] is not False
                or manifest['all_runtime_members_required_for_each_target_query'] is not True
                or set(manifest['runtime_files']) != RUNTIME_FILES):
            return None
        blobs = {}
        for name, expected in manifest['runtime_files'].items():
            content = _file(name).read_bytes()
            if (type(expected['bytes']) is not int or len(content) != expected['bytes']
                    or sha256(content).hexdigest() != expected['sha256']):
                return None
            blobs[name] = content
        data, selected = json.loads(blobs[DATA]), json.loads(blobs[SELECTED])
        if (data['schema'] != 'boss_hunt_reference_v1'
                or not _same(data['actual_and_mutation_fields'], _unknown())
                or not _same(data['targets'], [list(target) for target in TARGETS])):
            return None
        from .battle_preview import battle_data
        from .enemy_skills import skill_data
        battle, skills = battle_data(), skill_data()
        if (not _same(battle['source'], selected['complete_battle_source'])
                or not _same(skills['source'], selected['complete_skill_source'])):
            return None
        for stage_id in REFERENCE_STAGES:
            stage = battle['stages'][stage_id]
            if not _same(stage, selected['complete_canonical_stages'][stage_id]):
                return None
            for key, expected in selected['complete_skill_bindings'][stage_id].items():
                if not _same(skills['bindings'][stage_id][key], expected):
                    return None
        for enemy in RELATED_ENEMIES:
            if not _same(skills['definitions'][enemy], selected['complete_skill_definitions'][enemy]):
                return None
        return deepcopy(data)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, StopIteration,
            IndexError, RecursionError, UnicodeError):
        return None


def hunt_reference(stage_id, enemy_id, level):
    if (type(stage_id) is not str or type(enemy_id) is not str or type(level) is not int
            or (stage_id, enemy_id, level) not in TARGETS):
        return None
    data = _packet()
    identity = {'stage_id': stage_id, 'enemy_id': enemy_id, 'level': level}
    if data is None:
        return {'target': True, **identity, 'source_valid': False, 'status': 'source_unavailable',
                'reference': None, 'source_identity': None, **_unknown(), 'notice': UNAVAILABLE}
    ref = deepcopy(data['reference'])
    ref.update(**identity, entry_name=data['entry_names'][enemy_id])
    return {'target': True, **identity, 'source_valid': True, 'status': 'documented_reference',
            'reference': ref,
            'source_identity': {'manifest_sha256': MANIFEST_SHA256, 'data_sha256': DATA_SHA256},
            **_unknown(), 'notice': ref['overview_notice']}


def reference_text(result, topic_id=None):
    if result is None:
        return ''
    if type(result) is not dict or result.get('source_valid') is not True:
        return UNAVAILABLE
    if topic_id is not None and type(topic_id) is not str:
        return '所选资料条目暂时无法核对，请重新选择。'
    # A caller-supplied or stale "source_valid" flag cannot authorize old text.
    current = hunt_reference(result.get('stage_id'), result.get('enemy_id'), result.get('level'))
    if current is None or current['source_valid'] is not True or not _same(result, current):
        return UNAVAILABLE
    ref = current['reference']
    topics = ref['topics']
    if topic_id is not None:
        topics = [topic for topic in topics if topic['id'] == topic_id]
        if not topics:
            return '所选资料条目暂时无法核对，请重新选择。'
    scope = ('这里说明普通版固定关卡的技能与条件。来源记载不同的地方会并列说明；'
             '文献中的时长和数值不代表本局实际倒计时、伤害或状态。')
    lines = [ref['entry_name'] + ' · 围猎与休整资料', ref['overview_notice'], scope]
    for topic in topics:
        lines += ['', '【' + topic['name'] + '】', *topic['paragraphs']]
        for skill in ref['skills']:
            if skill['topic_id'] == topic['id']:
                lines += ['', '【' + skill['name'] + '】', skill['mode_label'], skill['text']]
    lines += ['', '【仍未确认】', *['• ' + text for text in ref['player_unknowns']]]
    text = '\n'.join(lines)
    for original, player in (
            ('原始冷却字段', '资料中的冷却数值'),
            ('实际持续攻击回调', '每次实际造成伤害的时刻'),
            ('普通版原配置', '普通版固定关卡资料'),
            ('完整原值与全部限定', '完整数值与适用条件')):
        text = text.replace(original, player)
    return text
