"""All-RC cost integer consensus under conditional ordinary hardware completion."""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

PROOF_SHA256 = '67455e993a068f538bda96bb45d6c5e6b33fb1357894c873bc73c39d691a5bc6'
MANIFEST_SHA256 = 'e33d2e344bc4838662da9314bd87190f0a518891d64be2f1a1aaece163b42bd5'
SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / 'research/p2-cost-rounding-consensus-280'
RC_SCOPE = 'all16_independent_RC_pairs_conservative_superset'
KINDS = ('rune_add', 'rune_mul', 'relic_mul')
STAGES = ('modifier_read', 'cost_decode', 'int32_to_single', 'single_operation', 'round')
UNKNOWNS = ('actual_cost_after', 'actual_sp_after', 'complete_cycle')
ACTION_KEYS = {'id', 'kind', 'ordinary_native_path', 'modifier_read', 'cost_decode',
               'conversion_normally', 'operation_normally', 'round_normally'}


def source_data():
    result = {'valid': False, 'status': 'source_unavailable', 'proof_sha256': None,
              'method_count': None, 'byte_span_count': None}
    try:
        manifest_raw = (SOURCE_DIRECTORY / 'source_manifest.json').read_bytes()
        proof_raw = (SOURCE_DIRECTORY / 'source-proof.json').read_bytes()
        if hashlib.sha256(manifest_raw).hexdigest() != MANIFEST_SHA256:
            return {**result, 'status': 'manifest_sha_mismatch'}
        if hashlib.sha256(proof_raw).hexdigest() != PROOF_SHA256:
            return {**result, 'status': 'proof_sha_mismatch'}
        manifest, proof = json.loads(manifest_raw), json.loads(proof_raw)
        for name, expected in manifest['support_files_sha256'].items():
            if hashlib.sha256((SOURCE_DIRECTORY / name).read_bytes()).hexdigest() != expected:
                return {**result, 'status': 'support_file_sha_mismatch'}
        if (manifest['proof_sha256'] != PROOF_SHA256 or proof['method_count'] != 9
                or proof['unique_instruction_count'] != 546 or proof['byte_span_count'] != 759
                or proof['dll_sha256'] != manifest['dll_sha256']
                or proof['metadata_sha256'] != manifest['metadata_sha256']
                or proof['rc_pair_scope'] != RC_SCOPE or proof['game_dll_executed'] is not False
                or proof['process_memory_read'] is not False
                or proof['all_spans_rechecked_against_fresh_primary_files'] is not True):
            return {**result, 'status': 'source_contract_mismatch'}
        return {'valid': True, 'status': 'pinned_file_source_reference', 'proof_sha256': PROOF_SHA256,
                'method_count': 9, 'byte_span_count': 759}
    except (OSError, ValueError, TypeError, KeyError):
        return result


def _keys(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError(label + ' exact keys required')


def _tri(value, label):
    if value is not None and type(value) is not bool:
        raise ValueError(label + ' must be true/false/null')


def _int(value, label, unsigned=False):
    if value is None:
        return
    low, high = (0, 1 << 32) if unsigned else (-(1 << 31), 1 << 31)
    if type(value) is not int or not low <= value < high:
        raise ValueError(label + ' integer range/type invalid')


def _label(value, label):
    if not isinstance(value, str) or not value.strip() or len(value) > 120:
        raise ValueError(label + ' nonempty public label required')


def _validate(payload):
    _keys(payload, {'receiver_exists', 'actions'}, 'payload')
    _tri(payload['receiver_exists'], 'receiver_exists')
    if not isinstance(payload['actions'], list) or not 1 <= len(payload['actions']) <= 50:
        raise ValueError('actions requires1–50 entries')
    ids = set()
    for action in payload['actions']:
        _keys(action, ACTION_KEYS, 'action')
        _label(action['id'], 'action.id')
        if action['id'] in ids:
            raise ValueError('action/read IDs must be globally unique')
        ids.add(action['id'])
        if not isinstance(action['kind'], str) or action['kind'] not in KINDS:
            raise ValueError('unknown action kind')
        for name in ('ordinary_native_path', 'conversion_normally', 'operation_normally', 'round_normally'):
            _tri(action[name], name)
    for action in payload['actions']:
        for name in ('modifier_read', 'cost_decode'):
            read = action[name]
            value_name = 'bits' if name == 'modifier_read' else 'value'
            _keys(read, {'id', 'normal', value_name}, name)
            _label(read['id'], 'read.id')
            if read['id'] in ids:
                raise ValueError('action/read IDs must be globally unique')
            ids.add(read['id'])
            _tri(read['normal'], 'read.normal')
            _int(read[value_name], value_name, unsigned=value_name == 'bits')


def _power2(exponent):
    return Fraction(1 << exponent) if exponent >= 0 else Fraction(1, 1 << -exponent)


def _single_fraction(bits):
    if bits is None:
        return None, 'modifier_value_unknown'
    exponent, fraction = (bits >> 23) & 255, bits & 0x7fffff
    if exponent == 255:
        return None, 'modifier_nonfinite_environment_unknown'
    if exponent == 0:
        return (Fraction(0), None) if fraction == 0 else (None, 'modifier_subnormal_environment_unknown')
    value = Fraction(0x800000 + fraction) * _power2(exponent - 150)
    return (-value if bits >> 31 else value), None


def _round_single(value, rc):
    """Exact rational normal/zero binary32 rounding; no host floating arithmetic."""
    if value == 0:
        return {'bits': 0, 'exact': True, 'status': 'normal_or_zero_reference'}
    magnitude = abs(value)
    if magnitude < _power2(-126):
        return {'bits': None, 'exact': None, 'status': 'operation_subnormal_or_underflow_environment_unknown'}
    if magnitude > Fraction((1 << 24) - 1) * _power2(104):
        return {'bits': None, 'exact': None, 'status': 'operation_overflow_environment_unknown'}
    exponent = magnitude.numerator.bit_length() - magnitude.denominator.bit_length()
    if magnitude < _power2(exponent):
        exponent -= 1
    scaled = magnitude / _power2(exponent - 23)
    lower, remainder = divmod(scaled.numerator, scaled.denominator)
    exact = remainder == 0
    if rc == 0:
        twice = remainder * 2
        up = twice > scaled.denominator or (twice == scaled.denominator and lower & 1)
    elif rc == 1:
        up = value < 0 and not exact
    elif rc == 2:
        up = value > 0 and not exact
    else:
        up = False
    significand = lower + int(bool(up))
    if significand == 1 << 24:
        exponent += 1
        significand = 1 << 23
    if not -126 <= exponent <= 127:
        return {'bits': None, 'exact': None, 'status': 'operation_exponent_domain_unknown'}
    bits = (0x80000000 if value < 0 else 0) | ((exponent + 127) << 23) | (significand - (1 << 23))
    return {'bits': bits, 'exact': exact, 'status': 'normal_or_zero_reference'}


def _half_even(value):
    lower, remainder = divmod(value.numerator, value.denominator)
    twice = remainder * 2
    return lower + (twice > value.denominator or (twice == value.denominator and lower & 1))


def _consensus(operation, cost, modifier_bits):
    result = {'operation': operation, 'cost_int32': cost, 'modifier_bits': modifier_bits, 'status': 'unknown',
              'rc_pair_scope': RC_SCOPE, 'cost_conversion_candidates': [], 'cases': [],
              'possible_operation_bits': [], 'integer_candidates': [], 'same_rc_integer_candidates': [],
              'int32_to_single_exact': None, 'all_operations_exact': None,
              'integer_consensus_reference': None, 'expanded_beyond_exact_only': False}
    if cost is not None:
        for rc in range(4):
            conversion = _round_single(Fraction(cost), rc)
            assert conversion['bits'] is not None
            result['cost_conversion_candidates'].append({'rc': rc, 'cost_single_bits': conversion['bits'], 'exact': conversion['exact']})
        result['int32_to_single_exact'] = all(c['exact'] for c in result['cost_conversion_candidates'])
    modifier, error = _single_fraction(modifier_bits)
    if cost is None:
        return {**result, 'status': 'cost_value_unknown'}
    if error:
        return {**result, 'status': error}
    all_valid = True
    operation_bits, integers, same_rc = set(), set(), set()
    for conversion in result['cost_conversion_candidates']:
        converted, error = _single_fraction(conversion['cost_single_bits'])
        assert error is None
        ideal = converted + modifier if operation == 'add' else converted * modifier
        for rc in range(4):
            rounded = _round_single(ideal, rc)
            case = {'conversion_rc': conversion['rc'], 'operation_rc': rc,
                    'cost_single_bits': conversion['cost_single_bits'], 'operation_exact': rounded['exact'],
                    'mathematical_numerator': ideal.numerator, 'mathematical_denominator': ideal.denominator,
                    'result_bits_candidates': [], 'status': rounded['status'], 'rounded_int32_reference': None}
            if rounded['bits'] is None:
                all_valid = False
            else:
                case['result_bits_candidates'] = [0, 0x80000000] if ideal == 0 else [rounded['bits']]
                operation_bits.update(case['result_bits_candidates'])
                value, error = _single_fraction(rounded['bits'])
                assert error is None
                integer = _half_even(value)
                if -(1 << 31) <= integer < (1 << 31):
                    case.update(status='normal_signed32_half_even_reference', rounded_int32_reference=integer)
                    integers.add(integer)
                    if conversion['rc'] == rc:
                        same_rc.add(integer)
                else:
                    all_valid = False
                    case['status'] = 'rounded_int32_conversion_domain_unknown'
            result['cases'].append(case)
    result.update(possible_operation_bits=sorted(operation_bits), integer_candidates=sorted(integers),
                  same_rc_integer_candidates=sorted(same_rc))
    exact_flags = [c['operation_exact'] for c in result['cases']]
    result['all_operations_exact'] = None if any(v is None for v in exact_flags) else all(exact_flags)
    if all_valid and len(integers) == 1:
        integer = next(iter(integers))
        result.update(status='all16_normal_RC_pairs_integer_consensus', integer_consensus_reference=integer,
                      expanded_beyond_exact_only=not (result['int32_to_single_exact'] and result['all_operations_exact']))
    else:
        result['status'] = 'RC_integer_outcomes_disagree' if all_valid else 'incomplete_numeric_domain_consensus_unknown'
    return result


def single_cost_consensus_reference(operation, cost, modifier_bits):
    if operation not in ('add', 'mul'):
        raise ValueError('operation must be add/mul')
    _int(cost, 'cost')
    _int(modifier_bits, 'modifier_bits', unsigned=True)
    return _consensus(operation, cost, modifier_bits) if source_data()['valid'] else None


class _Trace:
    def __init__(self, action):
        self.action = action
        self.row = {'id': action['id'], 'kind': action['kind'], 'called': None, 'normal': None, 'status': 'unknown',
                    'stages': [{'name': name, 'called': None, 'normal': None, 'reference': None} for name in STAGES],
                    'consensus_reference': None, 'encoder_argument_reference': None,
                    **{name: None for name in UNKNOWNS}}

    def stage(self, name):
        return self.row['stages'][STAGES.index(name)]

    def complete(self, name, normal, reference=None):
        self.stage(name).update(called=True, normal=normal, reference=deepcopy(reference) if normal is True else None)
        if normal is not True:
            self.row.update(normal=normal, status='prefix_failed' if normal is False else 'prefix_normality_unknown')
            if normal is False:
                for stage in self.row['stages'][STAGES.index(name) + 1:]:
                    stage.update(called=False, normal=None, reference=None)
            return False
        return True


def _action(trace):
    a = trace.action
    for name in ('modifier_read', 'cost_decode'):
        if not trace.complete(name, a[name]['normal'], a[name]):
            return
    operation = 'add' if a['kind'] == 'rune_add' else 'mul'
    reference = _consensus(operation, a['cost_decode']['value'], a['modifier_read']['bits'])
    if not trace.complete('int32_to_single', a['conversion_normally'],
                          {'candidates': reference['cost_conversion_candidates'], 'exact': reference['int32_to_single_exact']}):
        return
    arithmetic_cases = [{**{key: value for key, value in case.items() if key not in ('rounded_int32_reference', 'status')},
                         'status': 'normal_or_zero_Single_candidate_reference' if case['result_bits_candidates']
                         else case['status']}
                        for case in reference['cases']]
    if not trace.complete('single_operation', a['operation_normally'],
                          {'possible_operation_bits': reference['possible_operation_bits'], 'cases': arithmetic_cases,
                           'all_operations_exact': reference['all_operations_exact']}):
        return
    if not trace.complete('round', a['round_normally'], reference):
        return
    trace.row.update(normal=True, status='normal_numeric_prefix_complete_conditional_reference')
    trace.row['consensus_reference'] = reference
    trace.row['encoder_argument_reference'] = reference['integer_consensus_reference']


def skill_cost_rounding_consensus(payload):
    _validate(payload)
    source = source_data()
    rows = []
    for action in payload['actions']:
        trace = _Trace(action)
        receiver = payload['receiver_exists']
        if not source['valid'] or receiver is not True or action['ordinary_native_path'] is not True:
            trace.row.update(called=False if receiver is False else None, normal=False if receiver is False else None,
                             status='receiver_missing' if receiver is False else 'source_or_ordinary_path_unqualified')
            if receiver is False:
                for stage in trace.row['stages']:
                    stage.update(called=False, normal=None, reference=None)
        else:
            trace.row['called'] = True
            _action(trace)
        rows.append(trace.row)
    return {'kind': 'skill_cost_rounding_consensus', 'source': source, 'payload': deepcopy(payload), 'rows': rows,
            **{name: None for name in UNKNOWNS}}


def public_example():
    def action(label, kind, cost, bits):
        return {'id': label, 'kind': kind, 'ordinary_native_path': True,
                'modifier_read': {'id': label + '.modifier', 'normal': True, 'bits': bits},
                'cost_decode': {'id': label + '.cost', 'normal': True, 'value': cost},
                'conversion_normally': True, 'operation_normally': True, 'round_normally': True}
    rows = [action('public.inexact_product_closed_two', 'rune_mul', 10, 0x3e4ccccd),
            action('public.half_boundary_zero_or_one', 'rune_mul', 10, 0x3d4ccccd),
            action('public.single_1_05_cost20_closed21', 'relic_mul', 20, 0x3f866666),
            action('public.single_1_05_cost30_31_or32', 'relic_mul', 30, 0x3f866666),
            action('public.inexact_int32_conversion_closed_zero', 'rune_mul', 16777217, 0),
            action('public.inexact_int32_conversion_disagrees', 'rune_mul', 16777217, 0x3f800000),
            action('public.negative_inexact_product_closed', 'rune_mul', -10, 0x3e4ccccd),
            action('public.add_inexact_closed_ten', 'rune_add', 10, 0x3dcccccd),
            action('public.independent_next_decode', 'rune_mul', 101, 0x3f000000),
            action('public.nonfinite_kept_unknown', 'relic_mul', 20, 0x7f800000)]
    return {'receiver_exists': True, 'actions': rows}
