"""Explicit current Haruka BLS-Y selector arithmetic, never actual acquisition."""
import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from .catalog import catalog

FLAG = 'haruka_module_target_static_reference'
MODULE = 'uniequip_002_haruka'
OP = 'char_4202_haruka'


@lru_cache(maxsize=1)
def rule():
    return json.loads((Path(__file__).parent/'data'/'haruka-targets-native-reference.json').read_text(encoding='utf-8'))


def qualification(scenario):
    profile = catalog()['operators'][OP]
    module = next(m for m in profile['modules'] if m['id'] == MODULE)
    elite = scenario.get('elite', 2)
    level = scenario.get('level') or profile['phases'][elite]['max_level']
    stage = scenario.get('module_level', 0)
    skill = scenario.get('skill')
    parts = module['levels'][stage-1]['parts'] if type(stage) is int and stage in (1,2,3) else []
    candidates = [c for p in parts if p['target'] == 'TRAIT_DATA_ONLY' and p.get('resKey') is None
                  and not p.get('isToken') and p.get('validInGameTag') is None and p.get('validInMapTag') is None
                  for c in (p.get('overrideTraitDataBundle') or {}).get('candidates', [])]
    bound = any(c.get('prefabKey') == '-1' and c.get('requiredPotentialRank',0) <= scenario.get('potential',1)-1
                and int(c['unlockCondition']['phase'][-1]) <= elite
                and (int(c['unlockCondition']['phase'][-1]) < elite or c['unlockCondition']['level'] <= level)
                and {v['key']:v['value'] for v in c['blackboard']}.get('attack@max_target_heal') == 2 for c in candidates)
    qualified = (scenario.get('operator') == OP and scenario.get('module_id') == MODULE
                 and elite >= module['unlock_elite'] and level >= module['unlock_level'] and bound
                 and type(skill) is int and skill in (1,2,3))
    return {'qualified': bool(qualified), 'cultivation_qualified': bool(bound and elite >= module['unlock_elite']
            and level >= module['unlock_level']), 'native_trait_data_bound': bool(bound),
            'module_id': scenario.get('module_id'), 'module_level': stage,
            'native_skill_index': skill-1 if type(skill) is int and skill in (1,2,3) else None}


def select(scenario, ref):
    enabled = scenario.get(FLAG, False)
    if type(enabled) is not bool:
        raise ValueError(FLAG+' 需要明确的布尔值。')
    if not enabled or not qualification(scenario)['qualified']:
        return ref
    ref.update(legacy_modeled_target_limit_reference=ref['modeled_target_limit_reference'],
               modeled_target_limit_reference=ref['conditional_target_limit_reference'],
               selected_static_reference=True, native_static_binding_verified=True,
               native_static_composition_verified=True,
               native_selector_key=rule()['skill_modes'][str(scenario['skill'])]['selector_key'],
               native_selector_limit_reference=ref['conditional_target_limit_reference'])
    return ref


def finish(scenario, result):
    if scenario.get('operator') != OP:
        return
    enabled = scenario.get(FLAG, False)
    if type(enabled) is not bool:
        raise ValueError(FLAG+' 需要明确的布尔值。')
    if not enabled or not qualification(scenario)['qualified']:
        return
    old = result['haruka_healing_reference']
    body = next(c for c in result['components'] if c['name'] == '护佑者普通治疗')
    before = old['window_reference']['body_healing_reference_before_recipient_factor']
    targets = old['window_reference']['modeled_healing_targets']
    rows = [{'name':'护佑者普通治疗','damage_type':'healing',
             'per_recipient_heal_reference':body['per_hit'],
             'modeled_recipient_heal_count':body['hits'],
             'modeled_body_attempt_count':body['hits']/targets if targets else 0,
             'conditional_window_subtotal':body['total'],
             'before_covered_healing_factors':deepcopy(before),
             'actual_target_count':None,'actual_total':None}]
    if scenario['skill'] == 2:
        derived = next(c for c in result['components'] if c['name'] == '治疗衍生伤害')
        rows.append({'name':derived['name'],'damage_type':'magic','per_recipient_derived_damage_reference':derived['per_hit'],
                     'modeled_recipient_heal_count':derived['hits'],'conditional_window_subtotal':derived['total'],
                     'condition':'each preview recipient heals with the declared current enemy adjacent',
                     'actual_adjacent_enemy_coverage':None,'actual_total':None})
    ref = {'selected':True,'qualification':qualification(scenario),'source':deepcopy(rule()['source']),
           'trait_base_parameter':old['selected_trait_target_limit_parameter'],
           'skill_add_parameter':old['skill_target_add_parameter'],
           'selector_key':old['native_selector_key'],'selector_limit_reference':old['native_selector_limit_reference'],
           'declared_potential_recipients':old['declared_healing_targets'],'modeled_potential_recipients':targets,
           'packets':rows,'conditional_window_body_healing_reference':body['total'],
           'native_static_binding_verified':True,'native_static_composition_verified':True,
           'runtime_binding_verified':False,'current_hotfix_equivalence_verified':False,
           'actual_target_limit':None,'actual_target_count':None,'actual_acquisition_times_seconds':None,
           'actual_full_cast_healing':None,'actual_window_healing':None,'actual_cycle_healing':None,
           'notes':['已明确采用封存版本的BLS-Y特性数据与当前技能组合；S2为特性人数加技能增加人数，S1/S3直接读取特性人数。',
                    '数据流结果覆盖技能键，选择器再直接覆盖上限；不再加原技能值或选择器默认1名。',
                    '沿用既有局外受疗人数声明和出手预览，人数上限只限制满额潜在受疗分项；不推断实际可受疗友方、健康过滤、获取时刻或客户端回调。',
                    '治疗分项采用最终已覆盖治疗倍率后的金额，每个倍率只使用一次；浮泡与浮空仍是独立条件来源。',
                    'S2派生伤害保留当前敌人邻接每名受疗者的条件，不从治疗人数自动证明邻接或实际命中。',
                    '原件为TRAIT_DATA_ONLY且resKey为空，绑定已有-1特性Talent；不借用其他模组的附着能力原件。',
                    '实际热更新等价、当前特性成功使用及完整施放/观察/周期总量未知。']}
    result[FLAG] = ref
    # Pending flags are placed before the existing plan masks; final values
    # here preserve their normal relic scaling and separate source budgets.
    result['total_healing'] = None
    skill = result['estimate']['skill']
    for key in ('total_healing','phase_healing','window_healing','window_hps','cycle_healing','cycle_hps'):
        skill[key] = None
    if scenario['skill'] == 2:
        result['total_damage'] = None
        for key in ('total_damage','phase_damage','window_damage','window_dps','cycle_damage','cycle_dps'):
            skill[key] = None
    result['complete'] = result['estimate']['complete'] = False
    result['estimate']['notes'].extend(ref['notes'][:3])
