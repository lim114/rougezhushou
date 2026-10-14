"""Read-only, source-qualified calibration worksheets for the first three operators.

These tools explain existing arithmetic and compare declared evidence. They never
operate a game, mutate run memory, or certify an unobserved native action clock.
"""
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
from .catalog import catalog, operator_attributes
from .damage import calculate_damage, _prepare_damage

OPERATORS = ('kaltsit', 'silverash', 'mechanist')
LABELS = {'hp':'生命上限','attack':'攻击力','defense':'防御力',
          'resistance':'法术抗性','redeploy_seconds':'再部署秒数',
          'attack_speed':'攻速属性','block_count':'阻挡数',
          'deployment_cost':'部署费用','interval':'基础攻击间隔',
          'sp_recovery':'自然技力恢复速度'}
BOUNDARY = '局外声明条件下的计算对照；不证明当前客户端面板或原生时钟。'

def _number(value, name, maximum=None):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
        raise ValueError(name+'需要有限非负数。')
    if maximum is not None and value>maximum:raise ValueError(name+'超出范围。')
    return value

def _integer(value, name, maximum):
    if not isinstance(value,int) or isinstance(value,bool) or not 0<=value<=maximum:
        raise ValueError(name+'需要规定范围内的整数。')
    return value

def _scenario(scenario):
    if not isinstance(scenario,dict):raise ValueError('scenario需要JSON对象。')
    out=deepcopy(scenario)
    if out.get('operator') not in OPERATORS:raise ValueError('校准工具仅支持首批三名干员。')
    if any(str(key).startswith('_') for key in out):raise ValueError('校准输入不能注入内部字段。')
    out.setdefault('skill',1);out.setdefault('skill_rank',10)
    out.setdefault('elite',2);out.setdefault('level',catalog()['operators'][out['operator']]['phases'][out['elite']]['max_level'] if isinstance(out['elite'],int) and not isinstance(out['elite'],bool) and 0<=out['elite']<=2 else None)
    out.setdefault('trust',100);out.setdefault('potential',1)
    out.setdefault('module_id',None);out.setdefault('module_level',0)
    out.setdefault('timing_mode','frames')
    return out

def _source():return deepcopy(catalog()['source'])

def _cultivated(scenario, **overrides):
    s={**scenario,**overrides}
    return operator_attributes(s['operator'],s['elite'],s['level'],s['trust'],s['potential'],s['module_id'],s['module_level'])

def _fingerprint(value):
    return sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def _context(s):
    return {'scenario':deepcopy(s),'source_commit':catalog()['source']['commit']}

def panel_layers(scenario):
    """Expose ordered cultivation/rune/talent/skill stages, without changing math."""
    s=_scenario(scenario);cult=_cultivated(s)
    prepared=_prepare_damage(deepcopy(s));resolved,rune,_,_=prepared
    result=calculate_damage(deepcopy(s));base=result['estimate']['base_stats']
    skill=result['estimate']['skill']
    stages=[('培养与模组',cult),('藏品与分队符文写回',rune),('已覆盖常态天赋与效果',base),
            ('技能期间参考',{'attack':skill.get('skill_attack'),
              'attack_speed':skill.get('skill_attack_speed_reference')})]
    rows=[]
    for field,label in LABELS.items():
        values=[{'stage':name,'value':stats.get(field),'delta_from_previous':
                 None if i==0 or field not in stats or field not in stages[i-1][1]
                 else stats[field]-stages[i-1][1][field]} for i,(name,stats) in enumerate(stages)]
        if any(v['value'] is not None for v in values):rows.append({'field':field,'label':label,'stages':values})
    ctx=_context(s)
    return {'operator':catalog()['operators'][s['operator']]['name'],'context':ctx,
            'context_token':_fingerprint(ctx),'rows':rows,'panels':{name:deepcopy(stats) for name,stats in stages},
            'rune_sources':deepcopy(resolved.get('_attribute_runes',[])),
            'source':_source(),'model_complete':result['estimate'].get('complete',False),
            'warnings':deepcopy(result.get('warnings',[])),'native_verified':False,
            'notes':[BOUNDARY,'相邻层差值用于定位偏差，不代表把跨层效果相加即可重新得到结果。',
                     '技能面板仅列当前模型已输出的攻击与攻速；未覆盖的技能生命、防御变化没有伪造数值。']}

COMMANDS={'panel':panel_layers}

from .relic_panel_diagnostics import relic_panel_diagnostics
COMMANDS['relic-panels'] = relic_panel_diagnostics


def compare_panel(scenario, observation, tolerance=0):
    """Compare only the declared matching panel/context; never relabel a source."""
    predicted=panel_layers(scenario);_number(tolerance,'tolerance')
    if not isinstance(observation,dict):raise ValueError('observation需要JSON对象。')
    if observation.get('context_token')!=predicted['context_token']:
        raise ValueError('观察值与预测条件不一致；请先用panel导出相同条件标识。')
    panel=observation.get('panel')
    if panel not in predicted['panels']:raise ValueError('观察面板类型不明确。')
    kind=observation.get('evidence_kind')
    if kind not in ('game_panel','public_case','formula_reference'):
        raise ValueError('必须区分游戏面板、公开算例与公式参考。')
    source=observation.get('source')
    if not isinstance(source,str) or not source.strip():raise ValueError('观察值必须注明来源。')
    values=observation.get('values')
    if not isinstance(values,dict) or not values:raise ValueError('观察值不能为空。')
    rows=[]
    for field,actual in values.items():
        if field not in LABELS:raise ValueError('未支持的面板字段：'+str(field))
        _number(actual,field);expect=predicted['panels'][panel].get(field)
        delta=None if expect is None else actual-expect
        rows.append({'field':field,'label':LABELS[field],'predicted':expect,'observed':actual,
                     'difference':delta,'relative_difference':None if not expect else delta/abs(expect),
                     'matches_declared_tolerance':None if delta is None else abs(delta)<=tolerance,
                     'other_stage_matches':[r['stage'] for row in predicted['rows'] if row['field']==field
                         for r in row['stages'] if r['value'] is not None and abs(actual-r['value'])<=tolerance and r['stage']!=panel]})
    return {'operator':predicted['operator'],'context_token':predicted['context_token'],
            'panel':panel,'evidence_kind':kind,'source':source,'tolerance':tolerance,'rows':rows,
            'all_compared_values_match':all(r['matches_declared_tolerance'] is True for r in rows),
            'uncompared_fields':[f for f in predicted['panels'][panel] if f in LABELS and f not in values],
            'native_verified':False,'notes':[BOUNDARY,
                '来源类型由调用方声明；工具不把网页计算或用户填写值升级为实机证据。',
                '其它层命中仅是排查线索，不证明差异原因；部分字段相符不等于完整面板已通过。']}

COMMANDS['pair']=compare_panel


def skill_matrix(scenario, operators=None):
    """Show all nine skills' known components and missing complete totals."""
    base=_scenario(scenario);ops=list(OPERATORS) if operators is None else list(operators)
    if not ops or len(ops)>3 or any(op not in OPERATORS for op in ops):raise ValueError('operators只能选择首批三名。')
    rows=[]
    for op in dict.fromkeys(ops):
        profile=catalog()['operators'][op]
        for number,entry in enumerate(profile['skills'],1):
            s={**deepcopy(base),'operator':op,'skill':number}
            # Module IDs and operator-specific event conditions cannot cross owners.
            if op!=base['operator']:
                for key in ('module_id','module_level','base_attack','activation_count','deployment_stacks',
                            'companion_attack','shield_break_count','charge_count','cooperative','preexisting_fragile'):
                    s.pop(key,None)
            row={'operator':profile['name'],'operator_id':profile['id'],'skill':number,'skill_id':entry['id']}
            if s['elite']<entry['unlock_elite'] or (s['elite']<2 and s['skill_rank']>7):
                row.update(status='培养条件未开放',full_skill_damage=None,full_skill_healing=None)
            else:
                result=calculate_damage(s);skill=result['estimate']['skill']
                complete=bool(result['estimate'].get('complete',False))
                row.update(name=skill['name'],status='条件模型参考' if complete else '存在未核验项',
                    initial_seconds_reference=skill.get('initial_seconds'),recharge_seconds_reference=skill.get('recharge_seconds'),
                    cycle_seconds_reference=skill.get('cycle_seconds'),model_complete=complete,
                    model_complete_definition=result.get('complete_definition'),native_clock_verified=False,
                    conditional_total_reference={'damage':skill.get('total_damage'),'healing':skill.get('total_healing')},
                    full_skill_damage=0 if (op=='kaltsit' and number in (1,3)) or (op=='silverash' and number==1) else None,
                    full_skill_healing=0 if op in ('mechanist','silverash') else None,
                    declared_components=deepcopy(result.get('components',[])),
                    window_damage_reference=skill.get('window_damage'),window_healing_reference=skill.get('window_healing'),
                    missing_or_conditional_notes=deepcopy(result['estimate']['notes']),native_verified=False)
            rows.append(row)
    return {'rows':rows,'source':_source(),'native_verified':False,'notes':[BOUNDARY,
        '模型complete不是原生动作时钟核验；非零完整总量保持未知，原模型总量独立标为条件参考。',
        '调用方所选模组和专属事件条件只用于原干员，不复制到其他干员。']}

COMMANDS['skills']=skill_matrix


def cultivation_curve(scenario, levels=None):
    """Explain every level's base rounding and trust/potential/module increments."""
    s=_scenario(scenario);_cultivated(s)
    cap=catalog()['operators'][s['operator']]['phases'][s['elite']]['max_level']
    levels=list(range(1,cap+1)) if levels is None else list(levels)
    if not levels or len(levels)>cap or len(set(levels))!=len(levels):raise ValueError('levels需要不重复的有效等级。')
    rows=[]
    for level in sorted(levels):
        if not isinstance(level,int) or isinstance(level,bool) or not 1<=level<=cap:raise ValueError('等级超出当前阶段。')
        bare=_cultivated(s,level=level,trust=0,potential=1,module_id=None,module_level=0)
        trust=_cultivated(s,level=level,potential=1,module_id=None,module_level=0)
        pot=_cultivated(s,level=level,module_id=None,module_level=0)
        all_stats=_cultivated(s,level=level)
        rows.append({'level':level,'cultivated':all_stats,'contributions':{
            f:{'level_base':bare[f],'trust_increment':trust[f]-bare[f],
               'potential_increment':pot[f]-trust[f],'module_increment':all_stats[f]-pot[f]}
            for f in LABELS if f in all_stats}})
    return {'operator':catalog()['operators'][s['operator']]['name'],'elite':s['elite'],
            'rows':rows,'source':_source(),'scope':'培养属性，不包含藏品、部署天赋或技能。',
            'notes':['信赖为加成进度0–100，不是游戏显示的0–200信赖百分比。',
                     '潜能强化的天赋变体不冒充潜能直接白值增量；模组未达门槛时贡献为0。'],
            'native_verified':False}

COMMANDS['cultivation']=cultivation_curve


def module_stages(scenario):
    """List actual module stage records and cultivated deltas behind their gates."""
    s=_scenario(scenario);baseline=_cultivated(s,module_id=None,module_level=0)
    profile=catalog()['operators'][s['operator']];rows=[]
    for module in profile['modules']:
        qualified=s['elite']>=module['unlock_elite'] and s['level']>=module['unlock_level']
        for stage in module['levels']:
            stats=_cultivated(s,module_id=module['id'],module_level=stage['level'])
            parts=[]
            for index,part in enumerate(stage.get('parts',[])):
                parts.append({'part_index':index,'resource_key':part.get('resKey'),
                    'target':part.get('target'),'token_part':part.get('isToken'),
                    'game_tag':part.get('validInGameTag'),'map_tag':part.get('validInMapTag'),
                    'talent_candidates':deepcopy(part.get('addOrOverrideTalentDataBundle')),
                    'trait_candidates':deepcopy(part.get('overrideTraitDataBundle')),
                    'runtime_attachment_verified':False})
            rows.append({'module_id':module['id'],'name':module['name'],'stage':stage['level'],
                'qualified':qualified,'unlock_elite':module['unlock_elite'],'unlock_level':module['unlock_level'],
                'requested':s.get('module_id')==module['id'] and s.get('module_level')==stage['level'],
                'cultivated_attributes':stats,'attribute_delta':{f:stats[f]-baseline[f] for f in LABELS if f in stats},
                'source_attributes':deepcopy(stage.get('attributes',{})),'parts':parts})
    return {'operator':profile['name'],'baseline':baseline,'rows':rows,'source':_source(),
        'native_verified':False,'notes':[BOUNDARY,
            '属性资格与实际装备分开；列出候选不证明隐藏脚本附着或特殊伤害包都受加成。',
            '当前快照无模组记录时列空，不等同证明当前热更新也没有模组。']}

COMMANDS['modules']=module_stages


def talent_states(scenario, elapsed_seconds=None):
    """Inspect selected talent variants and their declaration-dependent panels."""
    from .operator_engine import selected_talents
    s=_scenario(scenario);_cultivated(s)
    profile=catalog()['operators'][s['operator']]
    selected,_=selected_talents(profile,s)
    times=[0,14.9,15,30] if elapsed_seconds is None else list(elapsed_seconds)
    if not times or len(times)>100:raise ValueError('最多100个在场时间条件。')
    rows=[]
    for elapsed in times:
        _number(elapsed,'在场秒数')
        request={**deepcopy(s),'deployment_elapsed_seconds':elapsed}
        result=calculate_damage(request);stats=result['estimate']['base_stats'];references=[]
        for talent in selected:
            bb=talent['values']
            if s['operator']=='silverash' and talent['name']=='雪境先驱':
                doubled=elapsed>=bb['interval']
                references.append({'name':talent['name'],'doubled':doubled,
                    'defense_addition_reference':bb['def']*(2 if doubled else 1),
                    'regeneration_per_second_reference':stats['hp']*bb['hp_recovery_per_sec_by_max_hp_ratio']*(2 if doubled else 1),
                    'kind':'独立生命回复速度','actual_healing_total':None})
            elif s['operator']=='kaltsit' and talent['name']=='医者丰碑':
                references.append({'name':talent['name'],'recipient_regeneration_rate_reference':bb['hp_recovery_per_sec'],
                    'rhodes_rate_reference':bb['hp_recovery_per_sec']*bb['rhodes_bonus'],
                    'duration_parameter_seconds':bb['buff_duration'],'kind':'进入范围后的条件生命回复',
                    'actual_healing_total':None})
        rows.append({'deployment_elapsed_seconds':elapsed,'base_stats':deepcopy(stats),'talent_references':references})
    return {'operator':profile['name'],'selected_talents':deepcopy(selected),'rows':rows,
        'source':_source(),'native_verified':False,'notes':[BOUNDARY,
            '在场秒数由调用方声明，不是局内自动测量；被动回复速度独立于技能直接治疗。',
            '未声明领取者、进入时刻、损血和首跳的增益不换算为有效治疗总量。']}

COMMANDS['talents']=talent_states


def animation_events(scenario, orientation=None, animation_contains=None):
    """Return original events, including excluded loops, without auto-binding."""
    s=_scenario(scenario);_cultivated(s)
    if orientation is not None and orientation not in ('Front','Back'):raise ValueError('orientation为Front或Back。')
    if animation_contains is not None and not isinstance(animation_contains,str):raise ValueError('animation_contains需要文本。')
    data=json.loads((Path(__file__).parent/'data/original-animation-references.json').read_text(encoding='utf-8'))
    profile=data['operators'].get(s['operator'])
    if profile is None:raise ValueError('当前干员缺原动画资料。')
    records=[deepcopy(r) for r in profile['records'] if (orientation is None or r['orientation']==orientation)
             and (animation_contains is None or animation_contains.casefold() in r['animation'].casefold())]
    return {'operator':profile['name'],'source_commit':data['source_commit'],'reference_fps':data['fps'],
        'records':records,'count':len(records),'native_verified':False,'notes':[
            '原版动作资料，不证明实际选择此动画、OnAttack等于命中、皮肤等价或技能状态重置。',
            '循环/过渡/多事件动作保留用于查证，不能默认拼接或作为攻击时钟。',
            '严格向上取整与表示误差归一帧均保留；表示归一不能当作实际游戏容差。']}

COMMANDS['animations']=animation_events


def recipient_events(scenario, recipients=None, enemy_defense=0, window_seconds=None):
    """SilverAsh S2 declared recipient packets; independent of his own attack."""
    s=_scenario(scenario)
    if s['operator']!='silverash' or s['skill']!=2:raise ValueError('此时间线仅支持凛御银灰S2。')
    calculate_damage(deepcopy(s))
    _number(enemy_defense,'enemy_defense')
    if window_seconds is not None:_number(window_seconds,'window_seconds')
    recipients=[] if recipients is None else recipients
    if not isinstance(recipients,list) or len(recipients)>100:raise ValueError('recipients最多100个声明单位。')
    bb=catalog()['operators']['silverash']['skills'][1]['levels'][s['skill_rank']-1]['values']
    records=[];seen=set()
    for recipient in recipients:
        if not isinstance(recipient,dict):raise ValueError('受益人需要JSON对象。')
        identity=recipient.get('id')
        if not isinstance(identity,str) or not identity or identity in seen:raise ValueError('每次受益部署需要唯一非空id。')
        seen.add(identity)
        if recipient.get('is_token',False) is not False:raise ValueError('固定原补丁排除召唤物卡；请声明真实干员受益部署。')
        deployment=recipient.get('deployment_seconds',0);_number(deployment,'deployment_seconds')
        stacks=_integer(recipient.get('stacks',0),'stacks',int(bb['max_stack_cnt']))
        attacks=recipient.get('attack_at_triggers',[None]*stacks)
        if not isinstance(attacks,list) or len(attacks)!=stacks:raise ValueError('attack_at_triggers需与声明叠层数一一对应。')
        for index,attack in enumerate(attacks):
            if attack is not None:_number(attack,'触发时受益干员攻击力')
            time=deployment+1.1+0.5*index
            raw=None if attack is None else attack*bb['atk_scale']
            amount=None if raw is None else max(raw-enemy_defense,raw*.05)
            included=window_seconds is None or time<window_seconds
            records.append({'recipient_id':identity,'trigger_index':index+1,
                'time_seconds_reference':time,'recipient_attack_at_trigger':attack,'attack_scale':bb['atk_scale'],
                'pre_defense_damage':raw,'post_defense_damage_reference':amount,
                'included_in_declared_window':included,'source_unit':None,'damage_type':'physical'})
    known=sum(r['post_defense_damage_reference'] for r in records if r['included_in_declared_window'] and r['post_defense_damage_reference'] is not None)
    missing=sum(r['included_in_declared_window'] and r['post_defense_damage_reference'] is None for r in records)
    return {'events':records,'known_packet_subtotal_reference':known,
        'declared_recipient_damage_reference':None if missing else known,'missing_attack_snapshots':missing,
        'full_skill_damage':None,'native_clock_verified':False,'source':[
            {'url':'https://prts.wiki/w/凛御银灰','observed_revision':435034,'kind':'社区详细机制资料'},
            {'url':'https://raw.githubusercontent.com/fexli/ArknightsResource/d0b5af0b004b044d322397ce5ae79632b6d9fcdd/gamedata/%5Buc%5Dlua/hotfixes/svash2hotfixer.lua',
             'kind':'固定原补丁','establishes':'待部署卡必须存在data且非token；不能证明事件时钟。'}],
        'notes':['声明受益条件下、单个命中目标的参考包；不自动判定获得效果、格子命中、在场存续或当前客户端热更新。',
            '每包使用调用方声明的触发时受益干员攻击力；不沿用银灰攻击，不推测同帧属性写入顺序。',
            '1.1秒首触发及0.5秒间隔来自已读取的机制页；未证明逻辑帧相位，不计入完整技能总量。',
            '仅标准物理减伤，未混入自身伤害来源天赋、敌方阶段、其他承伤倍率或脆弱；窗口为左闭右开。']}

COMMANDS['recipient-events']=recipient_events


def packet_worksheet(scenario):
    """Expose stat/multiplier/defense arithmetic without assuming attack counts."""
    from .enemy_environment import damage_factor
    s=_scenario(scenario);prepared=_prepare_damage(deepcopy(s));resolved=prepared[0]
    result=calculate_damage(deepcopy(s));profile=catalog()['operators'][s['operator']]
    bb=profile['skills'][s['skill']-1]['levels'][s['skill_rank']-1]['values']
    attack=result['attack'];op=s['operator'];number=s['skill'];rows=[]
    defense=float(resolved.get('enemy_defense',0));resistance=float(resolved.get('enemy_resistance',0))
    def add(name,dtype,scale,owner_attack=attack):
        raw=owner_attack*scale
        after=(max(raw-defense,raw*.05) if dtype=='physical' else
               max(raw*(1-resistance/100),raw*.05) if dtype=='magic' else raw)
        factor=damage_factor(resolved,dtype) if dtype!='healing' else 1
        if dtype!='healing':factor*=1+sum(float(e['value']) for e in result.get('applied_effects',[]) if e['kind']=='damage_taken' and e.get('damage_type')==dtype)
        fragile=bb['damage_scale'] if op=='silverash' and number==3 and s.get('preexisting_fragile',False) else 1
        if dtype!='healing':factor*=fragile
        rows.append({'name':name,'damage_type':dtype,'owner_attack_reference':owner_attack,'scale':scale,
            'pre_defense_value':raw,'enemy_defense':defense if dtype=='physical' else None,
            'enemy_resistance':resistance if dtype=='magic' else None,'after_defense_value':after,
            'supported_damage_factor':factor,'single_packet_reference':after*factor,
            'packet_count':None,'complete_cast_total':None})
    if op=='kaltsit':
        if number==2:
            add('医疗单元单个敌人真实伤害','true',bb['attack@atk_scale'])
            add('医疗单元每名受益人的潜在治疗','healing',bb['attack@heal_scale'])
        else:add('本体每个受疗目标的潜在治疗','healing',1)
    elif op=='mechanist':
        if number==1:add('五连击中单段物理伤害','physical',bb['attack@atk_scale'])
        elif number==2:add('单次破屏条件爆炸','magic',bb['atk_scale'])
        else:
            add('本体单次轰击','magic',bb['attack@atk_scale'])
            add('结构性原理单次冲锋条件','physical',bb['atk_scale'])
    elif number==2:
        add('本体单次技能范围效果','physical',bb['atk_scale'])
        if 'companion_attack' in s:add('声明受益干员单次部署效果','physical',bb['atk_scale'],float(s['companion_attack']))
    elif number==3:add('丹增单次命中条件','physical',bb['bird_atk_scale'])
    module_reference=result.get('mechanist_module_reference')
    if module_reference:
        selected=[row for row in module_reference['packets'] if row['key']!='normal']
        for row,packet in zip(rows,selected):
            row['module_attack_scale']=packet['module_attack_scale']
            row['pre_module_packet_reference']=row['pre_defense_value']
            raw=packet['selected_raw_packet']
            row['pre_defense_value']=raw
            row['after_defense_value']=None if raw is None else (max(raw-defense,raw*.05) if row['damage_type']=='physical' else max(raw*(1-resistance/100),raw*.05))
            row['single_packet_reference']=packet['per_hit_reference']
    return {'operator':profile['name'],'skill':s['skill'],'skill_name':result['estimate']['skill']['name'],
        **({'mechanist_module_reference':deepcopy(module_reference)} if module_reference else {}),
        'rows':rows,'source':_source(),'native_verified':False,'warnings':result.get('warnings',[]),
        'notes':[BOUNDARY,'单包不乘未知攻击次数，不生成技能总量、回转或周期。',
            '治疗包是单名受益人的原始潜在治疗，未加入受疗加成、禁疗、实际损血或有效覆盖。',
            '攻击取现有模型已覆盖条件；机械师模组伤害包适用范围及限时攻击快照仍须独立核验。']}

COMMANDS['packets']=packet_worksheet


def calibration_worksheets(cases=None):
    """Replay sourced arithmetic references, without calling them game captures."""
    if cases is None:
        common='已封存属性层原件算式，.cache/research/relic-panel-056/REPORT.md'
        cases=[
            {'id':'mechanist_base','scenario':{'operator':'mechanist','skill':3},'panel':'培养与模组',
             'values':{'hp':3631,'attack':573,'defense':765},'source':'https://m.prts.wiki/w/机械师','evidence_kind':'public_case'},
            {'id':'mechanist_module_1','scenario':{'operator':'mechanist','skill':3,'module_id':'uniequip_002_mcnist','module_level':1},
             'panel':'培养与模组','values':{'attack':633,'defense':805},'source':common,'evidence_kind':'formula_reference'},
            {'id':'mechanist_module_3','scenario':{'operator':'mechanist','skill':3,'module_id':'uniequip_002_mcnist','module_level':3},
             'panel':'培养与模组','values':{'attack':673,'defense':845},'source':common,'evidence_kind':'formula_reference'},
            {'id':'mechanist_rune_skill','scenario':{'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_16']},
             'panel':'技能期间参考','values':{'attack':2720.8},'source':common,'evidence_kind':'formula_reference','tolerance':1e-9},
            {'id':'kaltsit_base','scenario':{'operator':'kaltsit','skill':2},'panel':'培养与模组',
             'values':{'hp':2120,'attack':510,'defense':306},'source':'https://prts.wiki/w/凯尔希·思衡托','evidence_kind':'public_case'},
            {'id':'kaltsit_rune_talent','scenario':{'operator':'kaltsit','skill':2,'relic_ids':['rogue_6_relic_legacy_90']},
             'panel':'已覆盖常态天赋与效果','values':{'hp':3975},'source':common,'evidence_kind':'formula_reference'},
            {'id':'kaltsit_rune_skill','scenario':{'operator':'kaltsit','skill':2,'relic_ids':['rogue_6_relic_legacy_19']},
             'panel':'技能期间参考','values':{'attack':1595},'source':common,'evidence_kind':'formula_reference'},
            {'id':'silverash_base','scenario':{'operator':'silverash','skill':3},'panel':'培养与模组',
             'values':{'hp':2318,'attack':653,'defense':437},'source':'https://prts.wiki/w/凛御银灰','evidence_kind':'public_case'},
            {'id':'silverash_talent_early','scenario':{'operator':'silverash','skill':3,'deployment_elapsed_seconds':0},
             'panel':'已覆盖常态天赋与效果','values':{'defense':497},'source':'固定天赋60与培养DEF437算式','evidence_kind':'formula_reference'},
            {'id':'silverash_talent_late','scenario':{'operator':'silverash','skill':3,'deployment_elapsed_seconds':15},
             'panel':'已覆盖常态天赋与效果','values':{'defense':557},'source':'固定天赋60×2与培养DEF437算式','evidence_kind':'formula_reference'},
        ]
    if not isinstance(cases,list) or not cases or len(cases)>100:raise ValueError('cases需要1–100份注明来源的算例。')
    rows=[];seen=set()
    for case in cases:
        if not isinstance(case,dict) or not isinstance(case.get('id'),str) or not case['id'] or case['id'] in seen:
            raise ValueError('每份算例需要唯一非空id。')
        seen.add(case['id']);s=case['scenario'];panel=panel_layers(s)
        observation={key:deepcopy(case[key]) for key in ('panel','values','source','evidence_kind')}
        observation['context_token']=case.get('context_token',panel['context_token'])
        compared=compare_panel(s,observation,case.get('tolerance',0))
        rows.append({'id':case['id'],'scenario':deepcopy(s),'comparison':compared})
    return {'rows':rows,'case_count':len(rows),
        'matching_reference_cases':sum(r['comparison']['all_compared_values_match'] for r in rows),
        'source':_source(),'native_verified':False,'notes':[
            '默认案例为公开培养表与已封存原件算式的交叉核对，不是网上实机录屏或当局截图。',
            '公式参考、公开算例、调用方声明实机观察分别保留；不以共同数据源一致代替独立实机验收。',
            '机械师2720.8手算十进制例声明1e-9数值容差，仅覆盖浮点表示尾差，不是游戏误差范围；其它案例默认0。',
            '每份工作表仅覆盖列出的字段和固定来源版本；未证明动作时钟或当前热更新。']}

COMMANDS['worksheets']=calibration_worksheets


def barrier_packet_ledger(ledger):
    from .mechanist_barrier_ledger import mechanist_barrier_ledger
    return mechanist_barrier_ledger(ledger)


COMMANDS['barrier-ledger'] = barrier_packet_ledger
