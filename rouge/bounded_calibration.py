"""Explicit reading bounds and declared ordering, without guessed precision.

Only caller-supplied closed bounds are accepted. Timing dependencies are an
input protocol, never evidence of the actual native event order. Pure ordering
constraints tighten intervals before any phase difference is calculated.
"""
from copy import deepcopy
from fractions import Fraction
import math


STATES = ('all_compatible', 'possible_overlap', 'no_overlap', 'model_unknown', 'measurement_unknown')


def _number(value, name):
    try:
        good = not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and 0 <= value <= 1e12
    except (ValueError, OverflowError):
        good = False
    if not good:
        raise ValueError(name + '需要0–1e12范围内的有限数；界限由调用方声明。')
    return Fraction(str(value))


def _reading(value, name):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(name + '需明确填写[下界,上界]；不自动猜测读数精度。')
    lo, hi = (_number(v, name) for v in value)
    if lo > hi:
        raise ValueError(name + '下界不能大于上界。')
    return lo, hi


def _out(value):
    if value.denominator == 1:
        return value.numerator
    return float(value)


def _interval(lo, hi, lo_closed=True, hi_closed=True):
    return {'lower': _out(lo), 'upper': _out(hi), 'lower_exact': str(lo), 'upper_exact': str(hi),
            'lower_inclusive': lo_closed, 'upper_inclusive': hi_closed}


def _bounds(value):
    return Fraction(value.get('lower_exact', str(value['lower']))), Fraction(value.get('upper_exact', str(value['upper'])))


def _subtract(left, right):
    if left is None or right is None:
        return None
    alo, ahi = _bounds(left)
    blo, bhi = _bounds(right)
    return _interval(alo - bhi, ahi - blo,
                     left['lower_inclusive'] and right['upper_inclusive'],
                     left['upper_inclusive'] and right['lower_inclusive'])


def _residual(value, reference):
    if value is None or reference is None:
        return None
    lo, hi = _bounds(value)
    ref = Fraction(str(reference))
    return _interval(lo - ref, hi - ref, value['lower_inclusive'], value['upper_inclusive'])


def _classify(value, reference, tolerance):
    if value is None:
        return 'measurement_unknown'
    if reference is None:
        return 'model_unknown'
    lo, hi = _bounds(value)
    ref = Fraction(str(reference))
    accepted_lo, accepted_hi = ref - tolerance, ref + tolerance
    if lo >= accepted_lo and hi <= accepted_hi:
        return 'all_compatible'
    overlap_lo, overlap_hi = max(lo, accepted_lo), min(hi, accepted_hi)
    if overlap_lo < overlap_hi:
        return 'possible_overlap'
    if overlap_lo == overlap_hi:
        lower_ok = overlap_lo > lo or value['lower_inclusive']
        upper_ok = overlap_hi < hi or value['upper_inclusive']
        if lower_ok and upper_ok:
            return 'possible_overlap'
    return 'no_overlap'


def _panel_record(raw, name):
    if not isinstance(raw, dict) or set(raw) != {'scenario', 'observation'}:
        raise ValueError(name + '需仅包含scenario与observation。')
    record = deepcopy(raw)
    observation = record['observation']
    if not isinstance(observation, dict) or not isinstance(observation.get('values'), dict) or not observation['values']:
        raise ValueError(name + '需有独立来源和非空观察字段。')
    intervals = {key: _interval(*_reading(value, name + '/' + str(key))) for key, value in observation['values'].items()}
    observation['values'] = {key: value['lower'] for key, value in intervals.items()}
    return record, intervals


def compare_bounded_panels(before, after, tolerance=0):
    """Reuse exact provenance checks; compare independently declared field bounds."""
    from .paired_calibration import compare_paired_panels
    tolerance_value = _number(tolerance, '面板容差')
    left, left_intervals = _panel_record(before, '前组')
    right, right_intervals = _panel_record(after, '后组')
    exact = compare_paired_panels(left, right, tolerance)
    rows = []
    for row in exact['rows']:
        a, b = left_intervals[row['field']], right_intervals[row['field']]
        delta = _subtract(b, a)
        reference = row['model_after_minus_before']
        rows.append({'field': row['field'], 'label': row['label'],
            'before_observed_interval': a, 'after_observed_interval': b,
            'before_model_reference': row['before_model_reference'], 'after_model_reference': row['after_model_reference'],
            'before_absolute_residual_interval': _residual(a, row['before_model_reference']),
            'after_absolute_residual_interval': _residual(b, row['after_model_reference']),
            'observed_after_minus_before_interval': delta, 'model_after_minus_before': reference,
            'delta_residual_interval': _residual(delta, reference),
            'classification': _classify(delta, reference, tolerance_value),
            'before_absolute_classification': _classify(a, row['before_model_reference'], tolerance_value),
            'after_absolute_classification': _classify(b, row['after_model_reference'], tolerance_value),
            'actual_cause_of_difference': None})
    return {'operator': exact['operator'], 'panel': exact['panel'], 'evidence_kind': exact['evidence_kind'],
        'before_source': before['observation']['source'], 'after_source': after['observation']['source'],
        'before_context_token': exact['before']['comparison']['context_token'],
        'after_context_token': exact['after']['comparison']['context_token'],
        'rows': rows, 'before_only_fields': exact['before_only_fields'], 'after_only_fields': exact['after_only_fields'],
        'before_only_readings': {key: left_intervals[key] for key in exact['before_only_fields']},
        'after_only_readings': {key: right_intervals[key] for key in exact['after_only_fields']},
        'changed_conditions': exact['changed_conditions'], 'relic_transition': exact['relic_transition'],
        'source': exact['source'], 'before_warnings': exact['before']['model']['warnings'],
        'after_warnings': exact['after']['model']['warnings'], 'tolerance': tolerance,
        'declared_before_observation': deepcopy(before['observation']),
        'declared_after_observation': deepcopy(after['observation']),
        'native_verified': False, 'actual_causal_attribution': None}


class _OrderBounds:
    """Exact decimal-rational bounds under explicit <= / < dependencies only.

    Reachability propagates every ancestor's lower bound and descendant's upper
    bound. Pairwise difference extrema then include any direct/transitive order
    constraint. Strict edges retain open endpoints; no epsilon is introduced.
    """
    def __init__(self):
        self.original = {}
        self.declared = {}
        self.edges = []
        self.aliases = {}
        self.feasible = {}
        self.reach = {}

    def add(self, name, reading):
        self.original[name] = reading
        self.declared[name] = reading
        self.aliases[name] = name

    def intersect(self, name, reading):
        lo, hi = self.original[name]
        new_lo, new_hi = max(lo, reading[0]), min(hi, reading[1])
        if new_lo > new_hi:
            raise ValueError('同一声明时刻的首末/列表界限没有共同值；与已声明记录协议冲突。')
        self.original[name] = (new_lo, new_hi)

    def order(self, before, after, strict=False):
        if before not in self.aliases or after not in self.aliases:
            raise ValueError('排序约束引用了未录入界限的时刻。')
        self.edges.append((self.aliases[before], self.aliases[after], strict))

    def solve(self):
        if len(self.original) > 256:
            raise ValueError('联合界限最多256个已录入时刻。')
        adjacency = {name: [] for name in self.original}
        for before, after, strict in self.edges:
            adjacency[before].append((after, strict))
        for origin in self.original:
            found = {}
            pending = list(adjacency[origin])
            while pending:
                target, strict = pending.pop()
                if target in found and (found[target] or not strict):
                    continue
                found[target] = strict or found.get(target, False)
                pending.extend((nxt, strict or edge_strict) for nxt, edge_strict in adjacency[target])
            if found.get(origin):
                raise ValueError('联合时刻与已声明排序协议冲突：严格先后形成闭环。不能据此判断游戏行为。')
            self.reach[origin] = found
        for name, (own_lo, own_hi) in self.original.items():
            lo, hi, lc, hc = own_lo, own_hi, True, True
            for ancestor, paths in self.reach.items():
                if name not in paths:
                    continue
                candidate = self.original[ancestor][0]
                closed = not paths[name]
                if candidate > lo:
                    lo, lc = candidate, closed
                elif candidate == lo:
                    lc = lc and closed
            for descendant, strict in self.reach[name].items():
                candidate = self.original[descendant][1]
                if candidate < hi:
                    hi, hc = candidate, not strict
                elif candidate == hi:
                    hc = hc and not strict
            if lo > hi or (lo == hi and not (lc and hc)):
                raise ValueError('联合界限与调用方已声明的排序协议冲突；不代表游戏行为不可能。')
            self.feasible[name] = (lo, hi, lc, hc)

    def difference(self, before, after):
        if before is None or after is None:
            return None
        before, after = self.aliases[before], self.aliases[after]
        if before == after:
            return _interval(Fraction(0), Fraction(0))
        alo, ahi, alc, ahc = self.feasible[before]
        blo, bhi, blc, bhc = self.feasible[after]
        lo, hi, lc, hc = blo - ahi, bhi - alo, blc and ahc, bhc and alc
        if after in self.reach[before]:
            strict = self.reach[before][after]
            if lo < 0:
                lo, lc = Fraction(0), not strict
            elif lo == 0:
                lc = lc and not strict
        if before in self.reach[after]:
            strict = self.reach[after][before]
            if hi > 0:
                hi, hc = Fraction(0), not strict
            elif hi == 0:
                hc = hc and not strict
        return _interval(lo, hi, lc, hc)


def _clock(raw):
    if not isinstance(raw, dict) or set(raw) - {'id', 'unit', 'fps', 'origin_event', 'origin_stamp'}:
        raise ValueError('clock需为明确单位、FPS及部署原点界限的对象。')
    identity = raw.get('id')
    if not isinstance(identity, str) or not identity.strip() or raw.get('origin_event') != 'deployment':
        raise ValueError('时钟需有非空id和明确deployment原点。')
    if raw.get('unit') not in ('seconds', 'frames'):
        raise ValueError('单位仅支持seconds或frames。')
    origin = _reading(raw.get('origin_stamp'), '部署原点界限')
    if raw['unit'] == 'frames':
        if any(not isinstance(value, int) or isinstance(value, bool) for value in raw['origin_stamp']):
            raise ValueError('视频帧界限需为整数。')
        fps = _number(raw.get('fps'), '声明视频FPS')
        if not 0 < fps <= 1000:
            raise ValueError('视频FPS需大于0且不超过1000；不自动套30Hz。')
    else:
        if raw.get('fps') is not None:
            raise ValueError('秒记录不能混用FPS。')
        fps = Fraction(1)
    converted = (origin[0] / fps, origin[1] / fps)
    if any(value > Fraction(10 ** 12) for value in converted):
        raise ValueError('声明FPS换算后的部署秒坐标超出支持范围。')
    return {'id': identity, 'unit': raw['unit'], 'fps': raw.get('fps'),
            'origin_event': 'deployment', 'origin_stamp': deepcopy(raw['origin_stamp'])}, converted, fps


def _stamp(raw, clock, fps, name):
    if raw is None:
        return None
    if not isinstance(raw, dict) or set(raw) != {'clock_id', 'bounds'} or raw['clock_id'] != clock['id']:
        raise ValueError(name + '需有匹配clock_id与显式bounds；不同钟不能相减。')
    bounds = _reading(raw['bounds'], name)
    if clock['unit'] == 'frames' and any(not isinstance(v, int) or isinstance(v, bool) for v in raw['bounds']):
        raise ValueError(name + '视频帧界限需为整数。')
    result = (bounds[0] / fps, bounds[1] / fps)
    if any(value > Fraction(10 ** 12) for value in result):
        raise ValueError('换算后秒坐标超出支持范围。')
    return result


def compare_bounded_timing(scenario, observation, tolerance_seconds=0):
    from .timing_calibration import KINDS, RELEASE_KINDS, EVENTS, LABELS, timing_reference
    tolerance = _number(tolerance_seconds, '明确秒数容差')
    reference = timing_reference(scenario)
    allowed = {'context_token', 'operator', 'skill_id', 'evidence_kind', 'source', 'clock',
        'first_cycle_is_initial', 'release_kind', 'cycles', 'attack_speed_attribute', 'ordering_protocol', 'ordering_constraints'}
    if not isinstance(observation, dict) or set(observation) - allowed:
        raise ValueError('有界时刻记录需为支持的独立来源对象。')
    if observation.get('context_token') != reference['context_token']:
        raise ValueError('界限记录与当前声明条件标识不一致。')
    if (observation.get('operator') != reference['skill_identity']['operator'] or
            observation.get('skill_id') != reference['skill_identity']['skill_id']):
        raise ValueError('有界记录的干员/技能身份不一致。')
    if observation.get('evidence_kind') not in KINDS:
        raise ValueError('需区分game_timing/public_case/formula_reference。')
    if not isinstance(observation.get('source'), str) or not observation['source'].strip():
        raise ValueError('界限记录必须独立注明来源。')
    if not isinstance(observation.get('first_cycle_is_initial'), bool):
        raise ValueError('需明确是否为部署后的首次就绪。')
    kind = observation.get('release_kind', 'unknown')
    if kind not in RELEASE_KINDS:
        raise ValueError('释放/命中来源类别不明确。')
    protocol = observation.get('ordering_protocol')
    if protocol not in ('declared_normal_chain', 'explicit_constraints'):
        raise ValueError('需明确选择调用方声明的正常链协议或显式排序约束。')
    constraints = observation.get('ordering_constraints', [])
    if not isinstance(constraints, list) or len(constraints) > 512 or (protocol == 'declared_normal_chain' and constraints):
        raise ValueError('显式约束最多512条，不能与正常链预设混合。')
    clock, origin_bounds, fps = _clock(observation.get('clock'))
    graph = _OrderBounds()
    graph.add('deployment', origin_bounds)
    raw_cycles = observation.get('cycles')
    if not isinstance(raw_cycles, list) or not 1 <= len(raw_cycles) <= 20:
        raise ValueError('cycles需为1–20组界限记录。')
    cycles, ids = [], set()
    for raw in raw_cycles:
        allowed_cycle = {'id', *EVENTS, 'release_stamps', 'release_recording', 'recharge_basis'}
        if not isinstance(raw, dict) or set(raw) - allowed_cycle:
            raise ValueError('周期包含未支持字段。')
        identity = raw.get('id')
        if not isinstance(identity, str) or not identity.strip() or identity in ids or '.' in identity:
            raise ValueError('周期ID需唯一非空且不能包含点号。')
        ids.add(identity)
        recording = raw.get('release_recording', 'unknown')
        basis = raw.get('recharge_basis', 'unknown')
        if recording not in ('all_consecutive', 'selected', 'unknown') or basis not in ('model_depleted_requirement', 'precharged_or_partial', 'unknown'):
            raise ValueError('记录完整度或充值需求类别不明确。')
        event_nodes = {}
        for event in EVENTS:
            reading = _stamp(raw.get(event), clock, fps, identity + '.' + event)
            if reading is not None:
                node = identity + '.' + event
                graph.add(node, reading)
                event_nodes[event] = node
            else:
                event_nodes[event] = None
        releases = raw.get('release_stamps', [])
        if not isinstance(releases, list) or len(releases) > 200:
            raise ValueError('释放界限列表最多200项。')
        release_nodes = []
        for index, value in enumerate(releases):
            node = identity + '.release.' + str(index)
            reading = _stamp(value, clock, fps, node)
            if reading is None:
                raise ValueError('释放列表内不填null；未知时刻使用独立事件null。')
            graph.add(node, reading)
            release_nodes.append(node)
        if release_nodes:
            for event, node in (('first_release', release_nodes[0]), ('last_release', release_nodes[-1])):
                old = event_nodes[event]
                if old is not None:
                    graph.intersect(node, graph.original.pop(old))
                graph.aliases[identity + '.' + event] = node
                event_nodes[event] = node
        if not any(event_nodes.values()) and not release_nodes:
            raise ValueError('每周期至少有一个独立录入的界限。')
        cycles.append({'id': identity, 'event_nodes': event_nodes, 'release_nodes': release_nodes,
                       'release_recording': recording, 'recharge_basis': basis})
    if protocol == 'declared_normal_chain':
        for node in graph.original:
            if node != 'deployment':
                graph.order('deployment', node)
        previous_start = previous_end = None
        for cycle in cycles:
            events = cycle['event_nodes']
            known = [events[key] for key in EVENTS if events[key] is not None]
            for a, b in zip(known, known[1:]):
                graph.order(a, b)
            for a, b in zip(cycle['release_nodes'], cycle['release_nodes'][1:]):
                graph.order(a, b, True)
            if events['start']:
                if previous_start:
                    graph.order(previous_start, events['start'], True)
                if previous_end:
                    graph.order(previous_end, events['start'])
                previous_start = events['start']
            if events['end']:
                if previous_end:
                    graph.order(previous_end, events['end'])
                previous_end = events['end']
    else:
        for row in constraints:
            if not isinstance(row, dict) or set(row) != {'before', 'after', 'strict'} or not isinstance(row['strict'], bool):
                raise ValueError('显式约束需为before/after/strict对象。')
            graph.order(row['before'], row['after'], row['strict'])
    graph.solve()
    rows, repeats, intervals = [], [], []
    refs = reference['conditional_references']
    def measure(cycle_id, metric, a, b, expected):
        interval = graph.difference(a, b)
        return {'cycle_id': cycle_id, 'metric': metric, 'label': LABELS[metric],
            'observed_interval_seconds': interval, 'conditional_reference_seconds': expected,
            'residual_interval_seconds': _residual(interval, expected),
            'classification': _classify(interval, expected, tolerance),
            'actual_native_reference_seconds': None, 'actual_cause_of_difference': None}
    for index, cycle in enumerate(cycles):
        event = cycle['event_nodes']
        compatible = cycle['recharge_basis'] == 'model_depleted_requirement'
        definitions = [
            ('initial_ready', 'deployment' if index == 0 else None, event['ready'], refs['initial_ready'] if index == 0 and observation['first_cycle_is_initial'] else None),
            ('activation_wait', event['ready'], event['start'], None),
            ('first_release', event['start'], event['first_release'], None),
            ('release_span', event['first_release'], event['last_release'], None),
            ('active_duration', event['start'], event['end'], None),
            ('unlock_delay', event['end'], event['unblocked'], None),
            ('unblocked_recharge', event['unblocked'], event['next_ready'], None),
            ('recharge', event['end'], event['next_ready'], refs['recharge'] if compatible else None),
            ('cycle_to_ready', event['start'], event['next_ready'], refs['cycle_to_ready'] if compatible else None),
        ]
        rows.extend(measure(cycle['id'], metric, a, b, expected) for metric, a, b, expected in definitions)
        compatible_release = kind == 'body_attack_release' and cycle['release_recording'] == 'all_consecutive' and reference['constant_body_interval_reference_available']
        for release_index, (a, b) in enumerate(zip(cycle['release_nodes'], cycle['release_nodes'][1:]), 1):
            row = measure(cycle['id'], 'release_interval', a, b, reference['body_interval_conditional_reference_seconds'] if compatible_release else None)
            row['recorded_interval_index'] = release_index
            intervals.append(row)
        if index:
            previous = cycles[index - 1]['event_nodes']
            row = measure(cycle['id'], 'start_to_start', previous['start'], event['start'], None)
            row.update(previous_cycle_id=cycles[index - 1]['id'],
                previous_start_to_next_ready_interval_seconds=graph.difference(previous['start'], previous['next_ready']),
                next_ready_to_current_start_interval_seconds=graph.difference(previous['next_ready'], event['start']))
            repeats.append(row)
    speed_raw = observation.get('attack_speed_attribute')
    speed = None if speed_raw is None else _interval(*_reading(speed_raw, '独立攻速属性界限'))
    speed_reference = refs['attack_speed_attribute']
    return {'operator': reference['operator'], 'skill_name': reference['skill_name'],
        'skill_identity': reference['skill_identity'], 'context_token': reference['context_token'],
        'evidence_kind': observation['evidence_kind'], 'source': observation['source'], 'clock': clock,
        'ordering_protocol': protocol, 'ordering_is_caller_declaration': True, 'joint_constraints_feasible': True,
        'reading_domain': 'continuous_time_coverage_intervals',
        'declared_constraints': [{'before': a, 'after': b, 'strict': strict} for a, b, strict in graph.edges],
        'original_readings_seconds': {name: _interval(*bounds) for name, bounds in graph.declared.items()},
        'feasible_readings_seconds': {name: _interval(*graph.feasible[graph.aliases[name]]) for name in graph.declared},
        'declared_observation': deepcopy(observation),
        'event_aliases': graph.aliases, 'comparisons': rows, 'release_interval_rows': intervals,
        'repeat_cycle_rows': repeats, 'tolerance_seconds': tolerance_seconds,
        'attack_speed_comparison': {'observed_interval': speed, 'conditional_reference': speed_reference,
            'residual_interval': _residual(speed, speed_reference), 'classification': _classify(speed, speed_reference, Fraction(0)),
            'note': '独立攻速属性界限；不从视频间隔推导。'},
        'reference': reference, 'native_verified': False, 'actual_cause_of_difference': None}


def bounded_calibration(panel=None, timing=None, panel_tolerance=0, timing_tolerance_seconds=0):
    """One workspace for bounded panel and event records, each independently sourced."""
    if panel is None and timing is None:
        raise ValueError('至少需一组面板或时刻界限记录。')
    for value, keys, label in ((panel, {'before', 'after'}, '面板'), (timing, {'scenario', 'observation'}, '时刻')):
        if value is not None and (not isinstance(value, dict) or set(value) != keys):
            raise ValueError(label + '记录结构不正确。')
    _number(panel_tolerance, '明确面板容差')
    _number(timing_tolerance_seconds, '明确秒数容差')
    return {'scope': 'explicit_reading_bounds_and_declared_clock_constraints',
        'panel': None if panel is None else compare_bounded_panels(**deepcopy(panel), tolerance=panel_tolerance),
        'timing': None if timing is None else compare_bounded_timing(**deepcopy(timing), tolerance_seconds=timing_tolerance_seconds),
        'native_verified': False, 'actual_causal_attribution': None,
        'notes': ['所有界限、来源与排序协议均由调用方明确声明，不猜测测量精度、视频误差或置信度。',
            '时间界限是连续覆盖范围；视频整帧只作为端点坐标，不表示事件必须位于离散整数帧。',
            '所有可行值相符、可能重叠、无重叠分别显示；可能重叠不是通过认证。',
            '联合不可行只表示与已声明排序协议冲突，不证明实际游戏行为不可能。',
            '首出手、实际结束、解除阻回和当前热更新未绑定；原生参考及因果归属保持未知。']}


def public_bounded_payload(operator='kaltsit'):
    """Degenerate literal formula readings; no default game error margin."""
    from .paired_calibration import public_paired_payload
    from .timing_calibration import public_timing_payload, EVENTS
    pair = public_paired_payload(operator)
    for side in ('before', 'after'):
        observation = pair[side]['observation']
        observation['values'] = {key: [value, value] for key, value in observation['values'].items()}
    timing = public_timing_payload(operator)
    observation = timing['observation']
    clock = observation['clock']
    clock['origin_stamp'] = [clock['origin_stamp'], clock['origin_stamp']]
    observation.update(ordering_protocol='declared_normal_chain', ordering_constraints=[])
    for cycle in observation['cycles']:
        for key in EVENTS:
            if cycle.get(key) is not None:
                value = cycle[key].pop('value')
                cycle[key]['bounds'] = [value, value]
    speed = observation['attack_speed_attribute']
    observation['attack_speed_attribute'] = [speed, speed]
    return {'panel': {'before': pair['before'], 'after': pair['after']},
        'timing': {'scenario': timing['scenario'], 'observation': observation},
        'panel_tolerance': 0, 'timing_tolerance_seconds': 0}
