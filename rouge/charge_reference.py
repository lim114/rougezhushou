"""Separate declared charge hit damage from an unverified collision clock."""


def finish_charge_reference(scenario, result):
    if scenario['operator'] != 'mechanist' or scenario['skill'] != 3:
        return
    count = int(scenario.get('charge_count', 0))
    if not count:
        return
    charge = next(c for c in result['components'] if c['name'] == '结构性原理冲锋')
    skill = result['estimate']['skill']
    # The estimate deliberately computes the full cast without charge. A
    # declared window count does not establish a full cast count or placement.
    subtotals = {key: skill.get(key) for key in (
        'total_damage', 'phase_damage', 'cycle_damage', 'cycle_dps',
        'window_damage', 'window_dps')}
    if 'window_seconds' in scenario:
        subtotals['window_damage'] = max(0, skill['window_damage'] - charge['total'])
    else:
        skill['window_damage'] += charge['total']
    window = skill['window_seconds']
    subtotals['window_dps'] = subtotals['window_damage'] / window if window else None
    result['known_damage_subtotals'] = subtotals
    result['charge_reference'] = {
        'hits_requested': count, 'per_hit_damage': charge['per_hit'],
        'declared_count_damage': charge['per_hit']*count, 'collision_times_seconds': None,
        'events_scheduled': False, 'scope': 'declared scenario hit count',
        'full_cast_count_verified': False,
    }
    for key in ('total_damage', 'phase_damage', 'cycle_damage', 'cycle_dps'):
        skill[key] = None
    result['complete'] = False
    result['estimate']['complete'] = False
    result['complete_definition'] = '冲锋仅为给定次数的条件伤害参考，碰撞时刻与完整施放次数未知。'
    result['estimate']['notes'].append(
        '结构性原理冲锋只计指定情景的命中次数参考；缺少碰撞时刻，'
        '不自动分配到完整单次技能、技能阶段或本轮周期。'
        '轰击及充能期普攻小计独立保留，本体0.8秒落地延迟不用于冲锋。')
