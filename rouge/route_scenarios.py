"""Explicit finite-state route sensitivity, never a stochastic route optimum."""
from copy import deepcopy

from .route_resource_ledger import route_resource_ledger, _declarations
from .route_resident_review import review_resident_routes


SCENARIO_FIELDS = {'id', 'name', 'action_points', 'inventory', 'passive_items', 'residents',
                   'risk_policy', 'activation_declarations', 'after_battle_declarations',
                   'terminals', 'difficulty', 'split_unlocked'}


def _validate_routes(graph, nodes, adjacency, initial, routes):
    from .base_settlement_planning import settlements
    if not isinstance(routes, list) or not 1 <= len(routes) <= 20:
        raise ValueError('状态对照需要1–20条明确路线。')
    identities = set()
    for route in routes:
        if (not isinstance(route, dict) or set(route) - {'id', 'name', 'steps'} or
                not isinstance(route.get('id'), str) or not route['id'] or route['id'] in identities or
                not isinstance(route.get('name', route['id']), str) or not route.get('name', route['id'])):
            raise ValueError('路线需要唯一非空id、可选文字name，仅支持id/name/steps。')
        identities.add(route['id']); steps = route.get('steps')
        if not isinstance(steps, list) or not 1 <= len(steps) <= 10:
            raise ValueError('每条状态对照路线需要1–10步。')
        cursor = initial
        for step in steps:
            if (not isinstance(step, dict) or set(step) - {'mode', 'target', 'battle'} or
                    not isinstance(step.get('mode'), str) or not step['mode'] or
                    not isinstance(step.get('target'), str) or step['target'] not in nodes):
                raise ValueError('步骤只支持图中target、非空mode及独立battle。')
            if step['mode'] == 'walking' and step['target'] not in adjacency[cursor]:
                raise ValueError('多状态居民核对需逐条相邻步行连线声明；多格或同格步行时钟未证。')
            if 'battle' in step:
                if not isinstance(step['battle'], dict) or 'target' in step['battle']:
                    raise ValueError('独立battle对象不可改写target。')
                settlements([{'target': step['target'], **deepcopy(step['battle'])}], graph)
            cursor = step['target']


def _validate_inventory(value, label):
    from .exploration_planning import _item
    if value is None:
        return
    if not isinstance(value, list) or len(value) > 100:
        raise ValueError(label + '必须显式给出至多100项列表或null（未知）；不自动用默认库存代替。')
    ids = set()
    for ordinal, item in enumerate(value, 1):
        if not isinstance(item, dict) or set(item) - {'instance_id', 'item_id', 'remaining_uses'}:
            raise ValueError(label + '只支持加工品instance_id/item_id/remaining_uses。')
        source = _item(item.get('item_id'), 'MOVE'); identity = item.get('instance_id', 'inventory:' + str(ordinal))
        if not isinstance(identity, str) or not identity or identity == 'walking' or identity in ids:
            raise ValueError(label + '实例id需唯一非空且不能占用walking。')
        ids.add(identity); count = item.get('remaining_uses')
        if count is not None and (type(count) is not int or not 0 <= count <= source['raw']['count']):
            raise ValueError(label + '余次数需原件范围内整数或null。')


def _validate_passives(value):
    from .exploration_planning import _item
    if value is None:
        return
    if not isinstance(value, list) or len(value) > 6:
        raise ValueError('passive_items需显式列表或null（快照未知）。')
    seen = set()
    for row in value:
        if not isinstance(row, dict) or set(row) - {'item_id', 'remaining_activations'}:
            raise ValueError('概念体仅支持item_id及remaining_activations。')
        item = _item(row.get('item_id'), 'PASSIVE'); key = item['id']; count = row.get('remaining_activations')
        if key in seen:
            raise ValueError('同名概念体多来源叠加未证。')
        seen.add(key)
        if count is not None and (type(count) is not int or count < 0 or
                (key in ('rogue_6_scrap_P_01', 'rogue_6_scrap_P_02', 'rogue_6_scrap_P_03') and count > 1)):
            raise ValueError('概念体次数需来源范围内整数或null。')


def _validate_terminals(graph, nodes, routes, value):
    from .exploration_planning import region_transition, _type_candidates
    if value is None:
        return
    if not isinstance(value, dict):
        raise ValueError('terminals需要路线id到独立转移声明对象。')
    by_id = {route['id']: route for route in routes}
    for identity, row in value.items():
        if (identity not in by_id or not isinstance(row, dict) or set(row) - {'transition', 'success_declared', 'exit_node_type'} or
                'success_declared' not in row or (row['success_declared'] is not None and type(row['success_declared']) is not bool)):
            raise ValueError('转移必须绑定已有路线及独立success_declared。')
        if row.get('transition') == 'main_region_advance' and _type_candidates(nodes[by_id[identity]['steps'][-1]['target']])[0] != [row.get('exit_node_type')]:
            raise ValueError('主区域出口类型与该路线明确终点不符。')
        region_transition(row.get('transition'), remaining_ap=None, exit_node_type=row.get('exit_node_type'), goal_success=row['success_declared'])


def scenario_route_matrix(graph, routes, scenarios):
    from .exploration_planning import _graph, _adjacency, reference_data, resident_candidates
    nodes, initial = _graph(graph); adjacency = _adjacency(graph, nodes)
    if len(nodes) > 100:
        raise ValueError('状态对照仅支持至多100个声明节点。')
    _validate_routes(graph, nodes, adjacency, initial, routes)
    if not isinstance(scenarios, list) or not 1 <= len(scenarios) <= 10:
        raise ValueError('需要1–10个独立显式状态，不从区间或概率生成隐藏状态。')
    seen = set(); passive_catalog = {key for key, row in reference_data()['items'].items() if row['kind'] == 'PASSIVE'}
    for case in scenarios:
        if (not isinstance(case, dict) or set(case) - SCENARIO_FIELDS or
                not isinstance(case.get('id'), str) or not case['id'] or case['id'] in seen or
                not isinstance(case.get('name', case['id']), str) or not case.get('name', case['id']) or
                any(key not in case for key in ('action_points', 'inventory', 'passive_items'))):
            raise ValueError('每个状态需唯一id及显式action_points/inventory/passive_items；name可选。')
        seen.add(case['id']); ap = case['action_points']
        if ap is not None and (type(ap) is not int or ap < 0):
            raise ValueError('状态行动力需要非负整数或null。')
        _validate_inventory(case['inventory'], '状态库存'); _validate_passives(case['passive_items'])
        allowed = passive_catalog if case['passive_items'] is None else {row['item_id'] for row in case['passive_items']}
        _declarations(case.get('activation_declarations'), routes, 'activation_declarations', allowed)
        _declarations(case.get('after_battle_declarations'), routes, 'after_battle_declarations')
        _validate_terminals(graph, nodes, routes, case.get('terminals'))
        policy = case.get('risk_policy', 'show_all')
        if policy not in ('show_all', 'avoid_candidate_overlap'):
            raise ValueError('risk_policy需show_all或avoid_candidate_overlap。')
        if case.get('residents') is not None:
            if not isinstance(case['residents'], list) or len(case['residents']) > 3:
                raise ValueError('居民快照需0–3项列表或null（未知）。')
            # Validate identity/positions even if every plan is blocked by stock.
            if any(not isinstance(row, dict) or set(row) - {'id', 'node_id'} for row in case['residents']):
                raise ValueError('居民快照只支持id及图中node_id。')
            resident_candidates(graph, residents=case['residents'], moves=1)
        if case.get('difficulty') is not None and (type(case['difficulty']) is not int or case['difficulty'] < 0):
            raise ValueError('状态保密等级需非负整数或null。')
        if case.get('split_unlocked') is not None and type(case['split_unlocked']) is not bool:
            raise ValueError('split_unlocked需true/false/null。')
    cases = []
    for case in scenarios:
        rows = []; inventory = case['inventory']; passives = case['passive_items']
        stock_ids = {row.get('instance_id', 'inventory:' + str(ordinal)) for ordinal, row in enumerate(inventory or [], 1)}
        for route in routes:
            planned = {step['mode'] for step in route['steps'] if step['mode'] != 'walking'}
            missing = sorted(planned - stock_ids)
            row = {'route_id': route['id'], 'movement_status': None, 'movement_stop_reason': None,
                   'missing_planned_instances': missing, 'resource_reference': None, 'resident_reference': None,
                   'risk_policy_match': None, 'quantity_conditions_closed': False, 'unknown_reasons': []}
            if inventory is None:
                row['unknown_reasons'].append('inventory_snapshot_unknown')
            if passives is None:
                row['unknown_reasons'].append('passive_snapshot_unknown')
            if case.get('residents') is None:
                row['unknown_reasons'].append('resident_snapshot_unknown')
            if missing:
                row['movement_status'] = 'unknown_declared_inventory' if inventory is None else 'blocked_declared_inventory'
                row['movement_stop_reason'] = 'planned_instance_not_confirmed' if inventory is None else 'planned_instance_absent_from_explicit_snapshot'
                row['missing_mode_steps'] = [{'step': ordinal, 'instance_id': step['mode']} for ordinal, step in enumerate(route['steps'], 1) if step['mode'] in missing]
                row['unknown_reasons'].append('route_ledger_not_evaluated_after_missing_instance')
                first_missing = row['missing_mode_steps'][0]['step']
                row['evaluated_prefix_step_count'] = first_missing - 1
                if first_missing > 1:
                    prefix = {**deepcopy(route), 'steps': deepcopy(route['steps'][:first_missing - 1])}
                    prefix_args = {'graph': graph, 'routes': [prefix], 'inventory': inventory or [],
                                   'passive_items': passives or [], 'action_points': case['action_points'],
                                   'difficulty': case.get('difficulty'), 'split_unlocked': case.get('split_unlocked')}
                    for field in ('activation_declarations', 'after_battle_declarations'):
                        declarations = (case.get(field) or {}).get(route['id'], {})
                        prefix_args[field] = {route['id']: {key: deepcopy(value) for key, value in declarations.items() if int(key) < first_missing}}
                    if passives is None: prefix_args['activation_declarations'] = {}
                    partial = route_resource_ledger(**prefix_args)
                    partial['prefix_only'] = True; partial['planned_full_goal'] = route['steps'][-1]['target']
                    partial['routes'][0]['complete_modeled_grant_conditions'] = False
                    partial['routes'][0]['conditional_combined_component_total'] = None
                    partial['routes'][0]['unknown_snapshot_components'] = [reason for reason in row['unknown_reasons'] if reason.endswith('snapshot_unknown')]
                    row['resource_reference'] = partial
                    if case.get('residents') is not None:
                        row['resident_reference'] = review_resident_routes(graph, [prefix], case['residents'], inventory=inventory or [],
                            action_points=case['action_points'], passive_items=passives or [], difficulty=case.get('difficulty'),
                            split_unlocked=case.get('split_unlocked'), risk_policy=case.get('risk_policy', 'show_all'))
                        row['resident_reference']['prefix_only'] = True
                if case.get('risk_policy', 'show_all') == 'show_all': row['risk_policy_match'] = True
                rows.append(row); continue
            arguments = {'graph': graph, 'routes': [route], 'inventory': inventory or [], 'passive_items': passives or [],
                         'action_points': case['action_points'], 'difficulty': case.get('difficulty'),
                         'split_unlocked': case.get('split_unlocked')}
            for field in ('activation_declarations', 'after_battle_declarations', 'terminals'):
                value = case.get(field) or {}
                arguments[field] = {route['id']: deepcopy(value[route['id']])} if route['id'] in value else {}
            if passives is None:
                arguments['activation_declarations'] = {}
            resource = route_resource_ledger(**arguments); ref = resource['routes'][0]
            if inventory is None or passives is None:
                # Empty scratch inputs allow evaluation of independently known
                # walking/movement sources only; qualify the nested result too
                # so no consumer sees an unknown snapshot as a closed zero.
                missing_snapshots = [label for value, label in ((inventory, 'inventory_snapshot_unknown'),
                                                                (passives, 'passive_snapshot_unknown')) if value is None]
                ref['unknown_snapshot_components'] = missing_snapshots
                ref['complete_modeled_grant_conditions'] = False
                ref['conditional_combined_component_total'] = None
                resource['scenario_snapshot_qualification'] = missing_snapshots
            row['resource_reference'] = resource
            movement = ref['movement_and_base_reference']['movement_reference']
            blocked = next((move for move in movement['steps'] if move['status'] == 'blocked'), None)
            row['movement_status'] = ('closed' if movement['complete_declared_conditions'] else
                                      'blocked_movement_reference' if blocked else 'unknown_movement_reference')
            row['movement_stop_reason'] = movement['stopped_reason']
            row['quantity_conditions_closed'] = ref['complete_modeled_grant_conditions'] and inventory is not None and passives is not None
            if not ref['complete_modeled_grant_conditions']:
                row['unknown_reasons'].append('source_grants_or_terminal_not_closed')
            if case.get('residents') is not None:
                risk = review_resident_routes(graph, [route], case['residents'], inventory=inventory or [],
                                              action_points=case['action_points'], passive_items=passives or [],
                                              difficulty=case.get('difficulty'), split_unlocked=case.get('split_unlocked'),
                                              risk_policy=case.get('risk_policy', 'show_all'))
                row['resident_reference'] = risk; review = risk['routes'][0]
                row['risk_policy_match'] = (True if case.get('risk_policy', 'show_all') == 'show_all' else
                                            False if review['excluded_by_declared_risk_policy'] else
                                            None if review['navigation_unknown_steps'] or review['movement_stop_step'] is not None else True)
                if review['navigation_unknown_steps']:
                    row['unknown_reasons'].append('resident_navigation_unknown')
            elif case.get('risk_policy', 'show_all') == 'show_all':
                row['risk_policy_match'] = True
            rows.append(row)
        cases.append({'scenario_id': case['id'], 'scenario_name': case.get('name', case['id']),
                      'scenario_input': deepcopy(case), 'routes': rows})
    summaries = []
    for route in routes:
        paired = [(case, next(row for row in case['routes'] if row['route_id'] == route['id'])) for case in cases]
        movement_ids = [case['scenario_id'] for case, row in paired if row['movement_status'] == 'closed']
        quantity_ids = [case['scenario_id'] for case, row in paired if row['quantity_conditions_closed']]
        rejected = [case['scenario_id'] for case, row in paired if row['risk_policy_match'] is False]
        unknown_ids = [case['scenario_id'] for case, row in paired if row['unknown_reasons'] or 'unknown' in row['movement_status'] or row['risk_policy_match'] is None]
        envelope = None
        if len(quantity_ids) == len(cases):
            values = [row['resource_reference']['routes'][0]['conditional_combined_component_total'] for _, row in paired]
            envelope = {key: {'minimum': min(value[key] for value in values), 'maximum': max(value[key] for value in values)} for key in values[0] if key != 'gold'}
            envelope['gold'] = {'minimum': min(value['gold']['minimum'] for value in values), 'maximum': max(value['gold']['maximum'] for value in values)}
        witnesses = []
        for ordinal, (left_case, left) in enumerate(paired):
            for right_case, right in paired[ordinal + 1:]:
                changed = [key for key in ('movement_status', 'movement_stop_reason', 'missing_planned_instances', 'risk_policy_match', 'quantity_conditions_closed') if left[key] != right[key]]
                left_quantity = (left['resource_reference'] or {}).get('routes', [{}])[0].get('known_combined_component_subtotal')
                right_quantity = (right['resource_reference'] or {}).get('routes', [{}])[0].get('known_combined_component_subtotal')
                if left_quantity != right_quantity:
                    changed.append('known_component_subtotal')
                if changed:
                    witnesses.append({'left_scenario_id': left_case['scenario_id'], 'right_scenario_id': right_case['scenario_id'],
                                      'changed_fields': changed, 'case_inputs_preserved': True})
        summaries.append({'route_id': route['id'], 'name': route.get('name', route['id']),
                          'all_declared_movement_conditions_closed': len(movement_ids) == len(cases),
                          'all_modeled_quantity_conditions_closed': len(quantity_ids) == len(cases),
                          'all_declared_risk_policy_matches': all(row['risk_policy_match'] is True for _, row in paired),
                          'all_declared_compound_conditions_closed': all(row['movement_status'] == 'closed' and row['quantity_conditions_closed'] and row['risk_policy_match'] is True for _, row in paired),
                          'closed_quantity_envelope': envelope, 'movement_closed_scenario_ids': movement_ids,
                          'quantity_closed_scenario_ids': quantity_ids, 'policy_rejected_scenario_ids': rejected,
                          'unknown_scenario_ids': unknown_ids, 'sensitivity_witnesses': witnesses,
                          'actual_feasible': None, 'actual_safe': None})
    comparisons = []
    for ordinal, left in enumerate(routes):
        for right in routes[ordinal + 1:]:
            relations = []
            for case in cases:
                arow = next(row for row in case['routes'] if row['route_id'] == left['id']); brow = next(row for row in case['routes'] if row['route_id'] == right['id'])
                reason, relation, difference = None, None, None
                terminal = case['scenario_input'].get('terminals') or {}
                if left['steps'][-1]['target'] != right['steps'][-1]['target'] or terminal.get(left['id']) != terminal.get(right['id']):
                    reason = 'different_goal_or_terminal_declaration'
                elif not arow['quantity_conditions_closed'] or not brow['quantity_conditions_closed']:
                    reason = 'compound_case_quantities_not_closed'
                elif arow['risk_policy_match'] is not True or brow['risk_policy_match'] is not True:
                    reason = 'declared_risk_policy_not_matched'
                else:
                    a = arow['resource_reference']['routes'][0]; b = brow['resource_reference']['routes'][0]
                    av, bv = a['conditional_combined_component_total'], b['conditional_combined_component_total']
                    # Only deterministic named quantity axes. Random-item quality
                    # and value never become an order relation.
                    axes = ('hope_grant_quantity', 'shield_grant_quantity', 'base_experience')
                    difference = {key: av[key] - bv[key] for key in axes}
                    difference['gold_interval'] = {'minimum': av['gold']['minimum'] - bv['gold']['maximum'], 'maximum': av['gold']['maximum'] - bv['gold']['minimum']}
                    ap_a = a['movement_and_base_reference']['net_ap_consumption_reference']; ap_b = b['movement_and_base_reference']['net_ap_consumption_reference']
                    difference['net_ap_consumption'] = ap_a - ap_b
                    relation = all(av[key] >= bv[key] for key in axes) and av['gold']['minimum'] >= bv['gold']['maximum'] and ap_a <= ap_b
                    reason = 'closed_declared_component_rule' if relation else 'conservative_component_rule_not_satisfied'
                relations.append({'scenario_id': case['scenario_id'], 'relation': relation, 'reason': reason,
                                  'component_difference': difference, 'actual_better_route': None})
            comparisons.append({'left': left['id'], 'right': right['id'], 'case_relations': relations,
                                'declared_component_nonworse_across_all_cases': None if any(row['relation'] is None for row in relations) else all(row['relation'] for row in relations),
                                'random_item_value_comparable': False, 'actual_better_route': None})
    return {'scope': 'bounded_explicit_scenario_route_component_matrix', 'start': initial,
            'cases': cases, 'route_summaries': summaries, 'pairwise_robust_component_comparisons': comparisons,
            'scenario_count': len(cases), 'route_count': len(routes), 'probability': None,
            'actual_best_route': None, 'actual_gameplay_verified': False, 'inventory_updated': False,
            'source': deepcopy(reference_data()['source']), 'limits': [
                '只核对明确列出的有限状态，不从区间补全真实状态、概率或全部可发生局面。',
                '库存、概念体和居民null表示快照未知，空列表必须独立明确声明；不互借状态库存或替换缺失实例。',
                '每条路线每个状态独立计算，保留原输入、完整分项账本、风险阶段与敏感性见证。',
                '任一复合状态的数量条件未知时，跨状态包络保持未知，不能用其余状态或零填充。',
                '最小/最大只是全部已列且闭合状态的条件数量范围，不是期望收益、实际最坏情况或效用。',
                '稳健分项关系仅同终点/独立转移、所有所列条件闭合且偏好匹配；随机品价值不排序。',
                '居民候选偏好不是安全证明；真实可达、失败概率、完整奖励与最优路线仍未知。']}
