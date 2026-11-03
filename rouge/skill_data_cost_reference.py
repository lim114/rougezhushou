"""Source-bound cost data transformations. Actual costs/SP/clocks stay unknown."""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

PROOF_SHA256 = '823f5e9fca98291bba30336b2836f9167bbc4242c774c1fb93695cd0d17c7f30'
MANIFEST_SHA256 = 'f364880423bd7aebc707c0cee231287dfa3b4772306a97468bd75e5c73c1742d'
SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / 'research/p2-skill-data-cost-278'
UNKNOWNS = ('actual_cost_after', 'actual_sp_after', 'complete_cycle')
SINGLE_KINDS = ('rune_add', 'rune_mul', 'relic_mul')
SINGLE_STAGES = ('owner_read', 'character_data_read', 'skill_data_read', 'blackboard_read',
                 'modifier_read', 'sp_data_read', 'cost_copy', 'cost_decode', 'single_conversion',
                 'single_arithmetic', 'round', 'encode', 'store')
STAGES = {**{kind: SINGLE_STAGES for kind in SINGLE_KINDS},
          'scale_cost': ('first_data_read', 'first_sp_data_read', 'cost_copy', 'cost_decode', 'scale_read',
                         'imul', 'encode', 'store', 'owner_read', 'second_data_read', 'update'),
          'replace_cost': ('first_data_read', 'first_sp_data_read', 'encode', 'first_sp_data_check',
                           'store', 'modify_type_read', 'second_data_read', 'second_sp_data_read',
                           'type_value_read', 'type_store', 'first_owner_read', 'unity_truth_read',
                           'second_owner_read', 'third_data_read', 'update')}
SINGLE_POINTERS = ('owner_read', 'character_data_read', 'skill_data_read', 'blackboard_read', 'sp_data_read')
SINGLE_FLAGS = ('cost_copy_normally', 'single_conversion_normally', 'single_arithmetic_normally',
                'round_normally', 'encode_normally', 'store_normally')
SCALE_POINTERS = ('first_data_read', 'first_sp_data_read', 'owner_read', 'second_data_read')
REPLACE_POINTERS = ('first_data_read', 'first_sp_data_read', 'second_data_read', 'second_sp_data_read',
                    'first_owner_read', 'second_owner_read', 'third_data_read')
COMMON = {'id', 'kind', 'ordinary_native_path'}
EXTRA = {**{kind: set(SINGLE_POINTERS + SINGLE_FLAGS) | {'modifier_read', 'cost_decode', 'encoded_payload_identity'}
            for kind in SINGLE_KINDS},
         'scale_cost': set(SCALE_POINTERS) | {'cost_decode', 'scale_read', 'cost_copy_normally',
                        'encode_normally', 'store_normally', 'update_normally', 'encoded_payload_identity', 'update_sp_data_identity'},
         'replace_cost': set(REPLACE_POINTERS) | {'new_cost', 'modify_type_read', 'type_value_read', 'unity_truth_read',
                          'encode_normally', 'store_normally', 'type_store_normally', 'update_normally',
                          'encoded_payload_identity', 'update_sp_data_identity'}}


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
        if (manifest['proof_sha256'] != PROOF_SHA256 or proof['method_count'] != 32
                or proof['byte_span_count'] != 4034 or proof['dll_sha256'] != manifest['dll_sha256']
                or proof['metadata_sha256'] != manifest['metadata_sha256']
                or proof['game_dll_executed'] is not False or proof['process_memory_read'] is not False
                or proof['all_spans_rechecked_against_fresh_primary_files'] is not True):
            return {**result, 'status': 'source_contract_mismatch'}
        return {'valid': True, 'status': 'pinned_file_source_reference', 'proof_sha256': PROOF_SHA256,
                'method_count': 32, 'byte_span_count': 4034}
    except (OSError, ValueError, TypeError, KeyError):
        return result


def _keys(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError(label + ' exact keys required')


def _tri(value, label):
    if value is not None and type(value) is not bool:
        raise ValueError(label + ' must be true/false/null')


def _int(value, label, bits=32, unsigned=False, nullable=True):
    if value is None and nullable:
        return
    low, high = (0, 1 << bits) if unsigned else (-(1 << (bits - 1)), 1 << (bits - 1))
    if type(value) is not int or not low <= value < high:
        raise ValueError(label + ' integer range/type invalid')


def _label(value, name, nullable=False):
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value.strip() or len(value) > 120:
        raise ValueError(name + ' public nonempty label required')


def _read_validation(read, kind, ids):
    extras = {'exists', 'identity'} if kind == 'pointer' else {'found', 'bits'} if kind == 'rune_modifier' else {'bits'} if kind == 'single' else {'value'}
    _keys(read, {'id', 'normal'} | extras, kind)
    _label(read['id'], 'read.id')
    if read['id'] in ids:
        raise ValueError('action/read IDs must be globally unique')
    ids.add(read['id'])
    _tri(read['normal'], 'normal')
    if kind == 'pointer':
        _tri(read['exists'], 'exists')
        _label(read['identity'], 'identity', True)
    elif kind in ('single', 'rune_modifier'):
        _int(read['bits'], 'bits', unsigned=True)
        if kind == 'rune_modifier':
            _tri(read['found'], 'found')
    elif kind == 'bool':
        _tri(read['value'], 'value')
    else:
        _int(read['value'], 'value')


def _validate(payload):
    _keys(payload, {'receiver_exists', 'actions'}, 'payload')
    _tri(payload['receiver_exists'], 'receiver_exists')
    actions = payload['actions']
    if not isinstance(actions, list) or not 1 <= len(actions) <= 50:
        raise ValueError('actions requires1–50 entries')
    ids = set()
    for action in actions:
        if not isinstance(action, dict) or not isinstance(action.get('kind'), str) or action.get('kind') not in EXTRA:
            raise ValueError('unknown action kind')
        _keys(action, COMMON | EXTRA[action['kind']], 'action')
        _label(action['id'], 'action.id')
        if action['id'] in ids:
            raise ValueError('action/read IDs must be globally unique')
        ids.add(action['id'])
    for action in actions:
        kind = action['kind']
        _tri(action['ordinary_native_path'], 'ordinary_native_path')
        _label(action['encoded_payload_identity'], 'encoded_payload_identity', True)
        if kind in SINGLE_KINDS:
            pointers, flags = SINGLE_POINTERS, SINGLE_FLAGS
            _read_validation(action['modifier_read'], 'single' if kind == 'relic_mul' else 'rune_modifier', ids)
            _read_validation(action['cost_decode'], 'int', ids)
        elif kind == 'scale_cost':
            pointers = SCALE_POINTERS
            flags = ('cost_copy_normally', 'encode_normally', 'store_normally', 'update_normally')
            _read_validation(action['cost_decode'], 'int', ids)
            _read_validation(action['scale_read'], 'int', ids)
            _label(action['update_sp_data_identity'], 'update_sp_data_identity', True)
        else:
            pointers = REPLACE_POINTERS
            flags = ('encode_normally', 'store_normally', 'type_store_normally', 'update_normally')
            _int(action['new_cost'], 'new_cost')
            _read_validation(action['modify_type_read'], 'bool', ids)
            _read_validation(action['type_value_read'], 'int', ids)
            _read_validation(action['unity_truth_read'], 'bool', ids)
            _label(action['update_sp_data_identity'], 'update_sp_data_identity', True)
        for name in pointers:
            _read_validation(action[name], 'pointer', ids)
        for name in flags:
            _tri(action[name], name)


def _power2(exponent):
    return Fraction(1 << exponent) if exponent >= 0 else Fraction(1, 1 << -exponent)


def _exact_single(value):
    """Return exact normal/zero IEEE binary32 bits, orNone; no host f32 rounding."""
    value = Fraction(value)
    if value == 0:
        return 0
    magnitude = abs(value)
    exponent = magnitude.numerator.bit_length() - magnitude.denominator.bit_length()
    if magnitude < _power2(exponent):
        exponent -= 1
    if not -126 <= exponent <= 127:
        return None
    significand = magnitude / _power2(exponent - 23)
    if significand.denominator != 1 or not (1 << 23) <= significand < (1 << 24):
        return None
    return ((1 << 31) if value < 0 else 0) | ((exponent + 127) << 23) | (int(significand) - (1 << 23))


def _single_fraction(bits):
    exponent, fraction = (bits >> 23) & 255, bits & ((1 << 23) - 1)
    if exponent == 255:
        return None, 'modifier_nonfinite_unknown'
    if exponent == 0:
        return (Fraction(0), None) if fraction == 0 else (None, 'modifier_subnormal_environment_unknown')
    value = Fraction((1 << 23) + fraction) * _power2(exponent - 127 - 23)
    return (-value if bits >> 31 else value), None


def _half_even(value):
    quotient, remainder = divmod(value.numerator, value.denominator)
    twice = remainder * 2
    return quotient + (twice > value.denominator or (twice == value.denominator and quotient & 1))


def _single_cost(operation, cost, modifier_bits):
    result = {'operation': operation, 'cost_int32': cost, 'modifier_bits': modifier_bits,
              'status': 'unknown', 'cost_single_exact': False, 'binary_operation_exact': None,
              'mathematical_numerator': None, 'mathematical_denominator': None,
              'result_single_bits': None, 'rounded_int32_reference': None}
    if _exact_single(Fraction(cost)) is None:
        return {**result, 'status': 'int32_to_single_rounding_unknown'}
    result['cost_single_exact'] = True
    modifier, error = _single_fraction(modifier_bits)
    if error:
        return {**result, 'status': error}
    exact = Fraction(cost) + modifier if operation == 'add' else Fraction(cost) * modifier
    result.update(mathematical_numerator=exact.numerator, mathematical_denominator=exact.denominator)
    bits = _exact_single(exact)
    if bits is None:
        return {**result, 'status': 'single_arithmetic_environment_or_rounding_unknown', 'binary_operation_exact': False}
    result['binary_operation_exact'] = True
    # A signed-zero result may depend on RC; its final Int32 is still exactly zero.
    result['result_single_bits'] = bits if exact != 0 else None
    integer = _half_even(exact)
    if not -(1 << 31) <= integer < (1 << 31):
        return {**result, 'status': 'rounded_int32_conversion_domain_unknown'}
    return {**result, 'status': 'exact_single_half_even_reference', 'rounded_int32_reference': integer}


def single_cost_reference(operation, cost, modifier_bits):
    if operation not in ('add', 'mul'):
        raise ValueError('operation must be add/mul')
    _int(cost, 'cost', nullable=False)
    _int(modifier_bits, 'modifier_bits', unsigned=True, nullable=False)
    return _single_cost(operation, cost, modifier_bits) if source_data()['valid'] else None


def _signed_scale(cost, scale):
    product = ((cost * scale + (1 << 31)) % (1 << 32)) - (1 << 31)
    return {'cost_int32': cost, 'scale_int32': scale, 'product_int32_reference': product}


def signed_scale_reference(cost, scale):
    _int(cost, 'cost', nullable=False)
    _int(scale, 'scale', nullable=False)
    return _signed_scale(cost, scale) if source_data()['valid'] else None


class _Trace:
    def __init__(self, action):
        self.action = action
        self.names = STAGES[action['kind']]
        self.row = {'id': action['id'], 'kind': action['kind'], 'called': None, 'normal': None, 'status': 'unknown',
                    'stages': [{'name': name, 'called': None, 'normal': None, 'reference': None} for name in self.names],
                    'arithmetic_reference': None, 'encoder_argument_reference': None, 'stored_prefixes': [],
                    'update_arguments': None, **{key: None for key in UNKNOWNS}}

    def stage(self, name):
        return self.row['stages'][self.names.index(name)]

    def skip(self, names):
        for name in names:
            self.stage(name).update(called=False, normal=None, reference=None)

    def stop(self, name, normal, status):
        self.row.update(normal=normal, status=status)
        if normal is False:
            self.skip(self.names[self.names.index(name) + 1:])

    def complete(self, name, normal, reference=None):
        self.stage(name).update(called=True, normal=normal,
                                reference=deepcopy(reference) if normal is True else None)
        if normal is not True:
            self.stop(name, normal, 'prefix_failed' if normal is False else 'prefix_normality_unknown')
            return False
        return True

    def read(self, name):
        read = self.action[name]
        return self.complete(name, read['normal'], read)

    def pointer_check(self, name, exists, normal_null_return=False):
        if exists is True:
            return True
        if exists is False and normal_null_return:
            self.row.update(normal=True, status='no_main_skill_normal_return')
            self.skip(self.names[self.names.index(name) + 1:])
            return False
        self.stop(name, False if exists is False else None,
                  'pointer_missing' if exists is False else 'pointer_existence_unknown')
        return False

    def pointer(self, name, deferred=False, normal_null_return=False):
        if not self.read(name):
            return False
        return True if deferred else self.pointer_check(name, self.action[name]['exists'], normal_null_return)

    def unknown_value(self, name):
        self.stop(name, None, 'independent_value_unknown')

    def store_cost(self):
        if not self.complete('store', self.action['store_normally'], {'byte_count': 20}):
            return False
        self.row['stored_prefixes'].append({'field': 'spCost', 'byte_count': 20,
                                          'payload_identity': self.action['encoded_payload_identity'], 'decoded_value': None})
        return True

    def encode(self, value):
        self.row['encoder_argument_reference'] = value
        return self.complete('encode', self.action['encode_normally'], {'argument': value, 'returned_payload': None})

    def update(self, owner_read, onlycost):
        arguments = {'owner_identity': self.action[owner_read]['identity'],
                     'sp_data_identity': self.action['update_sp_data_identity'], 'only_update_sp_cost': onlycost}
        self.row['update_arguments'] = arguments
        if self.complete('update', self.action['update_normally'], arguments):
            self.row.update(normal=True, status='cost_data_update_call_prefix_complete')


def _single_action(trace):
    a = trace.action
    for name in ('owner_read', 'character_data_read', 'skill_data_read', 'blackboard_read'):
        if not trace.pointer(name, normal_null_return=name == 'skill_data_read'):
            return
    if not trace.read('modifier_read'):
        return
    if a['kind'] != 'relic_mul':
        found = a['modifier_read']['found']
        if found is not True:
            if found is False:
                trace.skip(SINGLE_STAGES[5:])
                trace.row.update(normal=True, status='modifier_key_missing_normal_return')
            else:
                trace.stop('modifier_read', None, 'modifier_presence_unknown')
            return
    if not trace.pointer('sp_data_read'):
        return
    if not trace.complete('cost_copy', a['cost_copy_normally'], {'byte_count': 20, 'fields': None}):
        return
    if not trace.read('cost_decode'):
        return
    cost, bits = a['cost_decode']['value'], a['modifier_read']['bits']
    if cost is None or bits is None:
        trace.unknown_value('cost_decode')
        return
    arithmetic = _single_cost('add' if a['kind'] == 'rune_add' else 'mul', cost, bits)
    if not trace.complete('single_conversion', a['single_conversion_normally'], {'input': cost, 'exact': arithmetic['cost_single_exact']}):
        return
    trace.row['arithmetic_reference'] = arithmetic
    if arithmetic['cost_single_exact'] is not True:
        trace.stop('single_conversion', None, arithmetic['status'])
        return
    if not trace.complete('single_arithmetic', a['single_arithmetic_normally'],
                          {'exact': arithmetic['binary_operation_exact'], 'bits': arithmetic['result_single_bits']}):
        return
    if arithmetic['rounded_int32_reference'] is None:
        trace.stop('single_arithmetic', None, arithmetic['status'])
        return
    rounded = arithmetic['rounded_int32_reference']
    if not trace.complete('round', a['round_normally'], {'integer_reference': rounded}):
        return
    if trace.encode(rounded) and trace.store_cost():
        trace.row.update(normal=True, status='cost_store_prefix_complete')


def _scale_action(trace):
    a = trace.action
    if not trace.pointer('first_data_read') or not trace.pointer('first_sp_data_read'):
        return
    if not trace.complete('cost_copy', a['cost_copy_normally'], {'byte_count': 20, 'fields': None}):
        return
    if not trace.read('cost_decode') or not trace.read('scale_read'):
        return
    cost, scale = a['cost_decode']['value'], a['scale_read']['value']
    if cost is None or scale is None:
        trace.unknown_value('scale_read')
        return
    arithmetic = _signed_scale(cost, scale)
    trace.row['arithmetic_reference'] = arithmetic
    trace.complete('imul', True, arithmetic)
    if not trace.encode(arithmetic['product_int32_reference']) or not trace.store_cost():
        return
    # Raw owner null is checked after the independently invoked second data getter.
    if not trace.pointer('owner_read', deferred=True) or not trace.pointer('second_data_read'):
        return
    if not trace.pointer_check('second_data_read', a['owner_read']['exists']):
        return
    trace.update('owner_read', True)


def _replace_action(trace):
    a = trace.action
    if not trace.pointer('first_data_read') or not trace.pointer('first_sp_data_read', deferred=True):
        return
    if a['new_cost'] is None:
        trace.unknown_value('first_sp_data_read')
        return
    # The encoder call precedes the null guard of the already-read SpData pointer.
    if not trace.encode(a['new_cost']):
        return
    trace.complete('first_sp_data_check', True, {'exists': a['first_sp_data_read']['exists']})
    if not trace.pointer_check('first_sp_data_check', a['first_sp_data_read']['exists']):
        return
    if not trace.store_cost() or not trace.read('modify_type_read'):
        return
    modify = a['modify_type_read']['value']
    if modify is None:
        trace.unknown_value('modify_type_read')
        return
    if modify is True:
        if not trace.pointer('second_data_read') or not trace.pointer('second_sp_data_read') or not trace.read('type_value_read'):
            return
        value = a['type_value_read']['value']
        if not trace.complete('type_store', a['type_store_normally'], {'value': value}):
            return
        trace.row['stored_prefixes'].append({'field': 'spType', 'value': value})
    else:
        trace.skip(('second_data_read', 'second_sp_data_read', 'type_value_read', 'type_store'))
    if not trace.pointer('first_owner_read', deferred=True) or not trace.read('unity_truth_read'):
        return
    truth = a['unity_truth_read']['value']
    if truth is None:
        trace.unknown_value('unity_truth_read')
        return
    if truth is False:
        trace.skip(('second_owner_read', 'third_data_read', 'update'))
        trace.row.update(normal=True, status='unity_owner_false_normal_return')
        return
    # A null second owner does not suppress the third data getter that precedes its guard.
    if not trace.pointer('second_owner_read', deferred=True) or not trace.pointer('third_data_read'):
        return
    if not trace.pointer_check('third_data_read', a['second_owner_read']['exists']):
        return
    trace.update('second_owner_read', not modify)


def skill_data_cost_reference(payload):
    _validate(payload)
    payload = deepcopy(payload)
    source = source_data()
    rows = []
    for action in payload['actions']:
        trace = _Trace(action)
        rows.append(trace.row)
        if not source['valid']:
            trace.row['status'] = 'source_unavailable'
            continue
        receiver = payload['receiver_exists']
        if receiver is not True:
            trace.row.update(called=False if receiver is False else None,
                             normal=False if receiver is False else None,
                             status='receiver_missing' if receiver is False else 'receiver_existence_unknown')
            if receiver is False:
                trace.skip(STAGES[action['kind']])
            continue
        trace.row['called'] = True
        if action['ordinary_native_path'] is not True:
            trace.row['status'] = 'native_branch_unqualified'
            continue
        if action['kind'] in SINGLE_KINDS:
            _single_action(trace)
        elif action['kind'] == 'scale_cost':
            _scale_action(trace)
        else:
            _replace_action(trace)
    return {'kind': 'skill_data_cost_reference', 'source': source, 'payload': payload,
            'rows': rows, **{key: None for key in UNKNOWNS}}


def public_example():
    def pointer(label, identity):
        return {'id': label, 'normal': True, 'exists': True, 'identity': identity}

    def integer(label, value):
        return {'id': label, 'normal': True, 'value': value}

    def boolean(label, value):
        return {'id': label, 'normal': True, 'value': value}

    def single(label, kind, cost, bits):
        action = {'id': label, 'kind': kind, 'ordinary_native_path': True,
                  'cost_decode': integer(label + '.cost', cost),
                  'modifier_read': {'id': label + '.modifier', 'normal': True, 'bits': bits},
                  'encoded_payload_identity': 'declared.payload.' + label}
        if kind != 'relic_mul':
            action['modifier_read']['found'] = True
        for name in SINGLE_POINTERS:
            action[name] = pointer(label + '.' + name, 'declared.' + name)
        for name in SINGLE_FLAGS:
            action[name] = True
        return action

    def scale(label, cost, factor):
        action = {'id': label, 'kind': 'scale_cost', 'ordinary_native_path': True,
                  'cost_decode': integer(label + '.cost', cost), 'scale_read': integer(label + '.factor', factor),
                  'cost_copy_normally': True, 'encode_normally': True, 'store_normally': True, 'update_normally': True,
                  'encoded_payload_identity': 'declared.payload.' + label, 'update_sp_data_identity': 'declared.update.data2'}
        for name in SCALE_POINTERS:
            action[name] = pointer(label + '.' + name, 'declared.' + name)
        return action

    def replacement(label, cost, modify):
        action = {'id': label, 'kind': 'replace_cost', 'ordinary_native_path': True, 'new_cost': cost,
                  'modify_type_read': boolean(label + '.modify', modify),
                  'type_value_read': integer(label + '.type', 6), 'unity_truth_read': boolean(label + '.unity', True),
                  'encode_normally': True, 'store_normally': True, 'type_store_normally': True, 'update_normally': True,
                  'encoded_payload_identity': 'declared.payload.' + label, 'update_sp_data_identity': 'declared.update.data3'}
        for name in REPLACE_POINTERS:
            action[name] = pointer(label + '.' + name, 'declared.' + name)
        return action

    actions = [single('public.tie_even_down', 'rune_mul', 25, 0x3f000000),
               single('public.tie_even_up', 'relic_mul', 23, 0x3f000000),
               single('public.independent_next_decode', 'rune_add', 101, 0x3f000000),
               single('public.negative_no_clamp', 'rune_mul', -23, 0x3f000000),
               single('public.RC_unknown', 'rune_mul', 10, 0x3d4ccccd),
               single('public.int_conversion_unknown', 'relic_mul', 16777217, 0x3f800000),
               scale('public.low32_min', -2147483648, -1),
               replacement('public.onlycost', 30, False),
               replacement('public.type_update', 40, True),
               replacement('public.null_sp_after_encode', 50, False)]
    actions[-1]['first_sp_data_read']['exists'] = False
    return {'receiver_exists': True, 'actions': actions}
