"""Explicit common-rank projection from an observed, limited run form.

The native UI shares mainSkillLvl across skills. A projection is still an
offline reference for a skill not directly read; it never fills saved facts,
propagates a mastery, or derives a recruitment compensation from upper bounds.
"""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path


@lru_cache(maxsize=1)
def source():
    return json.loads((Path(__file__).parent/'data/run-common-skill-rules.json').read_text(encoding='utf-8'))


def _original(profile):
    if not profile:
        return None
    original=source()['operators'].get(profile.get('id'))
    if not original or len(original['skills'])!=len(profile['skills']):
        return None
    if any(raw['skill_id']!=current.get('id') or
           int(raw['unlock_cond']['phase'].split('_')[-1])!=current.get('unlock_elite',index)
           for index,(raw,current) in enumerate(zip(original['skills'],profile['skills']))):
        return None
    return original


def use_qualification(profile,skill,rank,elite,level):
    """MainSkill rank-use gate; common training requirements are a separate gate."""
    original=_original(profile)
    if original is None:
        return {'available':None,'original_status':'missing','gate':None,'path':None}
    if type(skill) is not int or not 1<=skill<=len(original['skills']):
        return {'available':False,'original_status':'located','gate':None,'path':None}
    raw=original['skills'][skill-1]
    if type(rank) is not int or not 1<=rank<=min(10,len(profile['skills'][skill-1]['levels'])):
        return {'available':False,'original_status':'located','gate':None,'path':None}
    gate=raw['unlock_cond'];path=raw['original_path']+'.unlockCond'
    if rank>7 and raw['mastery_conditions']:
        index=min(rank-8,len(raw['mastery_conditions'])-1)
        gate=raw['mastery_conditions'][index]
        path=raw['original_path']+f'.levelUpCostCond[{index}].unlockCond'
    phase=int(gate['phase'].split('_')[-1])
    available=(type(elite) is int and type(level) is int and
               (elite>phase or elite==phase and level>=gate['level']))
    return {'available':available,'original_status':'located','gate':deepcopy(gate),'path':path,
            'native_static_rule_verified':True,'current_hotfix_equivalence_verified':False,
            'actual_runtime_use_verified':None}


def shared_common_reference(profile,elite,level,state):
    """Use only active, valid public1–7 observations from the confirmed run form."""
    state=state or {}
    out={'rank':None,'sources':[],'usable':False,'reason':'当前不是精英0/1的已确认本局形态。',
         'all_skill_qualifications':[],'actual_unread_skill_ranks':None}
    if state.get('scope')!='run' or elite not in (0,1) or type(elite) is not int:
        return out
    confirmed=state.get('run_confirmed_fields',())
    if ('elite' not in confirmed or 'elite' in state.get('invalid_fields',()) or
        state.get('fields',{}).get('elite')!=elite):
        return out
    original=_original(profile)
    if original is None:
        out['reason']='当前形态的技能身份与已封存原件未完整绑定。'
        return out
    if state.get('id') not in (profile['id'],original['profile_key']):
        out['reason']='公共等级来源没有绑定同一干员身份。'
        return out
    invalid=state.get('invalid_skill_ranks',())
    ranks=state.get('skill_ranks',{})
    for skill in range(1,len(profile['skills'])+1):
        if str(skill) in invalid or skill in invalid:
            continue
        rank=ranks.get(str(skill),ranks.get(skill))
        if type(rank) is not int or not 1<=rank<=7:
            continue
        gate=use_qualification(profile,skill,rank,elite,level)
        if gate['available'] is True:
            out['sources'].append({'skill':skill,'rank':rank,'scope':'run_observation',
                                   'use_gate':gate})
    candidates=sorted({s['rank'] for s in out['sources']})
    if not candidates:
        out['reason']='本局没有其它已开放技能的有效公共等级1–7来源；不从账号、专精或招募上限补齐。'
        return out
    if len(candidates)>1:
        out['reason']='本局已读公共等级来源互相冲突，不能选定共享等级。'
        out['candidate_ranks']=candidates
        return out
    out['rank']=candidates[0];out['usable']=True;out['reason']=''
    for skill,current in enumerate(profile['skills'],1):
        rank=ranks.get(str(skill),ranks.get(skill))
        observed=(type(rank) is int and 1<=rank<=min(10,len(current['levels'])) and
                  str(skill) not in invalid and skill not in invalid)
        out['all_skill_qualifications'].append({'skill':skill,'skill_name':current['levels'][0]['name'],
            'rank':rank if observed else out['rank'],
            'rank_source':'run_observation' if observed else 'shared_common_reference',
            'directly_observed':observed,
            'qualification':use_qualification(profile,skill,rank if observed else out['rank'],elite,level),
            'actual_runtime_use_verified':None})
    return out


def format_reference(reference):
    if not reference.get('usable'):
        return reference.get('reason','')
    origins='、'.join('S'+str(row['skill']) for row in reference['sources'])
    lines=[f'公共等级参考{reference["rank"]}来自本局已读{origins}；其它技能尚未直接读取。']
    for row in reference['all_skill_qualifications']:
        permitted=row['qualification']['available']
        qualification='静态使用门成立' if permitted is True else '当前培养门未开放' if permitted is False else '原件门未知'
        origin='本局已读' if row['directly_observed'] else '所选公共等级参考'
        lines.append(f'S{row["skill"]} {row["skill_name"]}：等级{row["rank"]}，{origin}；{qualification}。')
    lines.append('各技能的专精不互相继承；精英2的缺失专精、招募补偿及当前热更新仍未确认，不改写本局记录。')
    return '\n'.join(lines)
