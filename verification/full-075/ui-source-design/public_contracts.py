"""Shared public-output assertions; API use does not prove actual Qt execution."""
import json

def canonical075(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False)

def require_squad075(result,args,text,record):
    resolution=result['run_resolution']
    assert resolution['squad']['id']==record['id']
    assert resolution['squad']['effect_verified'] is args['run_config']['squad']['effect_verified']
    section_ids=[s['id'] for s in result['report']['sections']]
    if record['bandLevel']!=1:
        assert 'squad_unlock_reference' not in resolution
        assert 'squad_unlock_reference' not in section_ids
        return
    ref=resolution['squad_unlock_reference']
    assert ref['squad_id']==record['id'] and ref['base_squad_id']==record['normalBandId']
    assert ref['variant_level_parameter']==1
    assert ref['unlock_condition_reference']==record['unlockCondDesc']
    assert ref['account_unlocked'] is None and ref['actual_activation'] is None
    assert ref['reference_only'] is True
    assert section_ids.count('squad_unlock_reference')==1
    assert '强化分队 · 条件资料' in text and record['unlockCondDesc'] in text
    assert '账户解锁状态：未知' in text and '解锁条件实际激活：未知' in text
    assert '不据此切换分队版本或追加效果' in text
    assert 'rogue_6_band_' not in text and 'commonDevelopment' not in text
    gates={'rogue_6_band_2':3,'rogue_6_band_5':6,'rogue_6_band_7':9}
    node=ref['technology_node_reference']
    if record['id'] in gates:
        assert node['gate_reference']['enable_grade_parameter']==gates[record['id']]
        assert node['gate_reference']['enable_description_reference'] in text
    elif record['id']=='rogue_6_band_22':
        assert node is None
    else:
        assert node['gate_reference'] is None
    if record['id']=='rogue_6_band_7':
        if args['run_config']['squad']['effect_verified']:
            assert len(resolution['applied'])==3
            assert all(r['value']==.15 for r in resolution['applied'])
        else:
            assert resolution['applied']==[]
            assert any('效果阶段尚未确认' in s for s in resolution['pending'])

def require_headwolf075(result,args,text,plain=None):
    assert args['operator']=='char_1038_whitw2'
    drones=[c for c in result['components'] if c['name']=='浮游单元']
    if args['skill'] in (1,2):
        assert bool(drones) is (args.get('window_seconds')!=0)
        assert all(c['timing_reference']=='owner_attack_clock; independent drone clock unverified' for c in drones)
        if args['elite']==0:
            assert args['skill']==1
            if plain is not None:
                assert canonical075(result)==canonical075(plain)
    if args['skill']==3:
        ref=result['drone_lifecycle_reference']
        for key in ('aura_first_tick_seconds','aura_tick_count','arrival_seconds','same_target_hit_counter'):
            assert ref[key] is None
    assert '独立' in text and ('未核验' in text or '未知' in text)

def require_mei075(result,args,text,qualified,stage):
    section_ids=[s['id'] for s in result['report']['sections']]
    if not qualified:
        assert 'mei_airborne_module_reference' not in result
        assert 'mei_airborne_module' not in section_ids
        return
    ref=result['mei_airborne_module_reference']
    assert ref['module_id']=='uniequip_002_mm' and ref['module_level']==stage
    assert ref['unlock_elite']==2 and ref['unlock_level']==40
    assert ref['attack_scale_parameter']==1.1
    assert ref['actual_target_is_airborne'] is None and ref['actual_conditional_damage'] is None
    assert ref['reference_only'] is True and ref['applied_to_numeric_estimate'] is False
    for key in ('native_attachment_verified','damage_composition_verified','live_state_verified'):
        assert ref[key] is False
    assert section_ids.count('mei_airborne_module')==1
    assert '梅 MAR-X · 空中条件参数参考' in text
    assert '当前目标空中条件：未知' in text and '该特性实际条件伤害：未知' in text
    assert '110%参数未计入当前伤害数值' in text

def require_wisdel_routes075(result,args,text):
    ref=result['wisdel_summon_qualification_reference']
    assert ref['operator_id']=='char_1035_wisdel'
    assert ref['token_id']=='token_10035_wisdel_wward'
    assert ref['current_cultivation']=={k:args[k] for k in ('elite','level','potential')}
    talent=ref['talent_route'];skill=ref['skill_route'];qualified=args['elite']==2
    assert talent['cultivation_qualified'] is qualified and skill['cultivation_qualified'] is qualified
    assert talent['unlock_elite']==skill['unlock_elite']==2
    assert talent['unlock_level']==skill['unlock_level']==1
    assert skill['currently_selected'] is (args['skill']==3)
    if args['skill']==3:
        assert skill['selected_level_source']['rank']==args['skill_rank']
    else:
        assert skill['selected_level_source'] is None
    assert ref['actual_source_provenance'] is None
    for key in ('actual_presence_verified','actual_cast_clock_verified','covers_all_routes','declared_counts_reinterpreted'):
        assert ref[key] is False
    assert '魂灵之影 · 本体召唤途径培养资料' in text
    status='已达原表培养门槛' if qualified else '未达原表培养门槛'
    assert status in text and '未确定其来源归属' in text
    assert '本资料不涵盖模组或藏品' in text
    source=result['wisdel_secondary_reference']
    count=args['ghost_casts'] if args['ghost_count'] else 0
    assert type(source['ghost_casts_requested']) is int and source['ghost_casts_requested']==count
    assert source['ghost_cast_times_seconds'] is None
    assert source['shadow_lifecycle_verified'] is False

def require_movement075(entry,text,technical,stage):
    move=entry['movement_reference']
    assert move['complete_effective_speed_verified'] is False
    assert '预计有效移速：未知' in text
    if stage['id']=='ro6_e_3_6':
        ref=move['stage_move_speed_rune_reference']
        assert ref['parameter']==1.5 and ref['source_selector']=='$.runes[0].blackboard[2]'
        assert ref['source']==stage['level_source']
        assert ref['source']['sha256']=='2d2e89306c3d3c4a2a6c21f71b3828f66cb7a7996ab149faaad043d4867e8296'
        assert (ref['difficulty_mask_parameter'],ref['profession_mask_parameter'],ref['buildable_mask_parameter'])==('FOUR_STAR',1023,'ALL')
        assert ref['native_target_writer_layer_verified'] is False
        assert ref['combined_with_stage_multiplier_speed'] is None
        assert ref['complete_effective_speed_verified'] is False
        if technical:
            assert '关卡移速符文参数参考：1.5' in text
            assert '基础移速×关卡倍率小计：' in text
            assert '符文与关卡倍率合成的移速：未知' in text
            assert '原生目标、写入及叠加层尚未核验' in text
            assert ref['source']['url'] in text
        else:
            assert '关卡移速符文参数参考' not in text
            assert '基础移速×关卡倍率小计' not in text
    else:
        assert 'stage_move_speed_rune_reference' not in move
        assert '关卡移速符文参数参考' not in text
    if move['base_attribute'] is not None:
        assert move['base_times_stage_speed']==move['base_attribute']*stage['movement_multiplier']
