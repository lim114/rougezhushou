"""Declared preprocessing-order precision of six source-bound relics.

This reproduces the saved compositor's single-precision operation widths under
standard IEEE754 nearest-even arithmetic. It never claims runtime acquisition
order, native FP packet conversion or actual final damage.
"""
from copy import deepcopy
from decimal import Decimal
from functools import lru_cache
from itertools import permutations
from pathlib import Path
import hashlib
import json
import struct


IDS = tuple('rogue_6_relic_legacy_' + str(i) for i in range(5, 11))
SOURCE = 'research/p2-direct-continuation/relic-order-source-audit.json'
DATA_SHA256 = 'c31555d9f88a73a9bcad0bfcf0a69940b2b2109511e694ab6c7c72c31e78613d'
FAMILY_NAMES = {'physical': '物理承伤参数组', 'magic': '法术承伤参数组'}


@lru_cache(maxsize=1)
def _precision_source_data():
    try:
        raw = (Path(__file__).with_name('data') / 'relic-order-precision-source.json').read_bytes()
    except OSError:
        return None
    if hashlib.sha256(raw).hexdigest() != DATA_SHA256:
        return None
    return json.loads(raw)


def precision_sources():
    return deepcopy(_precision_source_data())


def supported_precision_sources():
    source = precision_sources()
    return deepcopy(source['records']) if source is not None else []


def _f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def _bits(value):
    return '0x' + struct.pack('>f', value).hex()


def _decimal_reference(records):
    return sum((Decimal(str(r['parameter'])) for r in records), Decimal(1)) - len(records)


def _existing_reference(records, family):
    # Compare to the actual existing composer; do not modify it or pretend a
    # changed/unbound current catalog still has the sealed source parameters.
    from .relics import mechanics
    from .relic_damage_factors import source_factor, verified_rule
    rules = []
    for record in records:
        packet = mechanics()['relics'].get(record['relic_id'], {})
        matching = [dict(r, relic_id=record['relic_id'], _verified_rule=True)
                    for r in packet.get('effects', []) if r.get('kind') == 'damage_taken'
                    and r.get('damage_type') == family]
        if len(matching) != 1 or not verified_rule(matching[0], family):
            return None
        rules.extend(matching)
    return source_factor(rules, family)


def _run_order(order, records, include_steps=False):
    carried, seen, steps = {}, {}, []
    for ordinal, identity in enumerate(order, 1):
        source = records[identity]
        family = source['damage_family']
        incoming = _f32(source['parameter'])
        previous = carried.get(family)
        addition = None if previous is None else _f32(previous + incoming)
        merged = incoming if previous is None else _f32(addition - _f32(1))
        carried[family] = merged
        seen.setdefault(family, []).append(source)
        if include_steps:
            decimal = _decimal_reference(seen[family])
            steps.append({'ordinal': ordinal, 'relic_id': identity, 'name': source['name'],
                'damage_family': family, 'prefab_group': source['prefab_group'],
                'source_parameter_decimal_text': str(source['parameter']),
                'incoming_f32': incoming, 'incoming_bits': _bits(incoming),
                'previous_group_f32': previous, 'previous_group_bits': None if previous is None else _bits(previous),
                'first_group_record_is_copy': previous is None,
                'rounded_addition_f32': addition, 'rounded_addition_bits': None if addition is None else _bits(addition),
                'group_result_f32': merged, 'group_result_bits': _bits(merged),
                'exact_decimal_reference_text': str(decimal),
                'f32_minus_exact_decimal_text': str(Decimal.from_float(merged) - decimal),
                'groups_after_step': {key: {'value_f32': value, 'bits': _bits(value)} for key, value in carried.items()},
                'actual_final_packet_factor': None})
    return {'order': list(order), 'family_outcomes': {
        family: {'value_f32': value, 'bits': _bits(value)} for family, value in carried.items()},
        **({'steps': steps} if include_steps else {})}


def _validate(payload):
    allowed = {'relic_ids', 'declared_processing_order', 'before_constraints'}
    if type(payload) is not dict or set(payload) - allowed or 'relic_ids' not in payload:
        raise ValueError('精度诊断需要relic_ids，可选declared_processing_order和before_constraints。')
    selected = payload['relic_ids']
    if type(selected) is not list or not 1 <= len(selected) <= 6 or any(type(i) is not str or i not in IDS for i in selected):
        raise ValueError('选择需要1–6件已证来源ID；不接受未知来源或其它伤害类型冒用。')
    if len(set(selected)) != len(selected):
        raise ValueError('同一来源ID不能重复；没有据此建模重复实际持有或重新获取。')
    constraints = payload.get('before_constraints', [])
    if type(constraints) is not list or len(constraints) > 30:
        raise ValueError('先后约束需要最多30项ID二元列表。')
    pairs = []
    for pair in constraints:
        if type(pair) is not list or len(pair) != 2 or any(type(i) is not str or i not in selected for i in pair) or pair[0] == pair[1]:
            raise ValueError('每项先后约束需要两个不同、已选择的来源ID。')
        if pair in pairs:
            raise ValueError('先后约束不能重复。')
        pairs.append(list(pair))
    accepted = []
    for order in permutations(sorted(selected)):
        positions = {identity: ordinal for ordinal, identity in enumerate(order)}
        if all(positions[a] < positions[b] for a, b in pairs):
            accepted.append(order)
    if not accepted:
        raise ValueError('先后约束存在循环冲突，没有可接受处理顺序。')
    declared = payload.get('declared_processing_order')
    if declared is not None:
        if type(declared) is not list or len(declared) != len(selected) or any(type(i) is not str for i in declared) or set(declared) != set(selected):
            raise ValueError('声明处理顺序需要每个已选来源恰好一次。')
        if tuple(declared) not in accepted:
            raise ValueError('声明处理顺序与填写的先后约束冲突。')
    return selected, pairs, declared, accepted


def diagnose_relic_processing_order(payload):
    selected, constraints, declared, accepted = _validate(payload)
    source = precision_sources()
    result = {'scope': 'declared_preprocessing_order_binary32_parameter_diagnostic',
        'declaration': deepcopy(payload), 'relic_ids': list(selected), 'before_constraints': constraints,
        'declared_processing_order': deepcopy(declared), 'accepted_order_count': len(accepted),
        'unconstrained_distinct_order_count': len(list(permutations(selected))),
        'source_available': source is not None, 'source': SOURCE,
        'arithmetic_policy': 'IEEE754 binary32 nearest-even; round each add and subtract separately; first group record copied',
        'groups_start_empty_as_reference_condition': True,
        'runtime_acquisition_to_processing_order_verified': False, 'actual_processing_order': None,
        'runtime_binding_verified': False, 'current_hotfix_equivalence_proven': False,
        'actual_fp_control_mode': None, 'actual_final_packet_factor': None,
        'actual_damage': None, 'enumeration_counts_are_probabilities': False,
        'actual_probability_by_order': None,
        'notes': ['选择清单不提供实际顺序。留空声明顺序时，枚举所有满足调用方先后约束的不同排列。',
            '每组从空的声明来源组开始；第一个来源复制参数，后续同一prefabKey才逐次合并。没有填入其它隐藏背景来源。',
            '物理与法术分别合并，不跨组相加或把两组倍率乘成一个总倍率。',
            '参考按IEEE754单精度最近偶数算术；加和减分别取单精度，不能仅把最终十进制结果转换一次。',
            '最小/最大值只是边界；仅列出的离散bit结果属于可接受顺序结果，中间bit不自动列为候选。',
            '顺序数量是完整枚举计数，不是实际出现频率或概率；未推定OnStack、实时获取或获取到列表顺序的绑定。',
            '当前十进制模型只作对照，原默认引擎数值不改。合并黑板参数不等于最终FP伤害包、实际承伤倍率或实机认证。']}
    if source is None:
        result.update(selected_sources=None, families=None, order_outcomes=None,
                      joint_outcomes=None, declared_order_trace=None)
        result['notes'].append('六件固定原件派生包缺失或哈希不符，数值和范围保持未知；没有按1或0补齐。')
        return result
    all_records = {r['relic_id']: r for r in source['records']}
    records = {identity: all_records[identity] for identity in selected}
    outcomes = [_run_order(order, records) for order in accepted]
    families, joint = [], {}
    for family in ('physical', 'magic'):
        members = [r for r in records.values() if r['damage_family'] == family]
        if not members:
            continue
        decimal = _decimal_reference(members)
        model = _existing_reference(members, family)
        values = {}
        for outcome in outcomes:
            value = outcome['family_outcomes'][family]
            key = value['bits']
            if key not in values:
                values[key] = {**value, 'accepted_order_count': 0,
                    'example_order': list(outcome['order']),
                    'f32_minus_existing_decimal_model': None if model is None else value['value_f32'] - model,
                    'f32_minus_exact_decimal_text': str(Decimal.from_float(value['value_f32']) - decimal)}
            values[key]['accepted_order_count'] += 1
        discrete = sorted(values.values(), key=lambda row: row['value_f32'])
        low, high = discrete[0], discrete[-1]
        families.append({'damage_family': family, 'name': FAMILY_NAMES[family],
            'prefab_group': members[0]['prefab_group'], 'relic_ids': [r['relic_id'] for r in members],
            'exact_decimal_reference_text': str(decimal), 'existing_decimal_model_reference': model,
            'existing_decimal_model_binary64_hex': None if model is None else '0x' + struct.pack('>d', model).hex(),
            'single_final_cast_of_exact_decimal_f32': _f32(float(decimal)),
            'single_final_cast_of_exact_decimal_bits': _bits(_f32(float(decimal))),
            'discrete_outcomes': discrete, 'distinct_outcome_count': len(discrete),
            'minimum_f32': low['value_f32'], 'minimum_bits': low['bits'],
            'maximum_f32': high['value_f32'], 'maximum_bits': high['bits'],
            'range_width': high['value_f32'] - low['value_f32'],
            'bit_word_span': int(high['bits'], 16) - int(low['bits'], 16),
            'actual_final_packet_factor': None})
    for outcome in outcomes:
        key = tuple((family, outcome['family_outcomes'][family]['bits']) for family in sorted(outcome['family_outcomes']))
        if key not in joint:
            joint[key] = {'family_outcomes': deepcopy(outcome['family_outcomes']),
                          'accepted_order_count': 0, 'example_order': list(outcome['order'])}
        joint[key]['accepted_order_count'] += 1
    result.update(selected_sources=deepcopy(list(records.values())), families=families,
        order_outcomes=outcomes, joint_outcomes=list(joint.values()),
        declared_order_trace=_run_order(declared, records, include_steps=True) if declared is not None else None)
    return result


def public_relic_order_payload(kind='magic'):
    if kind not in ('physical', 'magic', 'both'):
        raise ValueError('公开示例需要physical、magic或both。')
    selected = IDS[:3] if kind == 'physical' else IDS[3:] if kind == 'magic' else IDS
    return {'relic_ids': list(selected), 'declared_processing_order': None, 'before_constraints': []}


def format_relic_processing_order(result):
    lines = ['六件固定藏品 · 声明处理顺序精度诊断',
             f"满足声明约束的不同顺序：{result['accepted_order_count']}（不是概率）"]
    if not result['source_available']:
        lines.append('来源包不可用；参数数值及范围：未知。')
    else:
        for family in result['families']:
            model = '未知' if family['existing_decimal_model_reference'] is None else str(family['existing_decimal_model_reference'])
            lines.append(f"{family['name']}：当前十进制模型{model}；"
                f"不同bit结果{family['distinct_outcome_count']}种；单次末端转换{family['single_final_cast_of_exact_decimal_bits']}")
            for outcome in family['discrete_outcomes']:
                lines.append(f"  {outcome['value_f32']:.17g} / {outcome['bits']}；枚举顺序{outcome['accepted_order_count']}；"
                    f"相对精确十进制差{outcome['f32_minus_exact_decimal_text']}")
        trace = result['declared_order_trace']
        if trace is None:
            lines.append('处理顺序未声明；不替用户选择实际顺序。')
        else:
            lines.append('明确声明顺序的逐步结果：')
            for row in trace['steps']:
                operation = '首件复制' if row['first_group_record_is_copy'] else '同组加后减1，各自取单精度'
                lines.append(f"  第{row['ordinal']}步 {row['name']}：{operation}；"
                    f"{row['group_result_f32']:.17g} / {row['group_result_bits']}；相对十进制差{row['f32_minus_exact_decimal_text']}")
    lines.extend(['实际处理顺序、获取到处理顺序绑定、最终FP包及实际伤害：未知。', *result['notes']])
    return '\n'.join(lines)
