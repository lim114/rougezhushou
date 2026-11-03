"""Offline same-cultivation module upgrades from existing verified token rules."""
from copy import deepcopy

from .catalog import catalog,operator_attributes
from .summons import (module_rules,token_attributes,token_concurrent_limit,
                      token_cost_reference)
from .token_counts import token_count_reference

STAT_FIELDS=('hp','attack','defense','resistance','deployment_cost','interval')


def compare_token_module(operator,cultivation,module_id=None):
    profile=catalog()['operators'][operator]
    # Only the current cultivation is consumed; unrelated combat/state data is opaque.
    allowed=('elite','level','trust','potential')
    training={k:deepcopy(v) for k,v in cultivation.items() if k in allowed}
    operator_attributes(operator,**training)
    training.setdefault('elite',2)
    if training.get('level') is None:training['level']=profile['phases'][training['elite']]['max_level']
    module=next((m for m in profile['modules'] if m['id']==module_id),None)
    if module_id is not None and module is None:raise ValueError('模组不属于当前干员。')
    tokens=[]
    for identity,token in profile.get('tokens',{}).items():
        base_scenario={'operator':operator,**training,'module_id':None,'module_level':0}
        base_stats=token_attributes(profile,base_scenario,identity)
        base={k:base_stats[k] for k in STAT_FIELDS}
        rule=next((r for r in module_rules().values() if r['operator']==operator and r['token_id']==identity),None)
        base_counts=token_count_reference(profile,base_scenario,identity)
        base['held_limit']=base_counts['held_limit'] if base_counts else rule['base_held_limit'] if rule else None
        base['concurrent_limit']=token_concurrent_limit(profile,base_scenario,identity)
        stages=[{'module_level':0,'state':'base','values':base,'differences':{},'verified_fields':list(STAT_FIELDS),
            'source':None,'count_reference':deepcopy(base_counts)}]
        for level in range(1,len(module['levels'])+1) if module else ():
            scenario={**base_scenario,'module_id':module_id,'module_level':level}
            stats=token_attributes(profile,scenario,identity)
            reference=stats.get('module_reference')
            cost_reference=token_cost_reference(profile,scenario,identity)
            unlocked=training['elite']>=module['unlock_elite'] and training['level']>=module['unlock_level']
            counts=token_count_reference(profile,scenario,identity) if unlocked else None
            # Known effects are a partial projection. Do not treat a missing
            # rule as zero effect or inherit an operator's equipment stats.
            verified=set()
            if reference:verified.update(('hp','deployment_cost','held_limit','concurrent_limit'))
            if cost_reference:verified.add('deployment_cost')
            if counts:verified.update(('held_limit','concurrent_limit'))
            values={k:None for k in base}
            for key in verified:
                values[key]=((counts or reference)['held_limit'] if key=='held_limit' else
                    (counts or reference)['concurrent_limit'] if key=='concurrent_limit' else stats[key])
            state='locked' if not unlocked else 'partial_reference' if verified else 'unverified'
            stages.append({'module_level':level,'state':state,'values':values,
                'verified_fields':sorted(verified),
                'differences':{k:values[k]-base[k] for k in verified if base[k] is not None and values[k] is not None},
                'source':deepcopy(reference or cost_reference),'count_reference':deepcopy(counts)})
        tokens.append({'token_id':identity,'name':token['name'],'stages':stages,
                       'actual_presence':None,'actual_alive_seconds':None})
    return {'operator':operator,'operator_name':profile['name'],'cultivation':training,
        'module_id':module_id,'module_name':module['name'] if module else None,'tokens':tokens,
        'scope':'same_cultivation_known_token_module_fragments',
        'notes':['各列使用相同精英和等级；基础列仅为独立实体的培养参数，不证明召唤资格、实际在场或技能覆盖。',
                 '升级列只展示已核验的模组效果片段；未接入的属性与数量限制保持未知，不表示模组没有效果。',
                 '数量行只计入对应来源已核验的潜能隐藏天赋；技能、藏品、分队和未知模组效果不在本表叠加，本体培养加成不会自动流入独立实体。',
                 '库存与每类在场上限各自列出，不推算地块、全局部署位或实际数量。',
                 '沿用项目固定版本资料；当前游戏热更新、完整面板、实际创建与退出仍需独立核验。']}
