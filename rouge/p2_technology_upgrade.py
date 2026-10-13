"""Source-supported automatic technology gates and explicitly declared budgets."""
from copy import deepcopy
from collections import Counter
from functools import lru_cache
import json
from pathlib import Path


STATUSES = ('unknown', 'locked', 'unlocked')


@lru_cache(maxsize=1)
def source_data():
    return json.loads((Path(__file__).parent / 'data/p2-technology-upgrade-source.json').read_text(encoding='utf-8'))


def _labels():
    nodes = source_data()['common_development_raw']['developments']
    counts = Counter(node['buffName'] for node in nodes.values()); seen = Counter(); labels = {}
    for identity, node in nodes.items():
        name = node['buffName']; seen[name] += 1
        labels[identity] = name + (f'（{seen[name]}/{counts[name]}）' if counts[name] > 1 else '')
    return labels


def _integer(value, label, maximum=9999, unknown=True):
    if unknown and value is None: return None
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f'{label}需0–{maximum}整数，未知可用null。')
    return value


def _snapshot(value):
    nodes = source_data()['common_development_raw']['developments']
    if type(value) is not dict or set(value) != {'profile_name', 'nodes'}:
        raise ValueError('账户声明快照需profile_name及nodes。')
    name = value['profile_name']
    if (type(name) is not str or not 1 <= len(name) <= 60 or
            any(ord(c) < 32 or 0xd800 <= ord(c) <= 0xdfff for c in name)):
        raise ValueError('账户声明名称需1–60个可显示字符。')
    if type(value['nodes']) is not dict:
        raise ValueError('nodes需节点ID到unknown/locked/unlocked的明确声明。')
    for identity, status in value['nodes'].items():
        if identity not in nodes or type(status) is not str or status not in STATUSES:
            raise ValueError('科技节点身份或声明状态无效。')
    return deepcopy(value)


def capture_account_reference(account_state):
    """Read-only adapter; saving and account identity checks are never requested."""
    ids = source_data()['common_development_raw']['developments']
    return _snapshot({'profile_name': account_state.profile_name,
                      'nodes': {identity: account_state.view(identity)['status'] for identity in ids}})


def _and(values):
    return False if any(value is False for value in values) else None if any(value is None for value in values) else True


def automatic_gate_qualification(snapshot, mode, grade):
    snapshot = _snapshot(snapshot)
    if mode not in (None, 'regular', 'other'):
        raise ValueError('模式声明需regular、other或null。')
    _integer(grade, '保密等级', 15)
    data = source_data()['common_development_raw']; states = snapshot['nodes']; rows = []
    for identity, gate in data['developmentsDifficultyNodeInfos'].items():
        node = data['developments'][identity]
        front = {key: states.get(key, 'unknown') for key in node['frontNodeId']}
        or_met = True if 'unlocked' in front.values() else None if 'unknown' in front.values() else False
        mode_met = None if mode is None else mode == 'regular'
        grade_met = None if grade is None else grade >= gate['enableGrade']
        eligible = _and((or_met, mode_met, grade_met))
        mark = states.get(identity, 'unknown')
        conflict = (mark == 'unlocked' and eligible is False) or (mark == 'locked' and eligible is True)
        rows.append({'id': identity, 'name': node['buffName'], 'token_cost_reference': node['tokenCost'],
                     'front_statuses_declared': front, 'front_any_qualified': or_met,
                     'mode_qualified': mode_met, 'grade_threshold': gate['enableGrade'],
                     'grade_qualified': grade_met, 'eligible_reference': eligible,
                     'manual_gate_mark': mark, 'manual_mark_context_difference': conflict,
                     'actual_account_unlocked': None, 'actual_active': None,
                     'source_selector': '$.customizeData.rogue_6.commonDevelopment.developments.' + identity,
                     'grade_selector': '$.customizeData.rogue_6.commonDevelopment.developmentsDifficultyNodeInfos.' + identity,
                     'buff_numeric_effect': None})
    return rows


def technology_upgrade_plan(snapshot, preview):
    initial = _snapshot(snapshot)
    if type(preview) is not dict or set(preview) != {'mode', 'grade', 'budget', 'steps'}:
        raise ValueError('规划需mode、grade、budget和steps。')
    budget = _integer(preview['budget'], '演化算子预算')
    if type(preview['steps']) is not list or len(preview['steps']) > 54:
        raise ValueError('所选付费目标需0–54项。')
    before_gates = automatic_gate_qualification(initial, preview['mode'], preview['grade'])
    data = source_data()['common_development_raw']['developments']
    projected = deepcopy(initial); rows = []; seen = set()
    planned_remaining = budget; declared_remaining = budget; known_min = 0; possible_max = 0
    for index, step in enumerate(preview['steps'], 1):
        if type(step) is not dict or set(step) != {'node_id', 'accepted', 'charged_tokens', 'refunded_tokens'}:
            raise ValueError('每步需node_id/accepted/charged_tokens/refunded_tokens。')
        identity = step['node_id']
        if type(identity) is not str or identity not in data:
            raise ValueError('所选科技身份无效。')
        if identity in seen:
            raise ValueError('同一所选目标只出现一次；不重复计算同节点升级。')
        seen.add(identity); node = data[identity]
        if node['nodeType'] == 'DIFFICULTY':
            raise ValueError('生灵自动门不是付费购买目标；请核前置、模式和难度。')
        if step['accepted'] is not None and type(step['accepted']) is not bool:
            raise ValueError('接受情景需true、false或null。')
        charge = _integer(step['charged_tokens'], '声明扣除算子')
        refund = _integer(step['refunded_tokens'], '声明返还算子')
        status = projected['nodes'].get(identity, 'unknown'); cost = node['tokenCost']
        planned_cost = 0 if status == 'unlocked' else cost if status == 'locked' else None
        low = 0 if status in ('unknown', 'unlocked') else cost
        high = 0 if status == 'unlocked' else cost
        known_min += low; possible_max += high
        planned_remaining = (planned_remaining - planned_cost
                             if planned_remaining is not None and planned_cost is not None else None)
        declared_before = declared_remaining
        declared_candidate = declared_before - charge + refund if all(v is not None for v in (declared_before, charge, refund)) else None
        shortfall = -declared_candidate if declared_candidate is not None and declared_candidate < 0 else 0
        # A negative ledger cannot become a plausible balance for later rows.
        declared_remaining = None if shortfall else declared_candidate
        front = {key: projected['nodes'].get(key, 'unknown') for key in node['frontNodeId']}
        if step['accepted'] is True:
            projected['nodes'][identity] = 'unlocked'
        elif step['accepted'] is None and status != 'unlocked':
            projected['nodes'][identity] = 'unknown'
        # False leaves the declaration unchanged. Charges/refunds are wholly
        # independent; rejected steps never imply zero charge or a refund.
        rows.append({'ordinal': index, 'id': identity, 'name': node['buffName'],
                     'before_status': status, 'after_status_reference': projected['nodes'].get(identity, 'unknown'),
                     'nominal_new_node_cost': cost, 'planned_cost_reference': planned_cost,
                     'selected_cost_min': low, 'selected_cost_max': high,
                     'planned_remaining_reference': planned_remaining,
                     'accepted_declared': step['accepted'], 'charged_tokens_declared': charge,
                     'refunded_tokens_declared': refund, 'declared_budget_before': declared_before,
                     'declared_budget_after': declared_remaining, 'declared_budget_shortfall': shortfall,
                     'front_display_statuses': front, 'ordinary_prerequisite_logic': 'unknown',
                     'actual_purchase_legal': None, 'actual_paid_tokens': None, 'actual_account_status': None,
                     'automatic_gates_after_reference': automatic_gate_qualification(projected, preview['mode'], preview['grade']),
                     'source_selector': '$.customizeData.rogue_6.commonDevelopment.developments.' + identity})
    known_total = known_min if known_min == possible_max else None
    return {'topic_id': 'rogue_6', 'profile_name': initial['profile_name'],
            'snapshot': initial, 'preview': deepcopy(preview), 'rows': rows,
            'initial_gates': before_gates,
            'final_gates': automatic_gate_qualification(projected, preview['mode'], preview['grade']),
            'projected_nodes_reference': projected['nodes'], 'budget_declared': budget,
            'selected_cost_min': known_min, 'selected_cost_max': possible_max,
            'selected_cost_reference': known_total,
            'selected_budget_sufficient_reference': budget >= known_total if budget is not None and known_total is not None else None,
            'planned_remaining_reference': planned_remaining, 'declared_budget_after': declared_remaining,
            'full_prerequisite_cost': None, 'minimum_required_plan': None,
            'game_account_identity_verified': False, 'actual_activation': None,
            'source': deepcopy(source_data()['source']), 'public_rule': deepcopy(source_data()['public_rule']),
            'notes': ['账户状态只是当前快照的明确声明；未列出的节点保留未知，不读取或确认游戏账户身份。',
                      '三个生灵自动门按任一前置、常规行动及3/6/9门槛核资格；自动门手动标记不能代替前置。',
                      '接受情景只改变临时规划分支的节点状态，进而更新资格参考；符合资格不等于实际已激活。',
                      '所选目标费用来自逐节点tokenCost，未知解锁状态给所选成本范围；不含未列出的前置费用。',
                      '普通显示前置的AND/OR判定仍未知；不生成全树最短计划、最低必需费用或购买合法结论。',
                      '规划费用、明确接受情景、声明扣费/返还与真实付费分开；失败不自动免扣或退款。',
                      '声明预算任一数值未知时沿账本保留未知；负余额阻断后续余额推算，不补造缺少算子。',
                      '该工具只作独立规划，不购买、不改账户档案或本局；数值buff层和真实激活仍未知。']}


def format_technology_upgrade(plan):
    def show(value): return '未知' if value is None else str(value)
    def yes(value): return '未知' if value is None else '符合' if value else '不符合'
    labels = _labels(); statuses = {'unknown': '未知', 'locked': '未解锁声明', 'unlocked': '已解锁声明'}
    def fronts(values): return '、'.join(labels[key] + '：' + statuses[value] for key, value in values.items()) or '无显示前置'
    lines = [plan['profile_name'] + ' · 科技所选目标预算与生灵资格',
             '模式声明：' + {None: '未知', 'regular': '常规行动', 'other': '其它模式'}[plan['preview']['mode']]
             + '；保密等级声明：' + show(plan['preview']['grade']),
             f"声明演化算子预算{show(plan['budget_declared'])}；所选目标成本范围{plan['selected_cost_min']}–{plan['selected_cost_max']}；"
             f"完整前置费用未知；声明最终余额{show(plan['declared_budget_after'])}"]
    for row in plan['rows']:
        acceptance = '未知' if row['accepted_declared'] is None else '假设接受' if row['accepted_declared'] else '假设未接受'
        lines.append(f"{row['ordinal']}. {labels[row['id']]}：当前{statuses[row['before_status']]}；新节点原费用{row['nominal_new_node_cost']}；"
                     f"所选计划费用{show(row['planned_cost_reference'])}；接受情景{acceptance}；"
                     f"声明扣除{show(row['charged_tokens_declared'])}/返还{show(row['refunded_tokens_declared'])}；"
                     f"声明余额{show(row['declared_budget_after'])}")
        lines.append('普通显示前置：' + fronts(row['front_display_statuses']) + '；购买判定未知。')
        if row['declared_budget_shortfall']:
            lines.append(f"声明预算出现负余额矛盾：缺少{row['declared_budget_shortfall']}演化算子，后续余额未知。")
    for initial, row in zip(plan['initial_gates'], plan['final_gates']):
        lines.append(f"{row['name']}（门槛{row['grade_threshold']}）：任一前置{yes(row['front_any_qualified'])}、"
                     f"模式{yes(row['mode_qualified'])}、难度{yes(row['grade_qualified'])}；"
                     f"初始资格{yes(initial['eligible_reference'])}→接受情景后{yes(row['eligible_reference'])}；实际激活未知。")
        lines.append('初始前置声明：' + fronts(initial['front_statuses_declared']) + '；接受情景后：' + fronts(row['front_statuses_declared']))
        if row['manual_mark_context_difference']:
            lines.append('自动门手动标记与当前前置/模式/难度资格参考不同；保留原档案，不自动改写。')
    return '\n'.join([*lines, *plan['notes']])
