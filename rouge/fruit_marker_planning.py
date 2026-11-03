"""Read-only declared 藏果地 flow; never infer observations or mutate a run."""
from copy import deepcopy
from functools import lru_cache
import json
import re
from pathlib import Path

MARKERS = {'fruit': '藏果地', 'civilization': '文明之烬', 'none': '无标记（声明）', 'unknown': '未知'}
STATUSES = {'matched': '声明满足来源条件', 'excluded': '声明不满足该条件', 'unknown': '条件未知', 'conflict': '声明与来源冲突'}
NODE_TYPES = ('其它节点', '失与得', '曲折密道')


@lru_cache(maxsize=1)
def marker_reference():
    return json.loads((Path(__file__).parent / 'data' / 'fruit-marker-reference.json').read_text(encoding='utf-8'))


def _id(value, label, *, optional=False):
    if value is None and optional:
        return
    if type(value) is not str or not value.strip() or len(value) > 120 or any(ord(c) < 32 for c in value):
        raise ValueError(label + '需要1–120字符的明确声明身份。')


def _tri(value, label):
    if value is not None and type(value) is not bool:
        raise ValueError(label + '需要布尔或null；文字和整数不能当作确认。')


def _marker(value):
    if type(value) is not str or value not in MARKERS:
        raise ValueError('标记状态需要fruit、civilization、none或unknown。')


def _status(values):
    if False in values:
        return 'excluded'
    return 'matched' if all(v is True for v in values) else 'unknown'


def declared_marker_flow(node, events=None, *, relic_owned=None, new_region_entered=None):
    """Evaluate explicit proposals. Every ``actual_*`` result remains unknown.

    Node has node_id/map_id/node_type/marker/paired_node_id. A placement has
    performed and covers_civilization declarations. A visit has performed,
    mode, entry_node_id, exit_node_id, from_other_end and marker_after.
    The corridor rule requires an explicit other-end statement and exact
    identities; different IDs alone never establish a pairing or traversal.
    """
    if type(node) is not dict or set(node) != {'node_id', 'map_id', 'node_type', 'marker', 'paired_node_id'}:
        raise ValueError('节点需要node_id、map_id、node_type、marker、paired_node_id五项声明。')
    _id(node['node_id'], '标记节点'); _id(node['map_id'], '声明地图')
    _id(node['paired_node_id'], '另一端', optional=True)
    if node['paired_node_id'] == node['node_id']:
        raise ValueError('另一端不能和标记节点使用相同身份。')
    if node['node_type'] not in NODE_TYPES:
        raise ValueError('当前节点类别只接受其它节点、失与得或曲折密道。')
    if node['node_type'] != '曲折密道' and node['paired_node_id'] is not None:
        raise ValueError('另一端只用于曲折密道声明。')
    _marker(node['marker']); _tri(relic_owned, '迷藏持有'); _tri(new_region_entered, '进入新区域')
    events = [] if events is None else events
    if type(events) is not list or len(events) > 100:
        raise ValueError('局外流程需要至多100个声明步骤。')
    data = marker_reference(); current = node['marker']; rows = []
    for index, event in enumerate(events):
        if type(event) is not dict or event.get('kind') not in ('place', 'visit'):
            raise ValueError('步骤类别只接受place或visit。')
        kind = event['kind']
        keys = ({'kind', 'node_id', 'performed', 'covers_civilization'} if kind == 'place' else
                {'kind', 'node_id', 'performed', 'mode', 'entry_node_id', 'exit_node_id', 'from_other_end', 'marker_after'})
        if set(event) != keys or event['node_id'] != node['node_id']:
            raise ValueError('步骤字段需完整且精确绑定当前标记节点，不能沿用另一节点的旧声明。')
        _tri(event['performed'], '完成步骤'); before = current
        row = {'index': index + 1, 'kind': kind, 'node_id': node['node_id'], 'marker_before': before,
               'input': deepcopy(event), 'condition_status': 'unknown', 'marker_after_reference': 'unknown',
               'marker_after_declared': None, 'admitted_marker_after': 'unknown', 'warnings': [],
               'actual_marker_after': None, 'actual_triggered': None, 'actual_reward_received': None,
               'actual_reward_quantity': None, 'source_condition_reward_quantity': None,
               'documented_reward_candidates': [], 'reward_server_membership_known': False}
        if kind == 'place':
            _tri(event['covers_civilization'], '文明之烬覆盖')
            if event['covers_civilization'] is True and (node['node_type'] != '失与得' or before != 'civilization'):
                raise ValueError('文明之烬覆盖正声明必须绑定失与得和明确的覆盖前文明之烬。')
            if event['performed'] is False:
                row.update(condition_status='excluded', marker_after_reference=before)
                current = before
            elif event['performed'] is None:
                current = 'unknown'
            elif before == 'civilization':
                if event['covers_civilization'] is True:
                    current = 'fruit'; row.update(condition_status='matched', marker_after_reference='fruit')
                else:
                    current = 'unknown'
                    row['warnings'].append('未声明文明之烬覆盖发生；不推出藏果地独占该节点，也不保留为已证共存。')
            else:
                current = 'fruit'; row.update(condition_status='matched', marker_after_reference='fruit')
            row['warnings'].append('标记放置是用户独立声明；持有迷藏或进入新区域都不证明标记实际生成。')
        else:
            if event['mode'] not in ('explore', 'corridor'):
                raise ValueError('探索模式只接受explore或corridor。')
            _id(event['entry_node_id'], '入口', optional=True); _id(event['exit_node_id'], '钻出端', optional=True)
            _tri(event['from_other_end'], '另一端进入')
            if event['marker_after'] is not None:
                _marker(event['marker_after'])
            marker_gate = None if before == 'unknown' else before == 'fruit'
            if event['mode'] == 'explore':
                if node['node_type'] == '曲折密道':
                    row['warnings'].append('曲折密道需按另一端进入/钻出专门条件核对；普通探索不能补齐密道动作。')
                    status = _status([marker_gate, event['performed'], None])
                else:
                    if event['entry_node_id'] is not None or event['exit_node_id'] is not None or event['from_other_end'] is not None:
                        raise ValueError('普通探索不接受密道入口/出口或另一端声明。')
                    status = _status([marker_gate, event['performed']])
            else:
                if node['node_type'] != '曲折密道':
                    raise ValueError('密道钻出只适用于曲折密道。')
                if event['from_other_end'] is True:
                    if node['paired_node_id'] is None or event['entry_node_id'] != node['paired_node_id'] or event['exit_node_id'] != node['node_id']:
                        raise ValueError('另一端正声明须同时给出独立配对端、精确入口和标记端钻出身份。')
                positive = _status([marker_gate, event['performed'], event['from_other_end'],
                                    node['paired_node_id'] is not None if event['from_other_end'] is True else None])
                # A failed special-case condition cannot prove other corridor entries yield no reward.
                status = positive if event['from_other_end'] is not False else _status([marker_gate, event['performed'], None])
                row['corridor_special_condition_status'] = positive
                if status == 'matched':
                    row['marker_after_reference'] = 'fruit'
                else:
                    row['warnings'].append('未闭合另一端钻出特例；不推断同端/反向/未知配对的奖励或消除规则。')
            row['condition_status'] = status
            if event['performed'] is False:
                row['marker_after_reference'] = before
            if status == 'matched':
                row['source_condition_reward_quantity'] = data['original_reward_quantity_reference']
                row['documented_reward_candidates'] = deepcopy(data['documented_reward_candidates'])
            else:
                row['documented_reward_candidates'] = deepcopy(data['documented_reward_candidates']) if status == 'unknown' else []
            declared = event['marker_after']; reference_after = row['marker_after_reference']
            row['marker_after_declared'] = declared
            if declared is not None and declared != 'unknown' and reference_after != 'unknown' and declared != reference_after:
                row['condition_status'] = 'conflict'
                row['warnings'].append('步骤后的独立标记声明与此来源条件结果不一致；双方保留，不将冲突当验收通过。')
            current = declared if declared is not None else reference_after
            row['warnings'].append('移动/探索声明只用于条件参考；没有实际奖励、领取、库存更新或地图移动证明。')
        row['admitted_marker_after'] = current; rows.append(row)
    return {'node': deepcopy(node), 'events': deepcopy(events), 'rows': rows,
            'generation_condition_status': _status([relic_owned, new_region_entered]),
            'relic_owned_declared': relic_owned, 'new_region_entered_declared': new_region_entered,
            'final_marker_reference': current, 'actual_final_marker': None,
            'whole_reward_total': None, 'repeated_trigger_cap': None,
            'run_state_written': False, 'game_operated': False,
            'source': deepcopy(data),
            'notes': ['藏果地状态、覆盖、步骤完成和密道另一端关系全部来自独立声明；不从实际地图坐标或相邻节点反推。',
                      '普通探索后的标记状态未知；只有明确另一端钻出的来源特例支持条件保留。',
                      '每行的一个随机自然物是固定原文数量参考；候选不代表实收，重复流程不累计为总奖励。',
                      '来源匹配、用户声明、实际游戏观测分别保留；不生成概率，不写本局、库存或私人设置。']}


def format_marker_flow(result, *, technical=False):
    node = result['node']
    lines = [f"{node['node_type']} · 藏果地声明流程", '生成条件参考：' + STATUSES[result['generation_condition_status']],
             '初始标记：' + MARKERS[node['marker']]]
    for row in result['rows']:
        lines += [f"步骤{row['index']} · {'声明放置' if row['kind'] == 'place' else '声明探索/钻出'}：{STATUSES[row['condition_status']]}",
                  '来源条件后的标记：' + MARKERS[row['marker_after_reference']] + '；后续采用的独立声明/条件状态：' + MARKERS[row['admitted_marker_after']]]
        if row['documented_reward_candidates']:
            lines.append('固定文档候选：' + '、'.join(item['name'] for item in row['documented_reward_candidates']))
        if row['source_condition_reward_quantity'] is not None:
            lines.append('原版数量参考：一个随机自然物；实际成员和领取数量未知。')
        lines.extend(row['warnings'])
    lines += ['重复触发上限、总奖励和真实最终标记：未知。', *result['notes'],
              '原文：' + result['source']['original_quantity_quote'],
              *['原句：' + re.sub(r'\[\[[^|\]]+\|([^\]]+)\]\]', r'\1', q) for q in result['source']['marker_document_quotes']]]
    if technical:
        lines += ['声明身份与完整条件结果：', json.dumps(result, ensure_ascii=False, indent=2)]
    return '\n'.join(lines)
