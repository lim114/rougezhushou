"""Audit every collectible against pinned raw buffs before runtime evaluation."""
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'.cache/game-data/roguelike_topic_table.json'
data=json.loads(SOURCE.read_text(encoding='utf-8'))['details']['rogue_6']
receipt=json.loads((ROOT/'.cache/game-data/receipt.json').read_text(encoding='utf-8'))
URL=receipt['files']['roguelike_topic_table']['url']
HP_TEMPLATE_URL='https://raw.githubusercontent.com/fexli/ArknightsResource/d0b5af0b004b044d322397ce5ae79632b6d9fcdd/gamedata/battle/buff_template_data.json'
HP_TEMPLATE_SHA256='b119917318c464f92d28fc5eb40b2069e3644674d26cace165f17bf9044e00ff'
NATIVE_REFERENCE='rouge/data/native-relic-reference.json'
native=json.loads((ROOT/NATIVE_REFERENCE).read_text(encoding='utf-8'))
NATIVE_PROOF=native['research_summary_sha256']
TIMER_PROOF=native['timer_book_native_proof_sha256']
WAVE_STACK_PENDING='波纹之手与断杖-同调的3秒攻击叠层刷新、归属及逐命中取值待核验'
BINDING_RELIC_IDS={'rogue_6_relic_assign_'+str(n) for n in (5,7,9,10,12,13,15)}
NONCOMBAT={'immediate_reward','level_char_limit_add','level_init_cost_add','up_reward','shop_discount_item',
    'battle_extra_recruit_ticket','player_level_rewards','battle_fail_protect','battle_extra_relic',
    'misc_shuffle_deck_cost','immediate_reward_on_vehicle_broken','vehicle_move_no_ap_cost','scrap_fill_up',
    'layer_meet_node_types','drop_extra_pool','level_add_enemy_data','battle_extra_reward','layer_node_in',
    'relic_layer_reward','unlock_node','immediate_reward_on_collection_complete','push_message',
    'zone_into_reward','map_gen_delta','recruit_extra_prob','zone_into_node_attach_buff'}
def board(buff):return {b['key']:b['valueStr'] if b.get('valueStr') is not None else b['value'] for b in buff['blackboard']}
def rule(kind,value,bb,**extra):
    return {'kind':kind,'value':value,'profession':str(bb.get('selector.profession','')).lower(),
        'position':str(bb.get('selector.buildable','')).lower(),
        'subprofession':str(bb.get('selector.sub_profession','')).lower(),**extra}
def extract(buff,rid):
    key=buff['key'];bb=board(buff);effects=[];pending=[]
    attr={'atk':'attack_pct','max_hp':'hp_pct','def':'defense_pct',
        **({'cost':'deployment_cost_pct'} if rid=='rogue_6_relic_fight_11' else {})} if key=='char_attribute_mul' else {
        'attack_speed':'attack_speed','magic_resistance':'resistance_flat','hp_recovery_per_sec':'regeneration',
        'cost':'deployment_cost_add','block_cnt':'block_add','def_penetrate':'defense_penetration',
        'hp_recovery_per_sec_by_max_hp_ratio':'regeneration_hp_ratio'} if key=='char_attribute_add' else {}
    if attr:
        for a,v in bb.items():
            if a.startswith('selector.'):continue
            if a in attr:effects.append(rule(attr[a],v,bb))
            else:pending.append(key+':'+a)
    elif key=='char_attribute_final_scaler' and 'respawn_time' in bb:
        effects.append(rule('redeploy_delta',bb['respawn_time'],bb,group=key,stacking='independent_rune_scalers'))
    elif key=='char_skill_cost_mul':effects.append(rule('sp_cost_factor',bb['scale'],bb,group=key,stacking='unverified'))
    elif key in ('global_buff_stack','global_buff_stack_base_one','global_buff_normal'):
        token=bb.get('key')
        kind={'enemy_damage_scale[phy]':'physical','enemy_damage_scale[mag]':'magic','enemy_damage_scale[pure]':'true'}.get(token)
        if kind:effects.append(rule('damage_taken',bb['damage_scale']-1,{},damage_type=kind,group=token))
        elif token in ('modify_sp_recover[normal]','modify_sp_recover[medic]'):
            # The global prefab, not the relic blackboard, supplies this mask.
            # Fixed native prefab: advanced professionMask=8 (MEDIC); see 0.66.
            selector={**bb,'selector.profession':'MEDIC'} if token=='modify_sp_recover[medic]' else bb
            effects.append(rule('sp_recovery',bb['sp_recovery_per_sec'],selector,group=token))
        elif token=='modify_sp[born]':effects.append(rule('initial_sp',bb['sp'],bb,group=token))
        elif token in ('modify_sp[take_damage]','modify_sp[take_ep_damage]'):
            effects.append(rule('received_sp',bb['sp'],bb,
                event_type='damage' if token=='modify_sp[take_damage]' else 'elemental_loss',group=token))
        elif token=='rogue_6_char_kill_target[sp]' and rid=='rogue_6_relic_fight_5':
            effects.append(rule('event_sp',bb['sp'],bb,event_type='kill',group=token))
        elif token=='rogue_6_caster_book' and rid=='rogue_6_relic_hand_5':
            effects.append(rule('event_sp',bb['sp'],bb,event_type='dealt_damage',group=token))
            pending.append(WAVE_STACK_PENDING)
        elif token=='modify_sp[attack_or_damage]':
            effects.append(rule('periodic_sp',bb['sp'],bb,interval=bb['interval'],group=token,
                stacking='independent_instances',clock='deployment',wait_first=True,
                native_reference=NATIVE_REFERENCE,native_proof=NATIVE_PROOF,native_timer_proof=TIMER_PROOF))
        elif token=='rogue_2_attr_up[limited]' and rid in ('rogue_6_relic_legacy_105','rogue_6_relic_legacy_106'):
            reference=next(r for r in native['therapy']['relics'] if r['id']==rid)
            assert bb==reference['blackboard'] and bb['duration']==10
            effects.append(rule('deployment_attack_speed',bb['attack_speed'],bb,duration=bb['duration'],
                stacking='independent_instances',clock='deployment',native_reference=NATIVE_REFERENCE,
                native_proof=NATIVE_PROOF))
        elif token=='rogue_6_sp_skill_end':effects.append(rule('end_sp',bb['sp'],bb,group=token,stacking='unverified'))
        elif token=='rogue_6_caster_book_2':effects.append(rule('caster_end_sp',bb['sp'],bb,condition='deployed_casters',group=token))
        elif token=='rogue_6_tank_book_2' and rid=='rogue_6_relic_book_3':pass  # Synergy marker; fee comes from the separate card buff.
        elif token=='modify_sp[warrior]':effects.append(rule('attack_sp',bb['sp'],{'selector.profession':'warrior'},group=token))
        elif token=='heal_scale':effects.append(rule('healing_factor',bb['heal_scale'],{},group=token,stacking='unverified'))
        elif token in ('hp_recovery_per_sec[mul]','hp_recovery_per_sec_by_max_hp_ratio[mul]'):
            effects.append(rule('regeneration_factor',1+bb[token.split('[')[0]],{},group='received_regeneration',stacking='unverified'))
        elif token=='enemy_def_down':effects.append(rule('enemy_def_delta',bb['def'],{},group=token,stacking='unverified'))
        elif token=='enemy_lighter' and rid=='rogue_6_relic_legacy_56':
            effects.append(rule('enemy_weight_delta',bb['mass_level'],{},group=token,stacking='unverified'))
        elif token=='rogue_6_enemy_hp_savage' and rid=='rogue_6_relic_cargo_11':
            stages=next(board(b)['stage_ids'] for b in data['relics'][rid]['buffs'] if b['key']=='layer_pass_stage')
            effects.append(rule('enemy_hp_factor',bb['max_hp'],{},eligible_stage_ids=stages.split(','),
                group=token,stacking='independent_instances',hp_composition='final_scaler_verified',
                resident_hp=True,native_reference=NATIVE_REFERENCE,native_proof=NATIVE_PROOF))
        elif token=='rogue_6_char_loss_hp' and rid=='rogue_6_relic_fight_11':
            effects.append(rule('deployment_hp_loss',bb['hp_ratio'],bb,condition='deployment_hp_ratio',
                condition_type='ratio',loss_pending_condition='deployment_loss_unused'))
            pending.append('部署损血为一次事件独立参考；真实触发帧、当前生命和复合生命机制未自动确认')
        elif token=='enemy_atk_down' and rid in ('rogue_6_relic_cargo_12','rogue_6_start_4'):
            target={'target_enemy_id':bb['selector.enemy']} if bb.get('selector.enemy') else {}
            effects.append(rule('enemy_atk_factor',bb['atk'],{},**target,group=token,
                stacking='independent_instances',native_reference=NATIVE_REFERENCE,native_proof=NATIVE_PROOF))
        elif token=='rogue_6_from_other_layer' and rid=='rogue_6_relic_cargo_12':
            counter=next(board(b) for b in data['relics']['rogue_6_relic_fight_30']['buffs'] if b['key']=='layer_zone_end_battle')
            effects.append(rule('resistance_flat',bb['magic_resistance_layer'],{},condition='probe_stacks',
                maximum=counter['max'],scale_by_condition=True))
        elif token=='enemy_max_hp_down':effects.append(rule('enemy_hp_factor',bb['max_hp'] if bb['max_hp']>0 else 1+bb['max_hp'],{},
            group=token,stacking='independent_instances',enemy_level=bb.get('selector.enemy_level_type'),
            hp_composition='final_scaler_verified',native_reference=NATIVE_REFERENCE,native_proof=NATIVE_PROOF))
        elif token=='rogue_6_enemy_prob_max_hp' and rid=='rogue_6_relic_fight_25':
            effects.append(rule('enemy_spawn_hp_branch',1+bb['max_hp'],{},
                probability=bb['prob'],group=token,stacking='unverified'))
        elif token=='enemy_take_element_damage_up[fix]':effects.append(rule('damage_taken',bb['damage_scale']-1,{},damage_type='elemental',group=token,stacking='unverified'))
        elif token=='enemy_damage_scale[ep]':effects.append(rule('buildup_factor',bb['ep_damage_scale'],{},group=token))
        elif token=='rogue_6_enemy_ep_break_fix[sanity]' and rid=='rogue_6_relic_fight_22':
            effects.append(rule('neural_burst_scale',bb['damage_scale'],{},group=token,stacking='unverified',
                periodic_raw_damage=bb['damage'],periodic_interval=bb['interval']))
            pending.append('神经追加伤害的实际首跳和结束顺序、逐跳麻痹状态与目标减伤尚未确认')
        elif rid=='rogue_6_relic_fight_22' and token in (
                'rogue_6_enemy_ep_break_fix[dark]',
                'rogue_6_enemy_ep_break_fix[fire]',
                'rogue_6_enemy_ep_break_fix[water]'):
            pending.append({
                'rogue_6_enemy_ep_break_fix[dark]':'凋亡额外减攻的实际生效和结束时刻，以及与其他减攻效果的组合尚未确认',
                'rogue_6_enemy_ep_break_fix[fire]':'灼燃额外减法抗的实际生效和结束时刻，以及与其他法抗变化的组合尚未确认',
                'rogue_6_enemy_ep_break_fix[water]':'侵蚀追加伤害的实际创建和触发时刻、目标减伤及当前热更新适用性尚未确认',
            }[token])
        elif token=='element_resistance':effects.append(rule('incoming_element_resistance',bb['ep_damage_resistance'],{},group=token,stacking='unverified'))
        elif token=='damage_block[stack]' and rid=='rogue_6_relic_legacy_53':
            effects.append(rule('shield_layers',1,bb))
        elif token=='rogue_3_bornShield[via_MaxHp]':
            effects.append(rule('barrier_on_deploy_ratio',bb['born_hp_ratio'],bb))
        elif token=='rogue_6_char_shield_locate':
            effects.append(rule('barrier_on_deploy_ratio',bb['scale'],bb))
        elif token in ('evade[physical]','evade[magical]','evade[non_pure]'):
            types={'evade[physical]':['physical'],'evade[magical]':['magic'],'evade[non_pure]':['physical','magic']}[token]
            for dtype in types:effects.append(rule('evasion_chance',bb['prob'],bb,damage_type=dtype))
        elif token=='rogue_6_char_skill_add_cost':effects.append(rule('skill_start_dp',bb['cost'],bb))
        elif token=='rogue_6_relic_inventory':
            counter=next(board(b) for b in data['relics'][rid]['buffs'] if b['key']=='layer_scrap_owned')
            for a in ('atk','max_hp'):effects.append(rule({'atk':'attack_pct','max_hp':'hp_pct'}[a],bb[a],bb,
                condition='parts_count',maximum=counter['max'],scale_by_condition=True))
        elif token=='rogue_6_relic_inventory_cost':
            effects.append(rule('deployment_cost_add',bb['value'],bb,condition='empty_slots',
                predicate='at_least',threshold=bb['cnt'],scale_by_condition=True))
        elif token=='rogue_6_relic_employ':
            for a in ('atk','max_hp','def'):effects.append(rule({'atk':'attack_pct','max_hp':'hp_pct','def':'defense_pct'}[a],bb[a],bb,condition='emergency_hire'))
        elif token=='rogue_2_hp_ratio_to_attr_add[attack_speed]':
            effects.append(rule('attack_speed',bb['min_attack_speed'],bb,condition='current_hp_ratio',hp_curve_min=bb['min_hp_ratio']))
        elif token=='ammo_skill_start_attri_up':
            effects.append(rule('temporary_ammo_speed',bb['attack_speed'],bb,duration=bb['duration']))
        elif token=='add_remaining_ammo_by_max_ratio':
            effects.append(rule('ammo_refill',bb['ammo_add_ratio'],bb,threshold_ratio=bb['ammo_max_ratio'],
                group=token,stacking='shared_counter_budget',native_parameter_proof='ammo-refill-reference.json'))
            pending.append('未支持的特殊弹药计数器与不安全轮询窗口待接入')
        elif token=='atk_up_on_skill_start':
            effects.append(rule('temporary_attack',bb['atk'],bb,duration=bb['duration'],group=token,stacking='unverified'))
        elif token=='rogue_3_rangedATKUp':effects.append(rule('attack_pct',bb['atk'],bb,condition='adjacent_allies',scale_by_condition=True))
        elif token=='rogue_3_increaseMaxHPWhenHavingShield':
            effects.append(rule('hp_pct',bb['max_hp'],bb,condition='battle_start_shields',predicate='positive',scale_by_condition=True))
        elif token=='atk_up_on_skill_start[stacked]':effects.append(rule('attack_pct',bb['atk'],bb,condition='skill_cast_stacks',scale_by_condition=True,maximum=bb['max_stack_cnt']))
        elif token=='attr_up_on_trigger[def&mag_resist]':
            for attr,kind in (('def','defense_flat'),('magic_resistance','resistance_flat')):
                effects.append(rule(kind,bb[attr],bb,condition='deployed_seconds',condition_type='seconds',
                    predicate='at_least',threshold=bb['interval'],scale_by_condition=True))
        elif token=='rogue_4_finalDefense[end_tile]':
            for attr,kind in (('max_hp','hp_pct'),('block_cnt','block_add')):
                effects.append(rule(kind,bb[attr],bb,condition='near_protection_point',condition_type='flag',scale_by_condition=True))
        elif token=='rogue_6_char_first_damage':
            effects.append(rule('first_damage_scale',bb['damage_scale']-1,bb,
                condition='enemy_first_damage_unused',condition_type='flag',scale_by_condition=True,factor_offset=1))
        elif token=='rogue_3_relic_book_7':effects.append(rule('damage_taken',bb['damage_scale_factor'],{},damage_type='magic',condition='deployed_casters',scale_by_condition=True,maximum=8))
        else:pending.append(key+':'+str(token))
    elif key=='layer_char_attribute_add' and bb.get('stack_by_res')=='rogue_6_gold':
        effects.append(rule('attack_speed',bb['attack_speed'],bb,condition='gold',divisor=bb['stack_by_res_cnt'],scale_by_condition=True))
    elif key=='layer_char_attribute_add' and rid=='rogue_6_relic_cargo_11':
        counter=next(board(b) for b in data['relics'][rid]['buffs'] if b['key']=='layer_pass_stage')
        effects.append(rule('attack_speed',bb['attack_speed'],bb,condition='fire_rod_stacks',
            scale_by_condition=True,maximum=counter['max']))
    elif key=='layer_pass_stage' and rid=='rogue_6_relic_cargo_11':pass
    elif key=='layer_char_attribute_mul' and rid=='rogue_6_relic_legacy_103':
        counter=next(board(b) for b in data['relics'][rid]['buffs'] if b['key']=='layer_after_battle_data')
        for a,kind in (('atk','attack_pct'),('def','defense_pct')):
            effects.append(rule(kind,bb[a],bb,condition='altar_stacks',scale_by_condition=True,maximum=counter['max']))
    elif key=='layer_after_battle_data' and rid=='rogue_6_relic_legacy_103':pass
    elif key=='global_buff_layer' and bb.get('key')=='rogue_6_enemy_layer_multi':
        counter=next(board(b) for b in data['relics'][rid]['buffs'] if b['key']=='layer_zone_end_battle')
        for a,kind in (('atk','enemy_atk_factor'),('max_hp','enemy_hp_factor')):
            extra=({'hp_composition':'final_scaler_verified','hp_template_key':'rogue_6_enemy_layer_multi',
                'hp_template_source':HP_TEMPLATE_URL,'hp_template_sha256':HP_TEMPLATE_SHA256} if kind=='enemy_hp_factor' else {})
            effects.append(rule(kind,bb[a],{},condition='probe_stacks',scale_by_condition=True,
                factor_offset=1,maximum=counter['max'],target_enemy_id=bb['selector.enemy'],**extra))
    elif key=='layer_zone_end_battle' and rid=='rogue_6_relic_fight_30':pass
    elif key=='global_buff_layer' and bb.get('key')=='rogue_6_start_3':
        effects.append(rule('enemy_hp_factor',bb['max_hp']-1,{},condition='entered_zone_count',
            predicate='less_than',threshold=bb['max_cnt'],scale_by_condition=True,factor_offset=1,
            group='rogue_6_start_3',stacking='unverified',hp_composition='final_scaler_verified',
            hp_template_key='rogue_6_start_3',hp_template_source=HP_TEMPLATE_URL,hp_template_sha256=HP_TEMPLATE_SHA256))
    elif key=='layer_zone_in_up_elite_down' and rid=='rogue_6_start_3':pass
    elif key=='global_buff_layer' and bb.get('key')=='rogue6_relic_fight_63':
        effects.append(rule('attack_pct',bb['atk'],bb,condition='grudge_stacks',scale_by_condition=True,
            maximum=bb['max_stack_cnt'],group='rogue6_relic_fight_63',stacking='verified_multiplier',
            secondary_source='https://m.prts.wiki/w/沉沦者的黑流树海/拟造物质编目#仇名录',
            stacking_evidence='Pinned rogue6_relic_fight_63 child ATK MULTIPLIER; base +2% is a separate relic rune.',
            attribute_layer='battle',formula_item='MULTIPLIER',
            attribute_template_key='rogue6_relic_fight_63',attribute_template_source=HP_TEMPLATE_URL,
            attribute_template_sha256=HP_TEMPLATE_SHA256))
    elif key=='layer_after_battle_data' and rid=='rogue_6_relic_artifact_7':pass
    elif key=='layer_char_random_target_attribute' and rid=='rogue_6_relic_legacy_136':
        counter=next(board(b) for b in data['relics'][rid]['buffs'] if b['key']=='layer_after_perfect_battle')
        for a,kind in (('atk','attack_pct'),('max_hp','hp_pct'),('def','defense_pct')):
            effects.append(rule(kind,bb['multiplier@'+a],bb,condition='mercenary_stacks',
                recipient_condition='mercenary_recipient',scale_by_condition=True,maximum=counter['max']))
    elif key=='layer_after_perfect_battle' and rid=='rogue_6_relic_legacy_136':pass
    elif key=='char_random_target_attribute' and rid=='rogue_6_relic_legacy_52':
        for a,kind in (('atk','attack_pct'),('max_hp','hp_pct')):
            effects.append(rule(kind,bb['multiplier@'+a],bb,condition='chitin_recipient',condition_type='flag',scale_by_condition=True))
    elif key=='char_ability_new' and bb.get('key')=='rogue_6_char_invisible_aura':
        effects.append(rule('attack_pct',bb['atk'],bb,condition='active_other_aura_sources',scale_by_condition=True))
    elif key=='char_ability_new' and bb.get('key')=='passive_hp_ratio_to_attr_add[atk]':
        effects.append(rule('attack_pct',bb['min_atk'],bb,condition='current_hp_ratio',hp_curve_min=bb['min_hp_ratio']))
    elif key=='char_ability_new' and bb.get('key')=='AtkUp[BlockJustOne]':
        effects.append(rule('attack_pct',bb['atk'],bb,condition='blocked_enemies',predicate='equals_one',scale_by_condition=True,unit_condition=True))
    elif key=='char_ability_new' and bb.get('key')=='rogue_6_hp_ratio_to_attr_add[sp_recover]':
        effects.append(rule('sp_recovery',bb['min_sp_recovery_per_sec'],bb,condition='current_hp_ratio',hp_curve_min=bb['min_hp_ratio']))
    elif key=='char_ability_new' and bb.get('key')=='rogue_6_sp_recover' and rid=='rogue_6_relic_assign_15':
        effects.append(rule('sp_recovery',bb['sp_recovery_per_sec'],bb,skill_sp_type='INCREASE_WITH_TIME'))
    elif key=='char_ability_new' and bb.get('key')=='rogue_6_tank_damage_sp' and rid=='rogue_6_relic_assign_4':
        effects.append(rule('received_sp',bb['sp'],bb,event_type='attack'))
    elif key=='char_ability_new' and bb.get('key')=='rogue_6_skill_forbidden':
        effects.extend([rule('skill_forbidden',1,bb),rule('attack_pct',bb['atk'],bb),rule('attack_speed',bb['attack_speed'],bb)])
    elif key=='char_ability_new' and bb.get('key')=='AutoSkillTrigger':
        effects.append(rule('automatic_skill',1,bb))
    elif key=='enemy_attribute_add' and 'one_minus_status_resistance' in bb:
        effects.append(rule('status_duration_delta',bb['one_minus_status_resistance'],{},group=key,stacking='unverified'))
    elif key=='layer_scrap_owned' and rid=='rogue_6_relic_cargo_2':pass  # Owned-count cap is attached to both attribute effects.
    elif key=='deck_card_buff' and rid=='rogue_6_relic_book_3' and bb.get('selector.profession')=='TANK':
        effects.append(rule('first_deployment_cost_factor',bb['cost_scale'],bb,first_deployment_only=True))
    elif key=='deck_card_buff' and bb.get('selector.profession')=='token':
        effects.append(rule('token_deploy_slot_free',bb.get('dont_occupy_deploy_cnt',0),bb))
    elif key=='char_ability_new' and bb.get('key')=='rogue_2_occupy_zero[token]':pass
    elif key=='immediate_reward' and 'from_relic' in str(bb.get('id')):pending.append('绑定强化领取者:'+str(bb['id']))
    elif key in NONCOMBAT:pass
    else:pending.append(key+':'+str(bb.get('key','')))
    # The native CAttribute* preprocessors write the rune accumulator; these
    # sources must not be combined with skill/talent battle multipliers.
    rune_formulas={'char_attribute_mul':'MULTIPLIER','char_attribute_add':'ADDITION',
        'char_attribute_final_scaler':'FINAL_SCALER','layer_char_attribute_mul':'MULTIPLIER',
        'layer_char_attribute_add':'ADDITION',
        # Confirmed by registration + CRandomTargetAttribute.ApplyAttributeInternal;
        # DynamicAbility construction alone does not establish this layer.
        'char_random_target_attribute':'MULTIPLIER',
        'layer_char_random_target_attribute':'MULTIPLIER'}
    for effect in effects:
        effect['source_buff_key']=key
        if key in rune_formulas:
            effect.update(attribute_layer='relic_rune',formula_item=rune_formulas[key])
            if effect.get('scale_by_condition'):
                effect['native_count_scale']='float32_before_fp'
    return effects,pending

def main():
    relics={};char_buffs={}
    for rid,item in data['items'].items():
        if item.get('type')!='RELIC':continue
        buffs=data['relics'].get(rid,{}).get('buffs',[])
        effects=[];pending=[]
        for index,b in enumerate(buffs):
            e,p=extract(b,rid)
            for effect in e:effect['source_buff_index']=index
            effects.extend(e);pending.extend(p)
        bound=[v for v in data['charBuffData'].values() if v.get('iconId')==rid]
        if bound:pending.append('必须确认强化领取者及对应charBuff')
        status='partial' if effects and pending else 'pending' if pending else 'conditional' if any(e.get('condition') or e.get('event_type') for e in effects) else 'numeric' if effects else 'non_output'
        relics[rid]={'name':item['name'],'usage':item.get('usage'),'source':URL,'verification':'game_data_verified_runtime_pending',
            'status':status,'effects':effects,'pending':pending,'raw_buffs':buffs,
            'bound_char_buffs':bound,'relic_params':data['relicParams'].get(rid)}
        if rid=='rogue_6_relic_hand_5':
            relics[rid]['pending_scopes']=[{'message':WAVE_STACK_PENDING,
                'requires_relic_ids':['rogue_6_relic_book_5'],
                'subprofession':effects[0]['subprofession']}]
        if rid=='rogue_6_relic_hand_4':
            assert len(buffs)==1 and buffs[0]['key']=='global_buff_normal'
            selector=board(buffs[0])['selector.sub_profession']
            assert selector=='aoesniper|reaperrange|skybreaker'
            relics[rid]['pending_scopes']=[{'message':'global_buff_normal:rogue_6_sniper_book',
                'subprofession':selector}]
        for buff in bound:
            if buff['buffType']!='FROM_RELIC':continue
            effects=[];pending=[]
            for index,b in enumerate(buff['buffs']):
                e,p=extract(b,rid)
                for effect in e:effect['source_buff_index']=index
                effects.extend(e);pending.extend(p)
            professions=[p['valueProfessionMask'].lower() for p in (data['relicParams'].get(rid) or {}).get('checkCharBoxParams',[])
                         if p.get('valueProfessionMask') not in (None,'NONE')]
            char_buffs[buff['id']]={'name':buff['innerName'],'source':URL,'relic_id':rid,
                'required_profession':'|'.join(professions),'effects':effects,'pending':pending,'raw':buff}
    # Stable charBuff formulas are supported; their actual recipients must
    # still be observed. The parent never duplicates the charBuff's effects.
    for rid in BINDING_RELIC_IDS:
        item=relics[rid];bound=item['bound_char_buffs']
        assert len(bound)==1 and bound[0]['buffType']=='FROM_RELIC'
        bid=bound[0]['id'];buff=char_buffs[bid]
        assert buff['effects'] and not buff['pending'] and not item['effects']
        assert all(p=='必须确认强化领取者及对应charBuff' or p.startswith(
            ('绑定强化领取者:','next_recruit_upgrade_char_buff:','rand_gain_char_buff:')) for p in item['pending'])
        item['recipient_binding']={'char_buff_ids':[bid],'scope':'current_operator_only',
            'required_observation':'confirmed_char_buff_or_complete_current_operator_list',
            'effect_path':'char_buff_only','source':URL}
        item['pending']=[];item['status']='conditional'
    output={'schema_version':3,'commit':receipt['commit'],'source_url':URL,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'counts':dict(Counter(r['status'] for r in relics.values())),'relics':relics,'char_buffs':char_buffs}
    (ROOT/'rouge/data/relic-mechanics.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(output['counts']))
if __name__=='__main__':main()
