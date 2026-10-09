"""30 Hz event scheduling. Unknown animation bindings stay explicitly unknown."""
from functools import lru_cache
import json
import math
from .condition_inputs import read_continuous_attacks
from pathlib import Path

from .attribute_limits import effective_attack_speed

FPS=30

def finite(value,label,maximum=108000):
    if isinstance(value,bool):raise ValueError(label+'不能是布尔值。')
    try:value=float(value)
    except (TypeError,ValueError):raise ValueError(label+'需要有限非负数。') from None
    if not math.isfinite(value) or not 0<=value<=maximum:raise ValueError(label+'需要范围内有限非负数。')
    return value

def frame_time(seconds):return math.ceil(finite(seconds,'时间',3600)*FPS-1e-9)
def cadence(seconds):return max(1,math.floor(finite(seconds,'攻击间隔',3600)*FPS+.5+1e-9))

def has_periodic_sp(scenario):
    return any(r['kind']=='periodic_sp' for r in scenario.get('_relic_rules',[]))

def wine_events(scenario,horizon,offset=0,initial=False):
    """Relative owner-clock pulses; blocked ticks are discarded, never reset."""
    events=[]
    for wine in scenario.get('_relic_rules',[]):
        if wine['kind']!='periodic_sp':continue
        period=frame_time(wine['interval'])
        if wine.get('clock')=='deployment':
            origin=frame_time(offset+(0 if initial else scenario.get('_deployment_skill_start_seconds',0)))
            # Owner buffs tick before BasicSkill ends the skill on this frame.
            # A pulse exactly at the blocking boundary is still discarded.
            first=(origin//period+1)*period
            events.extend((f-origin,wine['value']) for f in range(first,origin+horizon,period))
        else:
            phase=scenario.get('_wine_phase_frame',period)
            events.extend((f+1,wine['value']) for f in range(phase,horizon,period))
    return events

def periodic_charge_seconds(scenario,required,increment,interval,speed,offset=0,initial=False,resume=0,
                            wait_next_attack=False,incoming_interval=None,attribute_speed=None):
    """Merge discrete credits after blocking, using each verified owner timer."""
    from .relics import recharge_requirement
    if not initial:required=recharge_requirement(scenario,required)
    if required<=0 and not wait_next_attack:return 0
    wines=[r for r in scenario['_relic_rules'] if r['kind']=='periodic_sp']
    horizon=min(108000,min(frame_time(w['interval'])*(math.ceil(required/w['value'])+1)+2 for w in wines))
    config=dict(scenario.get('timing',{}))
    if initial:
        for key in ('target_windows','movement_windows','interrupt_windows'):
            config.pop(key,None)
            if 'initial_'+key in config:config[key]=config['initial_'+key]
        config.pop('target_disappears_seconds',None);config.pop('post_skill_lock_frames',None)
    elif offset:
        config['post_skill_lock_frames']=max(0,finite(config.get('post_skill_lock_frames',0),'技能结束硬直帧')-
                                           frame_time(config.get('sp_lockout_extra_seconds',0)))
    config['_resume_frames']=resume
    config['_deployment_initial']=initial
    timeline=AttackTimeline({**scenario,'timing':config},normal=True,offset=offset)
    # Next-attack skills still need an attack slot after SP readiness.
    stream=timeline.attacks((min(108000-frame_time(offset),horizon) if not wait_next_attack else
                            max(0,108000-frame_time(offset)))/FPS,interval,speed,attribute_speed=attribute_speed)
    events=wine_events(scenario,horizon,offset,initial)
    if incoming_interval is not None:
        if incoming_interval>0:
            step=frame_time(incoming_interval)
            events.extend((f+1,increment) for f in range(step,horizon,step))
    elif read_continuous_attacks(scenario,active=lambda:increment+sum(r['value'] for r in scenario.get('_relic_rules',[]) if r['kind']=='attack_sp')>0):
        increment+=sum(r['value'] for r in scenario.get('_relic_rules',[]) if r['kind']=='attack_sp')
        events.extend((f+1,increment) for f in stream['release_frames'])
    charge=0;ready=0 if required<=0 else None
    for frame,value in sorted(events):
        if ready is not None:break
        charge+=value
        if charge>=required:ready=frame
    if ready is None:return None
    if wait_next_attack:
        start=next((f for f in stream['start_frames'] if f>=ready),None)
        return start/FPS if start is not None else None
    return ready/FPS

@lru_cache(maxsize=1)
def profiles():
    path=Path(__file__).with_name('data')/'timing-profiles.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'operators':{}}

@lru_cache(maxsize=1)
def impact_delays():
    """Documented projectile delays, separate from unverified animation bindings."""
    path=Path(__file__).with_name('data')/'skill-impact-delays.json'
    return json.loads(path.read_text(encoding='utf-8'))

def charge_seconds(scenario,required,increment,interval,speed,offset=0,initial=False,resume=0,wait_next_attack=False,attribute_speed=None):
    if has_periodic_sp(scenario):
        return periodic_charge_seconds(scenario,required,increment,interval,speed,offset,initial,resume,wait_next_attack,attribute_speed=attribute_speed)
    from .relics import recharge_requirement
    if not initial:required=recharge_requirement(scenario,required)
    increment+=sum(r['value'] for r in scenario.get('_relic_rules',[]) if r['kind']=='attack_sp')
    if required<=0 and not wait_next_attack:return 0
    if increment<=0:return None
    config=dict(scenario.get('timing',{}))
    if initial:
        for key in ('target_windows','movement_windows','interrupt_windows'):
            config.pop(key,None)
            if 'initial_'+key in config:config[key]=config['initial_'+key]
        config.pop('target_disappears_seconds',None)
        config.pop('post_skill_lock_frames',None)
    elif offset:
        config['post_skill_lock_frames']=max(0,finite(config.get('post_skill_lock_frames',0),'技能结束硬直帧')-frame_time(config.get('sp_lockout_extra_seconds',0)))
    config['_resume_frames']=resume
    config['_deployment_initial']=initial
    timeline=AttackTimeline({**scenario,'timing':config},normal=True,offset=offset)
    count=math.ceil(required/increment)
    events=timeline.attacks(max(0,3600-offset),interval,speed,attribute_speed=attribute_speed,limit=count+int(wait_next_attack))
    frames=events['release_frames']
    if len(frames)<count:return None
    if wait_next_attack and timeline.mode=='frames':
        if len(events['start_frames'])<=count:return None
        return events['start_frames'][count]/FPS
    # SP credited on a release is usable on the following simulated logic tick.
    # This ordering keeps the charging hit within the prior cycle, once only.
    return (frames[count-1]+1)/FPS if timeline.mode=='frames' else events['times_seconds'][count-1]


def mixed_charge_seconds(scenario,required,rate,attack_sp,interval,speed,offset=0,initial=False,stun=0,resume=0,blocked_seconds=0,attribute_speed=None):
    from .relics import recharge_requirement
    if not initial:required=recharge_requirement(scenario,required)
    attack_sp+=sum(r['value'] for r in scenario.get('_relic_rules',[]) if r['kind']=='attack_sp')
    blocked=frame_time(blocked_seconds)/FPS
    if required<=0:return blocked
    config=dict(scenario.get('timing',{}))
    if initial:
        for key in ('target_windows','movement_windows','interrupt_windows'):
            config.pop(key,None)
            if 'initial_'+key in config:config[key]=config['initial_'+key]
        config.pop('post_skill_lock_frames',None)
        config.pop('target_disappears_seconds',None)
    elif stun:
        config['interrupt_windows']=[*config.get('interrupt_windows',[]),[offset,offset+stun]]
    config['_resume_frames']=resume
    config['_deployment_initial']=initial
    timeline=AttackTimeline({**scenario,'timing':config},normal=True,offset=offset)
    stream=timeline.attacks(max(0,3600-offset),interval,speed,attribute_speed=attribute_speed)
    charge=0;last=0
    times=[frame/FPS for frame in stream['release_frames']] if timeline.mode=='frames' else stream['times_seconds']
    for time in times:
        if time<blocked:continue
        last=max(last,blocked)
        wait=(required-charge)/rate if rate>0 else math.inf
        if last+wait<=time:return frame_time(last+wait)/FPS if timeline.mode=='frames' else last+wait
        charge+=rate*(time-last)+attack_sp;last=time
        if charge>=required:return (frame_time(time)+1)/FPS if timeline.mode=='frames' else time
    if rate>0:
        remaining=max(last,blocked)+max(0,required-charge)/rate
        return frame_time(remaining)/FPS if timeline.mode=='frames' else remaining
    return None


class AttackTimeline:
    def __init__(self,scenario,normal=False,offset=0,target_scope='enemy'):
        if target_scope not in ('enemy','friendly'):raise ValueError('目标来源需要为enemy或friendly。')
        self.target_scope=target_scope
        self.s=scenario;self.normal=normal;self.offset=frame_time(offset)
        self.mode=scenario.get('timing_mode','frames')
        if self.mode not in ('frames','continuous'):raise ValueError('时序模式需要为frames或continuous。')
        self.options=scenario.get('timing',{})
        if not isinstance(self.options,dict):raise ValueError('时序情景需要是对象。')
        from .animation_reference import descriptor
        for normal_reference in (False,True):
            descriptor(scenario['operator'],scenario['skill'],self.options,normal=normal_reference)
        for key in ('windup_frames','recovery_frames','start_delay_frames','post_skill_lock_frames'):
            if key in self.options:finite(self.options[key],key)
        for key in ('sp_lockout_extra_seconds','projectile_travel_seconds','target_disappears_seconds'):
            if key in self.options:finite(self.options[key],key,3600)
        self.streams=[];self.notes=[];self.target_scope_notes=[]
        self.deployment_offset=0 if self.options.get('_deployment_initial') else frame_time(scenario.get('_deployment_skill_start_seconds',0))
        self.windows=self.ranges('target_windows')
        self.blocked=sorted(self.ranges('movement_windows')+self.ranges('interrupt_windows'))

    def ranges(self,key):
        if key not in self.options:return []
        value=self.options[key]
        if not isinstance(value,list) or len(value)>100:raise ValueError(key+'需要最多100组秒数区间。')
        found=[]
        for pair in value:
            if not isinstance(pair,(list,tuple)) or len(pair)!=2:raise ValueError(key+'每组需要开始和结束秒数。')
            start,end=map(frame_time,pair)
            if end<=start:raise ValueError(key+'结束时间必须晚于开始时间。')
            found.append((start,end))
        return sorted(found)

    def selectable(self,frame):
        if self.target_scope=='friendly' and (self.options.get('target_disappears_seconds')==0 or
                self.options.get('target_windows')==[]):return self.selectable_lifetime(frame)
        return self.selectable_lifetime(frame) and ('target_windows' not in self.options or any(a<=frame<b for a,b in self.windows))

    def unavailable(self,frame):return any(a<=frame<b for a,b in self.blocked)

    def descriptor(self,unit=None):
        key=unit or self.s['operator'];p=profiles()['operators'].get(key,{})
        from .animation_reference import descriptor
        chosen=descriptor(key,self.s['skill'],self.options,normal=self.normal)
        if chosen:return chosen,True
        selected=p.get('normal') if self.normal else p.get('skills',{}).get(str(self.s['skill']))
        return selected or p.get('normal') or {},bool(selected)

    def attacks(self,seconds,interval,speed=100,unit=None,limit=None,delay=0,start_delay=0,ramp=None,attribute_speed=None,target_scope=None):
        if target_scope is not None and target_scope!=self.target_scope:
            child=AttackTimeline(self.s,normal=self.normal,offset=self.offset/FPS,target_scope=target_scope)
            stream=child.attacks(seconds,interval,speed,unit=unit,limit=limit,delay=delay,
                start_delay=start_delay,ramp=ramp,attribute_speed=attribute_speed)
            self.streams.extend(child.streams)
            note='空敌方供靶或0秒敌人生命周期不取消友方潜在治疗；其它既有情景时钟保留参考，真实友方获取时钟未核验。'
            if target_scope=='friendly' and note not in self.notes:
                self.notes.append(note);self.target_scope_notes.append(note)
            return stream
        if attribute_speed is None:attribute_speed=speed
        if unit is not None:
            scoped=self.options.get('units',{})
            if not isinstance(scoped,dict) or not isinstance(scoped.get(unit,{}),dict):raise ValueError('独立单位时序需要对象。')
            config=dict(scoped.get(unit,{}))
            if 'target_disappears_seconds' in self.options:config.setdefault('target_disappears_seconds',self.options['target_disappears_seconds'])
            child=AttackTimeline({**self.s,'operator':unit,'timing':config,
                '_relic_rules':[r for r in self.s.get('_relic_rules',[]) if r['kind']!='deployment_attack_speed']},normal=True,offset=self.offset/FPS,target_scope=self.target_scope)
            stream=child.attacks(seconds,interval,speed,attribute_speed=attribute_speed,limit=limit,delay=delay,start_delay=start_delay)
            self.streams.extend(child.streams)
            return stream
        duration=finite(seconds,'窗口秒数',3600)
        ready=finite(start_delay,'起始延迟秒数',3600)
        deployment_speed=[r for r in self.s.get('_relic_rules',[]) if r['kind']=='deployment_attack_speed']
        if self.mode=='continuous':
            if deployment_speed:
                times=[];starts=[];steps=[];now=ready
                while now<duration and (limit is None or len(times)<limit):
                    age=(self.offset+self.deployment_offset)/FPS+now
                    bonus=sum(r['value'] for r in deployment_speed if age<r['duration'])
                    current=effective_attack_speed(attribute_speed+bonus);step=interval*speed/current
                    if now+step>duration+1e-9:break
                    starts.append(now);steps.append(step);now+=step;times.append(now)
            else:
                count=max(0,math.floor((duration-ready)/interval+1e-9))
                if limit is not None:count=min(count,limit)
                times=[ready+(i+1)*interval for i in range(count)]
                starts=[t-interval for t in times];steps=[interval]*len(times)
            if self.target_scope=='enemy' and (self.options.get('target_disappears_seconds')==0 or (self.options.get('target_windows')==[] and self.s['operator']!='char_4182_oblvns')):
                times=[];starts=[];steps=[]
            stream={'start_frames':([frame_time(t) for t in starts] if deployment_speed else
                [cadence(t)-cadence(interval) for t in times]),
                'release_frames':[cadence(t) for t in times],'impact_frames':[cadence(t) for t in times],
                'times_seconds':times,'interval_frames':cadence(interval),'interval_seconds':interval,
                'known_animation':False,'resume_frame':frame_time(duration),'unit':unit or self.s['operator'],
                'target_scope':self.target_scope}
            if self.target_scope=='enemy' and (self.options.get('target_disappears_seconds')==0 or (self.options.get('target_windows')==[] and self.s['operator']!='char_4182_oblvns')):stream['resume_frame']=0
            if deployment_speed:
                stream.update(temporary_attack_speed=True,interval_frames_by_attack=[cadence(s) for s in steps],
                    deployment_origin_seconds=(self.offset+self.deployment_offset)/FPS)
                self.streams.append(stream)
            return stream
        data,exact=self.descriptor(unit)
        # Per-scenario overrides are explicitly a preview, never account cultivation.
        raw_windup=self.options.get('windup_frames',data.get('windup_frames')) if unit is None else data.get('windup_frames')
        raw_recovery=self.options.get('recovery_frames',data.get('recovery_frames')) if unit is None else data.get('recovery_frames')
        step=cadence(interval)
        known=raw_windup is not None
        if known:
            anim=data.get('animation_frames',finite(raw_windup,'前摇帧')+finite(raw_recovery or 0,'后摇帧'))
            # Compress a conventional animation only when cadence is shorter than it.
            scale=max(.1,min(1,step/anim)) if anim else 1
            windup=math.ceil(finite(raw_windup,'前摇帧')*scale-1e-9)
            recovery=max(0,math.ceil(anim*scale-1e-9)-windup)
            if 'windup_frames' in self.options and unit is None:windup=math.ceil(finite(raw_windup,'情景前摇帧'))
            if 'recovery_frames' in self.options and unit is None:recovery=math.ceil(finite(raw_recovery,'情景后摇帧'))
            step=max(step,windup+recovery)
        else:
            # Retain a conservative late first release, not an invented zero windup.
            windup=step;recovery=0
        begin=finite(self.options.get('start_delay_frames',0),'起始延迟帧') if unit is None else 0
        if not self.normal:begin+=data.get('begin_frames',0)
        begin+=frame_time(start_delay)
        begin=max(begin,self.options.get('_resume_frames',0))
        if self.normal:begin=max(begin,math.ceil(finite(self.options.get('post_skill_lock_frames',0),'技能结束硬直帧')))
        travel=frame_time(self.options.get('projectile_travel_seconds',delay)) if unit is None else frame_time(delay)
        fixed_impact=None
        if not self.normal:
            fixed_impact=impact_delays().get(self.s['operator'],{}).get(str(self.s['skill']))
            if fixed_impact:
                travel+=frame_time(fixed_impact['seconds'])
                note=(fixed_impact['name']+'本体弹道按资料固定延迟'+str(fixed_impact['seconds'])+
                    '秒落地，另加指定的额外弹道时间；只估算留在伤害范围内的单个目标。来源：'+fixed_impact['source_url'])
                if note not in self.notes:self.notes.append(note)
        end=self.offset+frame_time(duration)
        starts=[];releases=[];impacts=[];emitted=[];steps=[];now=self.offset+math.ceil(begin);attempts=0
        permanent=self.s['operator']=='char_4182_oblvns'
        emitted_releases=[];impact_releases=[]
        temporary=[r for r in self.s.get('_relic_rules',[]) if r['kind']=='temporary_ammo_speed'] if not self.normal else []
        base_interval=interval
        while now<end and (limit is None or len(releases)<limit):
            attempts+=1
            if attempts>250000:raise ValueError('时序事件过多。')
            if (not permanent and not self.selectable(now)) or self.unavailable(now):now+=1;continue
            if ramp or temporary or deployment_speed:
                earned=sum(t<=now for t in impacts) if ramp else 0
                bonus=sum(r['value'] for r in temporary if now-self.offset<frame_time(r['duration']))
                bonus+=sum(r['value'] for r in deployment_speed if now+self.deployment_offset<frame_time(r['duration']))
                current=effective_attack_speed(attribute_speed+bonus+(min(earned*ramp[0],ramp[1]) if ramp else 0))
                step=cadence(base_interval*speed/current)
                if known:
                    scale=max(.1,min(1,step/anim)) if anim else 1
                    windup=math.ceil(finite(raw_windup,'前摇帧')*scale-1e-9)
                    recovery=max(0,math.ceil(anim*scale-1e-9)-windup)
                    if 'windup_frames' in self.options:windup=math.ceil(finite(raw_windup,'情景前摇帧'))
                    if 'recovery_frames' in self.options:recovery=math.ceil(finite(raw_recovery,'情景后摇帧'))
                    step=max(step,windup+recovery)
                else:windup=step
            release=now+windup
            cut=next((a for a,b in self.blocked if now<a<=release),None)
            if cut is not None:
                # Movement/disable interrupts windup; reacquire after it ends.
                now=next(b for a,b in self.blocked if a==cut);continue
            if release>=end:break
            starts.append(now);releases.append(release);steps.append(step)
            impact=release+travel
            if self.selectable_lifetime(impact) and (not permanent or self.selectable(release)):
                emitted.append(impact)
                emitted_releases.append(release)
                if impact<end:impacts.append(impact);impact_releases.append(release)
            now+=step
        stream={'unit':unit or self.s['operator'],'target_scope':self.target_scope,'known_animation':known,'exact_binding':False,'reference_binding':exact,
            'animation':data.get('animation'),'windup_frames':windup if known else None,
            'recovery_frames':recovery if known else None,'interval_frames':step,'interval_seconds':step/FPS,
            'start_frames':[x-self.offset for x in starts],'release_frames':[x-self.offset for x in releases],
            'impact_frames':[x-self.offset for x in impacts], 'times_seconds':[(x-self.offset)/FPS for x in impacts],
            'emitted_impact_frames':[x-self.offset for x in emitted],
            'emitted_times_seconds':[(x-self.offset)/FPS for x in emitted],
            'emitted_release_frames':[x-self.offset for x in emitted_releases],
            'hit_release_frames':[x-self.offset for x in impact_releases],
            'interval_frames_by_attack':steps,
            'temporary_attack_speed':bool(temporary or deployment_speed),
            'attack_speed_sample':'攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准',
            'resume_frame':max(0,(starts[-1]+step-end)) if starts else 0,
            'source':data.get('source','未确认；保留延迟首击情景')}
        if data.get('reference_id'):
            stream['original_animation_reference']={k:data[k] for k in (
                'reference_id','reference_label','original_orientation','skin','source_sha256','runtime_binding_verified')}
            stream['original_animation_reference']['overridden_by_preview']=any(
                key in self.options for key in ('windup_frames','recovery_frames'))
        if fixed_impact:
            stream.update(fixed_impact_delay_frames=frame_time(fixed_impact['seconds']),
                fixed_impact_delay_seconds=fixed_impact['seconds'],
                fixed_impact_delay_source=fixed_impact['source_url'])
        if deployment_speed:stream['deployment_origin_seconds']=(self.offset+self.deployment_offset)/FPS
        self.streams.append(stream)
        return stream

    def selectable_lifetime(self,frame):
        # Leaving range alone does not destroy a previously locked projectile.
        if self.target_scope=='friendly' and self.options.get('target_disappears_seconds')==0:return True
        ends=self.options.get('target_disappears_seconds')
        return ends is None or frame<frame_time(ends)

    def output(self):
        return {'mode':self.mode,'fps':FPS,'streams':self.streams,
            'window_convention':'[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消',
            'scenario_provided':bool({k:v for k,v in self.options.items() if not k.startswith('_')}),
            'target_scope_notes':list(self.target_scope_notes),
            'complete':False,
            'notes':['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。',
                '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。',*self.notes]}


def phase_totals(components,boundary):
    """Clip placed impacts; retain and separately disclose unplaced estimates."""
    damage=healing=0
    for c in components:
        times=c.get('times_seconds')
        amount=c['total']
        if times is not None:
            if 'event_amounts' in c:
                amount=sum(value for t,value in zip(times,c['event_amounts'],strict=True) if 0<=t<boundary)
            else:amount=amount*sum(0<=t<boundary for t in times)/len(times) if times else 0
        if c.get('damage_type')=='healing':healing+=amount
        elif c.get('damage_type') not in ('regeneration','buildup'):damage+=amount
    return damage,healing


def annotate_result(scenario,result):
    timing=result.setdefault('timing',AttackTimeline(scenario).output())
    if timing['mode']=='continuous':
        result['estimate']['notes'].extend(timing.get('target_scope_notes',[]))
        return
    timing['unplaced_components']=[c['name'] for c in result.get('components',[]) if c.get('hits') and 'times_seconds' not in c]
    skill=result['estimate']['skill']
    timing['resource_and_damage_shared_clock']=not timing.get('phase_clock_unbound',False)
    timing['initial_seconds']=skill['initial_seconds'];timing['cycle_seconds']=skill['cycle_seconds']
    if 'assumptions' in result:
        result['assumptions']=[n for n in result['assumptions'] if '未模拟首击、前后摇、帧取整及空转' not in n]
        result['assumptions'].append('使用30Hz参考事件模型，实际攻击模板绑定和未排程特殊分项仍需校准。')
    notes=result['estimate']['notes']
    notes.extend(timing.get('notes',[]))
    notes[:]=[n for n in notes if '未模拟首击、前后摇、帧取整、移动和空转' not in n and '未模拟首击前后摇、帧取整及移动' not in n]
    notes.extend(['时序采用30Hz参考事件模型：首击、攻击间隔帧对齐、供靶区间、移动/打断和指定弹道延迟参与已接入的攻击路径。',
        '动画帧为提取资料；攻击模板绑定、皮肤、多段/持续判定、部分施放/结束硬直尚未逐项校准，不是完整实战模拟。',
        '未提供战斗时序情景时使用连续供靶；当前尚不能从战斗画面自动跟踪移动路径、目标消失和弹体位置。',
        '攻击回复以出手事件计入技力、下一模拟帧可用；强化下次攻击还等待下一攻击槽。该先后顺序需对应客户端校准。'])
    notes.append('单次总量按本次施放归属计算；技能阶段、观察窗口及本轮周期只统计其结束前的已排程命中。跨上轮遗留弹体的稳态周期尚未接入。')
    if any(not s['known_animation'] for s in timing['streams']):
        notes.append('当前存在缺失的前后摇资料：保持延迟首击参考，不伪造零前摇；时序值需实测校准。')
    if timing['unplaced_components']:notes.append('尚未统一排入时间轴的输出分项：'+'、'.join(dict.fromkeys(timing['unplaced_components']))+'。')
    result['estimate']['complete']=False
