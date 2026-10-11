"""Seven low-star references using proven runes and stable battle attributes."""
import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from .catalog import operator_profiles
from .supplemental_skills import (_cultivated_stats,_skill_reference,
                                  supplemental_profiles,format_reference)
from .relic_attributes import is_attribute_rune,apply_attribute_runes

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


def run_skill_reference(preview,environment):
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
    # Identity-specific metadata must never follow a different selection.
    for key in ('recruitment_kind','char_buff_ids','char_buffs_complete',
                'char_buff_absent_ids','char_buff_pending_ids'):
        if key in member:scenario[key]=deepcopy(member[key])
    from .run_modifiers import prepare_run
    from .relics import prepare
    scenario,run_resolution=prepare_run(scenario)
    scenario,relic_resolution=prepare(scenario,profile)
    resolved=scenario.get('effects',[])+scenario.get('_relic_rules',[])
    runes=[e for e in resolved if is_attribute_rune(e) and not e.get('token_only')]
    ordinary=[e for e in resolved if _ordinary_attribute(e)]
    unsupported=[e for e in resolved if not is_attribute_rune(e) and
                 not _ordinary_attribute(e) and not e.get('token_only')]
    battle_attributes={kind:sum(e['value'] for e in ordinary if e['kind']==kind)
                       for kind in ('attack_pct','hp_pct','defense_pct')}
    modified=apply_attribute_runes(stats,runes)
    result=_skill_reference(preview,modified,battle_attributes)
    try:baseline=_skill_reference(preview,stats)
    except ValueError as error:
        # A gap can be legal with an HP rune but exceed unmodified max HP.
        baseline=None;baseline_error=str(error)
    else:baseline_error=None
    base_rows={r['name']:r['value'] for r in baseline['rows']} if baseline else {}
    for row in result['rows']:
        row['base_value']=base_rows.get(row['name'])
        row['delta']=row['value']-row['base_value'] if row['value'] is not None and row['base_value'] is not None else None
    warnings=[*relic_resolution['warnings'],*run_resolution['pending']]
    if complete is not True:warnings.append('藏品持有清单尚未确认完整；只计算当前明确的条目，不能当作完整本局面板。')
    names={r['id']:r['name'] for r in relic_resolution['records']}
    for rid in dict.fromkeys(e.get('relic_id') for e in unsupported):
        warnings.append(names.get(rid,'当前来源')+'：存在本工具尚未纳入的效果；仅列已计属性和单次分项参考。')
    result['run_attributes']={key:modified[key] for key in
                             ('hp','attack','defense','resistance','attack_speed','redeploy_seconds','block_count')}
    result['environment']=environment
    result['attribute_resolution']={'runes':deepcopy(runes),'ordinary':deepcopy(ordinary),
        'battle_attributes':battle_attributes,'unsupported':deepcopy(unsupported),
        'warnings':list(dict.fromkeys(warnings)),'relics':deepcopy(relic_resolution['records']),
        'run':run_resolution,'inventory_complete':complete is True,
        'complete_for_attribute_scope':not warnings,'baseline_error':baseline_error,
        'source':deepcopy(selectors()['source'])}
    result['notes'][1]='培养按独立预览条件计算；本局已证属性符文先写回，再将已确认的稳定普通属性增益与天赋/技能加成相加。未接入效果不默认为零；不写入账户或本局。'
    result['notes'].extend(['本局修正覆盖稳定属性符文、同行者应急增益、悲伤的红零件增益及仇名录已确认持久层数；未接入回费/费用、技力、持续回复或最终伤害修正，不能生成回转和周期。',
                            '对照列为相同培养且没有本局修正的单次参考；差值不代表完整施放、周期或真实击杀。',
                            '藏品与分队取打开或更新时的快照；修改干员仅使用其自己的已确认强化，不沿用上一名干员的领取信息。'])
    return result


def format_run_reference(result):
    resolution=result['attribute_resolution'];stats=result['attributes'];runes=result['run_attributes']
    lines=['本局属性与单次技能 · '+('当前支持范围内参考' if resolution['complete_for_attribute_scope'] else '部分参考，仍有未计或未确认项'),
           f"预计常态：生命{stats['hp']:.8g}；攻击{stats['attack']:.8g}；防御{stats['defense']:.8g}；法抗{runes['resistance']:.8g}；攻速{runes['attack_speed']:.8g}（官方单位）；再部署{runes['redeploy_seconds']:g}秒；阻挡{runes['block_count']:g}"]
    names={r['id']:r['name'] for r in resolution['relics']}
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
