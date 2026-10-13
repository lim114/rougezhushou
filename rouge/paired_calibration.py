"""Compare independently declared before/after panels without causal inference.

The arithmetic comes from existing source-qualified panel layers. A matching
delta never certifies either absolute panel, a mechanism, or a game client.
"""
from copy import deepcopy

from .calibration import LABELS, BOUNDARY, _number, compare_panel, panel_layers
from .relic_panel_diagnostics import relic_panel_diagnostics


def _record(record, name):
    if not isinstance(record, dict) or set(record) != {'scenario', 'observation'}:
        raise ValueError(name + '需包含且仅包含 scenario 与 observation。')
    return deepcopy(record)


def _changes(left, right):
    return [{'field': key, 'before_present': key in left, 'after_present': key in right,
             'before': deepcopy(left.get(key)), 'after': deepcopy(right.get(key))}
            for key in sorted(set(left) | set(right))
            if key not in left or key not in right or left[key] != right[key]]


def _relic_transition(before_model, after_model, changes):
    """Link the existing diagnostics only for a declared relic-only transition."""
    out = {'available': False, 'reason': None, 'added_relic_ids': [],
           'removed_relic_ids': [], 'before_diagnostics': None,
           'after_diagnostics': None, 'actual_causal_attribution': None}
    if not changes:
        out['reason'] = 'no_declared_condition_change'
        return out
    if any(row['field'] != 'relic_ids' for row in changes):
        out['reason'] = 'other_declared_conditions_changed'
        return out
    before = before_model['context']['scenario']
    after = after_model['context']['scenario']
    left, right = before.get('relic_ids', []), after.get('relic_ids', [])
    for ids in (left, right):
        if (not isinstance(ids, list) or any(not isinstance(v, str) or not v for v in ids)
                or len(ids) != len(set(ids))):
            raise ValueError('前后藏品声明需为不重复的非空ID列表。')
    added = [rid for rid in right if rid not in left]
    removed = [rid for rid in left if rid not in right]
    out.update(added_relic_ids=added, removed_relic_ids=removed)
    if not added and not removed:
        out['reason'] = 'same_relic_membership_or_order_only'
        return out
    if len(added) > 12 or len(removed) > 12:
        out['reason'] = 'transition_exceeds_existing_diagnostic_limit'
        return out
    out['available'] = True
    if removed:
        out['before_diagnostics'] = relic_panel_diagnostics(before, removed)
    if added:
        out['after_diagnostics'] = relic_panel_diagnostics(after, added)
    return out


def compare_paired_panels(before, after, tolerance=0):
    """Compare shared observed fields across two independently matching contexts.

    ``before`` and ``after`` each contain ``scenario`` and ``observation``. Each
    observation uses the existing compare_panel contract, including its own
    context_token, panel, evidence_kind, source and nonnegative finite values.
    """
    _number(tolerance, 'tolerance')
    left, right = _record(before, '前组'), _record(after, '后组')
    before_model = panel_layers(left['scenario'])
    after_model = panel_layers(right['scenario'])
    if before_model['context']['scenario']['operator'] != after_model['context']['scenario']['operator']:
        raise ValueError('前后成对校准必须为同一干员。')
    # Validate both full observations, including fields later excluded from the
    # intersection. A malformed one-sided field must not disappear silently.
    before_comparison = compare_panel(left['scenario'], left['observation'], tolerance)
    after_comparison = compare_panel(right['scenario'], right['observation'], tolerance)
    if before_comparison['panel'] != after_comparison['panel']:
        raise ValueError('前后成对校准必须为同一面板层；不同层不能计算前后差。')
    if before_comparison['evidence_kind'] != after_comparison['evidence_kind']:
        raise ValueError('前后来源类别必须一致；公开算例、公式参考和游戏面板不能混合。')
    left_rows = {row['field']: row for row in before_comparison['rows']}
    right_rows = {row['field']: row for row in after_comparison['rows']}
    shared = [field for field in LABELS if field in left_rows and field in right_rows]
    if not shared:
        raise ValueError('前后记录没有共同观察字段，无法成对校准。')
    rows = []
    for field in shared:
        a, b = left_rows[field], right_rows[field]
        observed_delta = b['observed'] - a['observed']
        model_delta = None if a['predicted'] is None or b['predicted'] is None else b['predicted'] - a['predicted']
        residual = None if model_delta is None else observed_delta - model_delta
        delta_match = None if residual is None else abs(residual) <= tolerance
        absolute_match = None if model_delta is None else (
            a['matches_declared_tolerance'] is True and b['matches_declared_tolerance'] is True)
        status = ('model_field_unknown' if residual is None else 'delta_mismatch' if not delta_match
                  else 'delta_matches_but_absolute_panels_differ' if not absolute_match else 'paired_values_match')
        rows.append({'field': field, 'label': LABELS[field],
            'before_observed': a['observed'], 'after_observed': b['observed'],
            'before_model_reference': a['predicted'], 'after_model_reference': b['predicted'],
            'before_observation_minus_model': a['difference'],
            'after_observation_minus_model': b['difference'],
            'observed_after_minus_before': observed_delta,
            'model_after_minus_before': model_delta,
            'delta_residual': residual, 'delta_matches_declared_tolerance': delta_match,
            'both_absolute_values_match_declared_tolerance': absolute_match, 'diagnostic_status': status,
            'before_other_stage_matches': deepcopy(a['other_stage_matches']),
            'after_other_stage_matches': deepcopy(b['other_stage_matches']),
            'actual_cause_of_residual': None})
    changes = _changes(before_model['context']['scenario'], after_model['context']['scenario'])
    return {'scope': 'independently_declared_before_after_panel_calibration',
        'operator': before_model['operator'], 'panel': before_comparison['panel'],
        'evidence_kind': before_comparison['evidence_kind'], 'tolerance': tolerance,
        'before': {'comparison': before_comparison, 'model': before_model},
        'after': {'comparison': after_comparison, 'model': after_model},
        'changed_conditions': changes, 'rows': rows,
        'before_only_fields': [f for f in LABELS if f in left_rows and f not in right_rows],
        'after_only_fields': [f for f in LABELS if f in right_rows and f not in left_rows],
        'shared_field_count': len(rows),
        'known_model_delta_count': sum(r['model_after_minus_before'] is not None for r in rows),
        'all_compared_deltas_match': all(r['delta_matches_declared_tolerance'] is True for r in rows),
        'all_paired_absolute_values_match': all(r['both_absolute_values_match_declared_tolerance'] is True for r in rows),
        'relic_transition': _relic_transition(before_model, after_model, changes),
        'source': deepcopy(before_model['source']), 'native_verified': False,
        'actual_causal_attribution': None,
        'notes': [BOUNDARY,
            '前后分别核对条件标识、面板层、来源类别与来源；观察值由调用方独立声明，不自动从预测填入。',
            '只比较两侧共同观察字段；单侧字段不补零，模型未覆盖字段的模型差与残差保持未知。',
            '所有差值均为后减前；残差为观察差减模型差，不能反推未知机制或自动修正面板。',
            '前后绝对偏差相同也可能得到零残差；差值相符不等于两个面板都相符。',
            '容差分别用于两端绝对偏差和差值残差，不自动叠加两次容差。',
            '藏品联接只展示当前模型的移除/添加参考；定向强化独立保留，实际丢失和获取顺序未证。',
            '公开算例与公式参考不会升级为游戏面板证据；即使声明游戏面板，也不自动认证客户端或原生时钟。']}


def public_paired_payload(operator='mechanist'):
    """Small literal formula examples, never model-generated observations."""
    examples = {
        'mechanist': ({'operator': 'mechanist', 'skill': 3, 'charge_count': 0, 'relic_ids': []},
            {'operator': 'mechanist', 'skill': 3, 'charge_count': 0, 'relic_ids': ['rogue_6_relic_legacy_16']},
            '藏品与分队符文写回', {'attack': 573, 'defense': 765}, {'attack': 716, 'defense': 765},
            '固定培养表机械师精二90/满信赖/潜能1/无模组；攻击符文25%写回取整：573→716。'),
        'kaltsit': ({'operator': 'kaltsit', 'skill': 2, 'relic_ids': []},
            {'operator': 'kaltsit', 'skill': 2, 'relic_ids': ['rogue_6_relic_legacy_90']},
            '已覆盖常态天赋与效果', {'hp': 2650, 'attack': 510}, {'hp': 3975, 'attack': 510},
            '固定培养表凯尔希·思衡托精二90/满信赖/潜能1；生命符文50%写回后再乘常态生命天赋25%：2650→3975。'),
        'silverash': ({'operator': 'silverash', 'skill': 2, 'deployment_elapsed_seconds': 14.9},
            {'operator': 'silverash', 'skill': 2, 'deployment_elapsed_seconds': 15},
            '已覆盖常态天赋与效果', {'defense': 497}, {'defense': 557},
            '固定培养表凛御银灰精二90/满信赖/潜能1；声明在场14.9→15秒的常态防御天赋参考：497→557。'),
    }
    if operator not in examples:
        raise ValueError('公开成对模板仅支持首批三名干员。')
    a, b, panel, av, bv, source = examples[operator]
    def record(scenario, values, side):
        return {'scenario': deepcopy(scenario), 'observation': {
            'context_token': panel_layers(scenario)['context_token'], 'panel': panel,
            'evidence_kind': 'formula_reference', 'source': source + ' / ' + side,
            'values': deepcopy(values)}}
    return {'before': record(a, av, '前组公式参考'), 'after': record(b, bv, '后组公式参考'), 'tolerance': 0}
