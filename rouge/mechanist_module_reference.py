"""Opt-in packet arithmetic for the sealed native Mechanist module rule.

The declaration is an offline reference. It does not sample a blocker, create
an attack, locate a collision, or assert current hotfix equivalence.
"""
import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

from .catalog import catalog
from .enemy_environment import damage_factor

FLAG = 'mechanist_module_static_reference'
BLOCKER = 'mechanist_target_blocker'
MODULE = 'uniequip_002_mcnist'
BLOCKERS = ('self', 'own_token', 'other', 'none', 'unknown')


@lru_cache(maxsize=1)
def rule():
    return json.loads((Path(__file__).parent / 'data' /
                       'mechanist-module-native-reference.json').read_text(encoding='utf-8'))


def qualification(scenario):
    """Keep cultivation/map qualification separate from the native skill gate."""
    data = rule()
    profile = catalog()['operators']['mechanist']
    module = next(m for m in profile['modules'] if m['id'] == MODULE)
    stage = scenario.get('module_level', 0)
    skill = scenario.get('skill')
    elite = scenario.get('elite', 2)
    level = scenario.get('level')
    if level is None and type(elite) is int and 0 <= elite < len(profile['phases']):
        level = profile['phases'][elite]['max_level']
    map_tag = scenario.get('map_tag', 'rogue_6')
    cultivation = (scenario.get('operator') == 'mechanist' and
                   scenario.get('module_id') == MODULE and type(stage) is int and
                   1 <= stage <= 3 and type(elite) is int and type(level) is int and
                   elite >= module['unlock_elite'] and level >= module['unlock_level'])
    gate = data['stages'][str(stage)]['skill_indices'] if type(stage) is int and 1 <= stage <= 3 else None
    index = skill - 1 if type(skill) is int and 1 <= skill <= 3 else None
    skill_valid = index is not None and gate is not None and (not gate or index in gate)
    return {'cultivation_qualified': cultivation, 'map_qualified': map_tag == 'rogue_6',
            'native_skill_index': index, 'allowed_native_skill_indices': deepcopy(gate),
            'native_skill_gate_qualified': skill_valid,
            'qualified': cultivation and map_tag == 'rogue_6' and skill_valid,
            'map_tag': map_tag, 'map_context': 'explicit' if 'map_tag' in scenario else 'current_product_theme',
            'module_id': scenario.get('module_id'), 'module_level': stage}


def _scale(stage):
    module = next(m for m in catalog()['operators']['mechanist']['modules'] if m['id'] == MODULE)
    part = next(p for p in module['levels'][stage-1]['parts']
                if p.get('resKey') == rule()['stages'][str(stage)]['res_key'])
    candidate = next(c for c in part['addOrOverrideTalentDataBundle']['candidates']
                     if c['prefabKey'] == '11_root' and c['isHideTalent'])
    return next(b['value'] for b in candidate['blackboard'] if b['key'] == 'atk_scale')


def finish(scenario, result):
    if scenario.get('operator') != 'mechanist':
        return
    enabled = scenario.get(FLAG, False)
    if type(enabled) is not bool:
        raise ValueError(FLAG + ' 需要明确的布尔值。')
    if not enabled:
        return
    qualified = qualification(scenario)
    if not qualified['qualified']:
        return
    context = scenario.get('relic_context') or {}
    blocker = context.get(BLOCKER)
    if blocker is not None and (type(blocker) is not str or blocker not in BLOCKERS):
        raise ValueError(BLOCKER + ' 需要 self、own_token、other、none 或 unknown；人数不能代替目标身份。')
    multiplier = _scale(qualified['module_level'])
    factor = None if blocker in (None, 'unknown') else multiplier if blocker in ('self', 'own_token') else 1.0
    profile = catalog()['operators']['mechanist']
    skill = scenario['skill']
    bb = profile['skills'][skill-1]['levels'][scenario.get('skill_rank', 10)-1]['values']
    attack = result['attack']
    stats = result['estimate']['base_stats']
    effects = result.get('applied_effects', [])
    rows = []

    def packet(key, name, dtype, source_attack, skill_scale, count=None, count_scope=None):
        base_raw = source_attack * skill_scale
        final_factor = damage_factor(scenario, dtype) * (1 + sum(
            e['value'] for e in effects if e['kind'] == 'damage_taken' and e.get('damage_type') == dtype))

        def dealt(scale):
            raw = base_raw * scale
            post = (max(raw - scenario.get('enemy_defense', 0), raw * .05) if dtype == 'physical' else
                    max(raw * (1 - scenario.get('enemy_resistance', 0)/100), raw * .05))
            return post * final_factor

        value = dealt(factor) if factor is not None else None
        total = 0 if count == 0 else count * value if count is not None and value is not None else None
        row = {'key': key, 'name': name, 'damage_type': dtype,
               'source_attack_reference': source_attack, 'skill_attack_scale': skill_scale,
               'module_attack_scale': factor, 'base_raw_packet': base_raw,
               'selected_raw_packet': base_raw * factor if factor is not None else None,
               'unmodified_per_hit_reference': dealt(1), 'per_hit_reference': value,
               'blocker_unknown_candidates': [dealt(1), dealt(multiplier)] if factor is None else [],
               'modeled_or_declared_count': count, 'count_scope': count_scope,
               'conditional_count_damage_reference': total, 'actual_total_damage': None,
               'source_valid_condition': True, 'source_event': 'ON_CALCULATE_DAMAGE',
               'source_entity': 'mechanist', 'actual_attack_sample_seconds': None}
        rows.append(row)
        return row

    packet('normal', '本体常态单次普攻', 'physical', stats['attack'], 1)
    if skill == 1:
        packet('skill', '五连击中的单段物理伤害', 'physical', attack, bb['attack@atk_scale'],
               result.get('hits'), 'existing_offline_attack_preview')
    elif skill == 2:
        shield_reference = result['shield_break_reference']
        packet('skill', '本体来源的单次破屏爆炸', 'magic', attack, bb['atk_scale'],
               shield_reference['hits_requested'] if shield_reference['source_possible']['cast'] else 0,
               'declared_whole_skill_break_count_subject_to_target_lifetime')
    else:
        bombard = next(c for c in result['components'] if c['name'] == '轰击')
        charge = next(c for c in result['components'] if c['name'] == '结构性原理冲锋')
        packet('bombard', '本体单次轰击', 'magic', attack, bb['attack@atk_scale'],
               bombard['hits'], 'existing_offline_attack_preview')
        packet('charge', '机械师来源的单次冲锋物理伤害', 'physical', attack, bb['atk_scale'],
               charge['hits'], 'declared_charge_hit_count')
    selected = [r for r in rows if r['key'] != 'normal']
    subtotal = (sum(r['conditional_count_damage_reference'] for r in selected)
                if all(r['conditional_count_damage_reference'] is not None for r in selected) else None)
    # A whole-skill shield declaration cannot be placed into this observation.
    window_subtotal = None if skill == 2 else subtotal
    if 'window_seconds' in scenario and result['estimate']['skill'].get('window_seconds') == 0:
        window_subtotal = 0
    reference = {'scope': 'explicit_current_native_module_packet_conditions',
                 'qualified': qualified, 'selected': True, 'target_blocker_declaration': blocker,
                 'condition_source': 'manual_offline_preview', 'native_multiplier_parameter': multiplier,
                 'packets': rows, 'conditional_count_damage_reference': subtotal,
                 'modeled_window_damage_reference': window_subtotal,
                 'full_cast_damage': None, 'actual_window_damage': None, 'cycle_damage': None,
                 'actual_blocker': None, 'actual_source_valid': None, 'actual_collision_seconds': None,
                 'current_hotfix_equivalence_verified': False, 'runtime_binding_verified': False,
                 'source': deepcopy(rule()['source']),
                 'notes': ['明确选用已封存原生模组规则：目标阻挡身份是局外声明，未从游戏读取。',
                           '本体伤害来源仍有效且模组隐藏能力已附着，才进入伤害计算事件；本表以这两个条件成立为前提。',
                           '150%乘入每个伤害包的atkScale后再减防/减抗；不改面板攻击，不在减伤后重复乘算。',
                           'self/own_token分别指本体或其所属召唤物阻挡当前目标；阻挡人数、上限及召唤物数量不能代替此身份。',
                           '单包采用所列稳定攻击与已覆盖修正；短时属性、首次伤害及未覆盖修饰不由本表补齐。',
                           '次数沿用既有出手预览或声明次数，仅是静态条件小计；不证明实际命中、碰撞、技能阶段或周期。',
                           '当前文件一级附着门只列技能索引0（第一技能），二/三级不限制所选技能；当前热更新未核验。',
                           '冲锋的伤害source是机械师，弹道起点/选择可使用结构性原理；未推广到召唤物自身普攻或其他技能。']}
    result['mechanist_module_reference'] = reference
    if skill == 1:
        row = selected[0]
        result['per_hit'] = row['per_hit_reference']
        # The opt-in fixed-condition model contains this supported owner packet.
        # Do not duplicate a whole-skill subtotal into any separate relic packet.
        result['components'] = [{'name': row['name'], 'damage_type': 'physical',
            'hits': row['modeled_or_declared_count'], 'per_hit': row['per_hit_reference'],
            'total': row['conditional_count_damage_reference'], 'actual_total': None}]
    elif skill == 2:
        row = selected[0]
        result['per_hit'] = row['per_hit_reference']
        shield = result['shield_break_reference']
        shield['per_hit_damage_reference'] = row['per_hit_reference']
        shield['declared_count_damage_reference'] = row['conditional_count_damage_reference']
        for part in result.get('components', []):
            part.update(per_hit=row['per_hit_reference'], total=row['conditional_count_damage_reference'], actual_total=None)
    else:
        for row, name in zip(selected, ('轰击', '结构性原理冲锋')):
            part = next(c for c in result['components'] if c['name'] == name)
            part.update(per_hit=row['per_hit_reference'], total=row['conditional_count_damage_reference'], actual_total=None)
            part.pop('event_amounts', None)
        if result.get('charge_reference'):
            result['charge_reference'].update(per_hit_damage=selected[1]['per_hit_reference'],
                declared_count_damage=selected[1]['conditional_count_damage_reference'])
    result.pop('known_damage_subtotals', None)
    result['total_damage'] = None
    for key in ('total_damage', 'phase_damage', 'cycle_damage', 'cycle_dps', 'window_damage', 'window_dps'):
        result['estimate']['skill'][key] = None
    result['complete'] = result['estimate']['complete'] = False
    result['scope'] = result['estimate']['scenario_scope'] = '当前静态模组条件单包与小计；实际阻挡、来源存续和完整伤害未知。'
    result['estimate']['notes'].extend(reference['notes'][:3])
