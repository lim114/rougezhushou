"""SHA-bound native skill threshold/debit references; no runtime or payment claims.

The payload declares independent read points and their normality. This module
does not inspect a game process, execute game code, apply a modifier, or infer
runtime hotfix/virtual identities from a base-method name.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

Q = 1 << 32
EPSILON = 42950
MIN32, MAX32 = -(1 << 31), (1 << 31) - 1
MIN64, MAX64 = -(1 << 63), (1 << 63) - 1
PROOF_SHA256 = 'f7c7908155ff9cb376fb7295d8bb71a84838e06d081af58ba4a2d51553ebdbbc'
# Filled by the cache packaging script from the exact source-only manifest.
MANIFEST_SHA256 = '2f77a3765ba9d5f89d4ab91b3abeaf225c0f7384d4c917c2b5771e3554b4d6f7'
SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / 'research/p2-skill-sp-cost-277'
STAGES = {
    'assign_min': ('blackboard_result', 'parameter_store'),
    'modify_min': ('parameter_store',),
    'modify_free': ('parameter_store',),
    'admission': ('owner_read', 'unity_null_read', 'first_min_read', 'free_read',
                  'sp_owner_read', 'sp_read', 'decoded_cost_read', 'second_min_read', 'ge_comparison'),
    'reduce': ('free_read', 'skip_virtual_read', 'newsp_owner_read', 'newsp_call',
               'apply_owner_read', 'modifier_copy', 'apply_call'),
}
COMMON = {'id', 'kind', 'ordinary_native_path'}
EXTRA = {
    'assign_min': {'blackboard_read', 'store_returns_normally'},
    'modify_min': {'value', 'store_returns_normally'},
    'modify_free': {'value', 'store_returns_normally'},
    'admission': {'owner_read', 'unity_null_read', 'first_min_read', 'free_read',
                  'sp_owner_read', 'sp_read', 'decoded_cost_read', 'second_min_read'},
    'reduce': {'delta', 'free_read', 'skip_virtual_read', 'newsp_owner_read',
               'newsp_ordinary_native_path', 'newsp_returns_normally', 'returned_modifier_identity',
               'modifier_copy_returns_normally', 'apply_owner_read', 'apply_returns_normally', 'apply_return'},
}
UNKNOWNS = ('actual_owner_sp_after', 'actual_cost_paid', 'actual_cast_success', 'complete_cycle')


def source_data():
    """Load only the pinned public proof/manifest; callers cannot override source validity."""
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
        if (manifest['proof_sha256'] != PROOF_SHA256
                or proof['dll_sha256'] != manifest['dll_sha256']
                or proof['metadata_sha256'] != manifest['metadata_sha256']
                or proof['method_count'] != 49 or proof['byte_span_count'] != 6859
                or proof['game_dll_executed'] is not False or proof['process_memory_read'] is not False
                or proof['all_spans_rechecked_against_fresh_primary_files'] is not True):
            return {**result, 'status': 'source_contract_mismatch'}
        apply = next(row for row in proof['method_metadata'] if row['index'] == 66665)
        if apply['return_type'] != 'System.Boolean' or apply['parameters'] != [
            {'name': 'modifier', 'type': 'Torappu.Battle.Modifier'},
            {'name': 'force', 'type': 'System.Boolean'},
        ]:
            return {**result, 'status': 'apply_signature_mismatch'}
        enum = {(row['type'], row['field']): row['value']['value'] for row in proof['enum_defaults']}
        if any(enum.get(pair) != value for pair, value in {
            ('Torappu.Battle.Modifier+TargetType', 'SP'): 1,
            ('Torappu.Battle.Modifier+DeltaType', 'ADD'): 1,
            ('Torappu.Battle.Modifier+DeltaType', 'MINUS'): 2,
            ('Torappu.PlayerSide', 'DEFAULT'): 0,
        }.items()):
            return {**result, 'status': 'enum_mismatch'}
        return {'valid': True, 'status': 'pinned_file_source_reference', 'proof_sha256': PROOF_SHA256,
                'method_count': 49, 'byte_span_count': 6859}
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        return result


def _keys(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(label + ' must contain exact keys ' + ','.join(sorted(expected)))


def _tri(value, label):
    if value is not None and type(value) is not bool:
        raise ValueError(label + ' must be true, false, or null')


def _integer(value, bits, label, nullable=True):
    if value is None and nullable:
        return
    if type(value) is not int or not -(1 << (bits - 1)) <= value < (1 << (bits - 1)):
        raise ValueError(label + ' must be signed' + str(bits) + ('/null' if nullable else ''))


def _label(value, name, nullable=False):
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value.strip() or len(value) > 120:
        raise ValueError(name + ' must be a public nonempty label up to120 characters')


def _validate_read(value, kind, ids):
    keys = {'id', 'normal'} | ({'exists', 'identity'} if kind == 'owner' else {'raw'} if kind == 'fp' else {'value'})
    _keys(value, keys, kind + ' read')
    _label(value['id'], 'read.id')
    if value['id'] in ids:
        raise ValueError('Action/read IDs must be globally unique')
    ids.add(value['id'])
    _tri(value['normal'], 'read.normal')
    if kind == 'owner':
        _tri(value['exists'], 'owner.exists')
        _label(value['identity'], 'owner.identity', True)
    elif kind == 'fp':
        _integer(value['raw'], 64, 'read.raw')
    elif kind == 'int':
        _integer(value['value'], 32, 'read.value')
    else:
        _tri(value['value'], 'read.value')


def _validate(payload):
    _keys(payload, {'skill_exists', 'state', 'actions'}, 'payload')
    _tri(payload['skill_exists'], 'skill_exists')
    _keys(payload['state'], {'cost_min_sp', 'cast_with_no_sp'}, 'state')
    _integer(payload['state']['cost_min_sp'], 32, 'state.cost_min_sp')
    _tri(payload['state']['cast_with_no_sp'], 'state.cast_with_no_sp')
    actions = payload['actions']
    if not isinstance(actions, list) or not 1 <= len(actions) <= 50:
        raise ValueError('actions must contain1–50 entries')
    ids = set()
    for action in actions:
        if not isinstance(action, dict) or action.get('kind') not in EXTRA:
            raise ValueError('unknown action kind')
        kind = action['kind']
        _keys(action, COMMON | EXTRA[kind], 'action')
        _label(action['id'], 'action.id')
        if action['id'] in ids:
            raise ValueError('Action/read IDs must be globally unique')
        ids.add(action['id'])
    for action in actions:
        kind = action['kind']
        _tri(action['ordinary_native_path'], 'ordinary_native_path')
        if kind in ('assign_min', 'modify_min', 'modify_free'):
            _tri(action['store_returns_normally'], 'store_returns_normally')
            if kind == 'assign_min':
                _validate_read(action['blackboard_read'], 'int', ids)
            elif kind == 'modify_min':
                _integer(action['value'], 32, 'value')
            else:
                _tri(action['value'], 'value')
        elif kind == 'admission':
            for key in ('owner_read', 'sp_owner_read'):
                _validate_read(action[key], 'owner', ids)
            for key in ('unity_null_read', 'free_read'):
                _validate_read(action[key], 'bool', ids)
            for key in ('first_min_read', 'decoded_cost_read', 'second_min_read'):
                _validate_read(action[key], 'int', ids)
            _validate_read(action['sp_read'], 'fp', ids)
        else:
            _integer(action['delta'], 32, 'delta')
            for key in ('free_read', 'skip_virtual_read'):
                _validate_read(action[key], 'bool', ids)
            for key in ('newsp_owner_read', 'apply_owner_read'):
                _validate_read(action[key], 'owner', ids)
            for key in ('newsp_ordinary_native_path', 'newsp_returns_normally',
                        'modifier_copy_returns_normally', 'apply_returns_normally', 'apply_return'):
                _tri(action[key], key)
            _label(action['returned_modifier_identity'], 'returned_modifier_identity', True)


def _wrap(value, bits):
    return ((value + (1 << (bits - 1))) % (1 << bits)) - (1 << (bits - 1))


def _ge(sp_raw, threshold):
    raw = threshold * Q
    right = _wrap(raw - EPSILON, 64)
    return {'threshold_int32': threshold, 'threshold_raw': raw, 'epsilon_raw': EPSILON,
            'comparison_rhs_raw': right, 'sp_raw': sp_raw, 'result': sp_raw > right}


def ge_reference(sp_raw, threshold):
    """Isolated strict EPS comparison. Never qualifies a real getter/cast."""
    _integer(sp_raw, 64, 'sp_raw', False)
    _integer(threshold, 32, 'threshold', False)
    return _ge(sp_raw, threshold) if source_data()['valid'] else None


def _debit(delta):
    negated = _wrap(-delta, 32)
    raw = negated * Q
    return {'delta_int32': delta, 'negated_int32': negated, 'input_raw': raw,
            'magnitude_raw': MAX64 - 1 if raw == MIN64 else abs(raw),
            'delta_type_value': 1 if raw >= 0 else 2,
            'delta_type_name': 'ADD' if raw >= 0 else 'MINUS',
            'target_type_value': 1, 'target_type_name': 'SP',
            'player_side_value': 0, 'player_side_name': 'DEFAULT'}


def debit_argument_reference(delta):
    """Isolated low32 NEG and NewSp pre-constructor reference, not a paid debit."""
    _integer(delta, 32, 'delta', False)
    return _debit(delta) if source_data()['valid'] else None


def _row(action, state):
    return {'id': action['id'], 'kind': action['kind'], 'called': None, 'normal': None,
            'status': 'unknown',
            'stages': [{'name': name, 'called': None, 'normal': None, 'reference': None}
                       for name in STAGES[action['kind']]],
            'known_prefix_state': deepcopy(state), 'state_after': deepcopy(state),
            'result_reference': None, 'arithmetic_reference': None,
            'modifier_constructor_arguments': None, 'opaque_modifier_identity': None,
            'apply_arguments': None, **{key: None for key in UNKNOWNS}}


def _stage(row, name):
    return next(stage for stage in row['stages'] if stage['name'] == name)


def _skip(row, names):
    for name in names:
        _stage(row, name).update(called=False, normal=None, reference=None)


def _stop(row, name, normal, status):
    row.update(normal=normal, status=status)
    if normal is False:
        names = STAGES[row['kind']]
        _skip(row, names[names.index(name) + 1:])


def _read(row, name, read):
    stage = _stage(row, name)
    normal = read['normal']
    stage.update(called=True, normal=normal,
                 reference=deepcopy(read) if normal is True else None)
    if normal is not True:
        _stop(row, name, normal, 'read_failed' if normal is False else 'read_normality_unknown')
        return False
    return True


def _completion(row, name, normal, reference=None):
    _stage(row, name).update(called=True, normal=normal,
                            reference=deepcopy(reference) if normal is True else None)
    if normal is not True:
        _stop(row, name, normal, 'call_failed' if normal is False else 'call_normality_unknown')
        return False
    return True


def _value_unknown(row):
    row.update(normal=None, status='independent_read_value_unknown')


def _store(row, action, state):
    kind = action['kind']
    key = 'cast_with_no_sp' if kind == 'modify_free' else 'cost_min_sp'
    if kind == 'assign_min':
        if not _read(row, 'blackboard_result', action['blackboard_read']):
            row['state_after'] = None
            state[key] = None
            return
        value = action['blackboard_read']['value']
    else:
        value = action['value']
    if not _completion(row, 'parameter_store', action['store_returns_normally'],
                       {'field': 'm_castWithNoSp' if key == 'cast_with_no_sp' else 'm_costMinSp',
                        'value': value}):
        row['state_after'] = None
        state[key] = None
        return
    state[key] = value
    row.update(normal=True, status='parameter_prefix_complete', state_after=deepcopy(state))


def _admission(row, action):
    if not _read(row, 'owner_read', action['owner_read']):
        return
    # The first owner is fed to Unity-null comparison; a raw null is permitted.
    if not _read(row, 'unity_null_read', action['unity_null_read']):
        return
    unity_null = action['unity_null_read']['value']
    if unity_null is None:
        _value_unknown(row)
        return
    if unity_null is True:
        _skip(row, STAGES['admission'][2:])
        row.update(normal=True, status='unity_owner_invalid', result_reference=False)
        return
    if not _read(row, 'first_min_read', action['first_min_read']):
        return
    first_min = action['first_min_read']['value']
    if first_min is None:
        _value_unknown(row)
        return
    if first_min < 0:
        _skip(row, ('second_min_read',))
        if not _read(row, 'free_read', action['free_read']):
            return
        free = action['free_read']['value']
        if free is None:
            _value_unknown(row)
            return
        if free is True:
            _skip(row, ('sp_owner_read', 'sp_read', 'decoded_cost_read', 'ge_comparison'))
            row.update(normal=True, status='free_admission', result_reference=True)
            return
        threshold_read = 'decoded_cost_read'
    else:
        _skip(row, ('free_read', 'decoded_cost_read'))
        threshold_read = 'second_min_read'
    if not _read(row, 'sp_owner_read', action['sp_owner_read']):
        return
    exists = action['sp_owner_read']['exists']
    if exists is not True:
        _stop(row, 'sp_owner_read', False if exists is False else None,
              'sp_owner_missing' if exists is False else 'sp_owner_existence_unknown')
        return
    if not _read(row, 'sp_read', action['sp_read']):
        return
    # The threshold getter/read follows the SP getter, even if its raw result is unknown.
    if not _read(row, threshold_read, action[threshold_read]):
        return
    sp, threshold = action['sp_read']['raw'], action[threshold_read]['value']
    if sp is None or threshold is None:
        _value_unknown(row)
        return
    arithmetic = _ge(sp, threshold)
    _completion(row, 'ge_comparison', True, arithmetic)
    row.update(normal=True, status='admission_reference_complete',
               arithmetic_reference=arithmetic, result_reference=arithmetic['result'])


def _reduce(row, action):
    delta = action['delta']
    if delta is None:
        _value_unknown(row)
        return
    if delta == 0:
        _skip(row, STAGES['reduce'])
        row.update(normal=True, status='zero_delta_short_circuit', result_reference=True)
        return
    for name in ('free_read', 'skip_virtual_read'):
        if not _read(row, name, action[name]):
            return
        value = action[name]['value']
        if value is None:
            _value_unknown(row)
            return
        if value is True:
            names = STAGES['reduce']
            _skip(row, names[names.index(name) + 1:])
            row.update(normal=True, status='free_debit_skip' if name == 'free_read' else 'virtual_debit_skip',
                       result_reference=True)
            return
    arithmetic = _debit(delta)
    row['arithmetic_reference'] = {key: arithmetic[key] for key in ('delta_int32', 'negated_int32', 'input_raw')}
    if not _read(row, 'newsp_owner_read', action['newsp_owner_read']):
        return
    owner = action['newsp_owner_read']
    # NewSp only receives owner as source/target. No owner dereference or equality with later owner is assumed.
    arguments = {'value_raw': arithmetic['input_raw'], 'source_identity': owner['identity'],
                 'target_identity': owner['identity'], 'source_exists': owner['exists'], 'target_exists': owner['exists']}
    if action['newsp_ordinary_native_path'] is True and action['newsp_returns_normally'] is True:
        row['modifier_constructor_arguments'] = {
            **{key: arithmetic[key] for key in ('magnitude_raw', 'delta_type_value', 'delta_type_name',
                                               'target_type_value', 'target_type_name', 'player_side_value', 'player_side_name')},
            'source_identity': owner['identity'], 'target_identity': owner['identity'],
            'source_exists': owner['exists'], 'target_exists': owner['exists'],
            'returned_payload_fields': None, 'cancel_reason_mask': None,
        }
    if not _completion(row, 'newsp_call', action['newsp_returns_normally'], arguments):
        return
    row['opaque_modifier_identity'] = action['returned_modifier_identity']
    # Exact source order: second owner read, then136-byte copy, then owner null check.
    if not _read(row, 'apply_owner_read', action['apply_owner_read']):
        return
    if not _completion(row, 'modifier_copy', action['modifier_copy_returns_normally'],
                       {'byte_count': 136, 'modifier_identity': action['returned_modifier_identity'], 'fields': None}):
        return
    exists = action['apply_owner_read']['exists']
    if exists is not True:
        _stage(row, 'apply_call').update(called=False if exists is False else None)
        row.update(normal=False if exists is False else None,
                   status='apply_owner_missing' if exists is False else 'apply_owner_existence_unknown')
        return
    row['apply_arguments'] = {'owner_identity': action['apply_owner_read']['identity'],
                              'modifier_identity': action['returned_modifier_identity'], 'force': False}
    if not _completion(row, 'apply_call', action['apply_returns_normally'], row['apply_arguments']):
        return
    row.update(normal=True, status='debit_call_prefix_complete', result_reference=action['apply_return'])


def skill_sp_cost_reference(payload):
    """Calculate declared native branch prefixes, never actual SP/payment/cast state."""
    _validate(payload)
    payload = deepcopy(payload)
    source = source_data()
    state = deepcopy(payload['state'])
    rows = []
    for action in payload['actions']:
        row = _row(action, state)
        rows.append(row)
        if not source['valid']:
            row.update(status='source_unavailable', known_prefix_state=None, state_after=None)
            continue
        if payload['skill_exists'] is not True:
            row.update(called=False if payload['skill_exists'] is False else None,
                       normal=False if payload['skill_exists'] is False else None,
                       status='skill_missing' if payload['skill_exists'] is False else 'skill_existence_unknown',
                       state_after=None)
            if payload['skill_exists'] is False:
                _skip(row, STAGES[action['kind']])
            continue
        row['called'] = True
        if action['ordinary_native_path'] is not True:
            row.update(status='native_branch_unqualified', state_after=None)
            if action['kind'] in ('assign_min', 'modify_min'):
                state['cost_min_sp'] = None
            elif action['kind'] == 'modify_free':
                state['cast_with_no_sp'] = None
            continue
        if action['kind'] in ('assign_min', 'modify_min', 'modify_free'):
            _store(row, action, state)
        elif action['kind'] == 'admission':
            _admission(row, action)
        else:
            _reduce(row, action)
    return {'kind': 'skill_sp_cost_reference', 'source': source, 'payload': payload, 'rows': rows,
            'final_declared_parameter_state': state if source['valid'] else None,
            **{key: None for key in UNKNOWNS}}


def public_example():
    """Public independent read labels, changed second reads and debit/admission separation."""
    def owner(label, identity):
        return {'id': label, 'normal': True, 'exists': True, 'identity': identity}

    def integer(label, value):
        return {'id': label, 'normal': True, 'value': value}

    def boolean(label, value):
        return {'id': label, 'normal': True, 'value': value}

    def admission(label, first, second, free, sp, cost):
        return {'id': label, 'kind': 'admission', 'ordinary_native_path': True,
                'owner_read': owner(label + '.initial_owner', 'declared.owner.A'),
                'unity_null_read': boolean(label + '.unity_null', False),
                'first_min_read': integer(label + '.first_min', first),
                'free_read': boolean(label + '.free', free),
                'sp_owner_read': owner(label + '.sp_owner', 'declared.owner.B'),
                'sp_read': {'id': label + '.sp', 'normal': True, 'raw': sp},
                'decoded_cost_read': integer(label + '.data_cost', cost),
                'second_min_read': integer(label + '.second_min', second)}

    def reduce(label, delta, free, virtual, returned):
        return {'id': label, 'kind': 'reduce', 'ordinary_native_path': True, 'delta': delta,
                'free_read': boolean(label + '.free', free),
                'skip_virtual_read': boolean(label + '.virtual_skip', virtual),
                'newsp_owner_read': owner(label + '.newsp_owner', 'declared.owner.C'),
                'newsp_ordinary_native_path': True, 'newsp_returns_normally': True,
                'returned_modifier_identity': 'declared.modifier.' + label, 'modifier_copy_returns_normally': True,
                'apply_owner_read': owner(label + '.apply_owner', 'declared.owner.D'),
                'apply_returns_normally': True, 'apply_return': returned}

    return {'skill_exists': True, 'state': {'cost_min_sp': -1, 'cast_with_no_sp': False}, 'actions': [
        {'id': 'public.assign', 'kind': 'assign_min', 'ordinary_native_path': True,
         'blackboard_read': integer('public.assign.bb', -1), 'store_returns_normally': True},
        {'id': 'public.set5', 'kind': 'modify_min', 'ordinary_native_path': True, 'value': 5, 'store_returns_normally': True},
        admission('public.override', 5, 5, False, 21474836480, 20),
        reduce('public.debit20', 20, False, False, False),
        admission('public.changed_second', 5, 7, False, 21474836480, 20),
        {'id': 'public.set_negative', 'kind': 'modify_min', 'ordinary_native_path': True, 'value': -1, 'store_returns_normally': True},
        admission('public.free_admission', -1, 7, True, 0, 20),
        reduce('public.independent_debit', 20, False, False, True),
        reduce('public.free_debit', 20, True, False, True),
        reduce('public.min32', -2147483648, False, False, False),
    ]}
