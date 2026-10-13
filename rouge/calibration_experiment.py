"""Multi-record compatibility of an explicitly declared common residual.

A feasible common residual is a hypothesis range, never a correction, hidden
mechanism, causal conclusion, fitted coefficient, or native certification.
"""
from copy import deepcopy
from .bounded_calibration import _reading, _interval, _bounds, _residual, compare_bounded_timing


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + '需要非空文本。')
    return value


def _intersection(entries):
    """Closed/open interval Helly witness: at most two conflicting records."""
    if not entries:
        return None, None
    lower = max(_bounds(value)[0] for _, value in entries)
    upper = min(_bounds(value)[1] for _, value in entries)
    lower_records = [(key, value) for key, value in entries if _bounds(value)[0] == lower]
    upper_records = [(key, value) for key, value in entries if _bounds(value)[1] == upper]
    lower_closed = all(value['lower_inclusive'] for _, value in lower_records)
    upper_closed = all(value['upper_inclusive'] for _, value in upper_records)
    if lower > upper or (lower == upper and not (lower_closed and upper_closed)):
        lower_witness = next(((key, value) for key, value in lower_records if not value['lower_inclusive']), lower_records[0])
        upper_witness = next(((key, value) for key, value in upper_records if not value['upper_inclusive']), upper_records[0])
        return None, {'record_ids': [lower_witness[0], upper_witness[0]],
            'lower_witness_residual': deepcopy(lower_witness[1]), 'upper_witness_residual': deepcopy(upper_witness[1]),
            'reason': 'declared_residual_ranges_have_no_common_value'}
    return _interval(lower, upper, lower_closed, upper_closed), None


def _subset(left, right):
    alo, ahi = _bounds(left)
    blo, bhi = _bounds(right)
    return (alo > blo or (alo == blo and (not left['lower_inclusive'] or right['lower_inclusive']))) and (
        ahi < bhi or (ahi == bhi and (not left['upper_inclusive'] or right['upper_inclusive'])))


def _control_differences(base, current, varying):
    return [{'field': key, 'control_present': key in base, 'record_present': key in current,
        'control': deepcopy(base.get(key)), 'record': deepcopy(current.get(key)), 'allowed_to_vary': key in varying}
        for key in sorted(set(base) | set(current))
        if key not in base or key not in current or base[key] != current[key]]


def _panel_value(data, channel):
    from .calibration import compare_panel
    if not isinstance(data, dict) or set(data) != {'scenario', 'observation'}:
        raise ValueError('面板样本需为scenario与独立observation。')
    observation = deepcopy(data['observation'])
    if not isinstance(observation, dict) or not isinstance(observation.get('values'), dict) or not observation['values']:
        raise ValueError('面板样本需有非空界限记录。')
    intervals = {key: _interval(*_reading(value, '独立面板界限/' + str(key))) for key, value in observation['values'].items()}
    observation['values'] = {key: interval['lower'] for key, interval in intervals.items()}
    comparison = compare_panel(data['scenario'], observation)
    if comparison['panel'] != channel['panel']:
        raise ValueError('面板样本层与实验通道不相符。')
    selected = next((r for r in comparison['rows'] if r['field'] == channel['field']), None)
    if selected is None:
        return None, None, 'selected_field_not_recorded', comparison
    reading, expected = intervals[channel['field']], selected['predicted']
    reason = 'existing_model_field_unknown' if expected is None else None
    return reading, expected, reason, comparison


def _timing_value(data, channel):
    if not isinstance(data, dict) or set(data) != {'scenario', 'observation'}:
        raise ValueError('时刻样本需为scenario与独立observation。')
    result = compare_bounded_timing(**data)
    collection = (result['release_interval_rows'] if channel['metric'] == 'release_interval' else
                  result['repeat_cycle_rows'] if channel['metric'] == 'start_to_start' else result['comparisons'])
    selected = next((r for r in collection if r['metric'] == channel['metric'] and r['cycle_id'] == channel['cycle_id'] and
                     (channel['metric'] != 'release_interval' or r['recorded_interval_index'] == channel['interval_index'])), None)
    if selected is None:
        return None, None, 'selected_cycle_or_interval_not_recorded', result
    reading, expected = selected['observed_interval_seconds'], selected['conditional_reference_seconds']
    reason = ('selected_measurement_unknown' if reading is None else
              'existing_model_clock_or_matching_definition_unknown' if expected is None else None)
    return reading, expected, reason, result


def calibration_experiment(experiment):
    """Validate controlled records, intersect training residuals, check held-out data."""
    from .calibration import panel_layers, OPERATORS, LABELS
    from .timing_calibration import LABELS as TIMING_LABELS
    allowed = {'id', 'hypothesis', 'operator', 'channel', 'control_scenario', 'varying_fields',
               'evidence_kind', 'evidence_version', 'records'}
    if not isinstance(experiment, dict) or set(experiment) != allowed:
        raise ValueError('实验需明确id/hypothesis/operator/channel/control_scenario/varying_fields/evidence_kind/evidence_version/records。')
    identity = _text(experiment['id'], '实验标识')
    if experiment['hypothesis'] != 'common_additive_residual':
        raise ValueError('需明确声明common_additive_residual假设；不自动拟合未知机制。')
    operator = experiment['operator']
    if operator not in OPERATORS:
        raise ValueError('实验仅支持首批三名干员。')
    version = _text(experiment['evidence_version'], '实验来源版本声明')
    kind = experiment['evidence_kind']
    if kind not in ('game_panel', 'game_timing', 'public_case', 'formula_reference'):
        raise ValueError('实验来源类别不明确。')
    channel = experiment['channel']
    if not isinstance(channel, dict):
        raise ValueError('实验通道需为明确对象。')
    if channel.get('kind') == 'panel':
        if set(channel) != {'kind', 'panel', 'field'} or channel['field'] not in LABELS or kind == 'game_timing':
            raise ValueError('面板通道需同层与同字段，不接受游戏时刻来源。')
        label = LABELS[channel['field']]
    elif channel.get('kind') == 'timing':
        required = {'kind', 'metric', 'cycle_id'} | ({'interval_index'} if channel.get('metric') == 'release_interval' else set())
        if set(channel) != required or channel['metric'] not in TIMING_LABELS or channel['metric'] == 'attack_speed_attribute' or kind == 'game_panel':
            raise ValueError('时刻通道需明确同口径metric/cycle_id，不接受游戏面板来源。')
        _text(channel['cycle_id'], '通道周期标识')
        if channel['metric'] == 'release_interval' and (isinstance(channel['interval_index'], bool) or not isinstance(channel['interval_index'], int) or not 1 <= channel['interval_index'] <= 199):
            raise ValueError('释放间隔序号需为1–199整数。')
        label = TIMING_LABELS[channel['metric']]
    else:
        raise ValueError('实验通道需为panel或timing。')
    control = panel_layers(experiment['control_scenario'])
    base = control['context']['scenario']
    if base['operator'] != operator:
        raise ValueError('控制条件的干员与实验身份不一致。')
    if channel['kind'] == 'panel' and channel['panel'] not in control['panels']:
        raise ValueError('实验面板层未支持。')
    varying = experiment['varying_fields']
    if (not isinstance(varying, list) or len(varying) > 20 or any(not isinstance(key, str) or not key or key.startswith('_') or key == 'operator' for key in varying)
            or len(set(varying)) != len(varying)):
        raise ValueError('允许变化键需为不重复的最多20个公开scenario键；干员不能变化。')
    records = experiment['records']
    if not isinstance(records, list) or not 2 <= len(records) <= 40:
        raise ValueError('实验需为2–40个独立记录。')
    ids, roles = set(), []
    for raw in records:
        if not isinstance(raw, dict) or set(raw) != {'id', 'role', 'evidence_version', 'data'}:
            raise ValueError('每记录需明确id/role/evidence_version/data。')
        key = _text(raw['id'], '记录ID')
        if key in ids or raw['role'] not in ('training', 'held_out'):
            raise ValueError('记录ID必须唯一，role必须为training或held_out。')
        ids.add(key)
        roles.append(raw['role'])
        _text(raw['evidence_version'], '记录来源版本声明')
    if roles.count('training') < 2:
        raise ValueError('共同残差假设至少需两个明确训练记录。')
    rows = []
    for raw in records:
        result = {'id': raw['id'], 'role': raw['role'], 'evidence_version': raw['evidence_version'],
            'state': 'blocked', 'blocking_reasons': [], 'source': None, 'context_token': None,
            'changed_controls': [], 'observed_interval': None, 'model_reference': None,
            'residual_interval': None, 'same_context_repeat_ids': [], 'native_verified': False,
            'actual_cause_of_difference': None}
        try:
            data = raw['data']
            if not isinstance(data, dict) or set(data) != {'scenario', 'observation'} or not isinstance(data['observation'], dict):
                raise ValueError('独立记录结构不正确。')
            observation = data['observation']
            result.update(source=observation.get('source'), context_token=observation.get('context_token'))
            model = panel_layers(data['scenario'])
            current = model['context']['scenario']
            result['declared_scenario'] = deepcopy(current)
            result['model_source'] = deepcopy(model['source'])
            differences = _control_differences(base, current, varying)
            result['changed_controls'] = differences
            if current['operator'] != operator:
                result['blocking_reasons'].append('operator_identity_mismatch')
            if any(not difference['allowed_to_vary'] for difference in differences):
                result['blocking_reasons'].append('undeclared_control_change')
            if observation.get('evidence_kind') != kind:
                result['blocking_reasons'].append('evidence_kind_mismatch')
            if raw['evidence_version'] != version:
                result['blocking_reasons'].append('caller_evidence_version_mismatch')
            reading, expected, reason, detail = (_panel_value(data, channel) if channel['kind'] == 'panel' else _timing_value(data, channel))
            result.update(observed_interval=reading, model_reference=expected,
                residual_interval=_residual(reading, expected), comparison_detail=detail,
                declared_observation=deepcopy(observation))
            if reason:
                result['blocking_reasons'].append(reason)
            if not result['blocking_reasons']:
                result['state'] = 'evaluable'
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            result['blocking_reasons'].append('record_validation_error')
            result['validation_error'] = str(error)
        rows.append(result)
    for record in rows:
        if record['context_token']:
            record['same_context_repeat_ids'] = [other['id'] for other in rows if other['id'] != record['id'] and other['context_token'] == record['context_token']]
    training = [r for r in rows if r['role'] == 'training']
    held_out = [r for r in rows if r['role'] == 'held_out']
    blocked_training = [r['id'] for r in training if r['state'] != 'evaluable']
    train_range, train_witness = (None, None) if blocked_training else _intersection([(r['id'], r['residual_interval']) for r in training])
    training_state = 'blocked' if blocked_training else 'contradicted' if train_range is None else 'compatible'
    checks = []
    for record in held_out:
        check = {'record_id': record['id'], 'state': None, 'allowed_training_residual_range': deepcopy(train_range),
            'held_out_residual_range': deepcopy(record['residual_interval']), 'remaining_hypothesis_range': None,
            'contradiction_witness': None, 'native_verified': False}
        if record['state'] != 'evaluable':
            check['state'] = 'record_blocked'
        elif training_state != 'compatible':
            check['state'] = 'training_unavailable'
        else:
            intersection, witness = _intersection([('training_hypothesis_range', train_range), (record['id'], record['residual_interval'])])
            check['remaining_hypothesis_range'] = intersection
            if intersection is None:
                check['state'] = 'no_overlap'
                _, check['contradiction_witness'] = _intersection([(r['id'], r['residual_interval']) for r in training] + [(record['id'], record['residual_interval'])])
            else:
                check['state'] = 'all_training_candidates_allowed' if _subset(train_range, record['residual_interval']) else 'possible_overlap_only'
        checks.append(check)
    blocked_all = [r['id'] for r in rows if r['state'] != 'evaluable']
    overall_range, overall_witness = (None, None) if blocked_all else _intersection([(r['id'], r['residual_interval']) for r in rows])
    overall_state = 'blocked' if blocked_all else 'contradicted' if overall_range is None else 'compatible_on_declared_ranges'
    return {'scope': 'controlled_multi_record_common_residual_hypothesis', 'experiment_id': identity,
        'operator': control['operator'], 'channel': deepcopy(channel), 'channel_label': label,
        'hypothesis': experiment['hypothesis'], 'evidence_kind': kind, 'evidence_version': version,
        'version_is_caller_declaration': True, 'control_scenario': deepcopy(base), 'varying_fields': deepcopy(varying),
        'records': rows, 'training_state': training_state, 'training_record_ids': [r['id'] for r in training],
        'blocked_training_record_ids': blocked_training, 'training_hypothesis_range': train_range,
        'training_contradiction_witness': train_witness, 'held_out_checks': checks,
        'held_out_record_count': len(held_out), 'held_out_evidence_missing': not held_out,
        'overall_state': overall_state, 'blocked_record_ids': blocked_all,
        'overall_hypothesis_range': overall_range, 'overall_contradiction_witness': overall_witness,
        'source': deepcopy(control['source']), 'native_verified': False, 'engine_correction': None,
        'actual_cause_of_difference': None,
        'notes': ['共同b只是调用方声明的加性残差假设，不推断藏品、技能、隐藏机制或偏差原因，不修正引擎。',
            '训练记录共同交集与留出复核分开；只称声明范围相容，可能重叠不是实机认证。',
            '任何训练记录被阻断都阻断整组假设，不丢弃不相符或未知记录后宣称通过。',
            '每条记录独立保留条件、来源、版本声明和界限；同条件重复列出，但不假定统计独立。',
            '来源版本与控制变量由调用方明确声明；这些标识不证明客户端版本或当前热更新。',
            '单通道共同b与跨记录差值相容不能证明完整面板、原生时钟或完整技能总量。']}


def public_experiment_payload(operator='mechanist', channel_kind='panel', variant='compatible'):
    """Literal public formula records with explicitly synthetic residuals."""
    from .calibration import panel_layers
    from .timing_calibration import timing_reference
    if operator not in ('kaltsit', 'silverash', 'mechanist') or channel_kind not in ('panel', 'timing') or variant not in ('compatible', 'held_out_conflict', 'control_drift'):
        raise ValueError('没有这个公开实验模板。')
    version = '固定原件公式声明演示v1'
    records = []
    if channel_kind == 'panel':
        originals = {'kaltsit': (476, 493, 510), 'silverash': (616, 634, 653), 'mechanist': (543, 558, 573)}[operator]
        control = {'operator': operator, 'skill': 1, 'level': 60, 'relic_ids': []}
        channel = {'kind': 'panel', 'panel': '培养与模组', 'field': 'attack'}
        varying = ['level']
        for index, (level, attack) in enumerate(zip((60, 75, 90), originals)):
            scenario = {**control, 'level': level}
            observed = attack + (7 if index == 2 and variant == 'held_out_conflict' else 5)
            observation = {'context_token': panel_layers(scenario)['context_token'], 'panel': channel['panel'],
                'evidence_kind': 'formula_reference', 'source': f'固定原件精二{level}/满信赖/潜能1培养攻击字面量；另明确声明+{observed-attack}的假设测试算式，非游戏面板。',
                'values': {'attack': [observed, observed]}}
            records.append({'id': 'level' + str(level), 'role': 'held_out' if index == 2 else 'training',
                'evidence_version': version, 'data': {'scenario': scenario, 'observation': observation}})
    else:
        initials = {'kaltsit': (7, 7, 15), 'silverash': (6, 4, 5), 'mechanist': (8.433333333333334, 15, 10)}[operator]
        control = {'operator': operator, 'skill': 1, 'relic_ids': []}
        channel = {'kind': 'timing', 'metric': 'initial_ready', 'cycle_id': 'A'}
        varying = ['skill']
        for index, initial in enumerate(initials):
            scenario = {**control, 'skill': index + 1}
            reference = timing_reference(scenario)
            offset = 4 if index == 2 and variant == 'held_out_conflict' else 2
            observed = initial + offset
            observation = {'context_token': reference['context_token'], 'operator': operator,
                'skill_id': reference['skill_identity']['skill_id'], 'evidence_kind': 'formula_reference',
                'source': f'固定表S{index+1}初动字面量；另明确声明+{offset}秒假设测试算式，非游戏事件。',
                'clock': {'id': 'literal-S' + str(index + 1), 'unit': 'seconds', 'origin_event': 'deployment', 'origin_stamp': [0, 0]},
                'first_cycle_is_initial': True, 'release_kind': 'unknown', 'ordering_protocol': 'declared_normal_chain',
                'ordering_constraints': [], 'cycles': [{'id': 'A', 'ready': {'clock_id': 'literal-S' + str(index + 1), 'bounds': [observed, observed]},
                    'recharge_basis': 'unknown', 'release_recording': 'unknown'}]}
            records.append({'id': 'S' + str(index + 1), 'role': 'held_out' if index == 2 else 'training',
                'evidence_version': version, 'data': {'scenario': scenario, 'observation': observation}})
    if variant == 'control_drift':
        records[-1]['data']['scenario']['potential'] = 4
        records[-1]['data']['observation']['context_token'] = panel_layers(records[-1]['data']['scenario'])['context_token']
    return {'experiment': {'id': operator + '_' + channel_kind + '_' + variant,
        'hypothesis': 'common_additive_residual', 'operator': operator, 'channel': channel,
        'control_scenario': control, 'varying_fields': varying, 'evidence_kind': 'formula_reference',
        'evidence_version': version, 'records': records}}
