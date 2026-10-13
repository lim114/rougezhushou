"""Construct bounded routes with explicitly declared visit and admission policies.

Policy declarations are planning preferences, not evidence of an ending script.
Movement and reward references remain the independent, source-backed ledgers.
"""
from collections import deque
from copy import deepcopy

from .base_settlement_planning import settlements
from .route_comparison import compare_routes


def _node_list(value, nodes, label):
    if value is None:
        return []
    if (not isinstance(value, list) or len(value) > 100 or
            any(not isinstance(key, str) or key not in nodes for key in value) or
            len(value) != len(set(value))):
        raise ValueError(label + '需要至多100个不重复的图中节点ID。')
    return deepcopy(value)


def constrained_routes(graph, goal, *, required_nodes=None, avoid_nodes=None,
                       checkpoints=None, qualifications=None, inventory=None,
                       action_points=None, start=None, passive_items=None,
                       difficulty=None, split_unlocked=None,
                       battle_declarations=None, max_steps=8, max_results=20,
                       max_transitions=200):
    """BFS over simple plans, carrying unsatisfied visits and checkpoint progress.

    False admission declarations exclude a branch; unknown ones retain its
    frontier but never authorize its descendants. No game ending is inferred.
    """
    from .exploration_planning import _graph, _adjacency, movement_options, itinerary
    nodes, initial = _graph(graph, start)
    adjacency = _adjacency(graph, nodes)
    if len(nodes) > 100:
        raise ValueError('受约束路线仅支持至多100个声明节点。')
    if not isinstance(goal, str) or goal not in nodes or goal == initial:
        raise ValueError('终点需要图中与起点不同的明确节点。')
    for value, upper, label in ((max_steps, 20, '最大步数'),
                                (max_results, 20, '结果上限'),
                                (max_transitions, 1000, '分支检查上限')):
        if type(value) is not int or not 1 <= value <= upper:
            raise ValueError(label + '需要1–' + str(upper) + '的整数。')
    required = _node_list(required_nodes, nodes, '必经节点')
    avoided = _node_list(avoid_nodes, nodes, '避开节点')
    ordered = _node_list(checkpoints, nodes, '顺序检查点')
    if set(avoided) & (set(required) | set(ordered) | {initial, goal}):
        raise ValueError('避开节点不可同时是起点、终点、必经节点或顺序检查点。')
    if initial in ordered and ordered[0] != initial:
        raise ValueError('起点若在顺序检查点中，必须排第一；简单计划不会重访起点。')
    if goal in ordered and ordered[-1] != goal:
        raise ValueError('终点若在顺序检查点中，必须排最后。')
    if qualifications is None:
        qualifications = {}
    if not isinstance(qualifications, dict):
        raise ValueError('qualifications需要以图中节点ID为键的声明对象。')
    for key, row in qualifications.items():
        if (key not in nodes or not isinstance(row, dict) or
                set(row) - {'matches', 'reason'} or 'matches' not in row or
                (row['matches'] is not None and type(row['matches']) is not bool) or
                ('reason' in row and not isinstance(row['reason'], str))):
            raise ValueError('节点准入声明只支持matches（true/false/null）及文字reason。')
    if battle_declarations is None:
        battle_declarations = {}
    if not isinstance(battle_declarations, dict):
        raise ValueError('battle_declarations需要以节点ID为键的对象。')
    for key, row in battle_declarations.items():
        if key not in nodes or not isinstance(row, dict) or 'target' in row:
            raise ValueError('战斗声明必须绑定已有节点，且不可改写target。')
        settlements([{'target': key, **deepcopy(row)}], graph)
    # Validate ledgers even if the visit policy prevents every expansion.
    source = movement_options(graph, goal, inventory, action_points, initial,
                              passive_items, difficulty=difficulty,
                              split_unlocked=split_unlocked)['source']
    initial_index = 1 if ordered and ordered[0] == initial else 0
    queue = deque([(initial, [], (initial,), set(required) - {initial}, initial_index)])
    plans, frontier, exclusions = [], [], []
    examined = depth_cuts = source_exclusions = pending_siblings = 0
    limit_reason = None
    node_order = sorted(nodes, key=lambda key: (nodes[key]['row'], nodes[key]['col'], key))

    def boundary(cursor, prefix, remaining, checkpoint_index, reason, **extra):
        return {'node_id': cursor, 'steps': deepcopy(prefix), 'reason': reason,
                'remaining_required_nodes': sorted(remaining),
                'remaining_checkpoints': deepcopy(ordered[checkpoint_index:]),
                'actual_continuation': None, **extra}

    while queue:
        if examined >= max_transitions or len(plans) >= max_results:
            limit_reason = 'transition_limit' if examined >= max_transitions else 'result_limit'
            break
        cursor, prefix, visited, remaining, checkpoint_index = queue.popleft()
        remaining_visits = remaining | set(ordered[checkpoint_index:]) | {goal}
        if len(prefix) >= max_steps or len(remaining_visits) > max_steps - len(prefix):
            depth_cuts += 1
            reason = ('depth_limit' if len(prefix) >= max_steps
                      else 'remaining_constraints_exceed_step_budget')
            frontier.append(boundary(cursor, prefix, remaining, checkpoint_index, reason))
            continue
        moves = [{key: step[key] for key in ('mode', 'target')} for step in prefix]
        ledger = itinerary(graph, moves, inventory, action_points, initial,
                           passive_items, difficulty, split_unlocked) if moves else None
        stock = ledger['inventory_reference_state'] if ledger else inventory
        passives = ledger['passive_reference_state'] if ledger else passive_items
        ap = ledger['nominal_final_ap'] if ledger else action_points
        candidates = []
        for target in node_order:
            if target in visited:
                continue
            options = movement_options(graph, target, stock, ap, cursor, passives,
                                       difficulty=difficulty, split_unlocked=split_unlocked)
            for option in options['options']:
                if option['id'] == 'walking' and target not in adjacency[cursor]:
                    continue
                if option['known_conditions_match'] is False:
                    source_exclusions += 1
                    continue
                candidates.append((target, option['id']))
        for offset, (target, mode) in enumerate(candidates):
            if examined >= max_transitions or len(plans) >= max_results:
                limit_reason = 'transition_limit' if examined >= max_transitions else 'result_limit'
                pending_siblings = len(candidates) - offset
                break
            examined += 1
            step = {'mode': mode, 'target': target}
            if target in battle_declarations:
                step['battle'] = deepcopy(battle_declarations[target])
            steps = prefix + [step]
            next_remaining = remaining - {target}
            next_index = checkpoint_index
            reason = None
            if target in avoided:
                reason = 'declared_avoided_node'
            elif target in ordered[checkpoint_index + 1:]:
                reason = 'declared_checkpoint_order_mismatch'
            elif next_index < len(ordered) and target == ordered[next_index]:
                next_index += 1
            qualification = qualifications.get(target)
            if reason is None and qualification is not None and qualification['matches'] is False:
                reason = 'declared_entry_qualification_failed'
            if reason:
                exclusions.append(boundary(target, steps, remaining, checkpoint_index, reason,
                                           qualification_declaration=deepcopy(qualification)))
                continue
            if target == goal and (next_remaining or next_index != len(ordered)):
                exclusions.append(boundary(target, steps, next_remaining, next_index,
                                           'declared_goal_prerequisites_missing'))
                continue
            reference = itinerary(graph, [{key: row[key] for key in ('mode', 'target')} for row in steps],
                                  inventory, action_points, initial, passive_items,
                                  difficulty, split_unlocked)
            if qualification is not None and qualification['matches'] is None:
                frontier.append(boundary(target, steps, next_remaining, next_index,
                                         'declared_entry_qualification_unknown',
                                         qualification_declaration=deepcopy(qualification),
                                         movement_reference=reference,
                                         movement_stop_reason=reference['stopped_reason']))
                continue
            if not reference['complete_declared_conditions']:
                frontier.append(boundary(target, steps, next_remaining, next_index,
                                         reference['stopped_reason'] or 'action_points_unknown',
                                         movement_reference=reference))
                continue
            if target == goal:
                plans.append({'id': 'constrained:' + str(len(plans) + 1),
                              'name': '声明约束候选' + str(len(plans) + 1),
                              'steps': deepcopy(steps)})
            else:
                queue.append((target, steps, visited + (target,), next_remaining, next_index))
        if limit_reason:
            break
    comparison = compare_routes(graph, plans, inventory=inventory, action_points=action_points,
                                start=initial, passive_items=passive_items,
                                difficulty=difficulty, split_unlocked=split_unlocked) if plans else None
    return {'scope': 'bounded_declared_visit_policy_route_search', 'start': initial,
            'goal_node': goal, 'policy': {'required_nodes': required, 'avoid_nodes': avoided,
                                        'checkpoints': ordered, 'qualifications': deepcopy(qualifications)},
            'plans': deepcopy(plans), 'comparison': comparison,
            'frontier': frontier, 'policy_exclusions': exclusions,
            'examined_transitions': examined, 'known_type_or_use_exclusions': source_exclusions,
            'max_steps': max_steps, 'max_results': max_results, 'max_transitions': max_transitions,
            'depth_limited_prefixes': depth_cuts, 'pending_prefixes_at_limit': len(queue),
            'pending_sibling_options_at_limit': pending_siblings, 'limit_reason': limit_reason,
            'bounded_queue_exhausted': not queue and limit_reason is None,
            'declared_policy_search_complete': not queue and not frontier and limit_reason is None,
            'all_actual_routes_enumerated': False, 'actual_goal_reachable': None,
            'actual_best_route': None, 'probability': None, 'inventory_updated': False,
            'actual_gameplay_verified': False, 'source': deepcopy(source),
            'limits': [
                '必经、避开、顺序检查点与准入条件都是显式规划声明；不识别或证明任何游戏结局前置。',
                '仅构造不重复节点的有限计划；避开约束指不进入该节点，不定义加工品飞越几何或隐藏路径。',
                '已声明准入不符排除分支；准入未知保留停止前沿，不以静态候选资助后续移动或奖励。',
                '每条步行连线逐步记账；加工品实例和一次性概念体在每条临时方案中独立扣减。',
                '付款到零、随机目的地、次数或到达AP未知保留停止前沿；不猜耗尽/返还执行顺序。',
                '步数、结果和分支上限及未检查兄弟分支如实保留；没有候选不证明实际没有路线。',
                '基础战斗收益另需独立来源与胜利声明；完整收益、动态住民、失败风险和真实最优仍未知。']}
