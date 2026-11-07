"""Declared per-target damage budgets from current numerical components."""
import json
from copy import deepcopy
from .damage import calculate_damage
from .healing_budget import AmountInputError, _amount
from .charge_timeline import event_seconds


class DamageBudgetInputError(ValueError):
    """The declared targets or damage events cannot form a budget."""


def damage_sources(result):
    sources=[]
    for index,part in enumerate(result.get('components',[])):
        if part.get('damage_type') not in ('physical','magic','true'): continue
        try: amount=_amount(part.get('per_hit'),'单次伤害参考')
        except AmountInputError: continue
        sources.append({'id':f'damage_{index}','name':part['name'],'damage_type':part['damage_type'],'per_hit':amount})
    if not sources and result.get('damage_type') in ('physical','magic','true'):
        try: amount=_amount(result.get('per_hit'),'单次伤害参考')
        except AmountInputError: return sources
        sources.append({'id':'legacy_damage','name':'既有单次技能伤害','damage_type':result['damage_type'],'per_hit':amount})
    return sources


def damage_budget(scenario,preview):
    return _damage_budget(scenario,preview,calculate_damage)


def _damage_budget(scenario,preview,calculator):
    """Shared declared-budget arithmetic, with a model-specific reference seam."""
    if type(preview) is not dict or set(preview)!={'targets','events'}: raise DamageBudgetInputError('需要targets和events。')
    targets=preview['targets']; events=preview['events']
    if type(targets) is not list or not 1<=len(targets)<=20: raise DamageBudgetInputError('目标需要1–20项。')
    if type(events) is not list or len(events)>1000: raise DamageBudgetInputError('事件最多1000项。')
    states={}; references={}; notes=[]
    by_mitigation = {}
    hit_amounts = {}
    for target in targets:
        if type(target) is not dict or set(target)!={'id','hp','defense','resistance'}: raise DamageBudgetInputError('每个目标需要id、hp、defense、resistance。')
        identity=target['id']
        if (type(identity) is not str or not 1<=len(identity)<=60 or identity in states or
            any(ord(c)<32 or 0xd800<=ord(c)<=0xdfff for c in identity)): raise DamageBudgetInputError('目标id需要唯一的1–60字符名称。')
        hp=_amount(target['hp'],'声明生命')
        if hp==0: raise DamageBudgetInputError('初始生命预算需要为正。')
        defense=_amount(target['defense'],'声明防御'); resistance=_amount(target['resistance'],'声明抗性',100)
        mitigation = (defense, resistance)
        if mitigation in by_mitigation:
            reference, amounts = by_mitigation[mitigation]
            references[identity] = deepcopy(reference)
        else:
            proposed = deepcopy(scenario)
            proposed.pop('target_enemy', None)
            proposed.update(enemy_defense=defense, enemy_resistance=resistance)
            calculated = calculator(proposed)
            sources = damage_sources(calculated)
            if not sources:
                raise DamageBudgetInputError('当前技能没有可用于预算的单次伤害分项。治疗与未知伤害不当作0。')
            reference = {'scenario': proposed, 'sources': sources,
                         'calculation_notes': deepcopy(calculated['estimate']['notes'])}
            amounts = {source['id']: source['per_hit'] for source in sources}
            by_mitigation[mitigation] = reference, amounts
            references[identity] = reference
            notes.extend(reference['calculation_notes'])
        hit_amounts[identity] = amounts
        states[identity]={'id':identity,'initial_hp':hp,'hp':hp,'potential_damage':0.,'effective_damage':0.,'overkill':0.,'budget_exhausted_at':None}
    parsed=[]
    for order,event in enumerate(events):
        if type(event) is not dict or set(event)!={'at_seconds','target','source'}: raise DamageBudgetInputError('事件需要at_seconds、target、source。')
        identity=event['target']; source=event['source']
        if type(identity) is not str or identity not in states: raise DamageBudgetInputError('事件需指定已声明目标。')
        source_map=hit_amounts[identity]
        if type(source) is not str or source not in source_map: raise DamageBudgetInputError('source需选择该目标下已有的单次伤害分项。')
        time=event_seconds(event['at_seconds'],'事件时刻')
        parsed.append((time,order,identity,source,source_map[source]))
    rows=[]
    for time,order,identity,source,amount in sorted(parsed):
        state=states[identity]; before=state['hp'];effective=min(before,amount)
        state['hp']-=effective;state['potential_damage']+=amount;state['effective_damage']+=effective;state['overkill']+=amount-effective
        if before>0 and state['hp']==0: state['budget_exhausted_at']=time
        rows.append({'at_seconds':time,'input_order':order,'target':identity,'source':source,
                     'hp_before':before,'per_hit':amount,'effective_damage':effective,'overkill':amount-effective,'hp_after':state['hp']})
    return {'scenario':deepcopy(scenario),'preview':deepcopy(preview),'rows':rows,'targets':list(states.values()),
            'references':references,'actual_kill_time':None,'native_hit_clock_verified':False,
            'notes':['目标生命、防御、抗性和事件均为用户声明；防御与抗性相同的目标共用单次伤害，各自扣减生命预算，固定关卡目标绑定由声明替代。',
                     '只按声明时刻排序，同刻按输入顺序；有效伤害截取至剩余生命，多余部分列为溢出。耗尽后声明事件仍保留为溢出。',
                     '生命预算耗尽时刻不是实际击杀时间。无敌、护盾、阶段转换、回血、真实获取/碰撞与原生时序未推断。',
                     '单次参考可能含现有模型的边际期望或不完整分项，不能用于击杀概率、独立抽样或全部技能输出。',
                     '不自动补齐隐藏伤害、持续首跳、首伤触发顺序或伤转疗；不会改写原计算、目标或本局。'],
            'calculation_notes':list(dict.fromkeys(notes))}


def format_damage_budget(result):
    lines=['逐目标声明伤害预算','打开时条件：'+json.dumps(result['scenario'],ensure_ascii=False),
           '声明条件：'+json.dumps(result['preview'],ensure_ascii=False)]
    for state in result['targets']:
        lines.append(f"{state['id']}：剩余预算{state['hp']:.8g}；潜在伤害{state['potential_damage']:.8g}、有效{state['effective_damage']:.8g}、溢出{state['overkill']:.8g}；预算耗尽声明时刻{state['budget_exhausted_at']}")
    lines += ['逐目标来源：'+json.dumps(result['references'],ensure_ascii=False),*result['notes'],*result['calculation_notes']]
    return '\n'.join(lines)
