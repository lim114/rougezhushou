"""Source-qualified skill clocks versus independent recorded event sequences.

This module measures declarations. It neither generates game observations nor
binds a nominal timer or a duration parameter to the current native client.
"""
from copy import deepcopy
import math


KINDS = ('game_timing', 'public_case', 'formula_reference')
RELEASE_KINDS = ('body_attack_release', 'body_impact', 'summon_impact', 'unknown')
EVENTS = ('ready', 'start', 'first_release', 'last_release', 'end', 'unblocked', 'next_ready')
LABELS = {
    'initial_ready': '部署到首次技能就绪', 'activation_wait': '就绪到实际开启等待',
    'first_release': '开启到首次记录释放/命中', 'release_span': '首次到末次记录释放/命中',
    'active_duration': '开启到记录结束', 'unlock_delay': '记录结束到解除阻回',
    'unblocked_recharge': '解除阻回到下次就绪', 'recharge': '记录结束到下次就绪',
    'cycle_to_ready': '开启到下次就绪', 'start_to_start': '相邻两次开启间隔',
    'attack_speed_attribute': '独立记录的技能攻速属性', 'release_interval': '连续两次记录释放/命中间隔',
}


def _number(value, name):
    try:
        valid = not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value >= 0
    except (OverflowError, ValueError):
        valid = False
    if not valid:
        raise ValueError(name + '需要有限非负数。')
    return value


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + '需要非空文本。')
    return value


def timing_reference(scenario):
    """Reuse the final existing forecast, preserving every unknown and warning."""
    from .calibration import panel_layers
    from .catalog import catalog
    from .damage import calculate_damage
    panel = panel_layers(scenario)
    normalized = panel['context']['scenario']
    result = calculate_damage(deepcopy(normalized))
    skill = result['estimate']['skill']
    profile = catalog()['operators'][normalized['operator']]
    entry = profile['skills'][normalized['skill'] - 1]
    level = entry['levels'][normalized['skill_rank'] - 1]
    channels = {
        'initial_ready': skill.get('initial_seconds'), 'recharge': skill.get('recharge_seconds'),
        'cycle_to_ready': skill.get('cycle_seconds'),
        'attack_speed_attribute': skill.get('skill_attack_speed_reference'),
    }
    body_streams = [s for s in result['timing'].get('streams', []) if s.get('unit') == normalized['operator']]
    constant_interval = bool(body_streams) and all(
        not stream.get('temporary_attack_speed') and
        len(set(stream.get('interval_frames_by_attack', []))) <= 1 for stream in body_streams)
    intervals = {stream.get('interval_seconds') for stream in body_streams}
    body_interval = next(iter(intervals)) if constant_interval and len(intervals) == 1 else None
    return {'operator': panel['operator'], 'context': deepcopy(panel['context']),
        'context_token': panel['context_token'],
        'skill_identity': {'operator': normalized['operator'], 'operator_id': profile['id'],
            'skill': normalized['skill'], 'skill_id': entry['id'], 'skill_rank': normalized['skill_rank']},
        'skill_name': skill['name'], 'conditional_references': channels,
        'model_duration_reference_seconds': skill.get('duration_seconds'),
        'source_duration_parameter_seconds': level['duration'] if level['duration'] >= 0 else None,
        'nominal_interval_reference_seconds': result.get('interval_seconds'),
        'constant_body_interval_reference_available': constant_interval,
        'body_interval_conditional_reference_seconds': body_interval,
        'max_charges': level['max_charges'], 'sp_type': level['sp_type'],
        'model_timing_mode': result['timing']['mode'], 'model_fps': result['timing'].get('fps'),
        'actual_first_release_seconds': None, 'actual_end_seconds': None,
        'actual_unblocked_seconds': None, 'actual_cycle_seconds': None,
        'source': deepcopy(panel['source']), 'warnings': deepcopy(result.get('warnings', [])),
        'native_verified': False,
        'notes': ['初动参考以部署为起点、首个技能就绪为终点；手动开启等待独立记录。',
            '回转参考以模型技能结束为起点，含同scenario中的额外阻回/硬直策略；解除阻回后的纯充能不是同一口径。',
            '周期参考为模型开启到下次就绪；相邻开启间隔包含额外启动等待，不自动与周期相等。',
            '持续参数、模型持续估计和名义间隔分别列出，均不证明实际结束、释放/碰撞绑定或当前热更新。']}


def _clock(raw):
    if not isinstance(raw, dict) or set(raw) - {'id', 'unit', 'fps', 'origin_event', 'origin_stamp'}:
        raise ValueError('clock需声明唯一id、unit、部署原点及可选视频fps。')
    identity = _text(raw.get('id'), '时钟标识')
    if raw.get('origin_event') != 'deployment':
        raise ValueError('时钟原点必须明确为deployment；片段起点不能冒充部署。')
    if raw.get('unit') not in ('seconds', 'frames'):
        raise ValueError('记录单位需要seconds或frames。')
    origin = _number(raw.get('origin_stamp'), '部署时钟坐标')
    if origin > 1e12:
        raise ValueError('部署时钟坐标超出支持范围。')
    if raw['unit'] == 'frames':
        if not isinstance(origin, int):
            raise ValueError('视频帧坐标需要整数；不强制转换为30Hz。')
        fps = _number(raw.get('fps'), '视频FPS')
        if fps == 0 or fps > 1000:
            raise ValueError('视频FPS需大于0且不超过1000。')
    else:
        if raw.get('fps') is not None:
            raise ValueError('秒时钟不接受FPS，避免混合单位。')
        fps = None
    origin_seconds = origin / fps if fps else origin
    if not math.isfinite(origin_seconds):
        raise ValueError('视频FPS换算后的部署坐标不是有限秒数。')
    return {'id': identity, 'unit': raw['unit'], 'fps': fps, 'origin_event': 'deployment',
            'origin_stamp': origin, 'origin_seconds': origin_seconds}


def _stamp(raw, clock, name):
    if raw is None:
        return None
    if not isinstance(raw, dict) or set(raw) != {'clock_id', 'value'}:
        raise ValueError(name + '需为含clock_id和value的独立时刻，未知填null。')
    if raw['clock_id'] != clock['id']:
        raise ValueError(name + '使用不同的时钟；不能直接相减。')
    value = _number(raw['value'], name)
    if value > 1e12:
        raise ValueError(name + '时钟坐标超出支持范围。')
    if clock['unit'] == 'frames' and not isinstance(value, int):
        raise ValueError(name + '视频帧坐标需要整数。')
    if value < clock['origin_stamp']:
        raise ValueError(name + '早于声明部署原点。')
    seconds = value / clock['fps'] if clock['fps'] else value
    if not math.isfinite(seconds):
        raise ValueError(name + '换算后不是有限秒数。')
    return seconds


def _cycle(raw, clock):
    allowed = {'id', *EVENTS, 'release_stamps', 'release_recording', 'recharge_basis'}
    if not isinstance(raw, dict) or set(raw) - allowed:
        raise ValueError('每次周期需为支持的事件记录对象。')
    identity = _text(raw.get('id'), '周期标识')
    recording = raw.get('release_recording', 'unknown')
    if recording not in ('all_consecutive', 'selected', 'unknown'):
        raise ValueError('release_recording需区分连续完整记录、抽样和未知。')
    basis = raw.get('recharge_basis', 'unknown')
    if basis not in ('model_depleted_requirement', 'precharged_or_partial', 'unknown'):
        raise ValueError('recharge_basis需区分模型耗尽后需求、预存/部分充能及未知。')
    stamps = {key: _stamp(raw.get(key), clock, identity + '/' + key) for key in EVENTS}
    releases = raw.get('release_stamps', [])
    if not isinstance(releases, list) or len(releases) > 200:
        raise ValueError('release_stamps需为最多200个非空时刻列表。')
    releases = [_stamp(value, clock, identity + '/release_stamps') for value in releases]
    if any(value is None for value in releases) or any(b <= a for a, b in zip(releases, releases[1:])):
        raise ValueError('连续记录时刻需严格递增，列表内未知项请改为独立事件null。')
    if releases:
        for name, actual in (('first_release', releases[0]), ('last_release', releases[-1])):
            if stamps[name] is not None and stamps[name] != actual:
                raise ValueError(name + '与记录列表边界不一致。')
            stamps[name] = actual
    known = [stamps[key] for key in EVENTS if stamps[key] is not None]
    if any(b < a for a, b in zip(known, known[1:])):
        raise ValueError('周期记录事件顺序逆转；请核对就绪、开启、释放、结束、解除阻回与下次就绪。')
    if not known:
        raise ValueError('每周期至少需要一个已注明来源的非空事件时刻。')
    return {'id': identity, 'events_seconds': stamps, 'release_seconds': releases,
            'release_recording': recording, 'recharge_basis': basis}


def _measure(identity, metric, start, end, expected, tolerance, reason=None):
    observed = None if start is None or end is None else end - start
    delta = None if observed is None or expected is None else observed - expected
    return {'cycle_id': identity, 'metric': metric, 'label': LABELS[metric],
        'observed_seconds': observed, 'conditional_reference_seconds': expected,
        'observed_minus_conditional_reference': delta,
        'matches_declared_tolerance': None if delta is None else abs(delta) <= tolerance,
        'reference_unavailable_reason': reason if expected is None else None,
        'actual_native_reference_seconds': None, 'actual_cause_of_difference': None}


def _summary(rows):
    values = [row['observed_seconds'] for row in rows if row['observed_seconds'] is not None]
    return {'recorded_count': len(values), 'minimum_seconds': min(values) if values else None,
            'maximum_seconds': max(values) if values else None,
            'range_seconds': max(values) - min(values) if values else None,
            'mean_seconds': math.fsum(value / len(values) for value in values) if values else None,
            'actual_cause_of_variation': None}


def compare_timing_observation(scenario, observation, tolerance_seconds=0):
    """Measure a source-labeled clock ledger and compare definition-matched fields."""
    _number(tolerance_seconds, '秒数容差')
    reference = timing_reference(scenario)
    if not isinstance(observation, dict):
        raise ValueError('observation需为JSON对象。')
    allowed = {'context_token', 'operator', 'skill_id', 'evidence_kind', 'source', 'clock',
               'first_cycle_is_initial', 'release_kind', 'cycles', 'attack_speed_attribute'}
    if set(observation) - allowed:
        raise ValueError('观察记录含未支持的字段。')
    if observation.get('context_token') != reference['context_token']:
        raise ValueError('事件记录与预测条件标识不一致；请核对独立记录的培养/技能/藏品条件。')
    if (observation.get('operator') != reference['skill_identity']['operator'] or
            observation.get('skill_id') != reference['skill_identity']['skill_id']):
        raise ValueError('事件记录干员或技能ID与当前条件不一致。')
    kind = observation.get('evidence_kind')
    if kind not in KINDS:
        raise ValueError('来源类别需为game_timing、public_case或formula_reference。')
    source = _text(observation.get('source'), '事件记录来源')
    if not isinstance(observation.get('first_cycle_is_initial'), bool):
        raise ValueError('需明确first_cycle_is_initial；中途录制不能冒充部署后的首次就绪。')
    release_kind = observation.get('release_kind', 'unknown')
    if release_kind not in RELEASE_KINDS:
        raise ValueError('需区分本体攻击释放、本体命中、召唤物命中或未知事件。')
    clock = _clock(observation.get('clock'))
    raw_cycles = observation.get('cycles')
    if not isinstance(raw_cycles, list) or not 1 <= len(raw_cycles) <= 20:
        raise ValueError('cycles需为1–20个独立周期记录。')
    cycles = [_cycle(raw, clock) for raw in raw_cycles]
    if len({c['id'] for c in cycles}) != len(cycles):
        raise ValueError('周期ID不能重复。')
    last_start = last_end = None
    for cycle in cycles:
        start = cycle['events_seconds']['start']
        end = cycle['events_seconds']['end']
        if start is not None:
            if last_start is not None and start <= last_start:
                raise ValueError('重复开启记录需按时钟严格递增。')
            if last_end is not None and start < last_end:
                raise ValueError('同一干员的重复开启早于上一已记录结束。')
            last_start = start
        if end is not None:
            if last_end is not None and end < last_end:
                raise ValueError('重复结束记录顺序逆转。')
            last_end = end
    comparisons, interval_rows, repeat_rows = [], [], []
    refs = reference['conditional_references']
    for index, cycle in enumerate(cycles):
        event = cycle['events_seconds']
        compatible_recharge = cycle['recharge_basis'] == 'model_depleted_requirement'
        definitions = [
            ('initial_ready', clock['origin_seconds'] if index == 0 else None, event['ready'],
             refs['initial_ready'] if index == 0 and observation['first_cycle_is_initial'] else None,
             'not_declared_first_readiness_after_deployment'),
            ('activation_wait', event['ready'], event['start'], None, 'manual_activation_wait_not_sp_readiness'),
            ('first_release', event['start'], event['first_release'], None, 'native_first_release_binding_unknown'),
            ('release_span', event['first_release'], event['last_release'], None, 'native_release_sequence_unknown'),
            ('active_duration', event['start'], event['end'], None, 'nominal_parameter_does_not_bind_actual_end'),
            ('unlock_delay', event['end'], event['unblocked'], None, 'native_unblocking_phase_unknown'),
            ('unblocked_recharge', event['unblocked'], event['next_ready'], None, 'different_origin_from_model_recharge'),
            ('recharge', event['end'], event['next_ready'], refs['recharge'] if compatible_recharge else None,
             'observed_charge_requirement_not_declared_compatible'),
            ('cycle_to_ready', event['start'], event['next_ready'], refs['cycle_to_ready'] if compatible_recharge else None,
             'observed_charge_requirement_not_declared_compatible'),
        ]
        for metric, begin, finish, expected, reason in definitions:
            if expected is None and metric in ('initial_ready', 'recharge', 'cycle_to_ready') and (
                    (metric == 'initial_ready' and index == 0 and observation['first_cycle_is_initial']) or
                    (metric != 'initial_ready' and compatible_recharge)):
                reason = 'existing_model_clock_unknown'
            comparisons.append(_measure(cycle['id'], metric, begin, finish, expected, tolerance_seconds, reason))
        compatible_interval = (release_kind == 'body_attack_release' and cycle['release_recording'] == 'all_consecutive'
                               and reference['constant_body_interval_reference_available'])
        for release_index, (begin, finish) in enumerate(zip(cycle['release_seconds'], cycle['release_seconds'][1:]), 1):
            row = _measure(cycle['id'], 'release_interval', begin, finish,
                reference['body_interval_conditional_reference_seconds'] if compatible_interval else None,
                tolerance_seconds, 'nonconsecutive_or_different_release_source')
            row['recorded_interval_index'] = release_index
            interval_rows.append(row)
        if index:
            previous = cycles[index - 1]['events_seconds']
            row = _measure(cycle['id'], 'start_to_start', previous['start'], event['start'], None,
                           tolerance_seconds, 'includes_separate_activation_wait')
            row.update(previous_cycle_id=cycles[index - 1]['id'],
                previous_start_to_next_ready_seconds=None if previous['start'] is None or previous['next_ready'] is None else previous['next_ready'] - previous['start'],
                next_ready_to_current_start_seconds=None if previous['next_ready'] is None or event['start'] is None else event['start'] - previous['next_ready'])
            repeat_rows.append(row)
    attack_speed = observation.get('attack_speed_attribute')
    if attack_speed is not None:
        _number(attack_speed, '独立观察攻速属性')
    attack_expected = refs['attack_speed_attribute']
    attack_delta = None if attack_speed is None or attack_expected is None else attack_speed - attack_expected
    compared = [row for row in comparisons + interval_rows if row['observed_minus_conditional_reference'] is not None]
    return {'scope': 'independently_recorded_skill_clock_calibration', 'operator': reference['operator'],
        'skill_name': reference['skill_name'], 'skill_identity': deepcopy(reference['skill_identity']),
        'context_token': reference['context_token'], 'evidence_kind': kind, 'source': source,
        'clock': clock, 'release_kind': release_kind, 'first_cycle_is_initial': observation['first_cycle_is_initial'],
        'tolerance_seconds': tolerance_seconds, 'cycles': cycles, 'comparisons': comparisons,
        'compared_conditional_clock_count': len(compared),
        'matching_conditional_clock_count': sum(row['matches_declared_tolerance'] is True for row in compared),
        'mismatching_conditional_clock_count': sum(row['matches_declared_tolerance'] is False for row in compared),
        'release_interval_rows': interval_rows, 'repeat_cycle_rows': repeat_rows,
        'variation': {metric: _summary([r for r in comparisons if r['metric'] == metric])
                      for metric in ('activation_wait', 'active_duration', 'unlock_delay', 'recharge', 'cycle_to_ready')},
        'repeat_variation': _summary(repeat_rows), 'release_interval_variation': _summary(interval_rows),
        'attack_speed_comparison': {'observed_attribute': attack_speed, 'conditional_reference_attribute': attack_expected,
            'observed_minus_reference': attack_delta, 'native_verified': False,
            'note': '攻速是独立填写的面板属性；不从视频释放/碰撞间隔反推。'},
        'reference': reference, 'warnings': deepcopy(reference['warnings']),
        'native_verified': False, 'actual_cause_of_difference': None,
        'notes': [
            '时刻均来自调用方独立来源；视频帧按声明FPS换秒，不强制套模型30Hz。',
            '只比较定义匹配的条件参考；实测首出手、结束及解除阻回没有已绑定原生预测，保持未知。',
            '模型周期到下次就绪，相邻开启还包含额外等待；多充能或部分充能需求不相符时不套空池回转。',
            '连续完整本体攻击释放记录可对照名义间隔；抽样、命中和召唤物记录只计算观察间隔。',
            '重复周期变化及偏差不证明具体原因；公开算例、公式参考和声明游戏记录不会升级为原生认证。',
            '不操作游戏、不自动采样、不修改当前本局或从模型生成观察时刻。']}


def public_timing_payload(operator='kaltsit'):
    """Literal formula-clock ledgers; none is an observed game event sequence."""
    samples = {
        'kaltsit': ({'operator': 'kaltsit', 'skill': 1}, 7, 35, 35, 150),
        'silverash': ({'operator': 'silverash', 'skill': 3}, 5, 48, 55, 100),
        'mechanist': ({'operator': 'mechanist', 'skill': 3, 'charge_count': 0}, 10, 40, 35, 100),
    }
    if operator not in samples:
        raise ValueError('公开时钟模板仅支持首批三名干员。')
    scenario, initial, duration, recharge, attack_speed = samples[operator]
    reference = timing_reference(scenario)
    clock_id = 'literal-formula-clock'
    def stamp(value):
        return {'clock_id': clock_id, 'value': value}
    # Explicit literal formula inputs are combined only with declared manual
    # waits. No predictor output is copied to observations or release stamps.
    start_a = 100 + initial + 2
    end_a = start_a + duration
    ready_b = end_a + recharge
    start_b = ready_b + 3
    end_b = start_b + duration
    cycles = [{'id': 'A', 'ready': stamp(100 + initial), 'start': stamp(start_a),
        'first_release': None, 'last_release': None, 'release_stamps': [],
        'end': stamp(end_a), 'unblocked': None, 'next_ready': stamp(ready_b),
        'recharge_basis': 'model_depleted_requirement', 'release_recording': 'unknown'},
        {'id': 'B', 'ready': stamp(ready_b), 'start': stamp(start_b),
         'first_release': None, 'last_release': None, 'release_stamps': [],
         'end': stamp(end_b), 'unblocked': None, 'next_ready': stamp(end_b + recharge),
         'recharge_basis': 'model_depleted_requirement', 'release_recording': 'unknown'}]
    return {'scenario': deepcopy(scenario), 'observation': {
        'context_token': reference['context_token'], 'operator': operator,
        'skill_id': reference['skill_identity']['skill_id'], 'evidence_kind': 'formula_reference',
        'source': '固定表初动/名义持续/回转算式参考；另声明首次等待2秒、第二次等待3秒。首末释放与解除阻回未提供；不是游戏事件。',
        'clock': {'id': clock_id, 'unit': 'seconds', 'origin_event': 'deployment', 'origin_stamp': 100},
        'first_cycle_is_initial': True, 'release_kind': 'unknown', 'cycles': cycles,
        'attack_speed_attribute': attack_speed}, 'tolerance_seconds': 0}
