"""Frozen-run comparisons; each row is a separate metric, never a summed cast."""
import json
from copy import deepcopy
from .supplemental_run import run_skill_reference


def metrics(result):
    rows=[]
    for key,label,unit in [('hp','常态生命','生命'),('attack','常态攻击','攻击力'),
                           ('defense','常态防御','防御力')]:
        rows.append({'key':'attribute:'+key,'name':label,'value':result['attributes'][key],'unit':unit})
    for key,label,unit in [('resistance','法抗','法抗'),('attack_speed','攻速','官方攻速单位'),
                          ('redeploy_seconds','再部署参数','秒'),('block_count','阻挡','个')]:
        rows.append({'key':'attribute:'+key,'name':label,'value':result['run_attributes'][key],'unit':unit})
    rows.append({'key':'deployment','name':'预计普通首次部署费用',
                 'value':result['deployment_reference']['estimated_cost'],'unit':'部署费用'})
    for key,label in [('cost_parameter','技力消耗参数'),('initial_parameter','部署预置技力参数'),
                      ('initial_requirement','初次技力缺口'),('end_return_parameter','标称结束返技力'),
                      ('recharge_requirement','结束后技力缺口')]:
        rows.append({'key':'sp:'+key,'name':label,'value':result['sp_reference'][key],'unit':'技力'})
    rows.extend({'key':'skill:'+r['name'],'name':r['name'],'value':r['value'],'unit':r['unit']}
                for r in result['rows'])
    return rows


def comparison_rows(result,baseline,**labels):
    previous={r['key']:r['value'] for r in metrics(baseline)} if baseline else {}
    rows=[]
    for metric in metrics(result):
        base=previous.get(metric['key']);value=metric['value']
        rows.append({**labels,**metric,'base_value':base,
                     'delta':value-base if value is not None and base is not None else None})
    return rows


def compare_ranks(operator_preview,environment,preview):
    if type(preview) is not dict or set(preview)!={'ranks'}:
        raise ValueError('技能等级对照需要ranks列表。')
    ranks=preview['ranks']
    if (type(ranks) is not list or not 1<=len(ranks)<=7 or
        any(type(r) is not int or not 1<=r<=7 for r in ranks) or len(set(ranks))!=len(ranks)):
        raise ValueError('ranks需要1–7个不重复的1–7整数。')
    original=deepcopy(operator_preview);environment=deepcopy(environment)
    baseline=run_skill_reference(original,environment)
    variants=[];rows=[]
    for rank in ranks:
        result=run_skill_reference({**original,'skill_rank':rank},environment)
        variants.append({'rank':rank,'result':result})
        rows.extend(comparison_rows(result,baseline,rank=rank))
    return {'operator_preview':original,'environment':environment,'preview':deepcopy(preview),
            'baseline':baseline,'variants':variants,'rows':rows,
            'notes':['每个分项独立比较，不能将不同伤害分支、期望、治疗和面板相加。',
                     '差值相对打开时当前技能等级；其他培养、目标及本局条件全部冻结。',
                     '这是局外参数方案，不证明精零高等级技能使用资格、时序、周期或材料收益。']}


def format_comparison(result):
    val=lambda v:'未知' if v is None else format(v,'.8g') if type(v) in (int,float) else str(v)
    lines=['冻结干员条件：'+json.dumps(result['operator_preview'],ensure_ascii=False),
           '冻结本局条件：'+json.dumps(result['environment'],ensure_ascii=False),
           '对照方案：'+json.dumps(result['preview'],ensure_ascii=False)]
    for row in result['rows']:
        label='；'.join(str(row[k]) for k in ('rank','proposal','enemy_name','grade') if k in row)
        lines.append(f"{label} · {row['name']}：{val(row['value'])} {row['unit']}；基准{val(row['base_value'])}；差值{val(row['delta'])}")
    for variant in result['variants']:
        if variant.get('error'):lines.append(variant['error'])
        if variant.get('result'):lines.extend(variant['result']['attribute_resolution']['warnings'])
    return '\n'.join([*lines,*result['notes']])
