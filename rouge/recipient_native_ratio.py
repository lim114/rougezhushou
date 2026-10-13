"""Native division-stage HP ratio diagnostics, separate from unknown Clamp01.

Declarations of integer HP or raw FP values are not sampled engine values.
Only an independently declared post-clamp ratio feeds the downstream gate
reference; the division result is never silently substituted for that ratio.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import hashlib
import json

from rouge.catalog import operator_profiles


OPERATORS = ('char_196_sunbr', 'char_2025_shu', 'char_298_susuro')
ONE = 1 << 32
MAX_RAW = (1 << 63) - 1
MAX_INTEGER_HP = (1 << 31) - 1
SOURCE_SHA256 = 'a95e0ac7fe99289825198ce1a59f4143bd5fe21e8669ebf8da0dea9842773ac3'
SOURCE = 'research/p2-recipient-native-ratio/REPORT.md'


@lru_cache(maxsize=1)
def _source():
    try:
        raw = (Path(__file__).with_name('data') / 'recipient-native-ratio-source.json').read_bytes()
    except OSError:
        return None
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        return None
    return json.loads(raw)


def native_positive_ratio_division(numerator_raw, denominator_raw, *, trace=False):
    """The saved positive 0<=x<=y numeric path of FP.op_Division220475.

    This follows the divisor nibble reduction, leading-zero shifts, quotient
    accumulation and final positive rounding. Exception/saturation paths are
    outside the checked HP-ratio domain and are never guessed.
    """
    if (type(numerator_raw) is not int or type(denominator_raw) is not int or
            not 0 <= numerator_raw <= denominator_raw <= MAX_RAW or denominator_raw == 0):
        raise ValueError('原生分商参考需要0≤当前原值≤正最大原值，均为有符号64位整数。')
    remainder, divisor, bit_position, quotient = numerator_raw, denominator_raw, 33, 0
    reduction = 0
    while divisor & 15 == 0 and bit_position >= 4:
        divisor >>= 4
        bit_position -= 4
        reduction += 4
    rows = []
    while remainder and bit_position >= 0:
        leading_zeros = 64 - remainder.bit_length()
        shift = min(leading_zeros, bit_position)
        remainder <<= shift
        bit_position -= shift
        digit, following_remainder = divmod(remainder, divisor)
        contribution = digit << bit_position
        quotient += contribution
        if trace:
            rows.append({'bit_position': bit_position, 'leading_zeros': leading_zeros,
                'left_shift': shift, 'scaled_remainder': remainder,
                'quotient_digit': digit, 'quotient_contribution': contribution,
                'quotient_accumulator': quotient, 'division_remainder': following_remainder})
        bit_position -= 1
        remainder = following_remainder << 1
    rounded = (quotient + 1) >> 1
    if trace:
        return {'quotient_33_fractional_raw': quotient, 'ratio_raw': rounded,
            'divisor_nibble_reduction_bits': reduction, 'divisor_after_reduction': divisor,
            'numeric_steps': rows, 'positive_midpoint_rounds_up': True,
            'Clamp01_applied': False}
    return rounded


def _integer(value, label, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(label + '需要范围内整数，不能使用布尔值、文本或小数。')
    return value


def _label(value, name, maximum=300):
    if (type(value) is not str or not 1 <= len(value) <= maximum or
            any(ord(c) < 32 or 0xd800 <= ord(c) <= 0xdfff for c in value)):
        raise ValueError(name + '需要非空、无控制字符的限定长度文本。')
    return value


def _cultivation(operator, value, source):
    if type(value) is not dict or set(value) != {'elite', 'level', 'potential', 'module_id', 'module_level'}:
        raise ValueError('培养需要elite、level、potential、module_id、module_level。')
    profile = operator_profiles()[operator]
    elite = _integer(value['elite'], '精英阶段', 0, len(profile['phases']) - 1)
    level = _integer(value['level'], '等级', 1, profile['phases'][elite]['max_level'])
    _integer(value['potential'], '潜能', 1, 6)
    stage = _integer(value['module_level'], '模组阶段', 0, 3)
    expected = 'uniequip_002_' + {'char_196_sunbr': 'sunbr', 'char_2025_shu': 'shu', 'char_298_susuro': 'susuro'}[operator]
    identity = value['module_id']
    if identity is None:
        if stage != 0:
            raise ValueError('无模组需要module_id=null和module_level=0。')
        eligible = False
    else:
        if type(identity) is not str or identity != expected or stage == 0:
            raise ValueError('模组身份必须与当前已证干员对应，阶段需要1–3。')
        module = next((m for m in profile['modules'] if m['id'] == identity), None)
        if module is None:
            raise ValueError('当前固定培养资料缺少所选模组。')
        eligible = elite >= module['unlock_elite'] and level >= module['unlock_level']
    trait = None
    if eligible and source is not None:
        scenario = {'operator': operator, **value}
        if operator == 'char_298_susuro':
            from rouge.susuro_healing import selected_trait
        else:
            from rouge.guardian_healing import selected_trait
        trait = selected_trait(profile, scenario)
    return {'declaration': deepcopy(value), 'module_unlock_reference': eligible,
            'matching_source_trait_selected': trait is not None,
            'selected_trait': deepcopy(trait), 'actual_module_attachment_verified': False}


def _last_true_value(maximum, scale, boundary):
    low, high = 0, maximum
    while low < high:
        middle = (low + high + 1) // 2
        if native_positive_ratio_division(middle * scale, maximum * scale) < boundary:
            low = middle
        else:
            high = middle - 1
    return low


def recipient_native_ratio_diagnostic(payload):
    if type(payload) is not dict or set(payload) != {'operator', 'cultivation', 'observations'}:
        raise ValueError('诊断需要operator、cultivation和observations。')
    operator = payload['operator']
    if type(operator) is not str or operator not in OPERATORS:
        raise ValueError('诊断只支持已证古米、黍、苏苏洛的对应模组。')
    source = _source()
    cultivation = _cultivation(operator, payload['cultivation'], source)
    observations = payload['observations']
    if type(observations) is not list or not 1 <= len(observations) <= 32:
        raise ValueError('原值观察声明需要1–32项。')
    info = source['operators'][operator] if source is not None else None
    boundary = None if info is None else source['threshold_raw'] + (source['epsilon_raw'] if info['comparison'] == 'LE' else -source['epsilon_raw'])
    rows, names, limits, previous = [], set(), {}, None
    for ordinal, observation in enumerate(observations, 1):
        required = {'label', 'hp', 'max_hp', 'unit', 'post_clamp_ratio_raw', 'evidence'}
        if type(observation) is not dict or set(observation) != required:
            raise ValueError('每项需要label、hp、max_hp、unit、post_clamp_ratio_raw和evidence。')
        label = _label(observation['label'], '观察标签', 80)
        if label in names:
            raise ValueError('观察标签不能重复。')
        names.add(label)
        unit = observation['unit']
        if type(unit) is not str or unit not in ('integer_hp', 'fp_raw'):
            raise ValueError('unit需要integer_hp或fp_raw；整数面板声明不自动当作内部精确原值。')
        cap, scale = (MAX_INTEGER_HP, ONE) if unit == 'integer_hp' else (MAX_RAW, 1)
        maximum = _integer(observation['max_hp'], '最大生命声明', 1, cap)
        hp = _integer(observation['hp'], '当前生命声明', 0, maximum)
        after = observation['post_clamp_ratio_raw']
        if after is not None:
            _integer(after, '独立后置比例原值', 0, ONE)
        evidence = observation['evidence']
        if type(evidence) is not dict or set(evidence) != {'kind', 'source'}:
            raise ValueError('原值证据需要kind和source，始终只作为调用方声明。')
        if type(evidence['kind']) is not str or evidence['kind'] not in ('formula_reference', 'public_case', 'game_panel_declaration'):
            raise ValueError('证据kind需要formula_reference、public_case或game_panel_declaration。')
        _label(evidence['source'], '原值证据来源')
        native = None if source is None else native_positive_ratio_division(hp * scale, maximum * scale, trace=True)
        ratio = None if native is None else native['ratio_raw']
        exact_truncated = None if source is None else (hp * ONE) // maximum
        row = {'ordinal': ordinal, 'label': label, 'original_declaration': deepcopy(observation),
            'hp_raw_reference': hp * scale, 'max_hp_raw_reference': maximum * scale,
            'native_division': native, 'native_division_ratio_raw': ratio,
            'ratio_stage_fraction': None if ratio is None else ratio / ONE,
            'exact_rational_truncated_ratio_raw': exact_truncated,
            'native_minus_exact_truncation_raw': None if ratio is None else ratio - exact_truncated,
            'comparison_boundary_raw': boundary,
            'division_stage_gate_reference': None if boundary is None else ratio < boundary,
            'exact_truncation_gate_reference': None if boundary is None else exact_truncated < boundary,
            'post_clamp_ratio_raw_declaration': after,
            'post_clamp_matches_division_reference': None if ratio is None or after is None else after == ratio,
            'declared_post_clamp_gate_reference': None if boundary is None or after is None else after < boundary,
            'conditional_direct_healing_factor_from_declared_post_ratio': None,
            'last_hp_value_under_division_stage_gate': None, 'first_hp_value_outside_division_stage_gate': None,
            'source_HP_values_verified': False, 'actual_get_hpRatio_raw': None,
            'actual_recipient_qualification': None, 'actual_healing_amount': None,
            'transition_witness': None}
        if boundary is not None:
            key = (unit, maximum)
            if key not in limits:
                limits[key] = _last_true_value(maximum, scale, boundary)
            row['last_hp_value_under_division_stage_gate'] = limits[key]
            row['first_hp_value_outside_division_stage_gate'] = limits[key] + 1
        if row['declared_post_clamp_gate_reference'] is not None and cultivation['matching_source_trait_selected']:
            row['conditional_direct_healing_factor_from_declared_post_ratio'] = source['conditional_heal_scale'] if row['declared_post_clamp_gate_reference'] else 1
        if previous is not None:
            a, b = previous['division_stage_gate_reference'], row['division_stage_gate_reference']
            c, d = previous['declared_post_clamp_gate_reference'], row['declared_post_clamp_gate_reference']
            row['transition_witness'] = {'before_label': previous['label'], 'after_label': label,
                'division_stage_raw_difference': None if ratio is None else ratio - previous['native_division_ratio_raw'],
                'division_stage_gate_changed': None if a is None or b is None else a != b,
                'declared_post_clamp_gate_changed': None if c is None or d is None else c != d,
                'actual_runtime_transition_verified': False,
                'native_HP_trajectory_or_event_order': None}
        rows.append(row)
        previous = row
    return {'scope': 'native_division_stage_and_independent_post_ratio_reference',
        'operator': operator, 'operator_name': info['name'] if info else operator,
        'declaration': deepcopy(payload), 'cultivation': cultivation,
        'source_available': source is not None, 'comparison': info['comparison'] if info else None,
        'fp_one_raw': ONE, 'epsilon_raw': source['epsilon_raw'] if source else None,
        'comparison_boundary_raw': boundary, 'rows': rows, 'source': SOURCE,
        'Clamp01_body_verified': False, 'division_output_used_as_post_clamp_ratio': False,
        'actual_get_hpRatio_verified': False, 'actual_recipient_qualification': None,
        'actual_healing_total': None, 'actual_acquisition_or_event_clock': None,
        'current_hotfix_equivalence_proven': False,
        'notes': ['HP、最大HP、证据来源和观察顺序都是调用方声明；整数面板数不证明内部生命没有小数。',
            '原件除法求33位分商后正值加1再右移1；正数中点向上，区别于精确有理数直接截断。',
            'Clamp01方法体未闭合，因此除法阶段的门参考不代表实际get_hpRatio或实际受疗资格。',
            '独立填写后置比例原值才计算其资格条件和直接治疗参数；留空不会自动借用除法阶段输出。',
            '观察行的门变化只比较明示原值，不生成伤害、治疗、存活/复活、首跳、获取或同帧事件规则。',
            '同一最大HP的末个符合值/首个不符合值仅针对除法阶段参考和当前LT/LE门；不认证实际血量轨迹。',
            '原默认计算与固定比例控件均不改；完整治疗、实际资格、Clamp01和当前热更新仍未知。']}


def public_recipient_ratio_payload(operator='char_196_sunbr'):
    if operator not in OPERATORS:
        raise ValueError('公开参考需要古米、黍或苏苏洛。')
    suffix = {'char_196_sunbr': 'sunbr', 'char_2025_shu': 'shu', 'char_298_susuro': 'susuro'}[operator]
    boundary = ONE // 2 + (42950 if operator != 'char_196_sunbr' else -42950)
    evidence = {'kind': 'formula_reference', 'source': '公开FP除法与严格门算术参考；非游戏采样'}
    return {'operator': operator, 'cultivation': {'elite': 2, 'level': 60 if operator == 'char_2025_shu' else 40,
        'potential': 1, 'module_id': 'uniequip_002_' + suffix, 'module_level': 1},
        'observations': [
            {'label': '整数HP低于门参考', 'hp': 49998, 'max_hp': 100000, 'unit': 'integer_hp',
             'post_clamp_ratio_raw': None, 'evidence': deepcopy(evidence)},
            {'label': '原值分商位于严格门中点', 'hp': 2 * boundary - 1, 'max_hp': 2 * ONE, 'unit': 'fp_raw',
             'post_clamp_ratio_raw': None, 'evidence': deepcopy(evidence)},
            {'label': '独立明示后置原值', 'hp': 2 * boundary - 1, 'max_hp': 2 * ONE, 'unit': 'fp_raw',
             'post_clamp_ratio_raw': boundary - 1, 'evidence': deepcopy(evidence)}]}


def format_recipient_ratio_diagnostic(result):
    lines = [result['operator_name'] + ' · HP原值与受疗门诊断',
        f"固定比较{result['comparison']}；严格边界原值{result['comparison_boundary_raw']}；模组门满足：{result['cultivation']['module_unlock_reference']}"]
    for row in result['rows']:
        original = row['original_declaration']
        text = lambda value: '未知' if value is None else str(value)
        lines.append(f"{row['ordinal']}. {row['label']}：{original['hp']}/{original['max_hp']}（{original['unit']}）；来源：{original['evidence']['source']}")
        lines.append('除法阶段原值' + text(row['native_division_ratio_raw']) + '；精确截断原值' + text(row['exact_rational_truncated_ratio_raw']) +
            '；差' + text(row['native_minus_exact_truncation_raw']) + '；仅除法阶段门参考' + text(row['division_stage_gate_reference']))
        lines.append('独立后置原值' + text(row['post_clamp_ratio_raw_declaration']) + '；后置资格参考' + text(row['declared_post_clamp_gate_reference']) +
            '；对应直接治疗参数' + text(row['conditional_direct_healing_factor_from_declared_post_ratio']))
        lines.append('仅除法阶段：末个符合HP值' + text(row['last_hp_value_under_division_stage_gate']) + '，首个不符合' + text(row['first_hp_value_outside_division_stage_gate']))
        if row['transition_witness'] is not None:
            witness = row['transition_witness']
            lines.append('相对前行除法门变化：' + text(witness['division_stage_gate_changed']) + '；明示后置门变化：' + text(witness['declared_post_clamp_gate_changed']))
    return '\n'.join([*lines, '实际get_hpRatio、受疗资格、HP轨迹和完整治疗：未知。', *result['notes']])
