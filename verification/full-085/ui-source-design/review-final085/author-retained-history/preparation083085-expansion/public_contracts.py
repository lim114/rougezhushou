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
    if args['window_seconds']==0:assert result['total_damage']==0 and result['total_healing']==0

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
