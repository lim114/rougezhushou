"""Fixed documentary boss forms; never actual phase state or a numeric model."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-boss-phase-309'
DATA = 'rouge/data/boss-phase-reference.json'
MANIFEST = PACK + '/source-manifest.json'
SELECTED = PACK + '/selected-original-records.json'
PLAYER = PACK + '/player-reading-data-candidate.json'
MODES = PACK + '/final-review/seven-complete-visible-cards.json'
REVIEW = PACK + '/final-review/source-review.json'
TARGET = ('ro6_b_6', 'enemy_2150_shchmr', 0)
DATA_SHA256 = '__DATA_SHA__'
MANIFEST_SHA256 = '__MANIFEST_SHA__'
ACTUAL_FIELDS = ('actual_phase', 'actual_transition', 'actual_damage', 'actual_elapsed_time',
                 'actual_target', 'actual_current_server_eligibility', 'phase_stats')
RUNTIME_FILES = {DATA, SELECTED, PLAYER, MODES, REVIEW, PACK + '/boss-complete.html',
                 PACK + '/stage-complete.html', PACK + '/http-source-records.json'}


def _same(one, two):
    if type(one) is not type(two):
        return False
    if type(one) is dict:
        return one.keys() == two.keys() and all(type(k) is str and _same(one[k], two[k]) for k in two)
    if type(one) is list:
        return len(one) == len(two) and all(_same(a, b) for a, b in zip(one, two))
    return one == two


def _unknown():
    return {**{key: None for key in ACTUAL_FIELDS}, 'current_server_verified': False,
            'numerical_phase_model_added': False, 'run_state_updated': False,
            'inventory_updated': False, 'modifiers_changed': False, 'maps_changed': False}


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


def _reference(player, mode_cards):
    ref = deepcopy(player)
    ref.update(stage_id=TARGET[0], enemy_id=TARGET[1], level=TARGET[2],
               boss_name='玻利瓦尔，症结之核')
    for phase in ref['phases']:
        phase['id'] = phase['phase_id']
    for skill, card in zip(ref['skills'], mode_cards['cards'][:6]):
        skill['original_documented_modes'] = deepcopy(skill['documented_modes'])
        skill['documented_modes'] = deepcopy(card['documented_mode_labels'])
    ref['common_documented_context']['reading_notes'] = [
        ('文献说明注：' + note) if '未用完的延长灾厄' in note else note
        for note in ref['common_documented_context']['reading_notes']]
    return ref


def _packet():
    """Fresh small authorities; entire selected mutable legacy objects are compared."""
    try:
        raw = _file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw)
        if (manifest['schema'] != 'boss_phase_source_manifest_v1'
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
        player, modes = json.loads(blobs[PLAYER]), json.loads(blobs[MODES])
        if (data['schema'] != 'boss_phase_reference_v1'
                or not _same(player['identity'], dict(zip(('stage_id', 'enemy_id', 'level'), TARGET)))
                or not _same(data['reference'], _reference(player, modes))
                or not _same(data['selected_originals'], selected)
                or not _same(data['actual_and_mutation_fields'], _unknown())):
            return None
        from .battle_preview import battle_data
        from .enemy_skills import skill_data
        battle, skills = battle_data(), skill_data()
        stage = battle['stages'][TARGET[0]]
        enemies = [row for row in stage['enemies'] if row['id'] == TARGET[1]
                   and type(row['level']) is int and row['level'] == TARGET[2]]
        if (len(enemies) != 1 or not _same(battle['source'], data['complete_battle_source'])
                or not _same(stage, selected['canonical_stage_complete'])
                or not _same(enemies[0], selected['canonical_enemy_complete'])
                or not _same(skills['source'], data['complete_skill_source'])
                or not _same(skills['definitions'][TARGET[1]], selected['current_skill_definition_complete'])
                or not _same(skills['bindings'][TARGET[0]][TARGET[1] + '@0'], selected['current_skill_binding_complete'])):
            return None
        return deepcopy(data)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, StopIteration,
            IndexError, RecursionError, UnicodeError):
        return None


def phase_reference(stage_id, enemy_id, level):
    if (type(stage_id) is not str or type(enemy_id) is not str or type(level) is not int
            or (stage_id, enemy_id, level) != TARGET):
        return None
    data = _packet()
    if data is None:
        return {'target': True, 'stage_id': stage_id, 'enemy_id': enemy_id, 'level': level,
                'source_valid': False, 'status': 'source_unavailable', 'reference': None,
                'source_identity': None, **_unknown(),
                'notice': '形态与转换资料暂时无法核对；旧说明与形态选择已清除，恢复后请重新选择。'}
    return {'target': True, 'stage_id': stage_id, 'enemy_id': enemy_id, 'level': level,
            'source_valid': True, 'status': 'documented_reference',
            'reference': data['reference'],
            'source_identity': {'manifest_sha256': MANIFEST_SHA256, 'data_sha256': DATA_SHA256},
            **_unknown(), 'notice': data['reference']['overview_notice']}


def _plain(text):
    text = text.replace('我方干员 > 自身', '我方干员（优先选择），其次为自身')
    text = text.replace('近战途径真实伤害', '真实伤害（按近战伤害类别处理）')
    text = text.replace('近战途径物理伤害', '物理伤害（按近战伤害类别处理）')
    text = text.replace('无途径法术伤害', '法术伤害（原资料未归入近战或远程伤害类别）')
    text = text.replace('dot', '持续灼烧').replace('DOT', '持续灼烧')
    text = text.replace('同名技能记录没有恢复模式绑定', '同名招式的对应关系尚未核实')
    text = text.replace('原字段10与文献11', '原始配置记为10秒，详细文献记为11秒，两者')
    return text


def reference_text(result, phase_id=None):
    """Plain documentary reading. Raw DOM and engine keys stay in the source tab."""
    if result is None:
        return ''
    if type(result) is not dict or result.get('source_valid') is not True:
        return '形态与转换资料暂时无法核对；旧说明与形态选择已清除，恢复后请重新选择。'
    ref = result.get('reference')
    if type(ref) is not dict:
        return '形态与转换资料暂时无法核对，请重新选择。'
    phase = None
    if phase_id is not None:
        if type(phase_id) is not str:
            return '所选形态资料暂时无法核对，请重新选择。'
        phase = next((row for row in ref['phases'] if row['id'] == phase_id), None)
        if phase is None:
            return '所选形态资料暂时无法核对，请重新选择。'
    lines = [ref['boss_name'] + ' · 形态与转换资料', ref['overview_notice'], ref['scope_notice']]
    if phase:
        lines += ['', '【' + phase['name'] + '】', phase['summary'], '', '【这个形态的招式】']
        skills = [row for row in ref['skills'] if row['skill_id'] in phase['skill_ids']]
    else:
        lines += ['', '【文献中的形态】']
        lines += ['• ' + row['name'] + '：' + row['summary'] for row in ref['phases']]
        skills = ref['skills']
        lines += ['', '【招式与适用形态】']
    if phase and not skills:
        lines.append('文献未在这个条目下另列专属招式；普通攻击与共同影响见下方。')
    for skill in skills:
        lines += ['', skill['name'] + '（' + '、'.join(skill['documented_modes']) + '）', skill['effect_text']]
        if skill['skill_id'] == 'flying_ground':
            corresponding = next(row for row in ref['skills'] if row['skill_id'] == 'unextinguished_ground')
            lines += ['', '对应的【未熄之地】效果（文献交叉说明）', corresponding['effect_text']]
    lines += ['', '【进入、离开和返回】']
    transitions = [row for row in ref['transitions'] if phase is None
                   or phase['id'] in (row['from_phase_id'], row['to_phase_id'])]
    lines += ['• ' + row['condition'] + '：' + row['text'] for row in transitions]
    lines += ['', '【共同能力与适用条件】', ref['common_documented_context']['text']]
    lines += ['• ' + row for row in ref['common_documented_context']['reading_notes']]
    lines += ['', '【不能直接对算的来源差异】']
    for row in ref['source_differences']:
        document_text = row['document_text']
        if row['difference_id'] == 'raw_mode_index_binding':
            document_text = '原始资料保留了多条同名招式记录，但尚未确认它们分别对应哪个形态。'
        lines += [row['title'] + '：' + document_text, row['reading_notice']]
    lines += ['', '【仍未确认】',
              '• 本局当前形态、实际转换是否发生以及发生时刻。',
              '• 各形态实际生命、攻击和完整加成方式。',
              '• 首次发动、冷却、打断后重启及转换的实际时间。',
              '• 实际选中的目标和具体伤害范围。',
              '• 第三或飞行形态被击倒后的完整结束过程，不能据此保证通关。']
    lines.append('这些是固定资料的有条件说明，不代表本局已经发生，也不产生阶段面板或实际倒计时。')
    return _plain('\n'.join(lines))
