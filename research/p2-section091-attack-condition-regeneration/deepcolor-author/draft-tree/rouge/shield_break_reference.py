"""Separate a declared shield-break total from unknown event and end clocks."""
from .catalog import catalog
from .timing import AttackTimeline, finite


NAME = '协防术式破屏爆炸条件参考'


def finish_shield_break_reference(scenario, result):
    if scenario['operator'] != 'mechanist' or scenario['skill'] != 2:
        return
    # The legacy evaluator validated float-to-int on its local scenario copy.
    count = int(float(scenario.get('shield_break_count', 0)))
    per_hit = result['per_hit']
    declared = count * per_hit
    lifetime = scenario.get('timing', {}).get('target_disappears_seconds')
    alive = lifetime is None or finite(lifetime, '目标生命周期', 3600) != 0
    skill = result['estimate']['skill']
    empty = 'window_seconds' in scenario and skill['window_seconds'] == 0
    pending = bool(count and alive)
    window_pending = pending and not empty
    source = catalog()['operators']['mechanist']['skills'][1]['levels'][scenario.get('skill_rank', 10)-1]
    # These legacy estimates already contain the optional, explicitly timed
    # ordinary-attack subtotal. Remove only the unplaced shield amount; do not
    # generate an ordinary attack or locate a break inside a short window.
    if count:
        excluded = per_hit * result['hits']
        def ordinary(key):
            value = skill.get(key)
            if value is None:return None
            return max(0, value - excluded) if alive else 0
        subtotal = {key: ordinary(key) for key in
            ('total_damage', 'phase_damage', 'cycle_damage')}
        subtotal['window_damage'] = ordinary('window_damage')
        if subtotal['window_damage'] is None:
            subtotal['window_damage'] = 0
        cycle = skill.get('cycle_seconds')
        window = skill.get('window_seconds')
        subtotal['cycle_dps'] = subtotal['cycle_damage'] / cycle if cycle and subtotal['cycle_damage'] is not None else None
        subtotal['window_dps'] = subtotal['window_damage'] / window if window else None
        result['known_damage_subtotals'] = subtotal
        for key in ('total_damage', 'phase_damage', 'cycle_damage', 'cycle_dps'):
            skill[key] = None if pending else subtotal[key]
        result['total_damage'] = None if window_pending else subtotal['window_damage']
        skill['window_damage'] = result['total_damage']
        skill['window_dps'] = None if window_pending else subtotal['window_dps']
    component = {'name': NAME, 'damage_type': 'magic', 'hits': count if window_pending else 0,
        'per_hit': per_hit, 'total': declared if window_pending else 0,
        'timing_reference': 'declared whole-skill shield-break amount; actual break/collision clock unverified'}
    if window_pending:
        component['actual_total'] = None
    if count:
        result['components'] = [component]
    result['shield_break_reference'] = {
        'hits_requested': count, 'per_hit_damage_reference': per_hit,
        'declared_count_damage_reference': declared,
        'nominal_ammunition_parameter': source['values']['trigger_time'],
        'manual_duration_parameter_seconds': scenario.get('skill_duration_seconds'),
        'source_possible': {'cast': pending, 'window': window_pending},
        'actual_break_times_seconds': None, 'actual_collision_times_seconds': None,
        'actual_end_seconds': None, 'actual_ammunition_consumption_times_seconds': None,
        'owner_and_structure_count_mapping_verified': False,
        'events_scheduled': False, 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'}
    result.setdefault('timing', AttackTimeline(scenario).output())['phase_clock_unbound'] = True
    result['timing']['resource_and_damage_shared_clock'] = False
    result['scope'] = result['estimate']['scenario_scope'] = (
        '声明总破屏次数的法术爆炸条件参考，事件时刻未知；已计普通攻击仅为手动结束参数参考。')
    result['complete'] = result['estimate']['complete'] = False
    result['estimate']['notes'].append(
        '协防术式总破屏次数只列命中当前敌人的条件伤害；破屏/爆炸时刻、双方耗弹对应和实际结束未核验，'
        '未自动放入观察窗口、技能阶段或周期。指定结束时间只保留手动条件参数和既有普通攻击小计，不能定位破屏事件。')
