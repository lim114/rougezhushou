def require_warning_order085(result,args,text,technical):
    """Three exact proved parameter families; actual attachment/ticks unknown."""
    import hashlib,json,math
    from rouge.relic_healing_factors import healing_factor,regeneration_factor
    evidence_name='research/p2-flower-healing-composition-current/receipt.json'
    evidence_path=ROOT/evidence_name
    assert hashlib.sha256(evidence_path.read_bytes()).hexdigest()=='42c5cbd5f37c0ac3376b4f6946cd8346108b4c86f7084868994050911af610b7'
    evidence=json.loads(evidence_path.read_bytes())
    assert evidence['source_ids']==['rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83']
    for name,digest in evidence['artifacts_sha256'].items():
        assert hashlib.sha256((evidence_path.parent/name).read_bytes()).hexdigest()==digest
    assert evidence['game_dll_executed'] is False and evidence['process_memory_read'] is False
    assert evidence['current_hotfix_equivalence_proven'] is False
    assert 'No actual buff attachment, first recovery tick, refresh/cover/lifetime or event count inferred.' in evidence['source_scope_limitations']
    selected=args['relic_ids']
    resolution=result['relic_resolution']
    records=resolution['records']
    assert [r['id']for r in records]==selected
    assert resolution['calculation_scope']=='offline_stable_effects'
    assert resolution['combat_effects_reference_only'] is True
    assert resolution.get('actual_buff_attachment_verified') is not True
    assert resolution.get('actual_ticks_verified') is not True
    actual=[w for w in result['warnings']if w.startswith('组合 ')]
    assert actual==[]
    assert '组合 heal_scale 'not in text and '组合 received_regeneration 'not in text
    assert '组合 未核验配置（原文见技术资料） 的叠加规则尚未核验，未套用该组合。' not in text
    factors={'rogue_6_relic_legacy_81':1.2,'rogue_6_relic_legacy_82':1.3,'rogue_6_relic_legacy_83':1.4}
    flower_ids=[rid for rid in selected if rid in factors]
    for record in records:
        if record['id'] not in factors:continue
        assert record['pending']==[] and record['missing_conditions']==[]
        assert record['status']=='applied'
        proved=[r for r in record['applied']if r['kind']in ('healing_factor','regeneration_factor')]
        assert sorted(r['source_buff_index']for r in proved)==[0,1,2]
        for rule in proved:
            assert rule['relic_id']==record['id'] and rule['_verified_rule'] is True
            assert rule['source_buff_key']=='global_buff_normal' and type(rule['source_buff_index']) is int
            assert rule['value']==factors[record['id']] and type(rule['value']) is float
            assert rule['composition_evidence']==evidence_name
            assert rule['stacking']=='native_independent_instances'
            if rule['source_buff_index']==0:
                assert rule['kind']=='healing_factor' and rule['group']=='heal_scale'
                assert rule['healing_composition']=='independent_modifier_product'
            else:
                assert rule['kind']=='regeneration_factor' and rule['group']=='received_regeneration'
                assert rule['regeneration_composition']=='direct_multiplier_sum'
    healing=[r for r in resolution['rules']if r['kind']=='healing_factor']
    regen=[r for r in resolution['rules']if r['kind']=='regeneration_factor']
    assert len(healing)==len(flower_ids) and len(regen)==2*len(flower_ids)
    assert {r['relic_id']for r in healing}==set(flower_ids)
    assert {(r['relic_id'],r['source_buff_index'])for r in healing+regen}=={(rid,index)for rid in flower_ids for index in (0,1,2)}
    assert all(r in next(record for record in records if record['id']==r['relic_id'])['applied']for r in healing+regen)
    # Literal independent product/sum oracles, not a reused implementation fit.
    oracles={(): (1.,1.),('rogue_6_relic_legacy_81',):(1.2,1.2),
        ('rogue_6_relic_legacy_82',):(1.3,1.3),('rogue_6_relic_legacy_83',):(1.4,1.4),
        ('rogue_6_relic_legacy_81','rogue_6_relic_legacy_82'):(1.56,1.5),
        ('rogue_6_relic_legacy_81','rogue_6_relic_legacy_83'):(1.68,1.6),
        ('rogue_6_relic_legacy_82','rogue_6_relic_legacy_83'):(1.82,1.7),
        ('rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83'):(2.184,1.9)}
    expected_heal,expected_regen=oracles[tuple(sorted(flower_ids))]
    assert math.isclose(healing_factor(healing),expected_heal,rel_tol=1e-12,abs_tol=1e-12)
    assert math.isclose(regeneration_factor(regen),expected_regen,rel_tol=1e-12,abs_tol=1e-12)
    assert math.isclose(result['relic_regeneration_multiplier'],expected_regen,rel_tol=1e-12,abs_tol=1e-12)
    if 'rogue_6_relic_legacy_5'in selected:
        other=next(r for r in records if r['id']=='rogue_6_relic_legacy_5')
        assert other['status']=='applied' and other['applied']
    # No parameter composition establishes actual recipients or a tick clock.
    if args['window_seconds']==0:
        assert result['total_damage']==0
        if args['operator']=='mechanist'and args['skill']==3:
            assert 'total_healing'not in result
            assert result['estimate']['skill']['window_healing']==0
        else:assert result['total_healing']==0
