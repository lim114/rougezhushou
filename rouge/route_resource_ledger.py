"""Finite plan grant quantities with independently declared passive/exit phases.

Documented quantities never become actual receipts or complete reward pools.
Possible single-use activation propagates uncertain remaining availability.
"""
from copy import deepcopy

from .route_comparison import compare_routes


RESOURCES = ('hope', 'gold', 'shield', 'random_relic', 'random_move_item')


def _declarations(value, routes, label, passive_ids=None):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(label + '需要路线id到步骤序号对象。')
    by_id = {row['id']: row for row in routes}
    for identity, steps in value.items():
        if identity not in by_id or not isinstance(steps, dict):
            raise ValueError(label + '必须绑定已有路线id。')
        for ordinal, declaration in steps.items():
            if (not isinstance(ordinal, str) or not ordinal.isdigit() or str(int(ordinal)) != ordinal or
                    not 1 <= int(ordinal) <= len(by_id[identity]['steps'])):
                raise ValueError(label + '步骤键需要1起的有效文字整数。')
            if passive_ids is None:
                if declaration is not None and type(declaration) is not bool:
                    raise ValueError(label + '每步需要true/false/null。')
            elif (not isinstance(declaration, dict) or any(key not in passive_ids or
                    (match is not None and type(match) is not bool) for key, match in declaration.items())):
                raise ValueError(label + '每步需要所声明概念体id到true/false/null的对象。')
    return deepcopy(value)


def route_resource_ledger(graph, routes, *, inventory=None, passive_items=None,
                          action_points=None, start=None, difficulty=None,
                          split_unlocked=None, activation_declarations=None,
                          after_battle_declarations=None, terminals=None):
    from .exploration_planning import (_graph, _type_candidates, _item, movement_effects,
                                       region_transition, reference_data)
    nodes, initial = _graph(graph, start)
    comparison = compare_routes(graph, routes, inventory=inventory, action_points=action_points,
                                start=initial, passive_items=passive_items,
                                difficulty=difficulty, split_unlocked=split_unlocked)
    if passive_items is None:
        passive_items = []
    if not isinstance(passive_items, list) or len(passive_items) > 6:
        raise ValueError('概念体需要至多6种固定目录声明。')
    ids = set()
    for row in passive_items:
        if not isinstance(row, dict) or set(row) - {'item_id', 'remaining_activations'}:
            raise ValueError('概念体只支持item_id及remaining_activations。')
        item = _item(row.get('item_id'), 'PASSIVE'); key = item['id']
        if key in ids:
            raise ValueError('同种概念体重复来源叠加未证，不能合并计算。')
        ids.add(key)
        count = row.get('remaining_activations')
        if count is not None and (type(count) is not int or count < 0):
            raise ValueError('概念体余激活次数需要非负整数或null。')
        if key in ('rogue_6_scrap_P_01', 'rogue_6_scrap_P_02', 'rogue_6_scrap_P_03') and count is not None and count > 1:
            raise ValueError('一次性概念体余次数不可超过1。')
    activations = _declarations(activation_declarations, routes, 'activation_declarations', ids)
    after_battles = _declarations(after_battle_declarations, routes, 'after_battle_declarations')
    if terminals is None:
        terminals = {}
    if not isinstance(terminals, dict):
        raise ValueError('terminals需要路线id到独立转移声明。')
    by_id = {row['id']: row for row in routes}
    for identity, declaration in terminals.items():
        if (identity not in by_id or not isinstance(declaration, dict) or
                set(declaration) - {'transition', 'success_declared', 'exit_node_type'} or
                'success_declared' not in declaration or
                (declaration['success_declared'] is not None and type(declaration['success_declared']) is not bool)):
            raise ValueError('转移声明只支持已有路线的transition、success_declared及主区域exit_node_type。')
        exit_type = declaration.get('exit_node_type')
        target = by_id[identity]['steps'][-1]['target']
        if declaration.get('transition') == 'main_region_advance' and _type_candidates(nodes[target])[0] != [exit_type]:
            raise ValueError('主区域转移exit_node_type须与该路线终点明确原类型一致。')
        region_transition(declaration.get('transition'), remaining_ap=None,
                          exit_node_type=exit_type, goal_success=declaration['success_declared'])
    outputs = []
    for reference in comparison['routes']:
        passives = deepcopy(passive_items); grants, unknowns, excluded, conflicts = [], [], [], []
        sums = {resource: 0 for resource in RESOURCES}
        movement = reference['movement_reference']

        def record(ordinal, target, resource, quantity, condition, origin, **details):
            row = {'step': ordinal, 'node_id': target, 'resource': resource,
                   'source_stated_quantity': quantity, 'condition_matches': condition,
                   'origin': origin, 'admitted_to_known_source_quantity': condition is True,
                   'actual_received': None, **details}
            grants.append(row)
            if condition is True:
                sums[resource] += quantity
            elif condition is None:
                unknowns.append({'step': ordinal, 'node_id': target, 'resource': resource,
                                 'origin': origin, 'reason': details.get('unresolved_reason') or 'grant_condition_unknown'})
            else:
                excluded.append({'step': ordinal, 'node_id': target, 'resource': resource,
                                 'origin': origin, 'reason': details.get('unresolved_reason') or 'declared_or_source_condition_failed'})

        for move in movement['steps']:
            ordinal, target = move['step'], move['target']
            option = move.get('option') or move.get('independent_declared_option_reference') or {}
            arrival = (move['status'] == 'conditional_reference_step' and
                       move.get('nominal_ap_after_payment') is not None and
                       move.get('payment_zero_boundary') is False and not move.get('unknown_ap_components'))
            if option.get('mode') != 'processed_item':
                continue
            if arrival:
                effects = movement_effects(graph, option['item_id'], target, move['start'],
                                           option['remaining_uses_declared'], passives)
            else:
                # Preserve independently source-stated effects on stopped tails,
                # with no contribution or depletion across unresolved movement.
                effects = {'movement_grants': option.get('movement_grants', []),
                           'passives': option.get('passives', [])}
            for grant in effects['movement_grants']:
                if grant['resource'] in RESOURCES:
                    condition = grant['condition_matches'] if arrival else None
                    record(ordinal, target, grant['resource'], grant['amount'], condition,
                           'processed_item', item_id=option.get('item_id'), source_selector=grant['source_selector'],
                           unresolved_reason=None if arrival else 'movement_chain_unresolved')
            for passive in effects['passives']:
                key = passive['item_id']
                activation = activations.get(reference['id'], {}).get(str(ordinal), {}).get(key)
                gate = passive['condition_matches']
                if arrival and gate is False and activation is True:
                    conflicts.append({'step': ordinal, 'node_id': target, 'item_id': key,
                                      'reason': 'declared_activation_conflicts_with_source_gate'})
                from .exploration_planning import _and
                active = _and(gate, activation) if arrival else None
                before = next(row for row in passives if row['item_id'] == key).get('remaining_activations')
                after_battle = after_battles.get(reference['id'], {}).get(str(ordinal))
                for effect in passive['effects']:
                    if effect['resource'] not in RESOURCES:
                        continue  # Combat-only attack speed remains reference information.
                    condition = _and(active, after_battle) if effect.get('timing') == 'after_battle' else active
                    reason = ('movement_chain_unresolved' if not arrival else
                              'after_battle_completion_not_declared' if effect.get('timing') == 'after_battle' and after_battle is None else
                              'passive_activation_not_declared' if activation is None else
                              'passive_availability_or_type_unknown' if gate is None else None)
                    record(ordinal, target, effect['resource'], effect['amount'], condition, 'passive',
                           item_id=key, source_selector=passive['source_selector'],
                           source_gate_matches=gate, activation_declared=activation,
                           after_battle_completed_declared=after_battle if effect.get('timing') == 'after_battle' else None,
                           availability_before_reference=before, unresolved_reason=reason,
                           random_pool_known=False if effect['resource'] == 'random_relic' else None)
                if passive['source_stated_single_activation'] and arrival:
                    entry = next(row for row in passives if row['item_id'] == key)
                    if active is True:
                        entry['remaining_activations'] -= 1
                    elif active is None:
                        entry['remaining_activations'] = None
        terminal = None
        if reference['id'] in terminals:
            declaration = terminals[reference['id']]
            stock = [deepcopy(row) for row in movement['inventory_reference_state'] if row.get('remaining_uses') != 0]
            used_ids = {row['instance_id'] for row in stock}
            for row in passives:
                base_id = 'passive:' + row['item_id']; generated_id = base_id; suffix = 2
                while generated_id in used_ids:
                    generated_id = base_id + ':' + str(suffix); suffix += 1
                used_ids.add(generated_id)
                stock.append({'instance_id': generated_id, 'item_id': row['item_id']})
            source = region_transition(declaration['transition'], stock,
                                       movement['nominal_final_ap'] if movement['complete_declared_conditions'] else None,
                                       declaration.get('exit_node_type'), declaration['success_declared'])
            unresolved_dispositions = []
            if declaration['transition'] == 'portal_return':
                # The current saved cards differ: M04 explicitly says entering
                # OR leaving; M07 only says entering. Do not broaden the latter
                # by inheriting the old ledger's missing-cache source claim.
                for item in source['inventory_conditions']:
                    if item['item_id'] == 'rogue_6_scrap_M_07':
                        item['preserved_by_portal_exception'] = None
                        unresolved_dispositions.append({'instance_id': item['instance_id'], 'item_id': item['item_id'],
                                                        'reason': 'm07_portal_return_disposition_unverified'})
                uncertain = {row['instance_id'] for row in unresolved_dispositions}
                source['preserved_by_explicit_portal_exception'] = [key for key in source['preserved_by_explicit_portal_exception'] if key not in uncertain]
            source['temporary_item_exception_qualification'] = {
                'revision': 434637, 'receipt': 'research/p3-route-continuation/resources/source-receipt.json',
                'M04': '不会因进入或离开误入奇境节点的特殊层而损坏',
                'M07': '不会因进入误入奇境节点的特殊层而损坏',
                'm07_return_verified': False}
            admitted = movement['complete_declared_conditions'] and declaration['success_declared'] is True
            terminal = {'declaration': deepcopy(declaration), 'reference': source,
                        'admitted_to_conditional_terminal_phase': admitted,
                        'conditional_expired_instances': source['losses_if_transition_succeeds'] if admitted else [],
                        'conditional_portal_preserved_instances': source['preserved_by_explicit_portal_exception'] if admitted else [],
                        'unresolved_inventory_dispositions': unresolved_dispositions,
                        'actual_transition_completed': None, 'actual_inventory_after': None}
            if declaration['transition'] == 'main_region_advance' and declaration.get('exit_node_type') in ('FINAL', 'BATTLE_BOSS'):
                amount = source['resources'].get('hope_gain_reference')
                failed = declaration['success_declared'] is False
                condition = False if failed else True if admitted and amount is not None else None
                record(len(reference['declared_steps']), reference['goal_node'], 'hope', amount,
                       condition, 'terminal_conversion', unresolved_reason='boss_conversion_ratio_unknown' if declaration.get('exit_node_type') == 'BATTLE_BOSS' else
                       'terminal_success_or_movement_unknown' if condition is None else None,
                       conversion_ratio_reference=source['resources']['hope_conversion_ratio'])
            for grant in source['resources']['named_item_grants']:
                record(len(reference['declared_steps']), reference['goal_node'], 'random_move_item', grant['quantity'],
                       False if declaration['success_declared'] is False else True if admitted else None,
                       'terminal_item_grant', random_pool_known=False,
                       unresolved_reason='terminal_success_or_movement_unknown' if not admitted else None)
        base = reference['known_base_subtotal']
        combined = {'hope_grant_quantity': sums['hope'], 'shield_grant_quantity': sums['shield'],
                    'random_relic_quantity': sums['random_relic'], 'random_move_item_quantity': sums['random_move_item'],
                    'base_experience': base['experience'],
                    'gold': {'minimum': base['gold']['minimum'] + sums['gold'],
                             'maximum': base['gold']['maximum'] + sums['gold']}}
        closed = not unknowns and not conflicts and reference['closed_declared_component_reference'] and (
            terminal is None or (terminal['admitted_to_conditional_terminal_phase'] and not terminal['unresolved_inventory_dispositions']))
        outputs.append({'id': reference['id'], 'name': reference['name'], 'goal_node': reference['goal_node'],
                        'declared_steps': deepcopy(reference['declared_steps']), 'grant_rows': grants,
                        'known_source_grant_subtotal': sums, 'unknown_grant_components': unknowns,
                        'excluded_grant_components': excluded, 'passive_availability_reference_state': passives,
                        'passive_budget_scope': 'independent_explicit_activation_declaration_ledger',
                        'declaration_conflicts': conflicts,
                        'terminal_phase': terminal, 'movement_and_base_reference': deepcopy(reference),
                        'known_combined_component_subtotal': combined,
                        'conditional_combined_component_total': deepcopy(combined) if closed else None,
                        'complete_modeled_grant_conditions': closed, 'actual_final_resources': None,
                        'complete_reward_pool_known': False, 'actual_received_rewards': None})
    differences = []
    for ordinal, left in enumerate(outputs):
        for right in outputs[ordinal + 1:]:
            a, b = left['known_combined_component_subtotal'], right['known_combined_component_subtotal']
            delta = {key: a[key] - b[key] for key in a if key != 'gold'}
            delta['gold_interval'] = {'minimum': a['gold']['minimum'] - b['gold']['maximum'],
                                      'maximum': a['gold']['maximum'] - b['gold']['minimum']}
            same_terminal = ((left['terminal_phase'] or {}).get('declaration') ==
                             (right['terminal_phase'] or {}).get('declaration'))
            closed = (left['complete_modeled_grant_conditions'] and right['complete_modeled_grant_conditions'] and
                      left['goal_node'] == right['goal_node'] and same_terminal)
            differences.append({'left': left['id'], 'right': right['id'],
                                'known_subtotal_difference_left_minus_right': delta,
                                'conditional_component_difference': deepcopy(delta) if closed else None,
                                'same_declared_goal_and_terminal': left['goal_node'] == right['goal_node'] and same_terminal,
                                'actual_better_route': None, 'random_item_value_comparable': False})
    return {'scope': 'finite_declared_route_source_grant_and_terminal_ledger', 'start': initial,
            'routes': outputs, 'pairwise_component_differences': differences,
            'source': deepcopy(reference_data()['source']),
            'actual_best_route': None, 'actual_gameplay_verified': False, 'inventory_updated': False,
            'probability': None, 'limits': [
                '移动、概念体及出口只列固定文档的条件数量，实际激活、领取和完整奖励总量未知。',
                '概念体激活需独立逐步声明；战斗后收藏品另需独立战斗结束声明，不由经过或通关奖励推定。',
                '一次性概念体的可能激活会让后续余次数未知；已明确未激活保留次数，各路线账本独立。',
                '本账本的概念体余次数使用独立激活声明；旧移动账本的自动触发参考不充当实际激活或本账本余次数。',
                '随机收藏品数量可列，具名池、品质、价值和概率未知；战斗攻速不进入本资源账本。',
                '停止移动尾链只保留独立来源，不累计资源或消耗概念体；返还不能透支付款。',
                '转移成功需独立声明；FINAL原件等量希望仅1:1条件参考，首领比率和新区域总AP未知。',
                '耗尽加工品不再算持有损失；临时加工品跨主区域损坏和秘境进出保留分别列，实际库存不改写。',
                '固定配件文档明确重弹簧秘境进出不损坏；小八界只明确进入，返回后的处置仍未知，不借用旧缓存缺失的概括。',
                '合并小计仅基础战斗和所列资源授予，不含商店消费、事件、失败、动态居民与其它未建模收益。']}
