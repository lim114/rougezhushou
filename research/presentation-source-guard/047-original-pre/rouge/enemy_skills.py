"""Enemy skill configuration references, with no activation or damage forecast."""
import copy,json,math
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def skill_data():
    return json.loads((Path(__file__).with_name('data')/'enemy-skill-references.json').read_text(encoding='utf-8'))

def enemy_skill_reference(stage_id,enemy_id,level):
    if isinstance(level,bool) or not isinstance(level,int) or level<0:
        raise ValueError('敌人引用等级需要非负整数。')
    data=skill_data();key=enemy_id+'@'+str(level)
    if key not in data['bindings'].get(stage_id,{}):
        raise ValueError('技能资料必须绑定本关卡的敌人和引用等级。')
    source=data['definitions'].get(enemy_id,{})
    definitions=[{'level':int(n),**copy.deepcopy(row)} for n,row in sorted(source.items(),key=lambda p:int(p[0])) if int(n)<=level]
    return {'source':copy.deepcopy(data['source']),'requested_level':level,'definitions':definitions,
        'exact_requested_level_present':str(level) in source,
        'stage_overrides':copy.deepcopy(data['bindings'][stage_id][key]['stage_overrides']),
        'first_activation_seconds':None,'effective_skill_damage':None,'inheritance_resolved':False,
        'limits':['按原始等级分别列出；未把null当空列表，也未猜测继承、覆盖或默认技能。',
            '冷却、初始冷却、技力和参数都是配置；不等于实际首发、轮次或技能伤害。',
            '图鉴触发、首领阶段、隐藏脚本和环境修正还需逐项核验；字段0不证明出生即发动。']}

def raw_text(value):
    if value is None:return '未知'
    if isinstance(value,bool):return 'true' if value else 'false'
    if isinstance(value,(int,float)):
        return f'{value:g}' if math.isfinite(value) else '未知'
    if isinstance(value,(list,dict)):return json.dumps(value,ensure_ascii=False,separators=(',',':'))
    return str(value)

def blackboard_text(values):
    if values is None:return '未列出'
    if not isinstance(values,list):return '格式未确认：'+raw_text(values)
    if not values:return '当前字段为空（不证明没有其他脚本参数）'
    parts=[]
    for v in values:
        if not isinstance(v,dict):parts.append('格式未确认：'+raw_text(v));continue
        value=v.get('valueStr') if v.get('valueStr') is not None else v.get('value')
        parts.append(str(v.get('key') or '未命名参数')+' = '+raw_text(value))
    return '；'.join(parts)

def definition_text(d):
    lines=[];skills=d.get('skills');sp=d.get('spData');talents=d.get('talentBlackboard')
    if skills is not None:
        if not isinstance(skills,list):lines.append('技能列表格式未确认：'+raw_text(skills))
        elif not skills:lines.append('技能字段为空（不证明没有默认/隐藏技能）。')
        else:
            for i,s in enumerate(skills,1):
                if not isinstance(s,dict):lines.append('技能条目格式未确认：'+raw_text(s));continue
                lines.append(f"招式配置 {i} · 标识：{raw_text(s.get('prefabKey'))}")
                lines.append('冷却参数：'+raw_text(s.get('cooldown'))+'；初始冷却参数：'+raw_text(s.get('initCooldown'))+
                    '；技力需求：'+raw_text(s.get('spCost'))+'；优先级参数：'+raw_text(s.get('priority')))
                lines.append('招式参数：'+blackboard_text(s.get('blackboard')))
    if sp is not None:
        if isinstance(sp,dict):
            lines.append('技力配置：'+'；'.join(label+' = '+raw_text(sp.get(key)) for key,label in (
                ('spType','回复类型'),('maxSp','上限'),('initSp','初始技力'),('increment','回复增量'))))
        else:lines.append('技力配置格式未确认：'+raw_text(sp))
    if talents is not None and (talents or not isinstance(talents,list)):
        lines.append('机制参数：'+blackboard_text(talents))
    return lines

def enemy_skill_text(reference):
    lines=[]
    for d in reference['definitions']:
        content=definition_text(d)
        if content:lines.extend([f"原始等级 {d['level']} 的定义（未合并）：",*content])
    if reference['stage_overrides']:
        content=definition_text(reference['stage_overrides']) or ['原始覆盖字段：'+raw_text(reference['stage_overrides'])]
        lines.extend(['本关卡的原始覆盖字段（未推定合并）：',*content])
    if not lines:
        return '未取得非空技能/技力配置；这不证明没有默认或隐藏技能。'
    if not reference['exact_requested_level_present']:lines.append('当前引用等级没有独立定义；上列低等级资料不能当作已确认的有效继承。')
    return '\n'.join(['敌人技能配置参考：',*lines,'实际首次发动时刻：未知；完整技能伤害：未知。',
        *('• '+s for s in reference['limits'])])
