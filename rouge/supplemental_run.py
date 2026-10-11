"""Seven low-star references using proven runes and stable battle attributes."""
import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from .catalog import operator_profiles
from .supplemental_skills import (_cultivated_stats,_skill_reference,
                                  supplemental_profiles,format_reference)
from .relic_attributes import is_attribute_rune,apply_attribute_runes
from .supplemental_cost import supported_cost,cost_reference
from .supplemental_sp import supported_sp,sp_reference
from .supplemental_healing import supported_healing,apply_healing_reference
from .supplemental_damage import supported_damage,damage_reference,apply_damage_reference

ENVIRONMENT_KEYS={'relic_ids','run_config','relic_context','inventory_status','operator_metadata'}
# Proven child-buff multipliers from the pinned templates, not every rule with
# an attribute-like name. Keep live combat conditions out of this adapter.
ORDINARY_SOURCES={
    'rogue_6_relic_cargo_2':('global_buff_normal',1,'parts_count',{'attack_pct','hp_pct'}),
    'rogue_6_relic_cargo_10':('global_buff_normal',1,'emergency_hire',{'attack_pct','hp_pct','defense_pct'}),
    'rogue_6_relic_artifact_7':('global_buff_layer',0,'grudge_stacks',{'attack_pct'}),
}


def _ordinary_attribute(effect):
    source=ORDINARY_SOURCES.get(effect.get('relic_id'))
    return bool(source and effect.get('_verified_rule') is True and
        (effect.get('source_buff_key'),effect.get('source_buff_index'),effect.get('condition'))==source[:3]
        and effect['kind'] in source[3] and not is_attribute_rune(effect)
        and not effect.get('token_only'))


@lru_cache(maxsize=1)
def selectors():
    return json.loads((Path(__file__).parent/'data/supplemental-run-selectors.json').read_text(encoding='utf-8'))


def run_skill_reference(preview,environment,*,target_enemy=None):
    """A frozen raw run input, never a previously prepared damage scenario.

    Attribute runes and the proven, stable ordinary HP/ATK/DEF sources are
    consumed. Other resolved rules remain explicit gaps, including costs/SP.
    """
    stats=_cultivated_stats(preview)
    if type(environment) is not dict or set(environment)!=ENVIRONMENT_KEYS:
        raise ValueError('本局条件需要relic_ids、run_config、relic_context、inventory_status、operator_metadata；不能传入已处理的属性或效果。')
    environment=deepcopy(environment)
    ids=environment['relic_ids'];metadata=environment['operator_metadata']
    if type(ids) is not list or not all(type(rid) is str for rid in ids):
        raise ValueError('藏品需要ID列表。')
    for key in ('relic_context','inventory_status','operator_metadata'):
        if type(environment[key]) is not dict:raise ValueError(key+'需要对象。')
    complete=environment['inventory_status'].get('complete')
    if complete is not None and type(complete) is not bool:
        raise ValueError('藏品读取完整性需要布尔值。')
    identity=preview['operator'];member=metadata.get(identity,{})
    if type(member) is not dict:raise ValueError('当前干员的本局强化条件需要对象。')
    # The adapter supplies original selectors and original skill type fields.
    # Account archive labels alone do not identify a branch selector.
    profile={**operator_profiles()[identity],**selectors()['operators'][identity],'tokens':{}}
    raw=supplemental_profiles()['operators'][identity]
    profile['skills']=[{'id':raw['skill_id'],'levels':[
        {'duration_type':s['durationType'],'sp_type':s['spData']['spType'],
         'values':{item['key']:item['value'] for item in s['blackboard']}}
        for s in raw['levels']]}]
    scenario={'operator':identity,'skill':1,'skill_rank':preview['skill_rank'],
              'base_attack':stats['attack'],'enemy_defense':preview['enemy_defense'],
              'enemy_resistance':preview['enemy_resistance'],'relic_ids':ids,
              'run_config':environment['run_config'],'relic_context':environment['relic_context']}
    if target_enemy is not None:
        if (type(target_enemy) is not dict or
            not {'stage_id','enemy_id','level'}<=set(target_enemy)<= {'stage_id','enemy_id','level','orb_mode'} or
            type(target_enemy['stage_id']) is not str or type(target_enemy['enemy_id']) is not str or
            type(target_enemy['level']) is not int):
            raise ValueError('绑定目标需固定stage_id、enemy_id及整数level，可选orb_mode。')
        scenario['target_enemy']=deepcopy(target_enemy)
    # Identity-specific metadata must never follow a different selection.
    for key in ('recruitment_kind','char_buff_ids','char_buffs_complete',
                'char_buff_absent_ids','char_buff_pending_ids'):
        if key in member:scenario[key]=deepcopy(member[key])
    from .run_modifiers import prepare_run
    from .relics import prepare
    scenario,run_resolution=prepare_run(scenario)
    baseline_preview={**preview,'enemy_defense':scenario['enemy_defense'],
                      'enemy_resistance':scenario['enemy_resistance']}
    scenario,relic_resolution=prepare(scenario,profile)
    if target_enemy is not None:
        from .run_modifiers import finish_run
        summary={'relic_resolution':relic_resolution,'estimate':{'notes':[],'warnings':[]},
                 'warnings':[],'complete':True}
        finish_run(summary,run_resolution)
    resolved=scenario.get('effects',[])+scenario.get('_relic_rules',[])
    runes=[e for e in resolved if is_attribute_rune(e) and not e.get('token_only')]
    ordinary=[e for e in resolved if _ordinary_attribute(e)]
    costs=[e for e in resolved if supported_cost(e)]
    sp_rules=[e for e in resolved if supported_sp(e)]
    healing_rules=[e for e in resolved if supported_healing(e,raw['kind'])]
    damage_rules=[e for e in resolved if supported_damage(e)]
    unsupported=[e for e in resolved if not is_attribute_rune(e) and
                 not _ordinary_attribute(e) and not supported_cost(e) and not supported_sp(e)
                 and not supported_healing(e,raw['kind'])
                 and not supported_damage(e)
                 and not (target_enemy is not None and e.get('_verified_rule') and
                          e['kind'] in ('enemy_hp_factor','enemy_atk_factor','enemy_spawn_hp_branch','enemy_weight_delta'))
                 and not e.get('token_only')]
    battle_attributes={kind:sum(e['value'] for e in ordinary if e['kind']==kind)
                       for kind in ('attack_pct','hp_pct','defense_pct')}
    modified=apply_attribute_runes(stats,runes)
    damage=damage_reference(scenario,resolved,relic_resolution['records'])
    effective_preview={**preview,'enemy_defense':damage['effective_target_defense']
        if damage['effective_target_defense'] is not None else scenario['enemy_defense'],
        'enemy_resistance':scenario['enemy_resistance']}
    result=_skill_reference(effective_preview,modified,battle_attributes)
    result['preview']=deepcopy(preview)
    result['target_enemy']=deepcopy(run_resolution.get('enemy'))
    result['damage_reference']=damage
    apply_damage_reference(result,damage)
    cost=cost_reference(stats,result['talents'],resolved,relic_resolution['records'])
    result['deployment_reference']=cost
    result['sp_reference']=sp_reference(result['skill_parameter'],resolved,relic_resolution['records'])
    result['healing_reference']=apply_healing_reference(result,resolved,relic_resolution['records'],raw['kind'])
    if preview['operator']=='char_123_fang':
        row=next(r for r in result['rows'] if r['name']=='单次回费')
        row['value']+=cost['skill_start_dp'];row['declared_total']=row['value']*preview['count']
        row=next(r for r in result['rows'] if r['name'].startswith('部署费用'))
        row['value']=cost['estimated_cost']
    try:baseline=_skill_reference(baseline_preview,stats)
    except ValueError as error:
        # A gap can be legal with an HP rune but exceed unmodified max HP.
        baseline=None;baseline_error=str(error)
    else:baseline_error=None
    base_rows={r['name']:r['value'] for r in baseline['rows']} if baseline else {}
    if baseline:base_rows['藏品常态生命回复']=0
    for row in result['rows']:
        row['base_value']=base_rows.get(row['name'])
        row['delta']=row['value']-row['base_value'] if row['value'] is not None and row['base_value'] is not None else None
    warnings=[*relic_resolution['warnings'],*run_resolution['pending']]
    warnings.extend(damage['warnings'])
    if cost['talent_composition_pending']:
        warnings.append('轻量化天赋与藏品费用链的组合层尚未核验；部署费用未知，未将天赋减费放入任意乘区。')
    if complete is not True:warnings.append('藏品持有清单尚未确认完整；只计算当前明确的条目，不能当作完整本局面板。')
    names={r['id']:r['name'] for r in relic_resolution['records']}
    for rid in dict.fromkeys(e.get('relic_id') for e in unsupported):
        warnings.append(names.get(rid,'当前来源')+'：存在本工具尚未纳入的效果；仅列已计属性和单次分项参考。')
    result['run_attributes']={key:modified[key] for key in
                             ('hp','attack','defense','resistance','attack_speed','redeploy_seconds','block_count')}
    result['environment']=environment
    result['attribute_resolution']={'runes':deepcopy(runes),'ordinary':deepcopy(ordinary),'costs':deepcopy(costs),'sp_rules':deepcopy(sp_rules),'healing_rules':deepcopy(healing_rules),'damage_rules':deepcopy(damage_rules),
        'battle_attributes':battle_attributes,'unsupported':deepcopy(unsupported),
        'warnings':list(dict.fromkeys(warnings)),'relics':deepcopy(relic_resolution['records']),
        'run':run_resolution,'inventory_complete':complete is True,
        'complete_for_attribute_scope':not warnings,'baseline_error':baseline_error,
        'source':deepcopy(selectors()['source'])}
    result['notes'][1]='培养按独立预览条件计算；本局已证属性符文先写回，再将已确认的稳定普通属性增益与天赋/技能加成相加。未接入效果不默认为零；不写入账户或本局。'
    result['notes'].extend(['本局修正含已证属性/费用/技力参数、单来源治疗/回复、减防/定向穿透及单来源受伤倍率；芬费用天赋、技力时钟、多来源倍率及其它特殊分项仍有缺口，不生成回转和周期。',
                            '生命回复以常态最大生命计算藏品贡献，独立于直接治疗；不推算首跳、次数、受疗资格或技能期间最大生命的动态积分。',
                            '对照列为相同培养且没有本局修正的单次参考；差值不代表完整施放、周期或真实击杀。',
                            '藏品与分队取打开或更新时的快照；修改干员仅使用其自己的已确认强化，不沿用上一名干员的领取信息。'])
    if target_enemy is not None:
        result['notes'].extend(run_resolution['notes'])
        result['notes'].append('绑定固定候选目标后，手动防御/法抗输入被目标引用覆盖；无本局对照采用相同目标和难度，未加敌方藏品修正。')
    return result


def format_run_reference(result):
    resolution=result['attribute_resolution'];stats=result['attributes'];runes=result['run_attributes']
    lines=['本局属性与单次技能 · '+('当前支持范围内参考' if resolution['complete_for_attribute_scope'] else '部分参考，仍有未计或未确认项'),
           f"预计常态：生命{stats['hp']:.8g}；攻击{stats['attack']:.8g}；防御{stats['defense']:.8g}；法抗{runes['resistance']:.8g}；攻速{runes['attack_speed']:.8g}（官方单位）；再部署{runes['redeploy_seconds']:g}秒；阻挡{runes['block_count']:g}"]
    if result.get('target_enemy'):
        enemy=result['target_enemy'];panel=enemy['stats']
        lines.append(f"固定候选目标：{enemy['stage_name']} · {enemy['name']}；生命参考{panel['maxHp']:.8g}、攻击参考{panel['atk']:.8g}、防御参考{panel['def']:.8g}、法抗参考{panel['magicResistance']:.8g}。未确认动态脚本及实际出场。")
    names={r['id']:r['name'] for r in resolution['relics']}
    cost=result['deployment_reference']
    sp=result['sp_reference']
    value=lambda v:'未知' if v is None else format(v,'.8g')
    damage=result['damage_reference']
    lines.append('物理结算目标防御（已计支持的减防/穿透）：'+value(damage['effective_target_defense']))
    lines.append(f"本局技力参数：消耗{value(sp['cost_parameter'])}；部署预置{value(sp['initial_parameter'])}；初次尚需补充{value(sp['initial_requirement'])}点。")
    if sp['end_return_parameter'] or sp['unresolved_end_sources']:
        lines.append(f"标称结束返技力{value(sp['end_return_parameter'])}；此后尚需补充{value(sp['recharge_requirement'])}点；实际结束/阻回及获取时钟未知。")
    lines.append('技力缺口是参数算术，不等于初动或回转秒数；不推算自动施放时刻。')
    lines.append('预计普通首次部署费用：'+('未知' if cost['estimated_cost'] is None else str(cost['estimated_cost'])))
    if cost['first_card_only']:lines.append('本费用包含仅首次有效卡片折扣；未确认本局是否已经消费，不沿用到再次部署。')
    if cost['skill_start_dp']:lines.append(f"先锋每次技能开启额外回费{cost['skill_start_dp']:g}；芬已合入单次回费，不生成回费时钟。")
    sources=list(dict.fromkeys(names.get(e.get('relic_id'),'已确认分队') for e in resolution['runes']))
    lines.append('已计符文及分队来源：'+('、'.join(sources) if sources else '没有已解析的适用属性符文'))
    ordinary=resolution['ordinary'];totals=resolution['battle_attributes']
    sources=list(dict.fromkeys(names[e['relic_id']] for e in ordinary))
    lines.append('已解析稳定普通属性来源：'+('、'.join(sources) if sources else '没有已确认的适用来源'))
    if ordinary:
        lines.append(f"普通属性加成：生命{totals['hp_pct']*100:+.8g}%；攻击{totals['attack_pct']*100:+.8g}%；防御{totals['defense_pct']*100:+.8g}%（与天赋/技能相加，不再次写回基础属性）")
        ids={e['relic_id'] for e in ordinary};context=result['environment']['relic_context']
        if 'rogue_6_relic_cargo_2' in ids:lines.append(f"悲伤的红：已确认零件{min(context['parts_count'],99):g}个参与计算。")
        if 'rogue_6_relic_artifact_7' in ids:lines.append(f"仇名录：已确认持久层数{min(context['grudge_stacks'],999):g}参与计算；不模拟击倒事件。")
        if 'rogue_6_relic_cargo_10' in ids:
            kind=result['environment']['operator_metadata'][result['preview']['operator']]['recruitment_kind']
            lines.append('同行者：当前干员'+('为应急助力招募，计入40%增益。' if kind=='emergency_hire' else '为非应急招募，本项增益为0。'))
    lines.extend(resolution['warnings'])
    if resolution['baseline_error']:lines.append('未加成对照不可测算：'+resolution['baseline_error'])
    lines.append(format_reference(result))
    lines.extend(r['name']+'：不含本局修正'+('未知' if r['base_value'] is None else format(r['base_value'],'.8g'))+
                 '；差值'+('未知' if r['delta'] is None else format(r['delta'],'.8g')) for r in result['rows'])
    lines.append('完整本局条件快照：'+json.dumps(result['environment'],ensure_ascii=False))
    return '\n'.join(lines)
