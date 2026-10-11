"""Independent cultivation proposals; recompute attributes and supported skills."""
import json
from copy import deepcopy
from .catalog import catalog,operator_profiles,operator_attributes
from .damage import calculate_damage
from .healing_budget import _amount
from .supplemental_skills import defaults,skill_reference,supplemental_profiles


def compare_cultivation(scenario,preview):
    if type(preview) is not dict or set(preview)!={'proposals'}: raise ValueError('需要proposals培养方案列表。')
    proposals=preview['proposals'];identity=scenario.get('operator')
    if type(identity) is not str or identity not in operator_profiles(): raise ValueError('需要有效干员。')
    if type(proposals) is not list or not 1<=len(proposals)<=12: raise ValueError('培养方案需要1–12项，第一项作为差值基准。')
    seen=set();rows=[]
    for proposal in proposals:
        if type(proposal) is not dict or set(proposal)!={'name','elite','level','trust','potential','module_id','module_level'}:
            raise ValueError('每个方案需要name、elite、level、trust、potential、module_id、module_level。')
        name=proposal['name']
        if (type(name) is not str or not 1<=len(name)<=60 or name in seen or
            any(ord(c)<32 or 0xd800<=ord(c)<=0xdfff for c in name)): raise ValueError('方案名称需要唯一的1–60字符名称。')
        seen.add(name)
        row={'name':name,'status':'待计算','error':None,'proposal':deepcopy(proposal),'attributes':None,
             'attack':None,'hp':None,'defense':None,'delta_attack':None,'delta_hp':None,'delta_defense':None,
             'window_damage':None,'window_healing':None,'delta_window_damage':None,'delta_window_healing':None,
             'skill_reference':None,'skill_differences':{},'module_applied':False,'notes':[]}
        rows.append(row)
        conditions={k:v for k,v in proposal.items() if k!='name'}
        try:
            conditions['trust']=_amount(conditions['trust'],'信赖',100)
            mid=conditions['module_id'];ml=conditions['module_level']
            if type(ml) is not int or (mid is None and ml!=0) or (mid is not None and type(mid) is not str):
                raise ValueError('无模组需module_id=null及module_level=0；模组需有效身份及整数等级。')
            attributes=operator_attributes(identity,**conditions)
            module=next((m for m in operator_profiles()[identity]['modules'] if m['id']==mid),None)
            row['module_applied']=bool(module and conditions['elite']>=module['unlock_elite'] and conditions['level']>=module['unlock_level'])
            row['attributes']=attributes
            for key in ('attack','hp','defense'):row[key]=attributes[key]
            row['status']='基础属性参考'
            if mid and not row['module_applied']:row['notes'].append('当前培养未满足所选模组解锁门，未加入模组属性或技能效果。')
        except (ValueError,KeyError,TypeError) as error:
            row.update(status='不可测算',error=str(error));continue
        proposed={**deepcopy(scenario),**conditions};proposed.pop('base_attack',None)
        try:
            if identity in catalog()['operators']:
                modeled=calculate_damage(proposed);metrics=modeled['estimate']['skill']
                row.update(status='技能已计参考' if modeled['complete'] else '技能部分参考',
                           window_damage=metrics.get('window_damage'),window_healing=metrics.get('window_healing'))
                row['notes'].extend(modeled['estimate']['notes'])
            elif identity in supplemental_profiles()['operators']:
                supplied=defaults(identity)
                for key in supplied:
                    if key in proposed:supplied[key]=proposed[key]
                # Supplemental budget is a one-event parameter comparison.
                supplied.update(count=1,missing_hp=0)
                row['skill_reference']=skill_reference(supplied);row['status']='单次技能参考'
            else:row['notes'].append('该干员技能数值尚未接入，只比较基础培养属性。')
        except ValueError as error:
            row['error']=str(error);row['status']='仅属性；技能不可测算'
    baseline=rows[0]
    if baseline['attributes'] is None:raise ValueError('基准培养方案不可测算：'+baseline['error'])
    for row in rows:
        for key in ('attack','hp','defense','window_damage','window_healing'):
            a=row[key];b=baseline[key];row['delta_'+key]=a-b if a is not None and b is not None else None
        if row['skill_reference'] and baseline['skill_reference']:
            base={r['name']:r['value'] for r in baseline['skill_reference']['rows']}
            row['skill_differences']={r['name']:r['value']-base[r['name']] if r['value'] is not None and base.get(r['name']) is not None else None for r in row['skill_reference']['rows']}
    return {'scenario':deepcopy(scenario),'preview':deepcopy(preview),'rows':rows,'baseline_name':baseline['name'],
            'operator_name':operator_profiles()[identity]['name'],
            'notes':['第一方案为差值基准；每行只替换培养及模组条件，技能、目标与其他计算条件沿用打开时预览。',
                     '基础属性列未叠加天赋/技能；已接入技能另行重算天赋门和模组门，未知输出或差值保留未知。',
                     '补充技能只比较单次分项；未接入的干员仍可比较培养属性。未提供材料成本或自动培养建议。',
                     '仅局外方案，不写入账户/本局。原生时序、条件模组完整性及当前实机面板仍待核验。']}


def format_cultivation(result):
    lines=[result['operator_name']+' · 培养方案对照；基准：'+result['baseline_name'],
           '固定技能/目标条件：'+json.dumps(result['scenario'],ensure_ascii=False),
           '声明方案：'+json.dumps(result['preview'],ensure_ascii=False)]
    for row in result['rows']:
        lines.append(f"{row['name']}（{row['status']}）：攻击{row['attack']}（差{row['delta_attack']}）；生命{row['hp']}（差{row['delta_hp']}）；防御{row['defense']}（差{row['delta_defense']}）；窗口伤害{row['window_damage']}、治疗{row['window_healing']}；未知差值不当零。")
        if row['skill_reference']:
            lines.append('单次技能分项：'+json.dumps(row['skill_reference']['rows'],ensure_ascii=False))
            lines.append('单次分项差值：'+json.dumps(row['skill_differences'],ensure_ascii=False))
            lines.extend(row['skill_reference']['notes'])
        if row['error']:lines.append(row['error'])
        lines.extend(row['notes'])
    return '\n'.join([*lines,*result['notes']])
