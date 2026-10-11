"""Declared breaks and collisions remain separate from ammunition/end clocks."""
import json
from copy import deepcopy
from .charge_timeline import _seconds
from .damage import calculate_damage


def compare_shield_windows(scenario, preview):
    if scenario.get('operator') != 'mechanist' or type(scenario.get('skill')) is not int or scenario['skill'] != 2:
        raise ValueError('破屏时刻对照仅用于机械师S2。')
    if set(preview) != {'events','windows_seconds'}: raise ValueError('需要events和windows_seconds。')
    events = preview['events']
    if not isinstance(events,list) or len(events)>100: raise ValueError('破屏声明最多100项。')
    validated = []
    for event in events:
        if not isinstance(event,dict) or set(event) != {'source','break_seconds','hit_seconds'}:
            raise ValueError('每项需要source、break_seconds、hit_seconds；未命中可将hit_seconds设为null。')
        if type(event['source']) is not str or event['source'] not in ('owner','structure'):
            raise ValueError('source需要owner或structure。')
        broke = _seconds([event['break_seconds']],'破屏时刻',1)[0]
        hit = None if event['hit_seconds'] is None else _seconds([event['hit_seconds']],'爆炸命中时刻',1)[0]
        if hit is not None and hit < broke: raise ValueError('声明命中不能早于本次破屏。')
        validated.append({'source':event['source'],'break_seconds':broke,'hit_seconds':hit})
    windows = _seconds(preview['windows_seconds'],'观察窗口',12)
    if not windows: raise ValueError('至少填写一个观察窗口。')
    base = deepcopy(scenario); base.pop('window_seconds',None); base['shield_break_count'] = 0
    reference = calculate_damage(base); per_hit = reference['shield_break_reference']['per_hit_damage_reference']
    rows = []
    for window in windows:
        modeled = calculate_damage({**deepcopy(base),'window_seconds':window})
        included = [e for e in validated if e['hit_seconds'] is not None and e['hit_seconds'] < window]
        owner = sum(e['source']=='owner' for e in included); structure = len(included)-owner
        ordinary = modeled['estimate']['skill']['window_damage']
        explosion = per_hit*len(included)
        subtotal = ordinary + explosion if ordinary is not None else None
        rows.append({'window_seconds':window,'owner_hits':owner,'structure_hits':structure,
            'declared_breaks':sum(e['break_seconds']<window for e in validated),
            'explosion_damage_reference':explosion,'ordinary_damage_reference':ordinary,
            'conditional_damage_subtotal':subtotal,'conditional_dps':subtotal/window if subtotal is not None and window else None})
    return {'scenario':deepcopy(scenario),'events':validated,'rows':rows,'per_hit_damage_reference':per_hit,
        'nominal_ammunition_parameter':reference['shield_break_reference']['nominal_ammunition_parameter'],
        'actual_ammunition_consumption':None,'actual_end_seconds':None,'full_cast_damage':None,'cycle_damage':None,
        'notes':['破屏来源与破屏/命中时刻均为用户声明，0秒为技能开启；null表示此事件未声明命中当前目标。',
                 '按原始秒数计入[0,窗口)，同刻多次保留；破屏计数和命中计数分开。',
                 '本体和结构体均沿用现有固定技能攻击与减伤的单次爆炸条件参考，不证明独立攻击快照或实际伤害。',
                 '普通攻击仅沿用既有时序与手动结束参考；不把供靶参数自动用作独立爆炸碰撞时钟。',
                 '原表弹药参数不限制声明事件数量；破屏与双方耗弹对应、实际结束、完整施放及周期仍未知。',
                 '此工具替代原合计破屏次数做局外事件条件对照，原计算、账号及本局不变。'],
        'calculation_notes':deepcopy(reference['estimate']['notes'])}


def format_shield_windows(result):
    lines = ['机械师S2 · 破屏与爆炸窗口对照', '原计算条件：'+json.dumps(result['scenario'],ensure_ascii=False,sort_keys=True),
             '用户事件：'+json.dumps(result['events'],ensure_ascii=False),
             f"单次条件爆炸{result['per_hit_damage_reference']:.8g}；原表弹药参数{result['nominal_ammunition_parameter']:.8g}"]
    for row in result['rows']:
        lines.append(f"{row['window_seconds']:g}秒：破屏{row['declared_breaks']}；本体命中{row['owner_hits']}、结构命中{row['structure_hits']}；爆炸条件伤害{row['explosion_damage_reference']:.8g}；普通攻击参考{row['ordinary_damage_reference']}；条件小计{row['conditional_damage_subtotal']}")
    return '\n'.join([*lines,*result['notes'],*result['calculation_notes']])
