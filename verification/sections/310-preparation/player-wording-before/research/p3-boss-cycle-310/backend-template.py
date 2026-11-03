"""Fixed two-actor documentary cycle reading, without combat-state prediction."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-boss-cycle-310'
DATA = 'rouge/data/boss-cycle-reference.json'
MANIFEST = PACK + '/source-manifest.json'
SELECTED = PACK + '/selected-original-records.json'
TARGETS = (('ro6_b_5', 'enemy_2147_shophm', 0), ('ro6_b_5', 'enemy_2148_shorbb', 0))
RELATED_ENEMIES = ('enemy_2147_shophm', 'enemy_2148_shorbb', 'enemy_2149_shorsm')
DATA_SHA256 = '__DATA_SHA__'
MANIFEST_SHA256 = '__MANIFEST_SHA__'
RUNTIME_FILES = __RUNTIME_FILES__
ACTUAL_FIELDS = ('actual_lorentz_mode', 'actual_cube_mode', 'actual_modules',
                 'actual_half_hp_gate', 'actual_skill', 'actual_transition',
                 'actual_elapsed_time', 'actual_target', 'actual_route', 'phase_stats', 'actual_damage')


def _unknown():
    return {**{key: None for key in ACTUAL_FIELDS}, 'current_server_verified': False,
            'numerical_phase_model_added': False, 'run_state_updated': False,
            'inventory_updated': False, 'modifiers_changed': False, 'maps_changed': False}


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
        if (manifest['schema'] != 'boss_cycle_source_manifest_v1'
                or manifest['data_file'] != DATA or manifest['data_sha256'] != DATA_SHA256
                or manifest['runtime_full_database_hashing'] is not False
                or manifest['all_runtime_members_required_for_each_target_query'] is not True
                or set(manifest['runtime_files']) != RUNTIME_FILES):
            return None
        blobs = {}
        for name, pin in manifest['runtime_files'].items():
            content = _file(name).read_bytes()
            if (type(pin['bytes']) is not int or len(content) != pin['bytes']
                    or sha256(content).hexdigest() != pin['sha256']):
                return None
            blobs[name] = content
        data, selected = json.loads(blobs[DATA]), json.loads(blobs[SELECTED])
        if (data['schema'] != 'boss_cycle_reference_v1'
                or not _same(data['actual_and_mutation_fields'], _unknown())
                or not _same(data['targets'], [list(target) for target in TARGETS])):
            return None
        from .battle_preview import battle_data
        from .enemy_skills import skill_data
        battle, skills = battle_data(), skill_data()
        stage = battle['stages']['ro6_b_5']
        if (not _same(battle['source'], data['complete_battle_source'])
                or not _same(stage, selected['complete_canonical_stage'])
                or not _same(skills['source'], data['complete_skill_source'])):
            return None
        for enemy in RELATED_ENEMIES:
            current = [row for row in stage['enemies'] if row['id'] == enemy
                       and type(row['level']) is int and row['level'] == 0]
            if (len(current) != 1
                    or not _same(skills['definitions'][enemy], selected['complete_skill_definitions'][enemy])
                    or not _same(skills['bindings']['ro6_b_5'][enemy + '@0'], selected['complete_skill_bindings'][enemy])):
                return None
        return deepcopy(data)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, StopIteration,
            IndexError, RecursionError, UnicodeError):
        return None


def cycle_reference(stage_id, enemy_id, level):
    if (type(stage_id) is not str or type(enemy_id) is not str or type(level) is not int
            or (stage_id, enemy_id, level) not in TARGETS):
        return None
    data = _packet()
    identity = {'stage_id': stage_id, 'enemy_id': enemy_id, 'level': level}
    if data is None:
        return {'target': True, **identity, 'source_valid': False, 'status': 'source_unavailable',
                'reference': None, 'source_identity': None, **_unknown(),
                'notice': '交替激活与模块资料暂时无法核对；旧说明与条目选择已清除，恢复后请重新选择。'}
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
        return '交替激活与模块资料暂时无法核对；旧说明与条目选择已清除，恢复后请重新选择。'
    ref = result.get('reference')
    if type(ref) is not dict:
        return '交替激活与模块资料暂时无法核对，请重新选择。'
    topics = ref['topics']
    if topic_id is not None:
        if type(topic_id) is not str:
            return '所选资料条目暂时无法核对，请重新选择。'
        topics = [topic for topic in topics if topic['id'] == topic_id]
        if not topics:
            return '所选资料条目暂时无法核对，请重新选择。'
    lines = [ref['entry_name'] + ' · 交替激活与模块资料', ref['overview_notice'], ref['scope_notice']]
    for topic in topics:
        actor = {'lorentz': '洛伦茨，扰动之谬', 'cube': '源阶方'}.get(topic['id'])
        skills = [skill for skill in ref['skills'] if actor is not None and skill['actor'] == actor]
        paragraphs = [text.replace('各技能的完整作用与限定模式见技能原文', '各技能的完整作用与限定模式见下方各招式')
                      for text in topic['paragraphs'] if not any(text == skill['text'] for skill in skills)]
        lines += ['', '【' + topic['name'] + '】', *paragraphs]
        for skill in skills:
            lines += ['', '【' + skill['name'] + '】', skill['mode_label'], skill['text']]
    lines += ['', '【仍未确认】', *['• ' + text for text in ref['player_unknowns']]]
    text = '\n'.join(lines)
    text = text.replace('近战途径法术普通伤害', '法术伤害（按近战伤害类别处理）')
    text = text.replace('无途径法术普通伤害', '法术伤害（原资料未归入近战或远程伤害类别）')
    return text
