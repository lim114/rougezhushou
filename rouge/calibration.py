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
