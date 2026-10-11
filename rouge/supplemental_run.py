"""Seven low-star skill references using resolved, proven attribute runes."""
import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from .catalog import operator_profiles
from .supplemental_skills import (_cultivated_stats,_skill_reference,
                                  supplemental_profiles,format_reference)
from .relic_attributes import is_attribute_rune,apply_attribute_runes

ENVIRONMENT_KEYS={'relic_ids','run_config','relic_context','inventory_status','operator_metadata'}


@lru_cache(maxsize=1)
def selectors():
    return json.loads((Path(__file__).parent/'data/supplemental-run-selectors.json').read_text(encoding='utf-8'))


def run_skill_reference(preview,environment):
    """A frozen raw run input, never a previously prepared damage scenario.

    Only attribute runes are consumed. All other resolved rules remain explicit
    gaps, including ordinary battle attributes, deployment costs and SP rules.
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
    unsupported=[e for e in resolved if not is_attribute_rune(e) and not e.get('token_only')]
    modified=apply_attribute_runes(stats,runes)
    result=_skill_reference(preview,modified)
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
        warnings.append(names.get(rid,'当前来源')+'：存在属性符文以外的效果，本工具尚未纳入；仅列已计属性和单次分项参考。')
    result['run_attributes']={key:modified[key] for key in
                             ('hp','attack','defense','resistance','attack_speed','redeploy_seconds','block_count')}
    result['environment']=environment
    result['attribute_resolution']={'runes':deepcopy(runes),'unsupported':deepcopy(unsupported),
        'warnings':list(dict.fromkeys(warnings)),'relics':deepcopy(relic_resolution['records']),
        'run':run_resolution,'inventory_complete':complete is True,
        'complete_for_attribute_scope':not warnings,'baseline_error':baseline_error,
        'source':deepcopy(selectors()['source'])}
    result['notes'][1]='培养按独立预览条件计算；本局已证属性符文先写回，再计算当前已接入的天赋/技能。未接入效果不默认为零；不写入账户或本局。'
    result['notes'].extend(['本局修正只覆盖稳定属性符文；未接入普通战斗增益、回费/费用修正、技力、持续回复或最终伤害修正，不能生成回转和周期。',
                            '对照列为相同培养且没有本局修正的单次参考；差值不代表完整施放、周期或真实击杀。',
                            '藏品与分队取打开或更新时的快照；修改干员仅使用其自己的已确认强化，不沿用上一名干员的领取信息。'])
    return result


def format_run_reference(result):
    resolution=result['attribute_resolution'];stats=result['attributes'];runes=result['run_attributes']
    lines=['本局属性符文 · '+('当前支持范围内参考' if resolution['complete_for_attribute_scope'] else '部分参考，仍有未计或未确认项'),
           f"预计常态：生命{stats['hp']:.8g}；攻击{stats['attack']:.8g}；防御{stats['defense']:.8g}；法抗{runes['resistance']:.8g}；攻速{runes['attack_speed']:.8g}（官方单位）；再部署{runes['redeploy_seconds']:g}秒；阻挡{runes['block_count']:g}"]
    names={r['id']:r['name'] for r in resolution['relics']}
    sources=list(dict.fromkeys(names.get(e.get('relic_id'),'已确认分队') for e in resolution['runes']))
    lines.append('已计属性来源：'+('、'.join(sources) if sources else '没有已解析的适用属性符文'))
    lines.extend(resolution['warnings'])
    if resolution['baseline_error']:lines.append('未加成对照不可测算：'+resolution['baseline_error'])
    lines.append(format_reference(result))
    lines.extend(r['name']+'：不含本局修正'+('未知' if r['base_value'] is None else format(r['base_value'],'.8g'))+
                 '；差值'+('未知' if r['delta'] is None else format(r['delta'],'.8g')) for r in result['rows'])
    lines.append('完整本局条件快照：'+json.dumps(result['environment'],ensure_ascii=False))
    return '\n'.join(lines)
