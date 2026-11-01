"""Current snapshot declarations, qualified before shared environment arithmetic."""
from copy import deepcopy
import math
from . import current_battle_reference as model
from .enemy_environment import apply_fixed_environment


def qualify_current(result):
    packet = model.packet()
    if packet is None:
        return None
    stage = packet['version']['current']['details']['stages'].get(result['id'])
    if stage is None:
        return None
    key = 'levels/' + stage['levelId'].lower() + '.json'
    level = packet['inputs']['levels'][key]
    profiles = {str(row['grade']): {k: row[k] for k in ('grade', 'modeDifficulty', 'bossValue', 'ruleDesc', 'addDesc')}
                for row in packet['version']['current']['details']['difficulties'] if row['modeDifficulty'] == 'NORMAL'}
    difficulty_source = next(row for row in packet['version']['source']['records'] if row.get('role') == 'current')
    if (result['source_identity'] != packet['identity'] or result['level_key'] != key
            or result['source'] != packet['selection']['original_sources'][key]
            or result['stage'] != stage or result['level'] != level
            or result['difficulty_reference'] != profiles or result['difficulty_source'] != difficulty_source
            or result['enemies'] != model.enemy_records(level, packet)):
        return None
    return {'stage': stage, 'preview': {'runes': level.get('runes') or [],
            'global_buffs': level.get('globalBuffs') or [], 'possible_enemies': result['enemies']},
            'difficulty_profiles': result['difficulty_reference']}


def environment(reference, enemy, config, grade):
    if enemy['tier'] not in model.TIERS:
        return None, '这份当前引用的敌人类别尚未确认，未套用类别相关难度修正。'
    if enemy['use_db'] and not enemy['exact_database_level_present']:
        return None, '这份当前引用缺少精确数据库等级，不借用其它等级。'
    values = enemy['declared_traits']['explicit_core_attributes']
    keys = ('maxHp', 'atk', 'def', 'magicResistance')
    if any(type(values.get(key)) not in (int, float) or not math.isfinite(values[key])
           or values[key] < 0 for key in keys):
        return None, '这份当前引用尚无完整的四项明确属性，缺项不填零。'
    component = {'enemy_id': enemy['id'], 'level_type': enemy['tier'],
                 'stats': {key: deepcopy(values[key]) for key in keys},
                 'steps': [], 'pending': [], 'damage_factor': 1}
    apply_fixed_environment(component, reference['stage'], reference['preview'],
        {'value': grade}, config.get('zone'), difficulty_profiles=reference['difficulty_profiles'])
    return component, None
