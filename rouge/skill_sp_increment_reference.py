"""Source-bound SP increment initialization/call prefixes, never actual SP/cycles."""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

PROOF_SHA256 = '6d0fe625c510701db798a3552c61847bcd3a38c5bc75d507de840d064fac0504'
MANIFEST_SHA256 = '7354aa0280bd802797e50b44f525d1a40f317395dcbf8366256091315968158c'
SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / 'research/p2-skill-sp-increments-279'
UNKNOWNS = ('actual_array_after', 'actual_sp_after', 'complete_cycle')
INDEX_NAMES = ('TIME', 'ATTACK', 'TAKEN_DAMAGE', 'NEVER_USE')
SLOT_STAGES = ('blackboard_check', 'key_format', 'lookup', 'mask_read', 'mask_set', 'mask_store',
               'increment_copy', 'increment_decode', 'array_read', 'array_check', 'length_read',
               'bounds_check', 'array_store')
STAGES = {
    'sp_data_init': ('blackboard_capture', 'inited_read', 'array_allocation', 'array_install', 'write_barrier')
                    + tuple('s' + str(index) + '.' + name for index in range(4) for name in SLOT_STAGES),
    'skill_data_init': ('inited_read', 'duration_first_read', 'flag_store', 'duration_ge',
                       'first_blackboard_read', 'duration_second_read', 'duration_assign',
                       'sp_data_read', 'second_blackboard_read', 'sp_init'),
    'attack_gain': ('sp_type_read', 'array_read', 'index', 'array_check', 'length_read',
                    'bounds_check', 'amount_read', 'single_to_fp', 'recover_request'),
    'damage_gain': ('sp_type_read', 'cancelled_read', 'modifier_flag_read', 'array_read', 'index',
                    'array_check', 'length_read', 'bounds_check', 'amount_read', 'single_to_fp', 'recover_request'),
}
COMMON = {'id', 'kind', 'ordinary_native_path'}
EXTRA = {
    'sp_data_init': {'captured_blackboard', 'inited_read', 'array_allocation', 'array_install_normally',
                     'write_barrier_normally', 'slots'},
    'skill_data_init': {'inited_read', 'duration_first_read', 'flag_store_normally', 'ge_normally',
                        'first_blackboard_read', 'duration_second_read', 'assign_normally',
                        'sp_data_read', 'second_blackboard_read', 'sp_init_normally'},
    'attack_gain': {'sp_type_read', 'array_read', 'index_normally', 'array_length_read', 'amount_read',
                    'single_to_fp_normally', 'recover_normally'},
    'damage_gain': {'sp_type_read', 'cancelled_read', 'modifier_flag_read', 'array_read', 'index_normally',
                    'array_length_read', 'amount_read', 'single_to_fp_normally', 'recover_normally'},
}
SLOT_KEYS = {'slot', 'key_format_normally', 'key_identity', 'lookup', 'mask_read', 'mask_store_normally',
             'increment_copy_normally', 'increment_decode', 'array_read', 'array_length_read', 'array_store_normally'}


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
        if (manifest['proof_sha256'] != PROOF_SHA256 or proof['method_count'] != 17
                or proof['unique_instruction_count'] != 938 or proof['byte_span_count'] != 1670
                or proof['dll_sha256'] != manifest['dll_sha256']
                or proof['metadata_sha256'] != manifest['metadata_sha256']
                or proof['game_dll_executed'] is not False or proof['process_memory_read'] is not False
                or proof['all_spans_rechecked_against_fresh_primary_files'] is not True):
            return {**result, 'status': 'source_contract_mismatch'}
        return {'valid': True, 'status': 'pinned_file_source_reference', 'proof_sha256': PROOF_SHA256,
                'method_count': 17, 'byte_span_count': 1670}
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


def _label(value, label, nullable=False):
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value.strip() or len(value) > 120:
        raise ValueError(label + ' nonempty public label required')


def _read_validate(read, kind, ids):
    extra = {'exists', 'identity'} if kind == 'pointer' else {'found', 'bits'} if kind == 'lookup' else {'bits'} if kind == 'single' else {'value'}
    _keys(read, {'id', 'normal'} | extra, kind + ' read')
    _label(read['id'], 'read.id')
    if read['id'] in ids:
        raise ValueError('action/read IDs must be globally unique')
    ids.add(read['id'])
    _tri(read['normal'], 'read.normal')
    if kind == 'pointer':
        _tri(read['exists'], 'pointer.exists')
        _label(read['identity'], 'pointer.identity', True)
    elif kind in ('single', 'lookup'):
        _int(read['bits'], 'Single bits', unsigned=True)
        if kind == 'lookup':
            _tri(read['found'], 'lookup.found')
    elif kind == 'bool':
        _tri(read['value'], 'bool.value')
    else:
        _int(read['value'], 'read.value', bits=8 if kind == 'byte' else 32,
             unsigned=kind in ('byte', 'length'))


def _validate(payload):
    _keys(payload, {'receiver_exists', 'actions'}, 'payload')
    _tri(payload['receiver_exists'], 'receiver_exists')
    if not isinstance(payload['actions'], list) or not 1 <= len(payload['actions']) <= 50:
        raise ValueError('actions requires1–50 entries')
    ids = set()
    for action in payload['actions']:
        if not isinstance(action, dict) or not isinstance(action.get('kind'), str) or action['kind'] not in EXTRA:
            raise ValueError('unknown action kind')
        _keys(action, COMMON | EXTRA[action['kind']], 'action')
        _label(action['id'], 'action.id')
        if action['id'] in ids:
            raise ValueError('action/read IDs must be globally unique')
        ids.add(action['id'])
    for action in payload['actions']:
        _tri(action['ordinary_native_path'], 'ordinary_native_path')
        kind = action['kind']
        if kind == 'sp_data_init':
            for name in ('captured_blackboard', 'array_allocation'):
                _read_validate(action[name], 'pointer', ids)
            _read_validate(action['inited_read'], 'bool', ids)
            for name in ('array_install_normally', 'write_barrier_normally'):
                _tri(action[name], name)
            if not isinstance(action['slots'], list) or len(action['slots']) != 4:
                raise ValueError('slots requires four ordered entries')
            for index, slot in enumerate(action['slots']):
                _keys(slot, SLOT_KEYS, 'slot')
                if type(slot['slot']) is not int or slot['slot'] != index:
                    raise ValueError('slot must match index0–3')
                for name in ('key_format_normally', 'mask_store_normally', 'increment_copy_normally', 'array_store_normally'):
                    _tri(slot[name], name)
                _label(slot['key_identity'], 'key_identity', True)
                for name, read_kind in (('lookup', 'lookup'), ('mask_read', 'int'), ('increment_decode', 'single'),
                                        ('array_read', 'pointer'), ('array_length_read', 'length')):
                    _read_validate(slot[name], read_kind, ids)
        elif kind == 'skill_data_init':
            for name, read_kind in (('inited_read', 'bool'), ('duration_first_read', 'single'),
                                    ('first_blackboard_read', 'pointer'), ('duration_second_read', 'single'),
                                    ('sp_data_read', 'pointer'), ('second_blackboard_read', 'pointer')):
                _read_validate(action[name], read_kind, ids)
            for name in ('flag_store_normally', 'ge_normally', 'assign_normally', 'sp_init_normally'):
                _tri(action[name], name)
        else:
            for name, read_kind in (('sp_type_read', 'int'), ('array_read', 'pointer'),
                                    ('array_length_read', 'length'), ('amount_read', 'single')):
                _read_validate(action[name], read_kind, ids)
            for name in ('index_normally', 'single_to_fp_normally', 'recover_normally'):
                _tri(action[name], name)
            if kind == 'damage_gain':
                _read_validate(action['cancelled_read'], 'bool', ids)
                _read_validate(action['modifier_flag_read'], 'byte', ids)


def _power2(exponent):
    return Fraction(1 << exponent) if exponent >= 0 else Fraction(1, 1 << -exponent)


def _single_fraction(bits):
    if bits is None:
        return None, 'Single_value_unknown'
    exponent, fraction = (bits >> 23) & 255, bits & 0x7fffff
    if exponent == 255:
        return None, 'Single_nonfinite_environment_unknown'
    if exponent == 0:
        return (Fraction(0), None) if fraction == 0 else (None, 'Single_subnormal_environment_unknown')
    value = Fraction(0x800000 + fraction) * _power2(exponent - 150)
    return (-value if bits >> 31 else value), None


def _single_ge_zero(bits):
    result = {'bits': bits, 'status': 'unknown', 'rhs_bits': 0, 'adjusted_rhs_bits': 0xb727c5ac,
              'ge_boolean_reference': None}
    value, error = _single_fraction(bits)
    if error:
        return {**result, 'status': error}
    threshold, error = _single_fraction(0xb727c5ac)
    assert error is None
    return {**result, 'status': 'ordered_exact_rhs_zero_inclusive_ge_reference',
            'ge_boolean_reference': value >= threshold}


def _single_increment(bits):
    result = {'bits': bits, 'status': 'unknown', 'scale_q': 4294967296,
              'scaled_numerator': None, 'scaled_denominator': None, 'raw_reference': None}
    value, error = _single_fraction(bits)
    if error:
        return {**result, 'status': error}
    scaled = value * 4294967296
    result.update(scaled_numerator=scaled.numerator, scaled_denominator=scaled.denominator)
    if not -(1 << 63) <= scaled < (1 << 63):
        return {**result, 'status': 'Single_to_Int64_conversion_domain_unknown'}
    # Multiplication by2^32 is exact and normal/zero in this signed64 input domain.
    magnitude = abs(scaled.numerator) // scaled.denominator
    raw = -magnitude if scaled < 0 else magnitude
    return {**result, 'status': 'exact_Single_scale_toward_zero_Int64_reference', 'raw_reference': raw}


def _mask_bit(mask, slot):
    value = None if mask is None else (((mask & 0xffffffff) | (1 << slot)) ^ 0x80000000) - 0x80000000
    return {'mask_int32': mask, 'slot': slot, 'result_int32_reference': value, 'known_set_bit': 1 << slot}


def single_ge_zero_reference(bits):
    _int(bits, 'bits', unsigned=True)
    return _single_ge_zero(bits) if source_data()['valid'] else None


def single_increment_reference(bits):
    _int(bits, 'bits', unsigned=True)
    return _single_increment(bits) if source_data()['valid'] else None


def mask_bit_reference(mask, slot):
    _int(mask, 'mask')
    if type(slot) is not int or not 0 <= slot <= 3:
        raise ValueError('slot must be integer0–3')
    return _mask_bit(mask, slot) if source_data()['valid'] else None


class _Trace:
    def __init__(self, action):
        self.action = action
        self.names = STAGES[action['kind']]
        self.row = {'id': action['id'], 'kind': action['kind'], 'called': None, 'normal': None, 'status': 'unknown',
                    'stages': [{'name': name, 'called': None, 'normal': None, 'reference': None} for name in self.names],
                    'stored_prefixes': [], 'slot_references': [], 'duration_ge_reference': None,
                    'assign_arguments': None, 'sp_init_arguments': None, 'increment_reference': None,
                    'recover_arguments': None, **{name: None for name in UNKNOWNS}}

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

    def read(self, name, read):
        return self.complete(name, read['normal'], read)

    def check_pointer(self, name, exists):
        if exists is True:
            return True
        self.stop(name, False if exists is False else None,
                  'pointer_missing' if exists is False else 'pointer_existence_unknown')
        return False

    def pointer(self, name, read, deferred=False):
        if not self.read(name, read):
            return False
        return True if deferred else self.check_pointer(name, read['exists'])

    def unknown(self, name, status='independent_control_value_unknown'):
        self.stop(name, None, status)

    def early_return(self, name, status):
        self.skip(self.names[self.names.index(name) + 1:])
        self.row.update(normal=True, status=status)

    def bounds(self, name, index, length):
        self.complete(name, True, {'index': index, 'length_uint32': length,
                                  'within_bounds': None if length is None else index < length})
        if length is None:
            self.unknown(name, 'array_length_unknown')
            return False
        if index >= length:
            self.stop(name, False, 'array_index_out_of_bounds')
            return False
        return True


def _sp_data_init(trace):
    a = trace.action
    bb = a['captured_blackboard']
    if not trace.pointer('blackboard_capture', bb, deferred=True) or not trace.read('inited_read', a['inited_read']):
        return
    inited = a['inited_read']['value']
    if inited is True:
        trace.early_return('inited_read', 'already_inited_normal_return_not_full_array_proof')
        return
    if inited is None:
        trace.unknown('inited_read')
        return
    if not trace.pointer('array_allocation', a['array_allocation'], deferred=True):
        return
    allocated = a['array_allocation']
    install = {'field': 'm_incrementsForAllSpTypes', 'identity': allocated['identity'],
               'exists': allocated['exists'], 'requested_length': 4}
    if not trace.complete('array_install', a['array_install_normally'], install):
        return
    trace.row['stored_prefixes'].append(install)
    if not trace.complete('write_barrier', a['write_barrier_normally'], {'array_identity': allocated['identity']}):
        return
    for slot in a['slots']:
        index = slot['slot']
        prefix = 's' + str(index) + '.'
        ref = {'slot': index, 'index_name': INDEX_NAMES[index], 'mask_bit': 1 << index,
               'value_source': 'unknown', 'value_bits': None, 'mask_reference': None, 'array_identity': None}
        trace.row['slot_references'].append(ref)
        trace.complete(prefix + 'blackboard_check', True, {'exists': bb['exists'], 'identity': bb['identity']})
        found = False
        if bb['exists'] is None:
            trace.unknown(prefix + 'blackboard_check', 'captured_blackboard_existence_unknown')
            return
        if bb['exists'] is True:
            if not trace.complete(prefix + 'key_format', slot['key_format_normally'],
                                  {'slot': index, 'key_identity': slot['key_identity'], 'key_text': None}):
                return
            if not trace.read(prefix + 'lookup', slot['lookup']):
                return
            found = slot['lookup']['found']
            if found is None:
                trace.unknown(prefix + 'lookup', 'lookup_found_unknown')
                return
        else:
            trace.skip((prefix + 'key_format', prefix + 'lookup'))
        if not trace.read(prefix + 'mask_read', slot['mask_read']):
            return
        mask = slot['mask_read']['value']
        if found is True:
            bits = slot['lookup']['bits']
            ref.update(value_source='blackboard', value_bits=bits)
            bit_ref = _mask_bit(mask, index)
            trace.complete(prefix + 'mask_set', True, bit_ref)
            ref['mask_reference'] = bit_ref
            write = {'field': 'spType', 'value': bit_ref['result_int32_reference'], 'known_set_bit': 1 << index}
            if not trace.complete(prefix + 'mask_store', slot['mask_store_normally'], write):
                return
            trace.row['stored_prefixes'].append(write)
            trace.skip((prefix + 'increment_copy', prefix + 'increment_decode'))
        else:
            trace.skip((prefix + 'mask_set', prefix + 'mask_store'))
            if mask is None:
                trace.unknown(prefix + 'mask_read', 'fallback_mask_branch_unknown')
                return
            if mask & (1 << index):
                if not trace.complete(prefix + 'increment_copy', slot['increment_copy_normally'], {'byte_count': 24}):
                    return
                if not trace.read(prefix + 'increment_decode', slot['increment_decode']):
                    return
                bits = slot['increment_decode']['bits']
                ref.update(value_source='protected_increment', value_bits=bits)
            else:
                bits = 0x3f800000
                ref.update(value_source='default_one', value_bits=bits)
                trace.skip((prefix + 'increment_copy', prefix + 'increment_decode'))
        if not trace.pointer(prefix + 'array_read', slot['array_read'], deferred=True):
            return
        ref['array_identity'] = slot['array_read']['identity']
        trace.complete(prefix + 'array_check', True, {'exists': slot['array_read']['exists']})
        if not trace.check_pointer(prefix + 'array_check', slot['array_read']['exists']):
            return
        if not trace.read(prefix + 'length_read', slot['array_length_read']):
            return
        if not trace.bounds(prefix + 'bounds_check', index, slot['array_length_read']['value']):
            return
        write = {'field': 'm_incrementsForAllSpTypes', 'identity': slot['array_read']['identity'],
                 'index': index, 'bits': bits}
        if not trace.complete(prefix + 'array_store', slot['array_store_normally'], write):
            return
        trace.row['stored_prefixes'].append(write)
    trace.row.update(normal=True, status='four_slot_write_prefix_complete_not_actual_array_proof')


def _skill_data_init(trace):
    a = trace.action
    if not trace.read('inited_read', a['inited_read']):
        return
    inited = a['inited_read']['value']
    if inited is True:
        trace.early_return('inited_read', 'skill_already_inited_normal_return')
        return
    if inited is None:
        trace.unknown('inited_read')
        return
    if not trace.read('duration_first_read', a['duration_first_read']):
        return
    flag = {'field': 'm_inited', 'value': True}
    if not trace.complete('flag_store', a['flag_store_normally'], flag):
        return
    trace.row['stored_prefixes'].append(flag)
    ge = _single_ge_zero(a['duration_first_read']['bits'])
    if not trace.complete('duration_ge', a['ge_normally'], ge):
        return
    trace.row['duration_ge_reference'] = ge
    branch = ge['ge_boolean_reference']
    if branch is None:
        trace.unknown('duration_ge', ge['status'])
        return
    if branch is True:
        if not trace.pointer('first_blackboard_read', a['first_blackboard_read']):
            return
        if not trace.read('duration_second_read', a['duration_second_read']):
            return
        arguments = {'blackboard_identity': a['first_blackboard_read']['identity'],
                     'duration_bits': a['duration_second_read']['bits'], 'key_identity': None}
        trace.row['assign_arguments'] = arguments
        if not trace.complete('duration_assign', a['assign_normally'], arguments):
            return
    else:
        trace.skip(('first_blackboard_read', 'duration_second_read', 'duration_assign'))
    if not trace.pointer('sp_data_read', a['sp_data_read']):
        return
    if not trace.pointer('second_blackboard_read', a['second_blackboard_read'], deferred=True):
        return
    arguments = {'sp_data_identity': a['sp_data_read']['identity'],
                 'blackboard_identity': a['second_blackboard_read']['identity'],
                 'blackboard_exists': a['second_blackboard_read']['exists']}
    trace.row['sp_init_arguments'] = arguments
    if trace.complete('sp_init', a['sp_init_normally'], arguments):
        trace.row.update(normal=True, status='skill_initialization_call_prefix_complete')


def _event_gain(trace):
    a = trace.action
    damage = a['kind'] == 'damage_gain'
    index, mask = (2, 4) if damage else (1, 2)
    if not trace.read('sp_type_read', a['sp_type_read']):
        return
    sp_type = a['sp_type_read']['value']
    if sp_type is None:
        trace.unknown('sp_type_read')
        return
    if not sp_type & mask:
        trace.early_return('sp_type_read', 'event_sp_type_bit_disabled_normal_return')
        return
    if damage:
        if not trace.read('cancelled_read', a['cancelled_read']):
            return
        cancelled = a['cancelled_read']['value']
        if cancelled is None:
            trace.unknown('cancelled_read')
            return
        if cancelled:
            trace.early_return('cancelled_read', 'cancelled_modifier_normal_return')
            return
        if not trace.read('modifier_flag_read', a['modifier_flag_read']):
            return
        flag = a['modifier_flag_read']['value']
        if flag is None:
            trace.unknown('modifier_flag_read')
            return
        if flag != 0:
            trace.early_return('modifier_flag_read', 'ignoreForSp_modifier_normal_return')
            return
    if not trace.pointer('array_read', a['array_read'], deferred=True):
        return
    if not trace.complete('index', a['index_normally'], {'argument_int32': index, 'index_reference': index,
                                                       'helper_address': '0x1844dc660', 'metadata_identity': None}):
        return
    trace.complete('array_check', True, {'exists': a['array_read']['exists']})
    if not trace.check_pointer('array_check', a['array_read']['exists']):
        return
    if not trace.read('length_read', a['array_length_read']):
        return
    if not trace.bounds('bounds_check', index, a['array_length_read']['value']):
        return
    if not trace.read('amount_read', a['amount_read']):
        return
    amount = _single_increment(a['amount_read']['bits'])
    if not trace.complete('single_to_fp', a['single_to_fp_normally'], amount):
        return
    trace.row['increment_reference'] = amount
    arguments = {'amount_raw': amount['raw_reference'], 'force': False}
    trace.row['recover_arguments'] = arguments
    if trace.complete('recover_request', a['recover_normally'], arguments):
        trace.row.update(normal=True, status='event_increment_request_prefix_complete_not_actual_sp_proof')


def skill_sp_increment_reference(payload):
    _validate(payload)
    source = source_data()
    rows = []
    for action in payload['actions']:
        trace = _Trace(action)
        receiver = payload['receiver_exists']
        if not source['valid'] or receiver is not True or action['ordinary_native_path'] is not True:
            trace.row.update(called=False if receiver is False else None,
                             normal=False if receiver is False else None,
                             status='receiver_missing' if receiver is False else 'source_or_ordinary_path_unqualified')
            if receiver is False:
                trace.skip(trace.names)
        else:
            trace.row['called'] = True
            if action['kind'] == 'sp_data_init':
                _sp_data_init(trace)
            elif action['kind'] == 'skill_data_init':
                _skill_data_init(trace)
            else:
                _event_gain(trace)
        rows.append(trace.row)
    return {'kind': 'skill_sp_increment_reference', 'source': source, 'payload': deepcopy(payload),
            'rows': rows, **{name: None for name in UNKNOWNS}}


def public_example():
    def read(label, value, kind='int', normal=True):
        return {'id': label, 'normal': normal, 'bits' if kind == 'single' else 'value': value}

    def pointer(label, identity, exists=True, normal=True):
        return {'id': label, 'normal': normal, 'exists': exists, 'identity': identity}

    def sp_init(label, bb_exists=False):
        a = {'id': label, 'kind': 'sp_data_init', 'ordinary_native_path': True,
             'captured_blackboard': pointer(label + '.bb', 'capturedBB' if bb_exists else None, bb_exists),
             'inited_read': read(label + '.inited', False), 'array_allocation': pointer(label + '.new', 'allocated4'),
             'array_install_normally': True, 'write_barrier_normally': True, 'slots': []}
        for i in range(4):
            s = label + '.s' + str(i)
            a['slots'].append({'slot': i, 'key_format_normally': True, 'key_identity': 'opaqueKey' + str(i),
                              'lookup': {'id': s + '.lookup', 'normal': True, 'found': False, 'bits': None},
                              'mask_read': read(s + '.mask', 0), 'mask_store_normally': True,
                              'increment_copy_normally': True, 'increment_decode': read(s + '.decode', 0x40000000, 'single'),
                              'array_read': pointer(s + '.array', 'allocated4'), 'array_length_read': read(s + '.length', 4),
                              'array_store_normally': True})
        return a

    def skill_init(label, first_bits):
        return {'id': label, 'kind': 'skill_data_init', 'ordinary_native_path': True,
                'inited_read': read(label + '.inited', False), 'duration_first_read': read(label + '.d1', first_bits, 'single'),
                'flag_store_normally': True, 'ge_normally': True,
                'first_blackboard_read': pointer(label + '.bb1', 'firstBB'),
                'duration_second_read': read(label + '.d2', 0xbf800000, 'single'), 'assign_normally': True,
                'sp_data_read': pointer(label + '.spdata', 'spData'),
                'second_blackboard_read': pointer(label + '.bb2', 'secondBB'), 'sp_init_normally': True}

    def event(label, damage=False, bits=0x3f800000):
        a = {'id': label, 'kind': 'damage_gain' if damage else 'attack_gain', 'ordinary_native_path': True,
             'sp_type_read': read(label + '.type', 4 if damage else 2), 'array_read': pointer(label + '.array', 'controllerArray'),
             'index_normally': True, 'array_length_read': read(label + '.length', 4),
             'amount_read': read(label + '.amount', bits, 'single'), 'single_to_fp_normally': True, 'recover_normally': True}
        if damage:
            a.update(cancelled_read=read(label + '.cancelled', False), modifier_flag_read=read(label + '.ignore', 0))
        return a

    default = sp_init('public.default_one_without_enabled_bits')
    mixed = sp_init('public.independent_lookup_mask_array', True)
    mixed['slots'][0]['lookup'].update(found=True, bits=0x3f800000)
    mixed['slots'][1]['mask_read']['value'] = 2
    mixed['slots'][1]['increment_decode']['bits'] = 0x40200000
    mixed['slots'][2]['lookup'].update(found=True, bits=None)
    mixed['slots'][2]['mask_read']['value'] = None
    mixed['slots'][2]['array_read']['identity'] = 'independentArrayB'
    mixed['slots'][3]['array_read']['identity'] = 'independentArrayC'
    short = sp_init('public.mask_written_before_short_array', True)
    short['slots'][0]['lookup'].update(found=True, bits=0x40400000)
    short['slots'][0]['array_length_read']['value'] = 0
    epsilon = skill_init('public.negative_single_epsilon_inclusive', 0xb727c5ac)
    uncertain = skill_init('public.flag_before_unknown_ge', 1)
    attack = event('public.attack_single_one')
    damage = event('public.damage_negative_request', True, 0xbf800000)
    cancelled = event('public.cancelled_damage_skips_request', True)
    cancelled['cancelled_read']['value'] = True
    overflow = event('public.convert_unknown_opaque_request', bits=0x4f000000)
    disabled = event('public.default_one_does_not_enable_attack')
    disabled['sp_type_read']['value'] = 0
    return {'receiver_exists': True, 'actions': [default, mixed, short, epsilon, uncertain, attack,
                                                damage, cancelled, overflow, disabled]}
