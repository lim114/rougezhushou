"""Low-star single-hit references bound to fixed stage candidates and grades."""
from copy import deepcopy
from .catalog import catalog,stage_previews
from .supplemental_run import run_skill_reference
from .supplemental_comparison import comparison_rows,format_comparison


def enemy_defaults(environment):
    sid='ro6_n_1_1';records=stage_previews()[sid]['possible_enemies']
    grade=(environment.get('run_config') or {}).get('difficulty') or {}
    value=grade.get('value',4)
    if type(value) is not int or not 0<=value<=15:value=4
    return {'stage_id':sid,'enemies':[{'enemy_id':e['id'],'level':e['level']} for e in records[:3]],
            'grades':[value], 'orb_mode':'unknown'}


def compare_fixed_enemies(operator_preview,environment,preview):
    if type(preview) is not dict or set(preview)!={'stage_id','enemies','grades','orb_mode'}:
        raise ValueError('需要stage_id、enemies、grades、orb_mode。')
    sid=preview['stage_id'];grades=preview['grades'];selections=preview['enemies']
    if type(sid) is not str or sid not in stage_previews():raise ValueError('需要固定关卡敌人档案。')
    if (type(grades) is not list or not 1<=len(grades)<=6 or
        any(type(g) is not int or not 0<=g<=15 for g in grades) or len(set(grades))!=len(grades)):
        raise ValueError('grades需要1–6个不重复的0–15整数。')
    mode=preview['orb_mode']
    if type(mode) is not str or mode not in ('unknown','active_same_column','active_other_column'):
        raise ValueError('源阶方情景仅支持未知、行动同列或行动异列。')
    if type(selections) is not list or not 1<=len(selections)<=20:raise ValueError('需要1–20个固定候选目标。')
    records=[];seen=set()
    for selection in selections:
        if (type(selection) is not dict or set(selection)!={'enemy_id','level'} or
            type(selection['enemy_id']) is not str or type(selection['level']) is not int):
            raise ValueError('每个目标需原表enemy_id与整数level。')
        key=(selection['enemy_id'],selection['level'])
        matches=[e for e in stage_previews()[sid]['possible_enemies'] if (e['id'],e['level'])==key]
        if len(matches)!=1 or key in seen:raise ValueError('目标需唯一匹配关卡引用且不能重复。')
        records.append(matches[0]);seen.add(key)
    original=deepcopy(operator_preview);environment=deepcopy(environment)
    run_skill_reference(original,environment) # Validate cultivation and raw run input first.
    rows=[];variants=[]
    for record in records:
        baseline=None
        for grade in grades:
            env=deepcopy(environment)
            config=env['run_config']
            if config is None:config=env['run_config']={}
            difficulty=deepcopy(config.get('difficulty') or {})
            difficulty.update(value=grade,source='手动局外候选目标对照');difficulty.pop('captured_at',None)
            config['difficulty']=difficulty
            target={'stage_id':sid,'enemy_id':record['id'],'level':record['level']}
            if record['id']=='enemy_2148_shorbb':target['orb_mode']=mode
            result=run_skill_reference(original,env,target_enemy=target)
            if baseline is None:baseline=result
            labels={'enemy_name':record['name'],'grade':grade,'enemy_id':record['id'],'level':record['level']}
            rows.extend(comparison_rows(result,baseline,**labels))
            for key,name,unit in [('maxHp','候选生命参考','生命'),('atk','候选攻击参考','攻击力'),
                                  ('def','候选防御参考','防御力'),('magicResistance','候选法抗参考','法抗')]:
                value=result['target_enemy']['stats'][key];base=baseline['target_enemy']['stats'][key]
                rows.append({**labels,'key':'enemy:'+key,'name':name,'value':value,
                             'base_value':base,'delta':value-base,'unit':unit})
            variants.append({**labels,'result':result})
    return {'operator_preview':original,'environment':environment,'preview':deepcopy(preview),
            'stage_name':catalog()['stages'][sid]['name'],'variants':variants,'rows':rows,
            'notes':['每个敌人以列表首个声明难度为比较基准；其他培养、藏品和区域保持打开时条件。',
                     '目标覆盖手动防御和法抗；每项修正仅按既有已证环境引擎计算。',
                     '候选敌人不保证出场，候选生命不代表已观察的随机出生分支；完整分支与来源在报告中保留。',
                     '动态阶段、脚本、实际获取/命中/击杀时钟仍未知，不计算真实周期或击杀概率。']}


def format_fixed_enemies(result):
    lines=[result['stage_name']+' · 低星固定候选目标对照',format_comparison(result)]
    import json
    for v in result['variants']:
        lines.append(v['enemy_name']+' · '+str(v['grade'])+'级目标来源与已计修正：'+
                     json.dumps(v['result']['target_enemy'],ensure_ascii=False))
    return '\n'.join(lines)
