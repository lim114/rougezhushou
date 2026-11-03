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
    if plain['total_healing'] is None:
        assert result['total_healing'] is None
        for source_result in (plain,result):
            ref=source_result['susuro_module_healing_reference']
            assert ref['evidence']=='research/p2-susuro-healing-composition-current/receipt.json' and ref['module_id']==args['module_id']=='uniequip_002_susuro' and ref['module_level']==args['module_level'] and ref['res_key']=='susuro_equip_1_'+str(args['module_level'])+'_p1'
            assert args.get('healing_target_hp_ratio') is None and ref['recipient_hp_ratio'] is None and ref['qualified'] is None and ref['factor'] is None
            assert ref['compiled_path_verified'] is True and ref['current_hotfix_equivalence_proven'] is False
            assert ref['actual_recipient_ratio_verified'] is False and ref['actual_recipient_acquisition_verified'] is False and ref['actual_hp_trajectory_verified'] is False
        for key in ('total_healing','phase_healing','window_healing','window_hps','cycle_healing','cycle_hps'):
            known_plain=plain['known_healing_subtotals'][key]
            known_result=result['known_healing_subtotals'][key]
            if known_plain is None:assert known_result is None
            else:assert abs(known_result-known_plain*effective)<1e-7
    else:
        assert abs(result['total_healing']-plain['total_healing']*effective)<1e-7
    if args['healing_targets']==0 or args['window_seconds']==0:assert result['total_healing']==0
    if args['skill']==2 and args['casts_used']==1:
        assert b['cycle_seconds']is None and b['cycle_healing']is None
    if args.get('timing',{}).get('target_disappears_seconds')==0 or args.get('timing',{}).get('target_windows')==[]:
        assert '真实友方获取时钟未核验'in text
