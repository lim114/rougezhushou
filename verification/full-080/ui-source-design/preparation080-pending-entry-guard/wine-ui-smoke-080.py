"""Real Windows Qt widgets under Wine; isolated state; no capture/chat operations."""
import hashlib, importlib, importlib.metadata, json, os, platform, subprocess, sys, tempfile, time, traceback
from pathlib import Path
ROOT=Path(r'Z:\workspace\rougezhushou')
OUT=Path(r'Z:\workspace\.compat')
sys.path.insert(0,str(ROOT))
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

"""Public design cases; list construction performs no API, GUI or state reads."""
def cases075(squads):
    rows=[]
    def add(section,owner,number,elite,level,rank,mode,**extra):
        args={'operator':owner,'skill':number,'elite':elite,'level':level,'skill_rank':rank,
              'potential':1,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':10,'enemy_defense':0,'enemy_resistance':0,
              'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[]}
        args.update(extra);rows.append({'section':section,'input':args})
    modes=('frames','continuous')
    for record in squads.values():
        for mode in modes:
            for flag in (False,True):
                add(71,'silverash',3,2,90,10,mode,run_config={'squad':{
                    'id':record['id'],'name':record['name'],'level':record['bandLevel'],'effect_verified':flag}})
    for sid,gate in (('rogue_6_band_2',3),('rogue_6_band_5',6),('rogue_6_band_7',9)):
        record=squads[sid]
        for grade in (gate-1,gate):
            for mode in modes:
                add(71,'silverash',3,2,90,10,mode,run_config={'squad':{
                    'id':sid,'name':record['name'],'level':1,'effect_verified':True},
                    'difficulty':{'value':grade,'modeDifficulty':'NORMAL'}})
    record=squads['rogue_6_band_22']
    for elite,level,rank in ((0,50,4),(1,80,7),(2,90,10)):
        for mode in modes:
            add(71,'mechanist',1,elite,level,rank,mode,run_config={'squad':{
                'id':record['id'],'name':record['name'],'level':1,'effect_verified':True}})
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,80,7,(1,2)),(2,90,10,(1,2,3))):
        for potential in (1,6):
            interval={(1,1):30,(1,6):26,(2,1):20,(2,6):16}.get((elite,potential))
            # Existing option QDoubleSpinBox has two decimal places.
            ages=(0,59,60,120,3600) if interval is None else (0,interval-.01,interval,3*interval-.01,3*interval,3600)
            for number in numbers:
                for mode in modes:
                    for warmup in (0,100):
                        for age in ages:
                            add(72,'char_1038_whitw2',number,elite,level,rank,mode,potential=potential,
                                deployment_elapsed_seconds=age,drone_warmup_hits=warmup)
    for elite,level,rank in ((1,60,7),(2,39,7),(2,40,10)):
        for stage in (1,2,3):
            for number in (1,2):
                for mode in modes:
                    for horizon in (0,10):
                        add(73,'char_133_mm',number,elite,level,rank,mode,module_id='uniequip_002_mm',
                            module_level=stage,window_seconds=horizon)
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,80,7,(1,2)),(2,1,1,(1,2,3)),(2,90,10,(1,2,3))):
        for stage in ((0,1,2,3) if elite==2 and level==90 else (0,)):
            for number in numbers:
                for mode in modes:
                    for ghosts,casts,horizon in ((0,0,10),(1,2,10),(3,0,0)):
                        add(74,'char_1035_wisdel',number,elite,level,rank,mode,
                            module_id='uniequip_002_wisdel' if stage else None,module_level=stage,
                            ghost_count=ghosts,ghost_casts=casts,window_seconds=horizon)
    return rows

def preview_cases075(stages):
    return [{'section':75,'stage_id':sid,'enemy_id':enemy['id'],'level':enemy['level'],'technical':technical}
        for sid in ('ro6_n_3_6','ro6_e_3_6') for enemy in stages[sid]['enemies'] for technical in (False,True)]


"""Public-output design only; assertions do not provide actual Qt proof."""
from copy import deepcopy
import json

HARUKA_LOCKED_NOTE080='当前培养尚未解锁扶摇花火；浮泡破碎声明保留，但不产生该天赋治疗或二技能中依赖该治疗的派生伤害。'

def canonical080(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False)

def normalized_locked_haruka080(result):
    value=deepcopy(result)
    for ref in (value['external_event_reference'],value['external_event_reference']['window_reference']):
        ref['parameter_rows'][0]=('声明窗口内浮泡破碎次数',0.0,'次')
        ref['notes']=[n for n in ref['notes']if n!=HARUKA_LOCKED_NOTE080]
    for section in value['report']['sections']:
        if section['id']=='external_events':
            section['notes']=[n for n in section['notes']if n!=HARUKA_LOCKED_NOTE080]
            next(m for m in section['metrics']if m['key']=='parameter_0')['value']=0.0
    return value

def require_haruka080(result,args,text,plain):
    count=args['bubble_bursts'];qualified=args['elite']==2
    ref=result['external_event_reference']
    assert ref['kind']=='haruka_bubbles'
    assert ref['parameter_rows'][0]==('声明窗口内浮泡破碎次数',float(count),'次')
    assert ref['actual_event_times_seconds'] is None
    if not qualified:
        assert canonical080(normalized_locked_haruka080(result))==canonical080(plain)
        if count>0:assert HARUKA_LOCKED_NOTE080 in ref['notes'] and HARUKA_LOCKED_NOTE080 in text
        else:assert HARUKA_LOCKED_NOTE080 not in ref['notes']
        for component in result['components']:
            if component['name'] in ('扶摇花火','浮泡治疗衍生伤害'):
                assert component['hits']==0 and component['total']==0
                assert 'actual_total' not in component
    else:
        assert HARUKA_LOCKED_NOTE080 not in ref['notes']
        healing=result['haruka_healing_reference']
        assert healing['native_attachment_verified'] is False
        assert healing['native_composition_verified'] is False
        if count>0 and args['window_seconds']>0:
            assert result['total_healing'] is None
    if args['window_seconds']==0:
        assert result['total_damage']==0 and result['total_healing']==0
    if args.get('timing',{}).get('target_disappears_seconds')==0:
        assert result['total_damage']==0
    assert '独立条件来源 · 事件时钟待核验' in text

def require_aglna080(result,args,text,controls):
    name='飘浮大地之上'
    component=next(c for c in result['components']if c['name']==name)
    if args['elite']==0:
        assert component['hits']==component['per_hit']==component['total']==0
        assert component['times_seconds']==[]
        assert result['estimate']['skill']['hit_counts'][name]==0
        assert canonical080(result)==canonical080(controls['light'])
    else:
        weight=args['enemy_weight']
        if weight<=3:
            assert canonical080(result)==canonical080(controls['light'])
        else:
            assert canonical080(result)==canonical080(controls['heavy'])
            light=next(c for c in controls['light']['components']if c['name']==name)
            hi,lo={(1,1):(.2,.13),(1,3):(.3,.18),(2,1):(.35,.25),(2,3):(.45,.3)}[(args['elite'],args['potential'])]
            assert abs(component['per_hit']*hi-light['per_hit']*lo)<1e-7
    if args['skill']==2:
        ref=result['aglna_liftoff_reference']
        assert ref['actual_takeoff_seconds'] is None and ref['lifecycle_binding_verified'] is False
        assert result['estimate']['skill']['duration_seconds'] is None
        assert result['estimate']['skill']['cycle_seconds'] is None
    if args['window_seconds']==0 or args.get('timing',{}).get('target_disappears_seconds')==0:
        assert result['total_damage']==0

def require_aglna_selected080(result,args,text,plain,mass):
    target=args['target_enemy'];enemy=result['run_resolution']['enemy']
    for key in ('stage_id','enemy_id','level'):
        assert enemy[key]==target[key]
    assert enemy['reference_stats']['massLevel']==mass
    assert canonical080(result)==canonical080(plain)
    component=next(c for c in result['components']if c['name']=='飘浮大地之上')
    if args['elite']==0:
        assert component['hits']==component['per_hit']==component['total']==0
        assert component['times_seconds']==[]
        assert result['estimate']['skill']['hit_counts']['飘浮大地之上']==0
    else:
        assert component['hits']>0 and component['per_hit']>0
    assert enemy['name'] in text

def normalized_locked_mantra080(result):
    value=deepcopy(result)
    for ref in (value['external_event_reference'],value['external_event_reference']['window_reference']):
        ref['parameter_rows'][0]=('声明当前目标麻痹触发次数',0.0,'次')
    for section in value['report']['sections']:
        if section['id']=='external_events':
            next(m for m in section['metrics']if m['key']=='parameter_0')['value']=0.0
    return value

def require_mantra080(result,args,text,plain):
    count=args['palsy_triggers'];qualified=args['elite']>=1
    ref=result['external_event_reference'];window=ref['window_reference']
    assert ref['kind']=='mantra_events'
    assert ref['parameter_rows'][0]==('声明当前目标麻痹触发次数',float(count),'次')
    assert window['parameter_rows'][0]==ref['parameter_rows'][0]
    assert ref['actual_event_times_seconds'] is None
    assert ref['collision_clock_verified'] is False and window['collision_clock_verified'] is False
    if not qualified:
        assert canonical080(normalized_locked_mantra080(result))==canonical080(plain)
        component=next(c for c in result['components']if c['name']=='麻痹触发天赋')
        assert component['hits']==component['per_hit']==component['total']==0
        assert 'actual_total'not in component
    elif count>0 and args['window_seconds']>0 and args.get('timing',{}).get('target_disappears_seconds')!=0:
        assert result['total_damage'] is None
    if args['skill']==3:
        assert ref['parameter_rows'][1]==('声明当前目标溢出跳跃命中次数',float(args['palsy_overflow_hits']),'次')
        if args['palsy_overflow_hits']>0 and args['window_seconds']>0 and args.get('timing',{}).get('target_disappears_seconds')!=0:
            assert result['total_damage'] is None
    if args['window_seconds']==0 or args.get('timing',{}).get('target_disappears_seconds')==0:
        assert result['total_damage']==0
    assert '独立条件来源 · 事件时钟待核验' in text

def require_medical_amiya080(result,args,text):
    name='诚挚期许本体生命回复'
    component=next(c for c in result['components']if c['name']==name)
    assert component['damage_type']=='regeneration' and component['source_unit']=='operator'
    assert type(component['hits'])is float and type(component['total'])is float
    assert '阿米娅 · 医疗'in text
    if args['elite']==0:
        assert args['skill']==1
        assert component['hits']==component['per_hit']==component['total']==0
        assert type(result['estimate']['skill']['hit_counts'][name])is float
        assert result['estimate']['skill']['hit_counts'][name]==0.0
        assert 'actual_total'not in component
        assert name not in result['timing'].get('unplaced_components',[])
        assert not any('尚未统一排入时间轴' in note and name in note for note in result['estimate']['notes'])
        assert '尚未统一排入时间轴的输出分项：'+name not in text
        assert result['estimate']['skill']['duration_seconds']>0
    else:
        assert component['per_hit']>0
        assert component['hits']==float(args['window_seconds'])
        if args['skill']==1:
            assert 'actual_total'not in component
            assert result['estimate']['skill']['hit_counts'][name]>0
            if args['timing_mode']=='frames' and args['window_seconds']>0:
                assert name in result['timing']['unplaced_components']
        else:
            phase=result['amiya_phase_reference']
            assert phase['actual_strengthening_start_seconds']is None
            assert phase['actual_skill_end_seconds']is None
            assert phase['phase_clock_verified']is False
            assert phase['opening_buff_healing_order_verified']is False
            assert result['estimate']['skill']['duration_seconds']is None
            assert result['estimate']['skill']['cycle_seconds']is None
            assert component['nominal_duration_reference_seconds']==float(args['window_seconds'])
            if args['window_seconds']>0:assert component['actual_total']is None
            else:assert 'actual_total'not in component
    if args['window_seconds']==0:
        assert result['total_damage']==0 and result['total_healing']==0
    if args['skill']==2 and args['window_seconds']>0 and args.get('timing',{}).get('target_disappears_seconds')!=0:
        assert result['total_damage']is None
        if args['healing_targets']==0:assert result['total_healing']==0
        else:assert result['total_healing']is None

def require_medical_trait080(result,args,text,ratio):
    require_medical_amiya080(result,args,text)
    heal=next(c for c in result['components']if c['name']=='咒愈师伤害转治疗')
    dependent=heal['damage_healing']
    expected=ratio*min(1,args['healing_targets'])
    assert dependent['ratio']==expected
    assert dependent['sources']==([0]if args['skill']==1 else [0,1])
    healing_factor=1.2 if args['relic_ids']==['rogue_6_relic_legacy_81']else 1.0
    subtotal=sum(result['components'][i]['total']for i in dependent['sources'])
    assert abs(heal['total']-subtotal*expected*healing_factor)<1e-7
    if args['skill']==2:
        phase=result['amiya_phase_reference']
        assert abs(phase['opening_healing_reference']-phase['opening_damage_reference']*expected*healing_factor)<1e-7
        if args['window_seconds']>0 and args['healing_targets']>0:
            assert heal['actual_total']is None
            assert phase['actual_skill_end_seconds']is None
    elif args['healing_targets']==2:
        direct=next(c for c in result['components']if c['name']=='哀恸共情范围治疗')
        assert direct['hits']>0 and direct['total']>0
        assert dependent['ratio']==ratio


"""Construct public design cases without API calls or private state reads."""
def cases080():
    rows=[]
    def add(elite,level,rank,number,mode,scope,horizon,timing,**extra):
        args={'operator':'char_4202_haruka','elite':elite,'level':level,'skill_rank':rank,
              'skill':number,'timing_mode':mode,'potential':5,'trust':100,
              'module_id':None,'module_level':0,'window_seconds':horizon,'healing_targets':1,
              'enemy_defense':0,'enemy_resistance':0,'cooperative':False,'preexisting_fragile':False,'relic_ids':[]}
        if timing:args['timing']=timing
        args.update(extra);rows.append({'section':76,'context':scope,'input':args})
    scopes=[('positive',10,{}),('zero_window',0,{}),
            ('zero_lifetime',10,{'target_disappears_seconds':0}),
            ('empty_target_windows',10,{'target_windows':[]})]
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,80,7,(1,2)),(2,60,10,(1,2,3))):
        for potential in (4,5):
            for number in numbers:
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for repeat in ((False,True)if number==2 else (False,)):
                            for count in (0,1,10000):
                                opts={'bubble_bursts':count,'potential':potential}
                                if number==2:opts['haruka_repeat']=repeat
                                if number==3:opts['levitate_triggers']=0
                                add(elite,level,rank,number,mode,scope,horizon,timing,**opts)
    for stage in (1,2,3):
        for level in (59,60):
            for mode in ('frames','continuous'):
                for count in (0,1):
                    add(2,level,10,2,mode,'module_unlock_boundary',10,{},bubble_bursts=count,
                        module_id='uniequip_002_haruka',module_level=stage,haruka_repeat=True)
    for elite,level,rank,number in ((0,50,4,1),(1,80,7,2)):
        for mode in ('frames','continuous'):
            for count in (0,1):
                opts={'haruka_repeat':False}if number==2 else {}
                add(elite,level,rank,number,mode,'locked_module_does_not_grant_talent',10,{},bubble_bursts=count,
                    module_id='uniequip_002_haruka',module_level=3,**opts)
    for mode in ('frames','continuous'):
        for trigger in (1,1000):
            for count in (0,1):
                add(2,60,10,3,mode,'independent_levitate_declaration',10,{},bubble_bursts=count,levitate_triggers=trigger)
    for elite,rank in ((1,7),(2,10)):
        for mode in ('frames','continuous'):
            for count in (0,1):
                add(elite,60,rank,2,mode,'zero_declared_friendly_targets',10,{},bubble_bursts=count,
                    healing_targets=0,haruka_repeat=False)
    def aglna(elite,level,rank,number,potential,mode,scope,horizon,timing,weight):
        args={'operator':'char_1015_aglna2','elite':elite,'level':level,'skill_rank':rank,'skill':number,
              'potential':potential,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':horizon,'enemy_defense':0,'enemy_resistance':0,
              'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[],
              'enemy_weight':weight}
        if timing:args['timing']=timing
        rows.append({'section':77,'context':scope,'input':args})
    for elite,numbers in ((0,(1,)),(1,(1,2)),(2,(1,2,3))):
        for number in numbers:
            for potential in (1,3):
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for weight in (0,3,4,100):
                            aglna(elite,1,1,number,potential,mode,scope,horizon,timing,weight)
    for elite,level,rank,number in ((0,50,4,1),(1,80,7,2),(2,90,10,3)):
        for mode in ('frames','continuous'):
            for weight in (0,3,4,100):
                aglna(elite,level,rank,number,3,mode,'readonly_max_cultivation',10,{},weight)
    # Exact public NORMAL roster identities, massLevel3/4. Selection overrides
    # the separate manual reference; declared weight remains genuine Qt input.
    for elite,number in ((0,1),(2,3)):
        for enemy_id,level,mass in (('enemy_10107_mjcdog_2',0,3),('enemy_2002_bearmi',1,4)):
            for mode in ('frames','continuous'):
                for weight in (0,100):
                    aglna(elite,1,1,number,3,mode,'selected_enemy_overrides_manual_weight',10,{},weight)
                    rows[-1]['input']['target_enemy']={'stage_id':'ro6_n_3_6','enemy_id':enemy_id,'level':level}
                    rows[-1]['expected_reference_mass']=mass
    #78 final source is committed; these designs still need final080 preflight.
    def mantra(elite,level,rank,number,potential,mode,scope,horizon,timing,count,**extra):
        args={'operator':'char_4204_mantra','elite':elite,'level':level,'skill_rank':rank,'skill':number,
              'potential':potential,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':horizon,'enemy_defense':0,'enemy_resistance':0,
              'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[],
              'palsy_triggers':count}
        if number==3:args['palsy_overflow_hits']=0
        if timing:args['timing']=timing
        args.update(extra)
        rows.append({'section':78,'context':scope,'input':args})
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,80,7,(1,2)),(2,90,10,(1,2,3))):
        for number in numbers:
            for potential in (4,5):
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for count in (0,1,10000):
                            mantra(elite,level,rank,number,potential,mode,scope,horizon,timing,count)
    for mode in ('frames','continuous'):
        for scope,horizon,timing in scopes:
            for overflow in (1,10000):
                for count in (0,1):
                    mantra(2,90,10,3,5,mode,'separate_overflow_'+scope,horizon,timing,count,palsy_overflow_hits=overflow)
    for number in (1,2,3):
        for mode in ('frames','continuous'):
            for count in (0,1):
                mantra(2,90,10,number,5,mode,'elemental_immunity_does_not_bind_clock',10,{},count,
                    enemy_elemental_resistance=100.0)
    for stage in (1,2,3):
        for level in (59,60):
            for mode in ('frames','continuous'):
                for count in (0,1):
                    mantra(2,level,10,2,5,mode,'readonly_module_boundary',10,{},count,
                        module_id='uniequip_002_mantra',module_level=stage)
    for mode in ('frames','continuous'):
        for count in (0,1):
            mantra(0,50,4,1,5,mode,'locked_module_does_not_grant_talent',10,{},count,
                module_id='uniequip_002_mantra',module_level=3)
    #79 medical form only. No assumed account form-unlock or unavailable HP0.
    def medical(elite,level,rank,number,potential,mode,scope,horizon,timing,**extra):
        args={'operator':'char_1037_amiya3','elite':elite,'level':level,'skill_rank':rank,
              'skill':number,'potential':potential,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':horizon,'enemy_defense':0,'enemy_resistance':0,
              'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[]}
        if number==2:args['amiya_hit_targets']=1
        if timing:args['timing']=timing
        args.update(extra);rows.append({'section':79,'context':scope,'input':args})
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,70,7,(1,2)),(2,80,10,(1,2))):
        for number in numbers:
            for potential in (1,6):
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for count in ((1,5,100)if number==2 else (None,)):
                            opts={'amiya_hit_targets':count}if count is not None else {}
                            medical(elite,level,rank,number,potential,mode,scope,horizon,timing,**opts)
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,70,7,(1,2)),(2,49,10,(1,2)),(2,50,10,(1,2))):
        for number in numbers:
            for stage in (1,2,3):
                for mode in ('frames','continuous'):
                    medical(elite,level,rank,number,1,mode,'readonly_INC_X_boundary',10,{},
                        module_id='uniequip_002_amiya3',module_level=stage)
    for elite,numbers in ((0,(1,)),(1,(1,2)),(2,(1,2))):
        for number in numbers:
            for mode in ('frames','continuous'):
                for targets in ((0,2)if number==1 else (0,1)):
                    medical(elite,1,1,number,1,mode,'own_regeneration_independent_of_friendly_count',10,{},
                        healing_targets=targets)
        for mode in ('frames','continuous'):
            medical(elite,1,1,1,1,mode,'readonly_talent_minimum_level',10,{})
    #80 confirmed same medical trait replacement. Final patch remains pending.
    def trait_case(elite,level,rank,number,stage,mode,scope,horizon,timing,**extra):
        medical(elite,level,rank,number,1,mode,scope,horizon,timing,
            module_id='uniequip_002_amiya3'if stage else None,module_level=stage,**extra)
        rows[-1]['section']=80
        rows[-1]['expected_trait_ratio']=.6 if elite==2 and level>=50 and stage else .5
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,70,7,(1,2)),(2,49,10,(1,2)),(2,50,10,(1,2))):
        for number in numbers:
            for stage in (0,1,2,3):
                for mode in ('frames','continuous'):
                    for targets in (0,1):
                        trait_case(elite,level,rank,number,stage,mode,'INC_X_same_trait_ratio_boundary',10,{},
                            healing_targets=targets)
    for stage in (1,2,3):
        for number in (1,2):
            for mode in ('frames','continuous'):
                for scope,horizon,timing in scopes[1:]:
                    trait_case(2,50,10,number,stage,mode,'qualified_trait_'+scope,horizon,timing)
                trait_case(2,50,10,number,stage,mode,'accepted_healing_factor_preserves_trait_ratio',10,{},
                    relic_ids=['rogue_6_relic_legacy_81'])
                trait_case(2,50,10,number,stage,mode,'conversion_uses_dealt_enemy_damage',10,{},
                    enemy_resistance=50)
    for stage in (0,1,2,3):
        for mode in ('frames','continuous'):
            trait_case(2,50,10,1,stage,mode,'trait_one_recipient_and_separate_S1_range_healing',10,{},
                healing_targets=2)
    return rows


def source_hashes():
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in (ROOT/'rouge',) for p in sorted(folder.rglob('*'))
            if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
checks=[];started=time.perf_counter();window=None;app=None;before=source_hashes()
receipt={'scope':'Wine Windows binary compatibility; no native Windows or game integration',
         'native_windows_verified':False,'game_captures':0,'chat_requests':0,
         'private_state_isolated':True,'platform':platform.platform(),'python':sys.version,
         'checks':checks,'passed':False,'complete_ui_validation':False,'plain_text_normalization':'QPlainTextEdit converts non-breaking spaces to ordinary spaces'}
try:
    for name in ('PySide6.QtWidgets','numpy','cv2','win32gui','win32process','win32api','httpx','rapidocr_onnxruntime','windows_capture'):
        importlib.import_module(name)
        checks.append({'scope':'real_dependency_import','module':name,'passed':True})
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication,QPushButton
    import rouge.app as module
    from rouge.reporting import format_report
    diagnosis_path=ROOT/'research/p2-friendly-scope-report/independent-diagnosis.json'
    assert diagnosis_path.is_file(),str(diagnosis_path)
    diagnosis_bytes=diagnosis_path.read_bytes()
    diagnosis=json.loads(diagnosis_bytes)
    from rouge.capture import list_game_windows
    with tempfile.TemporaryDirectory() as folder:
        isolated=Path(folder)
        module.RUN_STATE=isolated/'run.json';module.OPERATOR_STATE=isolated/'operators.json';module.SETTINGS=isolated/'settings.json'
        backend=module.DesktopBackend
        module.DesktopBackend=lambda _path,callback:backend(isolated/'chat',callback)
        app=QApplication([]);window=module.MainWindow();window.show();app.processEvents()
        assert window.isVisible()
        assert not window.auto.isChecked() and window.capture.target is None
        assert not window.desktop.process and not window.desktop_request_busy
        assert not list_game_windows()
        checks.append({'scope':'actual_main_window_visible','title':window.windowTitle(),
                       'win32_game_enumeration':'no Arknights.exe window present',
                       'auto_sampling':False,'desktop_backend_started':False})
        window.auto_relics.setChecked(False)
        original_select=window.select_operator
        def checked_select(op):
            assert op in module.catalog()['operators'],op
            selected=original_select(op)
            assert window.operator.currentData()==op,(op,window.operator.currentData())
            return selected
        window.select_operator=checked_select
        skills=0
        for op,profile in module.catalog()['operators'].items():
            for skill in range(1,len(profile['skills'])+1):
                window.select_operator(op)
                window.skill.setCurrentIndex(window.skill.findData(skill))
                window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                actual=window.damage_text.toPlainText();expected=format_report(result,technical=window.damage_technical.isChecked()).replace(chr(160),' ')
                if actual!=expected:
                    (OUT/'wine-ui-report-difference-080.json').write_text(json.dumps({'operator':op,'skill':skill,'actual':actual,'expected':expected},ensure_ascii=False,indent=2),encoding='utf-8')
                    raise AssertionError(f'report text differs for {op} skill {skill}')
                skills+=1
        assert skills==87,skills
        checks.append({'scope':'actual_controls_calculate_all_profiles','skills':skills,'passed':True})
        for guarded_op,reference_key in (('char_437_mizuki','mizuki_s1_reference'),('char_4087_ines','ines_dot_reference')):
            window.select_operator(guarded_op)
            window.skill.setCurrentIndex(window.skill.findData(1));window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            guarded=window.damage_result['result']
            assert reference_key in guarded
            assert guarded['estimate']['skill']['duration_seconds'] is None
            assert guarded['estimate']['skill']['cycle_seconds'] is None
            assert '未知' in window.damage_text.toPlainText()
            checks.append({'scope':'unknown_s1_end_and_cycle_visible','operator':guarded_op,'skill':1,
                           'duration_seconds':None,'cycle_seconds':None,
                           'report_contains_unknown':True,'passed':True})
        window.select_operator('char_1044_hsgma2')
        window.skill.setCurrentIndex(window.skill.findData(3))
        terminal=next(widget for owner,key,_skills,widget in window.model_option_widgets
                      if owner=='char_1044_hsgma2' and key=='last_stand_seconds')
        terminal.setValue(5);window.limit_window.setChecked(True);window.window_seconds.setValue(1)
        window.calculate();app.processEvents()
        assert window.damage_result,window.damage_text.toPlainText()
        guarded=window.damage_result['result'];reference=guarded['manual_close_reference']
        assert reference['close_seconds'] is None
        assert guarded['estimate']['skill']['window_seconds']==1
        assert guarded['estimate']['skill']['duration_seconds'] is None
        assert guarded['total_damage'] is None
        assert '未知' in window.damage_text.toPlainText()
        checks.append({'scope':'positive_terminal_duration_preserves_window','operator':'char_1044_hsgma2','skill':3,
                       'last_stand_seconds':5,'requested_window_seconds':1,'reported_window_seconds':1,
                       'close_seconds':None,'complete_total':None,'passed':True})
        window.select_operator('char_1015_aglna2')
        window.skill.setCurrentIndex(window.skill.findData(1))
        weight=next(widget for owner,key,_skills,widget in window.model_option_widgets
                    if owner=='char_1015_aglna2' and key=='enemy_weight')
        window.window_seconds.setValue(3)
        talent=[]
        for mass in (3,4):
            weight.setValue(mass);window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            talent.append(next(c['per_hit'] for c in result['components'] if c['name']=='飘浮大地之上'))
        assert talent[0]>talent[1],talent
        checks.append({'scope':'actual_manual_weight_control_selects_talent','weights':[3,4],'per_hit':talent,'passed':True})
        for op,key in (('char_1015_aglna2','aglna_liftoff_reference'),('char_196_sunbr','next_attack_healing_reference'),('char_2025_shu','next_attack_healing_reference'),('char_1046_sbell2','snow_field_reference')):
            window.select_operator(op)
            window.skill.setCurrentIndex(window.skill.findData(2 if op in ('char_1015_aglna2','char_1046_sbell2') else 1))
            for horizon in (0,1):
                window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                assert key in result
                assert result['estimate']['skill']['window_seconds']==horizon
                amount=result['total_healing'] if key=='next_attack_healing_reference' else result['total_damage']
                assert amount==0 if horizon==0 else amount is None
                assert result['estimate']['skill']['cycle_seconds'] is None
            checks.append({'scope':'actual_short_window_controls_and_unknowns','operator':op,'zero_window_total':0,'one_second_total':None,'passed':True})
        tech=window.technology_reference
        assert tech.nodes.count()==57
        for index in range(tech.nodes.count()):
            tech.nodes.setCurrentIndex(index);app.processEvents()
            assert '账户解锁状态：未知' in tech.text.toPlainText()
        tech.search.setText('颊囊');app.processEvents();assert tech.nodes.count()==2
        tech.search.setText('不存在的科技xyz');app.processEvents();assert tech.nodes.count()==0
        assert '没有匹配' in tech.text.toPlainText()
        tech.search.clear();tech.nodes.setCurrentIndex(tech.nodes.findData('rogue_6_difficulty_1'));app.processEvents()
        assert '<保密等级3>' in tech.text.toPlainText()
        assert '原件SHA256' not in tech.text.toPlainText()
        tech.technical.setChecked(True);app.processEvents();assert '原件SHA256' in tech.text.toPlainText()
        tech.technical.setChecked(False);app.processEvents()
        checks.append({'scope':'actual_technology_browser','nodes':57,'duplicate_name_results':2,'empty_search':True,'grade_gate':3,'technical_toggle':True,'passed':True})
        for op,skills in (('char_4182_oblvns',(1,)),('char_1044_hsgma2',(2,)),('char_1048_orchd2',(1,2,3))):
            window.select_operator(op)
            for skill in skills:
                window.skill.setCurrentIndex(window.skill.findData(skill))
                for horizon in (0,1):
                    window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                    assert window.damage_result,window.damage_text.toPlainText()
                    result=window.damage_result['result']
                    assert 'unbound_cast_reference' in result
                    assert result['estimate']['skill']['window_seconds']==horizon
                    assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                    if op=='char_1044_hsgma2':
                        assert result['total_healing']==0 if horizon==0 else result['total_healing'] is None
                    assert result['estimate']['skill']['cycle_seconds'] is None
                checks.append({'scope':'actual_unbound_multihit_short_window_controls','operator':op,'skill':skill,'zero_window_total':0,'one_second_total':None,'passed':True})
        for op,skills in (('char_1029_yato2',(2,3)),('char_1050_chen3',(2,3)),('char_4202_haruka',(1,2,3)),('char_2027_wang',(1,2,3)),('char_4204_mantra',(1,2,3))):
            window.select_operator(op)
            for skill in skills:
                window.skill.setCurrentIndex(window.skill.findData(skill))
                if op in ('char_4202_haruka','char_4204_mantra'):
                    keys=('bubble_bursts','levitate_triggers') if op=='char_4202_haruka' else ('palsy_triggers','palsy_overflow_hits')
                    for owner,key,_skills,widget in window.model_option_widgets:
                        if owner==op and key in keys:widget.setValue(1)
                for horizon in (0,1):
                    window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                    assert window.damage_result,window.damage_text.toPlainText()
                    result=window.damage_result['result']
                    assert result['estimate']['skill']['window_seconds']==horizon
                    if horizon==0:
                        assert result['total_damage']==0
                        if op=='char_4202_haruka':assert result['total_healing']==0
                    elif op=='char_4202_haruka' and skill==1:
                        assert result['total_healing'] is None
                    else:assert result['total_damage'] is None
                checks.append({'scope':'actual_section31_35_short_window_and_event_controls','operator':op,'skill':skill,'zero_window_output':0,'positive_unplaced_source_unknown':True,'passed':True})
        for op in ('char_133_mm','char_1046_sbell2'):
            window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(1))
            for horizon in (0,1):
                window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                assert result['estimate']['skill']['window_seconds']==horizon
                assert result['estimate']['skill']['duration_seconds'] is None
                assert result['estimate']['skill']['cycle_seconds'] is None
                if horizon==0:assert result['total_damage']==0
                assert '未知' in window.damage_text.toPlainText()
            checks.append({'scope':'actual_mei_and_sbell_window_end_controls','operator':op,'zero_window':0,'positive_window_preserved':1,'actual_end_unknown':True,'passed':True})
        window.select_operator('char_1046_sbell2')
        snow_count=next(widget for owner,key,_skills,widget in window.model_option_widgets if owner=='char_1046_sbell2' and key=='snow_entries')
        snow_count.setValue(2)
        for skill in (1,2,3):
            window.skill.setCurrentIndex(window.skill.findData(skill))
            for horizon in (0,1):
                window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                assert result['estimate']['skill']['window_seconds']==horizon
            checks.append({'scope':'actual_snow_entry_controls','skill':skill,'manual_entries':2,'zero_window':0,'unplaced_positive_total':None,'passed':True})
        snow_count.setValue(0)
        for op in ('char_4087_ines','char_1041_angel2'):
            window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(3))
            for horizon in (0,1):
                window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                assert result['estimate']['skill']['window_seconds']==horizon
                assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                assert result.get('external_event_reference')
            checks.append({'scope':'actual_independent_deployment_projectile_controls','operator':op,'zero_window':0,'unplaced_positive_total':None,'passed':True})
        window.select_operator('char_298_susuro');window.skill.setCurrentIndex(window.skill.findData(1))
        window.window_seconds.setValue(10)
        window.timing_scenario.setPlainText(json.dumps({'target_disappears_seconds':0}))
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames);window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            assert result['total_damage']==0 and result['total_healing']>0
            assert '真实友方获取时钟未核验' in window.damage_text.toPlainText()
            checks.append({'scope':'actual_friendly_clock_explanation_probe','passed':True,
                'mode':'frames' if use_frames else 'continuous','scenario':window.damage_result['scenario'],
                'report_contains_friendly_clock_unknown':True,'numerical_damage':result['total_damage'],
                'numerical_healing':result['total_healing']})
        checks.append({'scope':'actual_friendly_healing_survives_empty_enemy','modes':['frames','continuous'],'positive_healing':True,'enemy_damage':0,'passed':True})
        window.select_operator('char_002_amiya');window.skill.setCurrentIndex(window.skill.findData(1))
        window.timing_scenario.setPlainText(json.dumps({'target_disappears_seconds':0}))
        window.limit_window.setChecked(False);window.frame_timing.setChecked(False);window.calculate();app.processEvents()
        assert window.damage_result,window.damage_text.toPlainText()
        result=window.damage_result['result'];skill=result['estimate']['skill']
        assert result['total_damage']==0 and skill['initial_seconds']==7 and skill['recharge_seconds']==30
        checks.append({'scope':'actual_amiya_empty_enemy_natural_recharge','first':7,'recharge':30,'enemy_damage':0,'passed':True})
        window.timing_scenario.clear();window.frame_timing.setChecked(True);window.limit_window.setChecked(True);window.window_seconds.setValue(1)
        window.window_seconds.setValue(10)
        op='char_437_mizuki'
        window.operator_observations[op]={'fields':{'elite':2,'level':60,'potential':1,'trust':100,'module_id':'uniequip_003_mizuki','module_level':2},'skill_ranks':{'1':10,'2':10,'3':10}}
        window.select_operator(op);window.update_operator()
        for skill in (1,2,3):
            window.skill.setCurrentIndex(window.skill.findData(skill));window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            assert 'mizuki_amb_y_reference' in result and result['total_damage'] is None
            assert result['total_healing'] is None
            assert '模组实际额外回复：未知' in window.damage_text.toPlainText()
            checks.append({'scope':'actual_mizuki_amb_y_readonly_cultivation_preview','skill':skill,'module_level':2,'level':60,'actual_extra_healing':None,'passed':True})
        def train(op,fields,ranks=None):
            window.operator_observations[op]={'fields':fields,'skill_ranks':ranks or {'1':10,'2':10,'3':10}}
            window.select_operator(op);window.update_operator()
        def calculate_result():
            window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            actual=window.damage_text.toPlainText()
            assert actual==format_report(result,technical=window.damage_technical.isChecked()).replace(chr(160),' ')
            return result
        def relics(ids):
            window.relic_list.blockSignals(True)
            for index in range(window.relic_list.count()):
                item=window.relic_list.item(index)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in ids else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False)
        for stage,expected in ((1,30),(2,28),(3,27)):
            train('char_1048_orchd2',{'elite':2,'level':60,'potential':1,'trust':100,'module_id':'uniequip_002_orchd2','module_level':stage})
            window.skill.setCurrentIndex(window.skill.findData(1));window.timing_scenario.clear()
            result=calculate_result()
            assert result['estimate']['base_stats']['redeploy_seconds']==expected
            assert result['orchid_redeploy_reference']['actual_next_deployment_seconds'] is None
            checks.append({'scope':'actual_orchid_module_redeploy_reference','module_level':stage,'parameter_seconds':expected,'actual_next_deployment':None,'passed':True})
        train('char_2027_wang',{'elite':2,'level':60,'potential':1,'trust':100,'module_id':'uniequip_002_wang','module_level':2})
        window.skill.setCurrentIndex(window.skill.findData(1));window.timing_scenario.clear()
        result=calculate_result()
        token=next(t for t in result['relic_token_stats'] if t['id']=='token_10064_wang_stone1')
        assert token['deployment_cost']==2 and token['module_cost_reference']['cost_add']==-1
        checks.append({'scope':'actual_wang_module_token_cost_reference','cost':2,'module_level':2,'passed':True})
        window.select_operator('char_4202_haruka');window.skill.setCurrentIndex(window.skill.findData(1));window.timing_scenario.clear()
        window.window_seconds.setValue(10)
        bubble=next(widget for owner,key,_skills,widget in window.model_option_widgets if owner=='char_4202_haruka' and key=='bubble_bursts')
        bubble.setValue(1);relics([])
        base=calculate_result()['known_healing_subtotals']['window_healing']
        relics(['rogue_6_relic_legacy_81']);result=calculate_result()
        assert abs(result['known_healing_subtotals']['window_healing']-base*1.2)<1e-7
        assert result['total_healing'] is None
        checks.append({'scope':'actual_known_healing_subtotal_factor','base_subtotal':base,'final_subtotal':result['known_healing_subtotals']['window_healing'],'actual_healing':None,'passed':True})
        relics([])
        for op in ('char_1001_amiya2','char_1037_amiya3'):
            window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(2))
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                window.timing_scenario.clear();window.limit_window.setChecked(True)
                for horizon in (0,1):
                    window.window_seconds.setValue(horizon);result=calculate_result()
                    assert result['estimate']['skill']['window_seconds']==horizon
                    assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                    assert result['estimate']['skill']['duration_seconds'] is None
                    if op=='char_1037_amiya3':
                        assert result['total_healing']==0 if horizon==0 else result['total_healing'] is None
                    checks.append({'scope':'actual_amiya_phase_window_controls','operator':op,'mode':'frames' if use_frames else 'continuous','window':horizon,'actual_output':result['total_damage'],'actual_end':None,'passed':True})
        window.frame_timing.setChecked(True);window.window_seconds.setValue(10)
        base=calculate_result()['known_healing_subtotals']['window_healing']
        relics(['rogue_6_relic_legacy_81']);result=calculate_result()
        known=result['known_healing_subtotals']['window_healing']
        assert abs(known-base*1.2)<1e-7
        assert abs(result['amiya_phase_reference']['opening_healing_reference']-known)<1e-7
        assert result['total_healing'] is None
        checks.append({'scope':'actual_medical_amiya_opening_healing_factor','unscaled_opening_reference':base,'scaled_known_reference':known,'actual_healing':None,'passed':True})
        # New section46-50 checks use only actual window controls and read-only cultivation.
        from rouge.operator_engine import selected_talents
        from rouge.gnosis_module_reference import DOT_NAME
        window.timing_scenario.clear();window.limit_window.setChecked(True)
        window.window_seconds.setValue(10);window.healing_targets.setValue(1);relics([])
        for owner,key,_skills,widget in window.model_option_widgets:
            if owner=='char_4202_haruka' and key in ('bubble_bursts','levitate_triggers'):widget.setValue(0)
            if owner=='char_4202_haruka' and key=='haruka_repeat':widget.setChecked(False)
        cold=next(widget for owner,key,_skills,widget in window.model_option_widgets
                  if owner=='char_206_gnosis' and key=='cold_state')
        for stage in (1,2,3):
            train('char_206_gnosis',{'elite':2,'level':60,'potential':1,'trust':100,
                                   'module_id':'uniequip_004_gnosis','module_level':stage})
            cold.setValue(1)
            for skill in (1,2,3):
                window.skill.setCurrentIndex(window.skill.findData(skill))
                for use_frames in (True,False):
                    window.frame_timing.setChecked(use_frames)
                    for horizon in (0,1):
                        window.window_seconds.setValue(horizon);result=calculate_result()
                        ref=result['gnosis_isw_a_reference']
                        assert ref['module_id']=='uniequip_004_gnosis' and ref['module_level']==stage
                        assert ref['original_talent']['blackboard']=={'cold':1,'damage_scale_cold':1.25,'damage_scale_freeze':1.5}
                        assert ref['original_talent']['prefab_key']=='1'
                        assert ref['original_talent']['talent_index']==0
                        assert not ref['original_talent']['module_coexistence_verified']
                        assert ref['dot_parameters']=={'atk_scale':.5,'interval':.5}
                        assert not ref['native_ability_attachment_verified'] and not ref['events_scheduled']
                        for key in ('actual_tick_count','actual_tick_times_seconds','actual_first_tick_seconds'):
                            assert ref[key] is None
                        records={r['prefab_key']:r for r in ref['module_records'] if r['kind']=='talent'}
                        if stage in (2,3):
                            assert set(records)=={'#','1','10_root','11_root'}
                            assert records['#']['blackboard']=={}
                            assert records['10_root']['blackboard']=={'cold':stage+1,'delay':.8}
                            assert records['11_root']['blackboard']=={'cold':1}
                            expected={'damage_scale_cold':1.25,'multi':2,'add':0,'max':1.5} if stage==2 else {'damage_scale_cold':1.3,'multi':2,'add':.05,'max':1.8}
                            assert records['1']['blackboard']==expected
                            assert records['10_root']['hidden'] and records['11_root']['hidden']
                            assert all(not r['attachment_verified'] for r in records.values())
                        else:assert records=={}
                        dot=next(c for c in result['components'] if c['name']==DOT_NAME)
                        assert dot['attack_scale_parameter']==.5 and dot['tick_interval_parameter_seconds']==.5
                        assert 'times_seconds' not in dot and dot['hits']==0
                        assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                        assert ref['actual_dot_damage']==0 if horizon==0 else ref['actual_dot_damage'] is None
                        assert ref['source_possible']['window']==bool(horizon)
                        assert '灵知ISW-A' in window.damage_text.toPlainText()
                        checks.append({'scope':'actual_gnosis_isw_a_module_cultivation_and_unknown_boundaries',
                            'stage':stage,'skill':skill,'mode':'frames' if use_frames else 'continuous',
                            'window':horizon,'actual_damage':result['total_damage'],'dot_parameters':ref['dot_parameters'],
                            'original_talent':ref['original_talent'],'module_records':ref['module_records'],'passed':True})
        # Explicitly reset all Haruka manual sources left by the earlier suite.
        for owner,key,_skills,widget in window.model_option_widgets:
            if owner=='char_4202_haruka' and key in ('bubble_bursts','levitate_triggers'):widget.setValue(0)
            if owner=='char_4202_haruka' and key=='haruka_repeat':widget.setChecked(False)
        window.timing_scenario.clear();window.window_seconds.setValue(10)
        for stage in (1,2,3):
            train('char_4202_haruka',{'elite':2,'level':60,'potential':1,'trust':100,
                                    'module_id':'uniequip_002_haruka','module_level':stage})
            for skill in (1,3):
                window.skill.setCurrentIndex(window.skill.findData(skill))
                assert window.healing_targets.maximum()==2
                for use_frames in (True,False):
                    window.frame_timing.setChecked(use_frames)
                    window.healing_targets.setValue(1);one=calculate_result()
                    window.healing_targets.setValue(2);two=calculate_result()
                    assert one['total_healing']>0 and abs(two['total_healing']-one['total_healing']*2)<1e-7
                    assert two['haruka_healing_reference']['actual_target_count'] is None
                    assert not two['haruka_healing_reference']['native_attachment_verified']
                    checks.append({'scope':'actual_haruka_module_s1_s3_two_recipient_reference',
                        'stage':stage,'skill':skill,'mode':'frames' if use_frames else 'continuous',
                        'widget_maximum':2,'one_reference':one['total_healing'],'two_reference':two['total_healing'],'passed':True})
            window.skill.setCurrentIndex(window.skill.findData(2))
            assert window.skill_rank_value()==10 and window.healing_targets.maximum()==3
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                window.healing_targets.setValue(3);result=calculate_result()
                assert result['total_healing'] is None and result['total_damage'] is None
                assert result['known_healing_subtotals']['window_healing']>0
                assert result['haruka_healing_reference']['additional_conditional_targets']==1
                assert result['haruka_healing_reference']['skill_target_add_parameter']==1
                checks.append({'scope':'actual_haruka_rank10_s2_extra_conditional_recipient',
                    'stage':stage,'mode':'frames' if use_frames else 'continuous','widget_maximum':3,
                    'actual_healing':None,'known_healing':result['known_healing_subtotals']['window_healing'],'passed':True})
        for module_id,module_level,expected in (('uniequip_002_haruka',1,2),(None,0,1)):
            train('char_4202_haruka',{'elite':2,'level':60,'potential':1,'trust':100,
                'module_id':module_id,'module_level':module_level},ranks={'1':4,'2':4,'3':4})
            window.skill.setCurrentIndex(window.skill.findData(2))
            window.update_skill_options();app.processEvents()
            assert window.skill_rank_value()==4 and window.healing_targets.maximum()==expected
            window.healing_targets.setValue(expected);result=calculate_result()
            assert window.damage_result['scenario']['skill_rank']==4
            assert result['haruka_healing_reference']['skill_target_add_parameter']==0
            assert result['haruka_healing_reference']['conditional_target_limit_reference']==expected
            checks.append({'scope':'actual_haruka_rank4_readonly_training_input_limit',
                'module_id':module_id,'module_level':module_level,'read_skill_rank':4,
                'widget_maximum':expected,'passed':True})
        low_cost=next(widget for owner,key,_skills,widget in window.model_option_widgets
                      if owner=='char_298_susuro' and key=='low_cost_healing_target')
        from PySide6.QtWidgets import QCheckBox
        assert isinstance(low_cost,QCheckBox)
        train('char_298_susuro',{'elite':2,'level':60,'potential':1,'trust':100,
                               'module_id':None,'module_level':0})
        window.healing_targets.setValue(1);window.window_seconds.setValue(10)
        window.timing_scenario.clear();relics([])
        for skill in (1,2):
            window.skill.setCurrentIndex(window.skill.findData(skill))
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                low_cost.setChecked(False);plain=calculate_result()
                low_cost.setChecked(True);qualified=calculate_result()
                assert window.damage_result['scenario']['low_cost_healing_target'] is True
                talents,_=selected_talents(module.catalog()['operators']['char_298_susuro'],window.damage_result['scenario'])
                factor=next(t['values']['heal_scale'] for t in talents if t['name']=='微创治疗')
                assert abs(qualified['estimate']['skill']['cycle_healing']-plain['estimate']['skill']['cycle_healing']*factor)<1e-7
                for key in ('initial_seconds','recharge_seconds','cycle_seconds','duration_seconds','sp_recovery_per_second'):
                    assert qualified['estimate']['skill'][key]==plain['estimate']['skill'][key]
                checks.append({'scope':'actual_susuro_low_cost_checkbox_whole_cycle_factor',
                    'skill':skill,'mode':'frames' if use_frames else 'continuous','selected_factor':factor,
                    'plain_cycle_healing':plain['estimate']['skill']['cycle_healing'],
                    'qualified_cycle_healing':qualified['estimate']['skill']['cycle_healing'],
                    'natural_sp_clocks_unchanged':True,'passed':True})
        window.select_operator('char_1037_amiya3');window.skill.setCurrentIndex(window.skill.findData(2))
        opening=next(widget for owner,key,_skills,widget in window.model_option_widgets
                     if owner=='char_1037_amiya3' and key=='amiya_hit_targets')
        assert opening.minimum()==1
        calculate_result()
        assert window.rank.text() and window.skill_rank_value()==window.damage_result['scenario']['skill_rank']
        checks.append({'scope':'actual_medical_amiya_public_minimum_and_readonly_rank','minimum':1,'passed':True})
        # Sections 51–55: actual available widgets; API booleans have no widget input.
        relics([]);window.limit_window.setChecked(True);window.window_seconds.setValue(10)
        train('char_002_amiya',{'elite':2,'level':80,'potential':1,'trust':100,'module_id':None,'module_level':0})
        window.skill.setCurrentIndex(window.skill.findData(1));window.frame_timing.setChecked(False)
        for timing in ({'target_disappears_seconds':.1},{'target_windows':[[0,1]]},{'target_windows':[]}):
            for horizon in (0,10):
                window.window_seconds.setValue(horizon);window.timing_scenario.setPlainText(json.dumps(timing))
                result=calculate_result();ref=result['amiya_continuous_reference'];skill=result['estimate']['skill']
                assert result['total_damage']==0 if horizon==0 or timing.get('target_windows')==[] else result['total_damage'] is None
                assert skill['recharge_seconds'] is None and skill['cycle_seconds'] is None
                assert result['timing']['phase_clock_unbound'] and not result['timing']['resource_and_damage_shared_clock']
                assert ref['native_clock_binding_verified'] is False
                assert '受限连续时序参考' in window.damage_text.toPlainText()
                assert result['scope']==result['estimate']['scenario_scope']
                checks.append({'scope':'actual_caster_amiya_restricted_continuous_inputs','timing':timing,'window':horizon,
                    'actual_damage':result['total_damage'],'actual_recharge':None,'actual_cycle':None,'passed':True})
        train('mechanist',{'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0})
        window.skill.setCurrentIndex(window.skill.findData(2));window.shield_breaks.setValue(2)
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames)
            for horizon,life in ((0,None),(10,None),(10,0)):
                window.window_seconds.setValue(horizon)
                window.timing_scenario.setPlainText(json.dumps({} if life is None else {'target_disappears_seconds':life}))
                result=calculate_result();ref=result['shield_break_reference'];actual=window.damage_text.toPlainText()
                assert result['total_damage']==0 if horizon==0 or life==0 else result['total_damage'] is None
                assert ref['hits_requested']==2 and ref['declared_count_damage_reference']>0
                assert ref['actual_break_times_seconds'] is None and ref['actual_end_seconds'] is None
                assert '实际破屏/爆炸时刻：未知' in actual and '仅实际屏障破碎' not in actual
                assert result['scope']==result['estimate']['scenario_scope']
                assert type(window.damage_result['scenario']['shield_break_count']) is int
                checks.append({'scope':'actual_mechanist_shield_count_and_window_controls','mode':'frames' if use_frames else 'continuous',
                    'window':horizon,'enemy_lifetime':life,'count':2,'actual_damage':result['total_damage'],'passed':True})
        for op,number,key in (('char_151_myrtle',2,'healing_targets'),('char_1037_amiya3',2,'amiya_hit_targets'),('char_4087_ines',2,'stolen_enemy_count')):
            train(op,{'elite':2,'level':60,'potential':1,'trust':100,'module_id':None,'module_level':0})
            window.skill.setCurrentIndex(window.skill.findData(number));window.timing_scenario.clear();window.window_seconds.setValue(10)
            widget=window.healing_targets if key=='healing_targets' else next(w for owner,k,_skills,w in window.model_option_widgets if owner==op and k==key)
            widget.setValue(1);result=calculate_result();args=window.damage_result['scenario']
            assert type(widget.value()) is int and type(args[key]) is int and args[key]==1
            for field in ('elite','level','potential','module_level'):assert type(args[field]) is int,(field,args[field])
            checks.append({'scope':'actual_supported_count_widgets_supply_integers','operator':op,'key':key,'value':1,'passed':True})
        locked_note='所选模组未满足当前精英阶段或等级门槛，本次未计模组基础属性与能力覆盖。'
        for op,module_id,below,gate,cap in (('mechanist','uniequip_002_mcnist',59,60,90),('char_298_susuro','uniequip_002_susuro',39,40,70)):
            for elite,level,locked in ((1,60,True),(2,below,True),(2,gate,False)):
                fields={'elite':elite,'level':level,'potential':1,'trust':100,'module_id':module_id,'module_level':3}
                train(op,fields,{'1':7,'2':7,'3':7});window.skill.setCurrentIndex(window.skill.findData(1))
                window.timing_scenario.clear();window.frame_timing.setChecked(True);window.window_seconds.setValue(10)
                result=calculate_result();actual=window.damage_text.toPlainText()
                assert (locked_note in actual)==locked
                assert result['estimate']['training']['module_id']==module_id
                assert result['estimate']['training']['module_level']==3
                if locked:
                    assert '当前模组基础属性已参与估算' not in actual and '已计模组基础属性与适用天赋数据覆盖' not in actual
                    plain={**fields,'module_id':None,'module_level':0};stats=result['estimate']['base_stats']
                    train(op,plain,{'1':7,'2':7,'3':7});window.skill.setCurrentIndex(window.skill.findData(1))
                    assert calculate_result()['estimate']['base_stats']==stats
                checks.append({'scope':'actual_readonly_module_request_respects_qualification','operator':op,'elite':elite,'level':level,
                    'module_id':module_id,'module_level':3,'locked':locked,'passed':True})
        receipt['api_boolean_guard_scope']='API rejection is verified by regression; actual Qt numeric controls emit integers and cannot submit booleans.'
        # Sections56-60: actual Qt controls and calculation button; no Wine run
        # has been performed merely by authoring this external draft.
        supplemental_start=len(checks)
        from copy import deepcopy
        from PySide6.QtWidgets import QPlainTextEdit,QSpinBox
        window.centralWidget().setCurrentIndex(1);app.processEvents()
        supplemental_button=next(b for b in window.findChildren(QPushButton)
                                 if b.text()=='计算属性与技能预估')
        assert supplemental_button.isVisible() and supplemental_button.isEnabled()
        def click_result():
            supplemental_button.click();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            assert window.damage_text.toPlainText()==format_report(
                result,technical=window.damage_technical.isChecked()).replace(chr(160),' ')
            return result
        def clock_zero(value):
            payload=json.dumps({'target_disappears_seconds':value},ensure_ascii=False)
            window.timing_scenario.setPlainText(payload)
            result=click_result()
            submitted=window.damage_result['scenario']['timing']['target_disappears_seconds']
            assert type(submitted) is type(value) and submitted==value
            assert window.timing_scenario.toPlainText()==payload
            return result
        assert isinstance(window.timing_scenario,QPlainTextEdit)
        window.damage_technical.setChecked(False);relics([])
        window.limit_window.setChecked(True);window.window_seconds.setValue(10)
        # The string is entered in an existing JSON text field, never in a
        # numeric spinbox. The API's full87-skill aliases remain regression scope.
        for op,number,level in (('char_002_amiya',1,80),
                                ('char_298_susuro',1,60),('mechanist',2,90)):
            train(op,{'elite':2,'level':level,'potential':1,'trust':100,
                      'module_id':None,'module_level':0})
            window.skill.setCurrentIndex(window.skill.findData(number))
            window.healing_targets.setValue(1);window.shield_breaks.setValue(2)
            window.shield_duration_known.setChecked(False);low_cost.setChecked(False)
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                numeric=deepcopy(clock_zero(0))
                assert numeric['total_damage']==0
                if op=='char_298_susuro':assert numeric['total_healing']>0
                if op=='char_002_amiya' and not use_frames:
                    assert numeric['estimate']['skill']['initial_seconds']==7
                    assert numeric['estimate']['skill']['recharge_seconds']==30
                    assert numeric['estimate']['skill']['cycle_seconds']==60
                if op=='mechanist':
                    assert numeric['shield_break_reference']['declared_count_damage_reference']>0
                for alias in ('0','0.0','-0'):
                    aliased=clock_zero(alias)
                    assert aliased==numeric,(op,number,use_frames,alias)
                    checks.append({'scope':'actual_json_text_zero_lifetime_alias',
                        'section':56,'operator':op,'skill':number,
                        'mode':'frames' if use_frames else 'continuous','alias':alias,
                        'input_widget':'QPlainTextEdit JSON, not a numeric spinbox',
                        'complete_result_equal_to_numeric_zero':True,
                        'caller_json_text_and_raw_string_preserved':True,
                        'enemy_damage':0,'friendly_healing':aliased.get('total_healing'),
                        'passed':True})
        receipt['section56_input_scope']='Actual timing_scenario JSON text and calculate button verify three zero strings on three representative skills in both modes; numeric spinboxes do not emit strings. Full87-skill API equivalence is separate regression coverage.'

        # Section57 does not simulate booleans accepted by numeric widgets.
        # Its four declared counts are real QSpinBox values with existing limits.
        window.timing_scenario.clear();relics([])
        for op,number,key,widget,upper in (
                ('mechanist',2,'shield_break_count',window.shield_breaks,100),
                ('mechanist',3,'charge_count',window.charge_count,100),
                ('silverash',2,'activation_count',window.activation_count,100),
                ('silverash',2,'deployment_stacks',window.stacks,2)):
            train(op,{'elite':2,'level':90,'potential':1,'trust':100,
                      'module_id':None,'module_level':0})
            window.skill.setCurrentIndex(window.skill.findData(number))
            window.timing_scenario.clear();window.window_seconds.setValue(10)
            window.activation_count.setValue(1);window.stacks.setValue(0)
            window.shield_breaks.setValue(0);window.charge_count.setValue(0)
            assert isinstance(widget,QSpinBox)
            assert widget.minimum()==0 and widget.maximum()==upper
            assert widget.isVisible() and widget.isEnabled(),key
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for value in (0,1,upper):
                    widget.setValue(value);result=click_result()
                    args=window.damage_result['scenario']
                    assert type(widget.value()) is int and widget.value()==value
                    assert type(args[key]) is int and args[key]==value
                    if key=='shield_break_count':
                        ref=result['shield_break_reference']
                        assert ref['hits_requested']==value
                        assert (ref['declared_count_damage_reference']==0)==(value==0)
                        assert result['total_damage']==0 if value==0 else result['total_damage'] is None
                    if key=='charge_count':
                        if value:
                            ref=result['charge_reference']
                            assert ref['hits_requested']==value
                            assert ref['declared_count_damage']==ref['per_hit_damage']*value
                            assert ref['collision_times_seconds'] is None
                            assert ref['events_scheduled'] is False
                            assert ref['full_cast_count_verified'] is False
                        else:
                            assert 'charge_reference' not in result
                    checks.append({'scope':'actual_declared_count_spinbox_range_and_type',
                        'section':57,'operator':op,'skill':number,'key':key,
                        'mode':'frames' if use_frames else 'continuous',
                        'widget':'QSpinBox','minimum':0,'maximum':upper,
                        'widget_value':value,'serialized_type':'int','passed':True})
            # Verify Qt's configured limits with integers, without claiming an
            # API100 cap or inventing native counts/ammunition-source ownership.
            widget.setValue(-1);assert widget.value()==0
            widget.setValue(upper+1);assert widget.value()==upper
            widget.setValue(0)
        receipt['section57_input_scope']='Four actual QSpinBox controls emit int and retain GUI0..100/stack0..2 limits. Boolean API rejection and accepted API counts above GUI bounds are regression coverage, not fake GUI inputs or native event caps.'

        # Section58: only synthetic public state in the already isolated window.
        # No saved/private run, recognition frame or recruitment event is read.
        assert module.RUN_STATE.parent==isolated and module.OPERATOR_STATE.parent==isolated
        state_snapshot=deepcopy(window.run.state)
        account_snapshot=deepcopy(window.operator_observations)
        run_training_snapshot=window.use_run_training.isChecked()
        emergency_relic='rogue_6_relic_cargo_10';op='silverash'
        fields={'elite':2,'level':90,'potential':1,'trust':100,
                'module_id':None,'module_level':0}
        ranks={'1':10,'2':10,'3':10}
        def inject_origin(kind,scope='run'):
            member={'id':op,'scope':scope,'present':True,'fields':deepcopy(fields),
                    'skill_ranks':dict(ranks),'recruitment_kind':kind,
                    'char_buff_ids':[],'char_buffs_complete':False}
            window.run.state['operators']={op:member} if scope=='run' else {}
            window.operator_observations[op]={**deepcopy(member),'scope':'account'}
            window.select_operator(op);window.update_operator()
            window.skill.setCurrentIndex(window.skill.findData(3))
            window.timing_scenario.clear();window.window_seconds.setValue(3)
        def emergency_record(result):
            return next(record for record in result['relic_resolution']['records']
                        if record['id']==emergency_relic)
        try:
            window.use_run_training.setChecked(True)
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                inject_origin(None);relics([]);plain=deepcopy(click_result())
                relics([emergency_relic]);pending_reference=None
                for kind in (None,'unknown','non_emergency','emergency_hire'):
                    inject_origin(kind);result=click_result();record=emergency_record(result)
                    args=window.damage_result['scenario']
                    assert args['recruitment_kind']==kind
                    assert window.current_operator_state()['scope']=='run'
                    if kind in (None,'unknown'):
                        assert record['status']=='incomplete'
                        assert record['missing_conditions']==['emergency_hire']
                        assert record['applied']==[]
                        assert result['relic_resolution']['complete'] is False
                        assert result['estimate']['base_stats']==plain['estimate']['base_stats']
                        actual_human=window.damage_text.toPlainText()
                        assert '同行者：条件缺失或机制未覆盖；缺 应急招募来源' in actual_human
                        assert '同行者：尚未确认条件 应急招募来源，未按0或满层套用。' in actual_human
                        assert 'emergency_hire' not in actual_human
                        if kind is None:pending_reference=deepcopy(result)
                        else:assert result==pending_reference
                    else:
                        assert record['status']=='applied' and not record['missing_conditions']
                        assert result['relic_resolution']['complete'] is True
                        assert len(record['applied'])==3
                        factor=.4 if kind=='emergency_hire' else 0
                        assert {effect['kind'] for effect in record['applied']}=={'attack_pct','hp_pct','defense_pct'}
                        assert all(effect['value']==factor for effect in record['applied'])
                        if kind=='non_emergency':
                            assert result['estimate']['base_stats']==plain['estimate']['base_stats']
                        else:
                            assert abs(result['estimate']['base_stats']['attack']-
                                       plain['estimate']['base_stats']['attack']*1.4)<1e-7
                            assert '应急雇佣' in window.training_status.text()
                    checks.append({'scope':'actual_isolated_run_recruitment_source_condition',
                        'section':58,'mode':'frames' if use_frames else 'continuous',
                        'operator':op,'state_injection':'temporary in-memory public state only',
                        'recruitment_kind':kind,'serialized_kind':args['recruitment_kind'],
                        'missing_conditions':record['missing_conditions'],
                        'applied_effects':record['applied'],
                        'base_attack':result['estimate']['base_stats']['attack'],'passed':True})
                # Account-only source is not a confirmed current-run source.
                inject_origin('emergency_hire',scope='account')
                result=click_result();record=emergency_record(result)
                assert window.damage_result['scenario']['recruitment_kind'] is None
                assert record['missing_conditions']==['emergency_hire'] and not record['applied']
                assert result['estimate']['base_stats']==plain['estimate']['base_stats']
                checks.append({'scope':'actual_account_recruitment_source_not_used_for_run_condition',
                    'section':58,'mode':'frames' if use_frames else 'continuous',
                    'account_kind':'emergency_hire','submitted_kind':None,'passed':True})
                inject_origin('emergency_hire');window.use_run_training.setChecked(False)
                result=click_result();record=emergency_record(result)
                assert window.damage_result['scenario']['recruitment_kind'] is None
                assert record['missing_conditions']==['emergency_hire'] and not record['applied']
                checks.append({'scope':'actual_run_training_toggle_preserves_source_boundary',
                    'section':58,'mode':'frames' if use_frames else 'continuous',
                    'run_training_enabled':False,'submitted_kind':None,'passed':True})
                window.use_run_training.setChecked(True)
        finally:
            window.run.state=state_snapshot
            window.operator_observations=account_snapshot
            window.use_run_training.setChecked(run_training_snapshot)
            window.update_operator();relics([])
        receipt['section58_state_scope']='Recruitment origins are injected only into this temporary MainWindow public in-memory state, then restored. This checks current_operator_state, the real run-training checkbox, scenario serialization, relic pending/known output and report; no actual OCR/recruitment/private-state lifecycle is certified.'

        # Section59: source-specific unknown reports and known magic subtotals.
        # New complete sentences may be refined by root; stable source labels,
        # actual unknown boundaries and the absence of an unselected relic bind.
        from rouge.river_effects import RELIC_ID as river_id
        train('char_1042_phatm2',{'elite':2,'level':60,'potential':1,'trust':100,
                                'module_id':None,'module_level':0})
        window.target_enemy.setCurrentIndex(0)
        assert window.target_enemy.currentData() is None
        window.defense.setValue(0);window.resistance.setValue(0)
        for owner,key,_skills,widget in window.model_option_widgets:
            if owner=='char_1042_phatm2':
                default=next(entry[2] for entry in module.OPTIONS[owner] if entry[0]==key)
                widget.setChecked(default) if isinstance(widget,QCheckBox) else widget.setValue(default)
        incoming=next(widget for owner,key,_skills,widget in window.model_option_widgets
                      if owner=='char_1042_phatm2' and key=='enemy_attack_count')
        for number,horizon,count,reference_key,label in (
                (1,1,0,'neural_s1_reference','暗夜回声 · 束缚倍率待核验'),
                (2,30,20,'neural_incoming_reference','堕梦 · 目标攻击时间待确认')):
            window.skill.setCurrentIndex(window.skill.findData(number))
            incoming.setValue(count);window.timing_scenario.clear()
            window.limit_window.setChecked(True);window.window_seconds.setValue(horizon);relics([])
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames);result=click_result()
                actual=window.damage_text.toPlainText();skill=result['estimate']['skill']
                subtotal=result['known_damage_subtotals']['window_damage']
                section=next(s for s in result['report']['sections'] if s['id']=='known_damage_subtotals')
                assert result['total_damage'] is None and skill['window_damage'] is None
                assert result['complete'] is False and result['estimate']['complete'] is False
                assert subtotal>0
                assert abs(subtotal-sum(c['total'] for c in result['components']
                                       if c['damage_type']=='magic'))<1e-7
                assert reference_key in result and 'neural_relic_reference' not in result
                assert not any(r['id']==river_id for r in result['relic_resolution']['records'])
                assert window.damage_result['scenario']['relic_ids']==[]
                assert '河谷祭祈' not in actual
                assert label in actual and '观察窗口已计伤害小计' in actual
                assert any('不能当作完整' in note for note in section['notes'])
                source_note=('暗夜回声的束缚倍率首次生效与刷新顺序尚未核验；小计不含受其影响的未知神经爆发。'
                             if number==1 else
                             '堕梦的目标普通攻击次数没有事件时刻；小计不含受其影响的未知神经爆发。')
                assert source_note in section['notes'] and source_note in actual
                assert all('河谷祭祈' not in note for note in section['notes'])
                if number==1:assert 'neural_incoming_reference' not in result
                else:
                    assert 'neural_s1_reference' not in result and 'neural_bait_reference' not in result
                    assert '目标首个普通攻击时刻：未知' in actual and '观察窗口总伤：未知' in actual
                checks.append({'scope':'actual_no_river_damage_subtotal_source',
                    'section':59,'operator':'char_1042_phatm2','skill':number,
                    'mode':'frames' if use_frames else 'continuous',
                    'enemy_attack_count':count,'window_seconds':horizon,
                    'actual_damage':None,'known_magic_window_subtotal':subtotal,
                    'subtotal_notes':section['notes'],'source_label':label,
                    'unselected_river_name_absent':True,'passed':True})
        # A truly selected River still has its named, independently scoped info.
        window.frame_timing.setChecked(True);relics([river_id]);result=click_result()
        assert any(r['id']==river_id for r in result['relic_resolution']['records'])
        assert '河谷祭祈' in window.damage_text.toPlainText()
        assert result['total_damage'] is None and result['estimate']['skill']['window_damage'] is None
        checks.append({'scope':'actual_selected_river_reference_report_preserved',
            'section':59,'operator':'char_1042_phatm2','skill':2,
            'actual_damage':None,'selected_relic':river_id,'passed':True})
        # Held River supplies independent mechanism documentation without
        # attributing an unplaced shield subtotal to an absent neural source.
        train('mechanist',{'elite':2,'level':90,'potential':1,'trust':100,
                          'module_id':None,'module_level':0})
        window.skill.setCurrentIndex(window.skill.findData(2))
        window.shield_breaks.setValue(2);window.shield_duration_known.setChecked(False)
        window.limit_window.setChecked(True);window.window_seconds.setValue(10)
        window.timing_scenario.clear();relics([river_id])
        generic_subtotal_note='这些数值只包含已保留的本体来源参考，不含未核验的次生事件，不能当作完整输出。'
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames);result=click_result()
            actual=window.damage_text.toPlainText()
            section=next(s for s in result['report']['sections'] if s['id']=='known_damage_subtotals')
            assert result['total_damage'] is None and 'neural_relic_reference' not in result
            assert result['shield_break_reference']['hits_requested']==2
            assert result['shield_break_reference']['actual_break_times_seconds'] is None
            assert any(r['id']==river_id for r in result['relic_resolution']['records'])
            assert section['notes']==[generic_subtotal_note]
            assert generic_subtotal_note in actual
            assert all('河谷祭祈' not in note for note in section['notes'])
            assert any(s['id']=='river_limits' for s in result['report']['sections'])
            assert '河谷祭祈 · 已知边界与待确认' in actual
            assert '实际破屏/爆炸时刻：未知' in actual
            checks.append({'scope':'actual_held_river_reference_does_not_supply_shield_subtotal_source',
                'section':59,'operator':'mechanist','skill':2,
                'mode':'frames' if use_frames else 'continuous','shield_break_count':2,
                'selected_relic':river_id,'actual_damage':None,
                'neural_relic_reference_present':False,'subtotal_notes':section['notes'],
                'river_independent_reference_preserved':True,'passed':True})
        relics([]);window.timing_scenario.clear()
        # Section60 uses finalized source parameters and public API contracts.
        # This real checkbox selects a declared squad condition, not a clock.
        shu_widgets={key:widget for owner,key,_skills,widget in window.model_option_widgets
                     if owner=='char_2025_shu'}
        four_sui=shu_widgets['four_sui']
        assert isinstance(four_sui,QCheckBox)
        for key,widget in shu_widgets.items():widget.setChecked(False)
        train('char_2025_shu',{'elite':2,'level':90,'potential':1,'trust':100,
                             'module_id':None,'module_level':0})
        window.healing_targets.setValue(1);relics([])
        window.target_enemy.setCurrentIndex(0)
        assert window.target_enemy.currentData() is None
        window.defense.setValue(0);window.resistance.setValue(0)
        window.limit_window.setChecked(True);window.timing_scenario.clear()
        def assert_shu_clock(result,plain,number,use_frames,horizon,enemy_lifetime=None):
            args=window.damage_result['scenario'];skill=result['estimate']['skill']
            ref=result['shu_periodic_sp_reference'];actual=window.damage_text.toPlainText()
            assert args['four_sui'] is True and type(four_sui.isChecked()) is bool
            assert abs(result['estimate']['base_stats']['attack']-
                       plain['estimate']['base_stats']['attack']*1.12)<1e-7
            assert ref['interval_seconds_parameter']==4
            assert ref['sp_per_pulse_parameter']==1
            assert ref['attack_bonus_parameter']==.12
            assert skill['sp_recovery_per_second']==1
            for field in ('first_tick_seconds','actual_tick_times_seconds','clock_origin',
                          'reset_rule','blocked_credit_rule'):assert ref[field] is None,field
            for field in ('native_attachment_verified','clock_verified','events_scheduled'):
                assert ref[field] is False,field
            assert ref['independent_sp_clock_reference']['excludes_four_sui_periodic_credit'] is True
            for field in ('initial_seconds','recharge_seconds','cycle_seconds',
                          'cycle_damage','cycle_healing','cycle_dps','cycle_hps'):
                assert skill[field] is None,(number,field,skill[field])
            assert skill['window_seconds']==horizon
            if horizon==0:
                assert result['total_damage']==0 and result['total_healing']==0
            if enemy_lifetime==0:
                assert result['total_damage']==0 and result['total_healing']>0
            assert result['timing']['phase_clock_unbound'] is True
            assert result['timing']['resource_and_damage_shared_clock'] is False
            assert result['complete'] is False and result['estimate']['complete'] is False
            assert result['scope']==result['estimate']['scenario_scope']
            assert any(section['id']=='shu_periodic_sp' for section in result['report']['sections'])
            assert '天有四时 · 周期技力待核验' in actual
            assert '实际周期首跳：未知' in actual and '结束后充能：未知' in actual
            checks.append({'scope':'actual_shu_four_sui_checkbox_periodic_sp_boundary',
                'section':60,'operator':'char_2025_shu','skill':number,
                'mode':'frames' if use_frames else 'continuous','window_seconds':horizon,
                'enemy_lifetime_seconds':enemy_lifetime,'widget':'QCheckBox',
                'four_sui_condition':True,'natural_sp_per_second':skill['sp_recovery_per_second'],
                'attack_bonus_parameter':ref['attack_bonus_parameter'],
                'periodic_interval_parameter':ref['interval_seconds_parameter'],
                'periodic_sp_parameter':ref['sp_per_pulse_parameter'],
                'actual_first_tick':None,'actual_recharge':None,'actual_cycle':None,
                'resource_clock_unbound':True,'passed':True})
        for number in (1,2,3):
            window.skill.setCurrentIndex(window.skill.findData(number))
            assert four_sui.isVisible() and four_sui.isEnabled()
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for horizon in (0,10):
                    window.window_seconds.setValue(horizon);window.timing_scenario.clear()
                    four_sui.setChecked(False);plain=deepcopy(click_result())
                    assert 'shu_periodic_sp_reference' not in plain
                    four_sui.setChecked(True);result=click_result()
                    assert_shu_clock(result,plain,number,use_frames,horizon)
        # Empty enemy lifetime does not prove a friendly resource source absent.
        window.skill.setCurrentIndex(window.skill.findData(2));window.window_seconds.setValue(10)
        window.timing_scenario.setPlainText(json.dumps({'target_disappears_seconds':0}))
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames)
            four_sui.setChecked(False);plain=deepcopy(click_result())
            four_sui.setChecked(True);result=click_result()
            assert_shu_clock(result,plain,2,use_frames,10,enemy_lifetime=0)
        # The same real checkbox below the original E2 talent gate adds nothing.
        train('char_2025_shu',{'elite':1,'level':80,'potential':1,'trust':100,
                             'module_id':None,'module_level':0},ranks={'1':7,'2':7})
        window.window_seconds.setValue(10);window.timing_scenario.clear()
        for number in (1,2):
            window.skill.setCurrentIndex(window.skill.findData(number))
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                four_sui.setChecked(False);plain=deepcopy(click_result())
                four_sui.setChecked(True);result=click_result()
                assert result==plain and 'shu_periodic_sp_reference' not in result
                checks.append({'scope':'actual_shu_four_sui_checkbox_original_talent_qualification',
                    'section':60,'operator':'char_2025_shu','elite':1,'skill':number,
                    'mode':'frames' if use_frames else 'continuous','skill_rank':7,
                    'four_sui_condition':True,'full_result_equal_to_unselected':True,'passed':True})
        four_sui.setChecked(False);window.timing_scenario.clear();relics([])
        receipt['section60_input_scope']='The actual four_sui QCheckBox declares a squad condition; E2 static attack bonus and original4s/1SP parameters remain, actual pulse/resource clocks remain unknown in empty and positive observation windows, and the E1 talent gate still excludes the effect. No first tick, owner clock, reset, blocked credit or native event was inferred.'

        supplemental_end=len(checks)
        receipt['supplemental_sections']=[56,57,58,59,60]
        receipt['supplemental_checks_56_60']=supplemental_end-supplemental_start
        assert receipt['supplemental_checks_56_60']==79,receipt['supplemental_checks_56_60']
        receipt['section60_final_checks_pending']=False
        assert receipt['section60_final_checks_pending'] is False,'Section60 source review is not finalized; do not treat this candidate as a complete UI runner'
        # Root freezes integrated source after commit; API probing is not GUI proof.

        # Sections61-65: real Qt producers, not invented bool/text spinbox input.
        new_start=len(checks);new_section_counts={}
        def strict_json(value):
            return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False)
        from rouge.operator_options import OPTIONS
        option_widgets={(owner,key):widget for owner,key,_skills,widget in window.model_option_widgets}
        def reset_owner_options(owner):
            for key,label,default,maximum,skills in OPTIONS.get(owner,[]):
                widget=option_widgets[(owner,key)]
                widget.setChecked(default) if isinstance(widget,QCheckBox) else widget.setValue(default)
        def report_metrics(result,section_id):
            sections=[section for section in result['report']['sections'] if section['id']==section_id]
            assert len(sections)==1,(section_id,len(sections))
            return {row['key']:row['value'] for row in sections[0]['metrics']}
        window.damage_technical.setChecked(False);window.timing_scenario.clear();relics([])
        window.limit_window.setChecked(True);window.window_seconds.setValue(10)
        window.target_enemy.setCurrentIndex(0);window.defense.setValue(0);window.resistance.setValue(0)
        window.cooperative.setChecked(False);window.fragile.setChecked(False)
        assert window.target_enemy.currentData() is None

        #61: all24 existing owner/key integer controls, covering23 distinct keys.
        # Raw bool rejection is API regression scope; real QSpinBox emits int.
        count_fields={'summon_count','casts_used','slash_kills','amiya_slash_kills',
            'incoming_hits','shield_contact_ticks','cold_state','dash_hits','bubble_bursts',
            'levitate_triggers','snow_entries','drone_warmup_hits','note_count',
            'bait_triggers','enemy_attack_count','palsy_triggers','palsy_overflow_hits',
            'connected_stones','trap_triggers','trap_dot_ticks','dragon_arrow_hits',
            'ghost_count','ghost_casts'}
        integer_controls=[(owner,key,default,maximum,skills)
            for owner,entries in OPTIONS.items() for key,label,default,maximum,skills in entries
            if key in count_fields]
        assert len(integer_controls)==24 and {row[1] for row in integer_controls}==count_fields
        section_start=len(checks)
        for owner,key,default,maximum,skills in integer_controls:
            profile=module.catalog()['operators'][owner]
            train(owner,{'elite':2,'level':profile['phases'][2]['max_level'],'potential':1,
                         'trust':100,'module_id':None,'module_level':0})
            number=skills[0];window.skill.setCurrentIndex(window.skill.findData(number))
            reset_owner_options(owner);window.healing_targets.setValue(1)
            widget=option_widgets[(owner,key)]
            assert isinstance(widget,QSpinBox) and widget.isVisible() and widget.isEnabled()
            assert widget.minimum()==0 and widget.maximum()==(4 if key=='summon_count' else maximum)
            if key=='ghost_casts':option_widgets[(owner,'ghost_count')].setValue(1)
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for value in (0,1):
                    widget.setValue(value);result=click_result();args=window.damage_result['scenario']
                    assert type(widget.value()) is int and type(args[key]) is int
                    assert args[key]==value
                    assert args['timing_mode']==('frames' if use_frames else 'continuous')
                    checks.append({'scope':'actual_all_integer_option_spinbox_serializer',
                        'section':61,'operator':owner,'skill':number,'key':key,
                        'mode':args['timing_mode'],'value':value,'widget':'QSpinBox',
                        'submitted_type':'int','gui_minimum':widget.minimum(),
                        'gui_maximum':widget.maximum(),'calculation_returned':True,'passed':True})
            widget.setValue(default)
        new_section_counts[61]=len(checks)-section_start
        assert new_section_counts[61]==len(integer_controls)*2*2
        receipt['section61_input_scope']='All24 real owner/key QSpinBox controls emit integer0/1;23 distinct queried keys are covered. API raw bool errors are separate regression evidence. GUI maximums are control limits, not new native stock/event/deployment caps.'

        #62: true/false are actual checkbox values above and below the E2 gate.
        section_start=len(checks);four_sui=option_widgets[('char_2025_shu','four_sui')]
        for elite,number,rank in ((2,3,10),(1,2,7)):
            train('char_2025_shu',{'elite':elite,'level':90 if elite==2 else 80,
                'potential':1,'trust':100,'module_id':None,'module_level':0},
                ranks={'1':rank,'2':rank,'3':rank})
            reset_owner_options('char_2025_shu');window.skill.setCurrentIndex(window.skill.findData(number))
            window.window_seconds.setValue(10);window.timing_scenario.clear()
            assert isinstance(four_sui,QCheckBox) and four_sui.isVisible() and four_sui.isEnabled()
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames);plain=None
                for flag in (False,True):
                    four_sui.setChecked(flag);result=click_result();args=window.damage_result['scenario']
                    assert type(four_sui.isChecked()) is bool and args['four_sui'] is flag
                    if not flag:
                        plain=deepcopy(result);assert 'shu_periodic_sp_reference' not in result
                    elif elite==1:
                        assert strict_json(result)==strict_json(plain)
                        assert 'shu_periodic_sp_reference' not in result
                    else:
                        ref=result['shu_periodic_sp_reference'];skill=result['estimate']['skill']
                        assert abs(result['estimate']['base_stats']['attack']-
                                   plain['estimate']['base_stats']['attack']*1.12)<1e-7
                        assert ref['interval_seconds_parameter']==4 and ref['sp_per_pulse_parameter']==1
                        assert ref['first_tick_seconds'] is None and ref['clock_verified'] is False
                        assert ref['events_scheduled'] is False
                        assert skill['initial_seconds'] is None and skill['recharge_seconds'] is None
                        assert skill['cycle_seconds'] is None
                        assert '实际周期首跳：未知' in window.damage_text.toPlainText()
                    checks.append({'scope':'actual_four_sui_typed_bool_qualification',
                        'section':62,'operator':'char_2025_shu','elite':elite,'skill':number,
                        'mode':args['timing_mode'],'value':flag,'widget':'QCheckBox',
                        'submitted_type':'bool','talent_qualified':elite==2,
                        'periodic_clock_verified':False,'passed':True})
        four_sui.setChecked(False);new_section_counts[62]=len(checks)-section_start
        assert new_section_counts[62]==8
        receipt['section62_input_scope']='Existing four_sui QCheckBox serializes genuine bool False/True; E1 excludes the talent, E2 preserves static attack and original4s/1SP parameters with actual resource clocks unknown. API text refusal cannot be submitted through this checkbox and is covered by regression.'

        #63: real declared integer count and original cultivation/module caps.
        section_start=len(checks);deepcl='char_110_deepcl';mod='uniequip_002_deepcl'
        count_widget=option_widgets[(deepcl,'summon_count')]
        deepcl_training=[({'elite':0,'level':45,'module_id':None,'module_level':0},4,2),
            ({'elite':1,'level':60,'module_id':None,'module_level':0},7,3),
            ({'elite':2,'level':70,'module_id':None,'module_level':0},10,4),
            ({'elite':2,'level':39,'module_id':mod,'module_level':3},10,4),
            ({'elite':2,'level':40,'module_id':mod,'module_level':1},10,7),
            ({'elite':2,'level':40,'module_id':mod,'module_level':2},10,7),
            ({'elite':2,'level':40,'module_id':mod,'module_level':3},10,7)]
        expected63=0
        for fields,rank,cap in deepcl_training:
            train(deepcl,{**fields,'potential':1,'trust':100},
                  ranks={'1':rank,'2':rank})
            reset_owner_options(deepcl)
            for number in ((1,) if fields['elite']==0 else (1,2)):
                window.skill.setCurrentIndex(window.skill.findData(number))
                assert isinstance(count_widget,QSpinBox) and count_widget.isVisible() and count_widget.isEnabled()
                assert count_widget.minimum()==0 and count_widget.maximum()==cap
                for use_frames in (True,False):
                    window.frame_timing.setChecked(use_frames)
                    for value in (0,1,cap):
                        count_widget.setValue(value);result=click_result();args=window.damage_result['scenario']
                        assert type(args['summon_count']) is int and args['summon_count']==value
                        rates=report_metrics(result,'summons')
                        assert type(rates['summon_count']) is int and rates['summon_count']==value
                        assert rates['concurrent_limit']==cap
                        if number==1:
                            regeneration=report_metrics(result,'regeneration')
                            bb=module.catalog()['operators'][deepcl]['skills'][0]['levels'][rank-1]['values']
                            assert regeneration['per_token_rate']==bb['hp_recovery_per_sec']
                            assert regeneration['all_tokens_rate']==bb['hp_recovery_per_sec']*value
                        if cap==7:
                            module_metrics=report_metrics(result,'relic_token_token_10001_deepcl_tentac')
                            assert type(module_metrics['model_count']) is int and module_metrics['model_count']==value
                            assert module_metrics['held_limit']==7 and module_metrics['concurrent_limit']==7
                            assert '关卡可用部署位、地块和当前库存约束' in window.damage_text.toPlainText()
                        assert '局外假设' in window.damage_text.toPlainText()
                        checks.append({'scope':'actual_deepcolor_declared_integer_count_report',
                            'section':63,'operator':deepcl,'skill':number,'skill_rank':rank,
                            'elite':fields['elite'],'level':fields['level'],'module_id':fields['module_id'],
                            'module_level':fields['module_level'],'mode':args['timing_mode'],
                            'value':value,'widget':'QSpinBox','submitted_type':'int',
                            'gui_concurrent_cap':cap,'actual_stock_or_deployment_clock_verified':False,'passed':True})
                        expected63+=1
        count_widget.setValue(1);new_section_counts[63]=len(checks)-section_start
        assert new_section_counts[63]==expected63
        receipt['section63_input_scope']='Actual Deepcolor QSpinBox produces declared integer0/1/currentcap with existing E0/E1/E2 and SUM-Y unlock gates, typed report counts and S1 fixed per-token regeneration reference. Legal API numeric strings are verified separately; no actual stock, presence, concurrency, deployment event or recovery tick is inferred.'

        #64: select both real checkbox states; never infer the API flag from GUI default.
        section_start=len(checks)
        train('silverash',{'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0})
        window.skill.setCurrentIndex(window.skill.findData(3));window.window_seconds.setValue(10)
        window.timing_scenario.clear()
        assert isinstance(window.fragile,QCheckBox) and window.fragile.isVisible() and window.fragile.isEnabled()
        assert isinstance(window.cooperative,QCheckBox) and window.cooperative.isVisible()
        for rank in (1,7,10):
            train('silverash',{'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0},
                  ranks={'1':rank,'2':rank,'3':rank})
            window.skill.setCurrentIndex(window.skill.findData(3))
            factor=module.catalog()['operators']['silverash']['skills'][2]['levels'][rank-1]['values']['damage_scale']
            assert factor==({1:1.15,7:1.25,10:1.3}[rank])
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for cooperation in (False,True):
                    window.cooperative.setChecked(cooperation);plain=None
                    for flag in (False,True):
                        window.fragile.setChecked(flag);result=click_result();args=window.damage_result['scenario']
                        assert args['preexisting_fragile'] is flag and type(window.fragile.isChecked()) is bool
                        assert args['cooperative'] is cooperation and type(window.cooperative.isChecked()) is bool
                        components=result['components']
                        assert [row['name'] for row in components]==(['本体丹增','协同丹增'] if cooperation else ['本体丹增'])
                        assert all(row['damage_type']=='physical' for row in components)
                        if not flag:plain=deepcopy(result)
                        else:
                            assert abs(result['total_damage']-plain['total_damage']*factor)<1e-7
                            for old,row in zip(plain['components'],components):
                                assert row['hits']==old['hits']
                                assert abs(row['per_hit']-old['per_hit']*factor)<1e-7
                        checks.append({'scope':'actual_fragile_and_cooperative_typed_checkbox_controls',
                            'section':64,'operator':'silverash','skill':3,'skill_rank':rank,
                            'mode':args['timing_mode'],'preexisting_fragile':flag,'cooperative':cooperation,
                            'submitted_types':'bool/bool','selected_skill_factor':factor,
                            'native_attachment_or_overlap_rule_verified':False,'passed':True})
        train('silverash',{'elite':1,'level':80,'potential':1,'trust':100,'module_id':None,'module_level':0},
              ranks={'1':7,'2':7})
        assert window.skill.findData(3)==-1
        window.skill.setCurrentIndex(window.skill.findData(2))
        assert not window.fragile.isVisible() and not window.cooperative.isVisible()
        window.cooperative.setChecked(False)
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames);plain=None
            for flag in (False,True):
                window.fragile.setChecked(flag);result=click_result();args=window.damage_result['scenario']
                assert args['preexisting_fragile'] is flag
                if not flag:plain=deepcopy(result)
                else:assert strict_json(result)==strict_json(plain)
                checks.append({'scope':'actual_fragile_checkbox_inactive_skill_qualification',
                    'section':64,'operator':'silverash','elite':1,'skill':2,'skill_rank':7,
                    'mode':args['timing_mode'],'preexisting_fragile':flag,
                    's3_unavailable':True,'checkbox_hidden':True,'passed':True})
        window.fragile.setChecked(False);window.cooperative.setChecked(False)
        new_section_counts[64]=len(checks)-section_start
        assert new_section_counts[64]==3*2*2*2+2*2
        receipt['section64_input_scope']='Actual fragile/cooperative QCheckBox states serialize bool, preserve chosen S3 rank1/7/10 factor1.15/1.25/1.3 and physical component arithmetic; E1 excludes S3 and hides these controls for S2. Text rejection is API-only regression. No first-hit attachment, overlapping-source identity, max-source composition or native dynamic coverage is certified.'

        #65: only real integer bait count; original positive/empty boundary remains.
        section_start=len(checks);phatm='char_1042_phatm2'
        train(phatm,{'elite':2,'level':60,'potential':1,'trust':100,'module_id':None,'module_level':0})
        reset_owner_options(phatm);window.skill.setCurrentIndex(window.skill.findData(2))
        bait=option_widgets[(phatm,'bait_triggers')]
        assert isinstance(bait,QSpinBox) and bait.isVisible() and bait.isEnabled()
        assert bait.minimum()==0 and bait.maximum()==100
        scopes=[('positive',10,{}),('zero_window',0,{}),
                ('zero_lifetime',10,{'target_disappears_seconds':0}),
                ('empty_target_windows',10,{'target_windows':[]})]
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames)
            for scope_name,horizon,timing in scopes:
                window.window_seconds.setValue(horizon)
                window.timing_scenario.setPlainText(json.dumps(timing) if timing else '')
                for value in (0,1):
                    bait.setValue(value);result=click_result();args=window.damage_result['scenario']
                    assert type(bait.value()) is int and type(args['bait_triggers']) is int
                    assert args['bait_triggers']==value
                    sections=[section['id'] for section in result['report']['sections']]
                    if value==0:
                        assert 'neural_bait_reference' not in result and 'neural_bait' not in sections
                        assert '本能的召唤 · 诱饵持续效果待核验' not in window.damage_text.toPlainText()
                    else:
                        ref=result['neural_bait_reference']
                        assert type(ref['triggers_requested']) is int and ref['triggers_requested']==1
                        assert ref['snapshot_attack'] is None and ref['first_tick_seconds'] is None
                        assert ref['events_scheduled'] is False
                        metrics=report_metrics(result,'neural_bait')
                        assert metrics['trigger_count']==1 and metrics['snapshot_attack'] is None
                        assert metrics['first_tick'] is None
                        assert '本能的召唤 · 诱饵持续效果待核验' in window.damage_text.toPlainText()
                        if scope_name in ('zero_window','zero_lifetime'):
                            assert ref['affected_damage_phases']['window'] is False
                        else:
                            assert result['total_damage'] is None and result['estimate']['skill']['window_dps'] is None
                    if scope_name in ('zero_window','zero_lifetime'):assert result['total_damage']==0
                    checks.append({'scope':'actual_bait_integer_count_and_unknown_event_boundary',
                        'section':65,'operator':phatm,'skill':2,'mode':args['timing_mode'],
                        'scenario_scope':scope_name,'window_seconds':horizon,'value':value,
                        'widget':'QSpinBox','submitted_type':'int','reference_present':value>0,
                        'actual_snapshot_attack':None,'actual_first_tick':None,'events_scheduled':False,
                        'gui_maximum_not_native_cap':100,'passed':True})
            window.skill.setCurrentIndex(window.skill.findData(1));window.window_seconds.setValue(10)
            window.timing_scenario.clear();bait.setValue(1)
            assert not bait.isVisible()
            result=click_result();args=window.damage_result['scenario']
            assert 'bait_triggers' not in args and 'neural_bait_reference' not in result
            checks.append({'scope':'actual_bait_integer_widget_inactive_skill_serializer',
                'section':65,'operator':phatm,'skill':1,'mode':args['timing_mode'],
                'widget_hidden':True,'inactive_key_submitted':False,'passed':True})
            window.skill.setCurrentIndex(window.skill.findData(2))
        bait.setValue(0);window.timing_scenario.clear();relics([])
        new_section_counts[65]=len(checks)-section_start
        assert new_section_counts[65]==len(scopes)*2*2+2
        receipt['section65_input_scope']='Real bait_triggers QSpinBox integer0 has no bait reference; positive1 retains unplaced effect with actual deployment snapshot/firsttick unknown, and zero observation/enemy lifetime preserve original zero-window output. API string aliases use separate regression; no fixed trigger interval, original maxcap, scheduled tick or overlapping effect is inferred.'

        new_end=len(checks)
        receipt['supplemental_sections_61_65']=[61,62,63,64,65]
        receipt['supplemental_checks_by_section_61_65']=new_section_counts
        receipt['supplemental_checks_61_65']=new_end-new_start
        assert sum(new_section_counts.values())==new_end-new_start
        receipt['section65_final_checks_pending']=False
        assert receipt['section65_final_checks_pending'] is False,'Section65 source review is not finalized; do not execute this draft as a complete UI runner'
        # Root replaces the pending marker after final schema/source review,
        # freezes integrated source on a clean commit and alone executes Wine.

        #66-70: actual Qt values and actual visible results. API aliases/text are separate.
        latest_start=len(checks);latest_section_counts={}
        window.damage_technical.setChecked(False);window.timing_scenario.clear();relics([])
        window.target_enemy.setCurrentIndex(0);window.defense.setValue(0);window.resistance.setValue(0)
        window.limit_window.setChecked(True);window.healing_targets.setValue(1)
        window.cooperative.setChecked(False);window.fragile.setChecked(False)
        scopes070=[('positive',10,{}),('zero_window',0,{}),
            ('zero_lifetime',10,{'target_disappears_seconds':0}),
            ('empty_target_windows',10,{'target_windows':[]})]
        def set_observation070(horizon,timing):
            window.window_seconds.setValue(horizon)
            window.timing_scenario.setPlainText(json.dumps(timing) if timing else '')
        def require_real_int070(widget,args,key,value):
            assert isinstance(widget,QSpinBox) and widget.isVisible() and widget.isEnabled()
            assert type(widget.value()) is int and widget.value()==value
            assert type(args[key]) is int and args[key]==value
        def require_real_bool070(widget,args,key,value):
            assert isinstance(widget,QCheckBox) and widget.isVisible() and widget.isEnabled()
            assert type(widget.isChecked()) is bool and widget.isChecked() is value
            assert args[key] is value

        section_start=len(checks);wisdel='char_1035_wisdel'
        train(wisdel,{'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0})
        reset_owner_options(wisdel)
        ghosts_widget=option_widgets[(wisdel,'ghost_count')];casts_widget=option_widgets[(wisdel,'ghost_casts')]
        assert ghosts_widget.minimum()==0 and ghosts_widget.maximum()==3
        assert casts_widget.minimum()==0 and casts_widget.maximum()==1000
        for number in (1,2,3):
            window.skill.setCurrentIndex(window.skill.findData(number))
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for scope_name,horizon,timing in scopes070:
                    set_observation070(horizon,timing)
                    for ghosts,casts in ((0,0),(0,1),(1,0),(1,1),(3,2)):
                        ghosts_widget.setValue(ghosts);casts_widget.setValue(casts)
                        invalid=horizon==0 and ghosts>0 and casts>0
                        if invalid:
                            # A real, numeric combination the original UI can submit.
                            supplemental_button.click();app.processEvents()
                            assert window.damage_result is None
                            assert window.damage_text.toPlainText()=='零长度观察窗口不能声明魂灵施放命中。'
                            assert type(ghosts_widget.value()) is int and ghosts_widget.value()==ghosts
                            assert type(casts_widget.value()) is int and casts_widget.value()==casts
                        else:
                            result=click_result();args=window.damage_result['scenario']
                            require_real_int070(ghosts_widget,args,'ghost_count',ghosts)
                            require_real_int070(casts_widget,args,'ghost_casts',casts)
                            require_wisdel(result,args,window.damage_text.toPlainText(),scope_name)
                        checks.append({'scope':'actual_wisdel_integer_presence_gate_and_declared_cast_reference',
                            'section':66,'operator':wisdel,'skill':number,
                            'mode':'frames' if use_frames else 'continuous','observation_scope':scope_name,
                            'ghost_count':ghosts,'ghost_casts':casts,'submitted_types':'int/int',
                            'expected_numeric_input_error_visible':invalid,
                            'actual_shadow_clock_or_presence_verified':False,'passed':True})
        ghosts_widget.setValue(0);casts_widget.setValue(0)
        latest_section_counts[66]=len(checks)-section_start;assert latest_section_counts[66]==120
        receipt['section66_input_scope']='Real ghost_count/casts QSpinBoxes submit integers. Zero ghosts ignores declared casts; positive casts remain conditional without placement/cast time or full-phase attribution. Twelve genuinely numeric zero-window combinations show the existing exact error and clear the prior result; these are expected error checks, not successful calculations or API text inputs.'

        section_start=len(checks);phatm='char_1042_phatm2'
        train(phatm,{'elite':2,'level':60,'potential':1,'trust':100,'module_id':None,'module_level':0})
        reset_owner_options(phatm);incoming_widget=option_widgets[(phatm,'enemy_attack_count')]
        resistance_widget=option_widgets[(phatm,'enemy_buildup_resistance')]
        assert incoming_widget.minimum()==0 and incoming_widget.maximum()==10000
        def incoming_case070(number,use_frames,scope_name,horizon,timing,count,qualified=True,immune=False):
            set_observation070(horizon,timing);incoming_widget.setValue(count)
            result=click_result();args=window.damage_result['scenario']
            require_real_int070(incoming_widget,args,'enemy_attack_count',count)
            require_incoming(result,args,window.damage_text.toPlainText(),scope_name,qualified,immune)
            checks.append({'scope':'actual_enemy_attack_integer_metadata_and_unplaced_clock',
                'section':67,'operator':phatm,'skill':number,
                'mode':'frames' if use_frames else 'continuous','observation_scope':scope_name,
                'enemy_attack_count':count,'submitted_type':'int','talent_qualified':qualified,
                'buildup_immune':immune,'actual_attack_times':None,'events_scheduled':False,'passed':True})
        for number in (1,2,3):
            window.skill.setCurrentIndex(window.skill.findData(number));resistance_widget.setValue(0)
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for scope_name,horizon,timing in scopes070:
                    for count in (0,1):incoming_case070(number,use_frames,scope_name,horizon,timing,count)
                incoming_case070(number,use_frames,'positive',10,{},20)
                resistance_widget.setValue(100)
                for count in (0,1):incoming_case070(number,use_frames,'positive',10,{},count,immune=True)
                resistance_widget.setValue(0)
        train(phatm,{'elite':1,'level':80,'potential':1,'trust':100,'module_id':None,'module_level':0},ranks={'1':7,'2':7})
        assert window.skill.findData(3)==-1
        for number in (1,2):
            window.skill.setCurrentIndex(window.skill.findData(number))
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for count in (0,1):incoming_case070(number,use_frames,'positive',10,{},count,qualified=False)
        incoming_widget.setValue(0);latest_section_counts[67]=len(checks)-section_start
        assert latest_section_counts[67]==74
        receipt['section67_input_scope']='Real target-attack QSpinBox integers0/1/20 retain metadata70 per-attack parameter, but no attack timestamps or uniform schedule. Zero observation preserves cast pending/window0; lifetime0, immunity100 and E1 talent gates exclude this source. Empty target windows do not establish event timing and continuous subtotals are not forced to frame-mode zero.'

        section_start=len(checks);shu='char_2025_shu'
        different_widget=option_widgets[(shu,'three_professions')]
        same_widget=option_widgets[(shu,'three_same_profession')];four_widget=option_widgets[(shu,'four_sui')]
        assert different_widget.text()=='三种不同职业在场' and same_widget.text()=='三名相同职业在场'
        for elite,level,rank,numbers,fours in ((2,90,10,(1,2,3),(False,True)),
                (1,80,7,(1,2),(False,)),(0,50,4,(1,),(False,))):
            train(shu,{'elite':elite,'level':level,'potential':1,'trust':100,'module_id':None,'module_level':0},
                  ranks={'1':rank,'2':rank,'3':rank})
            reset_owner_options(shu);set_observation070(10,{})
            for number in numbers:
                window.skill.setCurrentIndex(window.skill.findData(number))
                for use_frames in (True,False):
                    window.frame_timing.setChecked(use_frames)
                    for four in fours:
                        four_widget.setChecked(four);plain=None
                        for different,same in ((False,False),(True,False),(False,True),(True,True)):
                            different_widget.setChecked(different);same_widget.setChecked(same)
                            result=click_result();args=window.damage_result['scenario']
                            require_real_bool070(different_widget,args,'three_professions',different)
                            require_real_bool070(same_widget,args,'three_same_profession',same)
                            require_real_bool070(four_widget,args,'four_sui',four)
                            if not different and not same:plain=deepcopy(result)
                            require_professions(result,args,window.damage_text.toPlainText(),plain,elite==2)
                            checks.append({'scope':'actual_shu_profession_checkbox_combinations_and_qualification',
                                'section':68,'operator':shu,'elite':elite,'skill':number,'skill_rank':rank,
                                'mode':args['timing_mode'],'three_professions':different,
                                'three_same_profession':same,'four_sui':four,'submitted_types':'bool/bool/bool',
                                'actual_squad_count_or_periodic_clock_verified':False,'passed':True})
        reset_owner_options(shu);latest_section_counts[68]=len(checks)-section_start
        assert latest_section_counts[68]==72
        receipt['section68_input_scope']='Actual different/same-profession QCheckBox combinations are bool; E2 affects only selected Shu HP12% and attack speed12, E0/E1 results remain unchanged. Four-sui coexistence retains unknown periodic clocks. This declares conditions without reading actual squad counts or certifying a team-wide application.'

        section_start=len(checks)
        train('silverash',{'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0},
              ranks={'1':4,'2':4,'3':4})
        window.skill.setCurrentIndex(window.skill.findData(3))
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames)
            for scope_name,horizon,timing in scopes070:
                set_observation070(horizon,timing);controls={}
                for cooperation in (False,True):
                    window.cooperative.setChecked(cooperation)
                    for fragile in (False,True):
                        window.fragile.setChecked(fragile);result=click_result();args=window.damage_result['scenario']
                        require_real_bool070(window.cooperative,args,'cooperative',cooperation)
                        require_real_bool070(window.fragile,args,'preexisting_fragile',fragile)
                        if not cooperation:controls[fragile]=deepcopy(result)
                        require_cooperative(result,args,window.damage_text.toPlainText(),controls[fragile],scope_name)
                        checks.append({'scope':'actual_cooperative_checkbox_explicit_coverage_condition',
                            'section':69,'operator':'silverash','skill':3,'skill_rank':4,
                            'mode':args['timing_mode'],'observation_scope':scope_name,
                            'cooperative':cooperation,'preexisting_fragile':fragile,'submitted_types':'bool/bool',
                            'actual_position_or_synchronized_hit_clock_verified':False,'passed':True})
        train('silverash',{'elite':0,'level':50,'potential':1,'trust':100,'module_id':None,'module_level':0},ranks={'1':1})
        assert window.skill.findData(3)==-1;window.skill.setCurrentIndex(window.skill.findData(1))
        assert not window.cooperative.isVisible();window.fragile.setChecked(False);set_observation070(10,{})
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames);plain=None
            for cooperation in (False,True):
                window.cooperative.setChecked(cooperation);result=click_result();args=window.damage_result['scenario']
                assert args['cooperative'] is cooperation and type(window.cooperative.isChecked()) is bool
                if not cooperation:plain=deepcopy(result)
                else:assert strict_json(result)==strict_json(plain)
                checks.append({'scope':'actual_cooperative_global_bool_inactive_skill',
                    'section':69,'operator':'silverash','elite':0,'skill':1,
                    'mode':args['timing_mode'],'cooperative':cooperation,'checkbox_hidden':True,'passed':True})
        window.cooperative.setChecked(False);window.fragile.setChecked(False)
        latest_section_counts[69]=len(checks)-section_start;assert latest_section_counts[69]==36
        receipt['section69_input_scope']='Explicit cooperative/fragile QCheckBox bool states preserve existing physical component math and rank4 declaration across empty/positive observations. E0 S1 ignores the global cooperative flag and offers no S3. API text rejection, native placement, synchronized events and overlap identity remain separate.'

        section_start=len(checks);tile_widget=option_widgets[(shu,'enemy_on_sown_tile')]
        assert tile_widget.text()=='存在地面敌人处于播种地块'
        for rank in (1,7,10):
            train(shu,{'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0},
                  ranks={'1':rank,'2':rank,'3':rank})
            reset_owner_options(shu);window.skill.setCurrentIndex(window.skill.findData(3))
            bb=module.catalog()['operators'][shu]['skills'][2]['levels'][rank-1]['values']
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for four in (False,True):
                    four_widget.setChecked(four)
                    for scope_name,horizon,timing in scopes070[:3]:
                        set_observation070(horizon,timing);plain=None
                        for tile in (False,True):
                            tile_widget.setChecked(tile);result=click_result();args=window.damage_result['scenario']
                            require_real_bool070(tile_widget,args,'enemy_on_sown_tile',tile)
                            require_real_bool070(four_widget,args,'four_sui',four)
                            assert window.target_enemy.currentData() is None and 'target_enemy' not in args
                            if not tile:plain=deepcopy(result)
                            require_sown(result,args,window.damage_text.toPlainText(),plain,scope_name,bb)
                            if rank==10 and use_frames and not four and scope_name=='positive' and tile:
                                assert tile_widget.grab().save(str(OUT/'wine-sown-tile-control-080.png'))
                                receipt['section70_actual_checkbox_screenshot']='wine-sown-tile-control-080.png'
                            checks.append({'scope':'actual_ground_enemy_presence_label_and_sown_checkbox',
                                'section':70,'operator':shu,'skill':3,'skill_rank':rank,
                                'mode':args['timing_mode'],'observation_scope':scope_name,
                                'label':tile_widget.text(),'enemy_on_sown_tile':tile,'four_sui':four,
                                'submitted_types':'bool/bool','current_target_selected':False,
                                'e_atk_parameter':bb['e_atk'],'e_attack_speed_parameter':bb['e_attack_speed'],
                                'actual_ground_presence_or_position_verified':False,'passed':True})
        train(shu,{'elite':1,'level':80,'potential':1,'trust':100,'module_id':None,'module_level':0},ranks={'1':7,'2':7})
        reset_owner_options(shu);assert window.skill.findData(3)==-1;set_observation070(10,{})
        for number in (1,2):
            window.skill.setCurrentIndex(window.skill.findData(number));assert not tile_widget.isVisible()
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames);plain=None
                for tile in (False,True):
                    tile_widget.setChecked(tile);result=click_result();args=window.damage_result['scenario']
                    assert type(tile_widget.isChecked()) is bool and tile_widget.isChecked() is tile
                    assert 'enemy_on_sown_tile' not in args
                    if not tile:plain=deepcopy(result)
                    else:assert strict_json(result)==strict_json(plain)
                    checks.append({'scope':'actual_sown_checkbox_inactive_skill_key_not_submitted',
                        'section':70,'operator':shu,'elite':1,'skill':number,'mode':args['timing_mode'],
                        'hidden_checkbox_state':tile,'inactive_key_submitted':False,'passed':True})
        reset_owner_options(shu);window.timing_scenario.clear();relics([])
        latest_section_counts[70]=len(checks)-section_start;assert latest_section_counts[70]==80
        receipt['section70_input_scope']='Actual checkbox label declares the existence of a ground enemy on a sown tile, not the selected target location. Genuine bool states retain original skill parameters/empty boundaries and four-sui unknown clock. No ground_type filter, position detection, actual coverage, trigger or teleport clock is inferred; S1/S2 omit this inactive key.'
        latest_end=len(checks)
        receipt['supplemental_sections_66_70']=[66,67,68,69,70]
        receipt['supplemental_checks_by_section_66_70']=latest_section_counts
        receipt['supplemental_checks_66_70']=latest_end-latest_start
        assert sum(latest_section_counts.values())==latest_end-latest_start
        receipt['section70_final_checks_pending']=False
        assert receipt['section70_final_checks_pending'] is False

        #71-75 genuine Qt controls and read-only public observation previews.
        from PySide6.QtWidgets import QDoubleSpinBox
        current_start=len(checks);current_section_counts={}
        window.damage_technical.setChecked(False);relics([])
        window.target_enemy.setCurrentIndex(0);window.defense.setValue(0);window.resistance.setValue(0)
        window.limit_window.setChecked(True);window.healing_targets.setValue(1)
        window.cooperative.setChecked(False);window.fragile.setChecked(False)
        window.deployment_elapsed.setValue(0)
        from rouge.run_config import config_data
        config075=config_data();design075=cases075(config075['squads'])
        state075=deepcopy(window.run.state);account075=deepcopy(window.operator_observations)
        run_training075=window.use_run_training.isChecked()
        difficulty075=window.difficulty.currentIndex();summary075=window.run_summary.text()
        plain_e0_075={}
        try:
            window.run.state['operators']={};window.use_run_training.setChecked(False)
            for case075 in design075:
                section075=case075['section'];requested075=case075['input']
                owner075=requested075['operator'];number075=requested075['skill']
                fields075={k:requested075[k] for k in ('elite','level','potential','trust','module_id','module_level')}
                # These are public synthetic observation records in the same
                #temporary window, not recognition, account files or selectors.
                window.run.state['config']=deepcopy(requested075.get('run_config',{}))
                window.run_summary.setText(window.run.summary());window.sync_run_config()
                train(owner075,fields075,ranks={str(n):requested075['skill_rank'] for n in (1,2,3)})
                reset_owner_options(owner075)
                index075=window.skill.findData(number075);assert index075>=0
                window.skill.setCurrentIndex(index075)
                assert window.elite.text()==f'精英 {fields075["elite"]}'
                assert window.potential.text()==str(fields075['potential'])
                if fields075['module_id']:assert f'阶段 {fields075["module_level"]}' in window.module.text()
                if fields075['elite']==0:assert window.skill.findData(2)==window.skill.findData(3)==-1
                if fields075['elite']==1:assert window.skill.findData(3)==-1
                window.frame_timing.setChecked(requested075['timing_mode']=='frames')
                window.window_seconds.setValue(requested075['window_seconds']);window.timing_scenario.clear()
                for key075 in ('deployment_elapsed_seconds','drone_warmup_hits','ghost_count','ghost_casts'):
                    if key075 in requested075:
                        widget075=option_widgets[(owner075,key075)]
                        widget075.setValue(requested075[key075])
                result075=click_result();args075=window.damage_result['scenario']
                for key075 in ('operator','skill','elite','level','potential','trust','skill_rank',
                        'module_id','module_level','timing_mode','window_seconds'):
                    assert args075[key075]==requested075[key075],(section075,key075,args075[key075],requested075[key075])
                actual075=window.damage_text.toPlainText()
                if section075==71:
                    assert canonical075(args075['run_config'])==canonical075(requested075['run_config'])
                    record075=config075['squads'][args075['run_config']['squad']['id']]
                    assert record075['name'] in window.run_summary.text()
                    assert ('（强化）' if record075['bandLevel']==1 else '（基础）') in window.run_summary.text()
                    grade075=requested075['run_config'].get('difficulty')
                    assert window.difficulty.isEnabled() is (grade075 is None)
                    if grade075:assert window.difficulty.currentData()==grade075['value']
                    require_squad075(result075,args075,actual075,record075)
                elif section075==72:
                    elapsed075=option_widgets[(owner075,'deployment_elapsed_seconds')]
                    assert isinstance(elapsed075,QDoubleSpinBox) and elapsed075.isVisible() and elapsed075.isEnabled()
                    assert elapsed075.minimum()==0 and elapsed075.maximum()==3600 and elapsed075.decimals()==2
                    assert type(elapsed075.value()) is float and type(args075['deployment_elapsed_seconds']) is float
                    assert elapsed075.value()==args075['deployment_elapsed_seconds']==requested075['deployment_elapsed_seconds']
                    require_real_int070(option_widgets[(owner075,'drone_warmup_hits')],args075,
                                        'drone_warmup_hits',requested075['drone_warmup_hits'])
                    baseline_key075=(args075['potential'],args075['timing_mode'],args075['drone_warmup_hits'])
                    if args075['elite']==0 and args075['deployment_elapsed_seconds']==0:
                        plain_e0_075[baseline_key075]=deepcopy(result075)
                    require_headwolf075(result075,args075,actual075,
                        plain_e0_075.get(baseline_key075) if args075['elite']==0 else None)
                elif section075==73:
                    require_mei075(result075,args075,actual075,args075['elite']==2 and args075['level']>=40,args075['module_level'])
                    if args075['window_seconds']==0:assert result075['total_damage']==0
                elif section075==74:
                    for key075 in ('ghost_count','ghost_casts'):
                        require_real_int070(option_widgets[(owner075,key075)],args075,key075,requested075[key075])
                    require_wisdel_routes075(result075,args075,actual075)
                    if args075['window_seconds']==0:assert result075['total_damage']==0
                else:raise AssertionError(('Unsealed section',section075))
                current_section_counts[section075]=current_section_counts.get(section075,0)+1
                checks.append({'scope':'actual_qt_public_config_and_readonly_cultivation_contract' if section075==71 else
                    'actual_qt_owner_controls_and_readonly_cultivation_reference',
                    'section':section075,'operator':owner075,'skill':number075,'mode':args075['timing_mode'],
                    'elite':args075['elite'],'level':args075['level'],'potential':args075['potential'],
                    'module_level':args075['module_level'],'window_seconds':args075['window_seconds'],
                    'input_design':requested075,'state_scope':'temporary public in-memory observation/config only',
                    'actual_account_source_or_clock_verified':False,'passed':True})
        finally:
            window.run.state=state075;window.operator_observations=account075
            window.use_run_training.setChecked(run_training075)
            window.run_summary.setText(summary075);window.sync_run_config()
            if not state075.get('config',{}).get('difficulty'):window.difficulty.setCurrentIndex(difficulty075)
            window.update_operator();relics([]);window.timing_scenario.clear()
        assert current_section_counts=={71:106,72:280,73:72,74:108},current_section_counts

        #75 The battle-preview combos/checkbox produce their real read-only text.
        #This is selected public stage data, not actual movement or game capture.
        from rouge.battle_preview import battle_data,enemy_preview,enemy_text
        preview075=window.battle_preview;stage075=window.target_stage.currentData()
        enemy075=window.target_enemy.currentData();page075=window.centralWidget().currentIndex()
        technical075=preview075.technical.isChecked()
        try:
            window.centralWidget().setCurrentIndex(4);app.processEvents()
            for case075 in preview_cases075(battle_data()['stages']):
                sid075=case075['stage_id'];eid075=case075['enemy_id'];level075=case075['level']
                # BranchChoice reveals the genuine stage/identity combo and emits
                #its normal Qt selection signal; no private _render API is called.
                assert preview075.stage_choices.select_value(sid075)
                app.processEvents()
                assert preview075.stage_combo.currentData()==sid075 and preview075.current_stage==sid075
                assert preview075.stage_combo.isVisible() and preview075.stage_combo.isEnabled()
                assert preview075.enemy_choices.select_value((eid075,level075))
                app.processEvents()
                assert tuple(preview075.enemy_combo.currentData())==(eid075,level075)
                assert preview075.enemy_combo.isVisible() and preview075.enemy_combo.isEnabled()
                preview075.technical.setChecked(case075['technical']);app.processEvents()
                assert isinstance(preview075.technical,QCheckBox) and preview075.technical.isVisible()
                assert preview075.technical.isChecked() is case075['technical']
                entry075=enemy_preview(sid075,eid075,level075,preview075.context)
                actual075=preview075.enemy_detail.toPlainText()
                assert preview075.enemy_detail.isReadOnly() and preview075.enemy_detail.isVisible()
                assert actual075==enemy_text(entry075,technical=case075['technical']).replace(chr(160),' ')
                require_movement075(entry075,actual075,case075['technical'],battle_data()['stages'][sid075])
                current_section_counts[75]=current_section_counts.get(75,0)+1
                checks.append({'scope':'actual_stage_enemy_combo_and_technical_movement_source_reference',
                    **case075,'old_base_times_stage_subtotal':entry075['movement_reference']['base_times_stage_speed'],
                    'effective_movement_known':False,'rune_composition_known':False,'passed':True})
                if sid075=='ro6_e_3_6' and eid075=='enemy_10107_mjcdog_2' and case075['technical']:
                    from PySide6.QtGui import QTextCursor
                    preview075.enemy_detail.moveCursor(QTextCursor.MoveOperation.Start)
                    assert preview075.enemy_detail.find('关卡移速符文参数参考')
                    preview075.enemy_detail.ensureCursorVisible();app.processEvents()
                    assert window.grab().save(str(OUT/'wine-movement-reference-080.png'))
                    receipt['section75_actual_technical_screenshot']='wine-movement-reference-080.png'
        finally:
            preview075.technical.setChecked(technical075)
            assert window.target_stage_choices.select_value(stage075)
            if enemy075 is None:window.target_enemy.setCurrentIndex(0)
            else:assert window.target_enemy_choices.select_value(enemy075)
            window.centralWidget().setCurrentIndex(page075);app.processEvents()
        assert current_section_counts[75]==48
        current_end=len(checks)
        receipt['supplemental_sections_71_75']=[71,72,73,74,75]
        receipt['supplemental_checks_by_section_71_75']=current_section_counts
        receipt['supplemental_checks_71_75']=current_end-current_start
        assert sum(current_section_counts.values())==current_end-current_start
        receipt['section71_input_scope']='No squad selector exists. Synthetic public run config plus real button/read-only summary/difficulty preset; grades and Mechanist cultivation never prove account unlock or actual activation. Entire state/observations/preset are restored.'
        receipt['section72_input_scope']='Owner QDoubleSpinBox elapsed has two decimals; QSpinBox warmup emits int. Cultivation is read-only public observation preview. E0 age does not activate absent Headwolf; original E1/E2 owner-clock reference remains distinct from unknown independent drone arrival/targeting/aura.'
        receipt['section73_input_scope']='Module stage/cultivation are existing QLabel public observation previews, not invented selectors. Exact110% airborne source parameter is unused; actual target, native attachment and composition remain unknown.'
        receipt['section74_input_scope']='Existing ghost count/cast QSpinBoxes retain legal E0/E1 declarations despite both original native body routes requiring E2level1. Qualification does not prove source, presence, cast clock or all module/relic routes.'
        receipt['section75_input_scope']='Actual battle-preview stage/enemy selectors and technical checkbox retain all12 enemy records in each normal/emergency stage. Exact emergency raw rune1.5 remains a source parameter; old base-times-stage subtotal is unchanged, effective speed and native writer/composition remain unknown. No capture, actual route or movement clock is certified.'
        receipt['section75_final_checks_pending']=False
        assert receipt['section75_final_checks_pending'] is False,'Final section75 source/independent review is not yet sealed'

        #76-80 genuine Qt design. API textual/invalid values are separate.
        next_start=len(checks);next_section_counts={};controls080={}
        state080=deepcopy(window.run.state);account080=deepcopy(window.operator_observations)
        run_training080=window.use_run_training.isChecked()
        difficulty080=window.difficulty.currentIndex();summary080=window.run_summary.text()
        target_stage080=window.target_stage.currentData();target_enemy080=deepcopy(window.target_enemy.currentData())
        try:
            window.run.state['operators']={};window.run.state['config']={}
            window.use_run_training.setChecked(False);window.sync_run_config()
            window.damage_technical.setChecked(False);relics([])
            window.target_enemy.setCurrentIndex(0);window.defense.setValue(0);window.resistance.setValue(0)
            window.cooperative.setChecked(False);window.fragile.setChecked(False)
            window.limit_window.setChecked(True);window.deployment_elapsed.setValue(0)
            for case080 in cases080():
                requested080=case080['input'];owner080=requested080['operator'];number080=requested080['skill']
                section080=case080['section']
                fields080={k:requested080[k]for k in ('elite','level','potential','trust','module_id','module_level')}
                train(owner080,fields080,ranks={str(n):requested080['skill_rank']for n in (1,2,3)})
                reset_owner_options(owner080)
                index080=window.skill.findData(number080);assert index080>=0
                window.skill.setCurrentIndex(index080)
                assert window.elite.text()==f'精英 {fields080["elite"]}'
                assert window.potential.text()==str(fields080['potential'])
                if fields080['module_id']:assert f'阶段 {fields080["module_level"]}'in window.module.text()
                if fields080['elite']==0:assert window.skill.findData(2)==window.skill.findData(3)==-1
                if fields080['elite']==1:assert window.skill.findData(3)==-1
                window.frame_timing.setChecked(requested080['timing_mode']=='frames')
                window.window_seconds.setValue(requested080['window_seconds'])
                window.healing_targets.setValue(requested080['healing_targets'])
                relics(requested080['relic_ids'])
                window.defense.setValue(requested080['enemy_defense'])
                window.resistance.setValue(requested080['enemy_resistance'])
                window.timing_scenario.setPlainText(json.dumps(requested080['timing'])if requested080.get('timing')else '')
                if requested080.get('target_enemy'):
                    target080=requested080['target_enemy']
                    assert window.target_stage_choices.select_value(target080['stage_id'])
                    assert window.target_enemy_choices.select_value(target080)
                    app.processEvents()
                    assert window.target_enemy.currentData()==target080
                else:
                    window.target_enemy.setCurrentIndex(0)
                if section080==76:
                    bubble080=option_widgets[(owner080,'bubble_bursts')]
                    repeat080=option_widgets[(owner080,'haruka_repeat')]
                    levitate080=option_widgets[(owner080,'levitate_triggers')]
                    assert isinstance(bubble080,QSpinBox) and bubble080.minimum()==0 and bubble080.maximum()==10000
                    bubble080.setValue(requested080['bubble_bursts'])
                    if number080==2:repeat080.setChecked(requested080['haruka_repeat'])
                    if number080==3:levitate080.setValue(requested080['levitate_triggers'])
                elif section080==77:
                    weight080=option_widgets[(owner080,'enemy_weight')]
                    assert isinstance(weight080,QSpinBox) and weight080.minimum()==0 and weight080.maximum()==100
                    weight080.setValue(requested080['enemy_weight'])
                elif section080==78:
                    palsy080=option_widgets[(owner080,'palsy_triggers')]
                    overflow080=option_widgets[(owner080,'palsy_overflow_hits')]
                    assert isinstance(palsy080,QSpinBox) and palsy080.minimum()==0 and palsy080.maximum()==10000
                    palsy080.setValue(requested080['palsy_triggers'])
                    if number080==3:overflow080.setValue(requested080['palsy_overflow_hits'])
                    if 'enemy_elemental_resistance'in requested080:
                        elemental080=option_widgets[(owner080,'enemy_elemental_resistance')]
                        assert isinstance(elemental080,QDoubleSpinBox) and elemental080.minimum()==0 and elemental080.maximum()==100
                        elemental080.setValue(requested080['enemy_elemental_resistance'])
                elif section080 in (79,80):
                    medical_targets080=option_widgets[(owner080,'amiya_hit_targets')]
                    assert isinstance(window.healing_targets,QSpinBox) and window.healing_targets.minimum()==0
                    assert window.healing_targets.maximum()==(100 if number080==1 else 1)
                    if number080==2:
                        assert isinstance(medical_targets080,QSpinBox)
                        assert medical_targets080.minimum()==1 and medical_targets080.maximum()==100
                        medical_targets080.setValue(requested080['amiya_hit_targets'])
                else:raise AssertionError('Unsealed section')
                result080=click_result();args080=window.damage_result['scenario']
                for key080 in ('operator','skill','elite','level','potential','trust','module_id','module_level',
                               'skill_rank','timing_mode','window_seconds','healing_targets','relic_ids',
                               'enemy_defense','enemy_resistance'):
                    assert args080[key080]==requested080[key080],(case080,key080,args080[key080])
                assert args080.get('timing',{})==requested080.get('timing',{})
                if section080==76:
                    require_real_int070(bubble080,args080,'bubble_bursts',requested080['bubble_bursts'])
                    if number080==2:
                        require_real_bool070(repeat080,args080,'haruka_repeat',requested080['haruka_repeat'])
                    else:
                        assert not repeat080.isVisible() and 'haruka_repeat'not in args080
                    if number080==3:
                        assert levitate080.minimum()==0 and levitate080.maximum()==1000
                        require_real_int070(levitate080,args080,'levitate_triggers',requested080['levitate_triggers'])
                    else:
                        assert not levitate080.isVisible() and 'levitate_triggers'not in args080
                    control_key080=canonical080({k:v for k,v in requested080.items()if k!='bubble_bursts'})
                    if requested080['bubble_bursts']==0:controls080[control_key080]=deepcopy(result080)
                    assert control_key080 in controls080
                    require_haruka080(result080,args080,window.damage_text.toPlainText(),controls080[control_key080])
                elif section080==77:
                    require_real_int070(weight080,args080,'enemy_weight',requested080['enemy_weight'])
                    control_key080=canonical080({k:v for k,v in requested080.items()if k!='enemy_weight'})
                    if requested080.get('target_enemy'):
                        assert args080['target_enemy']==requested080['target_enemy']
                        if args080['enemy_weight']==0:controls080[control_key080]=deepcopy(result080)
                        require_aglna_selected080(result080,args080,window.damage_text.toPlainText(),
                            controls080[control_key080],case080['expected_reference_mass'])
                    else:
                        assert window.target_enemy.currentData() is None and 'target_enemy'not in args080
                        control080=controls080.setdefault(control_key080,{})
                        if args080['enemy_weight']==0:control080['light']=deepcopy(result080)
                        if args080['enemy_weight']==4:control080['heavy']=deepcopy(result080)
                        require_aglna080(result080,args080,window.damage_text.toPlainText(),control080)
                elif section080==78:
                    require_real_int070(palsy080,args080,'palsy_triggers',requested080['palsy_triggers'])
                    if number080==3:
                        assert overflow080.minimum()==0 and overflow080.maximum()==10000
                        require_real_int070(overflow080,args080,'palsy_overflow_hits',requested080['palsy_overflow_hits'])
                    else:
                        assert not overflow080.isVisible() and 'palsy_overflow_hits'not in args080
                    if 'enemy_elemental_resistance'in requested080:
                        assert elemental080.isVisible() and elemental080.isEnabled()
                        assert type(args080['enemy_elemental_resistance']) is float
                        assert args080['enemy_elemental_resistance']==elemental080.value()==requested080['enemy_elemental_resistance']
                    control_key080=canonical080({k:v for k,v in requested080.items()if k!='palsy_triggers'})
                    if args080['palsy_triggers']==0:controls080[control_key080]=deepcopy(result080)
                    require_mantra080(result080,args080,window.damage_text.toPlainText(),controls080[control_key080])
                elif section080 in (79,80):
                    if number080==2:
                        require_real_int070(medical_targets080,args080,'amiya_hit_targets',requested080['amiya_hit_targets'])
                    else:
                        assert not medical_targets080.isVisible() and 'amiya_hit_targets'not in args080
                    if section080==79:require_medical_amiya080(result080,args080,window.damage_text.toPlainText())
                    else:require_medical_trait080(result080,args080,window.damage_text.toPlainText(),case080['expected_trait_ratio'])
                    if (section080==80 and case080['context']=='INC_X_same_trait_ratio_boundary' and
                            args080['elite']==2 and args080['level']==50 and args080['module_level']==3 and
                            number080==1 and args080['timing_mode']=='frames' and args080['healing_targets']==1):
                        from PySide6.QtGui import QTextCursor
                        window.damage_text.moveCursor(QTextCursor.MoveOperation.Start)
                        assert window.damage_text.find('【治疗输出】')
                        window.damage_text.ensureCursorVisible();app.processEvents()
                        assert window.isVisible() and window.module.isVisible()
                        assert '带有灼痕的裙子'in window.module.text() and '阶段 3'in window.module.text()
                        assert window.grab().save(str(OUT/'wine-medical-trait-080.png'))
                        conversion080=next(c for c in result080['components']if c['name']=='咒愈师伤害转治疗')
                        receipt['section80_actual_trait_screenshot']={'filename':'wine-medical-trait-080.png',
                            'captured_during_existing_case':True,'extra_API_or_Qt_case':False,
                            'readonly_elite_text':window.elite.text(),'readonly_module_text':window.module.text(),
                            'ratio':conversion080['damage_healing']['ratio'],
                            'damage_conversion_hits':conversion080['hits'],
                            'damage_conversion_per_hit':conversion080['per_hit'],
                            'damage_conversion_total':conversion080['total'],
                            'visible_report_scrolled_to_healing_section':True,
                            'native_clock_or_recipient_verified':False}
                next_section_counts[section080]=next_section_counts.get(section080,0)+1
                checks.append({'scope':{76:'actual_bubble_spin_and_readonly_talent_qualification_with_zero_control',
                    77:'actual_manual_weight_spin_and_readonly_locked_talent_event_count',
                    78:'actual_palsy_spin_and_readonly_talent_qualification_with_zero_control',
                    79:'actual_medical_form_readonly_talent_qualification_and_opening_count_spin',
                    80:'actual_medical_INC_X_same_trait_ratio_and_damage_dependent_healing'}[section080],
                    'section':section080,'operator':owner080,'skill':number080,'mode':args080['timing_mode'],
                    'context':case080['context'],'elite':args080['elite'],'potential':args080['potential'],
                    'module_level':args080['module_level'],'bubble_bursts':args080.get('bubble_bursts'),
                    'enemy_weight':args080.get('enemy_weight'),
                    'selected_enemy':args080.get('target_enemy'),'reference_mass':case080.get('expected_reference_mass'),
                    'haruka_repeat':args080.get('haruka_repeat'),'levitate_triggers':args080.get('levitate_triggers'),
                    'palsy_triggers':args080.get('palsy_triggers'),'palsy_overflow_hits':args080.get('palsy_overflow_hits'),
                    'enemy_elemental_resistance':args080.get('enemy_elemental_resistance'),
                    'amiya_hit_targets':args080.get('amiya_hit_targets'),
                    'expected_trait_ratio':case080.get('expected_trait_ratio'),
                    'state_scope':'temporary public readonly cultivation observation; no editable module/elite selector',
                    'native_clock_attachment_or_actual_recipient_verified':False,'passed':True})
        finally:
            window.run.state=state080;window.operator_observations=account080
            window.use_run_training.setChecked(run_training080)
            window.run_summary.setText(summary080);window.sync_run_config()
            if not state080.get('config',{}).get('difficulty'):window.difficulty.setCurrentIndex(difficulty080)
            assert window.target_stage_choices.select_value(target_stage080)
            if target_enemy080 is None:window.target_enemy.setCurrentIndex(0)
            else:assert window.target_enemy_choices.select_value(target_enemy080)
            window.update_operator();relics([]);window.timing_scenario.clear()
        next_end=len(checks)
        assert next_section_counts=={76:432,77:424,78:360,79:212,80:180},next_section_counts
        receipt['supplemental_sections_76_80']=[76,77,78,79,80]
        receipt['supplemental_checks_by_section_76_80']=next_section_counts
        receipt['supplemental_checks_76_80']=next_end-next_start
        receipt['section76_input_scope']='Genuine bubble QSpinBox int0/1/10000 retains declarations at every elite. Read-only public cultivation/module previews do not invent selectors. BeforeE2 only declared-count row and source exclusion note differ from same-window/count0 complete result; original ordinary healing/derived damage and other unknowns stay. E2 event clock, native attachment/composition and recipient/adjacency remain unknown. S2 repeat is real bool, S3 levitate count is separate int; inactive keys are omitted.'
        receipt['section77_input_scope']='Real manual enemy-weight QSpinBox0/3/4/100 and read-only E0/E1/E2/potential1/3 retain source threshold and coefficients. E0 S1 locked extra component has zero hits/timestamps/full-skill count without changing ordinary damage; selected E1/E2 conditional per-hit references remain. Separate genuine stage/enemy selections verify exact fixed roster identity massLevel3/4 overrides raw manual0/100 without claiming actual spawn/live weight/extra attack snapshot/native ordering/takeoff clock.'
        receipt['section78_input_scope']='Genuine palsy QSpinBox0/1/10000 preserves declarations beforeE1; only three declared-count metadata values differ from complete same-condition/count0 output with zero effective locked-talent damage. Qualified positive declarations, elemental immunity and separate S3 overflow hits retain unknown actual times/snapshots. Read-only module/elite observations introduce no selectors or native qualification inference.'
        receipt['section79_input_scope']='Readonly medical Amiya form/cultivation, actual S2 opening-count QSpinBox1/5/100, E0S1 zero effective own-regeneration events without an unplaced-source warning. Qualified S1 retains its existing regeneration reference; qualified S2 retains unknown actual strengthening/end/order/complete output even with zero friendly targets or empty hostile lifetime. INC-X49/50/stages remain genuine readonly previews. No HP0, account form unlock, or real-game recipient/clock proof is invented.'
        receipt['section80_input_scope']='The same medical damage-conversion trait uses its original0.5 below INC-X qualification and explicit same-template0.6 override at E2L50/all3stages. Real readonly cultivation and existing friendly-count controls verify damage-dependent treatment after dealt damage, separate S1 range healing, accepted healing factor and S2 opening subtotal; zero recipient/window/lifetime retain mathematical exclusions. Actual S2 end/order/recipient and complete totals remain unverified; no new selector or trait stacking guess.'
        receipt['sections77_80_final_checks_pending']=True
        assert receipt['sections77_80_final_checks_pending'] is False,'Final77-80 source/schema are pending'

        # Final visible screenshot scenario demonstrates the restored explanation.
        train('char_298_susuro',{'elite':2,'level':60,'potential':1,'trust':100,'module_id':None,'module_level':0})
        window.skill.setCurrentIndex(window.skill.findData(1));window.healing_targets.setValue(1)
        low_cost.setChecked(False);relics([]);window.limit_window.setChecked(True)
        window.window_seconds.setValue(10);window.frame_timing.setChecked(False)
        window.timing_scenario.setPlainText(json.dumps({'target_disappears_seconds':0}))
        result=calculate_result()
        assert result['total_damage']==0 and result['total_healing']>0
        assert window.damage_result['scenario']['relic_ids']==[]
        assert window.damage_result['scenario']['timing_mode']=='continuous'
        assert '真实友方获取时钟未核验' in window.damage_text.toPlainText()
        checks.append({'scope':'actual_final_visible_friendly_scope_explanation','operator':'char_298_susuro',
            'mode':'continuous','window_seconds':10,'enemy_lifetime_seconds':0,'relic_ids':[],
            'report_contains_friendly_clock_unknown':True,'passed':True})
        receipt['manual_token_attribute_scope']='Public API inputs have related regression coverage; actual UI has no manual all_units effects control'
        receipt['deferred_probes']=[]
        receipt['resolved_problem']={'problem':'friendly scope report explanation was deferred after three historical attempts',
            'independent_diagnosis_source':str(diagnosis_path),'independent_diagnosis_sha256':hashlib.sha256(diagnosis_bytes).hexdigest(),
            'historical_evidence_preserved':'verification/full-045/wine-ui.json; original three failed attempts remain unchanged',
            'prior_tmp_diagnosis':'/tmp/p2-draft50/independent-diagnosis.json unavailable after machine restart; reconstructed from persistent historical receipt',
            'recovery':'Both actual report modes now assert the explicit friendly acquisition clock remains unknown',
            'current_available_probe_passed':True}
        receipt['complete_ui_validation']=False
        receipt['window_scenario']=window.damage_result['scenario']
        receipt['window_result']=window.damage_result['result']
        window.centralWidget().setCurrentIndex(1);app.processEvents()
        calculate_button=next(b for b in window.findChildren(QPushButton) if b.text()=='计算属性与技能预估')
        calculate_button.click();app.processEvents()
        assert window.damage_result and window.damage_text.toPlainText()
        checks.append({'scope':'actual_calculate_button_click','passed':True})
        window.centralWidget().setCurrentIndex(1);app.processEvents()
        from PySide6.QtGui import QTextCursor
        window.damage_text.moveCursor(QTextCursor.MoveOperation.Start)
        assert window.damage_text.find('真实友方获取时钟未核验')
        window.damage_text.ensureCursorVisible();app.processEvents()
        checks.append({'scope':'actual_friendly_scope_text_scrolled_visible_for_screenshot','passed':True})
        screenshot=OUT/'wine-window-080.png'
        assert window.grab().save(str(screenshot))
        receipt['window_screenshot']='wine-window-080.png'
        assert not isolated.joinpath('chat').exists()
        assert not window.auto.isChecked() and window.capture.target is None
        assert not window.desktop.process
        checks.append({'scope':'no_external_operations','game_captures':0,'chat_requests':0,'temporary_state':True})
        receipt['preserved_old_checks']=len(checks)-(supplemental_end-supplemental_start)-(new_end-new_start)-(latest_end-latest_start)-(current_end-current_start)-(next_end-next_start)
        assert receipt['preserved_old_checks']==152,receipt['preserved_old_checks']
        receipt['preserved_full_060_checks']=len(checks)-(new_end-new_start)-(latest_end-latest_start)-(current_end-current_start)-(next_end-next_start)
        assert receipt['preserved_full_060_checks']==231,receipt['preserved_full_060_checks']
        receipt['preserved_full_065_checks']=len(checks)-(latest_end-latest_start)-(current_end-current_start)-(next_end-next_start)
        assert receipt['preserved_full_065_checks']==459,receipt['preserved_full_065_checks']
        receipt['preserved_full_070_checks']=len(checks)-(current_end-current_start)-(next_end-next_start)
        assert receipt['preserved_full_070_checks']==841,receipt['preserved_full_070_checks']
        receipt['preserved_full_075_checks']=len(checks)-(next_end-next_start)
        assert receipt['preserved_full_075_checks']==1455,receipt['preserved_full_075_checks']
        receipt['total_actual_checks']=len(checks)
        window.close();app.processEvents();window=None
    receipt['passed']=True
    receipt['complete_ui_validation']=True
    receipt['complete_ui_validation_scope']='Only this available actual Wine Qt suite; no native Windows, game capture, private replay or desktop integration certification'
except BaseException as error:
    receipt['complete_ui_validation']=False
    receipt['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    if window is not None:
        try:
            receipt['failure_actual_window']={'operator':window.operator.currentData(),
                'skill':window.skill.currentData(),'visible_report_text':window.damage_text.toPlainText(),
                'technical_checkbox':window.damage_technical.isChecked(),
                'last_calculation':window.damage_result,'timing_text':window.timing_scenario.toPlainText()}
            failure_screenshot=OUT/'wine-ui-failure-080.png'
            if window.grab().save(str(failure_screenshot)):
                receipt['failure_screenshot']=failure_screenshot.name
        except Exception as context_error:
            receipt['failure_context_capture_error']={'type':type(context_error).__name__,'message':str(context_error)}
finally:
    if window is not None:
        window.close()
        if app is not None:app.processEvents()
    receipt['elapsed_seconds']=round(time.perf_counter()-started,3)
    after=source_hashes();drift=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]
    receipt['source_sha256']=before;receipt['source_sha256_after']=after;receipt['source_drift']=drift
    if drift:receipt['passed']=False;receipt['complete_ui_validation']=False
    (OUT/'wine-ui-080.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
    sys.exit(0 if receipt['passed'] else 1)
