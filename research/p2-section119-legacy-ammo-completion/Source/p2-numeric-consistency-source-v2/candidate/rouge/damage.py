"""Deterministic, inspectable damage calculations; no model-generated numbers."""
import math
from .condition_inputs import validate_continuous_attacks
from .attribute_limits import effective_attack_speed
from .catalog import catalog
from .timing import AttackTimeline
from .enemy_environment import damage_factor


def _skill_damage(scenario: dict) -> dict:
    result=_skill_damage_base(scenario)
    if not any(r['kind']=='first_damage_scale' for r in scenario.get('_relic_rules',[])):return result
    from .relic_events import first_damage,DAMAGE
    components=result.get('components')
    if components is None and result.get('hits') is not None and result.get('damage_type') in DAMAGE:
        times=(result.get('timing',{}).get('streams') or [{}])[0].get('times_seconds')
        components=[{'name':'技能伤害','damage_type':result['damage_type'],'hits':result['hits'],
            'per_hit':result['per_hit'],'total':result['total_damage'],'times_seconds':times}]
        result['components']=components
    extra=first_damage(components or [],scenario)
    if extra is None:
        result['warnings'].append('首伤藏品：输出缺少完整事件时序或同帧多来源顺序未核验，未套用首次伤害倍率。')
        result['complete']=False
    elif extra:
        result['total_damage']+=extra
    return result


def _skill_damage_base(scenario: dict) -> dict:
    scenario=dict(scenario)
    companion_is_bool=isinstance(scenario.get('companion_attack'),bool)
    profile=catalog()['operators'][scenario['operator']]
    skill=scenario.get('skill')
    rank=scenario.get('skill_rank',10)
    if not isinstance(skill,int) or isinstance(skill,bool) or not 1<=skill<=len(profile['skills']):
        raise ValueError('请选择该干员的有效技能。')
    if not isinstance(rank,int) or isinstance(rank,bool) or not 1<=rank<=10:
        raise ValueError('技能等级需要为1–10的整数。')
    for field in ('base_attack','enemy_defense','enemy_resistance','window_seconds','companion_attack'):
        if field not in scenario:continue
        value=float(scenario[field])
        if not math.isfinite(value) or value<0 or (field=='enemy_resistance' and value>100):
            raise ValueError(f'{field} 需要有限非负数；法抗范围为 0–100。')
        scenario[field]=value
    for field in ('skill_rank','activation_count','deployment_stacks','shield_break_count','charge_count'):
        if field not in scenario:continue
        value=float(scenario[field])
        if not math.isfinite(value) or not value.is_integer() or value<0 or (field=='deployment_stacks' and value>2):
            raise ValueError(f'{field} 需要非负整数；部署触发叠层最多为 2。')
        scenario[field]=int(value)
    mechanist = scenario.get('operator') == 'mechanist' and scenario.get('skill') == 1
    silver = scenario.get('operator') == 'silverash' and scenario.get('skill') == 3
    bombard = scenario.get('operator') == 'mechanist' and scenario.get('skill') == 3
    shield = scenario.get('operator') == 'mechanist' and scenario.get('skill') == 2
    frost = scenario.get('operator') == 'silverash' and scenario.get('skill') == 2
    healing = scenario.get('operator') == 'kaltsit' and scenario.get('skill') in (1,3)
    utility=scenario.get('operator')=='silverash' and scenario.get('skill')==1
    if not (mechanist or silver or bombard or shield or frost or healing or utility) and (scenario.get('operator') != 'kaltsit' or scenario.get('skill') != 2):
        raise ValueError('This skill profile has not yet been implemented.')
    base_attack = float(scenario['base_attack'])
    if not math.isfinite(base_attack) or base_attack < 0:
        raise ValueError('Base attack must be finite and nonnegative.')
    profile = catalog()['operators'][scenario['operator']]
    rank = int(scenario.get('skill_rank', 10))
    if not 1 <= rank <= 10:
        raise ValueError('技能等级需要在 1–10 之间（8/9/10 为专精一/二/三）。')
    skill_profile = profile['skills'][scenario['skill']-1]['levels'][rank-1]
    bb = skill_profile['values']
    attack_bonus = bb.get('atk', 0)
    effects = list(scenario.get('effects', []))
    inapplicable = []
    warnings = []
    for rid in scenario.get('relic_ids', []):
        relic = catalog()['relics'].get(rid)
        if relic is None:
            warnings.append(f'未知藏品 {rid}，效果未计算。')
            continue
        if not relic['supported']:
            warnings.append(f'{relic["name"]}：效果尚未计算。')
            continue
        eligible = [e for e in relic['effects'] if
                    (not e.get('profession') or profile['profession'] in e['profession'].split('|')) and
                    (not e.get('position') or e['position'] == {'ranged': 'ranged', 'melee': 'melee'}[profile['position']])]
        effects.extend(eligible)
        if not eligible:
            inapplicable.append(rid)
    for effect in effects:
        value = float(effect['value'])
        signed=effect.get('_verified_rule') and effect['kind'] in ('hp_pct','attack_speed')
        if not math.isfinite(value) or (value < 0 and not signed) or effect['kind'] not in ('attack_pct','attack_speed','damage_taken',
                'hp_pct','defense_pct','resistance_flat','sp_recovery'):
            raise ValueError('加成必须是有限非负数，且使用已支持的效果类型。')
        if effect['kind'] == 'attack_pct':
            attack_bonus += value
    attack = base_attack * (1 + attack_bonus)
    status = {'complete': not warnings, 'warnings': warnings,
              'complete_definition':'complete 仅指所选藏品是否均有已实现的适用规则，不代表完整战斗模拟。',
              'scope':'指定技能伤害部分，单个持续命中的目标。',
              'assumptions':['时间按完整攻击间隔估计，未模拟首击、前后摇、帧取整及空转。',
                             '培养条件采用已读记录或明确标注的预览条件；模组条件机制、特训、条件藏品及难度环境修正尚未完整套用。']}
    if shield:status['scope']='仅实际屏障破碎的法术爆炸，未计普通攻击。'
    if silver and not scenario.get('preexisting_fragile',False):
        status['assumptions'].append('此算例全程未计技能脆弱，不模拟第一击后施加脆弱的动态过程。')
    base_speed_reference=scenario.get('_attribute_attack_speed',100)+sum(float(e['value']) for e in effects if e['kind']=='attack_speed')
    speed_reference=base_speed_reference+bb.get('attack_speed',0)
    # ATTACK_SPEED has no upper attribute bound; attack timing separately caps it.
    base_speed=effective_attack_speed(base_speed_reference)
    speed=effective_attack_speed(speed_reference)
    def taken(dtype):
        return (1 + sum(float(e['value']) for e in effects if e['kind'] == 'damage_taken' and e.get('damage_type') == dtype))*damage_factor(scenario,dtype)
    def timed_damage(raw,scale,dtype,events,multiplier=1):
        releases=events.get('emitted_release_frames' if 'window_seconds' not in scenario else 'hit_release_frames',[])
        amounts=[]
        for frame in releases:
            bonus=sum(r['value'] for r in scenario.get('_relic_rules',[]) if
                r['kind']=='temporary_attack' and 0<=frame<r['duration']*30)
            value=raw+base_attack*bonus*scale
            dealt=max(value-scenario.get('enemy_defense',0),value*.05) if dtype=='physical' else max(
                value*(1-scenario.get('enemy_resistance',0)/100),value*.05)
            amounts.append(dealt*taken(dtype)*multiplier)
        return amounts
    interval = (profile['phases'][2]['frames'][-1]['interval'] + bb.get('base_attack_time', 0)) * 100 / speed
    status.update(attack_speed=speed,base_attack_speed=base_speed,
        attack_speed_reference=speed_reference,base_attack_speed_reference=base_speed_reference,
        interval_seconds=interval,applied_effects=effects)
    timeline=AttackTimeline(scenario)
    empty_enemy=timeline.options.get('target_disappears_seconds')==0
    empty_ammo_target=empty_enemy or timeline.options.get('target_windows')==[]
    medical_fallback=not healing and scenario['operator']=='kaltsit' and empty_ammo_target and float(scenario.get('healing_targets',1))>0
    def attack_events(duration,limit=None):
        stream=timeline.attacks(duration,interval,speed,attribute_speed=speed_reference,limit=limit,
            target_scope='friendly' if healing or medical_fallback else 'enemy')
        if timeline.mode=='frames' and 'window_seconds' not in scenario:
            stream['times_seconds']=stream['emitted_times_seconds']
        status['timing']=timeline.output()
        if timeline.mode=='frames':status['interval_seconds']=stream['interval_seconds']
        return stream
    if utility:
        status['scope']='回费及后续部署屏障技能，没有直接伤害或治疗；屏障不作为治疗。'
        return {'attack':attack,'total_damage':0,'total_healing':0,'inapplicable_relics':inapplicable,**status}
    if healing:
        duration=min(float(scenario.get('window_seconds',skill_profile['duration'])),skill_profile['duration'])
        hits=len(attack_events(duration)['times_seconds'])
        status['scope']='本体技能期间普通治疗，未计医者丰碑的进入范围增益。'
        return {'attack':attack,'total_damage':0,'total_healing':attack*hits,'hits':hits,
                'per_heal':attack,'inapplicable_relics':inapplicable,**status}
    if frost:
        raw = attack * bb['atk_scale']
        damage = max(raw - scenario.get('enemy_defense', 0), raw * .05) * taken('physical')
        own_count = int(scenario.get('activation_count', 1))
        components = [{'name': '本体技能触发', 'hits': 0 if empty_enemy else own_count, 'damage_type': 'physical', 'per_hit': damage, 'total': 0 if empty_enemy else damage * own_count}]
        stacks = int(scenario.get('deployment_stacks', 0))
        if stacks:
            if companion_is_bool:raise ValueError('companion_attack 不接受布尔值；请使用数值。')
            recipient = float(scenario['companion_attack']) * bb['atk_scale']
            hit = max(recipient - scenario.get('enemy_defense', 0), recipient * .05) * taken('physical')
            components.append({'name': '受益干员部署触发', 'hits': 0 if empty_enemy else stacks, 'damage_type': 'physical', 'per_hit': hit, 'total': 0 if empty_enemy else hit * stacks})
        return {'attack': attack, 'total_damage': sum(c['total'] for c in components), 'components': components, 'inapplicable_relics': inapplicable, **status}
    if shield:
        count = int(scenario.get('shield_break_count', 0))
        if empty_enemy:count=0
        raw = attack * bb['atk_scale']
        damage = max(raw * (1 - scenario.get('enemy_resistance', 0) / 100), raw * .05) * taken('magic')
        return {'attack': attack, 'per_hit': damage, 'total_damage': damage * count,
                'hits': count, 'damage_type': 'magic', 'inapplicable_relics': inapplicable, **status}
    if bombard:
        events=attack_events(min(float(scenario.get('window_seconds', skill_profile['duration'])), skill_profile['duration']))
        hits=len(events['times_seconds'])
        per_hit = max(attack * bb['attack@atk_scale'] * (1 - scenario.get('enemy_resistance', 0) / 100), attack * bb['attack@atk_scale'] * .05)
        charge = max(attack * bb['atk_scale'] - scenario.get('enemy_defense', 0), attack * bb['atk_scale'] * .05)
        per_hit *= taken('magic')
        charge *= taken('physical')
        count = int(scenario.get('charge_count', 0))
        if count and scenario.get('window_seconds') == 0:
            raise ValueError('零长度观察窗口不能声明冲锋命中。')
        components = [{'name': '轰击', 'damage_type': 'magic', 'hits': hits, 'per_hit': per_hit, 'total': hits * per_hit,'times_seconds':events['times_seconds']},
                      {'name': '结构性原理冲锋', 'damage_type': 'physical', 'hits': count, 'per_hit': charge, 'total': count * charge}]
        if empty_enemy:
            components[1].update(hits=0,total=0)
        if any(r['kind']=='temporary_attack' for r in scenario.get('_relic_rules',[])):
            amounts=timed_damage(attack*bb['attack@atk_scale'],bb['attack@atk_scale'],'magic',events)
            components[0].update(event_amounts=amounts,total=sum(amounts),per_hit=sum(amounts)/len(amounts) if amounts else per_hit)
            status['timing']['notes'].append('短时攻击按出手帧取值后逐击减伤；实际弹体快照模板仍需校准。')
        return {'attack': attack, 'total_damage': sum(c['total'] for c in components), 'components': components, 'inapplicable_relics': inapplicable, **status}
    if silver:
        per_hit = max(attack * bb['bird_atk_scale'] - scenario.get('enemy_defense', 0), attack * bb['bird_atk_scale'] * .05)
        per_hit *= taken('physical')
        per_hit *= bb['damage_scale'] if scenario.get('preexisting_fragile', False) else 1
        duration = min(float(scenario.get('window_seconds', skill_profile['duration'])), skill_profile['duration'])
        stream=attack_events(duration);events=stream['times_seconds'];hits=len(events)
        components = [{'name': '本体丹增', 'damage_type':'physical','hits': hits, 'per_hit': per_hit, 'total': hits * per_hit,'times_seconds':events}]
        if any(r['kind']=='temporary_attack' for r in scenario.get('_relic_rules',[])):
            amounts=timed_damage(attack*bb['bird_atk_scale'],bb['bird_atk_scale'],'physical',stream,
                bb['damage_scale'] if scenario.get('preexisting_fragile',False) else 1)
            components[0].update(event_amounts=amounts,total=sum(amounts),per_hit=sum(amounts)/len(amounts) if amounts else per_hit)
            status['timing']['notes'].append('短时攻击按出手帧取值后逐击减伤；实际丹增/协同触发取值模板仍需校准。')
        if scenario.get('cooperative'):
            components.append({**components[0],'name':'协同丹增'})
        return {'attack': attack, 'per_hit': components[0]['per_hit'], 'total_damage': sum(c['total'] for c in components), 'damage_type': 'physical', 'components': components, 'inapplicable_relics': inapplicable, **status}
    raw = attack * bb['attack@atk_scale']
    damage = max(raw - scenario.get('enemy_defense', 0), raw * .05) if mechanist else raw
    damage *= taken('physical' if mechanist else 'true')
    from .relic_events import ammunition_rounds
    shots = ammunition_rounds(int(bb['attack@trigger_time']),1,scenario,minimum_interval=interval*speed/600)
    status['ammo_rounds']=shots
    if scenario.get('_ammo_refill_reference'):
        status['ammo_refill_reference']=scenario['_ammo_refill_reference']
    events=attack_events(scenario.get('window_seconds',3600),limit=shots)
    if timeline.mode=='continuous' and 'window_seconds' not in scenario and not empty_ammo_target:
        hits=shots*int(bb.get('attack@times',1))
    else:hits=len(events['times_seconds'])*int(bb.get('attack@times',1))
    if timeline.mode=='frames':
        from .timing import frame_time
        spacing=frame_time(bb.get('attack@interval',0)) if mechanist else 0
        intrinsic=frame_time(bb.get('attack@projectile_delay_time',0)) if mechanist else 0
        travel=frame_time(scenario.get('timing',{}).get('projectile_travel_seconds',0))
        pellet_count=int(bb.get('attack@times',1))
        impacts=[t+intrinsic+travel+i*spacing for t in events['release_frames'] for i in range(pellet_count)
            if ('window_seconds' not in scenario or t+intrinsic+travel+i*spacing<frame_time(scenario['window_seconds']))
            and (medical_fallback or timeline.selectable_lifetime(t+intrinsic+travel+i*spacing))]
        events['impact_frames']=impacts;events['times_seconds']=[t/30 for t in impacts]
        hits=len(impacts)
        status['execution_seconds']=(events['release_frames'][-1]+(pellet_count-1)*spacing+1)/30 if len(events['release_frames'])>=shots else None
        if status['execution_seconds'] is not None:
            events['resume_frame']=max(0,events['start_frames'][-1]+events['interval_frames']-frame_time(status['execution_seconds']))
        if mechanist:status['timing']['notes'].append('机械师S1按档案projectile_delay_time和attack@interval分配五连击；字段与客户端落地/发射行为的绑定仍待录屏校准。')
    elif any(r['kind']=='deployment_attack_speed' for r in scenario.get('_relic_rules',[])) and 'window_seconds' not in scenario:
        status['execution_seconds']=events['times_seconds'][-1] if len(events['times_seconds'])>=shots else None
    if empty_ammo_target and not medical_fallback:status['execution_seconds']=None
    if medical_fallback:
        status['healing_hits']=hits
    damage_hits=0 if empty_ammo_target else hits
    components=[{'name':'五连击' if mechanist else '弹药攻击','damage_type':'physical' if mechanist else 'true',
        'hits':damage_hits,'per_hit':damage,'total':damage*damage_hits,'times_seconds':[] if empty_ammo_target else events['times_seconds']}]
    return {'attack': attack, 'per_hit': damage, 'total_damage': damage * damage_hits, 'hits': damage_hits,'components':components,
        'interval_seconds': interval, 'damage_type': 'physical' if mechanist else 'true', 'inapplicable_relics': inapplicable, **status}


def _prepare_damage(scenario: dict):
    from .catalog import operator_attributes
    scenario=dict(scenario)
    profile=catalog()['operators'][scenario['operator']]
    skill=scenario.get('skill');rank=scenario.get('skill_rank',10)
    if not isinstance(skill,int) or isinstance(skill,bool) or not 1<=skill<=len(profile['skills']):
        raise ValueError('请选择该干员的有效技能。')
    if not isinstance(rank,int) or isinstance(rank,bool) or not 1<=rank<=10:
        raise ValueError('技能等级需要为1–10的整数。')
    attributes=operator_attributes(scenario['operator'],scenario.get('elite',2),scenario.get('level'),
                                   scenario.get('trust',100),scenario.get('potential',1),
                                   scenario.get('module_id'),scenario.get('module_level',0))
    scenario.setdefault('base_attack',attributes['attack'])
    elite=scenario.get('elite',2)
    if profile['skills'][skill-1].get('unlock_elite',skill-1)>elite or (elite<2 and rank>7):
        raise ValueError('当前精英阶段尚未开放所选技能或专精。')
    if scenario['operator']=='silverash' and skill==3 and isinstance(scenario.get('preexisting_fragile'),str):
        raise ValueError('preexisting_fragile不接受字符串，请提供明确的布尔条件。')
    if scenario['operator']=='silverash' and skill==3 and isinstance(scenario.get('cooperative'),str):
        raise ValueError('cooperative不接受字符串，请提供明确的布尔条件。')
    # Preserve raw count types before either engine converts them to numbers.
    from .reporting import has_healing
    active_counts=[]
    if has_healing(scenario['operator'],skill):
        active_counts.append(('healing_targets','治疗目标数需要为 0–100 的整数。'))
    if scenario['operator']=='char_1037_amiya3' and skill==2:
        active_counts.append(('amiya_hit_targets','amiya_hit_targets需要1到100之间的整数。'))
    if scenario['operator']=='char_4087_ines':
        active_counts.append(('stolen_enemy_count','stolen_enemy_count需要范围内的有限非负整数。'))
    for field,error in active_counts:
        if isinstance(scenario.get(field),bool):raise ValueError(error)
    declared_counts={('mechanist',2):('shield_break_count',),
                     ('mechanist',3):('charge_count',),
                     ('silverash',2):('activation_count','deployment_stacks')}
    for field in declared_counts.get((scenario['operator'],skill),()):
        if isinstance(scenario.get(field),bool):
            raise ValueError(f'{field} 需要非负整数；部署触发叠层最多为 2。')
    from .relics import prepare
    from .run_modifiers import prepare_run
    scenario,run_resolution=prepare_run(scenario)
    numeric_bool_fields=[field for field in ('base_attack','enemy_defense','enemy_resistance','window_seconds')
                         if isinstance(scenario.get(field),bool)]
    scenario,resolution=prepare(scenario,profile)
    from .relic_attributes import prepare_attribute_runes
    scenario,attributes=prepare_attribute_runes(scenario,attributes)
    if numeric_bool_fields:
        raise ValueError(numeric_bool_fields[0]+' 不接受布尔值；请使用数值。')
    # Reuse the existing numeric-zero gates after validating the raw timing.
    timing=scenario.get('timing',{})
    if isinstance(timing,dict) and isinstance(timing.get('target_disappears_seconds'),str):
        from .timing import finite
        AttackTimeline(scenario)
        if finite(timing['target_disappears_seconds'],'target_disappears_seconds',3600)==0:
            scenario['timing']={**timing,'target_disappears_seconds':0}
    return scenario,attributes,resolution,run_resolution


@validate_continuous_attacks
def _evaluate_damage_once(prepared,wine_phase=None) -> dict:
    """Consume one isolated preparation; finishers may annotate its resolutions."""
    from .estimate import build_estimate
    from .relics import finish
    from .run_modifiers import finish_run
    scenario,attributes,resolution,run_resolution=prepared
    scenario.pop('_wine_phase_frame',None)
    if wine_phase is not None:scenario['_wine_phase_frame']=wine_phase
    if scenario['operator'] not in ('kaltsit','silverash','mechanist'):
        from .operator_engine import Combat
        combat=Combat(scenario,attributes)
        result=combat.calculate()
    else:
        result=_skill_damage(scenario)
        result['estimate']=build_estimate(scenario,result,attributes,_skill_damage)
    from .charge_reference import finish_charge_reference
    finish_charge_reference(scenario,result)
    from .shield_break_reference import finish_shield_break_reference
    finish_shield_break_reference(scenario,result)
    from .timing import annotate_result
    annotate_result(scenario,result)
    finish(result,resolution,attributes,scenario)
    finish_run(result,run_resolution)
    if scenario['operator']=='kaltsit' and scenario['skill'] in (1,3):
        # The internal helper supplies healing per recipient to build_estimate.
        # Public totals use its capped recipient count and requested window,
        # after the finishers have applied relic multipliers exactly once.
        result['total_healing']=result['estimate']['skill']['window_healing']
    from .attribute_limits import finalize_attack_speed_references
    finalize_attack_speed_references(result)
    from .summons import finish_duration_references
    finish_duration_references(scenario,result)
    from .reporting import build_report
    result['report']=build_report(scenario,result)
    # Validate the processed neural scenario after preserving legacy errors.
    if scenario['operator'] in ('char_1042_phatm2','char_4204_mantra'):
        for field in ('enemy_is_boss','enemy_in_neural_break'):
            if isinstance(scenario.get(field),str):
                raise ValueError(field+' 不接受文本条件；请使用布尔值。')
    if scenario['operator']=='char_4202_haruka' and scenario['skill']==2 and isinstance(scenario.get('haruka_repeat'),str):
        raise ValueError('haruka_repeat 不接受文本条件；请使用布尔值。')
    if (scenario['operator']=='char_1048_orchd2' and
            isinstance(scenario.get('near_previous_deployment'),str)):
        from .operator_engine import selected_talents
        talents,_=selected_talents(catalog()['operators'][scenario['operator']],scenario)
        if any(t.get('name')=='翔虫机动' for t in talents):
            raise ValueError('near_previous_deployment 不接受文本条件；请使用布尔值。')
    # Keep legacy calculation/finisher/report errors before text-only conditions.
    op=scenario['operator'];number=scenario['skill']
    conditions={
        'char_4228_closur':('reinforcement_blocks_target',),
        'char_206_gnosis':('frozen_at_skill_end',) if number==3 else (),
        'char_4087_ines':('ines_first_deployment',) if number==3 else (),
        'char_1041_angel2':('steal_success',) if number==2 else ('delivery_coordinate',) if number==3 else (),
        'char_1035_wisdel':('overload',) if number==2 else (),
    }.get(op,())
    if op=='char_4182_oblvns':
        conditions=(('ranged_attack',) if combat.ranged_attack_condition_consumed else ())
        if number==2:conditions+=('organ_mode','fever')
    if op in ('char_437_mizuki','char_1048_orchd2'):
        field,talent=('enemy_below_half','反移情') if op=='char_437_mizuki' else ('power_coating','强击瓶专家')
        if isinstance(scenario.get(field),str):
            from .operator_engine import selected_talents
            talents,_=selected_talents(catalog()['operators'][op],scenario)
            if any(t.get('name')==talent for t in talents):conditions+=(field,)
        if op=='char_1048_orchd2' and number==1:conditions+=('double_charge',)
    for field in conditions:
        if isinstance(scenario.get(field),str):
            raise ValueError(field+' 不接受文本条件；请使用布尔值。')
    return result

def _evaluate_damage(prepared,wine_phase=None) -> dict:
    """Resolve deployment readiness before placing finite buffs or wine pulses."""
    from copy import deepcopy
    from .reporting import build_report
    rules=prepared[0].get('_relic_rules',[])
    finite_speed=any(r['kind']=='deployment_attack_speed' for r in rules)
    deployment_clock=finite_speed or any(r['kind']=='periodic_sp' and r.get('clock')=='deployment' for r in rules)
    if not deployment_clock:return _evaluate_damage_once(prepared,wine_phase)
    first_result=_evaluate_damage_once(deepcopy(prepared),wine_phase)
    first=first_result['estimate']['skill']['initial_seconds']
    if first is None:
        result=first_result
        if finite_speed:
            skill=result['estimate']['skill']
            for key in ('total_damage','total_healing','phase_damage','phase_healing','cycle_seconds','cycle_damage',
                        'cycle_healing','cycle_dps','cycle_hps','window_damage','window_healing','window_dps','window_hps'):
                if key in skill:skill[key]=None
            result['total_damage']=None;result['total_healing']=None
            result['estimate']['notes'].append('初动条件未确认，无法定位技能与部署后10秒攻速加成的重叠；依赖该重叠的输出保持未知。')
            result['report']=build_report(prepared[0],result)
        return result
    pristine=deepcopy(prepared)
    pristine[0]['_deployment_skill_start_seconds']=first
    result=_evaluate_damage_once(pristine,wine_phase)
    result['deployment_clock_reference']={'first_skill_start_seconds':first,
        'origin':'deployment','owner_tick_boundary_frames':1,'live_state_verified':False}
    result['estimate']['notes'].append('限时藏品与酒类共享部署时钟；技能在预计初动时开启，充能期沿用原计时，不按每轮重新获得部署加成。部署挂载与首个owner逻辑帧存在至多一帧边界。')
    result['report']=build_report(pristine[0],result)
    return result

def _calculate_damage(scenario: dict,wine_phase=None) -> dict:
    return _evaluate_damage(_prepare_damage(scenario),wine_phase)


class _PhaseBounds:
    """Retain extrema and eligibility, rather than every complete calculation."""
    def __init__(self):
        self.count=0
        self.known=True
        self.lower=self.upper=None

    def include(self,value):
        self.count+=1
        if not isinstance(value,(int,float)):
            self.known=False
            return
        self.lower=value if self.lower is None else min(self.lower,value)
        self.upper=value if self.upper is None else max(self.upper,value)


def calculate_damage(scenario: dict) -> dict:
    from copy import deepcopy
    prepared=_prepare_damage(scenario)
    wines=[r for r in prepared[2]['rules'] if r['kind']=='periodic_sp']
    if len(wines)!=1 or all(w.get('clock')=='deployment' for w in wines):return _evaluate_damage(prepared)
    from .timing import frame_time
    from .reporting import build_report
    # Each possible 30-Hz phase, including immediate and full-period first tick.
    # Initial and post-block phases are independent marginal envelopes.
    phases=frame_time(wines[0]['interval'])+1
    keys=('initial_seconds','recharge_seconds','cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps')
    skill_bounds={key:_PhaseBounds() for key in keys}
    metric_bounds={}
    for phase in range(phases):
        # Copy together to preserve aliases between rules and resolution records.
        # Never share a finisher's mutations with another phase or request.
        result=_evaluate_damage(deepcopy(prepared),phase)
        for key,bounds in skill_bounds.items():bounds.include(result['estimate']['skill'][key])
        metrics={(b['id'],m['key']):m['value'] for b in result['report']['sections'] for m in b['metrics']}
        for key,value in metrics.items():
            if key not in metric_bounds:metric_bounds[key]=_PhaseBounds()
            metric_bounds[key].include(value)
    skill=result['estimate']['skill']
    for key in keys:
        bounds=skill_bounds[key]
        if not bounds.known:
            skill[key]=None
            continue
        lower,upper=bounds.lower,bounds.upper
        skill[key+'_range']={'lower':lower,'upper':upper}
        skill[key]=lower if abs(upper-lower)<1e-9 else None
    result['estimate']['notes'].append('酒类相位范围：逐一枚举30Hz参考帧的下一次回复相位（立即至一个完整间隔），逐事件合并攻击/受击技力；不换算平均每秒技力。')
    result['estimate']['notes'].append('范围假设：技能及额外阻回期间不接收、不积存酒类技力，阻回结束后的相位重新包络；初动和回转分别取范围，不表示同一条已测实战时间线。隐藏脚本、攻击模板与实战相位仍待校准。')
    result['relic_resolution']['phase_estimate']={'mode':'frame_envelope','phases':phases,
        'blocking':'discard_blocked_ticks','verified_phase':False,'verified_blocking_script':False}
    result['timing']['initial_seconds']=skill['initial_seconds']
    result['timing']['cycle_seconds']=skill['cycle_seconds']
    result['report']=build_report(scenario,result)
    # Metrics are ranged from complete event calculations, including non-monotone DPS.
    for block in result['report']['sections']:
        for row in block['metrics']:
            bounds=metric_bounds.get((block['id'],row['key']))
            if bounds and bounds.known and bounds.count==phases:
                lower,upper=bounds.lower,bounds.upper
                if abs(upper-lower)>1e-9:
                    row['value']=None;row['range']={'lower':lower,'upper':upper}
    return result
