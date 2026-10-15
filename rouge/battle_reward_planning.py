"""Conditional reward references from fixed declarations, never actual grants."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from .battle_preview import battle_data, display_cell
from .base_settlement_planning import stage_base_rewards,stage_reward_text
from .rare_reward_sources import rare_stage_reward_sources
from .moving_reward_reference import moving_reward_rule

MOVING='enemy_2152_shezlc'

@lru_cache(maxsize=1)
def reward_data():
    return json.loads((Path(__file__).with_name('data')/'battle-reward-reference.json').read_text(encoding='utf8'))

def _rule(entity,level):
    if entity==MOVING:
        return moving_reward_rule(level.get('moving_enemy_refs'))
    return deepcopy(reward_data()['rules'][entity])

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
    rare=rare_stage_reward_sources(stage_id)
    rows.extend(rare['rows'])
    return {'stage_id':stage_id,'stage_name':stage['name'],'source':deepcopy(level['source']),
        'rows':rows,'random_groups':deepcopy(level['random_groups']),
        'rare_random_groups':deepcopy(rare['random_groups']),
        'rare_source_mimic_ids':rare['mimic_source_ids'],
        'unreferenced_mimic_ids':rare['unreferenced_mimic_ids'],
        'inspected_containers':list(level['inspected_containers']),
        'initial_records':deepcopy(level['initial_records']),
        'actual_reward_total':None,'complete_settlement_pool_known':False,
        'complete_random_scrap_pool_known':False,'runtime_spawn_coverage_known':False,
        'probability':None,'limits':list(data['limits'])}

def reward_source_text(result,row=None,technical=False):
    lines=['条件奖励资料：'+result['stage_name'],
        ('固定来源覆盖：预置装置、主队列与条件分支；这些是配置引用，实际出现、触发及领取未知。' if technical else
         '下面列出可能提供奖励的目标和领取条件；不保证目标出现，也不表示已经领取。'),
        '本关实际奖励总量与完整结算池：未知。']
    rows=[row] if row is not None else result['rows']
    if not technical:lines.append('当前列出'+str(len(rows))+'条奖励资料；不同候选、位置和来源不能相加为实际总奖励。')
    for reference in rows:
        lines += ['',reference['name']]
        cell=reference['display_cell']
        position_label=('原路线名义起点' if reference['kind']=='rare_enemy_action' else '预置资料位置') if technical else '地图参考位置'
        lines.append(f"{position_label}：第{cell['row']+1}行、第{cell['col']+1}列。" if cell else
            '位置：未绑定；不按分支routeIndex推断。' if technical else '位置：未绑定；不能借用其他目标的路线定位。')
        rule=reference['rule']
        # Put the useful outcome before source/activation details. Resource
        # types and every condition remain separate; nothing is totalled.
        for outcome in rule['outcomes']:
            amount=outcome['quantity'];resource={'gold':'源石锭','random_scrap':'随机零件','random_relic':'收藏品'}.get(outcome['resource'],'未核验资源')
            value='数量未证' if amount is None else f'{amount:+d}{resource}'
            lines.append('条件：'+outcome['condition_label']+'；数量参考 '+value+'。')
            if outcome.get('cost_quantity') is not None:
                lines.append(f"开启费用参考：{outcome['cost_quantity']}点部署费用；不等于源石锭或探索行动力。随机零件数量1，完整候选池未知。")
        if reference['kind']=='rare_enemy_action':
            levels=reference['rule']['referenced_levels']
            lines.append('固定敌人级别候选：'+('、'.join(str(n) for n in levels) if levels else '未知')+'；实际生成级别与击倒/领取未知。')
            group=reference.get('candidate_group_reference')
            if group:
                names=[m.get('name') or ('空候选' if m['is_empty_key'] else '其他原配置候选') for m in group['members']]
                lines.append('同一配置组全部候选：'+' / '.join(names)+'；这些不是同时出现的证明，不能相加为实际收藏品数。')
            lines.append('数量为单个敌人的文档条件参考；原路线位置也只是固定资料，不表示当前已生成或实际移动路径。')
        if reference['kind']=='moving_enemy_action':
            lines.append('两个结果互斥：击倒获得与漏过损失不能相加，也不能按出现条件的记录条数当成敌人数量。')
        if reference['kind']=='predefined_device':
            if technical:
                labels={'predefines':'普通预置容器','hardPredefines':'额外预置容器（实际适用未知）'}
                lines.append(labels.get(reference['container'],reference['container'])+'；激活引用 '+str(len(reference['activation_references']))+' 条，引用数不是实际生成数。')
            else:lines.append('是否出现或可领取：未确认；出现条件记录数不是实际生成数。')
            if reference['explicit_branch_id']:
                lines.append('原件明确声明关联分支；配置'+('存在' if reference['branch_configuration_exists'] else '未找到')+'，实际触发、路线数组与时钟未知。' if technical else
                    '此目标还有额外出现条件；是否触发、出现位置与时间仍未确认。')
        if rule.get('quantity_scope_notice'):lines.append(rule['quantity_scope_notice'])
        if reference['entity_id']=='trap_323_shsbox':
            lines.append('箱型装置与召出的移动恶笼草为不同目标；不能把两条来源各算一次10源石锭。移动实体级别与结算执行仍需核验。')
        if technical:
            lines += ['原实体：'+reference['entity_id'],'原件位置：'+reference['source_selector']]
            if reference.get('explicit_branch_id'):lines.append('原branch_id：'+reference['explicit_branch_id'])
            source=rule['quantity_source']
            if source:
                lines.append('数量来源：'+source['url'])
                if reference['entity_id']==MOVING:
                    lines.append('已核对文档版本：'+source['fixed_url'])
            else:lines.append('数量来源：固定来源未通过核对；数量未知。')
    if not rows:lines.append('固定来源中未找到已接入的奖励实体；不代表当前关卡没有奖励或动态生成。')
    base_text=stage_reward_text(stage_base_rewards(result['stage_id']))
    if not technical:
        base_text='\n'.join(line for line in base_text.splitlines() if not line.startswith('基础表来源：'))
        base_text=base_text.replace('此精确原ID的基础来源范围尚未绑定。','这关的基础奖励资料尚未确认。')
    lines += ['',base_text,*result['limits']]
    if technical:
        lines += ['原关卡来源：'+result['source']['url'],'已检查：'+', '.join(result['inspected_containers'])]
    return '\n'.join(lines)
