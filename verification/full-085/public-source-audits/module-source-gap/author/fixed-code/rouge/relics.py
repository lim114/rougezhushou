"""Evidence-backed collectible resolution; missing conditions are never zero."""
from functools import lru_cache
import json
import math
from .attribute_limits import effective_attack_speed
from pathlib import Path

BASE_KINDS={'attack_pct','hp_pct','defense_pct','resistance_flat','attack_speed','sp_recovery','damage_taken'}
SUPPORTED=BASE_KINDS|{'redeploy_delta','initial_sp','end_sp','caster_end_sp','sp_cost_factor','healing_factor',
    'enemy_def_delta','enemy_hp_factor','enemy_spawn_hp_branch','enemy_weight_delta','attack_sp','received_sp','event_sp','regeneration','regeneration_factor',
    'deployment_cost_add','deployment_cost_pct','first_deployment_cost_factor','deployment_hp_loss','block_add','skill_start_dp','incoming_element_resistance',
    'status_duration_delta','token_deploy_slot_free','buildup_factor','temporary_ammo_speed','temporary_attack','deployment_attack_speed','defense_penetration',
    'skill_forbidden','automatic_skill','periodic_sp','regeneration_hp_ratio','enemy_atk_factor','defense_flat','final_attack_factor','first_damage_scale','ammo_refill','barrier_on_deploy_ratio','evasion_chance','shield_layers','neural_burst_scale'}
@lru_cache(maxsize=1)
def mechanics():return json.loads((Path(__file__).with_name('data')/'relic-mechanics.json').read_text(encoding='utf-8'))

def matches(effect,profile,token=False):
    profession='token' if token else profile['profession']
    return (not effect.get('profession') or profession in effect['profession'].split('|')) and (
        not effect.get('position') or effect['position']==profile.get('position')) and (
        not effect.get('subprofession') or profile.get('subprofession_id') in effect['subprofession'].split('|'))

def context_value(effect,scenario):
    condition=effect.get('condition')
    if not condition:return 1
    context=scenario.get('relic_context',{})
    if not isinstance(context,dict):raise ValueError('藏品条件需要JSON对象。')
    if condition=='emergency_hire':
        kind=scenario.get('recruitment_kind')
        if type(kind) is not str or kind not in ('non_emergency','emergency_hire'):return None
        return int(kind=='emergency_hire')
    value=context.get(condition,scenario.get(condition) if condition=='current_hp_ratio' else None)
    if value is None:return None
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
        raise ValueError('藏品条件 '+condition+'需要有限非负数。')
    if effect.get('condition_type')=='flag':
        if value not in (0,1):raise ValueError('藏品条件 '+condition+'需要0（未生效）或1（生效）。')
        return value
    if effect.get('condition_type')=='ratio':
        if value>1:raise ValueError('藏品条件 '+condition+'需要0–1的生命比例。')
        return value
    if 'hp_curve_min' in effect:
        if value>1:raise ValueError('当前生命比例需要0–1。')
        return min(1,(1-value)/(1-effect['hp_curve_min']))
    if effect.get('condition_type')=='seconds':
        if value>3600:raise ValueError('藏品时间 '+condition+'需要0–3600秒。')
    elif not float(value).is_integer() or value>10000:raise ValueError('藏品计数 '+condition+'需要0–10000的整数。')
    if effect.get('predicate')=='positive':return int(value>0)
    if effect.get('predicate')=='equals_one':return int(value==1)
    if effect.get('predicate')=='at_least':return int(value>=effect['threshold'])
    if effect.get('predicate')=='less_than':return int(value<effect['threshold'])
    if effect.get('divisor'):value=math.floor(value/effect['divisor'])
    return min(value,effect['maximum']) if 'maximum' in effect else value

def prepare(scenario,profile):
    scenario=dict(scenario)
    selected=list(dict.fromkeys(scenario.get('relic_ids',[])))
    rules=[];records=[];warnings=[];effects=[];token_effects=[];inapplicable=[];timing_unresolved=False;ammo_unresolved=False;ammo_sources=set()
    inputs=[(rid,mechanics()['relics'].get(rid),False) for rid in selected]
    bound=scenario.get('char_buff_ids',[])
    if not isinstance(bound,list) or not all(isinstance(b,str) for b in bound):
        raise ValueError('干员定向强化需要已确认的ID列表。')
    absent=scenario.get('char_buff_absent_ids',[])
    if (not isinstance(absent,list) or not all(isinstance(b,str) and b in mechanics()['char_buffs'] for b in absent)
            or set(absent)&set(bound)):
        raise ValueError('已确认未领取的个人强化需要有效ID列表，且不能与已领取列表冲突。')
    uncertain=scenario.get('char_buff_pending_ids',[])
    if (not isinstance(uncertain,list) or not all(isinstance(b,str) and b in mechanics()['char_buffs'] for b in uncertain)
            or set(uncertain)&(set(bound)|set(absent)) or uncertain and scenario.get('char_buffs_complete') is True):
        raise ValueError('待更新的个人强化需要有效ID列表，且不能与已确认领取、未领取或完整列表冲突。')
    for bid in dict.fromkeys(uncertain):
        buff=mechanics()['char_buffs'][bid]
        if buff['required_profession'] and profile['profession'] not in buff['required_profession'].split('|'):
            raise ValueError('待更新的个人强化与当前干员职业不符。')
        if buff['relic_id'] not in selected:
            warnings.append(buff['name']+'：本局个人强化归属仍待更新；当前持有清单不能排除已领取效果，未计入该项。')
    if 'char_buffs_complete' in scenario and type(scenario['char_buffs_complete']) is not bool:
        raise ValueError('个人强化列表完整性必须为布尔值。')
    if 'char_buffs_complete' in scenario and 'char_buff_ids' not in scenario:
        raise ValueError('个人强化列表完整性必须与明确的强化ID列表一起读取。')
    for bid in dict.fromkeys(bound):
        data=mechanics()['char_buffs'].get(bid)
        if data is None:raise ValueError('未知干员定向强化 '+bid+'，不能计算。')
        if data['required_profession'] and profile['profession'] not in data['required_profession'].split('|'):
            raise ValueError(data['name']+'与当前干员职业不符，请核对强化归属。')
        inputs.append((bid,data,True))
    for rid,data,is_bound in inputs:
        if data is None:
            warnings.append('未知藏品 '+rid+'，效果未计算。');continue
        from .offline_scope import partition
        active,reference,pending,reference_pending=partition(data,rid)
        pending=list(pending);applied=[];missing=[]
        binding=data.get('recipient_binding')
        recipient_binding=None
        if binding and not is_bound:
            applicable=[bid for bid in binding['char_buff_ids'] if not mechanics()['char_buffs'][bid]['required_profession']
                        or profile['profession'] in mechanics()['char_buffs'][bid]['required_profession'].split('|')]
            confirmed=sorted(set(applicable)&set(bound))
            recipient_state=('confirmed' if confirmed else 'absent' if not applicable or scenario.get('char_buffs_complete') is True or set(applicable)<=set(absent)
                             else 'unknown')
            recipient_binding={'state':recipient_state,'char_buff_ids':confirmed,'scope':'current_operator_only'}
            if recipient_state=='unknown':missing.append('当前干员强化归属')
        # Some unfinished mechanics exist only with another held relic and
        # on the raw selector's recipients. Do not warn unrelated panels.
        for scope in data.get('pending_scopes',[]):
            if not set(scope.get('requires_relic_ids',[])).issubset(selected) or not matches(scope,profile):
                pending=[p for p in pending if p!=scope['message']]
        eligible=False
        for e in active:
            ammo_parameters=None
            own=matches(e,profile)
            token_ids=[] if is_bound else [tid for tid,t in profile.get('tokens',{}).items() if matches(e,t,token=True)]
            token=bool(token_ids)
            if not own and not token:continue
            if e.get('skill_sp_type'):
                selected_skill=profile['skills'][scenario['skill']-1]['levels'][scenario.get('skill_rank',10)-1]
                if selected_skill['sp_type']!=e['skill_sp_type']:continue
            if e['kind'] in ('received_sp','event_sp'):
                selected_skill=profile['skills'][scenario['skill']-1]['levels'][scenario.get('skill_rank',10)-1]
                if selected_skill['sp_type'] not in ('INCREASE_WITH_TIME','INCREASE_WHEN_ATTACK','INCREASE_WHEN_TAKEN_DAMAGE'):continue
            if e.get('eligible_stage_ids'):
                target=scenario.get('target_enemy')
                if not target:
                    eligible=True;missing.append('target_enemy');continue
                if target['stage_id'] not in e['eligible_stage_ids']:continue
            if e['kind']=='enemy_weight_delta':
                if not scenario.get('target_enemy'):
                    eligible=True;missing.append('target_enemy');continue
                if 'enemy_weight' not in scenario:
                    eligible=True;missing.append('enemy_weight');continue
            if e['kind']=='enemy_spawn_hp_branch' and not scenario.get('target_enemy'):
                eligible=True;missing.append('target_enemy');continue
            if e.get('target_enemy_id'):
                target=scenario.get('target_enemy')
                if not target:
                    eligible=True;missing.append('target_enemy');continue
                if target['enemy_id']!=e['target_enemy_id']:continue
            eligible=True
            if e['kind'] not in SUPPORTED:
                pending.append('计算尚未接入:'+e['kind']);continue
            if e.get('unit_condition') and token_ids:
                contexts=(scenario.get('relic_context') or {}).get('token_conditions',{})
                if not isinstance(contexts,dict):raise ValueError('召唤物藏品条件需要按召唤物ID分组的JSON对象。')
                for tid in token_ids:
                    context=contexts.get(tid,{})
                    if not isinstance(context,dict):raise ValueError('召唤物 '+tid+' 的条件需要JSON对象。')
                    factor=context_value(e,{**scenario,'relic_context':context})
                    if factor is None:
                        missing.append('token_conditions.'+tid+'.'+e['condition']);continue
                    rule={**e,'value':e['value']*factor,'relic_id':rid,'_verified_rule':True,'token_ids':[tid]}
                    applied.append(rule);token_effects.append(rule)
                token=False
                if not own:continue
            if e['kind']=='skill_forbidden':
                raise ValueError(data['name']+'禁止开启技能（含自动技能）；当前技能输出、初动和回转不可用。')
            if e['kind']=='periodic_sp':
                selected_skill=profile['skills'][scenario['skill']-1]['levels'][scenario.get('skill_rank',10)-1]
                if selected_skill['sp_type'] not in ('INCREASE_WHEN_ATTACK','INCREASE_WHEN_TAKEN_DAMAGE'):
                    pending=[p for p in pending if p!='周期回复计时相位/阻回行为待确认'];continue
                if e.get('clock')!='deployment':
                    timing_unresolved=True
                    pending.append('周期回复间隔已核验，当前计时相位/阻回脚本待确认；使用明确假设下的相位范围估算')
            if e['kind'] in ('received_sp','event_sp'):
                from .sp_events import event_phases
                event_phases(scenario)
            if e['kind']=='temporary_attack':
                if not (scenario['operator'] in ('mechanist','silverash') and scenario['skill']==3 and
                        scenario.get('timing_mode','frames')=='frames'):
                    pending.append('短时攻击尚未接入当前技能的逐事件取值路径');continue
                if scenario['operator']=='mechanist' and scenario.get('charge_count',0):
                    pending.append('未排程冲锋未套用短时攻击增益')
            if e['kind']=='temporary_ammo_speed':
                selected_skill=profile['skills'][scenario['skill']-1]['levels'][scenario.get('skill_rank',10)-1]
                if selected_skill['duration_type']!='AMMO':continue
                regular_ammo=(profile['id']=='char_1052_kalts2' and scenario['skill']==2 or
                    profile['id']=='char_4230_mcnist' and scenario['skill']==1 or
                    profile['id'] in ('char_1041_angel2','char_1035_wisdel') and scenario['skill'] in (1,3))
                if not regular_ammo or scenario.get('timing_mode','frames')!='frames':
                    pending.append('弹药限时攻速需要已接入的逐帧攻击弹药路径');continue
            if e['kind']=='ammo_refill':
                from .ammo_reference import refill_parameters,partial_packet_reference
                selected_skill=profile['skills'][scenario['skill']-1]['levels'][scenario.get('skill_rank',10)-1]
                pending=[p for p in pending if p!='未支持的特殊弹药计数器与不安全轮询窗口待接入']
                if selected_skill['duration_type']!='AMMO':continue
                ammo_sources.add(rid)
                maximum=selected_skill['values'].get('attack@trigger_time')
                ordinary=(profile['id']=='char_1052_kalts2' and scenario['skill']==2 or
                    profile['id']=='char_4230_mcnist' and scenario['skill']==1 or
                    profile['id']=='char_1041_angel2' and scenario['skill'] in (1,3) or
                    profile['id']=='char_1035_wisdel' and scenario['skill']==3)
                ammo_parameters=refill_parameters(maximum,e['threshold_ratio'],e['value'])
                if not ordinary or ammo_parameters is None:
                    ammo_unresolved=True
                    pending.append('当前技能的动态最大弹药/特殊耗弹路径未核验，未套用补弹');continue
                cost=5 if profile['id']=='char_1041_angel2' and scenario['skill']==3 else 1
                packet_reference=partial_packet_reference(profile['id'],scenario['skill'],cost)
                if ammo_parameters['can_trigger_before_empty'] and (
                        ammo_parameters['maximum']%cost or ammo_parameters['refill_count']%cost) and not packet_reference:
                    ammo_unresolved=True
                    pending.append('补弹后不足完整一次攻击的特殊耗弹路径未核验，未套用补弹');continue
                ammo_parameters['attack_cost_reference']=cost
                if packet_reference:ammo_parameters['partial_packet_reference']=packet_reference
            if e.get('recipient_condition'):
                recipient=context_value({'condition':e['recipient_condition'],'condition_type':'flag'},scenario)
                if recipient is None:missing.append(e['recipient_condition']);continue
                if not recipient:continue
            loss_unused=None
            if e['kind']=='deployment_hp_loss':
                loss_unused=context_value({'condition':e['loss_pending_condition'],'condition_type':'flag'},scenario)
                if loss_unused is None:missing.append(e['loss_pending_condition'])
            factor=context_value(e,scenario)
            if e.get('enemy_level') and scenario.get('enemy_level_type')!=e['enemy_level']:
                if scenario.get('enemy_level_type') is None:missing.append('enemy_level_type')
                continue
            if factor is None:
                missing.append(e['condition']);continue
            if e['kind']=='deployment_hp_loss' and loss_unused is None:continue
            value=e['value']*factor if e.get('scale_by_condition') or e.get('hp_curve_min') or e['kind']=='caster_end_sp' else e['value']*factor if e.get('condition')=='emergency_hire' else e['value']
            if 'factor_offset' in e:value+=e['factor_offset']
            rule={**e,'value':value,'relic_id':rid,'_verified_rule':True}
            if e.get('native_count_scale')=='float32_before_fp':
                rule.update(native_rune_base=e['value'],native_rune_factor=factor)
            if ammo_parameters is not None:rule['ammo_parameters']=ammo_parameters
            if e['kind']=='deployment_hp_loss':rule.update(hp_ratio_before=factor,loss_unused=loss_unused)
            applied.append(rule)
            if rule['kind'] in BASE_KINDS:
                if own:effects.append(rule)
                if token:token_effects.append({**rule,'token_ids':token_ids})
            elif own:
                rules.append(rule)
                if token and rule['kind'] in ('regeneration_hp_ratio','regeneration','barrier_on_deploy_ratio','evasion_chance','shield_layers'):rules.append({**rule,'token_only':True,'token_ids':token_ids})
            elif token:rules.append({**rule,'token_only':True,'token_ids':token_ids})
        if (active or data.get('pending_scopes') and not reference and not pending) and not eligible:
            inapplicable.append(rid)
            # Known scoped rules are inapplicable; unknown scripts may have another recipient.
        if pending:warnings.append(data['name']+'：未覆盖 '+ '、'.join(dict.fromkeys(pending))+'。')
        if missing:warnings.append(data['name']+'：尚未确认条件 '+ '、'.join(dict.fromkeys(missing))+'，未按0或满层套用。')
        records.append({'id':rid,'name':data['name'],'source':data['source'],'applied':applied,
            'missing_conditions':sorted(set(missing)),'pending':list(dict.fromkeys(pending)),
            'reference_effects':reference,'reference_pending':reference_pending,
            'reference_usage':data.get('usage',data.get('raw',{}).get('functionDesc','')),
            'status':'incomplete' if pending or missing else 'inapplicable' if rid in inapplicable else 'applied' if applied else 'reference_only' if reference or reference_pending else 'non_output'})
        if is_bound:records[-1].update(recipient=scenario['operator'],source_relic_id=data['relic_id'])
        if recipient_binding:
            records[-1]['recipient_binding']=recipient_binding
            if recipient_binding['state']=='confirmed':records[-1]['status']='bound'
            elif recipient_binding['state']=='absent':records[-1]['status']='inapplicable'
    # Preserve old direct effects as explicit test inputs, without trusting injected markers.
    scenario['effects']=[{k:v for k,v in e.items() if k!='_verified_rule'} for e in scenario.get('effects',[])]+effects
    scenario['relic_ids']=[]
    scenario['_token_relic_effects']=token_effects
    candidates=rules+effects+token_effects
    unresolved_hp_sources=set()
    for group in {r.get('group') for r in candidates if r.get('stacking')=='unverified'}:
        grouped=[r for r in candidates if r.get('group')==group]
        if len({r['relic_id'] for r in grouped})>1:
            if any(r['kind']=='ammo_refill' for r in grouped):ammo_unresolved=True
            unresolved_hp_sources.update(r['relic_id'] for r in grouped if r['kind']=='enemy_hp_factor')
            warnings.append('组合 '+str(group)+' 的叠加规则尚未核验，未套用该组合。')
            rules=[r for r in rules if r not in grouped]
            effects=[r for r in effects if r not in grouped]
            token_effects=[r for r in token_effects if r not in grouped]
            for record in records:
                if any(r['relic_id']==record['id'] for r in grouped):
                    record['applied']=[r for r in record['applied'] if r.get('group')!=group]
                    record['pending'].append('组合叠加规则待核验:'+str(group));record['status']='incomplete'
    resident=[r for r in rules if r.get('hp_composition')=='resident_script']
    other_hp=[r for r in rules if r['kind']=='enemy_hp_factor' and r not in resident and r['value']!=1]
    spawn_hp=[r for r in rules if r['kind']=='enemy_spawn_hp_branch']
    for record in records:
        if any(e['kind']=='enemy_hp_factor' and (
            e.get('condition') in record['missing_conditions'] or
            e.get('enemy_level') and 'enemy_level_type' in record['missing_conditions'])
            for e in mechanics()['relics'].get(record['id'],{}).get('effects',[])):
            unresolved_hp_sources.add(record['id'])
    unresolved_hp_sources.difference_update(r['relic_id'] for r in resident)
    verified_final_hp=[r for r in other_hp if r.get('hp_composition')=='final_scaler_verified']
    other_hp_sources=unresolved_hp_sources|{r['relic_id'] for r in resident+other_hp
        if r['value']!=1 and r.get('hp_composition')!='final_scaler_verified'}
    for rule in spawn_hp:
        rule['excluded_hp_sources']=sorted(other_hp_sources)
        if verified_final_hp:
            rule['verified_final_hp_sources']=sorted({r['relic_id'] for r in verified_final_hp})
        if not other_hp_sources:continue
        message='随机出生生命与其他生命藏品的组合尚未核验；保留单件分支，复合触发生命值未知'
        warnings.append(message+'。')
        for record in records:
            if record['id']==rule['relic_id']:
                record['pending'].append(message);record['status']='incomplete'
    hp_composition_pending=[]
    if resident and (other_hp or unresolved_hp_sources or spawn_hp):
        # The resident script's key differs from ordinary HP modifiers. That
        # does not prove multiplication, addition, or which source wins.
        hp_composition_pending=[r['relic_id'] for r in resident]
        rules=[r for r in rules if r not in resident]
        warnings.append('厄运火杆与其他敌方生命藏品的叠加脚本尚未核验；保留其他已接入参考，未额外乘0.6。')
        for record in records:
            if record['id'] in hp_composition_pending:
                record['applied']=[r for r in record['applied'] if r not in resident]
                record['pending'].append('居民HP与其他敌方生命藏品的组合待核验');record['status']='incomplete'
    scenario['effects']=[{k:v for k,v in e.items() if k!='_verified_rule'} for e in scenario.get('effects',[]) if not e.get('_verified_rule')]+effects
    scenario['_token_relic_effects']=token_effects
    scenario['_relic_rules']=rules
    final_attack=[r['value'] for r in rules if r['kind']=='final_attack_factor']
    if len(final_attack)==1:
        scenario['base_attack']*=final_attack[0]
        scenario['_relic_final_attack_factor']=final_attack[0]
    defense_rules=[r for r in rules if r['kind']=='enemy_def_delta']
    if len(defense_rules)==1:scenario['enemy_defense']=scenario.get('enemy_defense',0)*max(0,1+defense_rules[0]['value'])
    scenario['_relic_enemy_effects']={'defense_factor':max(0,1+defense_rules[0]['value']) if len(defense_rules)==1 else 1,
        'hp_factors':[r['value'] for r in rules if r['kind']=='enemy_hp_factor'],
        'resident_hp_applied':bool(resident and not hp_composition_pending or any(r.get('resident_hp') for r in rules)),
        'hp_composition_pending':hp_composition_pending,
        'spawn_hp_rules':spawn_hp,
        'atk_factors':[r['value'] for r in rules if r['kind']=='enemy_atk_factor'],
        'weight_delta':sum(r['value'] for r in rules if r['kind']=='enemy_weight_delta')}
    resolution={'records':records,'warnings':warnings,'inapplicable':inapplicable,'rules':rules,
        'calculation_scope':'offline_stable_effects','combat_effects_reference_only':True,
        'source_commit':mechanics()['commit'],'complete':not warnings,'enemy_effects':scenario['_relic_enemy_effects'],
        'token_effects':token_effects,'context':scenario.get('relic_context',{}),
        'context_source':scenario.get('relic_context_source','明确提供的计算情景'),'timing_unresolved':timing_unresolved}
    if ammo_unresolved:resolution['ammo_refill_unresolved']=True
    if uncertain:resolution['recipient_evidence_pending']=list(dict.fromkeys(uncertain))
    return scenario,resolution

def recharge_requirement(scenario,cost):
    return max(0,cost-sum(r['value'] for r in scenario.get('_relic_rules',[]) if r['kind'] in ('end_sp','caster_end_sp')))

def effective_skill(skill,scenario):
    rules=scenario.get('_relic_rules',[])
    factors=[r['value'] for r in rules if r['kind']=='sp_cost_factor']
    factor=factors[0] if len(factors)==1 else 1
    return {**skill,'sp_cost':skill['sp_cost']*factor,
        'initial_sp':skill['initial_sp']+sum(r['value'] for r in rules if r['kind']=='initial_sp')}

def finish(result,resolution,attributes,scenario):
    rules=resolution['rules'];warnings=resolution['warnings']
    for rule in rules:
        if rule.get('ammo_polling_pending') or rule.get('ammo_order_pending'):
            message=('补弹检查与耗尽可能同帧，检查相位未校准；本情景未套用补弹，完整技能输出/周期未知。'
                if rule.get('ammo_polling_pending') else '补弹书的合法处理顺序产生不同结果；获取先后未确认，完整技能输出/周期未知。')
            if message not in warnings:warnings.append(message)
            resolution['complete']=False
            for record in resolution['records']:
                if record['id']==rule['relic_id'] and message not in record['pending']:
                    record['pending'].append(message);record['status']='incomplete'
    if any(rule['kind']=='ammo_refill' for rule in rules):
        result['estimate']['notes'].append('补弹按原生动作：最大弹药与比例先作单精度浮点乘法，再分别向下取整阈值、向上取整补充量；50×30%会补16发，而10×30%补3发。每本书每次技能至多一次，弹药归零不补回；检查窗口与耗尽同帧的未知情景保持保护。')
    if scenario.get('_ammo_refill_reference'):
        result['ammo_refill_reference']=scenario['_ammo_refill_reference']
        if len(result['ammo_refill_reference']['cases'])>1:
            result['estimate']['notes'].append('两本书共享当前弹药计数器的恢复上限；已枚举两种合法处理顺序，只有攻击总次数一致才给出确定值。触发帧和真实获取顺序未由此确定。')
    references=result['estimate'].get('sp_events',{})
    event_label='事件技力' if any(r['kind']=='event_sp' for r in rules) else '受击技力'
    missing_events=['timing.sp_events.'+phase for phase,value in references.items() if value['status']=='missing']
    if missing_events:
        warnings.append(event_label+'缺少明确阶段事件表：'+'、'.join(missing_events)+'；不将缺失事件当作0次。')
        for record in resolution['records']:
            if any(r['kind'] in ('received_sp','event_sp') for r in record['applied']):
                record['missing_conditions']=sorted(set(record['missing_conditions']+missing_events))
                record['status']='incomplete'
    if references:
        from .sp_events import EVENT_TYPES
        event_types=sorted({r['event_type'] for r in rules if r['kind'] in ('received_sp','event_sp') and not r.get('token_only')})
        result['estimate']['notes'].extend([
            event_label+'使用局外明确分类事件：'+'、'.join(EVENT_TYPES[k] for k in event_types)+'；不从攻击间隔、总伤或闪避概率猜测触发。',
            'initial以部署完成为0秒，cycle以本次技能开启为0秒；技能及额外阻回期间丢弃事件。空表表示已确认没有事件，缺失阶段保持未知。',
            '事件仅描述本次初动和一轮周期，不自动重复为多轮稳态；屏障/零伤害的回调归属和实际客户端同帧次序仍需校准。'])
    def protection(rules,hp):
        values=[]
        for r in rules:
            if r['kind'] not in ('barrier_on_deploy_ratio','evasion_chance','shield_layers'):continue
            value={'kind':r['kind'],'relic_id':r['relic_id'],'name':mechanics()['relics'][r['relic_id']]['name']}
            if r['kind']=='barrier_on_deploy_ratio':value.update(value=None if hp is None else hp*r['value'],hp_reference=hp)
            elif r['kind']=='shield_layers':
                prior=next((v for v in values if v['kind']=='shield_layers' and v['relic_id']==r['relic_id']),None)
                if prior is not None:prior['value']+=r['value'];continue
                value['value']=r['value']
            else:value.update(value=r['value'],damage_type=r['damage_type'])
            values.append(value)
        return values
    event_warnings=[w for w in result.get('warnings',[]) if w.startswith('首伤藏品：')]
    warnings.extend(w for w in event_warnings if w not in warnings)
    if event_warnings:
        for record in resolution['records']:
            if any(r['kind']=='first_damage_scale' for r in record['applied']):
                record['pending'].extend(event_warnings);record['status']='incomplete'
    if resolution['timing_unresolved'] and '_wine_phase_frame' not in scenario:
        skill=result['estimate']['skill']
        for key in ('initial_seconds','recharge_seconds'):
            if skill[key]!=0:skill[key]=None
        for key in ('cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps'):skill[key]=None
        result['estimate']['notes'].append('酒类每次回复按离散事件发生；缺少计时相位和阻回规则，未将其替换为平均每秒技力。技能单次伤害仍按已确认情景计算。')
    from .relic_attributes import is_attribute_rune
    scalers=[r for r in rules if r['kind']=='redeploy_delta' and not is_attribute_rune(r)]
    if len(scalers)==1:result['estimate']['base_stats']['redeploy_seconds']*=1+scalers[0]['value']
    elif scalers:warnings.append('多个最终再部署缩放的叠加规则尚未核验，此组合未套用。')
    healing=[r for r in rules if r['kind']=='healing_factor']
    if len(healing)==1:
        factor=healing[0]['value']
        if result.get('total_healing') is not None:result['total_healing']*=factor
        skill=result['estimate']['skill']
        for key in ('total_healing','phase_healing','window_healing','cycle_healing','cycle_hps','window_hps'):
            if skill.get(key) is not None:skill[key]*=factor
        subtotals=result.get('known_healing_subtotals',{})
        for key in ('total_healing','phase_healing','window_healing','cycle_healing','cycle_hps','window_hps'):
            if subtotals.get(key) is not None:subtotals[key]*=factor
        for c in result.get('components',[]):
            if c.get('damage_type')=='healing':
                c['total']*=factor;c['per_hit']*=factor
                if c.get('event_amounts') is not None:c['event_amounts']=[amount*factor for amount in c['event_amounts']]
                for source in c.get('known_healing_sources',[]):
                    source['total']*=factor;source['per_hit']*=factor
                    if source.get('event_amounts') is not None:source['event_amounts']=[amount*factor for amount in source['event_amounts']]
        amiya=result.get('amiya_phase_reference')
        if amiya and amiya['kind']=='medical_opening':
            amiya['opening_healing_reference']*=factor
            amiya['window_reference']['opening_healing_reference']*=factor
    regeneration={r['relic_id']:r['value'] for r in rules if r['kind']=='regeneration_factor'}
    factor=next(iter(regeneration.values())) if len(regeneration)==1 else 1
    result['relic_regeneration_multiplier']=factor
    for c in result.get('components',[]):
        if c.get('damage_type')=='regeneration':c['total']*=factor;c['per_hit']*=factor
    result['relic_regeneration_rate']=(sum(r['value'] for r in rules if r['kind']=='regeneration' and not r.get('token_only'))+
        result['estimate']['base_stats']['hp']*sum(r['value'] for r in rules if r['kind']=='regeneration_hp_ratio' and not r.get('token_only')))*factor
    if any(r['kind']=='regeneration_hp_ratio' for r in rules):
        result['estimate']['notes'].append('百分比生命回复按当前常态最大生命参考，单独报告，不混入直接治疗HPS；技能期间最大生命变化未作动态积分。')
    result['relic_features']=[r for r in rules if r['kind'] in ('deployment_cost_add','block_add',
        'status_duration_delta','incoming_element_resistance','token_deploy_slot_free')]
    result['deployment_cost']=max(0,attributes['deployment_cost']+
        sum(r['value'] for r in rules if r['kind']=='deployment_cost_add' and not r.get('token_only')))
    from .catalog import catalog
    profile=catalog()['operators'][scenario['operator']]
    result['relic_token_stats']=[]
    from .summons import module_reference,token_attributes,token_cost_reference
    for tid,token in profile.get('tokens',{}).items():
        applied=[e for e in resolution['token_effects'] if tid in e.get('token_ids',[])]
        run_effects=[e for e in scenario.get('_attribute_runes',[])+scenario.get('effects',[])
                    if e.get('origin')=='run_squad' and e.get('target_scope')=='all_units']
        module=module_reference(profile,scenario,tid)
        cost_module=token_cost_reference(profile,scenario,tid)
        features=[r for r in rules if r.get('token_only') and tid in r.get('token_ids',[])]
        sources=(['模组'] if module or cost_module else [])+(['藏品'] if applied or cost_module and features else [])+(['分队'] if run_effects else [])
        applied+=run_effects
        from .summons import manual_token_stat_effects
        manual_effects=manual_token_stat_effects(scenario,tid)
        if manual_effects:
            applied+=manual_effects
            sources.append('手动输入')
        if not applied and not features and not module and not cost_module:continue
        from .relic_attributes import is_attribute_rune
        runes=[e for e in applied if is_attribute_rune(e)]
        def total(kind):return sum(e['value'] for e in applied+features if e['kind']==kind and not is_attribute_rune(e))
        stats=token_attributes(profile,scenario,tid,total('hp_pct'),rune_effects=runes)
        for key,kind in (('attack','attack_pct'),('defense','defense_pct')):stats[key]*=1+total(kind)
        stats['attack_speed']=effective_attack_speed(stats['attack_speed']+total('attack_speed'))
        stats['resistance']=min(100,stats['resistance']+sum(e['value'] for e in manual_effects if e['kind']=='resistance_flat'))
        stats['deployment_cost']=max(0,stats['deployment_cost']+total('deployment_cost_add'))
        stats['free_deployment_slot']=bool(total('token_deploy_slot_free'))
        if total('regeneration_hp_ratio') or total('regeneration'):
            stats['regeneration_rate']=(None if stats['hp'] is None and total('regeneration_hp_ratio') else
                ((stats['hp'] or 0)*total('regeneration_hp_ratio')+total('regeneration'))*factor)
        if stats.get('module_reference',{}).get('hp_composition_pending'):
            warnings.append('触手：模组生命与藏品/分队生命的叠加层尚未核验，复合生命及依赖该生命的回复未知；单项参考分别列出。')
        stats['protection']=protection(features,stats['hp'])
        result['relic_token_stats'].append({'id':tid,'name':token['name'],'modifier_sources':sources or ['藏品'],**stats})
    result['relic_protection']=protection([r for r in rules if not r.get('token_only')],result['estimate']['base_stats']['hp'])
    result['estimate']['base_stats']['block_count']+=sum(r['value'] for r in rules if r['kind']=='block_add' and not r.get('token_only'))
    result['estimate']['base_stats']['defense']+=sum(r['value'] for r in rules if r['kind']=='defense_flat' and not r.get('token_only'))
    from .deployment import finish_deployment
    finish_deployment(result,resolution,attributes,profile)
    from .elemental_relics import finish_neural_reference
    finish_neural_reference(result)
    if resolution.get('ammo_refill_unresolved') or any(r.get('ammo_polling_pending') or r.get('ammo_order_pending') for r in rules):
        skill=result['estimate']['skill']
        for key in ('total_damage','total_healing','phase_damage','phase_healing','duration_seconds',
                    'cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps',
                    'window_damage','window_healing','window_seconds','window_dps','window_hps'):
            if key in skill:skill[key]=None
        result['total_damage']=None
        if 'total_healing' in result:result['total_healing']=None
        result['timing']['cycle_seconds']=None
        source=profile['skills'][scenario['skill']-1]['levels'][scenario.get('skill_rank',10)-1]
        if source['sp_type']!='INCREASE_WITH_TIME' or any(r['kind']=='periodic_sp' for r in rules):
            skill['recharge_seconds']=None
        result['estimate']['notes'].append('本情景存在未核验的补弹耗弹/获取顺序/检查窗口，完整技能输出和周期未知；未套用部分不能当作零收益。基础属性及不依赖技能耗尽的初动/充能保留。')
    resolution['complete']=not warnings
    result['relic_resolution']=resolution
    result['inapplicable_relics']=resolution['inapplicable']
    result['warnings'].extend(warnings)
    result['complete']=result['complete'] and not warnings
    result['complete_definition']='complete 仅指当前局外计算范围内的已支持部分；资料栏的战斗触发效果未计入，也不表示完整实战模拟。'
    result['estimate']['complete']=result['estimate']['complete'] and not warnings
    if result['estimate']['warnings'] is not result['warnings']:result['estimate']['warnings'].extend(warnings)
    if resolution['records']:
        result['estimate']['notes'].append('藏品按固定版本黑板、职业/分支/位置及已确认条件解析；资料核验不代表隐藏脚本和实战全部已验证。')
    if any(r['kind']=='automatic_skill' for r in rules):
        result['estimate']['notes'].append('零食盒已计入技力需求缩放，并会自动开启技能；当前时序按技力就绪后开启估计，真实客户端开启帧仍需校准。')
    finite_speed=[r for r in rules if r['kind']=='deployment_attack_speed']
    if finite_speed:
        from .timing import finite
        age=finite(scenario.get('deployment_elapsed_seconds',0),'部署经过秒数',3600)
        stats=result['estimate']['base_stats'];skill=result['estimate']['skill']
        permanent=stats.get('attack_speed_reference',stats['attack_speed'])
        active=sum(r['value'] for r in finite_speed if age<r['duration'])
        start=scenario.get('_deployment_skill_start_seconds',0)
        skill_bonus=sum(r['value'] for r in finite_speed if start<r['duration'])
        reference=skill.get('skill_attack_speed_reference',skill['skill_attack_speed'])
        stats['attack_speed_reference']=permanent+active
        stats['attack_speed']=effective_attack_speed(permanent+active)
        skill['skill_attack_speed_reference']=reference+skill_bonus
        skill['skill_attack_speed']=effective_attack_speed(reference+skill_bonus)
        result['attack_speed_reference']+=skill_bonus
        result['attack_speed']=effective_attack_speed(result['attack_speed_reference'])
        result['deployment_buff_reference']={'spans':[{'id':r['relic_id'],'attack_speed_addition':r['value'],
            'start_seconds':0,'end_seconds':r['duration']} for r in finite_speed],
            'snapshot_age_seconds':age,'permanent_attack_speed':permanent,
            'first_skill_start_seconds':start,'live_state_verified':False,
            'expiry_attack_sampling':'attack_start_reference'}
        result['estimate']['notes'].append('疗养卡攻速只在本次部署前10秒叠加，参与初动攻击、技能与充能期事件；基础属性按指定部署经过时间显示，周期表示首轮，不将限时收益沿用为稳态。到期动画仍按攻击开始帧采样参考。')
