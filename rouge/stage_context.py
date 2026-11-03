"""Exact fixed-stage entry references, separate from server or forced-entry rules."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path


@lru_cache(maxsize=1)
def context_data():
    return json.loads((Path(__file__).with_name('data')/'stage-context-reference.json').read_text(encoding='utf8'))


def stage_context(stage_id,*,node_type=None,floor=None,special_region=False,difficulty=None,entry_mode=None):
    if floor is not None and (type(floor) is not int or floor not in range(1,7)):
        raise ValueError('主层需要1–6的整数。')
    if difficulty is not None and (type(difficulty) is not int or difficulty not in range(16)):
        raise ValueError('保密等级需要0–15整数或留空。')
    if type(special_region) is not bool:raise ValueError('特殊区域标志需要布尔值。')
    if entry_mode not in (None,'natural','content'):raise ValueError('入口需要natural、content或留空。')
    data=context_data();entry=data['stages'].get(stage_id)
    if entry is None:return None
    result=deepcopy(entry);checks=[]
    for rule in result['conditions']:
        applies=node_type==rule['node_type'] and (rule['entry_scope']=='shop_challenge' or entry_mode=='natural')
        value=None;reason='当前入口来源未明确；不把自然节点条件推广到强制内容入口。'
        if applies:
            if rule['kind']=='main_floor':
                value=None if special_region or floor is None else floor in rule['allowed']
                reason='特殊区域或主层未知，保留候选。' if value is None else '核对可靠主层与精确入口的已列范围。'
            elif rule['kind']=='difficulty':
                value=None if difficulty is None else difficulty>=rule['minimum']
                reason='保密等级未明确，保留候选。' if value is None else '核对自然节点保密等级门槛。'
        checks.append({**rule,'matches':value,'applicable':applies,'reason':reason})
    values=[r['matches'] for r in checks]
    status='excluded' if False in values else 'matched' if values and all(v is True for v in values) else 'unknown'
    result.update(status=status,checks=checks,declared_main_floor=floor,special_region=special_region,
                  node_type=node_type,entry_mode=entry_mode,actual_entry_verified=False,server_eligibility=None,
                  source=deepcopy(data['source']),limitations=deepcopy(data['limitations']))
    return result


def stage_context_text(result):
    if not result:return ''
    statuses={'matched':'已列条件相符','unknown':'资格未确认','excluded':'已列条件不符'}
    lines=['入口分类：'+result['label'],'入口条件：'+statuses[result['status']],
           '精确原关卡：'+result['stage_id']+'；当前服务器资格与实际触发仍未知。']
    for row in result['checks']:
        state='相符' if row['matches'] is True else '不符' if row['matches'] is False else '未知'
        lines += [row['description']+'；核对结果：'+state+'。',row['reason']]
    if not result['checks']:lines.append('此入口的层数适用规则未取得；继续保留候选。')
    lines += ['入口依据：'+result['entry_reference'],
              '固定原目录的层数字段仍未记录；社区入口条件另列参考，不改写原件。',
              '原具名池绑定与层数条件是两项证据；不从ID后缀、同名或NEXT反推。',
              '资料版本：固定游戏原件 '+result['source']['game_commit']+'；社区修订 '+str(result['source']['community_revision'])+'。',
              result['source']['community_pinned_url']]
    lines.extend(result['limitations'])
    return '\n'.join(lines)
