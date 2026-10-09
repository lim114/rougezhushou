"""Attribute and repeat-cycle estimates, with explicit conditions and unknowns."""
import math
from .condition_inputs import read_continuous_attacks
from .catalog import catalog
from .enemy_environment import damage_factor
from .timing import AttackTimeline,charge_seconds,frame_time,FPS,finite,phase_totals,has_periodic_sp


def build_estimate(scenario,result,attributes,compute_skill):
    operator=scenario['operator']
    profile=catalog()['operators'][operator]
    skill_index=scenario['skill']
    skill=profile['skills'][skill_index-1]['levels'][int(scenario.get('skill_rank',10))-1]
    from .relics import effective_skill,recharge_requirement
    skill=effective_skill(skill,scenario)
    effects=result['applied_effects']
    def total(kind):return sum(e['value'] for e in effects if e['kind']==kind)
    def nonnegative(field,default):
        value=float(scenario.get(field,default))
        if not math.isfinite(value) or value<0:raise ValueError(f'{field} 需要有限非负数。')
        return value
    elapsed=nonnegative('deployment_elapsed_seconds',0)
    extra_sp=nonnegative('initial_sp_bonus',0)
    extra_rate=nonnegative('sp_recovery_bonus',0)
    healing_targets=nonnegative('healing_targets',1)
    if not healing_targets.is_integer() or healing_targets>100:
        raise ValueError('治疗目标数需要为 0–100 的整数。')
    elite=scenario.get('elite',2)
    level=scenario.get('level') or profile['phases'][elite]['max_level']
    potential=scenario.get('potential',1)
    talents=[]
    for candidates in profile['talents']:
        eligible=[t for t in candidates if t['phase']<=elite and
                  (t['phase']<elite or t['level']<=level) and t['potential_rank']<=potential-1]
        if eligible:talents.append(max(eligible,key=lambda t:(t['phase'],t['level'],t['potential_rank'])))
    hp_bonus=defense_bonus=defense_flat=block_bonus=talent_sp=0
    redeploy_scale=1
    talent_notes=[]
    for talent in talents:
        bb=talent['values']
        if operator=='kaltsit' and talent['name']=='遗尘守望':
            hp_bonus+=bb['max_hp'];defense_bonus+=bb['def'];block_bonus+=bb['block_cnt']
            talent_notes.append(talent['name'])
        if operator=='silverash' and talent['name']=='开放性开局':
            talent_sp+=bb['sp'];redeploy_scale*=bb['respawn_time']
            talent_notes.append('开放性开局：自身初始技力及下次再部署时间')
        if operator=='silverash' and talent['name']=='雪境先驱':
            defense_flat+=bb['def']*(2 if elapsed>=bb['interval'] else 1)
            talent_notes.append('雪境先驱：自身防御按在场时间计算；被动生命回复不混入技能治疗量')
    stats={
        'hp':attributes['hp']*(1+hp_bonus+total('hp_pct')),
        'attack':float(scenario['base_attack'])*(1+total('attack_pct')),
        'defense':attributes['defense']*(1+defense_bonus+total('defense_pct'))+defense_flat,
        'resistance':min(100,attributes['resistance']+total('resistance_flat')),
        'redeploy_seconds':attributes['redeploy_seconds']*redeploy_scale,
        'attack_speed':result['base_attack_speed'],
        'attack_speed_reference':result['base_attack_speed_reference'],
        'block_count':attributes['block_count']+block_bonus}
    normal_interval=attributes['interval']*100/stats['attack_speed']
    sp_rate=attributes['sp_recovery']+total('sp_recovery')+extra_rate
    initial_sp=skill['initial_sp']+talent_sp+extra_sp
    recharge=initial=None
    notes=[
        '基础数值先按培养、信赖、潜能和模组计算，再套用藏品/分队符文，最后计算已覆盖天赋；不含技能加成。',
        '回转为本次开启至下次开启；充能为技能结束后恢复一份技力的时间。',
        '周期 DPS/HPS 包含技能与充能期普攻/普疗，按单个敌人和指定满额受疗目标计算。',
        '秒数为连续供靶估计，未模拟首击、前后摇、帧取整、移动和空转。',
        '已支持已选模组的基础属性；模组条件机制、机械师特训、分队和难度环境修正仍有缺失。',
        *talent_notes]
    if operator=='silverash' and skill_index==3:
        notes.append('技能脆弱按所选“全程计入/全程未计”假设，未模拟施加延迟、衰减和结束后的残留时间。')
        notes.append('协同丹增仅在选中持续覆盖时计入；协同攻击使用凛御银灰攻击力。')
    if float(scenario['base_attack'])!=attributes['attack'] and '_relic_final_attack_factor' not in scenario:
        notes.append('基础攻击使用手动测试值；其余属性仍来自当前选择的培养条件。')
    unconfirmed=scenario.get('unconfirmed_training',[])
    inventory=scenario.get('inventory_status')
    if inventory:
        if inventory.get('source')=='manual_test':
            notes.insert(0,'藏品来自手动情景测试选择，不代表已读取的本局持有状态。')
        elif not inventory.get('complete'):
            expected=inventory.get('expected_count')
            notes.insert(0,f'本局藏品读取未完整：已确认 {inventory.get("recognized",0)} 件，总数 '+
                         (str(expected) if expected is not None else '未确认')+'；使用本局已确认记录，变更或遗漏效果仍待核对。')
        else:notes.insert(0,f'藏品来自本局自动读取并保留的记录：已确认 {inventory.get("recognized",0)} 件。')
    if unconfirmed:
        notes.insert(0,'尚未从画面确认：'+ '、'.join(unconfirmed)+'；当前使用清楚标出的数据档案预览条件，不代表本局真实面板。')
    if scenario.get('module_id'):
        module=next(m for m in profile['modules'] if m['id']==scenario['module_id'])
        if elite>=module['unlock_elite'] and level>=module['unlock_level']:
            notes.append('当前模组基础属性已参与估算；条件伤害和召唤物模组机制尚未完整计入。')
        else:
            notes.append('所选模组未满足当前精英阶段或等级门槛，本次未计模组基础属性与能力覆盖。')
    if skill['sp_type']=='INCREASE_WITH_TIME' and sp_rate>0:
        recharge=recharge_requirement(scenario,skill['sp_cost'])/sp_rate
        initial=max(0,skill['sp_cost']-initial_sp)/sp_rate
    elif skill['sp_type']=='INCREASE_WHEN_ATTACK':
        if read_continuous_attacks(scenario) or has_periodic_sp(scenario):
            recharge=charge_seconds(scenario,skill['sp_cost'],skill['sp_increment'],normal_interval,stats['attack_speed'],attribute_speed=stats['attack_speed_reference'])
            initial=charge_seconds(scenario,max(0,skill['sp_cost']-initial_sp),skill['sp_increment'],normal_interval,stats['attack_speed'],attribute_speed=stats['attack_speed_reference'],initial=True)
            notes.append('攻击回复按实际出手事件计入规定技力；适用酒类另按离散周期事件合并，自然回复速率不代替攻击回复。')
        else:notes.append('攻击回复缺少持续攻击条件，初动与回转未知。')
    else:notes.append('缺少可用技力恢复条件，初动与回转未知。')
    full_scenario={k:v for k,v in scenario.items() if k!='window_seconds'}
    if operator=='silverash' and skill_index==1:
        notes.append('周旋的谋略提供费用/屏障，单次直接伤害与治疗为 0；屏障不作为治疗。')
    if operator=='silverash' and skill_index==2:
        full_scenario.update(activation_count=1,deployment_stacks=0)
        notes.append('御敌的锋锐单次技能仅计本体一次；受益干员部署触发在情景分项中另列。')
    if operator=='mechanist' and skill_index==3:
        full_scenario['charge_count']=0  # Collision time and full-cast count are unverified.
    full=compute_skill(full_scenario)
    damage=full['total_damage']
    healing=0
    duration=max(0,skill['duration'])
    if skill['duration_type']=='AMMO':
        if operator=='mechanist' and skill_index==2:
            duration=None
            damage=None
            if 'skill_duration_seconds' in scenario:
                duration=nonnegative('skill_duration_seconds',0)
                if duration<=0:raise ValueError('指定技能持续时间需要大于 0 秒。')
                raw=full['attack']
                hit=max(raw-float(scenario.get('enemy_defense',0)),raw*.05)
                hit*=1+sum(e['value'] for e in effects if e['kind']=='damage_taken' and e.get('damage_type')=='physical')
                hit*=damage_factor(scenario,'physical')
                damage=full['total_damage']+math.floor(duration/full['interval_seconds']+1e-9)*hit
                if (scenario.get('timing_mode','frames')=='frames' or
                        scenario.get('timing',{}).get('target_disappears_seconds')==0 or
                        scenario.get('timing',{}).get('target_windows')==[]):
                    timeline=AttackTimeline(scenario,normal=True)
                    stream=timeline.attacks(duration,normal_interval,stats['attack_speed'],attribute_speed=stats['attack_speed_reference'])
                    events=stream.get('emitted_times_seconds',stream['times_seconds'])
                    damage=full['total_damage']+len(events)*hit
                    full['components']=[{'name':'指定破屏爆炸','damage_type':'magic','total':full['total_damage']},
                        {'name':'协防术式期间普通攻击','damage_type':'physical','total':len(events)*hit,'times_seconds':events}]
                    full['timing']=timeline.output()
                    result['timing']=timeline.output()
                notes.append('协防术式按指定时间结束（可手动停止），计入本体普攻和给定总破屏次数；不据此推断弹药耗尽时刻。')
            else:
                notes.append('协防术式依赖本体/结构性原理屏障破碎与弹药消耗，单次完整技能总伤和持续时间未知。可指定本次技能结束时间进行条件估算；情景爆炸伤害另列。')
        else:duration=full.get('execution_seconds',full.get('ammo_rounds',skill['values']['attack@trigger_time'])*full['interval_seconds'])
    if operator=='kaltsit' and skill_index==2:
        healing=full['attack']*skill['values']['attack@heal_scale']*full.get('healing_hits',full['hits'])*healing_targets
        notes.append('治疗量为满额潜在治疗，未扣过量治疗；医者丰碑的进入范围增益另行建模。')
    if operator=='kaltsit' and skill_index in (1,3):
        maximum=2 if skill_index==3 else 1
        healing=full['total_healing']*min(maximum,healing_targets)
        notes.append(f'{skill["name"]}每次治疗至多 {maximum} 个目标；治疗量未扣过量治疗。')
    window_healing=0
    if operator=='kaltsit':
        if skill_index==2:
            window_healing=result['attack']*skill['values']['attack@heal_scale']*result.get('healing_hits',result['hits'])*healing_targets
        else:window_healing=result['total_healing']*min(2 if skill_index==3 else 1,healing_targets)
    window_seconds=nonnegative('window_seconds',duration or 0)
    if duration is not None:window_seconds=min(window_seconds,duration)
    if scenario.get('timing_mode','frames')=='frames':
        if initial is not None:initial=frame_time(initial)/FPS
        if duration is not None:duration=frame_time(duration)/FPS
        lockout=float(scenario.get('timing',{}).get('sp_lockout_extra_seconds',0))
        if not math.isfinite(lockout) or not 0<=lockout<=3600:raise ValueError('额外阻回需要0–3600秒。')
        if duration is not None and skill['sp_type']=='INCREASE_WHEN_ATTACK' and (read_continuous_attacks(scenario) or has_periodic_sp(scenario)):
            resume=max((s.get('resume_frame',0) for s in full.get('timing',{}).get('streams',[])),default=0)
            recharge=charge_seconds(scenario,skill['sp_cost'],skill['sp_increment'],normal_interval,stats['attack_speed'],attribute_speed=stats['attack_speed_reference'],offset=duration+lockout,resume=max(0,resume-frame_time(lockout)))
        if recharge is not None:recharge=frame_time(recharge+lockout)/FPS
        if recharge is not None:recharge=max(recharge,math.ceil(finite(scenario.get('timing',{}).get('post_skill_lock_frames',0),'技能结束硬直帧'))/FPS)
    from .sp_events import has_event_sp,charge as event_charge
    if scenario.get('timing_mode','frames')=='continuous' and duration is not None and skill['sp_type']=='INCREASE_WHEN_ATTACK' and any(
            r['kind']=='deployment_attack_speed' or r['kind']=='periodic_sp' and r.get('clock')=='deployment'
            for r in scenario.get('_relic_rules',[])):
        lockout=finite(scenario.get('timing',{}).get('sp_lockout_extra_seconds',0),'额外阻回秒数',3600)
        recharge=charge_seconds(scenario,skill['sp_cost'],skill['sp_increment'],normal_interval,
            stats['attack_speed'],attribute_speed=stats['attack_speed_reference'],offset=duration+lockout)
        if recharge is not None:recharge+=lockout
    sp_events={}
    if has_event_sp(scenario):
        sp_events['initial']=event_charge(scenario,skill,max(0,skill['sp_cost']-initial_sp),
            sp_rate,normal_interval,stats['attack_speed'],attribute_speed=stats['attack_speed_reference'],initial=True)
        initial=sp_events['initial']['seconds']
        if duration is not None:
            resume=max((s.get('resume_frame',0) for s in full.get('timing',{}).get('streams',[])),default=0)
            sp_events['cycle']=event_charge(scenario,skill,skill['sp_cost'],sp_rate,normal_interval,
                stats['attack_speed'],attribute_speed=stats['attack_speed_reference'],offset=duration,resume=resume)
            recharge=sp_events['cycle']['seconds']
        else:recharge=None
    cycle=(duration+recharge) if duration is not None and recharge is not None else None
    placed_components=full.get('components',[])
    if not placed_components and full.get('timing',{}).get('streams'):
        times=full['timing']['streams'][0]['times_seconds']
        placed_components=[{'damage_type':'physical','total':damage,'times_seconds':times},
            {'damage_type':'healing','total':healing,'times_seconds':times}]
    elif healing and full.get('timing',{}).get('streams') and not any(c.get('damage_type')=='healing' for c in placed_components):
        placed_components=[*placed_components,{'damage_type':'healing','total':healing,
            'times_seconds':full['timing']['streams'][0]['times_seconds']}]
    phase_damage,phase_healing=damage,healing
    if scenario.get('timing_mode','frames')=='frames' and duration is not None and placed_components:
        phase_damage,phase_healing=phase_totals(placed_components,duration)
        if 'window_seconds' not in scenario:
            window_healing=phase_healing
    cycle_damage=cycle_healing=cycle_dps=cycle_hps=None
    if cycle is not None and cycle>0:
        resume=max((s.get('resume_frame',0) for s in full.get('timing',{}).get('streams',[])),default=0)
        normal=AttackTimeline({**scenario,'timing':{**scenario.get('timing',{}),'_resume_frames':resume}},normal=True,offset=duration)
        normal_hits=len(normal.attacks(recharge,normal_interval,stats['attack_speed'],attribute_speed=stats['attack_speed_reference'],
            target_scope='friendly' if operator=='kaltsit' else 'enemy')['times_seconds'])
        if skill['sp_type']=='INCREASE_WHEN_ATTACK' and not read_continuous_attacks(scenario):
            normal_hits=0
            normal.streams=[]
        normal_damage=normal_healing=0
        if operator=='kaltsit':normal_healing=normal_hits*stats['attack']*min(1,healing_targets)
        else:
            raw=stats['attack']
            physical=max(raw-float(scenario.get('enemy_defense',0)),raw*.05)
            physical*=1+sum(e['value'] for e in effects if e['kind']=='damage_taken' and e.get('damage_type')=='physical')
            physical*=damage_factor(scenario,'physical')
            normal_damage=normal_hits*physical
            if any(r['kind']=='first_damage_scale' for r in scenario.get('_relic_rules',[])):
                from .relic_events import first_damage
                extra=first_damage([{'name':'充能期普攻','damage_type':'physical','per_hit':physical,
                    'hits':normal_hits,'total':normal_damage,'times_seconds':normal.streams[0]['times_seconds'] if normal.streams else []}],
                    {**scenario,'_first_damage_consumed_in_skill':bool(damage)},normal=True)
                if extra:normal_damage+=extra
        cycle_damage=damage+normal_damage
        cycle_healing=healing+normal_healing
        if scenario.get('timing_mode','frames')=='frames' and placed_components:
            inside_damage,inside_healing=phase_totals(placed_components,cycle)
            cycle_damage=inside_damage+normal_damage;cycle_healing=inside_healing+normal_healing
        cycle_dps=cycle_damage/cycle;cycle_hps=cycle_healing/cycle
        result.setdefault('timing',normal.output())['recharge_streams']=normal.streams
    return {'base_stats':stats,**({'sp_events':sp_events} if sp_events else {}),'skill':{
        'name':skill['name'],'initial_seconds':initial,'recharge_seconds':recharge,'cycle_seconds':cycle,
        'duration_seconds':duration,'total_damage':damage,'total_healing':healing,
        'phase_damage':phase_damage,'phase_healing':phase_healing,
        'cycle_dps':cycle_dps,'cycle_hps':cycle_hps,'cycle_damage':cycle_damage,'cycle_healing':cycle_healing,
        'sp_type':skill['sp_type'],'initial_sp':initial_sp,'sp_cost':skill['sp_cost'],
        'sp_recovery_per_second':sp_rate if skill['sp_type']=='INCREASE_WITH_TIME' else None,
        'skill_attack':full['attack'],'skill_attack_speed':full['attack_speed'],
        'skill_attack_speed_reference':full['attack_speed_reference'],'healing_targets':int(healing_targets),
        'window_healing':window_healing,'window_damage':result['total_damage'] if 'window_seconds' in scenario else phase_damage,
        'window_seconds':window_seconds},
        'training':{'elite':elite,'level':level,'trust':scenario.get('trust',100),'potential':potential,
                    'module_id':scenario.get('module_id'),'module_level':scenario.get('module_level',0)},
        'complete':result['complete'] and not unconfirmed and not scenario.get('module_id') and
                   (not inventory or inventory.get('complete',False)),
        'warnings':result['warnings'],'notes':notes,
        'scenario_scope':result['scope']}


def format_estimate(result):
    if 'report' in result:
        from .reporting import format_report
        return format_report(result)
    estimate=result['estimate'];stats=estimate['base_stats'];skill=estimate['skill']
    def number(value):return '未知' if value is None else f'{value:,.2f}'.rstrip('0').rstrip('.')
    def seconds(value):return '未知' if value is None else f'{value:.2f} 秒'
    training=estimate['training']
    lines=['预计属性（含已支持的天赋和藏品）：',
        f"生命值：{number(stats['hp'])}    攻击力：{number(stats['attack'])}    防御：{number(stats['defense'])}    法抗：{number(stats['resistance'])}",
        f"再部署时间：{seconds(stats['redeploy_seconds'])}    攻速：{number(stats['attack_speed'])}（游戏数值单位，基础 100）",
        f"阻挡数：{number(stats['block_count'])}",
        f"培养条件：精英 {training['elite']} · 等级 {training['level']} · 信赖加成进度 {training['trust']}% · 潜能 {training['potential']}",
        '', '技能情况：',
        f"（{skill['name']}）：预计回转：{seconds(skill['cycle_seconds'])}    预计初动：{seconds(skill['initial_seconds'])}",
        f"周期 DPS/HPS：{number(skill['cycle_dps'])} / {number(skill['cycle_hps'])}",
        f"单次技能总伤/总治疗量：{number(skill['total_damage'])} / {number(skill['total_healing'])}",
        f"技能持续：{seconds(skill['duration_seconds'])}    技能结束后充能：{seconds(skill['recharge_seconds'])}",
        f"技能期间攻击力：{number(skill['skill_attack'])}    技能期间攻速：{number(skill['skill_attack_speed'])}",
        '',f"当前指定情景伤害：{number(result['total_damage'])}（指定窗口/触发次数可能不同于完整单次技能）",
        '当前情景范围：'+estimate['scenario_scope'],
        '计算状态：'+('支持范围内估算' if estimate['complete'] else '不完整（见未确认条件与未覆盖项）'),
        '', '计算条件与未覆盖项：', *['• '+note for note in estimate['notes']],
        *['• '+warning for warning in estimate['warnings']]]
    if 'mode' in skill:
        modes={'infinite':'无限持续','passive':'常驻被动','switch':'切换模式','once':'整场限用一次',
               'once_deploy':'结束后退场','deployment':'部署触发，无原地回转','triggered_ammo':'布子弹药，结束时间依赖实际触发',
               'ammo':'攻击弹药','next_attack':'强化/替代下次攻击','instant':'瞬时触发','timed':'有限持续'}
        lines.insert(9,'技能类型：'+modes.get(skill['mode'],skill['mode']))
        if skill.get('window_seconds'):
            lines.extend(['',f"情景窗口：{seconds(skill['window_seconds'])}    窗口平均 DPS/HPS：{number(skill['window_dps'])} / {number(skill['window_hps'])}"])
    if result.get('components'):
        lines.extend(['','输出分项（潜在损伤积累和生命回复不合并为直接伤害/治疗）：'])
        for item in result['components']:
            lines.append(f"• {item['name']}：{number(item.get('hits'))} 次 · {item.get('damage_type','')} · 总量 {number(item['total'])}")
    return '\n'.join(lines)
