"""Existing public contracts for future Qt checks; no Qt or game inference."""
import json
def require_wisdel(result,args,text,scope):
    ghosts=args['ghost_count'];casts=args['ghost_casts'] if ghosts else 0
    ref=result['wisdel_secondary_reference']
    assert type(ref['ghost_casts_requested']) is int and ref['ghost_casts_requested']==casts
    for field in ('ghost_cast_times_seconds','secondary_hit_times_seconds','explosion_expected_count'):
        assert ref[field] is None,field
    for field in ('ghost_full_cast_attribution_verified','shadow_lifecycle_verified','random_independence_verified','s1_binding_verified'):
        assert ref[field] is False,field
    if casts:
        assert ref['ghost_per_cast_damage_reference'] is not None
        assert abs(ref['ghost_declared_count_damage_reference']-casts*ref['ghost_per_cast_damage_reference'])<1e-7
        ghost=next(c for c in result['components'] if c['name']=='魂灵之影施放')
        assert ghost['hits']==0 and 'times_seconds' not in ghost
        assert '指定魂灵之影施放次数参考' in text
        assert '魂灵之影施放时刻：未知' in text
    else:
        assert ref['ghost_declared_count_damage_reference']==0
        assert '指定魂灵之影施放次数参考' not in text
    assert '好礼与余震 · 次生事件待核验' in text
    if scope in ('zero_window','zero_lifetime'):assert result['total_damage']==0

def require_incoming(result,args,text,scope,qualified=True,immune=False):
    count=args['enemy_attack_count']
    active=bool(count and qualified and not immune and scope!='zero_lifetime')
    if active:
        ref=result['neural_incoming_reference']
        assert type(ref['attacks_requested']) is int and ref['attacks_requested']==count
        assert ref['buildup_per_attack']==70
        assert ref['attack_times_seconds'] is None and ref['events_scheduled'] is False
        assert '堕梦 · 目标攻击时间待确认' in text
        assert '目标首个普通攻击时刻：未知' in text
        if scope=='zero_window':
            assert ref['affected_damage_phases']['cast'] is True
            assert ref['affected_damage_phases']['window'] is False
        else:
            assert result['total_damage'] is None
            assert result['estimate']['skill']['window_dps'] is None
    else:
        assert 'neural_incoming_reference' not in result
        assert '堕梦 · 目标攻击时间待确认' not in text
    if scope in ('zero_window','zero_lifetime'):assert result['total_damage']==0

def require_shu_periodic(result,text):
    ref=result['shu_periodic_sp_reference'];skill=result['estimate']['skill']
    assert ref['interval_seconds_parameter']==4 and ref['sp_per_pulse_parameter']==1
    for field in ('first_tick_seconds','actual_tick_times_seconds','clock_origin','reset_rule','blocked_credit_rule'):
        assert ref[field] is None,field
    for field in ('clock_verified','events_scheduled','native_attachment_verified'):
        assert ref[field] is False,field
    assert skill['sp_recovery_per_second']==1
    for field in ('initial_seconds','recharge_seconds','cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps'):
        assert skill[field] is None,field
    assert '天有四时 · 周期技力待核验' in text

def require_professions(result,args,text,plain,qualified):
    if not qualified:
        assert json.dumps(result,sort_keys=True,allow_nan=False)==json.dumps(plain,sort_keys=True,allow_nan=False)
        assert 'shu_periodic_sp_reference' not in result
        return
    stats=result['estimate']['base_stats'];base=plain['estimate']['base_stats']
    hp_factor=1.12 if args['three_professions'] else 1
    speed_bonus=12 if args['three_same_profession'] else 0
    assert abs(stats['hp']-base['hp']*hp_factor)<1e-7
    assert stats['attack_speed_reference']==base['attack_speed_reference']+speed_bonus
    assert stats['attack']==base['attack']
    if args['four_sui']:require_shu_periodic(result,text)
    else:assert 'shu_periodic_sp_reference' not in result

def require_cooperative(result,args,text,plain,scope):
    names=['本体丹增','协同丹增'] if args['cooperative'] else ['本体丹增']
    assert [c['name'] for c in result['components']]==names
    assert all(c['damage_type']=='physical' for c in result['components'])
    if args['cooperative']:
        assert abs(result['total_damage']-plain['total_damage']*2)<1e-7
        first,second=result['components']
        assert first['hits']==second['hits'] and first['per_hit']==second['per_hit']
        assert first['per_hit']==plain['components'][0]['per_hit']
    if scope in ('zero_window','zero_lifetime'):assert result['total_damage']==0

def require_sown(result,args,text,plain,scope,bb):
    if args['enemy_on_sown_tile']:
        assert result['attack']>plain['attack']
        assert result['attack_speed_reference']==plain['attack_speed_reference']+bb['e_attack_speed']
        assert result['estimate']['base_stats']==plain['estimate']['base_stats']
    if args['four_sui']:require_shu_periodic(result,text)
    else:assert 'shu_periodic_sp_reference' not in result
    if scope=='zero_window':
        assert result['total_damage']==0 and result['total_healing']==0
    elif scope=='zero_lifetime':
        assert result['total_damage']==0 and result['total_healing']>0
