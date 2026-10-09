"""Explicit operator models over pinned game data; deterministic single-target estimates.

Each emitted hit is mitigated separately. Conditional events are scenario inputs,
never inferred from a character's name or from another operator's controls.
"""
import math
from .condition_inputs import read_continuous_attacks
from .attribute_limits import effective_attack_speed
from .catalog import catalog
from .enemy_environment import damage_factor
from .timing import AttackTimeline,charge_seconds,mixed_charge_seconds,frame_time,FPS,finite,has_periodic_sp,periodic_charge_seconds


def selected_talents(profile, scenario):
    elite=scenario.get('elite',2)
    level=scenario.get('level') or profile['phases'][elite]['max_level']
    potential=scenario.get('potential',1)-1
    def eligible(candidate):
        condition=candidate.get('unlockCondition')
        phase=int(condition['phase'][-1]) if condition else candidate['phase']
        minimum=condition['level'] if condition else candidate['level']
        rank=candidate.get('requiredPotentialRank',candidate.get('potential_rank',0))
        return phase<=elite and (phase<elite or minimum<=level) and rank<=potential
    talents={}
    for i,candidates in enumerate(profile['talents']):
        candidates=[t for t in candidates if eligible(t)]
        if candidates:talents[i]=candidates[-1]
    module=next((m for m in profile['modules'] if m['id']==scenario.get('module_id')),None)
    parts=[]
    if module and elite>=module['unlock_elite'] and level>=module['unlock_level']:
        parts=module['levels'][scenario['module_level']-1]['parts']
        from .gnosis_module_reference import selected_reference
        gnosis_reference=selected_reference(profile,module,scenario['module_level'],parts,talents.get(0),eligible)
        if gnosis_reference:
            talents[0]={**talents[0],'reference_only':True,
                'reference_identity':{'talent_index':0,'prefab_key':'1'},
                'gnosis_isw_a_reference':gnosis_reference}
        for part in parts:
            if part.get('isToken'):continue
            candidates=(part.get('addOrOverrideTalentDataBundle') or {}).get('candidates') or []
            grouped={}
            for candidate in candidates:
                index=candidate.get('talentIndex',-1)
                if index>=0 and eligible(candidate):grouped[index]=candidate
            for index,talent in grouped.items():
                if gnosis_reference and index==0:continue
                if (profile['id']=='char_437_mizuki' and module['id']=='uniequip_003_mizuki' and
                        part.get('target')=='TALENT' and index==0 and talent.get('prefabKey')=='10' and
                        talent.get('isHideTalent') is True and talent.get('name') is None and
                        talents.get(index,{}).get('name')=='创伤性癔症' and
                        talents[index]['values'].get('attack@mizuki_t_1.atk_scale')==.5):
                    # Pinned original prefab 1 remains a conditional reference.
                    # Prefab 10's attachment/retention CFG is not available;
                    # keep its distinct fields without merging talent values.
                    talents[index]={**talents[index],'reference_only':True,
                        'reference_identity':{'talent_index':0,'prefab_key':'1'},
                        'unresolved_module_ability':{
                            'target':part['target'],'talent_index':index,
                            'prefab_key':talent['prefabKey'],'res_key':part.get('resKey'),
                            'hidden':True,'name':talent['name'],
                            'blackboard':{b['key']:b['value'] for b in talent['blackboard']},
                            'attachment_verified':False}}
                    continue
                name=talent['name']
                if (profile['id']=='char_437_mizuki' and module['id']=='uniequip_004_mizuki' and
                        part.get('target')=='TALENT_DATA_ONLY' and index==0 and name is None):
                    # Reviewed IS data-only overlay targets the same existing
                    # talent; its null label must not erase that identity.
                    name=talents.get(index,{}).get('name')
                talents[index]={'name':name,'description':talent.get('upgradeDescription'),
                    'values':{b['key']:b['value'] for b in talent['blackboard']}}
    return list(talents.values()),parts


class Combat:
    def __init__(self, scenario, attributes):
        self.s=scenario
        self.p=catalog()['operators'][scenario['operator']]
        self.a=attributes
        self.n=scenario['skill']
        self.skill=self.p['skills'][self.n-1]['levels'][scenario.get('skill_rank',10)-1]
        from .relics import effective_skill
        self.skill=effective_skill(self.skill,scenario)
        self.bb=self.skill['values']
        self.talents,self.module_parts=selected_talents(self.p,scenario)
        self.tv={t['name']:t['values'] for t in self.talents}
        self.gnosis_isw_a_reference=next((t['gnosis_isw_a_reference'] for t in self.talents
            if t.get('gnosis_isw_a_reference')),None)
        self.mizuki_amb_y_reference=next((t for t in self.talents
            if t.get('unresolved_module_ability')),None)
        self.effects=list(scenario.get('effects',[]))
        # Manual stat effects belong to the operator unless their unit scope is explicit.
        from .summons import manual_token_effects
        self.token_effects=manual_token_effects(scenario)
        self.token_effects.extend(scenario.get('_token_relic_effects',[]))
        self.warnings=[];self.notes=[];self.inapplicable=[]
        for rid in scenario.get('relic_ids',[]):
            relic=catalog()['relics'].get(rid)
            if not relic or not relic['supported']:
                self.warnings.append((relic['name'] if relic else rid)+'：效果未覆盖。');continue
            applicable=[e for e in relic['effects'] if
                (not e.get('profession') or self.p['profession'] in e['profession'].split('|')) and
                (not e.get('position') or e['position']==self.p['position'])]
            self.effects.extend(applicable)
            self.token_effects.extend(e for e in relic['effects'] if not e.get('profession') and not e.get('position') and
                (e['kind']=='damage_taken' or '我方单位' in relic['usage']))
            if not applicable:self.inapplicable.append(rid)
        for effect in self.effects:
            if effect['kind'] not in ('attack_pct','hp_pct','defense_pct','resistance_flat','attack_speed','sp_recovery','damage_taken'):
                raise ValueError('加成类型尚未支持。')
            self.value(abs(effect['value']) if effect.get('_verified_rule') and effect['kind'] in ('hp_pct','attack_speed') else effect['value'],'藏品加成')
        self.enemy_def=self.option('enemy_defense',0)
        self.enemy_res=self.option('enemy_resistance',0,maximum=100)
        for field in ('window_seconds','skill_duration_seconds'):
            if field in scenario:scenario[field]=self.option(field,maximum=3600)
        self.base=float(scenario['base_attack'])
        self.value(self.base,'基础攻击')
        self.atk_bonus=self.total('attack_pct');self.as_bonus=self.total('attack_speed')
        self.hp_bonus=self.total('hp_pct');self.def_bonus=self.total('defense_pct')
        self.res_bonus=self.total('resistance_flat')
        self.initial_bonus=0;self.sp_extra=0
        self.shu_periodic_sp_reference=None
        self.redeploy=attributes['redeploy_seconds']
        self.atk_flat=0
        self.apply_self_talents()
        self.base_attack=self.base*(1+self.atk_bonus)+self.atk_flat
        self.base_speed_reference=attributes['attack_speed']+self.as_bonus
        self.base_speed=effective_attack_speed(self.base_speed_reference)
        self.normal_interval=attributes['interval']*100/self.base_speed
        self.stats={'hp':attributes['hp']*(1+self.hp_bonus),'attack':self.base_attack,
            'defense':attributes['defense']*(1+self.def_bonus),
            'resistance':min(100,attributes['resistance']+self.res_bonus),
            'redeploy_seconds':self.redeploy,'attack_speed':self.base_speed,
            'attack_speed_reference':self.base_speed_reference,
            'block_count':attributes['block_count']}

    @staticmethod
    def value(value,label,maximum=None,integer=False):
        value=float(value)
        if not math.isfinite(value) or value<0 or (maximum is not None and value>maximum) or (integer and not value.is_integer()):
            raise ValueError(label+'需要范围内的有限非负'+('整数。' if integer else '数。'))
        return value

    def option(self,key,default=0,maximum=None,integer=False):
        value=self.s.get(key,default)
        # Healing-target validation uses the public capability gate; inactive fields stay ignored.
        if key!='healing_targets' and isinstance(value,bool):
            raise ValueError(key+'需要范围内的有限非负'+('整数。' if integer else '数。'))
        return self.value(value,key,maximum,integer)

    def total(self,kind):return sum(float(e['value']) for e in self.effects if e['kind']==kind)
    def talent(self,name,key,default=0):return self.tv.get(name,{}).get(key,default)
    def effects_for_token(self,token_id):
        from .relic_attributes import is_attribute_rune
        return [e for e in self.token_effects if not is_attribute_rune(e) and
                (not e.get('token_ids') or token_id in e['token_ids'])]

    def token_stats(self,token_id):
        from .summons import token_attributes
        from .relic_attributes import is_attribute_rune
        runes=[e for e in self.token_effects if is_attribute_rune(e) and
               (not e.get('token_ids') or token_id in e['token_ids'])]
        runes += [e for e in self.s.get('_attribute_runes',[]) if
                  e.get('origin')=='run_squad' and e.get('target_scope')=='all_units']
        hp_pct=sum(e['value'] for e in self.effects_for_token(token_id) if e['kind']=='hp_pct')
        return token_attributes(self.p,self.s,token_id,hp_pct,rune_effects=runes)

    def apply_self_talents(self):
        op=self.s['operator']
        if op=='char_133_mm':
            self.atk_bonus+=self.talent('维多利亚探员','atk')
            self.as_bonus+=self.talent('维多利亚探员','attack_speed')
        stat_talents={'char_4228_closur':'极限调度','char_1050_chen3':'形意洞照',
            'char_4182_oblvns':'毋畏遗忘','char_328_cammou':'协调一致','char_1001_amiya2':'青色怒火'}
        if op in stat_talents:
            name=stat_talents[op]
            self.atk_bonus+=self.talent(name,'atk')
            self.as_bonus+=self.talent(name,'attack_speed')
            self.def_bonus+=self.talent(name,'def')
        if op=='char_1037_amiya3':self.hp_bonus+=self.talent('诚挚期许','max_hp')
        if op=='char_1044_hsgma2':
            ratio=self.option('current_hp_ratio',1,maximum=1)
            bb=self.tv.get('鬼之架势',{})
            fraction=min(1,(1-ratio)/(1-bb.get('min_hp_ratio',.3)))
            self.atk_bonus+=bb.get('min_atk',0)*fraction
            self.res_bonus+=bb.get('min_magic_resistance',0)*fraction
        if op=='char_2025_shu':
            if self.s.get('three_professions'):self.hp_bonus+=self.talent('天有四时','max_hp')
            if self.s.get('three_same_profession'):self.as_bonus+=self.talent('天有四时','attack_speed')
            if '天有四时' in self.tv and isinstance(self.s.get('four_sui'),str):
                raise ValueError('four_sui 不接受文本条件；请使用布尔值。')
            if '天有四时' in self.tv:
                for field in ('three_professions','three_same_profession'):
                    if isinstance(self.s.get(field),str):
                        raise ValueError(field+' 不接受文本条件；请使用布尔值。')
            if self.s.get('four_sui'):
                self.atk_bonus+=self.talent('天有四时','atk')
                if self.talent('天有四时','sp')>0:
                    # A discrete talent interval is not a natural SP rate.
                    # The original selector does not establish its first pulse,
                    # owner clock, reset or credit during skill lockout.
                    self.shu_periodic_sp_reference={
                        'interval_seconds_parameter':self.talent('天有四时','interval'),
                        'sp_per_pulse_parameter':self.talent('天有四时','sp'),
                        'attack_bonus_parameter':self.talent('天有四时','atk'),
                        'first_tick_seconds':None,'actual_tick_times_seconds':None,
                        'clock_origin':None,'reset_rule':None,'blocked_credit_rule':None,
                        'native_attachment_verified':False,'clock_verified':False,
                        'events_scheduled':False,
                        'source_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
                        'source_selector':'character_table.char_2025_shu.talents[1].candidates[0]'}
        if op=='char_1048_orchd2':
            self.orchid_redeploy_delta=0
            if '翔虫机动' in self.tv:
                # Reviewed original index3/prefab3 and its same-identity
                # TALENT_DATA_ONLY overrides retain a redeploy parameter.
                self.orchid_redeploy_delta=next((t['values']['respawn_time'] for t in self.talents
                    if 'respawn_time' in t['values']),-15)
                self.redeploy=max(0,self.redeploy+self.orchid_redeploy_delta)
                if self.s.get('near_previous_deployment'):self.atk_bonus+=self.talent('翔虫机动','atk')
        if op=='char_1038_whitw2':self.initial_bonus+=self.talent('叙拉古的荣幸','sp')
        if op=='char_1041_angel2' and self.skill['duration_type']=='AMMO':
            self.atk_bonus+=self.talent('铳弹协约','atk')*self.talent('铳弹协约','mult',2)
        if op=='char_4087_ines':
            self.atk_flat=self.talent('影织','steal_atk')*self.option('stolen_enemy_count',1,maximum=100,integer=True)
        if op=='char_437_mizuki' and self.s.get('enemy_below_half'):
            self.atk_bonus+=self.talent('反移情','atk')
        if op=='char_1046_sbell2':self.def_bonus+=2;self.res_bonus+=20
        if op=='char_4107_vrdant' and self.n==1:
            self.hp_bonus+=self.bb['max_hp'];self.res_bonus+=self.bb['magic_resistance']

    def hit(self,raw,dtype,defense=None,resistance=None,effects=None):
        defense=self.enemy_def if defense is None else max(0,defense)
        resistance=self.enemy_res if resistance is None else max(0,resistance)
        if effects is None:
            penetration=sum(r['value'] for r in self.s.get('_relic_rules',[]) if r['kind']=='defense_penetration')
            defense*=max(0,1-penetration)
        if dtype=='weakness':
            # Choose against the acting unit's effective defense; mitigate only once.
            dtype='physical' if max(raw-defense,raw*.05)>=max(raw*(1-resistance/100),raw*.05) else 'magic'
        if dtype=='physical':damage=max(raw-defense,raw*.05)
        elif dtype=='magic':damage=max(raw*(1-resistance/100),raw*.05)
        elif dtype=='true':damage=raw
        elif dtype=='elemental':damage=raw*(1-self.option('enemy_elemental_resistance',0,maximum=100)/100)
        else:raise ValueError('未知伤害类型。')
        return damage*(1+sum(float(e['value']) for e in (self.effects if effects is None else effects) if e['kind']=='damage_taken' and e.get('damage_type')==dtype))*damage_factor(self.s,dtype)

    def neural(self,events,components,recovery_speed=1):
        threshold=2000 if self.s.get('enemy_is_boss') else 1000
        initial=self.option('initial_neural_buildup',0,maximum=threshold)
        remaining=threshold-initial
        def break_end(time):
            if isinstance(recovery_speed,tuple):
                speed,expires=recovery_speed
                accelerated=max(0,expires-time)
                return time+10/speed if accelerated*speed>=10 else time+accelerated+10-accelerated*speed
            return time+10/recovery_speed
        breaking_until=break_end(0) if self.s.get('enemy_in_neural_break') else -1
        resistance=self.option('enemy_buildup_resistance',0,maximum=100)
        buildup_factor=math.prod(r['value'] for r in self.s.get('_relic_rules',[]) if r['kind']=='buildup_factor')
        burst_times=[]
        for time,amount in sorted(events):
            if time<breaking_until:continue
            remaining-=amount*(1-resistance/100)*buildup_factor
            if remaining<=1e-9:
                burst_times.append(time);remaining=threshold;breaking_until=break_end(time)
        burst_rules=[r for r in self.s.get('_relic_rules',[]) if r['kind']=='neural_burst_scale']
        scale=burst_rules[0]['value'] if len(burst_rules)==1 else 1
        per=self.hit(6000*scale,'elemental')
        if len(burst_rules)==1:
            rule=burst_rules[0]
            self.neural_relic_reference={
                'relic_id':rule['relic_id'],'instant_raw_damage':6000*scale,
                'instant_adjusted_damage':per,'instant_factor':scale,
                'periodic_raw_damage':rule['periodic_raw_damage'],
                'periodic_interval':rule['periodic_interval'],
                'periodic_damage_scheduled':False,
                'preexisting_break_assumed':bool(self.s.get('enemy_in_neural_break')),
            }
        components.append({'name':'神经损伤爆发','damage_type':'elemental','hits':len(burst_times),
                           'per_hit':per,'total':len(burst_times)*per,'times_seconds':burst_times,
                           'source_unit':'environment'})
        return burst_times

    def plan(self,normal=False,window=None):
        bb={} if normal else self.bb
        attack=self.base*(1+self.atk_bonus+bb.get('atk',0))+self.atk_flat
        speed_reference=self.base_speed_reference+bb.get('attack_speed',0)
        speed=effective_attack_speed(speed_reference)
        interval=(self.a['interval']+bb.get('base_attack_time',0))*100/speed
        mode='timed';duration=max(0,self.skill['duration']) if not normal else window
        if not normal and window is not None:duration=min(duration,window)
        if not normal and self.s['operator']=='char_1029_yato2':
            attack+=self.base*self.talent('鬼人强化状态','atk')
        components=[];neural_events=None;neural_secondary_seeds=[];neural_binding_seeds=[];neural_incoming_pending=False;op=self.s['operator'];ammo_rounds=None;mantra_attacks=[];drone_trait_reference=None;aglna_attack_phase_reference=None;unbound_cast_reference=None;external_event_reference=None;chen_phase_reference=None;amiya_phase_reference=None;unbound_source_components=None;haruka_healing_reference=None
        timeline=AttackTimeline(self.s,normal=normal,offset=self.s.get('_timeline_offset_seconds',0) if normal else 0)
        def emit(name,raw,dtype,count,defense=None,resistance=None,effects=None,event_times=None):
            if dtype=='buildup':raw*=math.prod(r['value'] for r in self.s.get('_relic_rules',[]) if r['kind']=='buildup_factor')
            per_hit=raw if dtype in ('healing','regeneration','buildup') else self.hit(raw,dtype,defense,resistance,effects)
            item={'name':name,'damage_type':dtype,'hits':count,'per_hit':per_hit,'total':per_hit*count}
            item['source_unit']='operator' if effects is None else 'token'
            if event_times is not None:item['times_seconds']=event_times
            components.append(item)
        def attack_times(seconds=None,target_scope='enemy'):
            horizon=duration if seconds is None else max(0,seconds)
            if mode=='ammo' and ammo_rounds is not None and (timeline.mode=='frames' or any(
                    r['kind']=='deployment_attack_speed' for r in self.s.get('_relic_rules',[]))):
                horizon=3600 if window is None else window
                stream=timeline.attacks(horizon,interval,speed,attribute_speed=speed_reference,limit=ammo_rounds,target_scope=target_scope)
                return stream.get('emitted_times_seconds',stream['times_seconds']) if window is None else stream['times_seconds']
            if mode=='next_attack' and window is None:horizon+=1/FPS
            stream=timeline.attacks(horizon,interval,speed,attribute_speed=speed_reference,limit=1 if mode=='next_attack' else None,target_scope=target_scope)
            return stream['emitted_times_seconds'] if timeline.mode=='frames' and window is None and not normal else stream['times_seconds']
        def attacks(seconds=None):return len(attack_times(seconds))
        def regular(dtype='physical',scale=1,times=1,seconds=None,name='技能攻击',defense=None,resistance=None,target_scope=None):
            scope=target_scope if target_scope is not None else ('friendly' if dtype=='healing' else 'enemy')
            events=attack_times(seconds,target_scope=scope)
            emit(name,attack*scale,dtype,len(events)*times,defense,resistance,
                event_times=[t for t in events for _ in range(int(times))] if float(times).is_integer() else events)
        def instant(dtype='physical',scale=1,times=1,name='施放伤害'):
            if (window==0 or timeline.options.get('target_disappears_seconds')==0 or timeline.options.get('target_windows')==[] or
                    timeline.mode=='frames' and (not timeline.selectable(0) or timeline.unavailable(0) or not timeline.selectable_lifetime(0))):
                times=0
            emit(name,attack*scale,dtype,times)
            if times==1:components[-1]['instant_event']=True
        def damage_healing(name,ratio):
            # Keep the dependency until ordered damage modifiers have settled.
            # A damage-based heal must use dealt damage, including the first hit.
            from .relic_events import DAMAGE
            sources=[i for i,c in enumerate(components) if c['damage_type'] in DAMAGE]
            emit(name,0,'healing',1)
            components[-1]['damage_healing']={'sources':sources,'ratio':ratio}
        healing_targets=self.option('healing_targets',1,maximum=100,integer=True)
        if op=='char_110_deepcl':
            attack=self.base_attack
            own_events=attack_times()
            emit('本体普攻',attack if normal else self.base_attack,'magic',len(own_events),event_times=own_events)
            token=self.token_stats('token_10001_deepcl_tentac')
            token_effects=self.effects_for_token('token_10001_deepcl_tentac')
            from .summons import token_concurrent_limit
            cap=token_concurrent_limit(self.p,self.s,'token_10001_deepcl_tentac')
            count=self.option('summon_count',1,maximum=cap if cap is not None else
                self.talent('召唤触手','cnt',2),integer=True)
            # Token stats are not the operator's stats, and receive no trust or potential ATK.
            raw=token['attack']*(1+sum(e['value'] for e in token_effects if e['kind']=='attack_pct')+
                (0 if normal or self.n!=1 else bb['atk']))
            token_speed=effective_attack_speed(token['attack_speed']+sum(e['value'] for e in token_effects if e['kind']=='attack_speed'))
            token_stream=timeline.attacks(duration,token['interval']*100/token_speed,token_speed,unit=next(iter(self.p['tokens'])))
            token_events=token_stream['emitted_times_seconds'] if timeline.mode=='frames' and window is None and not normal else token_stream['times_seconds']
            hits=len(token_events)*count
            emit('触手',raw,'physical',hits,effects=token_effects,event_times=[t for t in token_events for _ in range(int(count))])
            if not normal and self.n==1:
                scope=(f'名义技能持续参数 {duration:g} 秒' if window is None else
                    f'观察窗口中 {duration:g} 秒的名义技能覆盖假设')
                self.notes.append(f'触手数量 {count:g}（局外假设）；{scope}下，按基础每只 {bb["hp_recovery_per_sec"]:g} 生命/秒连续覆盖的回复参考 {bb["hp_recovery_per_sec"]*duration*count:g}（未计生命回复效果倍率）；实际触手在场、技能回复覆盖及时钟未核验，实际回复总量未知，生命回复不计直接治疗。')
            self.notes.append('触手不继承本体信赖/潜能及职业加成；已确认的所有我方单位藏品攻击/攻速及敌方易伤单独套用。')
        elif op in ('char_196_sunbr','char_2025_shu','char_298_susuro'):
            if (op=='char_298_susuro' and '微创治疗' in self.tv and
                    isinstance(self.s.get('low_cost_healing_target'),str)):
                raise ValueError('low_cost_healing_target 不接受文本条件；请使用布尔值。')
            recipient_factor=self.talent('微创治疗','heal_scale',1) if (
                op=='char_298_susuro' and self.s.get('low_cost_healing_target')) else 1
            if normal and op=='char_298_susuro':regular('healing',scale=recipient_factor,times=min(1,healing_targets),name='普通治疗')
            elif normal:
                if op=='char_196_sunbr':
                    prob=self.talent('平底锅专精','prob');scale=self.talent('平底锅专精','atk_scale',1)
                    events=attack_times()
                    for name,raw,weight in (('普攻期望',attack,1-prob),('平底锅专精期望',attack*scale,prob)):
                        emit(name,raw,'physical',len(events)*weight,event_times=list(events))
                        components[-1]['event_amounts']=[components[-1]['per_hit']*weight for _ in events]
                else:regular(name='普通攻击')
            elif op=='char_298_susuro':
                regular('healing',scale=recipient_factor,times=min(1,healing_targets))
                if self.n==2:self.notes.append('深度治疗整场最多开启两次；周期指标仅描述尚可再次开启时的一轮。')
            elif self.n==1:
                mode='next_attack';duration=interval if window is None else window
                recipients=min(1,healing_targets) if duration>0 else 0
                emit('治疗替代下次攻击',attack*bb['heal_scale'],'healing',recipients)
                if recipients:components[-1]['actual_total']=None
            elif op=='char_196_sunbr':
                stream=timeline.attacks(duration,interval,speed,attribute_speed=speed_reference,start_delay=bb['disarm'],target_scope='friendly')
                events=stream.get('emitted_times_seconds',stream['times_seconds']) if window is None else stream['times_seconds']
                events=[t for t in events for _ in range(int(min(1,healing_targets)))]
                emit('技能攻击',attack,'healing',len(events),event_times=events)
                self.notes.append('食粮烹制先停止攻击烹饪，再按特殊间隔治疗。')
            elif self.n==2:regular('healing',times=min(2,healing_targets))
            else:
                if isinstance(self.s.get('enemy_on_sown_tile'),str):
                    raise ValueError('enemy_on_sown_tile 不接受文本条件；请使用布尔值。')
                if self.s.get('enemy_on_sown_tile'):
                    attack+=self.base*bb['e_atk'];speed_reference+=bb['e_attack_speed']
                    speed=effective_attack_speed(speed_reference)
                    interval=self.a['interval']*100/speed
                regular(name='本体攻击')
                regular('healing',times=min(1,healing_targets),name='同步治疗')
            if op=='char_2025_shu' and not normal:
                self.notes.append('播种地块生命回复与庇护不混入直接技能治疗；四岁/三职业等条件按所选情景。')
        elif op=='char_4228_closur':
            if not normal and self.n==1:attack=self.base_attack
            if self.s.get('reinforcement_blocks_target'):attack*=1.5
            regular(scale=bb.get('attack@atk_scale',1))
            self.notes.append('仅计可露希尔自身输出；指挥中心攻击为0，援军的独立攻击不相加。援军阻挡目标时才计150%特性。')
        elif op=='char_1050_chen3':
            dtype='weakness' if '形意洞照' in self.tv else 'magic'
            if normal:regular(dtype)
            elif self.n==1:regular(dtype,times=2)
            elif self.n==2:
                count=10+self.option('slash_kills',0,maximum=100,integer=True)
                # Slash counts establish a conditional amount, not a cast-time hit.
                emit('绝影斩击',attack*bb['atk_scale'],dtype,count)
                attack+=self.base*bb['chen3_s2[respawn_buff].atk']
                regular(dtype,name='斩击后的6秒强化')
                strengthened=components[-1]
                chen_phase_reference={
                    'kind':'post_slash_strengthening',
                    'strengthening_duration_parameter_seconds':self.skill['duration'],
                    'attack_bonus_parameter':bb['chen3_s2[respawn_buff].atk'],
                    'strengthened_attack_reference':attack,
                    'isolated_attack_phase_reference':{
                        'phase_seconds':duration,'timing':timeline.output(),
                        'conditional_damage':strengthened['total'],
                        'conditional_hits':strengthened['hits'],
                        'per_hit_damage_reference':strengthened['per_hit']},
                    'actual_slash_end_seconds':None,'actual_strengthening_start_seconds':None,
                    'actual_skill_end_seconds':None,'phase_clock_verified':False}
                unbound_cast_reference={'kind':'chen_slashes',
                    'parameter_rows':[('基础斩击次数参数',10,'次'),
                        ('声明击倒追加斩击次数',count-10,'次'),
                        ('斩击倍率参数',bb['atk_scale'],'倍'),
                        ('斩击后强化持续参数',self.skill['duration'],'秒'),
                        ('斩击后攻击力加成参数',bb['chen3_s2[respawn_buff].atk']*100,'%')],
                    'notes':['斩击次数与孤立强化阶段只列条件来源；实际斩击结束、强化起点和普通攻击冷却交接未绑定。']}
                timeline.streams=[]
                if window is not None:duration=window
                self.notes.append('绝影的10次斩击（声明击倒可追加）与斩击后强化分开保留参考；6秒仅为强化阶段参数，不证明完整技能持续或强化在开启时开始。')
            else:
                hp=self.option('enemy_current_hp',0)
                raw=max(hp*bb['hp_ratio'],attack*bb['projectile_min_atk_scale'])
                emit('天喟剑气',raw,dtype,1)
                from .uncertain_sources import preserve_unplaced_sources
                chen_phase_reference={
                    'kind':'swordwave','declared_current_hp':hp,
                    'hp_ratio_parameter':bb['hp_ratio'],
                    'minimum_attack_scale_parameter':bb['projectile_min_atk_scale'],
                    'body_duration_parameter_seconds':self.skill['duration'],
                    'actual_collision_times_seconds':None,'collision_clock_verified':False,
                    **preserve_unplaced_sources([components[-1]],window=window,
                        target_lifetime=timeline.options.get('target_disappears_seconds'))}
                regular(dtype,bb['attack@atk_scale'],3)
                self.notes.append('剑气仅按声明当前生命与攻击力保底列单次条件参考；开启时释放不证明立即碰撞，独立剑气时钟不套用本体攻击或弹道时间。')
            if timeline.options.get('target_disappears_seconds')==0 and self.n==3:
                # The current target has no life even in continuous mode.
                for c in components:
                    c['hits']=0;c['total']=0
                    if 'times_seconds' in c:c['times_seconds']=[]
                timeline.streams=[]
        elif op in ('char_002_amiya','char_1001_amiya2','char_1037_amiya3'):
            if op=='char_1037_amiya3':
                # The reviewed INC-X data-only bundle replaces this same trait ratio.
                healing_scale=next(b['value'] for b in self.p['trait']['candidates'][0]['blackboard'] if b['key']=='scale')
                if self.s.get('module_id')=='uniequip_002_amiya3':
                    for part in self.module_parts:
                        if (part.get('target')=='TRAIT_DATA_ONLY' and not part.get('isToken') and
                                part.get('validInGameTag') is None and part.get('validInMapTag') is None):
                            candidate=part['overrideTraitDataBundle']['candidates'][0]
                            healing_scale=next(b['value'] for b in candidate['blackboard'] if b['key']=='scale')
            if op=='char_1001_amiya2' and not normal:
                attack+=self.base*self.talent('青色怒火','atk')*(bb.get('talent_scale',2)-1)
            if normal:
                regular('magic')
                if op=='char_1037_amiya3':
                    damage_healing('咒愈师伤害转治疗',healing_scale*min(1,healing_targets))
            elif op=='char_002_amiya':
                regular('true' if self.n==3 else 'magic',bb.get('attack@atk_scale',1),bb.get('attack@times',1))
                if self.n==2:self.notes.append('精神爆发结束后10秒晕眩；仅单一目标情景中八发均命中该目标。')
                if self.n==3:mode='once_deploy'
            elif op=='char_1001_amiya2':
                if self.n==1:regular('magic',times=2)
                else:
                    kills=self.option('amiya_slash_kills',0,maximum=bb['amiya2_s_2[kill].max_stack_cnt'],integer=True)
                    # Immediate target search does not establish ten t=0 hits.
                    emit('绝影前九击',attack*bb['atk_scale'],'magic',bb['times']-1)
                    emit('绝影终击',attack*bb['atk_scale_2'],'true',1)
                    attack+=self.base*bb['amiya2_s_2[kill].atk']*kills
                    regular('true',seconds=self.skill['duration'],name='绝影持续真伤')
                    strengthened=components[-1]
                    amiya_phase_reference={
                        'kind':'tactical_slashes',
                        'nominal_skill_duration_parameter_seconds':self.skill['duration'],
                        'declared_slash_kills':kills,
                        'kill_attack_bonus_parameter':bb['amiya2_s_2[kill].atk'],
                        'kill_stack_cap_parameter':bb['amiya2_s_2[kill].max_stack_cnt'],
                        'strengthened_attack_reference':attack,
                        'isolated_attack_phase_reference':{
                            'phase_seconds':self.skill['duration'],'timing':timeline.output(),
                            'conditional_damage':strengthened['total'],
                            'conditional_hits':strengthened['hits'],
                            'per_hit_damage_reference':strengthened['per_hit']},
                        'actual_slash_end_seconds':None,'actual_strengthening_start_seconds':None,
                        'actual_skill_end_seconds':None,'phase_clock_verified':False}
                    unbound_cast_reference={'kind':'amiya_slashes',
                        'parameter_rows':[('斩击次数参数',bb['times'],'次'),
                            ('前九击法术倍率参数',bb['atk_scale'],'倍'),
                            ('最后一击真实倍率参数',bb['atk_scale_2'],'倍'),
                            ('原表技能持续参数',self.skill['duration'],'秒'),
                            ('声明斩击击倒数量',kills,'个'),
                            ('每层击倒攻击加成参数',bb['amiya2_s_2[kill].atk']*100,'%')],
                        'notes':['立即寻找目标不证明10次斩击均在开启时命中；实际斩击结束、强化起点和完整结束未知。',
                            '声明击倒只沿用后续攻击力条件参考；击倒的先后未知，不倒推重写斩击。']}
                    timeline.streams=[]
                    if window is not None:duration=window
                    mode='once';self.notes.append('绝影整场仅一次；35秒仅为原表技能持续参数，既有孤立攻击参考不证明斩击结束后另有35秒。')
            else:
                if self.n==1:
                    regular('magic')
                    damage_healing('咒愈师伤害转治疗',healing_scale*min(1,healing_targets))
                    # The skill grants this extra heal on each attack; it is
                    # not an independently acquired friendly treatment.
                    regular('healing',bb['heal_scale'],healing_targets,name='哀恸共情范围治疗',target_scope='enemy')
                else:
                    declared_hits=self.option('amiya_hit_targets',1,maximum=100,integer=True)
                    if declared_hits<1:raise ValueError('amiya_hit_targets需要1到100之间的整数。')
                    attack=self.base_attack
                    instant('magic',bb['atk_scale'],name='慈悲愿景开启伤害')
                    attack+=self.base*bb['atk']*min(bb['max_stack_cnt'],declared_hits)
                    regular('true',seconds=self.skill['duration'])
                    strengthened=components[-1]
                    unbound_source_components=[strengthened]
                    damage_healing('咒愈师伤害转治疗',healing_scale*min(1,healing_targets))
                    amiya_phase_reference={
                        'kind':'medical_opening',
                        'nominal_skill_duration_parameter_seconds':self.skill['duration'],
                        'opening_attack_scale_parameter':bb['atk_scale'],
                        'opening_damage_reference':components[0]['total'],
                        'opening_healing_reference':components[0]['total']*healing_scale*min(1,healing_targets),
                        'declared_opening_hit_targets':declared_hits,
                        'hit_attack_bonus_parameter':bb['atk'],
                        'hit_stack_cap_parameter':bb['max_stack_cnt'],
                        'strengthened_attack_reference':attack,
                        'isolated_attack_phase_reference':{
                            'phase_seconds':self.skill['duration'],'timing':timeline.output(),
                            'conditional_damage':strengthened['total'],
                            'conditional_hits':strengthened['hits'],
                            'per_hit_damage_reference':strengthened['per_hit']},
                        'actual_strengthening_start_seconds':None,'actual_skill_end_seconds':None,
                        'opening_buff_healing_order_verified':False,'phase_clock_verified':False}
                    unbound_cast_reference={'kind':'amiya_medical_followup',
                        'parameter_rows':[('开启单次攻击倍率参数',bb['atk_scale'],'倍'),
                            ('原表技能持续参数',self.skill['duration'],'秒'),
                            ('声明开启命中敌人数',amiya_phase_reference['declared_opening_hit_targets'],'个'),
                            ('每层命中攻击加成参数',bb['atk']*100,'%')],
                        'notes':['原描述立刻范围攻击保留既有单次参数来源，显式零观察窗口不产生开启伤害或其派生治疗。',
                            '开启伤害、命中加攻及派生治疗的实际链顺序未知；后续攻击只保留孤立条件参考。']}
                    timeline.streams=[]
                    mode='once'
                # Own regeneration is independent of the hostile target.
                regeneration_seconds=duration if '诚挚期许' in self.tv else 0.0
                emit('诚挚期许本体生命回复',self.stats['hp']*self.talent('诚挚期许','hp_recovery_per_sec_by_max_hp_ratio'),
                     'regeneration',regeneration_seconds)
                if self.n==2:
                    components[-1]['nominal_duration_reference_seconds']=duration
                    if duration>0:components[-1]['actual_total']=None
                    if window is not None:duration=window
                    self.notes.append('32秒仅为原表技能持续参数；本体生命回复分项沿用名义时长参考，不受敌人零生命周期取消，实际总回复随结束时钟保持未知。')
                self.notes.append('阿米娅医疗：直接治疗与最大生命百分比生命回复分项；未凭空补齐其他友方最大生命。')
        elif op=='char_1044_hsgma2':
            if normal:regular()
            elif self.n==1:
                mode='infinite';duration=window if window is not None else 30
                regular('magic')
                emit('恶业苦果反击',attack*bb['atk_scale'],'magic',self.option('incoming_hits',0,maximum=10000,integer=True))
                if timeline.options.get('target_disappears_seconds')==0:
                    counter=components[-1]
                    counter.update(conditional_hits_reference=counter['hits'],
                        conditional_damage_reference=counter['total'],hits=0,total=0)
            elif self.n==2:
                mode='instant';duration=0 if window is None else window
                emit('盾击三连',attack*bb['attack@atk_scale'],'magic',3)
                count=self.option('shield_contact_ticks',1,maximum=1000,integer=True)
                raw=attack*bb['shield_atk_scale']
                emit('环绕盾牌',raw,'magic',count)
                emit('盾牌伤害转治疗',self.hit(raw,'magic')*bb['heal_ratio'],'healing',count)
                unbound_cast_reference={'kind':'shield_contact',
                    'parameter_rows':[('盾击段数参数',3,'段'),('接触判定间隔参数',bb['interval'],'秒'),
                                      ('声明盾牌接触次数',count,'次'),('盾牌伤转治疗比例',bb['heal_ratio']*100,'%')],
                    'notes':['盾击三连与独立盾牌环绕只列条件来源；接触次数不证明投盾、首跳或一圈结束时刻。',
                             '治疗依赖盾牌实际造成的伤害；缺少接触时钟时，实际伤害和对应治疗同时未知。']}
                self.notes.append('环绕盾牌0.5秒为接触判定参数；所选次数只给条件参考，不生成实际接触时刻。')
            else:
                regular('magic',times=2)
                terminal=self.option('last_stand_seconds',0,maximum=bb['before_dead_duration'])
                if terminal:
                    # The declared terminal duration is not a close timestamp.
                    # Even the active-phase hit count depends on when it closes.
                    if components[-1]['hits']:components[-1]['actual_total']=None
                    emit('主动关闭后四连击',attack,'magic',0)
                    if duration>0 and timeline.options.get('target_disappears_seconds')!=0 and timeline.options.get('target_windows')!=[]:
                        components[-1]['actual_total']=None
                    mode='once_deploy'
        elif op=='char_437_mizuki':
            if not normal and self.n==1:
                mode='next_attack';duration=interval if window is None else window
                stream=timeline.attacks(3600 if window is None else window,interval,speed,
                    attribute_speed=speed_reference,limit=1)
                events=stream.get('emitted_times_seconds',stream['times_seconds']) if window is None else stream['times_seconds']
                emit('唤醒物理',attack*bb['atk_scale'],'physical',1 if events else 0)
                if events:components[-1]['actual_total']=None
                emit('唤醒额外法术',attack*self.talent('创伤性癔症','attack@mizuki_t_1.atk_scale')*bb['talent_scale'],'magic',1 if events else 0)
                if events:components[-1]['actual_total']=None
            else:
                regular()
                regular('magic',self.talent('创伤性癔症','attack@mizuki_t_1.atk_scale'),name='创伤性癔症')
            if self.mizuki_amb_y_reference:
                for component in components:
                    if component['name'] in ('唤醒额外法术','创伤性癔症'):
                        component.pop('times_seconds',None)
                        component['timing_reference']='original first-talent conditional reference; module attachment unverified'
                        if component['hits']:component['actual_total']=None
            self.notes.append('单目标为天赋可选目标；多人时天赋优先最低生命值，不将全场人数乘入当前敌人伤害。')
        elif op=='char_206_gnosis':
            status=self.option('cold_state',0,maximum=2,integer=True)
            fragile=(self.talent('坚冰','damage_scale_freeze',1) if status==2 else
                     self.talent('坚冰','damage_scale_cold',1) if status==1 else 1)
            res=max(0,self.enemy_res-(15 if status==2 else 0))
            def frost(raw,count,name,event_times=None):
                per=self.hit(raw,'magic',resistance=res)*fragile
                item={'name':name,'damage_type':'magic','hits':count,'per_hit':per,'total':per*count}
                if event_times is not None:item['times_seconds']=event_times
                components.append(item)
            if normal:
                events=attack_times();frost(attack,len(events),'普通攻击',events)
            elif self.n==1:
                mode='next_attack';duration=interval if window is None else window
                # Two animation events exist, but their S1 binding and relative
                # clock are not verified. Use acquisition only as a source guard.
                stream=timeline.attacks(3600 if window is None else window,interval,speed,
                    attribute_speed=speed_reference,limit=1)
                events=stream.get('emitted_times_seconds',stream['times_seconds']) if window is None else stream['times_seconds']
                frost(attack*bb['atk_scale'],2 if events else 0,'高速思考')
            elif self.n==2:
                mode='instant';duration=0
                available=timeline.options.get('target_disappears_seconds')!=0 and timeline.options.get('target_windows')!=[] and (window is None or window>0) and (timeline.mode!='frames' or (
                    timeline.selectable(0) and not timeline.unavailable(0)))
                frost(attack*bb['atk_scale'],1 if available else 0,'零度爆发')
                if available:components[-1]['instant_event']=True
            else:
                events=attack_times();frost(attack,len(events),'失温症攻击',events)
                if self.s.get('frozen_at_skill_end',True) and (window is None or window>=self.skill['duration']):
                    disappears=timeline.options.get('target_disappears_seconds')
                    # A target absent before the nominal end cannot receive
                    # this conditional terminal source. Equal-frame order is
                    # unresolved; do not turn it into a known zero.
                    alive=disappears is None or frame_time(disappears)>=frame_time(self.skill['duration'])
                    frost(attack*bb['atk_scale'],1 if alive else 0,'失温症终结')
                    components[-1]['terminal_clock_verified']=False
                    components[-1]['nominal_terminal_seconds']=self.skill['duration']
                    if disappears is not None and frame_time(disappears)==frame_time(self.skill['duration']):
                        components[-1]['actual_total']=None
            self.notes.append('寒冷/冻结易伤按所选全程状态估算；不把首击后的寒冷倒推至首击。冻结法抗-15与脆弱分开结算。')
            if self.gnosis_isw_a_reference:
                from .gnosis_module_reference import preserve_plan
                preserve_plan(components,self.gnosis_isw_a_reference,window=window,
                    target_lifetime=timeline.options.get('target_disappears_seconds'),
                    per_tick=self.hit(attack*self.gnosis_isw_a_reference['dot_parameters']['atk_scale'],
                        'magic',resistance=res)*fragile)
        elif op=='char_4087_ines':
            if normal:regular()
            elif self.n==1:
                mode='next_attack';duration=interval if window is None else window
                stream=timeline.attacks(3600 if window is None else window,interval,speed,
                    attribute_speed=speed_reference,limit=1)
                events=stream.get('emitted_times_seconds',stream['times_seconds']) if window is None else stream['times_seconds']
                emit('淬影突袭物理攻击',attack,'physical',len(events),event_times=events)
                emit('淬影突袭持续法术',attack*bb['bleed_atk_scale'],'magic',0)
                if events:components[-1]['actual_total']=None
            elif self.n==2:
                # Each successful attack adds 7 ASPD up to 70, not 70 from the first hit.
                if timeline.mode=='frames':
                    events=timeline.attacks(duration,interval,speed,attribute_speed=speed_reference,
                        ramp=(bb['attack@steal_atk_speed'],bb['attack@steal_atk_speed_max']))['times_seconds']
                    count=len(events)
                else:
                    elapsed=0;count=0;events=None
                    while timeline.options.get('target_disappears_seconds')!=0:
                        current=effective_attack_speed(speed_reference+min(count*bb['attack@steal_atk_speed'],bb['attack@steal_atk_speed_max']))
                        elapsed+=self.a['interval']*100/current
                        if elapsed>duration+1e-9:break
                        count+=1
                emit('暗夜无明递增攻速攻击',attack,'physical',count,event_times=events)
            else:
                mode='deployment'
                if self.s.get('ines_first_deployment',False):
                    duration=0;self.notes.append('伊内丝首次部署仅放置影哨后离场，没有此次技能攻击。')
                else:
                    # The recalled shadow crosses an independent path. The
                    # owner attack windows do not locate that collision.
                    emit('收回影哨',attack*bb['atk_scale'],'physical',1)
                    from .uncertain_sources import preserve_unplaced_sources
                    external_event_reference={**preserve_unplaced_sources([components[-1]],window=window,
                        target_lifetime=timeline.options.get('target_disappears_seconds')),
                        'kind':'ines_shadow_return',
                        'parameter_rows':[('穿过敌人数上限参数',bb['max_target'],'名')],
                        'notes':['收回影哨列单个穿过目标的条件伤害；立刻收回不证明路径碰撞发生在开启当帧。',
                                 '本体供靶/打断窗口不代表影哨路径覆盖；实际路径、碰撞及施放归属未核验，未叠加到完整输出。']}
                    if timeline.options.get('target_disappears_seconds')==0:
                        emit('技能攻击',attack,'physical',0,event_times=[])
                    else:regular()
        elif op=='char_4202_haruka':
            if normal:regular('magic')
            else:
                if self.n==2:
                    repeat=self.s.get('haruka_repeat',False)
                    attack=self.base*(1+self.atk_bonus+(bb['atk'] if repeat else 0))+self.atk_flat
                    if repeat:mode='infinite';duration=window if window is not None else 30
                from .haruka_healing_reference import reference
                haruka_healing_reference=reference(self.p,self.s,self.skill)
                scale=haruka_healing_reference['healing_scale_parameter']
                targets=min(haruka_healing_reference['modeled_target_limit_reference'],healing_targets)
                declared=min(haruka_healing_reference['conditional_target_limit_reference'],healing_targets)
                extra_targets=max(0,declared-targets)
                regular('healing',scale,targets,name='护佑者普通治疗')
                body=components[-1]
                if extra_targets:
                    emit('护佑者额外目标治疗（组合待核验）',attack*scale,'healing',
                        len(body['times_seconds'])//int(targets)*extra_targets)
                bursts=self.option('bubble_bursts',0,maximum=10000,integer=True)
                flower_bursts=bursts if '扶摇花火' in self.tv else 0.0
                emit('扶摇花火',attack*self.talent('扶摇花火','heal_scale'),'healing',flower_bursts)
                if self.n==2:
                    regular('magic',scale*bb['atk_scale_extra'],targets,name='治疗衍生伤害')
                    if extra_targets:
                        count=components[-1]['hits']/targets*extra_targets
                        emit('额外目标治疗衍生伤害（组合待核验）',
                            attack*scale*bb['atk_scale_extra'],'magic',count)
                    emit('浮泡治疗衍生伤害',attack*self.talent('扶摇花火','heal_scale')*bb['atk_scale_extra'],'magic',flower_bursts)
                triggers=0
                if self.n==3:
                    triggers=self.option('levitate_triggers',0,maximum=1000,integer=True)
                    emit('浮泡浮空持续伤害',attack*bb['atk_scale'],'magic',0)
                manual=[c for c in components if c['name'] in ('扶摇花火','浮泡治疗衍生伤害','浮泡浮空持续伤害',
                    '护佑者额外目标治疗（组合待核验）','额外目标治疗衍生伤害（组合待核验）')]
                from .uncertain_sources import preserve_unplaced_sources
                references=[]
                for c in manual:
                    alive=None if c['damage_type']=='healing' else timeline.options.get('target_disappears_seconds')
                    r=preserve_unplaced_sources([c],window=window,target_lifetime=alive)
                    references.extend(r['conditional_components'])
                    if c['name'] in ('护佑者额外目标治疗（组合待核验）','额外目标治疗衍生伤害（组合待核验）'):
                        # The existing body clock only supplies a relative
                        # amount reference; it cannot prove acquisition for an
                        # unverified extra recipient, including blocked owners.
                        if window!=0 and duration>0 and alive!=0:c['actual_total']=None
                    if c['name']=='浮泡浮空持续伤害':
                        references[-1]['hits']=references[-1]['total']=None
                        if triggers>0 and r['source_possible']:c['actual_total']=None
                if timeline.options.get('target_disappears_seconds')==0:
                    for c in components:
                        if c['damage_type'] not in ('healing','regeneration','buildup'):
                            c['hits']=0;c['total']=0
                            if 'times_seconds' in c:c['times_seconds']=[]
                rows=[('声明窗口内浮泡破碎次数',bursts,'次')]
                haruka_healing_reference.update(declared_healing_targets=healing_targets,
                    modeled_healing_targets=targets,conditional_healing_targets=declared,
                    additional_conditional_targets=extra_targets,
                    body_healing_reference_before_recipient_factor={
                        key:body[key] for key in ('per_hit','hits','total')})
                if self.n==3:
                    dot=next(c for c in manual if c['name']=='浮泡浮空持续伤害')
                    rows += [('声明浮空触发次数',triggers,'次'),('浮空持续参数',bb['levitate_duration'],'秒'),
                             ('浮空每跳伤害条件参考',dot['per_hit'],'伤害'),('跳伤间隔参数',bb['interval'],'秒')]
                external_event_reference={'kind':'haruka_bubbles','conditional_components':references,'parameter_rows':rows,
                    'notes':['破裂次数只声明观察窗口内条件来源，未定位破裂/受疗及派生伤害时刻；不自动归完整施放、阶段或周期。',
                             '敌方0秒生命周期不取消独立友方受疗；派生伤害需当前敌人邻接覆盖。浮空持续参数不证明首跳、刷新或实际跳数。']}
                if bursts>0 and '扶摇花火' not in self.tv:
                    external_event_reference['notes'].append('当前培养尚未解锁扶摇花火；浮泡破碎声明保留，但不产生该天赋治疗或二技能中依赖该治疗的派生伤害。')
                self.notes.append('遥的治疗衍生伤害保留邻近目标的条件参考；浮泡破碎/浮空计数不生成实际时钟或每次固定四跳。')
        elif op=='char_1046_sbell2':
            if not normal:
                if self.n==1:
                    mode='instant';duration=0 if window is None else window
                    instant('magic',bb['atk_scale'])
                elif self.n==2:
                    mode='infinite';duration=window if window is not None else 30
                    regular('magic',bb['attack@atk_scale_s2'])
                    coverage=self.option('snow_coverage',1,maximum=1)
                    emit('积雪持续伤害',attack*bb['talent@s2_magic_scale'],'magic',0)
                    if duration>0 and coverage>0 and timeline.options.get('target_disappears_seconds')!=0:
                        components[-1]['actual_total']=None
                    components[-1]['timing_reference']='snow field coverage and first tick unverified'
                else:
                    regular('magic',bb['attack@atk_scale_s3'],resistance=max(0,self.enemy_res-bb['magic_resist_penetrate_fixed']))
            # A declared observation count has no sourced stage/phase identity.
            # Never replay it as another count during the recharge plan.
            entries=0 if normal else self.option('snow_entries',0,maximum=1000,integer=True)
            emit('积雪经过伤害',attack*self.talent('无垠的雪景','talent_magic_scale'),'magic',entries)
            if entries>0:
                from .uncertain_sources import preserve_unplaced_sources
                reference=preserve_unplaced_sources([components[-1]],window=window,
                    target_lifetime=timeline.options.get('target_disappears_seconds'))
                external_event_reference={**reference,'kind':'snow_entries',
                    'parameter_rows':[('声明观察窗口内积雪经过次数',entries,'次'),
                                      ('当前阶段攻击力条件参考',attack,'攻击'),
                                      ('经过伤害倍率参数',self.talent('无垠的雪景','talent_magic_scale'),'倍')],
                    'notes':['经过计数只声明观察窗口内条件来源；实际进入时刻、施放前后归属和经过时攻击快照未知。',
                             '不向充能期复制声明次数；本体攻击范围不证明积雪场地覆盖，当前阶段攻击仅作条件参考。']}
            if window==0 or timeline.options.get('target_disappears_seconds')==0:
                for c in components:
                    c['hits']=0;c['total']=0
                    if 'times_seconds' in c:c['times_seconds']=[]
                    c.pop('instant_event',None)
            self.notes.append('阵法术师充能期不进行普通攻击；积雪经过次数与覆盖比例分别指定，不把减速或冻结当伤害。')
        elif op in ('char_328_cammou','char_1038_whitw2'):
            if not normal and op=='char_1038_whitw2' and self.n==1:
                mode='switch';duration=window if window is not None else 30
            regular('magic',name='本体攻击')
            trait_candidates=(self.p.get('trait') or {}).get('candidates') or []
            base_trait={b['key']:b['value'] for b in trait_candidates[-1]['blackboard']} if trait_candidates else {}
            from .drone_traits import selected_drone_trait
            trait=selected_drone_trait(self.p,self.s,self.module_parts)
            if trait!=base_trait:
                drone_trait_reference={'module_id':self.s.get('module_id'),
                    'module_level':self.s.get('module_level'),'parameters':trait,
                    'independent_clock_verified':False,'live_panel_verified':False}
                self.notes.append('浮游单元暖机参数采用已核对且满足培养门槛的模组直接特性覆盖；实际独立单元时序、重选目标重置和当前热更新仍未核验。')
            lower=trait.get('init_atk_scale',.2);step=trait.get('delta_atk_scale',.15);upper=trait.get('max_atk_scale',1.1)
            drone_count=1+(0 if normal else (1 if op=='char_1038_whitw2' and self.n==1 else bb.get('attack@cnt',0)))
            elapsed=self.option('deployment_elapsed_seconds',0,maximum=3600)
            head_interval=self.talent('头狼','interval',20)
            headwolf=op=='char_1038_whitw2' and '头狼' in self.tv
            starting=self.option('drone_warmup_hits',0,maximum=100,integer=True)
            if op=='char_1038_whitw2' and self.n==3:
                # Special S3 units acquire enemies independently. Neither the
                # unlabeled attack@times nor suppressed owner attempts prove
                # arrival, actual hits, warmup, or their return-phase clock.
                emit('特殊浮游单元条件参考',attack*lower,'magic',0)
                disappears=timeline.options.get('target_disappears_seconds')
                if duration>0 and (disappears is None or disappears>timeline.offset/FPS):
                    components[-1]['actual_total']=None
            else:
                for i,event_time in enumerate(attack_times()):
                    time=elapsed+timeline.offset/FPS+event_time
                    ceiling=upper*(self.talent('头狼','scale',1) if headwolf and time>=head_interval else 1)
                    units=drone_count+(1 if headwolf and time>=3*head_interval else 0)
                    scale=min(ceiling,lower+step*(starting+i))
                    emit('浮游单元',attack*scale,'magic',units,event_times=[event_time]*int(units))
                    components[-1]['timing_reference']='owner_attack_clock; independent drone clock unverified'
            if not normal and op=='char_1038_whitw2' and self.n==3:
                # Aura is around globally pursuing drones. Owner range windows
                # cannot prove its coverage, and a per-second description does
                # not establish the first tick or count at an arbitrary boundary.
                emit('狼群光环（不叠加）',attack*bb['attack@magic_atk_scale'],'magic',0)
                if duration>0 and timeline.options.get('target_disappears_seconds')!=0:
                    components[-1]['actual_total']=None
            if op=='char_1038_whitw2' and self.n==3:
                self.notes.append('特殊浮游单元的到达、独立命中、同目标暖机和返回阶段连续性未知；不解释无语义绑定的attack@times参数，也不从本体事件推进暖机。')
            else:self.notes.append('浮游单元连续命中同一目标逐击增长，不按开局满倍率；每次情景从指定暖机命中数开始。本体与单元共享局外命中时间参考用于阶段截断；实际独立单元时钟未核验，不模拟弹道追踪或重新索敌。')
        elif op=='char_4182_oblvns':
            notes=self.option('note_count',0,maximum=self.talent('颂乐音符','max_cnt',10),integer=True)
            defense=self.enemy_def*(1-notes*self.talent('颂乐音符','def_penetrate_ratio'))
            resistance=self.enemy_res*(1-notes*self.talent('颂乐音符','magic_resist_penetrate_ratio'))
            ranged_scale=.8 if self.s.get('ranged_attack',True) else 1
            if self.s.get('module_id') and not normal and self.tv.get('颂乐音符',{}).get('max_cnt',10)>10:ranged_scale=1
            if normal:regular('physical',ranged_scale,defense=defense)
            elif self.n==1:
                mode='instant';duration=0 if window is None else window
                scales=[bb['atk_scale']]+[bb[f'atk_scale_{i}'] for i in range(2,9)]
                for i,scale in enumerate(scales):emit(f'新月音符{i+1}',attack*scale*ranged_scale,'magic',1,resistance=resistance)
                unbound_cast_reference={'kind':'xiangzi_notes',
                    'parameter_rows':[('音符数量参数',8,'个'),('可充能次数参数',self.skill['max_charges'],'次')],
                    'notes':['八音符倍率是条件来源参考；首个音符、后续间隔、独立碰撞与实际结束未绑定。']}
            elif self.n==2:
                mode='switch';duration=window if window is not None else 30
                organ=self.s.get('organ_mode',False)
                if organ:
                    speed_reference+=bb['attack@attack_speed'];speed=effective_attack_speed(speed_reference)
                    interval=self.a['interval']*100/speed
                else:attack+=self.base*bb['attack@atk']
                regular('magic' if organ else 'physical',ranged_scale,2 if self.s.get('fever') else 1,
                        defense=defense,resistance=resistance)
            else:
                regular('physical',bb['attack@atk_scale']*ranged_scale,2,name='钢琴音符',defense=defense)
                regular('magic',bb['attack@atk_scale']*ranged_scale,2,name='风琴音符',resistance=resistance)
            self.notes.append('祥子按指定音符数计算穿透，范围内持续供靶；Fever只改变有明确二连击描述的技能。音符飞行延迟和实际碰撞丢失未模拟。')
        elif op=='char_1015_aglna2':
            if not normal:
                attack+=self.base*self.talent('天穹间的舞步','atk')
                if self.n==1:mode='deployment'
                if self.n==3:
                    mode='ammo';ammo_rounds=int(bb['attack@trigger_time']);duration=ammo_rounds*interval
                    if window is not None:duration=min(duration,window)
                if self.n==2:
                    nominal_horizon=duration
                    duration=max(0,duration-bb['chant_duration'])
            regular('magic' if not normal and self.n==2 else 'physical',bb.get('attack@atk_scale',1))
            weight=self.option('enemy_weight',3,maximum=100,integer=True)
            # Base declarations stay validated; prepared signed deltas also feed the talent.
            weight+=self.s.get('_relic_enemy_effects',{}).get('weight_delta',0)
            extra=self.talent('飘浮大地之上','atk_scale_hi' if weight<=self.talent('飘浮大地之上','mass_level',3) else 'atk_scale_lo')
            regular('magic',extra,times=1 if '飘浮大地之上' in self.tv else 0,name='飘浮大地之上')
            if not normal and self.n==2:
                # Keep the existing isolated attack-phase parameter reference;
                # its origin is not a proved absolute takeoff clock.
                aglna_attack_phase_reference={'timing':timeline.output(),
                    'conditional_damage':sum(c['total'] for c in components),
                    'attack_phase_seconds':duration}
                for c in components:
                    c.pop('times_seconds',None)
                    c['timing_reference']='isolated attack phase; absolute takeoff binding unverified'
                    if nominal_horizon>0 and timeline.options.get('target_disappears_seconds')!=0 and timeline.options.get('target_windows')!=[]:
                        c['actual_total']=None
                timeline.streams=[]
                duration=nominal_horizon
            self.notes.append('予愿安洁莉娜技能按起飞状态计算；二技能滑翔吟唱阶段不计普通攻击，重量决定额外法术倍率。')
        elif op=='char_1042_phatm2':
            ep=self.talent('形为心役','attack@ep_damage_ratio')
            if not normal and self.n==1:
                from .multi_melee import wine_s1
                mode='next_attack';duration=interval if window is None else window
                stream=wine_s1(timeline,interval,speed,speed_reference,bb['times'],window)
                times=stream['emitted_times_seconds'] if window is None else stream['times_seconds']
                emit('暗夜回声',attack*bb['atk_scale'],'magic',len(times),event_times=times)
                # The target buff callback is verified, but first attachment,
                # blackboard initialization and refresh are not. Preserve the
                # source amount; the finisher masks dependent burst totals.
                events=[(time,attack*ep) for time in times]
                if attack*ep>0 and self.option('enemy_buildup_resistance',0,maximum=100)<100:
                    break_end=10 if self.s.get('enemy_in_neural_break') else 0
                    neural_binding_seeds=[t for t in times if t>=break_end]
            else:
                if not normal and self.n==2:mode='infinite';duration=window if window is not None else 30
                regular('magic')
                events=[(t,attack*ep) for t in components[-1]['times_seconds']]
                if not normal and self.n==2:
                    bait=self.option('bait_triggers',0,maximum=100,integer=True)
                    if bait:
                        # Trigger count alone establishes neither placement ATK
                        # nor retreat time, first tick, refresh or overlap.
                        # In particular 25s is not a documented trigger cadence.
                        self.notes.append('本能的召唤诱饵触发次数不提供部署攻击快照、退场时刻或持续效果首跳；未排程诱饵法伤/损伤，不能按固定25秒间隔生成事件。')
            if not normal:
                incoming=self.option('enemy_attack_count',0,maximum=10000,integer=True)
                # A count contains no attack timestamps. Evenly placing the
                # events can invent a burst or a S3 seed before any real hit.
                neural_incoming_pending=bool(incoming and self.talent('堕梦','value')>0 and
                    self.option('enemy_buildup_resistance',0,maximum=100)<100 and duration>0 and
                    timeline.selectable_lifetime(0))
                if self.n==3:
                    # The original description requires prior neural damage
                    # by this operator during the skill. Interval=1 does not
                    # establish first tick, refresh or post-burst lifecycle.
                    if self.option('enemy_buildup_resistance',0,maximum=100)<100:
                        neural_secondary_seeds=[t for t,amount in events if amount>0 and t<duration]
            total_ep=sum(amount for _,amount in events)
            neural_events=events
            emit('潜在神经损伤积累（不是生命伤害）',total_ep,'buildup',1)
            if not normal and self.n==1:
                components[-1]['name']='未计束缚倍率的损伤基础参考（不是生命伤害）'
                components[-1]['binding_multiplier_applied']=False
            self.neural(events,components,1+(bb.get('talent@ep_break_recover_speed',0) if not normal else 0))
            self.notes.append('神经损伤独立积累：普通/精英阈值1000、领袖2000，爆发造成6000元素伤害；爆发冷却内不继续积累。只计本体和指定诱饵事件，不将全场麻痹/牢笼触发凭空加入。')
        elif op=='char_4204_mantra':
            def mantra_hit(scale,time,name):
                emit(name,attack*scale,'magic',1,event_times=[time])
                component=components[-1]
                component['damage_buildup']={'element':'neural',
                    'ratio':bb.get('ep_damage_ratio',bb.get('attack@ep_damage_ratio',0))}
                if self.n==2:
                    component.update(event_chain=f'mantra_s2:{time}',event_order=0)
                mantra_attacks.append(component)
            if normal:regular('magic')
            elif self.n==1:
                mode='next_attack';duration=interval if window is None else window
                # Full skill means its one actual release, even if windup or
                # reacquisition takes longer than the nominal attack interval.
                horizon=3600-1/FPS if window is None and timeline.mode=='frames' else None
                for time in attack_times(horizon):mantra_hit(bb['atk_scale'],time,'共鸣溃缩')
            elif self.n==2:
                for time in attack_times():mantra_hit(bb['attack@atk_scale'],time,'意识联协主目标')
                self.notes.append('意识联协的跳跃攻击其他敌人，不重复计入当前主目标。')
            else:
                regular('magic')
                overflow=self.option('palsy_overflow_hits',0,maximum=10000,integer=True)
                emit('无言为真溢出跳跃',attack*bb['atk_scale'],'elemental',overflow)
            if not normal:
                triggers=self.option('palsy_triggers',0,maximum=10000,integer=True)
                emit('麻痹触发天赋',attack*self.talent('噤声限域','atk_scale'),'elemental',triggers if '噤声限域' in self.tv else 0.0)
                manual=[c for c in components if c['name'] in ('麻痹触发天赋','无言为真溢出跳跃')]
                from .uncertain_sources import preserve_unplaced_sources
                reference=preserve_unplaced_sources(manual,window=window,
                    target_lifetime=timeline.options.get('target_disappears_seconds'))
                rows=[('声明当前目标麻痹触发次数',triggers,'次')]
                if self.n==3:rows += [('声明当前目标溢出跳跃命中次数',overflow,'次'),
                                    ('溢出跳跃间隔原表参数',bb['interval_projectile_trigger'],'秒')]
                external_event_reference={**reference,'kind':'mantra_events','parameter_rows':rows,
                    'notes':['场上麻痹与溢出次数只保留当前培养/当前技能攻击力下的条件参考；实际发生时技能阶段和快照未知。',
                             '不从层数、总技能时长或间隔参数生成时刻；不自动归属完整施放或周期，不推测10%不消耗层数的独立次数。']}
            if timeline.options.get('target_disappears_seconds')==0:
                for c in components:
                    c['hits']=0;c['total']=0
                    if 'times_seconds' in c:c['times_seconds']=[]
                mantra_attacks=[];timeline.streams=[]
            # Skill 1 has no evidenced same-hit callback order. If the target
            # is already breaking, both damage sources exist before modifiers;
            # the ordinary simultaneous-source guard must remain in force.
            if not normal and self.n==1 and self.s.get('enemy_in_neural_break'):
                for component in mantra_attacks:
                    time=component['times_seconds'][0]
                    if time<10:
                        emit('爆发期间附带元素',attack*bb['element_atk_scale'],'elemental',1,event_times=[time])
            self.notes.append('真言附带神经损伤按实际法术伤害比例积累；麻痹触发/溢出跳跃使用指定次数，不把麻痹层数直接当伤害。')
        elif op=='char_2027_wang':
            if normal:regular()
            else:
                mode='triggered_ammo' if self.n==3 else 'instant';duration=0 if window is None else window
                lines=self.option('connected_stones',1,maximum=3,integer=True)
                factor=1+lines*self.talent('料敌机先','attack@per_atk_scale')
                resistance=max(0,self.enemy_res-lines*self.talent('料敌机先','attack@per_magic_resist_penetrate_fixed'))
                count=self.option('trap_triggers',1,maximum=1000,integer=True)
                if self.n==1:
                    ticks=self.option('trap_dot_ticks',6,maximum=7,integer=True)
                    emit('取势棋子持续伤害',attack*bb['attack@atk_scale']*factor,'magic',count*ticks,resistance=resistance)
                else:emit('棋子触发',attack*bb.get('attack@atk_scale',bb.get('atk_scale'))*factor,'magic',count,resistance=resistance)
                if self.n==3 and window is None:duration=self.s.get('skill_duration_seconds')
                rows=[('主动获得棋子参数',bb['cnt'],'枚'),('声明当前目标棋子触发次数',count,'次')]
                if self.n==1:rows += [('持续伤害时长参数',bb['attack@sluggish'],'秒'),('声明每次触发跳数情景',ticks,'次')]
                if self.n==3:rows += [('弹药数量参数',bb['trigger_time'],'发')]
                unbound_cast_reference={'kind':'wang_traps','parameter_rows':rows,
                    'notes':['主动获得棋子不产生对敌直接伤害，也不证明被动触发；手动触发/跳数只给条件参考，不归入完整主动施放。',
                             '连线与法抗穿透保留已有条件参考；首跳/刷新、棋子部署/进入地块及弹药创建消耗时钟未知，持续参数不扩长观察窗口。']}
                self.notes.append('主动资源获取与被动棋子触发分开；所选触发/跳数不生成实际时钟，弹药耗尽不由攻速推导。')
        elif op=='char_1048_orchd2':
            bottle=self.talent('强击瓶专家','power_attack_scale',1) if self.s.get('power_coating',True) and not normal else 1
            if normal:regular(times=3)
            elif self.n==1:
                mode='instant';duration=0 if window is None else window
                emit('刚射',attack*bb['atk_scale_1']*bottle,'physical',4)
                if self.s.get('double_charge',True):emit('刚连射',attack*bb['atk_scale_2']*bottle,'physical',5)
                unbound_cast_reference={'kind':'orchid_arrows',
                    'parameter_rows':[('首轮箭矢数量参数',4,'支'),
                                      ('追加箭矢数量情景',5 if self.s.get('double_charge',True) else 0,'支'),
                                      ('可充能次数参数',self.skill['max_charges'],'次')],
                    'notes':['四箭及可选五箭保留条件量；额外充能消费、发射/飞行、强击瓶逐箭覆盖和实际结束未绑定。']}
            elif self.n==2:
                duration=self.skill['duration'] if window is None else window
                emit('飞翔瞪射箭矢',attack*bb['attack@atk_scale_loop']*bottle,'physical',12)
                emit('飞翔瞪射落地',attack*bb['attack@atk_scale_end']*bottle,'physical',1)
                unbound_cast_reference={'kind':'orchid_arrows',
                    'parameter_rows':[('三轮箭矢数量参数',12,'支'),
                                      ('名义技能持续参数',self.skill['duration'],'秒'),
                                      ('起飞参数',bb['attack@fly_duration'],'秒'),
                                      ('落地参数',bb['attack@fly_end_duration'],'秒')],
                    'notes':['三轮3/4/5箭和落地只列条件来源；4.2秒与起落参数不证明各箭、落地或结束的实际相位。']}
            else:
                mode='instant';duration=0 if window is None else window
                count=self.option('dragon_arrow_hits',1,maximum=1000,integer=True)
                emit('龙之箭物理',attack*bb['atk_scale']*bottle,'physical',count)
                emit('龙之箭法术',attack*bb['atk_scale_magic']*bottle,'magic',count)
                unbound_cast_reference={'kind':'orchid_arrows',
                    'parameter_rows':[('描述蓄力时长参数',3,'秒'),('原表等待参数',bb['wait_duration'],'秒'),
                                      ('声明龙之箭命中次数',count,'次')],
                    'notes':['先蓄力后射箭有描述依据；3秒与wait_duration参数不证明当前观察时钟上的释放/命中或整箭结束。',
                             '贯穿路径和距离参数不转换为时间，不把指定次数放在开启或3秒时刻。']}
            self.notes.append('强击瓶按本次命中仍在首次50次加成覆盖内估算；龙之箭次数取决于敌人体积与路径，使用指定命中次数。')
        elif op=='char_1041_angel2':
            if normal:regular()
            else:
                mode='ammo';ammo=bb['attack@trigger_time'];cost=5 if self.n==3 else 1
                if self.n==2 and self.s.get('steal_success',True):
                    speed_reference+=bb['steal'];speed=effective_attack_speed(speed_reference)
                    interval=(self.a['interval']+bb['base_attack_time'])*100/speed
                    ammo+=bb['addtional_ammo_each']
                duration=ammo/cost*interval
                from .relic_events import ammunition_rounds
                ammo_rounds=ammunition_rounds(ammo,cost,self.s,minimum_interval=interval*speed/600)
                duration=ammo_rounds*interval
                if window is not None:duration=min(duration,window)
                no_current_target=self.n==3 and timeline.options.get('target_disappears_seconds')==0
                if no_current_target:
                    emit('技能攻击',attack*bb['attack@atk_scale'],'physical',0,event_times=[])
                else:regular(scale=bb['attack@atk_scale'],times=cost)
                consumed=0 if no_current_target else attacks()*cost
                per=self.hit(attack*self.talent('火力电台','aoe_atk_scale'),'physical')
                prob=self.talent('火力电台','prob')
                components.append({'name':'火力电台期望轰炸','damage_type':'physical','hits':consumed*prob,
                    'per_hit':per,'total':per*consumed*prob})
                if self.n==3 and self.s.get('delivery_coordinate',True):
                    emit('投递坐标轰炸',attack*bb['attack@cannon_atk_scale'],'physical',1)
                    from .uncertain_sources import preserve_unplaced_sources
                    external_event_reference={**preserve_unplaced_sources([components[-1]],window=window,
                        target_lifetime=timeline.options.get('target_disappears_seconds')),
                        'kind':'angel_coordinate_bomb',
                        'parameter_rows':[('投递坐标轰炸倍率参数',bb['attack@cannon_atk_scale'],'倍')],
                        'notes':['投递坐标存在时列一次物理溅射的单目标条件伤害；立即对该处轰炸不证明目标覆盖或实际命中帧。',
                                 '本体供靶/打断窗口不定位坐标轰炸；实际覆盖、碰撞及阶段归属未核验，弹药攻击参考单独保留。']}
                emit('火力电台本体生命回复',self.stats['hp']*self.talent('火力电台','hp_ratio'),'regeneration',consumed)
            self.notes.append('火力电台按每发弹药触发期望值分项，不把生命回复与屏障计作直接治疗；其他友方耗弹触发需要独立记录，未默认累加。')
        elif op=='char_1035_wisdel':
            main=self.talent('好礼','attack@main_atk_scale',1)
            probability=self.talent('好礼','attack@prob',0)
            shock_count=2 if self.module_parts and self.s.get('module_id')=='uniequip_002_wisdel' else 1
            scale=1;shock_scale=.5
            if not normal and self.n==1:
                mode='next_attack';duration=interval if window is None else window;shock_count+=2;shock_scale=bb['append_atk_scale']
            elif not normal and self.n==3:
                mode='ammo';scale=bb['attack@atk_scale_3'];probability=bb['attack@prob']
                from .relic_events import ammunition_rounds
                ammo_rounds=ammunition_rounds(int(bb['attack@trigger_time']),1,self.s,minimum_interval=interval*speed/600);duration=ammo_rounds*interval
                if window is not None:duration=min(duration,window)
            if not normal and self.n==1:
                stream=timeline.attacks(3600 if window is None else window,interval,speed,
                    attribute_speed=speed_reference,limit=1)
                events=stream.get('emitted_times_seconds',stream['times_seconds']) if window is None else stream['times_seconds']
            else:events=attack_times()
            count=len(events)
            overload=not normal and self.n==2 and self.s.get('overload',False)
            if overload:count*=4;scale=bb['attack@atk_scale_ol']
            emit('维什戴尔主攻击',attack*scale*main,'physical',count,
                event_times=None if overload or mode=='next_attack' else events)
            if count and (overload or mode=='next_attack'):components[-1]['actual_total']=None
            emit('余震',attack*scale*main*shock_scale,'physical',count*shock_count)
            if count:components[-1]['actual_total']=None
            # The described single-check chance does not prove independent
            # draws, shadow consumption order or an explosion count.
            emit('残影单次爆炸条件参考',attack*self.talent('好礼','attack@bomb_atk_scale'),'physical',0)
            if count and probability:components[-1]['actual_total']=None
            ghosts=self.option('ghost_count',0,maximum=3,integer=True)
            if ghosts:
                token=self.token_stats('token_10035_wisdel_wward')
                token_effects=self.effects_for_token('token_10035_wisdel_wward')
                # Explicit cast count avoids asserting a deterministic random SP regeneration schedule.
                cast_count=self.option('ghost_casts',0,maximum=1000,integer=True)
                if cast_count and window==0:
                    raise ValueError('零长度观察窗口不能声明魂灵施放命中。')
                token_attack=token['attack']*(1+sum(e['value'] for e in token_effects if e['kind']=='attack_pct'))
                emit('魂灵之影施放',token_attack,'magic',0,effects=token_effects)
                if cast_count and duration>0 and timeline.options.get('target_disappears_seconds')!=0:
                    components[-1]['actual_total']=None
            self.notes.append('好礼和余震只列条件参数参考；随机独立性、残影刷新/消耗顺序及次生事件时间未核验，不推算爆炸期望。魂灵之影有随机技力回复，使用指定施放次数，未推定自动频率。')
        elif op=='char_4107_vrdant':
            if not normal and self.n==1:
                mode='passive';duration=window if window is not None else 30
            regular('magic' if not normal and self.n==2 else 'physical')
            self.notes.append('维荻按本体在场计算；切换替身时技能中止，替身生命回复不计直接治疗。')
        elif op=='char_1029_yato2':
            arts=self.talent('双雷剑麒麟','attack@atk_scale_1')
            if normal:
                count=attacks()
                emit('普通斩击',attack,'physical',count)
                emit('双雷剑麒麟',attack*arts,'magic',count)
            elif self.n==1:
                attack_count=attacks()
                # Third attack changes to six hits; the other two attacks have two hits.
                count=(attack_count//3)*10+(attack_count%3)*2
                emit('鬼人化',attack,'physical',count)
                emit('双雷剑麒麟',attack*arts,'magic',count)
                mode='deployment'
            elif self.n==2:
                mode='deployment';duration=0 if window is None else window
                emit('乱舞',attack*bb['atk_scale'],'physical',16)
                emit('强化双雷剑麒麟',attack*arts*bb['talent_scale'],'magic',16)
                unbound_cast_reference={'kind':'yato_deployment',
                    'parameter_rows':[('斩击数量参数',16,'次'),('物理斩击倍率参数',bb['atk_scale'],'倍'),
                                      ('第一天赋运算倍率参数',bb['talent_scale'],'倍')],
                    'notes':['16次斩击与第一天赋保留逐段条件伤害；首伤、段间隔、碰撞与实际结束未绑定。',
                             '部署触发不证明0秒完成；不按攻击速度均分斩击，也不推导技能结束后天赋的绝对起点。']}
            else:
                mode='deployment';duration=0 if window is None else window
                count=self.option('dash_hits',1,maximum=100,integer=True)
                emit('空中回旋乱舞',attack*bb['atk_scale'],'physical',count)
                emit('双雷剑麒麟',attack*arts*bb['atk_scale'],'magic',count)
                unbound_cast_reference={'kind':'yato_deployment',
                    'parameter_rows':[('声明回旋命中次数',count,'次'),('斩击倍率参数',bb['atk_scale'],'倍'),
                                      ('基础突进距离参数',bb['min_dist'],'格'),('最大突进距离参数',bb['max_dist'],'格')],
                    'notes':['突进斩击与第一天赋保留指定次数的条件伤害；实际速度、路径碰撞和结束未绑定。',
                             '距离参数不转换为时间，指定命中次数不证明开启即命中；本体供靶范围不证明独立突进路径覆盖。']}
                self.notes.append('回旋命中次数由敌人体积、碰撞、路径决定，不能按攻击速度推算；当前使用明确指定命中次数。')
        elif op=='char_151_myrtle':
            if normal:regular(name='普攻')
            elif self.n==2:
                emit('治愈之翼',attack*bb['attack@heal_scale'],'healing',math.floor(duration)*min(1,healing_targets))
                self.notes.append('治愈之翼每秒至多治疗一名友方，零受疗目标不产生治疗；敌方供靶区间不代替友方受疗条件。')
        elif op=='char_133_mm':
            if self.n==1 and not normal:
                mode='next_attack';duration=interval if window is None else window;scale=bb['atk_scale']
                # One next attack may acquire its target long after the nominal
                # interval. Keep the user's observation and the full search apart.
                horizon=3600 if window is None else window
                if timeline.options.get('target_disappears_seconds')==0 or timeline.options.get('target_windows')==[]:
                    horizon=0
                # A fully blocked observation is a known absence in either
                # mode; this does not add general continuous acquisition timing.
                blocked_until=0
                for begin,end in timeline.blocked:
                    if begin>blocked_until:break
                    blocked_until=max(blocked_until,end)
                if blocked_until>=frame_time(horizon):horizon=0
                stream=timeline.attacks(horizon,interval,speed,attribute_speed=speed_reference,limit=1)
                events=stream.get('emitted_times_seconds',stream['times_seconds']) if window is None else stream['times_seconds']
                if window is None and not stream['release_frames']:duration=None
            else:scale=1;events=attack_times()
            count=min(1,len(events)) if mode=='next_attack' else len(events)
            per_hit=self.hit(attack*scale,'physical')
            components.append({'name':'普攻' if normal else self.skill['name'],'damage_type':'physical',
                'hits':count,'per_hit':per_hit,'total':count*per_hit,'times_seconds':events[:count]})
        else:raise ValueError('该干员的明确技能模型尚未实现。')
        if timeline.mode=='frames' and mode=='next_attack' and window is None and not (op=='char_1042_phatm2' and self.n==1):
            primary=next((s for s in timeline.streams if s['unit']==op),None)
            if primary and primary['release_frames']:
                duration=(primary['release_frames'][-1]+1)/FPS
                primary['resume_frame']=max(0,primary['start_frames'][-1]+primary['interval_frames']-frame_time(duration))
        if timeline.mode=='frames' and mode=='ammo' and ammo_rounds is not None and window is None:
            primary=next((s for s in timeline.streams if s['unit']==op),None)
            duration=(primary['release_frames'][-1]+1)/FPS if primary and len(primary['release_frames'])>=ammo_rounds else None
        elif timeline.mode=='continuous' and mode=='ammo' and ammo_rounds is not None and window is None and any(
                r['kind']=='deployment_attack_speed' for r in self.s.get('_relic_rules',[])):
            primary=next((s for s in timeline.streams if s['unit']==op),None)
            duration=primary['times_seconds'][-1] if primary and len(primary['times_seconds'])>=ammo_rounds else None
        if unbound_cast_reference is not None:
            from .uncertain_sources import preserve_unplaced_sources
            unbound_cast_reference.update(preserve_unplaced_sources(
                components if unbound_source_components is None else unbound_source_components,window=window,
                target_lifetime=timeline.options.get('target_disappears_seconds')))
            if amiya_phase_reference is not None and unbound_cast_reference['source_possible']:
                # An empty isolated reference does not bind the absolute phase.
                body_name='绝影持续真伤' if amiya_phase_reference['kind']=='tactical_slashes' else '技能攻击'
                next(c for c in components if c['name']==body_name)['actual_total']=None
        from .relic_events import first_damage
        first_extra=first_damage(components,self.s,normal=normal)
        if first_extra is None:
            self.warnings.append('首伤藏品：存在未排程/期望输出分项或同帧多来源，不能证明首次伤害归属；未套用首伤倍率。')
        if op=='char_4204_mantra':
            # Damage-dependent buildup is derived only after sourced damage
            # modifiers settle. It is not an independent attack-ATK effect.
            neural_events=[]
            for component in mantra_attacks:
                ratio=component['damage_buildup']['ratio']
                amounts=component.get('event_amounts',[component['per_hit']]*component['hits'])
                neural_events.extend((time,amount*ratio) for time,amount in
                    zip(component['times_seconds'],amounts,strict=True))
            factor=math.prod(r['value'] for r in self.s.get('_relic_rules',[]) if r['kind']=='buildup_factor')
            amounts=[amount*factor for _,amount in neural_events]
            emit('潜在神经损伤积累（不是生命伤害）',0,'buildup',len(amounts),
                 event_times=[time for time,_ in neural_events])
            components[-1].update(event_amounts=amounts,total=sum(amounts),
                per_hit=sum(amounts)/len(amounts) if amounts else 0)
            bursts=self.neural(neural_events,components)
            if self.n==1 and not normal and bursts:
                warning='共鸣溃缩：同次命中刚触发神经爆发时，附带元素的判断顺序尚未核验；该次附带元素未计入。'
                if warning not in self.warnings:self.warnings.append(warning)
            if self.n==2 and not normal:
                breaks=([0] if self.s.get('enemy_in_neural_break') else [])+bursts
                for component in mantra_attacks:
                    time=component['times_seconds'][0]
                    if any(start<=time<start+10 for start in breaks):
                        # PRTS skill-2 note: arts -> neural buildup -> element.
                        # This child occurs after its parent, so cannot consume
                        # another first-hit bonus or create a fabricated tie.
                        emit('爆发期间附带元素',attack*bb['attack@element_atk_scale'],'elemental',1,event_times=[time])
                        components[-1].update(event_chain=component['event_chain'],event_order=2)
        for c in components:
            dependency=c.get('damage_healing')
            if not dependency:continue
            sources=[components[i] for i in dependency['sources']]
            ratio=dependency['ratio']
            c['total']=sum(source['total'] for source in sources)*ratio
            if ratio>0 and any(source.get('actual_total',0) is None for source in sources):
                c['actual_total']=None
                c['timing_reference']='damage-dependent healing; parent damage clock unverified'
                c['known_healing_sources']=[]
                for source in sources:
                    if source.get('actual_total',0) is None:continue
                    known={key:source[key] for key in ('name','hits','times_seconds','instant_event') if key in source}
                    known.update(damage_type='healing',total=source['total']*ratio,
                        per_hit=source['per_hit']*ratio)
                    if 'event_amounts' in source:known['event_amounts']=[amount*ratio for amount in source['event_amounts']]
                    c['known_healing_sources'].append(known)
            events=[]
            for source in sources:
                times=source.get('times_seconds')
                if times is None and source.get('instant_event'):times=[0]
                if times is None:break
                amounts=source.get('event_amounts',[source['per_hit']]*len(times))
                if len(times)!=len(amounts):break
                events.extend((time,amount*ratio) for time,amount in zip(times,amounts))
            else:
                events.sort(key=lambda event:event[0])
                c['times_seconds']=[time for time,_ in events]
                c['event_amounts']=[amount for _,amount in events]
                c['hits']=len(events)
            c['per_hit']=c['total']/c['hits'] if c['hits'] else 0
        from .amiya_continuous_reference import preserve_plan
        amiya_continuous_reference=preserve_plan(self.s,components,duration)
        return {**({'amiya_continuous_reference':amiya_continuous_reference} if amiya_continuous_reference else {}),
            'attack':attack,'attack_speed':speed,'attack_speed_reference':speed_reference,
            'interval':interval,'duration':duration,'mode':mode,
            'damage':sum(c['total'] for c in components if c['damage_type'] not in ('healing','regeneration','buildup')),
            'healing':sum(c['total'] for c in components if c['damage_type']=='healing'),
            'components':components,'neural_events':neural_events,'drone_trait_reference':drone_trait_reference,
            'neural_secondary_seeds':neural_secondary_seeds,
            'neural_binding_seeds':neural_binding_seeds,
            'neural_incoming_pending':neural_incoming_pending,'aglna_attack_phase_reference':aglna_attack_phase_reference,'unbound_cast_reference':unbound_cast_reference,'external_event_reference':external_event_reference,'haruka_healing_reference':haruka_healing_reference,'chen_phase_reference':chen_phase_reference,'amiya_phase_reference':amiya_phase_reference,'timing':timeline.output()}

    def calculate(self):
        self.ranged_attack_condition_consumed=False
        if self.s['operator']=='char_298_susuro' and self.n==2 and self.option('casts_used',0,maximum=2,integer=True)>=2:
            raise ValueError('深度治疗本场已使用两次，不能再次开启。')
        full=self.plan()
        shown=self.plan(window=self.s['window_seconds']) if 'window_seconds' in self.s else full
        if 'window_seconds' not in self.s and self.s.get('timing_mode','frames')=='frames' and full['duration']:
            shown=self.plan(window=full['duration'])
        sp=self.skill
        from .relics import recharge_requirement
        recharge_cost=recharge_requirement(self.s,sp['sp_cost'])
        rate=self.a['sp_recovery']+self.total('sp_recovery')+self.sp_extra
        initial=sp['initial_sp']+self.initial_bonus
        mixed_recovery=None
        if sp['sp_type']=='INCREASE_WITH_TIME':
            recharge=recharge_cost/rate if rate>0 else None
            first=max(0,sp['sp_cost']-initial)/rate if rate>0 else None
            if self.s['operator']=='char_1048_orchd2' and self.n==1 and self.s.get('double_charge',True):
                recharge=recharge_requirement(self.s,2*sp['sp_cost'])/rate if rate>0 else None
                first=max(0,2*sp['sp_cost']-initial)/rate if rate>0 else None
            if self.s['operator']=='char_002_amiya' and read_continuous_attacks(self.s):
                attack_sp=self.talent('情绪吸收','amiya_t_1[atk].sp')
                def time_to_charge(required,stun=0):
                    if required<=0:return 0
                    if rate<=0 and attack_sp<=0:return None
                    time=stun;charge=rate*stun
                    while charge<required:
                        wait=(required-charge)/rate if rate>0 else math.inf
                        if wait<=self.normal_interval:return time+wait
                        time+=self.normal_interval;charge+=rate*self.normal_interval+attack_sp
                    return time
                first=time_to_charge(max(0,sp['sp_cost']-initial))
                recharge=(max(sp['values'].get('stun',0),recharge_cost/rate) if rate>0 else None) if (
                    self.s.get('timing_mode','frames')=='continuous' and
                    (self.s.get('timing',{}).get('target_disappears_seconds')==0 or
                     full.get('amiya_continuous_reference',{}).get('enemy_source_excluded'))) else time_to_charge(recharge_cost,sp['values'].get('stun',0))
                if self.s.get('timing_mode','frames')=='frames':
                    first=mixed_charge_seconds(self.s,max(0,sp['sp_cost']-initial),rate,attack_sp,self.normal_interval,self.base_speed,attribute_speed=self.base_speed_reference,initial=True)
                    mixed_recovery=(attack_sp,sp['values'].get('stun',0))
                self.notes.append('术师阿米娅自然充能与攻击额外技力按事件共同计算；精神爆发后晕眩期间停止攻击，技力自然回复继续。未额外假设击倒回技力。')
            elif read_continuous_attacks(self.s,active=lambda:any(r['kind']=='attack_sp' for r in self.s.get('_relic_rules',[]))) and any(r['kind']=='attack_sp' for r in self.s.get('_relic_rules',[])):
                first=mixed_charge_seconds(self.s,max(0,sp['sp_cost']-initial),rate,0,self.normal_interval,self.base_speed,attribute_speed=self.base_speed_reference,initial=True)
                mixed_recovery=(0,0)
        elif sp['sp_type']=='INCREASE_WHEN_ATTACK' and (read_continuous_attacks(self.s) or has_periodic_sp(self.s)):
            recharge=charge_seconds(self.s,sp['sp_cost'],sp['sp_increment'],self.normal_interval,self.base_speed,attribute_speed=self.base_speed_reference,wait_next_attack=full['mode']=='next_attack')
            first=charge_seconds(self.s,max(0,sp['sp_cost']-initial),sp['sp_increment'],self.normal_interval,self.base_speed,attribute_speed=self.base_speed_reference,initial=True,wait_next_attack=full['mode']=='next_attack')
        elif sp['sp_type']=='INCREASE_WHEN_TAKEN_DAMAGE':
            incoming=self.option('incoming_attack_interval',0,maximum=3600)
            recharge=math.ceil(recharge_cost/sp['sp_increment'])*incoming if incoming>0 else None
            first=math.ceil(max(0,sp['sp_cost']-initial)/sp['sp_increment'])*incoming if incoming>0 else None
            if has_periodic_sp(self.s):
                recharge=periodic_charge_seconds(self.s,sp['sp_cost'],sp['sp_increment'],self.normal_interval,self.base_speed,attribute_speed=self.base_speed_reference,incoming_interval=incoming)
                first=periodic_charge_seconds(self.s,max(0,sp['sp_cost']-initial),sp['sp_increment'],self.normal_interval,self.base_speed,attribute_speed=self.base_speed_reference,initial=True,incoming_interval=incoming)
        else:recharge=first=None
        mode=full['mode']
        observation_seconds=self.s['window_seconds'] if mode=='ammo' and 'window_seconds' in self.s else shown['duration']
        total_damage=full['damage'];total_healing=full['healing'];duration=full['duration']
        wine_s1_unresolved=self.s['operator']=='char_1042_phatm2' and self.n==1
        gnosis_s1_unresolved=self.s['operator']=='char_206_gnosis' and self.n==1
        wisdel_s1_unresolved=self.s['operator']=='char_1035_wisdel' and self.n==1
        mizuki_s1_unresolved=self.s['operator']=='char_437_mizuki' and self.n==1
        ines_s1_unresolved=self.s['operator']=='char_4087_ines' and self.n==1
        healing_s1_unresolved=self.s['operator'] in ('char_196_sunbr','char_2025_shu') and self.n==1
        aglna_s2_unresolved=self.s['operator']=='char_1015_aglna2' and self.n==2
        manual_close_unresolved=self.s['operator']=='char_1044_hsgma2' and self.n==3 and self.option('last_stand_seconds',0,maximum=self.bb['before_dead_duration'])>0
        if wine_s1_unresolved:
            # The native multihit gap does not establish absolute cast end,
            # SP observation or normal-attack resumption. A resource anchor
            # must not turn into a fabricated complete cycle.
            duration=None;recharge=None
            first=0.0 if initial>=sp['sp_cost'] else None
            self.notes.append('暗夜回声单次两段与观察窗口采用原版动作参考；当前客户端首伤相位、技能结束与解除阻回尚未闭合，持续时间、结束后充能及周期输出保持未知。')
        if gnosis_s1_unresolved:
            duration=None;recharge=None
            first=0.0 if initial>=sp['sp_cost'] else None
            self.notes.append('高速思考两段的实际技能绑定、间隔及结束/阻回相位未核验；不把两段当同刻命中或套用常规攻击结束，完整持续和周期未知。')
        if wisdel_s1_unresolved or mizuki_s1_unresolved:
            duration=None;recharge=None
            first=0.0 if initial>=sp['sp_cost'] else None
            self.notes.append(('定点清算' if wisdel_s1_unresolved else '唤醒')+'实际技能绑定与结束/阻回未核验；不由普通攻击结束推导完整周期。')
        if ines_s1_unresolved:
            duration=None;recharge=None
            first=0.0 if initial>=sp['sp_cost'] else None
            self.notes.append('淬影突袭持续法术首跳、刷新和技能结束/阻回未核验，3秒参数不证明实际跳数或完整周期。')
        if manual_close_unresolved:
            duration=None;recharge=None
            self.notes.append('主动关闭的绝对时刻和转换后攻击相位未知；尾段时长不扩长观察窗口，关闭前后完整输出未知。')
        if aglna_s2_unresolved:
            duration=None;recharge=None
            self.notes.append('2.5秒chant参数仅保留已有孤立攻击阶段参考；实际起飞/循环绑定与结束时钟未知，未将其当作固定到达时间。')
        if healing_s1_unresolved:
            duration=None;recharge=None
            self.notes.append('治疗替代下次攻击只列符合条件的单次友方治疗参考；实际友方获取、判断阈值、结束及多充能链未知，不使用敌方供靶时钟。')
        if full['unbound_cast_reference'] is not None:
            duration=None;recharge=None
            self.notes.append('未绑定实际命中和结束时钟的多段来源只列条件参考，未用瞬时触发分类推导0秒结束或完整充能周期。')
        if mode=='ammo' and duration is None:total_damage=total_healing=None
        if mode in ('deployment','passive'):first=0;recharge=None
        nonrepeat=mode in ('infinite','passive','switch','once','once_deploy','deployment','triggered_ammo')
        if self.s['operator']=='char_298_susuro' and self.n==2 and self.option('casts_used',0,maximum=2,integer=True)>=1:
            nonrepeat=True
        if mode in ('infinite','switch','passive'):
            duration=None;total_damage=total_healing=None
            self.notes.append('没有固定的完整技能持续/总量或可重复回转；显示指定观察窗口的伤害与平均输出，默认窗口30秒。')
        if mode=='triggered_ammo':
            total_damage=total_healing=None
            self.notes.append('完整布子弹药技能总量未知；当前棋子触发数量仅为情景总量。')
        if self.s['operator']=='char_1050_chen3' and self.n==2:
            nonrepeat=True
            self.notes.append('斩击结束与强化阶段的绝对起点未确认，完整持续、结束后充能与完整回转保持未知；孤立强化参考不作为开启后的实际命中时钟。')
        if self.s.get('timing_mode','frames')=='frames':
            if first is not None:first=frame_time(first)/FPS
            if duration is not None:duration=frame_time(duration)/FPS
            lockout=self.value(self.s.get('timing',{}).get('sp_lockout_extra_seconds',0),'额外阻回秒数',maximum=3600)
            if duration is not None and mixed_recovery is not None:
                resume=max((s.get('resume_frame',0) for s in full['timing']['streams']),default=0)
                recharge=mixed_charge_seconds(self.s,sp['sp_cost'],rate,mixed_recovery[0],self.normal_interval,self.base_speed,attribute_speed=self.base_speed_reference,
                    offset=duration,stun=mixed_recovery[1],resume=resume,blocked_seconds=lockout)
            if duration is not None and sp['sp_type']=='INCREASE_WHEN_ATTACK' and (read_continuous_attacks(self.s) or has_periodic_sp(self.s)):
                resume=max((s.get('resume_frame',0) for s in full['timing']['streams']),default=0)
                recharge=charge_seconds(self.s,sp['sp_cost'],sp['sp_increment'],self.normal_interval,self.base_speed,attribute_speed=self.base_speed_reference,
                    offset=duration+lockout,resume=max(0,resume-frame_time(lockout)),wait_next_attack=full['mode']=='next_attack')
            if duration is not None and sp['sp_type']=='INCREASE_WHEN_TAKEN_DAMAGE' and has_periodic_sp(self.s):
                recharge=periodic_charge_seconds(self.s,sp['sp_cost'],sp['sp_increment'],self.normal_interval,self.base_speed,attribute_speed=self.base_speed_reference,
                    offset=duration+lockout,incoming_interval=self.option('incoming_attack_interval',0,maximum=3600))
            if recharge is not None:recharge=frame_time(recharge+(0 if mixed_recovery is not None else lockout))/FPS
            if recharge is not None:recharge=max(recharge,math.ceil(finite(self.s.get('timing',{}).get('post_skill_lock_frames',0),'技能结束硬直帧'))/FPS)
        from .sp_events import has_event_sp,charge as event_charge
        if self.s.get('timing_mode','frames')=='continuous' and duration is not None and any(
                r['kind']=='deployment_attack_speed' or r['kind']=='periodic_sp' and r.get('clock')=='deployment'
                for r in self.s.get('_relic_rules',[])):
            lockout=finite(self.s.get('timing',{}).get('sp_lockout_extra_seconds',0),'额外阻回秒数',3600)
            if mixed_recovery is not None:
                recharge=mixed_charge_seconds(self.s,sp['sp_cost'],rate,mixed_recovery[0],self.normal_interval,
                    self.base_speed,attribute_speed=self.base_speed_reference,offset=duration,stun=mixed_recovery[1],blocked_seconds=lockout)
            elif sp['sp_type']=='INCREASE_WHEN_ATTACK' and (read_continuous_attacks(self.s) or has_periodic_sp(self.s)):
                recharge=charge_seconds(self.s,sp['sp_cost'],sp['sp_increment'],self.normal_interval,self.base_speed,attribute_speed=self.base_speed_reference,
                    offset=duration+lockout,wait_next_attack=full['mode']=='next_attack')
                if recharge is not None:recharge+=lockout
            elif sp['sp_type']=='INCREASE_WHEN_TAKEN_DAMAGE' and has_periodic_sp(self.s):
                recharge=periodic_charge_seconds(self.s,sp['sp_cost'],sp['sp_increment'],self.normal_interval,
                    self.base_speed,attribute_speed=self.base_speed_reference,offset=duration+lockout,incoming_interval=self.option('incoming_attack_interval',0,maximum=3600))
                if recharge is not None:recharge+=lockout
        sp_events={}
        if has_event_sp(self.s) and mode not in ('deployment','passive'):
            cost=sp['sp_cost']*(2 if self.s['operator']=='char_1048_orchd2' and self.n==1 and self.s.get('double_charge',True) else 1)
            attack_sp=self.talent('情绪吸收','amiya_t_1[atk].sp') if self.s['operator']=='char_002_amiya' else 0
            sp_events['initial']=event_charge(self.s,sp,max(0,cost-initial),rate,self.normal_interval,
                self.base_speed,attribute_speed=self.base_speed_reference,initial=True,attack_sp=attack_sp,wait_next_attack=mode=='next_attack')
            first=sp_events['initial']['seconds']
            if not nonrepeat and duration is not None:
                resume=max((s.get('resume_frame',0) for s in full['timing']['streams']),default=0)
                sp_events['cycle']=event_charge(self.s,sp,cost,rate,self.normal_interval,self.base_speed,attribute_speed=self.base_speed_reference,
                    offset=duration,resume=resume,attack_sp=attack_sp,wait_next_attack=mode=='next_attack',
                    stun=sp['values'].get('stun',0) if self.s['operator']=='char_002_amiya' and self.n==2 else 0)
                recharge=sp_events['cycle']['seconds']
            else:recharge=None
        if wine_s1_unresolved or gnosis_s1_unresolved or wisdel_s1_unresolved or mizuki_s1_unresolved or ines_s1_unresolved:
            recharge=None
            first=0.0 if initial>=sp['sp_cost'] else None
        if self.shu_periodic_sp_reference is not None:
            self.shu_periodic_sp_reference['independent_sp_clock_reference']={
                'initial_seconds':first,'recharge_seconds':recharge,
                'excludes_four_sui_periodic_credit':True}
            first=0.0 if initial>=sp['sp_cost'] else None
            recharge=None
        cycle=duration+recharge if not nonrepeat and duration is not None and recharge is not None else None
        self.s['_timeline_offset_seconds']=duration or 0
        from .relic_events import DAMAGE
        self.s['_first_damage_consumed_in_skill']=any(c['total']>0 and c['damage_type'] in DAMAGE and
            c.get('source_unit','operator')=='operator' for c in full['components'])
        resume=max((s.get('resume_frame',0) for s in full['timing']['streams']),default=0)
        self.s['timing']={**self.s.get('timing',{}),'_resume_frames':resume}
        if self.s['operator']=='char_002_amiya' and self.n==2 and self.s.get('timing_mode','frames')=='frames':
            self.s['timing']['interrupt_windows']=[*self.s['timing'].get('interrupt_windows',[]),[duration,duration+sp['values'].get('stun',0)]]
        normal=self.plan(normal=True,window=recharge) if cycle is not None and not (
            sp['sp_type']=='INCREASE_WHEN_ATTACK' and not read_continuous_attacks(self.s)) else None
        if self.s['operator']=='char_4182_oblvns':
            ranged_overridden=self.s.get('module_id') and self.tv.get('颂乐音符',{}).get('max_cnt',10)>10
            self.ranged_attack_condition_consumed=not ranged_overridden or normal is not None
        damage=full['damage']+(normal['damage'] if normal else 0)
        healing=full['healing']+(normal['healing'] if normal else 0)
        from .timing import phase_totals
        phase_damage,phase_healing=phase_totals(full['components'],duration) if duration is not None else (None,None)
        if cycle is not None and self.s.get('timing_mode','frames')=='frames':
            inside_damage,inside_healing=phase_totals(full['components'],cycle)
            damage=inside_damage+(normal['damage'] if normal else 0)
            healing=inside_healing+(normal['healing'] if normal else 0)
        cycle_neural_burst_times=[];cycle_neural_burst_damage=0
        if normal is not None and full['neural_events'] is not None:
            # Damage from isolated phases cannot be added when their EP state is shared.
            events=full['neural_events']+[(duration+t,amount) for t,amount in normal['neural_events']]
            if self.s.get('timing_mode','frames')=='frames':events=[(t,a) for t,a in events if t<cycle]
            bursts=[]
            recovery=(1+self.bb.get('talent@ep_break_recover_speed',0),duration)
            self.neural(events,bursts,recovery)
            cycle_neural_burst_times=[t for c in bursts for t in c.get('times_seconds',[])]
            cycle_neural_burst_damage=sum(c['total'] for c in bursts)
            separate=sum(phase_totals([c],cycle if phase is full else recharge)[0]
                for phase in (full,normal) for c in phase['components'] if c['name']=='神经损伤爆发')
            if self.s.get('timing_mode','frames')!='frames':
                separate=sum(c['total'] for phase in (full,normal) for c in phase['components'] if c['name']=='神经损伤爆发')
            damage=damage-separate+sum(c['total'] for c in bursts)
            self.notes.append('周期神经损伤连续结算技能与充能期，共享已有积累和爆发冷却；不将两个独立爆发算例相加。跨多轮稳态仍需时序校准。')
        inventory=self.s.get('inventory_status')
        unconfirmed=self.s.get('unconfirmed_training',[])
        if unconfirmed:self.notes.insert(0,'尚未从画面确认：'+'、'.join(unconfirmed)+'；当前为已标注的培养预览。')
        if inventory and not inventory.get('complete'):
            self.notes.insert(0,f'本局藏品读取未完整：已确认{inventory.get("recognized",0)}件；沿用本局已确认记录。')
        if self.s.get('module_id'):
            module=next(m for m in self.p['modules'] if m['id']==self.s['module_id'])
            elite=self.s.get('elite',2)
            level=self.s.get('level') or self.p['phases'][elite]['max_level']
            if elite<module['unlock_elite'] or level<module['unlock_level']:
                self.notes.append('所选模组未满足当前精英阶段或等级门槛，本次未计模组基础属性与能力覆盖。')
        if self.module_parts:
            self.notes.append('已计模组基础属性与适用天赋数据覆盖；未建模的新增模组特性/隐藏战斗脚本不自动推断。')
        self.notes.append('单目标持续存活、供靶/满额受疗情景；难度、分队、特训和条件藏品尚未完整套用。')
        complete=not (wine_s1_unresolved or gnosis_s1_unresolved) and not self.warnings and not unconfirmed and not self.module_parts and (not inventory or inventory.get('complete'))
        result={'attack':shown['attack'],'total_damage':shown['damage'],'total_healing':shown['healing'],
            'attack_speed':shown['attack_speed'],'base_attack_speed':self.base_speed,
            'attack_speed_reference':shown['attack_speed_reference'],
            'base_attack_speed_reference':self.base_speed_reference,
            'interval_seconds':shown['interval'],'components':shown['components'],'applied_effects':self.effects,
            'inapplicable_relics':self.inapplicable,'complete':not self.warnings,'warnings':self.warnings,
            'complete_definition':'complete仅表示所选藏品规则支持；不代表完整战斗模拟。',
            'scope':'单个持续命中目标的明确技能情景；多段逐段结算防御。','timing':shown['timing']}
        result['timing']['recharge_streams']=normal['timing']['streams'] if normal else []
        result['estimate']={'base_stats':self.stats,**({'sp_events':sp_events} if sp_events else {}),'skill':{
            'name':sp['name'],'initial_seconds':first,'recharge_seconds':recharge,'cycle_seconds':cycle,
            'duration_seconds':duration,'total_damage':total_damage,'total_healing':total_healing,
            'phase_damage':phase_damage,'phase_healing':phase_healing,
            'cycle_dps':damage/cycle if cycle else None,'cycle_hps':healing/cycle if cycle else None,
            'cycle_damage':damage if cycle else None,'cycle_healing':healing if cycle else None,
            'skill_attack':full['attack'],'skill_attack_speed':full['attack_speed'],
            'skill_attack_speed_reference':full['attack_speed_reference'],
            'sp_recovery_per_second':rate if sp['sp_type']=='INCREASE_WITH_TIME' else None,'mode':mode,
            'hit_counts':{name:sum(c['hits'] for c in full['components'] if c['name']==name)
                for name in sorted({c['name'] for c in full['components']})},
            'window_seconds':observation_seconds,
            'window_healing':shown['healing'],
            'window_dps':shown['damage']/observation_seconds if observation_seconds else None,
            'window_hps':shown['healing']/observation_seconds if observation_seconds else None},
            'training':{'elite':self.s.get('elite',2),'level':self.s.get('level') or self.p['phases'][self.s.get('elite',2)]['max_level'],
                'trust':self.s.get('trust',100),'potential':self.s.get('potential',1),'module_id':self.s.get('module_id'),'module_level':self.s.get('module_level',0)},
            'complete':complete,
            'warnings':self.warnings,'notes':list(dict.fromkeys(self.notes))+['连续供靶、按完整攻击间隔估算；未模拟首击前后摇、帧取整及移动。'],
            'scenario_scope':result['scope']}
        from .mei_module_reference import reference as mei_module_reference
        mei_reference=mei_module_reference(self.p,self.s,self.module_parts)
        if mei_reference is not None:result['mei_airborne_module_reference']=mei_reference
        if full['drone_trait_reference']:
            result['drone_trait_reference']=full['drone_trait_reference']
        if self.s['operator']=='char_206_gnosis' and self.n==3 and self.s.get('frozen_at_skill_end',True):
            cast=next((c for c in full['components'] if c['name']=='失温症终结'),None)
            observed=next((c for c in shown['components'] if c['name']=='失温症终结'),None)
            result['gnosis_terminal_reference']={
                'nominal_skill_end_seconds':self.skill['duration'],
                'terminal_clock_verified':False,'freeze_removal_order_verified':False,
                'conditional_terminal_damage':cast['per_hit'] if cast else None,
                'source_possible':{'cast':bool(cast and cast['hits']),
                    'window':bool(observed and observed['hits'])},
                'same_frame_disappearance_unresolved':bool(cast and 'actual_total' in cast),
            }
            if cast and 'actual_total' in cast:
                result['known_damage_subtotals']={
                    key:(value-cast['total'] if value is not None and key in ('total_damage','phase_damage','cycle_damage') else value)
                    for key,value in result['estimate']['skill'].items()
                    if key in ('total_damage','phase_damage','cycle_damage','cycle_dps')}
                subtotal=result['known_damage_subtotals']
                subtotal['window_damage']=shown['damage']-(observed['total'] if observed else 0)
                subtotal['window_dps']=subtotal['window_damage']/shown['duration'] if shown['duration'] else None
                subtotal['cycle_dps']=subtotal['cycle_damage']/cycle if cycle else None
                for key in ('total_damage','phase_damage','cycle_damage','cycle_dps'):
                    result['estimate']['skill'][key]=None
                if observed and observed['hits']:
                    result['total_damage']=None;result['estimate']['skill']['window_dps']=None
                result['complete']=False;result['estimate']['complete']=False
            result['estimate']['notes'].append('失温症终结按给定技能结束时冻结条件列伤害参考；名义持续参数不证明实际结束当帧、冻结移除顺序或同帧消失顺序。')
        if gnosis_s1_unresolved:
            cast=next(c for c in full['components'] if c['name']=='高速思考')
            observed=next(c for c in shown['components'] if c['name']=='高速思考')
            result['gnosis_s1_reference']={
                'two_hit_damage_reference':cast['per_hit']*2,
                'per_hit_damage_reference':cast['per_hit'],
                'source_possible':{'cast':bool(cast['hits']),'window':bool(observed['hits'])},
                'relative_hit_times_seconds':None,'multi_event_binding_verified':False,
                'source_acquisition_times':{'cast':[t for stream in full['timing']['streams']
                    for t in stream['times_seconds']],
                    'window':[t for stream in shown['timing']['streams'] for t in stream['times_seconds']]},
            }
            if cast['hits']:result['estimate']['skill']['total_damage']=None
            if observed['hits']:
                result['total_damage']=None
                result['estimate']['skill']['window_dps']=None
                observed['actual_total']=None
            result['complete']=False
            result['complete_definition']='高速思考两段只列条件伤害参考；实际两段时间和完整结束/周期未核验。'
        if full['haruka_healing_reference'] is not None:
            result['haruka_healing_reference']={**full['haruka_healing_reference'],
                'window_reference':shown['haruka_healing_reference']}
            result['estimate']['notes'].append('遥的普通治疗人数按已核特性和当前技能参数列满额潜在参考；未证明实际友方获取、模组附着或当前客户端。特性人数与当前技能增加人数分别保留，额外份额仅为组合条件来源。')
        if full['external_event_reference'] is not None:
            result['external_event_reference']={**full['external_event_reference'],
                'window_reference':shown['external_event_reference'],'actual_event_times_seconds':None}
            from .uncertain_sources import mask_pending_damage,mask_pending_healing
            mask_pending_damage(result,full,shown,normal,duration,cycle)
            mask_pending_healing(result,full,shown,normal,duration,cycle)
            result['complete']=False;result['estimate']['complete']=False
        if full['unbound_cast_reference'] is not None:
            result['unbound_cast_reference']={**full['unbound_cast_reference'],
                'window_reference':shown['unbound_cast_reference'],
                'actual_hit_times_seconds':None,'actual_end_seconds':None}
            from .uncertain_sources import mask_pending_damage,mask_pending_healing
            mask_pending_damage(result,full,shown,normal,duration,cycle)
            mask_pending_healing(result,full,shown,normal,duration,cycle)
            result['timing']['phase_clock_unbound']=True
            if full['unbound_cast_reference']['kind']=='wang_traps':
                result['active_resource_reference']={'direct_enemy_damage':0,
                    'granted_stones_parameter':self.bb['cnt'],'passive_event_attribution_verified':False}
                if self.n in (1,2):
                    result['estimate']['skill']['total_damage']=0
                    if 'known_damage_subtotals' in result:result['known_damage_subtotals']['total_damage']=0
            result['complete']=False;result['estimate']['complete']=False
        if full['amiya_phase_reference'] is not None:
            result['amiya_phase_reference']={**full['amiya_phase_reference'],
                'window_reference':shown['amiya_phase_reference']}
            result['complete']=False;result['estimate']['complete']=False
        if full['chen_phase_reference'] is not None:
            result['chen_phase_reference']={**full['chen_phase_reference'],
                'window_reference':shown['chen_phase_reference']}
            if self.n==3:
                from .uncertain_sources import mask_pending_damage
                mask_pending_damage(result,full,shown,normal,duration,cycle)
            result['complete']=False;result['estimate']['complete']=False
        if self.s['operator']=='char_1046_sbell2' and self.n==2:
            snow=next(c for c in full['components'] if c['name']=='积雪持续伤害')
            result['snow_field_reference']={
                'per_tick_damage_reference':snow['per_hit'],'tick_interval_parameter_seconds':1,
                'declared_coverage_fraction':self.option('snow_coverage',1,maximum=1),
                'target_condition_reference':'处于积雪上的地面敌人',
                'actual_coverage_windows_seconds':None,'actual_tick_times_seconds':None,
                'source_possible':{'cast':'actual_total' in snow,
                    'window':any(c['name']=='积雪持续伤害' and 'actual_total' in c for c in shown['components'])},
                'skill_duration_kind':'infinite','post_skill_snow_lifecycle_verified':False,
            }
            from .uncertain_sources import mask_pending_damage
            mask_pending_damage(result,full,shown,normal,duration,cycle)
            result['complete']=False;result['estimate']['complete']=False
            self.notes.append('积雪覆盖比例不证明首跳、实际覆盖区间或技能后雪的生命周期；仅列每秒条件参数，不生成实际跳数。')
        if self.s['operator']=='char_1046_sbell2' and self.n==1:
            # Retain the old zero-duration arithmetic as a parameter reference,
            # not proof of skill end/SP lockout or a complete repeating cycle.
            known=[c for c in full['components'] if 'actual_total' not in c]
            body_cycle=phase_totals(known,cycle)[0]+(normal['damage'] if normal else 0) if cycle is not None else None
            skill=result['estimate']['skill']
            result['sbell_instant_reference']={
                'per_hit_damage_reference':next(c['per_hit'] for c in full['components'] if c['name']=='施放伤害'),
                'attack_scale_parameter':self.bb['atk_scale'],'charge_count_parameter':sp['max_charges'],
                'parameter_clock_reference':{**{k:skill[k] for k in ('initial_seconds','duration_seconds','recharge_seconds','cycle_seconds')},
                    'cycle_damage':body_cycle,'cycle_dps':body_cycle/cycle if cycle else None},
                'actual_skill_end_seconds':None,'skill_lifecycle_binding_verified':False,
                'observation_seconds':shown['duration']}
            for key in ('duration_seconds','recharge_seconds','cycle_seconds','phase_damage','phase_healing',
                        'cycle_damage','cycle_healing','cycle_dps','cycle_hps'):
                skill[key]=None
            if 'known_damage_subtotals' in result:
                for key in ('phase_damage','cycle_damage','cycle_dps'):result['known_damage_subtotals'][key]=None
            result['timing']['phase_clock_unbound']=True
            result['complete']=False;result['estimate']['complete']=False
            result['estimate']['notes'].append('铃音吹雪原描述的立即伤害保留参数来源参考；原有0秒结束/回转算术另存参数参考，不证明实际技能结束、阻回和多充能链。观察窗口保留指定长度，零窗口没有伤害。')
        if healing_s1_unresolved:
            heal=next(c for c in full['components'] if c['name']=='治疗替代下次攻击')
            result['next_attack_healing_reference']={
                'per_heal_reference':heal['per_hit'],'recipient_limit':1,
                'recipient_condition_reference':'附近生命不足一半的友方' if self.s['operator']=='char_2025_shu' else '附近友方',
                'charge_count_parameter':self.bb['ct'],'actual_acquisition_times_seconds':None,
                'source_possible':{'cast':'actual_total' in heal,
                    'window':any('actual_total' in c for c in shown['components'])},
                'skill_end_seconds':None,'multi_charge_chain_verified':False,
            }
            from .uncertain_sources import mask_pending_healing
            mask_pending_healing(result,full,shown,normal,duration,cycle)
            result['complete']=False;result['estimate']['complete']=False
        if aglna_s2_unresolved:
            result['aglna_liftoff_reference']={
                'chant_duration_parameter_seconds':self.bb['chant_duration'],
                'nominal_skill_duration_parameter_seconds':self.skill['duration'],
                'actual_takeoff_seconds':None,'lifecycle_binding_verified':False,
                'cast_attack_phase_reference':full['aglna_attack_phase_reference'],
                'window_attack_phase_reference':shown['aglna_attack_phase_reference'],
            }
            from .uncertain_sources import mask_pending_damage
            mask_pending_damage(result,full,shown,normal,duration,cycle)
            result['timing']['phase_clock_unbound']=True
            result['complete']=False;result['estimate']['complete']=False
        if manual_close_unresolved:
            tail=next(c for c in full['components'] if c['name']=='主动关闭后四连击')
            result['manual_close_reference']={
                'declared_terminal_seconds':self.option('last_stand_seconds',0,maximum=self.bb['before_dead_duration']),
                'terminal_limit_parameter_seconds':self.bb['before_dead_duration'],
                'four_hit_attack_damage_reference':tail['per_hit']*4,
                'active_body_damage_reference':sum(c['total'] for c in full['components'] if c['name']=='技能攻击'),
                'close_seconds':None,'transition_clock_verified':False,
                'terminal_hit_times_seconds':None,
            }
            from .uncertain_sources import mask_pending_damage
            mask_pending_damage(result,full,shown,normal,duration,cycle)
            result['complete']=False;result['estimate']['complete']=False
        if ines_s1_unresolved:
            dot=next(c for c in full['components'] if c['name']=='淬影突袭持续法术')
            result['ines_dot_reference']={
                'per_second_damage_reference':dot['per_hit'],'duration_parameter_seconds':self.bb['bleed_duration'],
                'interval_description_seconds':1,'actual_first_tick_seconds':None,
                'actual_tick_count':None,'refresh_order_verified':False,'dot_stacks':False,
                'source_possible':{'cast':'actual_total' in dot,
                    'window':any('actual_total' in c for c in shown['components'] if c['name']=='淬影突袭持续法术')},
            }
            from .uncertain_sources import mask_pending_damage
            mask_pending_damage(result,full,shown,normal,duration,cycle)
            result['complete']=False;result['estimate']['complete']=False
        if self.s['operator']=='char_133_mm' and self.n==1:
            # Preserve the established ordinary-action/explicit-preview clock as
            # a parameter example before protecting the unverified actual bind.
            skill_result=result['estimate']['skill']
            clock_keys=('initial_seconds','duration_seconds','recharge_seconds','cycle_seconds',
                'total_damage','phase_damage','cycle_damage','cycle_dps','cycle_healing','cycle_hps')
            parameter_clock={key:skill_result[key] for key in clock_keys}
            parameter_clock['recharge_streams']=result['timing']['recharge_streams']
            result['mei_s1_reference']={
                'per_hit_damage_reference':next(c['per_hit'] for c in full['components'] if c['name']==sp['name']),
                'attack_scale_parameter':self.bb['atk_scale'],'sluggish_duration_parameter_seconds':self.bb['sluggish'],
                'source_possible':{'cast':any(c['hits'] for c in full['components']),
                    'window':any(c['hits'] for c in shown['components'])},
                'source_acquisition_times':{'cast':[f/FPS for stream in full['timing']['streams']
                    for f in stream.get('emitted_release_frames',stream['release_frames'])],
                    'window':[f/FPS for stream in shown['timing']['streams']
                    for f in stream.get('emitted_release_frames',stream['release_frames'])]},
                'impact_times_reference':{'cast':[t for c in full['components'] for t in c.get('times_seconds',[])],
                    'window':[t for c in shown['components'] for t in c.get('times_seconds',[])]},
                'parameter_clock_reference':parameter_clock,
                'parameter_clock_binding_verified':False,'skill_binding_verified':False,'actual_cast_end_seconds':None,
            }
            for plan in (full,shown):
                for component in plan['components']:
                    component.pop('times_seconds',None)
                    component['timing_reference']='next attack conditional reference; actual S1 binding unverified'
                    if component['hits']:component['actual_total']=None
            from .uncertain_sources import mask_pending_damage
            mask_pending_damage(result,full,shown,None,None,None)
            for key in ('duration_seconds','phase_damage','phase_healing','recharge_seconds',
                        'cycle_seconds','cycle_damage','cycle_dps','cycle_healing','cycle_hps'):
                skill_result[key]=None
            skill_result['initial_seconds']=0.0 if initial>=sp['sp_cost'] else None
            result['timing']['recharge_streams']=[]
            result['timing']['parameter_clock_only']=True
            result['timing']['phase_clock_unbound']=True
            result['complete']=False;result['estimate']['complete']=False
            result['estimate']['notes'].append('麻痹弹有效出手采用已有常规动作参考；原版Attack_Loop及手动时序的充能算例保留，实际S1动作绑定、结束/阻回与完整周期未知。')
        if mizuki_s1_unresolved:
            result['mizuki_s1_reference']={
                'physical_per_hit_reference':next(c['per_hit'] for c in full['components'] if c['name']=='唤醒物理'),
                'arts_per_hit_reference':next(c['per_hit'] for c in full['components'] if c['name']=='唤醒额外法术'),
                'source_possible':{'cast':any(c['hits'] for c in full['components']),
                    'window':any(c['hits'] for c in shown['components'])},
                'source_acquisition_times':{'cast':[t for stream in full['timing']['streams'] for t in stream['times_seconds']],
                    'window':[t for stream in shown['timing']['streams'] for t in stream['times_seconds']]},
                'skill_binding_verified':False,'actual_cast_end_seconds':None,
            }
            from .uncertain_sources import mask_pending_damage
            mask_pending_damage(result,full,shown,normal,duration,cycle)
            result['complete']=False;result['estimate']['complete']=False
        if full.get('amiya_continuous_reference'):
            from .amiya_continuous_reference import attach_result as attach_amiya_continuous
            attach_amiya_continuous(result,self.s,full,shown,normal,duration,cycle,rate=rate,
                cost=recharge_cost,attack_credit=self.talent('情绪吸收','amiya_t_1[atk].sp'))
        if self.gnosis_isw_a_reference:
            from .gnosis_module_reference import attach_result
            attach_result(result,self.gnosis_isw_a_reference,full,shown,normal,duration,cycle)
        if self.mizuki_amb_y_reference:
            talent=self.mizuki_amb_y_reference
            arts=next(c for c in full['components'] if c['name'] in ('唤醒额外法术','创伤性癔症'))
            result['mizuki_amb_y_reference']={
                'original_first_talent':{'name':talent['name'],**talent['reference_identity'],
                    'blackboard':dict(talent['values']),'reference_only':True,
                    'per_hit_damage_reference':arts['per_hit'],'attachment_verified':False},
                'hidden_module_ability':talent['unresolved_module_ability'],
                'actual_extra_healing':None,'kill_recovery_clock_verified':False,
                'source_possible':{'cast':bool(arts['hits']),
                    'window':any(c['hits'] for c in shown['components']
                        if c['name'] in ('唤醒额外法术','创伤性癔症'))}}
            from .uncertain_sources import mask_pending_damage
            mask_pending_damage(result,full,shown,normal,duration,cycle)
            # No kill-count/kill-clock input or native recovery callback exists.
            # Keep the old modeled healing subtotal, not an actual zero total.
            # A missing current target does not exclude kills elsewhere.
            recovery_possible=lambda plan:bool(plan and plan['duration']>0)
            cast_recovery=recovery_possible(full);window_recovery=recovery_possible(shown)
            cycle_recovery=cycle is not None and (cast_recovery or recovery_possible(normal))
            skill=result['estimate']['skill']
            result['known_healing_subtotals']={key:skill[key] for key in
                ('total_healing','phase_healing','window_healing','cycle_healing','cycle_hps','window_hps')}
            result['mizuki_amb_y_reference']['recovery_source_possible']={
                'cast':cast_recovery,'window':window_recovery,'cycle':bool(cycle_recovery)}
            if cast_recovery:skill['total_healing']=skill['phase_healing']=None
            if window_recovery:
                result['total_healing']=None
                skill['window_healing']=skill['window_hps']=None
            if cycle_recovery:skill['cycle_healing']=skill['cycle_hps']=None
            result['complete']=False;result['estimate']['complete']=False
            result['estimate']['notes'].append('AMB-Y原版第一天赋参数仅保留条件参考；隐藏能力与原天赋的实际附着关系未核验，额外回复不生成治疗事件。')
        if self.s['operator']=='char_1038_whitw2' and self.n==3:
            aura=next(c for c in full['components'] if c['name']=='狼群光环（不叠加）')
            observed=next(c for c in shown['components'] if c['name']=='狼群光环（不叠加）')
            result['drone_lifecycle_reference']={
                'aura_per_tick_damage_reference':aura['per_hit'],
                'aura_interval_description_seconds':1,'aura_first_tick_seconds':None,
                'aura_tick_count':None,'aura_coverage_verified':False,'aura_stacks':False,
                'aura_source_possible':{'cast':'actual_total' in aura,
                    'window':'actual_total' in observed},
                'global_target_search':True,'native_lifecycle_verified':False,
                'unbound_attack_times_parameter':self.bb['attack@times'],
                'arrival_seconds':None,'independent_attack_times_seconds':None,
                'same_target_hit_counter':None,'return_phase_clock_verified':False,
                'drone_initial_per_hit_reference':next(c['per_hit'] for c in full['components'] if c['name']=='特殊浮游单元条件参考'),
                'drone_source_possible':{'cast':any('actual_total' in c for c in full['components'] if c['name']=='特殊浮游单元条件参考'),
                    'window':any('actual_total' in c for c in shown['components'] if c['name']=='特殊浮游单元条件参考')},
            }
            from .uncertain_sources import mask_pending_damage
            mask_pending_damage(result,full,shown,normal,duration,cycle)
            result['estimate']['notes'].append('狼群光环围绕独立追敌单元；每秒伤害描述不证明首跳、覆盖或边界，不以本体供靶区间替代单元位置。')
        if self.s['operator']=='char_1035_wisdel':
            ghosts=self.option('ghost_count',0,maximum=3,integer=True)
            ghost_casts=int(self.option('ghost_casts',0,maximum=1000,integer=True)) if ghosts>0 else 0
            result['wisdel_secondary_reference']={
                'described_single_check_probability':self.bb.get('attack@prob',self.talent('好礼','attack@prob',0)) if self.n==3 else self.talent('好礼','attack@prob',0),
                'explosion_per_hit_reference':next(c['per_hit'] for c in full['components'] if c['name']=='残影单次爆炸条件参考'),
                'explosion_expected_count':None,'random_independence_verified':False,
                'shadow_lifecycle_verified':False,'secondary_hit_times_seconds':None,
                'source_possible':{'cast':any(c['hits'] for c in full['components'] if c['name']=='维什戴尔主攻击'),
                    'window':any(c['hits'] for c in shown['components'] if c['name']=='维什戴尔主攻击')},
                's1_binding_verified':False,
                'ghost_casts_requested':ghost_casts,
                'ghost_per_cast_damage_reference':next((c['per_hit'] for c in full['components'] if c['name']=='魂灵之影施放'),None),
                'ghost_cast_times_seconds':None,'ghost_full_cast_attribution_verified':False,
                'ghost_declared_count_damage_reference':ghost_casts*next((c['per_hit'] for c in full['components'] if c['name']=='魂灵之影施放'),0),
            }
            from .uncertain_sources import mask_pending_damage
            mask_pending_damage(result,full,shown,normal,duration,cycle)
            result['complete_definition']='余震与残影只列条件参数；实际命中时钟、随机独立性和生命周期未核验。'
            if wisdel_s1_unresolved:result['complete']=False;result['estimate']['complete']=False
            from .wisdel_summon_qualification import reference as summon_qualification_reference
            result['wisdel_summon_qualification_reference']=summon_qualification_reference(self.p,self.s)
        if hasattr(self,'neural_relic_reference'):
            result['neural_relic_reference']={**self.neural_relic_reference,
                'cast_burst_times':[t for c in full['components'] if c['name']=='神经损伤爆发' for t in c.get('times_seconds',[])],
                'window_burst_times':[t for c in shown['components'] if c['name']=='神经损伤爆发' for t in c.get('times_seconds',[])],
                'cycle_burst_times':cycle_neural_burst_times}
        if full['neural_incoming_pending'] or shown['neural_incoming_pending']:
            result['neural_incoming_reference']={
                'talent':'堕梦','attacks_requested':int(self.option('enemy_attack_count',0,maximum=10000,integer=True)),
                'buildup_per_attack':self.talent('堕梦','value'),
                'events_scheduled':False,'attack_times_seconds':None,
                'affected_damage_phases':{'cast':full['neural_incoming_pending'],
                    'window':shown['neural_incoming_pending'],
                    'cycle':full['neural_incoming_pending'] and cycle is not None},
                'excluded_burst_damage':{
                    'cast':sum(c['total'] for c in full['components'] if c['name']=='神经损伤爆发'),
                    'phase':phase_totals([c for c in full['components'] if c['name']=='神经损伤爆发'],duration)[0] if duration is not None else 0,
                    'window':sum(c['total'] for c in shown['components'] if c['name']=='神经损伤爆发'),
                    'cycle':cycle_neural_burst_damage}}
        if full['neural_binding_seeds'] or shown['neural_binding_seeds']:
            result['neural_s1_reference']={
                'skill':'暗夜回声',
                'direct_buildup_ratio':self.talent('形为心役','attack@ep_damage_ratio'),
                'direct_buildup_raw':full['attack']*self.talent('形为心役','attack@ep_damage_ratio'),
                'binding_multiplier':self.bb['ep_damage_scale'],
                'binding_duration_seconds':self.bb['unmove'],
                'first_attachment_verified':False,'refresh_order_verified':False,
                'binding_multiplier_applied':False,
                'qualified_hit_times':{'cast':full['neural_binding_seeds'],
                    'window':shown['neural_binding_seeds']},
                'affected_damage_phases':{'cast':bool(full['neural_binding_seeds']),
                    'window':bool(shown['neural_binding_seeds']),'cycle':False},
                'excluded_burst_damage':{
                    'cast':sum(c['total'] for c in full['components'] if c['name']=='神经损伤爆发'),
                    'phase':0,'window':sum(c['total'] for c in shown['components'] if c['name']=='神经损伤爆发'),
                    'cycle':0}}
        if full['neural_secondary_seeds'] or shown['neural_secondary_seeds']:
            cast_bursts=[c for c in full['components'] if c['name']=='神经损伤爆发']
            result['neural_skill_reference']={
                'skill':'空剧场','periodic_buildup_ratio':self.bb['ep_damage_ratio'],
                'periodic_buildup_raw':full['attack']*self.bb['ep_damage_ratio'],
                'periodic_interval':self.bb['interval'],'first_tick_seconds':None,
                'secondary_events_scheduled':False,
                'qualified_seed_times':{'cast':full['neural_secondary_seeds'],'window':shown['neural_secondary_seeds']},
                'affected_damage_phases':{'cast':bool(full['neural_secondary_seeds']),
                    'window':bool(shown['neural_secondary_seeds']),
                    'cycle':bool(full['neural_secondary_seeds']) and cycle is not None},
                # These direct-only bursts cannot be claimed as the real
                # sequence when an unplaced secondary source changes EP state.
                'excluded_burst_damage':{
                    'cast':sum(c['total'] for c in cast_bursts),
                    'phase':phase_totals(cast_bursts,duration)[0] if duration is not None else 0,
                    'window':sum(c['total'] for c in shown['components'] if c['name']=='神经损伤爆发'),
                    'cycle':cycle_neural_burst_damage}}
        bait_triggers=int(self.option('bait_triggers',0,maximum=100,integer=True)) if self.s['operator']=='char_1042_phatm2' and self.n==2 else 0
        if bait_triggers:
            alive=self.s.get('timing',{}).get('target_disappears_seconds')!=0
            cast_bursts=[c for c in full['components'] if c['name']=='神经损伤爆发']
            result['neural_bait_reference']={
                'skill':'本能的召唤','triggers_requested':bait_triggers,
                'attack_snapshot':'deployment','snapshot_attack':None,
                'duration_seconds':self.bb['buff_time'],'tick_interval_seconds':self.bb['interval_damage'],
                'arts_attack_scale':self.bb['atk_scale'],'buildup_attack_ratio':self.bb['ep_damage_ratio_token'],
                'buildup_ignores_resistance':True,'first_tick_seconds':None,
                'events_scheduled':False,
                'affected_damage_phases':{'cast':alive and full['duration']>0,
                    'window':alive and shown['duration']>0,'cycle':alive and cycle is not None},
                'excluded_burst_damage':{'cast':sum(c['total'] for c in cast_bursts),
                    'phase':phase_totals(cast_bursts,duration)[0] if duration is not None else 0,
                    'window':sum(c['total'] for c in shown['components'] if c['name']=='神经损伤爆发'),
                    'cycle':cycle_neural_burst_damage}}
        if self.s['operator']=='char_1048_orchd2':
            module=next((m for m in self.p['modules'] if m['id']==self.s.get('module_id')),None)
            elite=self.s.get('elite',2)
            level=self.s.get('level') or self.p['phases'][elite]['max_level']
            applied=bool(module and elite>=module['unlock_elite'] and level>=module['unlock_level'])
            module_delta=module['levels'][self.s['module_level']-1]['attributes'].get('respawn_time',0) if applied else 0
            result['orchid_redeploy_reference']={
                'scope':'cultivated attribute and same-identity talent parameter reference',
                'operator_id':self.p['id'],'module_id':self.s.get('module_id'),
                'module_level':self.s.get('module_level',0),'module_unlocked':applied,
                'module_attribute_delta_seconds_parameter':module_delta,
                'after_attribute_sources_seconds_reference':self.a['redeploy_seconds'],
                'talent_delta_seconds_parameter':self.orchid_redeploy_delta,
                'parameter_seconds':self.redeploy,
                'original_talent_identity':{'talent_index':3,'prefab_key':'3'},
                'actual_retreat_seconds':None,'actual_defeat_seconds':None,
                'actual_next_deployment_seconds':None,'events_scheduled':False,
                'native_attachment_verified':False,'live_state_verified':False,
                'source_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
                'source_selectors':[
                    'character_table.char_1048_orchd2.phases[*].attributesKeyFrames[*].data.respawnTime',
                    'character_table.char_1048_orchd2.potentialRanks[1].buff.attributes.attributeModifiers',
                    'character_table.char_1048_orchd2.talents[1].candidates',
                    'character_table.char_1048_orchd2.talents[3].candidates',
                    'uniequip_table.equipDict.uniequip_002_orchd2',
                    'battle_equip_table.uniequip_002_orchd2.phases[*].attributeBlackboard',
                    'battle_equip_table.uniequip_002_orchd2.phases[*].parts[*].addOrOverrideTalentDataBundle.candidates']}
            result['estimate']['notes'].append('梓兰再部署为原始培养与同身份天赋的参数参考；实际撤退、倒下和再次部署的时刻及当前热更新未核验，未安排部署事件。')
        if self.shu_periodic_sp_reference is not None:
            result['shu_periodic_sp_reference']=self.shu_periodic_sp_reference
            result['timing']['phase_clock_unbound']=True
            result['timing']['resource_and_damage_shared_clock']=False
            result['complete']=result['estimate']['complete']=False
            result['scope']=result['estimate']['scenario_scope']=(
                '所选技能阶段与观察窗口沿用明确情景；四岁周期技力首跳与阻回归属未核验，完整资源回转未知。')
            result['estimate']['notes'].append(
                '四岁条件下保留攻击力加成与4秒获得1点技力原参数；周期首跳、计时起点、重置和阻回期间归属未核验，'
                '不折算成自然回复速度，不用其它来源的充能算例证明完整初动、结束后充能或周期。')
        return result



def calculate_extended(scenario,attributes):return Combat(scenario,attributes).calculate()
