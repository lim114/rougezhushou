"""Finite level hypotheses against an independently declared panel observation.

The observation is bound to its original conditions once. Candidate conditions
are hypotheses, never new evidence or replacements for account/run cultivation.
"""
from copy import deepcopy
import math

from .calibration import LABELS, compare_panel, panel_layers
from .catalog import catalog


STATUS_NAMES = {
    'compatible': '所填字段与模型相容',
    'excluded': '已知字段存在冲突',
    'undetermined': '未冲突，但模型字段未知',
    'unavailable': '该等级条件不可测算',
}
CONCLUSION_NAMES = {
    'unique_model_candidate': '声明模型中仅一个等级相容',
    'multiple_model_candidates': '声明模型中多个等级相容',
    'compatible_with_unresolved_candidates': '存在相容等级，也有未能排除的等级',
    'no_compatible_level_in_declared_model': '当前固定条件下，没有等级与所填字段相容',
    'incomplete_model_search': '模型缺项或不可测算，不能排除所有等级',
}


def level_ranges(levels):
    """Compact consecutive integer levels without dropping gaps."""
    result = []
    for level in sorted(set(levels)):
        if result and result[-1]['last'] + 1 == level:
            result[-1]['last'] = level
        else:
            result.append({'first': level, 'last': level})
    return result


def diagnose_panel_levels(scenario, observation, tolerance=0):
    original = compare_panel(deepcopy(scenario), deepcopy(observation), tolerance)
    model = panel_layers(deepcopy(scenario))
    normalized = model['context']['scenario']
    if normalized.get('base_attack') is not None:
        raise ValueError('等级排查不能使用独立攻击白值覆盖；请使用由培养条件计算的属性。')
    phase = catalog()['operators'][normalized['operator']]['phases'][normalized['elite']]
    maximum = phase['max_level']
    panel = observation['panel']
    values = deepcopy(observation['values'])
    candidates = []
    constraints = {field: {'field': field, 'label': LABELS[field], 'observed': actual,
        'compatible_levels': [], 'excluded_levels': [], 'unresolved_levels': []}
        for field, actual in values.items()}
    for level in range(1, maximum + 1):
        candidate = {**deepcopy(normalized), 'level': level}
        row = {'level': level, 'status': None, 'fields': [], 'error': None,
               'candidate_context_token': None, 'model_complete': None}
        try:
            current = panel_layers(candidate)
        except (ValueError, OverflowError) as error:
            row.update(status='unavailable', error=str(error))
            for field in values:
                constraints[field]['unresolved_levels'].append(level)
            candidates.append(row)
            continue
        row['candidate_context_token'] = current['context_token']
        row['model_complete'] = current['model_complete']
        mismatch = False
        unknown = False
        for field, actual in values.items():
            predicted = current['panels'][panel].get(field)
            if predicted is not None and (isinstance(predicted, bool)
                    or not isinstance(predicted, (int, float)) or not math.isfinite(predicted)):
                raise ValueError('模型返回了非法属性数值：' + field)
            delta = None if predicted is None else actual - predicted
            matches = None if delta is None else abs(delta) <= tolerance
            unknown |= matches is None
            mismatch |= matches is False
            key = ('unresolved_levels' if matches is None else
                   'compatible_levels' if matches else 'excluded_levels')
            constraints[field][key].append(level)
            row['fields'].append({'field': field, 'label': LABELS[field],
                'observed': actual, 'predicted': predicted, 'difference': delta,
                'matches_declared_tolerance': matches})
        row['status'] = 'excluded' if mismatch else 'undetermined' if unknown else 'compatible'
        candidates.append(row)
    statuses = {name: [r['level'] for r in candidates if r['status'] == name]
                for name in STATUS_NAMES}
    unresolved = sorted(statuses['undetermined'] + statuses['unavailable'])
    compatible = statuses['compatible']
    if compatible:
        conclusion = ('compatible_with_unresolved_candidates' if unresolved else
                      'unique_model_candidate' if len(compatible) == 1 else 'multiple_model_candidates')
    else:
        conclusion = 'incomplete_model_search' if unresolved else 'no_compatible_level_in_declared_model'
    for constraint in constraints.values():
        for key in ('compatible_levels', 'excluded_levels', 'unresolved_levels'):
            constraint[key.replace('_levels', '_ranges')] = level_ranges(constraint[key])
    return {'operator': model['operator'], 'elite': normalized['elite'],
        'original_level': normalized['level'], 'searched_levels': {'first': 1, 'last': maximum},
        'fixed_conditions': {k: deepcopy(v) for k, v in normalized.items() if k != 'level'},
        'observation': deepcopy(observation), 'original_comparison': original,
        'source': deepcopy(model['source']), 'tolerance': tolerance,
        'rows': candidates, 'field_constraints': list(constraints.values()),
        'compatible_levels': compatible, 'compatible_ranges': level_ranges(compatible),
        'unresolved_levels': unresolved, 'unresolved_ranges': level_ranges(unresolved),
        'excluded_levels': statuses['excluded'], 'conclusion': conclusion,
        'unique_model_level': compatible[0] if len(compatible) == 1 and not unresolved else None,
        'actual_level': None, 'actual_cause_of_residual': None, 'native_verified': False,
        'notes': ['仅改变等级，固定当前精英、信赖、潜能、模组、技能、藏品和其他声明条件；穷举该精英阶段的全部合法等级。',
            '观察条件标识仅验证原记录；候选标识用于区别假设，不替换观察标识，不表示观察属于候选等级。',
            '相容仅针对所填字段及当前条件模型，不证明实际等级或偏差原因。缺失观察字段不补零，模型未知或不可测算的等级不假称已排除。',
            '无相容等级只排除当前固定条件的等级解释；遗漏效果、错误面板层、信赖/潜能/模组读取或未证机制仍可能导致差异。',
            '独立局外排查，不修改本局或账户培养；冻结资料与当前游戏热更新的等价性仍未认证。']}


def format_ranges(ranges):
    return '、'.join(str(r['first']) if r['first'] == r['last'] else
                    str(r['first']) + '–' + str(r['last']) for r in ranges) or '无'


def format_level_diagnostics(result):
    lines = [result['operator'] + ' · 精英' + str(result['elite']) + '等级排查',
        CONCLUSION_NAMES[result['conclusion']],
        '相容等级：' + format_ranges(result['compatible_ranges']),
        '未能排除等级：' + format_ranges(result['unresolved_ranges']),
        '实际等级与偏差原因：未知；来源：' + result['observation']['source']]
    for field in result['field_constraints']:
        lines.append(field['label'] + '观察' + str(field['observed']) +
            '；单字段相容等级：' + format_ranges(field['compatible_ranges']) +
            '；单字段未知等级：' + format_ranges(field['unresolved_ranges']))
    return '\n'.join([*lines, *result['notes']])
