"""Arithmetic healing budgets for declared recipients/events; no acquisition clock."""
import json, math
from copy import deepcopy
from .damage import calculate_damage
from .charge_timeline import _seconds


def _amount(value, label, maximum=10000000):
    if type(value) not in (int,float): raise ValueError(label+'需要有限非负数值。')
    try: value = float(value)
    except OverflowError: raise ValueError(label+'超出范围。') from None
    if not math.isfinite(value) or not 0 <= value <= maximum: raise ValueError(label+'超出范围。')
    return value


def healing_sources(result):
    sources = []
    for index, component in enumerate(result.get('components',[])):
        if component.get('damage_type') == 'healing' and type(component.get('per_hit')) in (int,float):
            try: amount = _amount(component['per_hit'],'单次治疗参考')
            except ValueError: continue
            sources.append({'id':f'healing_{index}','name':component['name'],'per_heal_reference':amount})
    if not sources and type(result.get('per_heal')) in (int,float):
        try: amount = _amount(result['per_heal'],'单次治疗参考')
        except ValueError: return sources
        sources.append({'id':'legacy_heal','name':'既有单次技能治疗','per_heal_reference':amount})
    return sources


def healing_budget(scenario, preview):
    return _healing_budget(scenario,preview,calculate_damage)


def _healing_budget(scenario,preview,calculator):
    """Shared declared-budget arithmetic; the caller owns the reference model."""
    if set(preview) != {'recipients','events'}: raise ValueError('需要recipients和events。')
    reference = calculator(deepcopy(scenario)); sources = healing_sources(reference)
    if not sources: raise ValueError('当前技能没有已接入的单次治疗参考。生命回复与伤害不自动当作治疗。')
    source_map = {source['id']:source for source in sources}
    recipients = preview['recipients']
    if not isinstance(recipients,list) or not 1 <= len(recipients) <= 20: raise ValueError('友方声明需要1–20项。')
    states = {}
    for recipient in recipients:
        if not isinstance(recipient,dict) or set(recipient) != {'id','max_hp','hp'}: raise ValueError('每位友方需要id、max_hp、hp。')
        identity = recipient['id']
        if (type(identity) is not str or not 1 <= len(identity) <= 60 or
                any(ord(c)<32 or 0xd800<=ord(c)<=0xdfff for c in identity) or identity in states):
            raise ValueError('友方id需要唯一的1–60字符名称。')
        maximum = _amount(recipient['max_hp'],'最大生命'); hp = _amount(recipient['hp'],'当前生命')
        if maximum == 0 or hp > maximum: raise ValueError('最大生命必须为正，当前生命不能超过最大生命。')
        states[identity] = {'id':identity,'max_hp':maximum,'initial_hp':hp,'hp':hp,'effective_healing':0.,'overhealing':0.}
    events = preview['events']
    if not isinstance(events,list) or len(events)>1000: raise ValueError('声明事件最多1000项。')
    parsed = []
    for order,event in enumerate(events):
        if not isinstance(event,dict) or event.get('kind') not in ('heal','loss'): raise ValueError('事件kind需要heal或loss。')
        keys = {'at_seconds','recipient','kind','source'} if event['kind']=='heal' else {'at_seconds','recipient','kind','amount'}
        if set(event) != keys: raise ValueError('治疗事件需要source；生命减少事件需要amount。')
        if type(event['recipient']) is not str or event['recipient'] not in states: raise ValueError('事件需指定已声明的友方。')
        time = _seconds([event['at_seconds']],'事件时刻',1)[0]
        if event['kind']=='heal':
            if type(event['source']) is not str or event['source'] not in source_map: raise ValueError('治疗source需选用当前单次治疗来源。')
            amount = source_map[event['source']]['per_heal_reference']
        else: amount = _amount(event['amount'],'声明生命减少')
        parsed.append((time,order,deepcopy(event),amount))
    rows = []
    for time,order,event,amount in sorted(parsed):
        state = states[event['recipient']]; before = state['hp']
        effective = min(amount,state['max_hp']-before) if event['kind']=='heal' else 0.
        overheal = amount-effective if event['kind']=='heal' else 0.
        state['hp'] = before+effective if event['kind']=='heal' else max(0,before-amount)
        state['effective_healing'] += effective; state['overhealing'] += overheal
        rows.append({'at_seconds':time,'input_order':order,'recipient':event['recipient'],'kind':event['kind'],
            'source':event.get('source'),'hp_before':before,'amount_reference':amount,'effective_healing':effective,
            'overhealing':overheal,'hp_after':state['hp']})
    return {'scenario':deepcopy(scenario),'preview':deepcopy(preview),'sources':sources,'rows':rows,
        'recipients':list(states.values()),'effective_healing':sum(s['effective_healing'] for s in states.values()),
        'overhealing':sum(s['overhealing'] for s in states.values()),'actual_acquisition_verified':False,
        'notes':['每次治疗使用打开时的单次治疗参数；友方生命与事件均由用户声明，不自动读取友方或生成治疗时钟。',
                 '预算按生命缺口截取有效治疗；过量部分分列，生命减少截取至0。该算术不判断存活、倒地、复活或真实受疗资格。',
                 '事件按秒数排序，同刻按输入顺序；这只是声明的预算顺序，不证明游戏的同帧结算。',
                 '附近范围、生命阈值、多目标人数、充能及治疗快照仍按实际机制待核验；声明事件不授权技能获取。',
                 '生命回复、伤转疗的动态伤害来源和多来源叠加不自动加入预算；不会改写本局或原治疗估算。'],
        'calculation_notes':deepcopy(reference['estimate']['notes'])}


def format_healing_budget(result):
    lines = ['逐友方治疗预算（局外声明）','原计算条件：'+json.dumps(result['scenario'],ensure_ascii=False,sort_keys=True),
             '用户条件：'+json.dumps(result['preview'],ensure_ascii=False),
             '可选单次治疗来源：'+json.dumps(result['sources'],ensure_ascii=False),
             f"条件有效治疗{result['effective_healing']:.8g}；条件过量治疗{result['overhealing']:.8g}"]
    for state in result['recipients']:
        lines.append(f"{state['id']}：最终预算生命{state['hp']:g}/{state['max_hp']:g}；有效治疗{state['effective_healing']:g}、过量{state['overhealing']:g}、剩余缺口{state['max_hp']-state['hp']:g}")
    return '\n'.join([*lines,*result['notes'],*result['calculation_notes']])
