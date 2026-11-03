"""Bounded simple-plan construction, reusing the sealed scratch ledgers.

This is an algorithm over a supplied graph, never a claim about the actual
server route space, hidden edges, battle success, or optimal gameplay.
"""
from collections import deque
from copy import deepcopy

from .base_settlement_planning import settlements
from .route_comparison import compare_routes


def search_routes(graph, goal, *, inventory=None, action_points=None, start=None,
                  passive_items=None, difficulty=None, split_unlocked=None,
                  battle_declarations=None, max_steps=8, max_results=20,
                  max_transitions=200):
    from .exploration_planning import _graph, _adjacency, movement_options, itinerary
    nodes, initial = _graph(graph, start)
    adjacency = _adjacency(graph, nodes)
    if len(nodes) > 100:
        raise ValueError('路线构造仅支持至多100个声明节点。')
    if not isinstance(goal, str) or goal not in nodes or goal == initial:
        raise ValueError('终点需要图中与起点不同的明确节点。')
    for value, upper, label in ((max_steps, 20, '最大步数'),
                                (max_results, 20, '结果上限'),
                                (max_transitions, 1000, '分支检查上限')):
        if type(value) is not int or not 1 <= value <= upper:
            raise ValueError(label + '需要1–' + str(upper) + '的整数。')
    if battle_declarations is None:
        battle_declarations = {}
    if not isinstance(battle_declarations, dict):
        raise ValueError('battle_declarations需要以节点ID为键的对象。')
    for key, declaration in battle_declarations.items():
        if key not in nodes or not isinstance(declaration, dict) or 'target' in declaration:
            raise ValueError('战斗声明必须绑定已有节点，且不可改写target。')
        settlements([{'target': key, **deepcopy(declaration)}], graph)
    # Validate even an unreachable or cap-limited inventory declaration.
    movement_options(graph, goal, inventory, action_points, initial,
                     passive_items, difficulty=difficulty,
                     split_unlocked=split_unlocked)
    ordered_nodes = sorted(nodes, key=lambda key: (nodes[key]['row'], nodes[key]['col'], key))
    queue = deque([(initial, [], (initial,))])
    plans, frontier = [], []
    transitions = depth_cuts = exclusions = 0
    limit_reason = None
    while queue:
        if transitions >= max_transitions or len(plans) >= max_results:
            limit_reason = 'transition_limit' if transitions >= max_transitions else 'result_limit'
            break
        cursor, prefix, visited = queue.popleft()
        if len(prefix) >= max_steps:
            depth_cuts += 1
            frontier.append({'node_id': cursor, 'steps': deepcopy(prefix),
                             'reason': 'depth_limit', 'actual_continuation': None})
            continue
        # The prior ledger is recomputed in isolation; no branch shares decrements.
        ledger = itinerary(graph, prefix, inventory, action_points, initial,
                           passive_items, difficulty, split_unlocked) if prefix else None
        stock = ledger['inventory_reference_state'] if ledger else inventory
        passives = ledger['passive_reference_state'] if ledger else passive_items
        ap = ledger['nominal_final_ap'] if ledger else action_points
        candidates = []
        for target in ordered_nodes:
            if target in visited:
                continue
            options = movement_options(graph, target, stock, ap, cursor, passives,
                                       difficulty=difficulty, split_unlocked=split_unlocked)
            for option in options['options']:
                # Do not let a shortest multi-edge walking macro silently omit
                # rewards/unknown conditions on intermediate visited nodes.
                if option['id'] == 'walking' and target not in adjacency[cursor]:
                    continue
                if option['known_conditions_match'] is False:
                    exclusions += 1
                    continue
                candidates.append((target, option['id']))
        for target, mode in candidates:
            if transitions >= max_transitions or len(plans) >= max_results:
                limit_reason = 'transition_limit' if transitions >= max_transitions else 'result_limit'
                break
            transitions += 1
            step = {'mode': mode, 'target': target}
            if target in battle_declarations:
                step['battle'] = deepcopy(battle_declarations[target])
            steps = prefix + [step]
            movement_steps = [{key: row[key] for key in ('mode', 'target')} for row in steps]
            reference = itinerary(graph, movement_steps, inventory, action_points,
                                  initial, passive_items, difficulty, split_unlocked)
            closed = reference['complete_declared_conditions']
            if target == goal:
                plans.append({'id': 'plan:' + str(len(plans) + 1),
                              'name': '声明候选' + str(len(plans) + 1),
                              'steps': deepcopy(steps)})
            if not closed:
                frontier.append({'node_id': target, 'steps': deepcopy(steps),
                                 'reason': reference['stopped_reason'] or 'action_points_unknown',
                                 'movement_reference': reference,
                                 'actual_continuation': None})
            elif target != goal:
                queue.append((target, steps, visited + (target,)))
        if limit_reason:
            break
    comparison = compare_routes(graph, plans, inventory=inventory, action_points=action_points,
                                start=initial, passive_items=passive_items,
                                difficulty=difficulty, split_unlocked=split_unlocked) if plans else None
    return {'scope': 'bounded_supplied_graph_simple_plan_search', 'start': initial,
            'goal_node': goal, 'plans': deepcopy(plans), 'comparison': comparison,
            'frontier': frontier, 'examined_transitions': transitions,
            'known_type_or_use_exclusions': exclusions,
            'max_steps': max_steps, 'max_results': max_results,
            'max_transitions': max_transitions, 'depth_limited_prefixes': depth_cuts,
            'pending_prefixes_at_limit': len(queue), 'limit_reason': limit_reason,
            'bounded_queue_exhausted': not queue and limit_reason is None,
            'all_actual_routes_enumerated': False, 'actual_best_route': None,
            'actual_goal_reachable': None, 'probability': None, 'inventory_updated': False,
            'actual_gameplay_verified': False,
            'source': deepcopy(movement_options(graph, goal, inventory, action_points,
                       initial, passive_items, difficulty=difficulty,
                       split_unlocked=split_unlocked)['source']),
            'limits': [
                '仅在显式图中构造不重复节点的有限声明计划；步行逐条已声明连线，加工品沿用已证几何和临时次数。',
                '随机落点、未知资格、付款到零及到达返还未知保留为停止前沿，不自动续行或赋概率。',
                '上限截断、深度裁剪与未证前沿均保留；没有结果不证明实际不存在路线。',
                '未自动将经过节点改为已完成，不补胜利、领取、库存或居民变化；战斗条件需独立声明。',
                '候选按已知分项比较，缺完整奖励、失败风险、结局前置与动态状态，不推荐真实最优。']}
