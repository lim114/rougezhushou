"""Current source-backed planned assertions; no actual Qt/Wine certification."""
import json

def canonical085(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False)

def require_warning_order085(result,args,text,technical):
    groups=('heal_scale','received_regeneration')
    selected=args['relic_ids']
    conflicting=len(set(selected)&{'rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83'})>=2
    expected=['组合 '+group+' 的叠加规则尚未核验，未套用该组合。'for group in groups]if conflicting else []
    actual=[w for w in result['warnings']if w.startswith('组合 ')]
    assert actual==expected
    records=result['relic_resolution']['records']
    assert [r['id']for r in records]==selected
    if conflicting:
        assert not result['relic_resolution']['complete']
        assert not any(r['kind']in ('healing_factor','regeneration_factor')for r in result['relic_resolution']['rules'])
        for record in records:
            if record['id']in ('rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83'):
                assert record['pending']==['组合叠加规则待核验:'+group for group in groups]
                assert record['applied']==[] and record['status']=='incomplete'
        if technical:
            assert text.index(expected[0])<text.index(expected[1])
        else:
            rendered='组合 未核验配置（原文见技术资料） 的叠加规则尚未核验，未套用该组合。'
            assert text.count(rendered)==2
            assert '组合 heal_scale 'not in text and '组合 received_regeneration 'not in text
    if 'rogue_6_relic_legacy_5'in selected:
        other=next(r for r in records if r['id']=='rogue_6_relic_legacy_5')
        assert other['status']=='applied' and other['applied']
    # Unknown stacking is excluded irrespective of zero observation; this
    # never establishes real target/recipient state or a composition formula.
    if args['window_seconds']==0:
        assert result['total_damage']==0
        if args['operator']=='mechanist'and args['skill']==3:
            # Legacy _skill_damage emits a damage-only dictionary; its estimate
            # independently carries zero direct healing without adding a field.
            assert 'total_healing'not in result
            assert result['estimate']['skill']['window_healing']==0
        else:assert result['total_healing']==0

def require_susuro_checkbox085(result,args,text,plain,factor):
    assert type(args['low_cost_healing_target'])is bool
    assert result['total_damage']==0
    assert result['timing']==plain['timing']
    a,b=plain['estimate']['skill'],result['estimate']['skill']
    for key in ('mode','initial_seconds','recharge_seconds','cycle_seconds','duration_seconds',
                'sp_recovery_per_second','hit_counts'):
        assert b[key]==a[key]
    effective=factor if args['low_cost_healing_target']else 1.0
    for key in ('total_healing','phase_healing','window_healing','window_hps','cycle_healing','cycle_hps'):
        if a[key]is None:assert b[key]is None
        else:assert abs(b[key]-a[key]*effective)<1e-7
    assert abs(result['total_healing']-plain['total_healing']*effective)<1e-7
    if args['healing_targets']==0 or args['window_seconds']==0:assert result['total_healing']==0
    if args['skill']==2 and args['casts_used']==1:
        assert b['cycle_seconds']is None and b['cycle_healing']is None
    if args.get('timing',{}).get('target_disappears_seconds')==0 or args.get('timing',{}).get('target_windows')==[]:
        assert '真实友方获取时钟未核验'in text

"""Provisional sourced contracts; no API execution or native validation proof."""
def require_neural_checkbox085(result,args,text):
    hidden=args['operator']=='char_4204_mantra'and args['skill']==3
    if hidden:
        assert not {'enemy_is_boss','enemy_in_neural_break','initial_neural_buildup','enemy_buildup_resistance'}&args.keys()
    else:
        assert type(args['enemy_is_boss'])is bool and type(args['enemy_in_neural_break'])is bool
        assert type(args['initial_neural_buildup'])is int
    if 'rogue_6_relic_fight_22'in args['relic_ids']:
        ref=result['neural_relic_reference']
        assert ref['periodic_damage_scheduled']is False
        assert ref['preexisting_break_assumed']is args.get('enemy_in_neural_break',False)
        section=next(s for s in result['report']['sections']if s['id']=='river_neural')
        assert next(m['value']for m in section['metrics']if m['key']=='first_tick')is None
        assert '实际首跳时刻和每跳麻痹条件尚未确认'in text
    else:assert 'neural_relic_reference'not in result
    if args['operator']=='char_1042_phatm2':
        assert 'neural_bait_reference'not in result and 'neural_incoming_reference'not in result
    else:
        ref=result['external_event_reference']
        assert ref['kind']=='mantra_events' and ref['actual_event_times_seconds']is None
    target=args.get('target_enemy')
    if target:
        enemy=result['run_resolution']['enemy']
        assert enemy['id']==target['enemy_id'] and enemy['level']==target['level']
        assert enemy['level_type']=='BOSS'
        assert args['initial_neural_buildup']==1500
    if args['window_seconds']==0:
        assert result['total_damage']==0 and result['total_healing']==0

def require_repeat_checkbox085(result,args,text,plain,attack_bonus):
    healing=result['haruka_healing_reference']
    for ref in (healing,healing['window_reference']):
        assert ref['actual_target_count']is None and ref['actual_acquisition_times_seconds']is None
        assert ref['native_composition_verified']is False and ref['native_attachment_verified']is False
    events=result['external_event_reference']
    assert events['kind']=='haruka_bubbles' and events['actual_event_times_seconds']is None
    if args['skill']==2:
        assert type(args['haruka_repeat'])is bool
        skill=result['estimate']['skill']
        assert skill['mode']==('infinite'if args['haruka_repeat']else 'timed')
        delta=plain['estimate']['base_stats']['attack']*attack_bonus if args['haruka_repeat']else 0.0
        assert abs(result['attack']-plain['attack']-delta)<1e-7
        assert abs(skill['skill_attack']-plain['estimate']['skill']['skill_attack']-delta)<1e-7
        assert result['estimate']['base_stats']==plain['estimate']['base_stats']
        if args['haruka_repeat']:
            assert skill['duration_seconds']is None and skill['cycle_seconds']is None
            assert skill['cycle_damage']is None and skill['cycle_healing']is None
    else:assert 'haruka_repeat'not in args
    if args['elite']<2:
        for c in result['components']:
            if c['name']in ('扶摇花火','浮泡治疗衍生伤害'):
                assert c['hits']==0 and c['total']==0
    if args['healing_targets']==0 or args['window_seconds']==0:assert result['total_healing']==0
    assert '实际友方获取'in text

def require_nearby_checkbox085(result,args,text,plain,talent_bonus):
    assert type(args['near_previous_deployment'])is bool
    factor=talent_bonus if args['near_previous_deployment']else 0.0
    base=plain['estimate']['base_stats']['attack']
    assert abs(result['estimate']['base_stats']['attack']-base*(1+factor))<1e-7
    assert abs(result['attack']-plain['attack']-base*factor)<1e-7
    assert abs(result['estimate']['skill']['skill_attack']-plain['estimate']['skill']['skill_attack']-base*factor)<1e-7
    if args['elite']==0:
        assert factor==0 and canonical085(result)==canonical085(plain)
    assert result['orchid_redeploy_reference']==plain['orchid_redeploy_reference']
    redeploy=result['orchid_redeploy_reference']
    assert redeploy['events_scheduled']is False and redeploy['native_attachment_verified']is False
    assert redeploy['actual_retreat_seconds']is None and redeploy['actual_next_deployment_seconds']is None
    cast=result['unbound_cast_reference']
    assert cast['kind']=='orchid_arrows' and cast['collision_clock_verified']is False
    assert cast['actual_hit_times_seconds']is None and cast['actual_end_seconds']is None
    assert result['estimate']['skill']['cycle_seconds']is None
    if args['window_seconds']==0 or args.get('timing',{}).get('target_disappears_seconds')==0:
        assert result['total_damage']==0
    else:assert result['total_damage']is None
    assert result['total_healing']==0
    assert '实际撤退、倒下和再次部署的时刻'in text
