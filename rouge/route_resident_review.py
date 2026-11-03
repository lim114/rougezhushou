"""Conditional resident-candidate phases for finite, explicitly declared plans.

No candidate overlap is converted to a collision, success rate, or safety claim.
Unknown fallbacks persist as unknown positions rather than disappearing.
"""
from copy import deepcopy

from .route_comparison import compare_routes


RESIDENT_SOURCE = {
    'url': 'https://m.prts.wiki/w/沉沦者的黑流树海', 'revision': '433770',
    'sha256': '8df90d811ef9516f46bb877a15c8701d83bd7d36ff744a42d9b27cfede8551e4',
    'file': 'research/p3-base-settlement/current-main.html',
    'scope': '文档流窜居民段落；不证明当前服务器脚本与移动顺序',
}


def _phase(states, target):
    positions = sorted(set().union(*(state['positions'] for state in states.values()))) if states else []
    unknown_ids = sorted(key for key, state in states.items() if state['position_unknown'])
    overlap = target in positions
    status = ('source_candidate_overlap' if overlap else
              'navigation_position_unknown' if unknown_ids else 'no_declared_candidate_overlap')
    return {'possible_occupied_union': positions, 'position_unknown_residents': unknown_ids,
            'target_candidate_overlap': overlap, 'status': status,
            'actual_collision_or_blockage': None, 'actual_safe': None}


def _advance(nodes, adjacency, states):
    from .exploration_planning import _resident_destination
    result, references = {}, []
    for identity, state in states.items():
        destinations, candidates, excluded, fallbacks = set(), [], [], []
        for current in sorted(state['positions']):
            found = False
            for other in sorted(adjacency[current]):
                match, basis = _resident_destination(nodes[other])
                row = {'from': current, 'to': other,
                       'destination_condition_matches': match, 'basis': basis,
                       'actual_selected': None, 'probability': None}
                if match is False:
                    excluded.append(row)
                else:
                    candidates.append(row); destinations.add(other); found = True
            if not found:
                fallbacks.append({'from': current, 'reason': 'no_nonexcluded_neighbor_fallback_unverified'})
        unknown = state['position_unknown'] or bool(fallbacks)
        result[identity] = {'positions': destinations, 'position_unknown': unknown}
        references.append({'resident_id': identity, 'candidate_positions': sorted(destinations),
                           'navigation_candidates': candidates, 'source_excluded_transitions': excluded,
                           'unresolved_fallbacks': fallbacks, 'prior_position_unknown': state['position_unknown'],
                           'future_position_unknown': unknown, 'actual_position': None})
    return result, references


def review_resident_routes(graph, routes, residents, *, inventory=None,
                          action_points=None, start=None, passive_items=None,
                          difficulty=None, split_unlocked=None,
                          risk_policy='show_all', resident_post_victories=None):
    """Review up to 20 plans of at most 10 single-edge/item moves each.

    Independent movement/base reward comparison is never modified by resident
    candidate sets. A stopped movement dependency disables subsequent phases.
    """
    from .exploration_planning import _graph, _adjacency, _type_candidates
    nodes, initial = _graph(graph, start); adjacency = _adjacency(graph, nodes)
    if len(nodes) > 100:
        raise ValueError('居民路线核对仅支持至多100个声明节点。')
    if risk_policy not in ('show_all', 'avoid_candidate_overlap'):
        raise ValueError('risk_policy需要show_all或avoid_candidate_overlap。')
    if not isinstance(residents, list) or len(residents) > 3:
        raise ValueError('居民快照需要0–3项明确位置对象；不从未知或未读自动推定为空。')
    declared = {}; original = []
    for ordinal, row in enumerate(residents, 1):
        if (not isinstance(row, dict) or set(row) - {'id', 'node_id'} or
                not isinstance(row.get('node_id'), str) or row['node_id'] not in nodes):
            raise ValueError('每名居民需要图中node_id，可选唯一id。')
        identity = row.get('id', 'resident:' + str(ordinal))
        if not isinstance(identity, str) or not identity or identity in declared:
            raise ValueError('居民id需要唯一非空文字。')
        declared[identity] = {'positions': {row['node_id']}, 'position_unknown': False}
        original.append({'id': identity, 'node_id': row['node_id']})
    if not isinstance(routes, list) or not 1 <= len(routes) <= 20:
        raise ValueError('需要1–20条显式路线。')
    for route in routes:
        if not isinstance(route, dict) or not isinstance(route.get('steps'), list) or not 1 <= len(route['steps']) <= 10:
            raise ValueError('每条居民核对路线需要1–10步；不自动拆解多格步行或截断后续声明。')
        cursor = initial
        for step in route['steps']:
            if not isinstance(step, dict):
                raise ValueError('路线步骤需要对象。')
            target = step.get('target')
            if step.get('mode') == 'walking' and (target == cursor or target not in adjacency[cursor]):
                raise ValueError('居民核对的每步walking需一条明确相邻连线；多格路线请逐格声明，同格再进入时钟未证。')
            if not isinstance(target, str) or target not in nodes:
                raise ValueError('步骤target需要图中明确节点。')
            cursor = target
    comparison = compare_routes(graph, routes, inventory=inventory, action_points=action_points,
                                start=initial, passive_items=passive_items,
                                difficulty=difficulty, split_unlocked=split_unlocked)
    if resident_post_victories is None:
        resident_post_victories = {}
    route_by_id = {row['id']: row for row in routes}
    if not isinstance(resident_post_victories, dict):
        raise ValueError('resident_post_victories需要以路线id为键的已声明获胜步骤列表。')
    for identity, steps in resident_post_victories.items():
        if (identity not in route_by_id or not isinstance(steps, list) or
                any(type(step) is not int or not 1 <= step <= len(route_by_id[identity]['steps']) for step in steps) or
                len(steps) != len(set(steps))):
            raise ValueError('据点获胜声明需要已有路线id及不重复的有效步骤序号。')
        for ordinal in steps:
            target = route_by_id[identity]['steps'][ordinal - 1]['target']
            types, _ = _type_candidates(nodes[target])
            if types != ['BATTLE_SAVAGE']:
                raise ValueError('据点获胜声明只能绑定明确原类型BATTLE_SAVAGE的到达步骤；普通作战或类型未知不借用驱逐规则。')
    reviewed, retained, policy_excluded = [], [], []
    for reference in comparison['routes']:
        states = deepcopy(declared); rows = []; stopped_at = None
        overlap_steps, navigation_unknown_steps, eviction_steps = [], [], []
        for move in reference['movement_reference']['steps']:
            ordinal, target = move['step'], move['target']
            if stopped_at is not None:
                rows.append({'step': ordinal, 'node_id': target, 'status': 'not_evaluated_after_movement_stop',
                             'pre_entry_reference': None, 'post_move_reference': None,
                             'resident_navigation_references': [], 'resident_post_victory_declared': ordinal in resident_post_victories.get(reference['id'], []),
                             'after_declared_post_victory_reference': None,
                             'actual_collision_or_blockage': None, 'actual_safe': None})
                continue
            pre = _phase(states, target)
            # Source arrival/payment uncertainty does not authorize a resident tick.
            movement_closed = (move['status'] == 'conditional_reference_step' and
                               move.get('nominal_ap_after_payment') is not None and
                               move.get('payment_zero_boundary') is False and
                               not move.get('unknown_ap_components'))
            row = {'step': ordinal, 'node_id': target,
                   'status': 'conditional_declared_move_review' if movement_closed else 'movement_dependency_unresolved',
                   'pre_entry_reference': pre, 'post_move_reference': None,
                   'resident_navigation_references': [],
                   'resident_post_victory_declared': ordinal in resident_post_victories.get(reference['id'], []),
                   'after_declared_post_victory_reference': None,
                   'actual_collision_or_blockage': None, 'actual_safe': None}
            if pre['target_candidate_overlap']:
                overlap_steps.append(ordinal)
            if pre['position_unknown_residents']:
                navigation_unknown_steps.append(ordinal)
            if not movement_closed:
                stopped_at = ordinal; row['movement_stop_reason'] = move.get('reason') or reference['movement_reference']['stopped_reason'] or 'action_points_unknown'
                rows.append(row); continue
            states, navigation = _advance(nodes, adjacency, states)
            post = _phase(states, target); row['post_move_reference'] = post
            row['resident_navigation_references'] = navigation
            if post['target_candidate_overlap']:
                overlap_steps.append(ordinal)
            if post['position_unknown_residents']:
                navigation_unknown_steps.append(ordinal)
            # This is a distinct caller-declared battle-success phase, never
            # inferred from movement, generic battle types or base reward rows.
            if row['resident_post_victory_declared']:
                states = {}; eviction_steps.append(ordinal)
                row['after_declared_post_victory_reference'] = {
                    **_phase(states, target), 'all_residents_evicted_if_declared_post_victory': True,
                    'source': deepcopy(RESIDENT_SOURCE), 'actual_eviction': None}
            rows.append(row)
        excluded = risk_policy == 'avoid_candidate_overlap' and bool(overlap_steps)
        (policy_excluded if excluded else retained).append(reference['id'])
        reviewed.append({'id': reference['id'], 'name': reference['name'], 'declared_steps': deepcopy(reference['declared_steps']),
                         'phase_rows': rows, 'candidate_overlap_steps': sorted(set(overlap_steps)),
                         'navigation_unknown_steps': sorted(set(navigation_unknown_steps)),
                         'movement_stop_step': stopped_at, 'conditional_post_eviction_steps': eviction_steps,
                         'excluded_by_declared_risk_policy': excluded,
                         'actual_feasible': None, 'actual_safe': None, 'actual_failure_probability': None})
    return {'scope': 'finite_declared_route_resident_candidate_phase_review', 'start': initial,
            'residents_snapshot_declaration': original, 'resident_post_victories': deepcopy(resident_post_victories),
            'routes': reviewed, 'movement_and_base_comparison': comparison,
            'risk_policy': risk_policy, 'policy_retained_route_ids': retained,
            'policy_excluded_route_ids': policy_excluded, 'source': deepcopy(RESIDENT_SOURCE),
            'actual_gameplay_verified': False, 'inventory_updated': False,
            'actual_best_route': None, 'actual_failure_probability': None,
            'joint_collision_resolution_verified': False, 'move_entry_battle_order_verified': False,
            'limits': [
                '居民起始位置和0名居民均为显式快照声明；不是从未读页面推断，没有当前服务器验证。',
                '逐次玩家声明移动后按显式连线展开一格候选；来源排除节点保留，所有其余资格仍未知。',
                '进入前与移动后阶段分别显示；玩家进入、居民移动、碰撞、战斗与回退的实际顺序未知。',
                '某候选分支无未排除相邻节点时，回退及后续位置保持未知，不让空候选集合冒充安全。',
                '移动链已阻断或AP/资格未知后不展开居民尾链；该步之后不能从未评估结果判断无风险。',
                '据点获胜驱逐只用独立步骤声明和明确BATTLE_SAVAGE原类型；不从经过节点推断获胜或改变本局。',
                '候选并集不证明多个居民能同时占领；候选无交集不证明安全，排除仅为显式保守规划偏好。',
                '未据此改写费用、基础奖励、节点完成、居民据点或库存；完整收益、实际失败率与最优路线未知。']}
