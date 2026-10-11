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
