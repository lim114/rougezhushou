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
    reference={'source':copy.deepcopy(data['source']),'requested_level':level,'definitions':definitions,
        'exact_requested_level_present':str(level) in source,
        'stage_overrides':copy.deepcopy(data['bindings'][stage_id][key]['stage_overrides']),
        'first_activation_seconds':None,'effective_skill_damage':None,'inheritance_resolved':False,
        'limits':['原始等级分别保留；已证的基包配置另列，未把null当空列表或猜测当前实战默认技能。',
            '冷却、初始冷却、技力和参数都是配置；不等于实际首发、轮次或技能伤害。',
            '图鉴触发、首领阶段、隐藏脚本和环境修正还需逐项核验；字段0不证明出生即发动。']}
    from .enemy_reference_construction import source_path
    reference['construction_reference']=source_path(data['bindings'][stage_id][key],reference['exact_requested_level_present'])
    from .enemy_sp_reference import compiled_sp_reference
    reference['compiled_sp_reference']=compiled_sp_reference(reference)
    from .enemy_configuration import compiled_configuration
    reference['compiled_configuration']=compiled_configuration(reference)
    return reference

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

def enemy_skill_text(reference,technical=False):
    lines=['【技能状态】','实际首次发动时刻：未知；完整技能伤害：未知。']
    definitions=reference['definitions']
    overrides=reference['stage_overrides']
    records=[*definitions,*([overrides] if overrides else [])]
    configured=sum(len(d['skills']) for d in records if isinstance(d.get('skills'),list))
    sp_records=sum(isinstance(d.get('spData'),dict) for d in records)
    parameter_count=sum(len(d['talentBlackboard']) for d in records if isinstance(d.get('talentBlackboard'),list))
    parameter_count+=sum(len(s['blackboard']) for d in records if isinstance(d.get('skills'),list)
        for s in d['skills'] if isinstance(s,dict) and isinstance(s.get('blackboard'),list))
    malformed=any(d.get('skills') is not None and (not isinstance(d['skills'],list) or
        any(not isinstance(s,dict) for s in d['skills'])) for d in records)
    malformed|=any(d.get('spData') is not None and not isinstance(d['spData'],dict) for d in records)
    malformed|=any(d.get('talentBlackboard') is not None and (not isinstance(d['talentBlackboard'],list) or
        any(not isinstance(v,dict) for v in d['talentBlackboard'])) for d in records)
    malformed|=any(s.get('blackboard') is not None and (not isinstance(s['blackboard'],list) or
        any(not isinstance(v,dict) for v in s['blackboard'])) for d in records if isinstance(d.get('skills'),list)
        for s in d['skills'] if isinstance(s,dict))
    if configured or sp_records or parameter_count:
        parts=([f'{configured}条招式配置'] if configured else [])+([f'{sp_records}组技力配置'] if sp_records else [])
        lines.append('未合并资料：'+('、'.join(parts) if parts else '仅包含待核验机制参数')+'。')
        if parameter_count:lines.append(f'另有{parameter_count}项未核验参数；原文可在技术资料中查看。')
        lines.append('原始等级定义与本关卡覆盖分别保留，未推定合并为当前实战技能；配置不等于实际首发、轮次或技能伤害。')
    else:
        lines.append('未取得非空技能/技力配置；这不证明没有默认或隐藏技能。')
    if malformed:lines.append('部分参数格式未确认，保留原文并等待核验。')
    if any(d.get('skills')==[] for d in records):lines.append('部分技能字段为空，不证明没有默认/隐藏技能。')
    if reference.get('construction_reference',{}).get('mode')=='stage_constructor':
        lines.append('本关卡采用独立构造，不使用数据库等级定义；资源标识与关卡别名分开。')
    elif not reference['exact_requested_level_present']:
        lines.append('当前引用等级没有独立定义；低等级资料不能当作已确认的有效继承。')
    compiled=reference.get('compiled_sp_reference')
    if compiled and compiled['state']=='unavailable_exact_database_level':
        lines.append('固定数据库缺少精确等级；默认/别名构建路径未核验，未借用较低等级技力配置。')
    elif compiled and compiled['state']=='constructor_sp_baseline_unknown':
        lines.append('未见非空技力覆盖，构造空指针分配基线尚未闭合；完整技力配置保持未知，不借用数据库。')
    elif compiled and compiled['state']=='compiled_configuration_available':
        lines.append('技力配置分项已按基包非空整记录规则解析；实际控制器、首次发动与完整回转仍未知。')
    if compiled and compiled['initialization_reference']['state']=='conditional_baseline_available':
        lines.append('默认或显式初始化来源已核验到基包条件分支；当前热更新和实际控制器仍未知。')
    configuration=reference.get('compiled_configuration')
    if configuration:
        from .enemy_configuration import construction_text
        lines.extend(['',construction_text(configuration,technical=technical)])
    if not technical:return '\n'.join(lines)
    if compiled:
        lines.extend(['','【基包技力配置继承参考】',
            '解析状态：'+({'compiled_configuration_available':'有明确配置参考',
                'no_explicit_sp_configuration':'未取得显式配置，不证明没有默认控制器',
                'unavailable_exact_database_level':'精确等级不可用，构建路径待核验',
                'unsupported_source_shape':'来源形状未覆盖，保留未知'}.get(compiled['state'],'未知')),
            '按源配置解析的技力记录：'+raw_text(compiled['configuration']),
            '继承来源链：'+raw_text(compiled['source_chain']),
            '当前实际技力控制器、首次发动和完整回转：未知。'])
        init=compiled['initialization_reference']
        lines.extend(['【无热更新钩子的基包初始化参考】',
            '初始化参考状态：'+raw_text(init['state'])+'；路径：'+raw_text(init['path']),
            '条件成立时的字段赋值参考：'+raw_text(init['scalar_assignment_reference']),
            *('• '+note for note in init['required_conditions'])])
    detail=[]
    for d in reference['definitions']:
        content=definition_text(d)
        if content:detail.extend([f"原始等级 {d['level']} 的定义（未合并）：",*content])
    if reference['stage_overrides']:
        content=definition_text(reference['stage_overrides']) or ['原始覆盖字段：'+raw_text(reference['stage_overrides'])]
        detail.extend(['本关卡的原始覆盖字段（未推定合并）：',*content])
    lines.extend(['','【技能原始配置】',*detail,*('• '+s for s in reference['limits'])])
    lines.extend(['完整原始等级字段：'+raw_text(definitions),'完整本关卡覆盖字段：'+raw_text(overrides)])
    source=reference.get('source') or {}
    database=source.get('enemy_database') or {}
    if database.get('url'):lines.append('技能配置来源：'+database['url'])
    return '\n'.join(lines)
