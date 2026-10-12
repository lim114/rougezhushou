"""Compare finite declared plans over sealed movement and base-reward rules.

No path is invented, no success probability is assigned, and a stopped
dependency chain cannot contribute its unvisited tail to the known subtotal.
"""
from copy import deepcopy

from .base_settlement_planning import settlements


def compare_routes(graph, routes, *, inventory=None, action_points=None,
                   start=None, passive_items=None, difficulty=None,
                   split_unlocked=None):
    from .exploration_planning import itinerary, _graph, _type_candidates
    nodes, initial = _graph(graph, start)
    if not isinstance(routes, list) or not 1 <= len(routes) <= 20:
        raise ValueError('比较需要1–20条明确声明的路线；不自动穷举或推荐真实最优路线。')
    seen = set()
    plans = []
    for route in routes:
        if (not isinstance(route, dict) or set(route) - {'id', 'name', 'steps'} or
                not isinstance(route.get('id'), str) or not route['id'] or
                route['id'] in seen):
            raise ValueError('每条路线需要唯一非空id，只支持id/name/steps。')
        seen.add(route['id'])
        name = route.get('name', route['id'])
        if not isinstance(name, str) or not name:
            raise ValueError('路线名称需要非空文字。')
        steps = route.get('steps')
        if not isinstance(steps, list) or not 1 <= len(steps) <= 100:
            raise ValueError('每条路线需要1–100项步骤。')
        moves = []
        for step in steps:
            if not isinstance(step, dict) or set(step) - {'mode', 'target', 'battle'}:
                raise ValueError('路线步骤只支持mode/target/battle；不忽略额外事件效果。')
            if 'battle' in step and not isinstance(step['battle'], dict):
                raise ValueError('battle需为独立的战斗结算条件对象。')
            if 'target' in (step.get('battle') or {}):
                raise ValueError('战斗条件不可改写移动目标；请在步骤target中绑定节点。')
            moves.append({key: deepcopy(step.get(key)) for key in ('mode', 'target')})
        movement = itinerary(graph, moves, inventory, action_points, initial,
                             passive_items, difficulty, split_unlocked)
        reward_rows = []
        known_xp = known_gold_min = known_gold_max = 0
        gaps = []
        claimed = set()
        for ordinal, (step, move) in enumerate(zip(steps, movement['steps']), 1):
            target = step['target']
            node = nodes[target]
            types, _ = _type_candidates(node)
            battle = step.get('battle')
            expected_battle = not types or any(key in (
                'BATTLE_NORMAL', 'BATTLE_ELITE', 'BATTLE_BOSS',
                'BATTLE_SAVAGE', 'DUEL') for key in types)
            expected_battle |= (node.get('content') or {}).get('kind') == 'battle'
            if battle is None and not expected_battle:
                continue
            declaration = {'target': target, **deepcopy(battle or {})}
            # Always validate and retain the independently documented reward,
            # even for a blocked tail. Its subtotal is admitted separately.
            source = settlements([declaration], graph)
            ref = source['rows'][0]
            arrival = (move['status'] == 'conditional_reference_step' and
                       move.get('nominal_ap_after_payment') is not None and
                       move.get('payment_zero_boundary') is False)
            repeated = target in claimed
            reasons = deepcopy(ref['unknown_components'])
            if not arrival:
                reasons.append('arrival_chain_unresolved_or_blocked')
            if repeated:
                reasons.append('repeated_battle_reward_eligibility_unknown')
            if ref['victory_declared'] is False:
                reasons.append('declared_battle_not_won')
            admitted = arrival and not repeated and ref['admitted_to_known_base_subtotal']
            xp = ref['conditional_base_experience']
            gold = ref['conditional_base_gold']
            if admitted and xp is not None:
                known_xp += xp
            if admitted and gold is not None:
                known_gold_min += gold['minimum']
                known_gold_max += gold['maximum']
            claimed.add(target)
            if reasons:
                gaps.append({'step': ordinal, 'node_id': target, 'reasons': reasons})
            reward_rows.append({'step': ordinal, 'node_id': target,
                               'conditional_arrival_reference': arrival,
                               'repeated_battle_reference': repeated,
                               'admitted_to_known_base_subtotal': admitted,
                               'base_reward_reference': ref,
                               'unknown_or_failed_conditions': reasons,
                               'actual_received': None})
        closed = movement['complete_declared_conditions'] and not gaps
        known = {'experience': known_xp,
                 'gold': {'minimum': known_gold_min, 'maximum': known_gold_max}}
        net_ap = (None if movement['nominal_final_ap'] is None or action_points is None
                  else action_points - movement['nominal_final_ap'])
        plans.append({'id': route['id'], 'name': name,
                      'goal_node': steps[-1]['target'],
                      'declared_steps': deepcopy(steps), 'movement_reference': movement,
                      'battle_reward_rows': reward_rows, 'known_base_subtotal': known,
                      'unknown_or_failed_conditions': gaps,
                      'closed_declared_component_reference': closed,
                      'conditional_base_total': deepcopy(known) if closed else None,
                      'net_ap_consumption_reference': net_ap,
                      'base_cost_reference': movement['known_base_ap_cost_sum'],
                      'component_dominated_by': [],
                      'actual_feasible': None, 'actual_final_resources': None})
    comparisons = []
    for left in plans:
        for right in plans:
            if left is right:
                continue
            reason = ('different_declared_goal' if left['goal_node'] != right['goal_node']
                      else 'component_conditions_not_closed' if not (
                          left['closed_declared_component_reference'] and
                          right['closed_declared_component_reference']) else None)
            dominates = None
            if reason is None:
                a, b = left['conditional_base_total'], right['conditional_base_total']
                # Interval comparison is conservative: the left minimum must
                # reach the right maximum, not just its midpoint or expectation.
                weak = (left['net_ap_consumption_reference'] <= right['net_ap_consumption_reference'] and
                        a['experience'] >= b['experience'] and
                        a['gold']['minimum'] >= b['gold']['maximum'])
                strict = (left['net_ap_consumption_reference'] < right['net_ap_consumption_reference'] or
                          a['experience'] > b['experience'] or
                          a['gold']['minimum'] > b['gold']['maximum'])
                dominates = weak and strict
                if dominates:
                    right['component_dominated_by'].append(left['id'])
            comparisons.append({'left': left['id'], 'right': right['id'],
                                'component_dominates': dominates, 'unresolved_reason': reason,
                                'actual_better_route': None})
    return {'scope': 'finite_declared_route_component_comparison', 'start': initial,
            'routes': plans, 'pairwise_comparisons': comparisons,
            'comparison_axes': ['net_declared_ap_consumption', 'base_battle_experience',
                                'base_battle_gold_interval'],
            'component_nondominated_candidates': [p['id'] for p in plans if
                p['closed_declared_component_reference'] and not p['component_dominated_by']],
            'actual_best_route': None, 'actual_gameplay_verified': False,
            'inventory_updated': False, 'probability': None,
            'source': {'movement': deepcopy(movement['source']),
                       'base_rewards': deepcopy(settlements([], graph)['source'])},
            'limits': [
                '仅比较有限声明方案；未枚举全部图路线，也未证明服务器资格、成功或真实可续行。',
                '费用、返还及临时次数沿用已证账本；未知、付款到零或阻断后不累计尾链战斗奖励。',
                '同节点再次作战能否重复领取未证，第二次奖励不作为已知小计。',
                '分项支配只比较同声明终点的净行动力、基础战斗经验和源石锭范围；不是完整收益或最优推荐。',
                '事件、掉落、加工品其他资源、失败风险、结局前置、住民动态、当前热更新和完整奖励池仍未计入。',
                '公开数值及明确胜利声明只构成局外条件参考，不写本局资源、持有或完成标记。']}
