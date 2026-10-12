"""Conditional reward references from fixed declarations, never actual grants."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from .battle_preview import battle_data, display_cell

MOVING='enemy_2152_shezlc'

@lru_cache(maxsize=1)
def reward_data():
    return json.loads((Path(__file__).with_name('data')/'battle-reward-reference.json').read_text(encoding='utf8'))

def _rule(entity,level):
    rule=deepcopy(reward_data()['rules'][entity])
    if entity==MOVING:
        refs=level['moving_enemy_refs'];values={r['raw'].get('level') for r in refs}
        rule['referenced_levels']=sorted(v for v in values if type(v) is int)
        rule['documented_base_level_matches_reference']=values=={0}
        rule['action_level_binding_unique']=len(values)==1
        if values!={0}:
            for outcome in rule['outcomes']:outcome['quantity']=None
            rule['quantity_scope_notice']='该关卡引用级别不是唯一0；级别1/2或多级别奖励数量未证。'
    return rule

def stage_reward_sources(stage_id):
    if not isinstance(stage_id,str) or not stage_id:raise ValueError('固定关卡ID需要非空文本。')
    data=reward_data();stage=battle_data()['stages'].get(stage_id);index=data['stages'].get(stage_id)
    if stage is None or index is None:raise ValueError('没有此固定战斗奖励来源。')
    level=data['levels'][index['level_key']]
    if stage['level_source']['sha256']!=level['source']['sha256']:raise ValueError('奖励来源与固定战斗版本不同。')
    declarations={r['id']:r for r in level['declarations']};rows=[]
    nr,nc=len(stage['map']),len(stage['map'][0])
    for declaration in level['declarations']:
        links=[r for r in level['actions'] if declaration['id'] in r['definition_ids']]
        branch=declaration['explicit_branch_id'];branch_actions=[r for r in level['actions']
            if branch and r['queue_id'].startswith('$.branches['+json.dumps(branch)+'].')]
        rows.append({'id':declaration['id'],'kind':'predefined_device','entity_id':declaration['entity_id'],
            'name':data['rules'][declaration['entity_id']]['name'],'alias':declaration['alias'],
            'container':declaration['container'],'raw':deepcopy(declaration['raw']),
            'source_selector':declaration['source_selector'],
            'display_cell':display_cell(declaration['raw'].get('position'),nr,nc),
            'configured_hidden':declaration['raw'].get('hidden'),
            'activation_references':deepcopy(links),'explicit_branch_id':branch,
            'branch_configuration_exists':declaration['branch_configuration_exists'],
            'explicit_branch_reward_actions':deepcopy(branch_actions),
            'rule':_rule(declaration['entity_id'],level),'actual_activation':None,
            'actual_outcome':None,'actual_reward':None,'quantity_is_total':False})
    for action in level['actions']:
        if action['raw'].get('actionType')!='SPAWN' or action['raw'].get('key')!=MOVING:continue
        rows.append({'id':action['id'],'kind':'moving_enemy_action','entity_id':MOVING,
            'name':'恶笼草（移动敌人）','raw':deepcopy(action['raw']),
            'source_selector':action['source_selector'],'queue_id':action['queue_id'],
            'display_cell':None,'rule':_rule(MOVING,level),'actual_activation':None,
            'actual_outcome':None,'actual_reward':None,'quantity_is_total':False})
    return {'stage_id':stage_id,'stage_name':stage['name'],'source':deepcopy(level['source']),
        'rows':rows,'random_groups':deepcopy(level['random_groups']),
        'inspected_containers':list(level['inspected_containers']),
        'initial_records':deepcopy(level['initial_records']),
        'actual_reward_total':None,'complete_settlement_pool_known':False,
        'complete_random_scrap_pool_known':False,'runtime_spawn_coverage_known':False,
        'probability':None,'limits':list(data['limits'])}

def reward_source_text(result,row=None,technical=False):
    lines=['条件奖励资料：'+result['stage_name'],
        '固定来源覆盖：预置装置、主队列与条件分支；这些是配置引用，实际出现、触发及领取未知。',
        '本关实际奖励总量与完整结算池：未知。']
    rows=[row] if row is not None else result['rows']
    for reference in rows:
        lines += ['',reference['name']]
        cell=reference['display_cell']
        lines.append(f"预置资料位置：第{cell['row']+1}行、第{cell['col']+1}列。" if cell else '位置：未绑定；不按分支routeIndex推断。')
        if reference['kind']=='predefined_device':
            labels={'predefines':'普通预置容器','hardPredefines':'额外预置容器（实际适用未知）'}
            lines.append(labels.get(reference['container'],reference['container'])+'；激活引用 '+str(len(reference['activation_references']))+' 条，引用数不是实际生成数。')
            if reference['explicit_branch_id']:
                lines.append('原件明确声明关联分支；配置'+('存在' if reference['branch_configuration_exists'] else '未找到')+'，实际触发、路线数组与时钟未知。')
        rule=reference['rule']
        for outcome in rule['outcomes']:
            amount=outcome['quantity'];resource='源石锭' if outcome['resource']=='gold' else '随机零件'
            value='数量未证' if amount is None else f'{amount:+d}{resource}'
            lines.append('条件：'+outcome['condition_label']+'；数量参考 '+value+'。')
            if outcome.get('cost_quantity') is not None:
                lines.append(f"开启费用参考：{outcome['cost_quantity']}点部署费用；不等于源石锭或探索行动力。随机零件数量1，完整候选池未知。")
        if rule.get('quantity_scope_notice'):lines.append(rule['quantity_scope_notice'])
        if reference['entity_id']=='trap_323_shsbox':
            lines.append('箱型装置与召出的移动恶笼草为不同目标；不能把两条来源各算一次10源石锭。移动实体级别与结算执行仍需核验。')
        if technical:
            lines += ['原实体：'+reference['entity_id'],'原件位置：'+reference['source_selector']]
            if reference.get('explicit_branch_id'):lines.append('原branch_id：'+reference['explicit_branch_id'])
            source=rule['quantity_source'];lines.append('数量来源：'+source['url'])
    if not rows:lines.append('固定来源中未找到已核验的这五类实体；不代表当前关卡没有奖励或动态生成。')
    lines += ['',*result['limits']]
    if technical:
        lines += ['原关卡来源：'+result['source']['url'],'已检查：'+', '.join(result['inspected_containers'])]
    return '\n'.join(lines)
