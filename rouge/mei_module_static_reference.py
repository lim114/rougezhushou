"""Explicit Mei packet arithmetic under the sealed native FLY_ONLY condition."""
import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

from .catalog import catalog
from .enemy_environment import damage_factor
from .mei_module_reference import reference as parameter_reference

FLAG = 'mei_module_static_reference'
MOTION = 'mei_target_motion'
MODULE = 'uniequip_002_mm'
MOTIONS = ('fly', 'not_fly', 'unknown')


@lru_cache(maxsize=1)
def rule():
    return json.loads((Path(__file__).parent/'data'/'mei-module-native-reference.json').read_text(encoding='utf-8'))


def qualification(scenario):
    profile = catalog()['operators']['char_133_mm']
    module = next(m for m in profile['modules'] if m['id'] == MODULE)
    stage = scenario.get('module_level', 0)
    skill = scenario.get('skill')
    parts = module['levels'][stage-1]['parts'] if type(stage) is int and 1 <= stage <= 3 else []
    ref = parameter_reference(profile, scenario, parts) if scenario.get('module_id') == MODULE and parts else None
    reskey = rule()['stages'].get(str(stage))
    bound = bool(ref and any(p.get('resKey') == reskey and p.get('target') == 'TRAIT' for p in parts))
    return {'qualified': bound and type(skill) is int and skill in (1, 2),
            'cultivation_qualified': bool(ref), 'native_trait_resource_bound': bound,
            'module_id': scenario.get('module_id'), 'module_level': stage,
            'native_skill_index': skill-1 if type(skill) is int and skill in (1, 2) else None,
            'native_skill_gate': 'none_in_current_trait_prefabs',
            'map_gate': 'none_in_original_module_parts'}


def finish(scenario, result):
    if scenario.get('operator') != 'char_133_mm':
        return
    enabled = scenario.get(FLAG, False)
    if type(enabled) is not bool:
        raise ValueError(FLAG+' 需要明确的布尔值。')
    if not enabled or not qualification(scenario)['qualified']:
        return
    motion = (scenario.get('relic_context') or {}).get(MOTION)
    if motion is not None and (type(motion) is not str or motion not in MOTIONS):
        raise ValueError(MOTION+' 需要 fly、not_fly 或 unknown；基础敌人分类不能代替当前原生条件。')
    old = result['mei_airborne_module_reference']
    multiplier = old['attack_scale_parameter']
    factor = None if motion in (None, 'unknown') else multiplier if motion == 'fly' else 1.0
    skill = scenario['skill']
    profile = catalog()['operators']['char_133_mm']
    bb = profile['skills'][skill-1]['levels'][scenario.get('skill_rank', 10)-1]['values']
    defense = scenario.get('enemy_defense', 0) * max(0, 1-sum(
        r['value'] for r in scenario.get('_relic_rules', []) if r['kind'] == 'defense_penetration'))
    final = damage_factor(scenario, 'physical') * (1+sum(
        e['value'] for e in result.get('applied_effects', [])
        if e['kind'] == 'damage_taken' and e.get('damage_type') == 'physical'))
    rows = []

    def packet(key, name, attack, scale, count=None):
        raw = attack*scale
        def dealt(k):
            value = raw*k
            return max(value-defense, value*.05)*final
        value = None if factor is None else dealt(factor)
        subtotal = 0 if count == 0 else count*value if count is not None and value is not None else None
        row = {'key': key, 'name': name, 'damage_type': 'physical', 'source_entity': profile['id'],
               'source_attack_reference': attack, 'skill_attack_scale': scale,
               'module_attack_scale': factor, 'base_raw_packet': raw,
               'selected_raw_packet': raw*factor if factor is not None else None,
               'effective_defense_reference': defense, 'covered_final_multiplier': final,
               'unmodified_per_hit_reference': dealt(1), 'per_hit_reference': value,
               'motion_unknown_candidates': [dealt(1), dealt(multiplier)] if factor is None else [],
               'modeled_or_declared_count': count,
               'count_scope': 'existing_offline_attack_preview' if count is not None else None,
               'conditional_count_damage_reference': subtotal,
               'actual_total_damage': None, 'actual_attack_sample_seconds': None,
               'source_valid_condition': True, 'source_event': 'ON_CALCULATE_DAMAGE'}
        rows.append(row)
        return row

    packet('normal', '常态单次普攻', result['estimate']['base_stats']['attack'], 1)
    part = next(c for c in result['components'] if c['name'] == profile['skills'][skill-1]['levels'][scenario.get('skill_rank', 10)-1]['name'])
    selected = packet('skill', '麻痹弹单次物理伤害' if skill == 1 else '技能期间单次物理普攻',
                      result['attack'], bb['atk_scale'] if skill == 1 else 1, part['hits'])
    ref = {'selected': True, 'qualified': qualification(scenario),
           'scope': 'explicit_current_native_module_packet_conditions',
           'target_motion_declaration': motion, 'condition_source': 'manual_offline_preview',
           'native_multiplier_parameter': multiplier, 'packets': rows,
           'conditional_count_damage_reference': selected['conditional_count_damage_reference'],
           'actual_window_damage': None, 'full_cast_damage': None, 'cycle_damage': None,
           'native_static_binding_verified': True, 'native_static_composition_verified': True,
           'current_hotfix_equivalence_verified': False, 'runtime_binding_verified': False,
           'actual_target_motion_mode': None, 'actual_target_is_airborne': None,
           'actual_attachment': None, 'actual_source_valid': None,
           'source': deepcopy(rule()['source']),
           'notes': ['已明确选择当前封存原生模组规则；fly仅声明当前目标满足get_changeableMotionMode的FLY_ONLY条件。',
                     'not_fly声明该条件不成立，unknown/留空保持两种单包候选；不从敌人基础飞行分类、名字、重量或浮空参数推断。',
                     '以模组特性能力已成功附着、伤害来源有效为条件；当前热更新和实际运行态尚未核验。',
                     '110%乘入本体伤害包的atkScale后再减防和最低伤害，随后应用已覆盖的最终修正；不改面板攻击，不重复乘天赋或模组属性。',
                     '普通、麻痹弹替换攻击及S2模式攻击的当前原件均使用MeleeAttack→ApplyDamage；不依据近远程名称推测伤害链。',
                     '单包采用所列稳定攻击参考，次数沿用原有局外出手预览；小计不证明实际命中、攻击快照、首次/结束相位或完整回转。',
                     '沿用现有十进制参数算术参考，未宣称逐位复刻客户端单精度转FP及后续取整。',
                     '该声明不写本局、不读取站位或实时状态，也不将战斗内触发藏品重新加入数值。']}
    result['mei_module_static_reference'] = ref
    old.update(native_static_binding_verified=True, native_static_composition_verified=True,
               selected_static_reference=True, applied_to_numeric_estimate=factor is not None)
    part.update(per_hit=selected['per_hit_reference'], total=selected['conditional_count_damage_reference'], actual_total=None)
    # Only the supported owner packet is replaced; separate relic/reference
    # packets keep their own source and applicability.
    part.pop('event_amounts', None)
    result['per_hit'] = selected['per_hit_reference']
    if 'mei_s1_reference' in result:
        result['mei_s1_reference']['per_hit_damage_reference'] = selected['per_hit_reference']
    result.pop('known_damage_subtotals', None)
    result['total_damage'] = None
    for key in ('total_damage','phase_damage','cycle_damage','cycle_dps','window_damage','window_dps'):
        result['estimate']['skill'][key] = None
    result['complete'] = result['estimate']['complete'] = False
    result['scope'] = result['estimate']['scenario_scope'] = '梅当前静态模组条件单包及条件小计；实际空中状态、来源存续与完整伤害未知。'
    result['estimate']['notes'].extend(ref['notes'][:4])
