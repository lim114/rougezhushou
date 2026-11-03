"""Restricted caster S1 interval references without an invented native clock."""
from copy import deepcopy


def source_state(scenario):
    if (scenario['operator'] != 'char_002_amiya' or scenario['skill'] != 1 or
            scenario.get('timing_mode', 'frames') != 'continuous'):
        return None
    options = scenario.get('timing', {})
    lifetime = options.get('target_disappears_seconds')
    lifetime = float(lifetime) if lifetime is not None else None
    # Keep the established numeric life0 path unchanged. Its scope is already
    # excluded by the existing ordinary attack and natural-SP reference model.
    if lifetime == 0 and options.get('target_disappears_seconds') == 0:
        return None
    if lifetime == 0 or options.get('target_windows') == []:
        return 'empty'
    if (lifetime is not None and lifetime > 0) or options.get('target_windows'):
        return 'unbound'
    return None


def preserve_plan(scenario, components, duration):
    state = source_state(scenario)
    if state is None:
        return None
    excluded = state == 'empty'
    damage = [c for c in components if c['damage_type'] not in ('healing', 'regeneration', 'buildup')]
    if excluded:
        for component in damage:
            component.update(hits=0, total=0, times_seconds=[])
            if 'event_amounts' in component:
                component['event_amounts'] = []
            component.pop('actual_total', None)
    reference = deepcopy(damage)
    possible = not excluded and duration > 0
    for component in damage:
        component.pop('times_seconds', None)
        component['timing_reference'] = 'continuous interval conditional reference; native acquisition/release/impact unverified'
        if possible:
            # An interval-reference count of zero does not exclude an earlier
            # real first hit in a positive observation window.
            component['actual_total'] = None
        else:
            component.update(hits=0, total=0)
            component.pop('actual_total', None)
    return {'enemy_source_excluded': excluded, 'source_possible': possible,
            'observation_seconds': duration, 'conditional_components': reference}


def attach_result(result, scenario, full, shown, normal, duration, cycle, *, rate, cost, attack_credit):
    from .timing import phase_totals
    from .uncertain_sources import mask_pending_damage
    reference = full.get('amiya_continuous_reference')
    if reference is None:
        return
    skill = result['estimate']['skill']
    clock_keys = ('initial_seconds', 'duration_seconds', 'recharge_seconds', 'cycle_seconds',
                  'total_damage', 'phase_damage', 'cycle_damage', 'cycle_dps',
                  'cycle_healing', 'cycle_hps')
    clock = {key: skill[key] for key in clock_keys}
    # Actual components have no synthesized timestamps. Preserve the old
    # half-open phase arithmetic using only the separately retained reference.
    clock['phase_damage'] = phase_totals(reference['conditional_components'], duration)[0] if duration is not None else None
    observed = shown['amiya_continuous_reference']
    clock.update(window_damage=result['total_damage'], window_dps=skill['window_dps'])
    components = reference['conditional_components']
    result['amiya_continuous_reference'] = {
        'operator_id': 'char_002_amiya', 'skill_number': 1,
        'enemy_source_excluded': reference['enemy_source_excluded'],
        'declared_target_lifetime_seconds': scenario.get('timing', {}).get('target_disappears_seconds'),
        'declared_target_windows_seconds': deepcopy(scenario.get('timing', {}).get('target_windows')),
        'per_hit_damage_reference': components[0]['per_hit'] if components else None,
        'parameter_clock_reference': clock,
        'cast_reference': reference, 'window_reference': observed,
        'recharge_reference': normal.get('amiya_continuous_reference') if normal else None,
        'natural_sp_rate_parameter': rate, 'required_sp_parameter': cost,
        'natural_only_recharge_seconds_reference': cost / rate if rate > 0 else None,
        'attack_sp_per_attack_parameter': attack_credit,
        'attack_sp_enabled_in_reference': bool(scenario.get('continuous_attacks', True)),
        'actual_acquisition_times_seconds': None, 'actual_impact_times_seconds': None,
        'actual_recharge_seconds': None, 'actual_cycle_seconds': None,
        'native_clock_binding_verified': False,
        'initial_scope': 'existing independent pre-cast reference unchanged',
        'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
        'source_selectors': ['character_table.char_002_amiya.skills[0].skillId',
                             'character_table.char_002_amiya.talents[0].candidates',
                             'character_table.char_002_amiya.phases[2].attributesKeyFrames[0].data.baseAttackTime',
                             'skill_table.skcom_magic_rage[3].levels[*]'],
    }
    mask_pending_damage(result, full, shown, normal, duration, cycle)
    for key in ('recharge_seconds', 'cycle_seconds', 'cycle_damage', 'cycle_dps',
                'cycle_healing', 'cycle_hps'):
        skill[key] = None
    if 'known_damage_subtotals' in result:
        result['known_damage_subtotals']['cycle_damage'] = None
        result['known_damage_subtotals']['cycle_dps'] = None
    result['timing']['phase_clock_unbound'] = True
    result['timing']['resource_and_damage_shared_clock'] = False
    result['complete'] = result['estimate']['complete'] = False
    scope = '术师阿米娅S1受限continuous情景；旧连续供靶条件参数与当前有限约束的实际伤害/回转分列。'
    result['scope'] = result['estimate']['scenario_scope'] = scope
    conditional_notes = {
        '单目标持续存活、供靶/满额受疗情景；难度、分队、特训和条件藏品尚未完整套用。':
            '旧连续供靶条件参考假设单目标持续存活；当前有限生命周期/范围的实际伤害和回转另列未知或数学排除结果。难度、分队、特训和条件藏品尚未完整套用。',
        '连续供靶、按完整攻击间隔估算；未模拟首击前后摇、帧取整及移动。':
            '旧连续供靶条件参考按完整攻击间隔估算；不证明当前受限情景的实际首击、命中或回技力时刻。',
        '术师阿米娅自然充能与攻击额外技力按事件共同计算；精神爆发后晕眩期间停止攻击，技力自然回复继续。未额外假设击倒回技力。':
            '术师阿米娅旧条件参考中自然充能与攻击额外技力按合成间隔事件计算；实际postcast获取、命中和回技力时钟未知，未额外假设击倒回技力。',
    }
    result['estimate']['notes'] = [conditional_notes.get(note, note) for note in result['estimate']['notes']]
    result['estimate']['notes'].append(
        '术师阿米娅S1受限continuous情景只保留旧间隔条件参考；有限正生命周期/范围的实际获取、命中及攻击回技力时钟未知，未按minlife或均匀比例裁剪。'
        '空范围只排除当前敌人的数学来源；自然充能量保留独立参数参考，不证明游戏没有其它目标或来源。施放后约束不重写施放前初动约定，实际回转和周期未知。')
