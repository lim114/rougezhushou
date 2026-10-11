"""Low-star declared budgets, excluding expectations and continuous regen."""
import json
from copy import deepcopy
from .supplemental_run import run_skill_reference
from .supplemental_skills import supplemental_profiles
from .damage_budget import _damage_budget,damage_sources,format_damage_budget
from .healing_budget import _healing_budget,healing_sources,format_healing_budget


def budget_reference(operator_preview,environment):
    result=run_skill_reference(operator_preview,environment)
    components=[]
    for row in result['rows']:
        dtype={'物理伤害':'physical','法术伤害':'magic'}.get(row['unit'])
        if row['name'] in ('普通单次治疗','技能单次治疗'):dtype='healing'
        components.append({'name':row['name'],'per_hit':row['value'],'damage_type':dtype})
    return {'components':components,'estimate':{'notes':[
        *result['notes'],*result['attribute_resolution']['warnings']]},'supplemental':result}


def damage_defaults(operator_preview,environment):
    sources=damage_sources(budget_reference(operator_preview,environment))
    if not sources:raise ValueError('当前干员没有已知的单次伤害预算来源。')
    return {'targets':[{'id':'目标甲','hp':3000,'defense':operator_preview['enemy_defense'],
                       'resistance':operator_preview['enemy_resistance']}],
            'events':[{'at_seconds':0,'target':'目标甲','source':sources[0]['id']}]}


def healing_defaults(operator_preview,environment):
    reference=budget_reference(operator_preview,environment);sources=healing_sources(reference)
    if not sources:raise ValueError('当前干员没有已知的单次治疗预算来源。')
    self_heal=supplemental_profiles()['operators'][operator_preview['operator']]['kind']=='self_heal'
    maximum=reference['supplemental']['attributes']['hp'] if self_heal else 3000
    recipient='自身' if self_heal else '友方甲'
    return {'recipients':[{'id':recipient,'max_hp':maximum,'hp':max(0,maximum-operator_preview['missing_hp'])}],
            'events':[{'at_seconds':0,'recipient':recipient,'kind':'heal','source':sources[-1]['id']}]}


def declared_damage_budget(operator_preview,environment,preview):
    frozen=deepcopy(environment)
    result=_damage_budget(deepcopy(operator_preview),preview,lambda p:budget_reference(p,frozen))
    result['environment']=frozen
    result['notes'].extend(['期望伤害与未知天赋组合不提供预算来源；克洛丝已知分支仅为用户声明的条件，未抽取随机序列。',
                            '来源名称和每目标单次数值在报告中列出；同一条事件只记一个来源，不能重复叠加普通攻击与其期望。'])
    return result


def declared_healing_budget(operator_preview,environment,preview):
    frozen=deepcopy(environment);reference=budget_reference(operator_preview,frozen)
    if supplemental_profiles()['operators'][operator_preview['operator']]['kind']=='self_heal':
        recipients=preview.get('recipients') if type(preview) is dict else None
        maximum=reference['supplemental']['attributes']['hp']
        if (type(recipients) is not list or len(recipients)!=1 or type(recipients[0]) is not dict or
            recipients[0].get('id')!='自身' or type(recipients[0].get('max_hp')) not in (int,float) or
            recipients[0]['max_hp']!=maximum):
            raise ValueError('卡缇仅可对自身建立预算，id需为自身，max_hp需为本次计算的最大生命。')
    result=_healing_budget(deepcopy(operator_preview),preview,lambda p:reference)
    result['environment']=frozen
    result['notes'].append('持续生命回复不当作单次治疗；卡缇仅对自身，芙蓉友方生命为局外声明，不判断真实受疗资格。')
    return result


def format_supplemental_damage_budget(result):
    return format_damage_budget(result)+'\n冻结本局条件：'+json.dumps(result['environment'],ensure_ascii=False)


def format_supplemental_healing_budget(result):
    return format_healing_budget(result)+'\n冻结本局条件：'+json.dumps(result['environment'],ensure_ascii=False)
