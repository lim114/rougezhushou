"""Revalidate a declared suffix against fresh, separately declared observations.

Progress, battle results and resource snapshots are independent facts. No
nominal ledger is promoted to actual inventory, completion or game state.
"""
from copy import deepcopy

from .route_constraints import constrained_routes, _node_list


def _snapshot(value, label):
    from .exploration_planning import _graph, _adjacency, _item
    if (not isinstance(value, dict) or set(value) - {'graph', 'action_points', 'inventory', 'passive_items'} or
            any(field not in value for field in ('graph', 'action_points', 'inventory', 'passive_items'))):
        raise ValueError(label + '需独立graph/action_points/inventory/passive_items，不自动采用旧预测。')
    nodes, current = _graph(value['graph']); _adjacency(value['graph'], nodes)
    if len(nodes) > 100:
        raise ValueError('续接只支持至多100个声明节点。')
    ap = value['action_points']
    if ap is not None and (type(ap) is not int or ap < 0):
        raise ValueError(label + '行动力需非负整数或null。')
    stock = value['inventory']; ids = set()
    if stock is not None:
        if not isinstance(stock, list) or len(stock) > 100:
            raise ValueError(label + '库存需列表或null（未知）。')
        for ordinal, entry in enumerate(stock, 1):
            if not isinstance(entry, dict) or set(entry) - {'instance_id', 'item_id', 'remaining_uses'}:
                raise ValueError('加工品只支持instance_id/item_id/remaining_uses。')
            item = _item(entry.get('item_id'), 'MOVE'); identity = entry.get('instance_id', 'inventory:' + str(ordinal))
            count = entry.get('remaining_uses')
            if not isinstance(identity, str) or not identity or identity == 'walking' or identity in ids:
                raise ValueError('加工品实例需唯一非空id，不能占用walking。')
            if count is not None and (type(count) is not int or not 0 <= count <= item['raw']['count']):
                raise ValueError('加工品余次数需固定来源范围内整数或null。')
            ids.add(identity)
    passives = value['passive_items']; ids = set()
    if passives is not None:
        if not isinstance(passives, list) or len(passives) > 6:
            raise ValueError('概念体需列表或null（未知）。')
        for entry in passives:
            if not isinstance(entry, dict) or set(entry) - {'item_id', 'remaining_activations'}:
                raise ValueError('概念体只支持item_id/remaining_activations。')
            item = _item(entry.get('item_id'), 'PASSIVE'); count = entry.get('remaining_activations')
            if item['id'] in ids or (count is not None and (type(count) is not int or count < 0 or
                    (item['id'] in ('rogue_6_scrap_P_01', 'rogue_6_scrap_P_02', 'rogue_6_scrap_P_03') and count > 1))):
                raise ValueError('概念体同种来源不可重复，余次数需来源范围内整数或null。')
            ids.add(item['id'])
    return nodes, current


def _identity(graph):
    instance, zone, template = graph.get('map_instance_id'), graph.get('zone_id'), graph.get('template_id')
    return (instance, zone, template) if all(isinstance(value, str) and value for value in (instance, zone, template)) else None


def _bound(before, after, identity):
    return (identity in before and identity in after and
            (before[identity]['row'], before[identity]['col']) == (after[identity]['row'], after[identity]['col']))


def _stock(value):
    if value is None:
        return None
    return {row.get('instance_id', 'inventory:' + str(ordinal)): row for ordinal, row in enumerate(value, 1)}


def _policy(value, nodes):
    if value is None:
        value = {}
    if not isinstance(value, dict) or set(value) - {'required_nodes', 'avoid_nodes', 'checkpoints', 'qualifications'}:
        raise ValueError('人工目标只支持required_nodes/avoid_nodes/checkpoints/qualifications。')
    result = {key: _node_list(value.get(key), nodes, key) for key in ('required_nodes', 'avoid_nodes', 'checkpoints')}
    qualifications = value.get('qualifications') or {}
    if not isinstance(qualifications, dict):
        raise ValueError('qualifications需节点id对象。')
    for key, row in qualifications.items():
        if (key not in nodes or not isinstance(row, dict) or set(row) - {'matches', 'reason'} or 'matches' not in row or
                (row['matches'] is not None and type(row['matches']) is not bool) or
                ('reason' in row and not isinstance(row['reason'], str))):
            raise ValueError('准入需图中节点matches true/false/null及可选文字reason。')
    result['qualifications'] = deepcopy(qualifications)
    return result


def continue_route_plan(before, plan, progress, after, *, objectives=None,
                        goal_after=None, objectives_after=None,
                        continue_after_failure_declared=None,
                        max_steps=8, max_results=20, max_transitions=200):
    from .exploration_planning import _adjacency, itinerary, reference_data
    old_nodes, old_start = _snapshot(before, '原声明'); new_nodes, new_start = _snapshot(after, '新声明')
    if (not isinstance(plan, dict) or set(plan) - {'id', 'name', 'steps'} or
            not isinstance(plan.get('id'), str) or not plan['id'] or
            not isinstance(plan.get('name', plan['id']), str) or not plan.get('name', plan['id']) or
            not isinstance(plan.get('steps'), list) or not 1 <= len(plan['steps']) <= 20):
        raise ValueError('原计划需id及1–20步明确steps。')
    old_adjacency = _adjacency(before['graph'], old_nodes); cursor = old_start
    for step in plan['steps']:
        if (not isinstance(step, dict) or set(step) - {'mode', 'target', 'battle'} or
                not isinstance(step.get('mode'), str) or not step['mode'] or step.get('target') not in old_nodes):
            raise ValueError('原步骤需要图中target及明确mode，可选battle资料。')
        if step['mode'] == 'walking' and step['target'] not in old_adjacency[cursor]:
            raise ValueError('续接原计划每步步行需一条明确相邻连线，不自动补齐中途完成事件。')
        cursor = step['target']
        if 'battle' in step:
            from .base_settlement_planning import settlements
            if not isinstance(step['battle'], dict) or 'target' in step['battle']:
                raise ValueError('battle需独立对象，不可改写target。')
            settlements([{'target': step['target'], **deepcopy(step['battle'])}], before['graph'])
    if not isinstance(progress, list) or len(progress) > len(plan['steps']):
        raise ValueError('进度声明需不超过原计划步数的逐步对象列表。')
    if continue_after_failure_declared is not None and type(continue_after_failure_declared) is not bool:
        raise ValueError('失败后继续资格需独立true/false/null声明。')
    for value, upper in ((max_steps, 20), (max_results, 20), (max_transitions, 1000)):
        if type(value) is not int or not 1 <= value <= upper:
            raise ValueError('重规划上限需来源允许范围内正整数。')
    policy = _policy(objectives, old_nodes)
    if objectives_after is not None:
        new_policy = _policy(objectives_after, new_nodes)
        if goal_after is None:
            raise ValueError('独立新人工目标需同时明确goal_after，不忽略其作用范围。')
    else:
        new_policy = None
    if goal_after is not None and (not isinstance(goal_after, str) or goal_after not in new_nodes):
        raise ValueError('新目标必须是新图中的明确节点。')
    old_identity, new_identity = _identity(before['graph']), _identity(after['graph'])
    scope_match = None if old_identity is None or new_identity is None else old_identity == new_identity
    rows = []; matched = 0; stopped = False; failures = []
    for ordinal, receipt in enumerate(progress, 1):
        if (not isinstance(receipt, dict) or set(receipt) - {'step', 'target', 'mode', 'movement_completed_declared', 'battle_result_declared'} or
                type(receipt.get('step')) is not int or receipt['step'] != ordinal or
                not isinstance(receipt.get('target'), str) or not isinstance(receipt.get('mode'), str) or
                'movement_completed_declared' not in receipt or
                (receipt['movement_completed_declared'] is not None and type(receipt['movement_completed_declared']) is not bool) or
                receipt.get('battle_result_declared') not in (None, 'won', 'lost')):
            raise ValueError('进度需连续1起步骤、target/mode、独立移动完成及won/lost/null战斗结果。')
        declared = plan['steps'][ordinal - 1]
        match = receipt['target'] == declared['target'] and receipt['mode'] == declared['mode']
        admitted = not stopped and match and receipt['movement_completed_declared'] is True
        reason = ('previous_progress_gap' if stopped else 'progress_deviates_from_declared_plan' if not match else
                  'movement_not_completed_declared' if receipt['movement_completed_declared'] is False else
                  'movement_completion_unknown' if receipt['movement_completed_declared'] is None else None)
        rows.append({**deepcopy(receipt), 'match_to_plan': match, 'admitted_to_prefix': admitted, 'reason': reason})
        if admitted:
            matched += 1
        else:
            stopped = True
        if receipt.get('battle_result_declared') == 'lost':
            failures.append(ordinal)
    anchor = plan['steps'][matched - 1]['target'] if matched else old_start
    anchor_status = ('unknown' if scope_match is not True or not _bound(old_nodes, new_nodes, anchor) else
                     'matched' if anchor == new_start else 'mismatch')
    prefix_reference = None; prefix_error = None
    if matched:
        moves = [{key: step[key] for key in ('mode', 'target')} for step in plan['steps'][:matched]]
        try:
            if before['inventory'] is None and any(step['mode'] != 'walking' for step in moves):
                prefix_error = 'original_inventory_snapshot_unknown'
            else:
                prefix_reference = itinerary(before['graph'], moves, before['inventory'] or [], before['action_points'], old_start, before['passive_items'] or [])
        except ValueError as exc:
            prefix_error = str(exc)
    old_prediction = prefix_reference['nominal_final_ap'] if prefix_reference and prefix_reference['complete_declared_conditions'] else before['action_points'] if not matched else None
    ap_after = after['action_points']; ap_delta = ap_after - old_prediction if old_prediction is not None and ap_after is not None and anchor_status == 'matched' else None
    predicted_stock = _stock(prefix_reference['inventory_reference_state']) if prefix_reference and prefix_reference['complete_declared_conditions'] else _stock(before['inventory']) if not matched else None
    if anchor_status != 'matched':
        predicted_stock = None
    new_stock = _stock(after['inventory']); stock_changes = []
    if predicted_stock is None or new_stock is None:
        stock_changes.append({'instance_id': None, 'kind': 'unknown', 'reason': 'inventory_prediction_or_new_snapshot_unknown'})
    else:
        for identity in sorted(predicted_stock.keys() | new_stock.keys()):
            a, b = predicted_stock.get(identity), new_stock.get(identity)
            if a is not None and a.get('remaining_uses') == 0 and b is None:
                continue  # Model-depleted is not an unexplained new inventory loss.
            kind = ('added' if a is None else 'missing' if b is None else 'identity_conflict' if a['item_id'] != b['item_id'] else
                    'unknown' if a.get('remaining_uses') is None or b.get('remaining_uses') is None else 'changed' if a.get('remaining_uses') != b.get('remaining_uses') else None)
            if kind:
                stock_changes.append({'instance_id': identity, 'kind': kind, 'predicted_reference': deepcopy(a), 'after_declared': deepcopy(b),
                                      'delta': b['remaining_uses'] - a['remaining_uses'] if kind == 'changed' else None,
                                      'cause_verified': False})
    node_changes = []
    fields = ('base_node_type', 'node_type_raw', 'completed_declared', 'occupied_declared', 'other_blocked_declared', 'light_arrival_declaration')
    for identity in sorted(old_nodes.keys() | new_nodes.keys()):
        a, b = old_nodes.get(identity), new_nodes.get(identity)
        if a is None or b is None or not _bound(old_nodes, new_nodes, identity):
            node_changes.append({'node_id': identity, 'changes': ['node_binding_unknown_or_changed'], 'before': deepcopy(a), 'after': deepcopy(b)})
        else:
            changed = [field for field in fields if a.get(field) != b.get(field)]
            if changed:
                node_changes.append({'node_id': identity, 'changes': changed, 'before': deepcopy(a), 'after': deepcopy(b)})
    edges_a = {tuple(sorted(edge)) for edge in before['graph']['edges']}; edges_b = {tuple(sorted(edge)) for edge in after['graph']['edges']}
    differences = {'action_points': {'predicted_reference': old_prediction, 'after_declared': ap_after, 'delta': ap_delta,
                                    'reason': None if ap_delta is not None else 'prediction_or_anchor_or_new_ap_unknown'},
                   'inventory': stock_changes, 'nodes': node_changes,
                   'edges': {'added': [list(edge) for edge in sorted(edges_b - edges_a)], 'removed': [list(edge) for edge in sorted(edges_a - edges_b)]}}
    remaining_policy = None; origin = None; frontier = []; status = None
    explicit_reset = goal_after is not None and new_policy is not None
    goal = goal_after if goal_after is not None else plan['steps'][-1]['target']
    if explicit_reset:
        remaining_policy = new_policy; origin = 'explicit_new_goal_and_objectives'
    elif anchor_status == 'matched' and not stopped:
        visited = [old_start, *[step['target'] for step in plan['steps'][:matched]]]
        cursor = 0; order_conflict = False
        for target in visited:
            if cursor < len(policy['checkpoints']) and target == policy['checkpoints'][cursor]:
                cursor += 1
            elif target in policy['checkpoints'][cursor + 1:]:
                order_conflict = True
        remaining_policy = {**deepcopy(policy), 'required_nodes': [key for key in policy['required_nodes'] if key not in visited], 'checkpoints': policy['checkpoints'][cursor:]}
        origin = 'matched_declared_prefix_and_fresh_snapshot'
        if order_conflict:
            frontier.append({'node_id': new_start, 'reason': 'declared_checkpoint_progress_order_conflict'})
        missing_bindings = sorted({goal, *remaining_policy['required_nodes'], *remaining_policy['avoid_nodes'], *remaining_policy['checkpoints'], *remaining_policy['qualifications']} - new_nodes.keys())
        binding_keys = {*remaining_policy['required_nodes'], *remaining_policy['avoid_nodes'], *remaining_policy['checkpoints'], *remaining_policy['qualifications']}
        if goal_after is None:
            binding_keys.add(goal)
        changed_bindings = sorted(key for key in binding_keys if not _bound(old_nodes, new_nodes, key))
        if missing_bindings or changed_bindings:
            frontier.append({'node_id': new_start, 'reason': 'residual_goal_or_policy_binding_unknown', 'missing_nodes': missing_bindings, 'changed_nodes': changed_bindings})
    else:
        frontier.append({'node_id': new_start, 'reason': 'progress_anchor_or_scope_or_prefix_unknown'})
    if failures and continue_after_failure_declared is not True:
        frontier.append({'node_id': new_start, 'reason': 'failed_battle_continuation_not_declared' if continue_after_failure_declared is None else 'failed_battle_continuation_declared_false'})
    suffix_review = None
    if anchor_status == 'matched' and not stopped:
        suffix = [{key: step[key] for key in ('mode', 'target')} for step in plan['steps'][matched:]]
        issues = []; adjacency = _adjacency(after['graph'], new_nodes); cursor = new_start
        for ordinal, step in enumerate(suffix, matched + 1):
            target = step['target']
            reason = None
            if target not in new_nodes or not _bound(old_nodes, new_nodes, target):
                reason = 'suffix_node_binding_unknown'
            elif step['mode'] == 'walking' and target not in adjacency[cursor]:
                reason = 'planned_walking_edge_removed'
            elif step['mode'] != 'walking' and (new_stock is None or step['mode'] not in new_stock):
                reason = 'suffix_inventory_unknown' if new_stock is None else 'planned_item_instance_missing'
            if reason:
                issues.append({'step': ordinal, 'node_id': target, 'reason': reason})
            if target in new_nodes:
                cursor = target
        ledger = None
        if suffix and not issues:
            try:
                ledger = itinerary(after['graph'], suffix, after['inventory'] or [], after['action_points'], new_start, after['passive_items'] or [])
                for move in ledger['steps']:
                    if move['status'] != 'conditional_reference_step' or move.get('payment_zero_boundary') or move.get('unknown_ap_components'):
                        issues.append({'step': matched + move['step'], 'node_id': move['target'], 'reason': move.get('reason') or ledger['stopped_reason'] or 'action_points_unknown'})
            except ValueError as exc:
                issues.append({'step': matched + 1, 'node_id': suffix[0]['target'], 'reason': 'suffix_declaration_not_evaluable', 'detail': str(exc)})
        suffix_review = {'status': 'declared_target_already_reached' if not suffix else 'blocked_or_unknown' if issues else 'closed_movement_reference',
                         'steps': suffix, 'ledger': ledger, 'blocked_or_unknown_rows': issues,
                         'failure_continuation_condition_matches': continue_after_failure_declared if failures else True,
                         'old_battle_declarations_reused': False, 'actual_continuation_verified': False}
    alternatives = None
    if remaining_policy is not None and not frontier:
        if after['inventory'] is None or after['passive_items'] is None:
            frontier.append({'node_id': new_start, 'reason': 'fresh_inventory_or_passive_snapshot_unknown'})
        elif goal == new_start:
            status = 'declared_target_reached' if not remaining_policy['required_nodes'] and not remaining_policy['checkpoints'] else 'same_goal_reentry_unverified'
        else:
            try:
                alternatives = constrained_routes(after['graph'], goal, inventory=after['inventory'], action_points=after['action_points'],
                    passive_items=after['passive_items'], **remaining_policy, max_steps=max_steps, max_results=max_results, max_transitions=max_transitions)
                status = 'bounded_replanning_complete'
            except ValueError as exc:
                frontier.append({'node_id': new_start, 'reason': 'residual_policy_conflict', 'detail': str(exc)})
    if status is None:
        status = 'replanning_conditions_unknown' if frontier else 'replanning_not_evaluated'
    return {'scope': 'declared_progress_fresh_snapshot_route_continuation', 'start_before': old_start, 'start_after': new_start,
            'goal_before': plan['steps'][-1]['target'], 'goal_after': goal, 'before_snapshot': deepcopy(before), 'after_snapshot': deepcopy(after),
            'scope_identity_match': scope_match, 'matched_completed_prefix_count': matched, 'progress_rows': rows,
            'anchor_status': anchor_status, 'failed_battle_steps_declared': failures, 'continue_after_failure_declared': continue_after_failure_declared,
            'remaining_objectives': remaining_policy, 'source_prefix_reference': prefix_reference, 'source_prefix_unknown_reason': prefix_error,
            'state_differences': differences, 'remaining_plan_review': suffix_review, 'replanning_status': status,
            'replanning_origin': origin, 'alternatives': alternatives, 'replanning_frontier': frontier,
            'goal_source': 'explicit_after_goal' if goal_after is not None else 'original_goal_with_checked_binding',
            'actual_goal_completed': None, 'actual_best_route': None, 'inventory_updated': False, 'actual_gameplay_verified': False,
            'source': deepcopy(reference_data()['source']), 'limits': [
                '移动完成、战斗结果、新图当前位置、AP和库存各自独立声明，不由胜利或名义计划写回任何实际状态。',
                '只有连续匹配且明确完成的前缀可消解人工必经/顺序要求；不是游戏结局前置或真实成功证明。',
                '地图实例声明ID、区域/模板、节点ID和坐标须核对；同模板的新实例、无锚定或进度缺口不搬运旧目标。',
                '新区域可独立明确新目标及完整人工要求后规划；这个重置不证明原路线或结局完成。',
                '失败后的继续资格未知时保留前沿；失败或胜利不自动扣生命、AP、更新库存、完成节点或驱逐居民。',
                '原余路逐条核对新连线/实例，旧战斗身份不自动作为新图事实；替代路线仅声明图有限候选。',
                'AP/次数差值只比较名义来源分项与新声明，原因未知，不把偏差归因于机制或测试通过。',
                '库存/概念体新快照未知不借旧预测补全；上限、付款到零、未知资格保留，不赋概率或真实最优。']}
