"""File-source-bound SP initialization and controller lifecycle prefixes.

Caller declarations qualify a native reference, never a live pointer/read,
protected payload decoding, final SP, a whole Entity.Init, or a skill cycle.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import mmap
import struct

from .mechanist_explosion_math import ONE, MIN_RAW, MAX_RAW, add, subtract
from .sp_recovery_clock import safe_fp_divide, _validate as _validate_clock

SOURCE = 'rouge/data/sp-initialization-source.json'
SOURCE_SHA256 = 'b3afe25032ddcf6669a78e869b9105a34990d91e0dd8d794930e410fa2cdf3a1'
MIN32 = -(1 << 31)
MAX32 = (1 << 31) - 1
STATE_FIELDS = {'owner_id', 'sp_type', 'cost_payload_id',
                'increments_payload_id', 'max_sp', 'timer'}


@lru_cache(maxsize=1)
def _source_data():
    root = Path(__file__).resolve().parents[1]
    try:
        raw = (root / SOURCE).read_bytes()
        if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
            return None
        data = json.loads(raw)
        if (data['file_only'] is not True or data['game_dll_executed'] is not False
                or data['process_memory_read'] is not False
                or data['method_count'] != 47
                or data['unique_instruction_count'] != 4866
                or data['byte_span_count'] != 6351):
            return None
        for name, digest in data['source_artifacts_sha256'].items():
            if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
                return None
        proof = json.loads((root / data['primary_proof']).read_bytes())
        if (proof['method_count'] != 47 or proof['unique_instruction_count'] != 4866
                or proof['byte_span_count'] != 6351 or len(proof['methods']) != 47
                or len(proof['byte_spans']) != 6351
                or proof['all_spans_rechecked_against_fresh_primary_files'] is not True
                or proof['dll_sha256'] != data['dll_sha256']
                or proof['metadata_sha256'] != data['metadata_sha256']):
            return None
        # The proof's extraction inputs are provenance. The actual public
        # runtime artifacts are exactly the separately checked manifest table.
        return {**proof, **data}
    except (OSError, ValueError, KeyError, TypeError):
        return None


def source_data():
    return deepcopy(_source_data())


def _tri(v):
    if v is not None and type(v) is not bool:
        raise ValueError('资格只接受true、false或null。')


def _integer(v, lower, upper):
    if v is not None and (type(v) is not int or not lower <= v <= upper):
        raise ValueError('需要对应范围的整数或null，不能填布尔值或小数。')


def _id(v, *, nullable=False):
    if nullable and v is None:
        return
    if (type(v) is not str or not 1 <= len(v) <= 60
            or any(ord(c) < 32 or 0xd800 <= ord(c) <= 0xdfff for c in v)):
        raise ValueError('身份需要1–60字符的公开标签，不能含控制字符。')


def _keys(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError('请使用完整且对应的声明字段。')


def _identity(value, seen):
    _id(value)
    if value in seen:
        raise ValueError('各操作及独立读点必须使用不同身份。')
    seen.add(value)


def _read(v, kind, seen):
    keys = {'id', 'normal', 'value'} if kind == 'int' else (
        {'id', 'normal', 'payload_id'} if kind == 'opaque' else
        {'id', 'exists', 'normal', 'value'} if kind == 'can' else
        {'id', 'exists', 'normal', 'raw'})
    _keys(v, keys)
    _identity(v['id'], seen)
    _tri(v['normal'])
    if 'exists' in v:
        _tri(v['exists'])
    if kind == 'int':
        _integer(v['value'], MIN32, MAX32)
    elif kind == 'opaque':
        _id(v['payload_id'], nullable=True)
    elif kind == 'can':
        _tri(v['value'])
    else:
        _integer(v['raw'], MIN_RAW, MAX_RAW)


def _capacity(v, seen):
    _keys(v, {'id', 'ordinary_native_path', 'sp_data_exists', 'cost_decode',
              'charges_decode', 'max_encode_normally', 'max_decode_normally',
              'getter_returns_normally'})
    _identity(v['id'], seen)
    for key in ('ordinary_native_path', 'sp_data_exists', 'max_encode_normally',
                'max_decode_normally', 'getter_returns_normally'):
        _tri(v[key])
    _read(v['cost_decode'], 'int', seen)
    _read(v['charges_decode'], 'int', seen)


def _data(v, seen):
    _keys(v, {'exists', 'sp_type_read', 'sp_type_store_normally', 'cost_read',
              'cost_copy_normally', 'increments_read',
              'increments_destination_exists', 'increments_length_read_normally',
              'increments_destination_length', 'increments_copy_normally'})
    for key in ('exists', 'sp_type_store_normally', 'cost_copy_normally',
                'increments_destination_exists', 'increments_length_read_normally',
                'increments_copy_normally'):
        _tri(v[key])
    _integer(v['increments_destination_length'], 0, MAX32)
    _read(v['sp_type_read'], 'int', seen)
    _read(v['cost_read'], 'opaque', seen)
    _read(v['increments_read'], 'opaque', seen)


def _action(a, seen):
    if type(a) is not dict:
        raise ValueError('操作需要对象。')
    common = {'id', 'kind', 'ordinary_native_path'}
    kind = a.get('kind')
    options = {
        'construct': {'increments_allocate_normally', 'increments_assign_normally',
                      'timer_allocate_normally', 'timer_constructor_normally',
                      'timer_assign_normally', 'base_constructor_normally',
                      'post_ctor_hotfix'},
        'reset': {'owner_id', 'owner_write_normally', 'data', 'can_recover_read',
                  'second_rate_read', 'timer_call_returns_normally'},
        'reset_timer': {'timer_call_returns_normally'},
        'update_data': {'only_update_sp_cost', 'data', 'can_recover_read',
                        'second_rate_read', 'timer_call_returns_normally'},
        'entity_init': {'first_max_read', 'init_sp_read', 'single_encoder_normally',
                        'sp_payload_copy_normally', 'second_max_read',
                        'max_sp_write_normally', 'controller_reset'},
        'entity_update': {'max_read', 'max_sp_write_normally', 'controller_update'},
    }
    if type(kind) is not str or kind not in options:
        raise ValueError('需要对应的构造/重置/更新/Entity初始化操作。')
    _keys(a, common | options[kind])
    _identity(a['id'], seen)
    _tri(a['ordinary_native_path'])
    for key in options[kind]:
        if key.endswith('_normally') or key == 'only_update_sp_cost':
            _tri(a[key])
    if kind == 'construct':
        _keys(a['post_ctor_hotfix'], {'present', 'returns_normally'})
        for v in a['post_ctor_hotfix'].values():
            _tri(v)
    elif kind in ('reset', 'update_data'):
        if kind == 'reset':
            _id(a['owner_id'], nullable=True)
        _data(a['data'], seen)
        _read(a['can_recover_read'], 'can', seen)
        _read(a['second_rate_read'], 'rate', seen)
    elif kind == 'entity_init':
        _capacity(a['first_max_read'], seen)
        _read(a['init_sp_read'], 'int', seen)
        _capacity(a['second_max_read'], seen)
        _action(a['controller_reset'], seen)
        if a['controller_reset']['kind'] != 'reset':
            raise ValueError('Entity初始化需要独立完整controller_reset声明。')
    elif kind == 'entity_update':
        _capacity(a['max_read'], seen)
        _action(a['controller_update'], seen)
        if a['controller_update']['kind'] != 'update_data':
            raise ValueError('Entity更新需要独立完整controller_update声明。')


def _validate(p):
    _keys(p, {'entity_exists', 'controller_exists', 'precise_timer_identity',
              'no_intervening_state_changes', 'state', 'actions'})
    for key in ('entity_exists', 'controller_exists', 'precise_timer_identity',
                'no_intervening_state_changes'):
        _tri(p[key])
    s = p['state']
    _keys(s, STATE_FIELDS)
    for key in ('owner_id', 'cost_payload_id', 'increments_payload_id'):
        _id(s[key], nullable=True)
    for key in ('sp_type', 'max_sp'):
        _integer(s[key], MIN32, MAX32)
    _keys(s['timer'], {'exists', 'period_raw', 'remaining_raw'})
    _tri(s['timer']['exists'])
    for key in ('period_raw', 'remaining_raw'):
        _integer(s['timer'][key], MIN_RAW, MAX_RAW)
    if type(p['actions']) is not list or not 1 <= len(p['actions']) <= 50:
        raise ValueError('操作需要1–50项。')
    seen = set()
    for action in p['actions']:
        _action(action, seen)


def max_sp_reference(cost, charges):
    """Qualified decoded Int32 literals: IMUL low32, not saturation."""
    _integer(cost, MIN32, MAX32)
    _integer(charges, MIN32, MAX32)
    valid = _source_data() is not None
    value = None
    if valid:
        if cost == 0 or charges == 0:
            value = 0
        elif cost is not None and charges is not None:
            value = ((cost * charges - MIN32) % (1 << 32)) + MIN32
    return {'cost': cost, 'charges': charges,
            'signed32_product_reference': value, 'source_valid': valid}


def initial_single_reference(first_max, init_sp):
    """Signed min and the exact Single/scaled-signed64 eligibility subdomain."""
    _integer(first_max, MIN32, MAX32)
    _integer(init_sp, MIN32, MAX32)
    valid = _source_data() is not None
    value = None
    if valid:
        if first_max is not None and init_sp is not None:
            value = min(first_max, init_sp)
        elif first_max == MIN32 or init_sp == MIN32:
            value = MIN32
    exact = None if value is None else struct.unpack('<f', struct.pack('<f', value))[0] == value
    eligible = None if exact is not True else MIN_RAW <= value * ONE <= MAX_RAW
    raw = value * ONE if eligible is True else None
    return {'signed_min_reference': value, 'single_exact_reference': exact,
            'scaled_signed64_eligible_reference': eligible,
            'encoder_constructor_argument_raw_reference': raw,
            'actual_initial_sp': None, 'source_valid': valid}


def _unknown_state(s, fields=STATE_FIELDS, *, pointer_unknown=False):
    after = deepcopy(s)
    for key in fields:
        if key == 'timer':
            after[key] = {'exists': None if pointer_unknown else after[key]['exists'],
                          'period_raw': None, 'remaining_raw': None}
        else:
            after[key] = None
    return after


def _affected(kind, action=None):
    if kind == 'construct':
        return {'increments_payload_id', 'timer'}
    if kind == 'reset_timer':
        return {'timer'}
    if kind == 'update_data' and action['only_update_sp_cost'] is True:
        return {'cost_payload_id'}
    fields = {'sp_type', 'cost_payload_id', 'increments_payload_id', 'timer'}
    if kind in ('reset', 'entity_init'):
        fields.add('owner_id')
    if kind in ('entity_init', 'entity_update'):
        fields.add('max_sp')
    return fields


class _Prefix:
    def __init__(self, state, action, context):
        self.state = deepcopy(state)
        self.action = action
        self.context = context
        self.row = {'id': action['id'], 'kind': action['kind'],
                    'called_reference': True, 'normal_return_reference': True,
                    'status': 'qualified_native_prefix', 'stages': [],
                    'known_prefix_state_reference': deepcopy(state),
                    'state_after_reference': deepcopy(state),
                    'initial_sp_prefix': None, 'capacity_reads': [],
                    'conditional_branches': []}
        self.active = True

    def stage(self, name, normal, argument=None, value=None, detail=None, *, dirty=()):
        self.row['stages'].append({'name': name, 'called_reference': True,
                                  'normal_return_reference': normal,
                                  'argument_reference': deepcopy(argument),
                                  'value_reference': deepcopy(value) if normal is True else None,
                                  'detail': detail})
        if normal is not True:
            self.active = False
            self.row['normal_return_reference'] = normal
            self.row['status'] = 'unqualified_' + name
            self.row['state_after_reference'] = _unknown_state(
                self.state, _affected(self.action['kind'], self.action) if normal is None else dirty)
        return self.active

    def write(self, name, key, value, normal, *, argument=None, detail=None):
        if self.stage(name, normal, value if argument is None else argument,
                      value, detail, dirty={key}):
            self.state[key] = deepcopy(value)
            self.boundary()
        return self.active

    def boundary(self):
        self.row['known_prefix_state_reference'] = deepcopy(self.state)
        self.row['state_after_reference'] = deepcopy(self.state)

    def finish(self):
        return self.row


def _read_stage(m, name, read, value_key):
    if 'exists' in read and not m.stage(name + '.access', read['exists'],
                                       detail={'read_id': read['id']}):
        return None
    if not m.stage(name, read['normal'], value=read[value_key],
                   detail={'read_id': read['id']}):
        return None
    return read[value_key]


def _capacity_read(m, role, read):
    r = {'role': role, 'read_id': read['id'], 'signed32_product_reference': None,
         'returned_max_sp_reference': None, 'normal_return_reference': None,
         'cost_decode_called_reference': False, 'charges_decode_called_reference': False,
         'max_encode_called_reference': False, 'max_decode_called_reference': False,
         'getter_return_called_reference': False, 'status': 'unqualified_capacity'}
    m.row['capacity_reads'].append(r)
    if read['ordinary_native_path'] is not True:
        m.stage(role + '.ordinary_path', None)
        return None
    if not m.stage(role + '.sp_data_access', read['sp_data_exists']):
        r['normal_return_reference'] = m.row['normal_return_reference']
        return None
    for key, flag in (('cost_decode', 'cost_decode_called_reference'),
                      ('charges_decode', 'charges_decode_called_reference')):
        r[flag] = True
        _read_stage(m, role + '.' + key, read[key], 'value')
        if not m.active:
            r['normal_return_reference'] = m.row['normal_return_reference']
            return None
    value = max_sp_reference(read['cost_decode']['value'], read['charges_decode']['value'])['signed32_product_reference']
    r['signed32_product_reference'] = value
    for name, flag, qualification in (
            ('max_encode', 'max_encode_called_reference', 'max_encode_normally'),
            ('max_decode', 'max_decode_called_reference', 'max_decode_normally'),
            ('getter_return', 'getter_return_called_reference', 'getter_returns_normally')):
        r[flag] = True
        if not m.stage(role + '.' + name, read[qualification], argument=value, value=value):
            r['normal_return_reference'] = m.row['normal_return_reference']
            return None
    r.update(returned_max_sp_reference=value, normal_return_reference=True,
             status='qualified_capacity_return')
    return value


def _timer(m, mode, normal, argument=None):
    timer = m.state['timer']
    if not m.stage('timer_access', timer['exists']):
        return
    numeric = m.context['timer_qualified']
    before = deepcopy(timer)
    after = deepcopy(timer)
    detail = {'wait_first_period_reference': True if mode in ('periodic_reset', 'periodic_reset_current') else None,
              'precise_timer_qualified_reference': numeric}
    if numeric:
        if mode == 'timer_mark_invalid':
            after.update(period_raw=-ONE, remaining_raw=-ONE)
        elif mode == 'periodic_reset':
            period = None if argument is None else max(0, argument)
            after.update(period_raw=period, remaining_raw=period)
        elif mode == 'periodic_reset_current':
            after['remaining_raw'] = before['period_raw']
        else:
            past = subtract(before['period_raw'], before['remaining_raw'])
            unclamped = subtract(argument, past)
            after.update(period_raw=argument,
                         remaining_raw=None if unclamped is None else max(0, unclamped))
            detail.update(past_raw_reference=past, unclamped_remaining_raw_reference=unclamped)
    else:
        after.update(period_raw=None, remaining_raw=None)
    m.write(mode, 'timer', after, normal, argument=argument, detail=detail)


def _data_access(m, data):
    return m.stage('data_access', data['exists'])


def _cost(m, data):
    token = _read_stage(m, 'cost_read', data['cost_read'], 'payload_id')
    if m.active:
        m.write('cost_copy', 'cost_payload_id', token, data['cost_copy_normally'],
                detail={'opaque_payload_size_bytes': 20, 'decoded_cost_reference': None})


def _type_and_increments(m, data):
    value = _read_stage(m, 'sp_type_read', data['sp_type_read'], 'value')
    if not m.active or not m.write('sp_type_store', 'sp_type', value, data['sp_type_store_normally']):
        return
    token = _read_stage(m, 'increments_read', data['increments_read'], 'payload_id')
    if not m.active or not m.stage('increments_destination', data['increments_destination_exists']):
        return
    if not m.stage('increments_length', data['increments_length_read_normally'],
                   value=data['increments_destination_length']):
        return
    m.write('increments_copy', 'increments_payload_id', token, data['increments_copy_normally'],
            detail={'copied_count_reference': data['increments_destination_length'],
                    'actual_elements_reference': None,
                    'partial_elements_on_failed_copy_reference': None})


def _recover_timer(m, action, reset):
    can = _read_stage(m, 'can_recover_read', action['can_recover_read'], 'value')
    if not m.active:
        return
    if can is False:
        _timer(m, 'timer_mark_invalid', action['timer_call_returns_normally'])
        return
    if can is None:
        # The caller merges explicit True/False native branches, retaining the
        # common data-copy boundary; it never chooses a first/second-rate value.
        return
    rate = _read_stage(m, 'second_rate_read', action['second_rate_read'], 'raw')
    if m.active:
        period = safe_fp_divide(ONE, rate)
        _timer(m, 'periodic_reset' if reset else 'periodic_keep_past',
               action['timer_call_returns_normally'], period)


def _merge_value(a, b):
    if type(a) is dict and type(b) is dict and set(a) == set(b):
        return {key: _merge_value(a[key], b[key]) for key in a}
    if type(a) is list and type(b) is list and len(a) == len(b):
        return [_merge_value(x, y) for x, y in zip(a, b)]
    return deepcopy(a) if type(a) is type(b) and a == b else None


def _merge_rows(a, b):
    result = _merge_value(a, b)
    names = list(dict.fromkeys(s['name'] for row in (a, b) for s in row['stages']))
    stages = []
    for name in names:
        found = [next((s for s in row['stages'] if s['name'] == name), None) for row in (a, b)]
        for index in range(2):
            if found[index] is None:
                found[index] = {'name': name, 'called_reference': False,
                                'normal_return_reference': None, 'argument_reference': None,
                                'value_reference': None, 'detail': None}
        stages.append(_merge_value(*found))
    result.update(stages=stages, status='conditional_native_branches',
                  conditional_branches=[a, b])
    # No call/return information is manufactured by list-position alignment.
    if result['capacity_reads'] is None:
        result['capacity_reads'] = []
    return result


def _branch(state, action, context, path):
    reports = []
    for value in (False, True):
        declaration = deepcopy(action)
        target = declaration
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        reports.append(_run_action(state, declaration, context))
    return _merge_rows(*reports)


def _child(m, action, name):
    child = _run_action(m.state, action, m.context)
    m.row['stages'].extend({**deepcopy(s), 'name': name + '.' + s['name']} for s in child['stages'])
    m.row['conditional_branches'] = deepcopy(child['conditional_branches'])
    m.row['known_prefix_state_reference'] = deepcopy(child['known_prefix_state_reference'])
    m.row['state_after_reference'] = deepcopy(child['state_after_reference'])
    m.row['normal_return_reference'] = child['normal_return_reference']
    m.row['status'] = name + '_' + child['status']
    m.state = deepcopy(child['state_after_reference'])
    m.active = child['normal_return_reference'] is True


def _run_action(state, action, context):
    m = _Prefix(state, action, context)
    kind = action['kind']
    if action['ordinary_native_path'] is not True:
        m.stage('ordinary_native_path', None)
        m.row['state_after_reference'] = _unknown_state(state, pointer_unknown=True)
        return m.finish()
    exists = context['entity_exists'] if kind.startswith('entity_') else context['controller_exists']
    if not m.stage('entity_access' if kind.startswith('entity_') else 'controller_access', exists):
        return m.finish()
    if kind == 'construct':
        for name, qualification in (
                ('construct.increment_allocate', 'increments_allocate_normally'),
                ('construct.increment_assign', 'increments_assign_normally')):
            if not m.stage(name, action[qualification], argument=4, value=4):
                if qualification == 'increments_assign_normally':
                    m.row['state_after_reference']['increments_payload_id'] = None
                return m.finish()
        # Allocation proves length4, not element values or a zero cost/owner.
        m.state['increments_payload_id'] = None
        m.boundary()
        if not m.stage('construct.timer_allocate', action['timer_allocate_normally']):
            return m.finish()
        if not m.stage('construct.timer_constructor', action['timer_constructor_normally'],
                       value={'period_raw': 0, 'remaining_raw': 0}):
            return m.finish()
        timer = {'exists': True, 'period_raw': 0 if context['timer_qualified'] else None,
                 'remaining_raw': 0 if context['timer_qualified'] else None}
        if not m.write('construct.timer_assign', 'timer', timer, action['timer_assign_normally']):
            # A failed/unknown reference assignment does not prove which
            # pointer is now stored. This differs from a timer method failure,
            # whose native body does not reassign the controller timer field.
            m.row['state_after_reference']['timer']['exists'] = None
            return m.finish()
        if not m.stage('construct.base_constructor', action['base_constructor_normally']):
            return m.finish()
        hook = action['post_ctor_hotfix']
        if hook['present'] is None:
            return _branch(state, action, context, ('post_ctor_hotfix', 'present'))
        if hook['present']:
            m.stage('construct.post_ctor_hotfix', hook['returns_normally'],
                    detail={'post_callback_state_reference': None})
            m.row['state_after_reference'] = _unknown_state(m.state, pointer_unknown=True)
            m.row['status'] = 'constructor_prefix_only_callback_effects_unknown'
        else:
            m.row['status'] = 'constructor_prefix_complete_no_callback'
        return m.finish()
    if kind == 'reset_timer':
        _timer(m, 'periodic_reset_current', action['timer_call_returns_normally'])
        return m.finish()
    if kind in ('reset', 'update_data'):
        data = action['data']
        if kind == 'reset':
            if not m.write('owner_write', 'owner_id', action['owner_id'], action['owner_write_normally']):
                return m.finish()
        if not _data_access(m, data):
            return m.finish()
        if kind == 'reset':
            # Reset stores type before cost; UpdateSpData does cost first.
            value = _read_stage(m, 'sp_type_read', data['sp_type_read'], 'value')
            if not m.active or not m.write('sp_type_store', 'sp_type', value, data['sp_type_store_normally']):
                return m.finish()
        _cost(m, data)
        if not m.active:
            return m.finish()
        if kind == 'update_data':
            only = action['only_update_sp_cost']
            if only is None:
                return _branch(state, action, context, ('only_update_sp_cost',))
            if only:
                m.row['status'] = 'cost_only_prefix_returned'
                return m.finish()
            _type_and_increments(m, data)
        else:
            # Type has already been stored; no second type read is introduced.
            token = _read_stage(m, 'increments_read', data['increments_read'], 'payload_id')
            if m.active and m.stage('increments_destination', data['increments_destination_exists']):
                if m.stage('increments_length', data['increments_length_read_normally'], value=data['increments_destination_length']):
                    m.write('increments_copy', 'increments_payload_id', token, data['increments_copy_normally'],
                            detail={'copied_count_reference': data['increments_destination_length'],
                                    'actual_elements_reference': None,
                                    'partial_elements_on_failed_copy_reference': None})
        if not m.active:
            return m.finish()
        if action['can_recover_read']['value'] is None:
            # Fork only when the getter reaches and returns normally. A failed
            # independent getter is not silently promoted into either result.
            s = action['can_recover_read']
            if s['exists'] is True and s['normal'] is True:
                return _branch(state, action, context, ('can_recover_read', 'value'))
        _recover_timer(m, action, kind == 'reset')
        return m.finish()
    if kind == 'entity_init':
        first = _capacity_read(m, 'first_max', action['first_max_read'])
        if not m.active:
            return m.finish()
        initial = _read_stage(m, 'init_sp_read', action['init_sp_read'], 'value')
        if not m.active:
            return m.finish()
        prefix = initial_single_reference(first, initial)
        prefix.update(encoder_called_reference=True, encoder_normal_reference=action['single_encoder_normally'],
                      sp_payload_copy_called_reference=False, sp_payload_copy_normal_reference=None,
                      copied_byte_count_reference=None, source_copy_size_bytes=40)
        m.row['initial_sp_prefix'] = prefix
        if not m.stage('single_encoder', action['single_encoder_normally'],
                       argument=prefix['encoder_constructor_argument_raw_reference'],
                       detail={'input_kind': 'System.Single', 'cipher_payload_reference': None}):
            return m.finish()
        prefix.update(sp_payload_copy_called_reference=True,
                      sp_payload_copy_normal_reference=action['sp_payload_copy_normally'])
        if not m.stage('sp_payload_copy', action['sp_payload_copy_normally'], argument=40,
                       detail={'stores_bytes': [16, 16, 8], 'actual_decoded_sp_reference': None}):
            return m.finish()
        prefix['copied_byte_count_reference'] = 40
        second = _capacity_read(m, 'second_max', action['second_max_read'])
        if m.active and m.write('max_sp_store', 'max_sp', second, action['max_sp_write_normally']):
            _child(m, action['controller_reset'], 'controller_reset')
        return m.finish()
    value = _capacity_read(m, 'max', action['max_read'])
    if m.active and m.write('max_sp_store', 'max_sp', value, action['max_sp_write_normally']):
        _child(m, action['controller_update'], 'controller_update')
    return m.finish()


def sp_initialization_reference(payload):
    _validate(payload)
    valid = _source_data() is not None
    context = {key: payload[key] for key in ('entity_exists', 'controller_exists')}
    context['timer_qualified'] = (valid and payload['precise_timer_identity'] is True
                                  and payload['no_intervening_state_changes'] is True)
    state = deepcopy(payload['state'])
    if not valid or payload['no_intervening_state_changes'] is not True:
        state = _unknown_state(state, pointer_unknown=True)
    elif not context['timer_qualified']:
        state = _unknown_state(state, {'timer'})
    chain = True if valid and payload['no_intervening_state_changes'] is True else None
    rows = []
    for action in payload['actions']:
        if chain is not True:
            row = _Prefix(state, action, context).row
            row.update(called_reference=False if chain is False else None,
                       normal_return_reference=None, status='not_called_after_unqualified_chain')
            if chain is None:
                state = _unknown_state(state, _affected(action['kind'], action))
            row['state_after_reference'] = deepcopy(state)
        else:
            row = _run_action(state, action, context)
            state = deepcopy(row['state_after_reference'])
            chain = row['normal_return_reference']
        rows.append(row)
    return {'source_valid': valid, 'source_file': SOURCE,
            'declared_initial_state': deepcopy(payload['state']), 'rows': rows,
            'state_after_reference': state, 'normal_return_reference': chain,
            'actual_current_sp': None, 'complete_cycle': None,
            'actual_attribute_values': None, 'events_scheduled': False,
            'hotfix_equivalence_proven': False,
            'scope': 'Ordinary native SP prefixes over independent declarations; encoded input/copy and timer references are not actual SP or a whole initialization/cycle.',
            'remaining_unknown': ['protected encoding/next decode', 'actual owner/data/timer/attribute reads',
                                  'later Entity/Character/BasicSkill callbacks and modifiers',
                                  'actual skill activation, first/cast/recovery cycle']}


def natural_clock_link(report, link):
    """Create a separate274 request; never overwrite observations or execute it."""
    _keys(link, {'after_action_id', 'controller_exists', 'precise_timer_identity',
                 'no_intervening_timer_changes', 'actions'})
    _id(link['after_action_id'])
    for key in ('controller_exists', 'precise_timer_identity', 'no_intervening_timer_changes'):
        _tri(link[key])
    # Validate even an unqualified proposed link using the exact pinned274 schema.
    request = {key: deepcopy(link[key]) for key in (
        'controller_exists', 'precise_timer_identity', 'no_intervening_timer_changes', 'actions')}
    request['timer'] = {'exists': None, 'period_raw': None, 'remaining_raw': None}
    _validate_clock(request)
    if type(report) is not dict or type(report.get('rows')) is not list:
        raise ValueError('link需要本模块完整结果。')
    row = next((r for r in report['rows'] if r['id'] == link['after_action_id']), None)
    if row is None:
        raise ValueError('link所指定操作不在结果内。')
    valid = _source_data() is not None and report.get('source_valid') is True
    after = row['state_after_reference']
    qualified = (valid and row['called_reference'] is True
                 and row['normal_return_reference'] is True
                 and all(link[k] is True for k in (
                     'controller_exists', 'precise_timer_identity', 'no_intervening_timer_changes'))
                 and after['timer']['exists'] is True
                 and after['timer']['period_raw'] is not None
                 and after['timer']['remaining_raw'] is not None)
    if qualified:
        request['timer'] = deepcopy(after['timer'])
    return {'source_valid': valid, 'qualified_reference': qualified,
            'request': request if qualified else None,
            'status': 'separate_274_request' if qualified else 'unqualified_timer_link',
            'actual_clock': None, 'complete_cycle': None}


def verify_primary_files(dll_path, metadata_path):
    """Explicit file-only guard for every47 proof span plus inherited MAX.

    Never loads/executed the DLL or reads game-process memory. Paths are provided
    explicitly for local acceptance; runtime arithmetic does not find the game.
    """
    source = _source_data()
    if source is None:
        return {'available': False, 'passed': False, 'status': 'unqualified_public_source',
                'game_dll_executed': False, 'process_memory_read': False}
    root = Path(__file__).resolve().parents[1]
    proof = json.loads((root / source['primary_proof']).read_text(encoding='utf-8'))
    inherited = json.loads((root / source['timer_max_proof']).read_text(encoding='utf-8'))
    selected = next(m for m in inherited['methods'] if m['method']['metadata_method_index'] == 220529)
    extra = [{'source': 'dll', 'physical_offset': int(i['physical_offset'], 16),
              'raw_hex': i['bytes'], 'label': 'TSMath.Max@' + i['address']}
             for i in selected['instructions']]
    spans = proof['byte_spans'] + extra
    files = {'dll': Path(dll_path), 'metadata': Path(metadata_path)}
    checked = 0
    hashes = {}
    try:
        for kind, path in files.items():
            with path.open('rb') as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as raw:
                digest = hashlib.sha256(raw).hexdigest()
                hashes[kind] = digest
                if digest != source[kind + '_sha256']:
                    return {'available': True, 'passed': False, 'status': 'primary_hash_mismatch',
                            'sha256': hashes, 'checked_spans': checked,
                            'game_dll_executed': False, 'process_memory_read': False}
                for span in spans:
                    if span['source'] != kind:
                        continue
                    offset = span['physical_offset']
                    expected = bytes.fromhex(span['raw_hex'])
                    if offset < 0 or raw[offset:offset + len(expected)] != expected:
                        return {'available': True, 'passed': False, 'status': 'primary_byte_span_mismatch',
                                'label': span['label'], 'checked_spans': checked,
                                'game_dll_executed': False, 'process_memory_read': False}
                    checked += 1
        return {'available': True, 'passed': True, 'status': 'fresh_all_47_plus_inherited_max_file_guard',
                'sha256': hashes, 'checked_spans': checked, 'method_count': 47,
                'primary_span_count': 6351, 'inherited_max_instruction_spans': len(extra),
                'game_dll_executed': False, 'process_memory_read': False}
    except OSError as exc:
        return {'available': False, 'passed': False, 'status': 'primary_file_unavailable',
                'error_type': type(exc).__name__, 'checked_spans': checked,
                'game_dll_executed': False, 'process_memory_read': False}


def _example_read(identity, value):
    return {'id': identity, 'normal': True, 'value': value}


def _example_capacity(identity, cost, charges):
    return {'id': identity, 'ordinary_native_path': True, 'sp_data_exists': True,
            'cost_decode': _example_read(identity + '-cost', cost),
            'charges_decode': _example_read(identity + '-charges', charges),
            'max_encode_normally': True, 'max_decode_normally': True,
            'getter_returns_normally': True}


def _example_data(identity, cost_token):
    return {'exists': True, 'sp_type_read': _example_read(identity + '-type', 1),
            'sp_type_store_normally': True,
            'cost_read': {'id': identity + '-opaque-cost', 'normal': True, 'payload_id': cost_token},
            'cost_copy_normally': True,
            'increments_read': {'id': identity + '-increments', 'normal': True,
                                'payload_id': identity + '-declared-segment'},
            'increments_destination_exists': True, 'increments_length_read_normally': True,
            'increments_destination_length': 4, 'increments_copy_normally': True}


def _example_reset(identity):
    return {'id': identity, 'kind': 'reset', 'ordinary_native_path': True,
            'owner_id': '声明的Entity甲', 'owner_write_normally': True,
            'data': _example_data(identity, '不解码的cost甲'),
            'can_recover_read': {'id': identity + '-eligibility', 'exists': True,
                                 'normal': True, 'value': True},
            'second_rate_read': {'id': identity + '-second-rate', 'exists': True,
                                 'normal': True, 'raw': 4 * ONE},
            'timer_call_returns_normally': True}


def public_example():
    """Public labels/literals only; no actual game/private-state snapshot."""
    construct = {'id': '构造0比0计时器', 'kind': 'construct', 'ordinary_native_path': True,
                 **{k: True for k in ('increments_allocate_normally', 'increments_assign_normally',
                                     'timer_allocate_normally', 'timer_constructor_normally',
                                     'timer_assign_normally', 'base_constructor_normally')},
                 'post_ctor_hotfix': {'present': False, 'returns_normally': None}}
    init = {'id': '两次独立上限与初始编码前缀', 'kind': 'entity_init', 'ordinary_native_path': True,
            'first_max_read': _example_capacity('第一上限', 10, 2),
            'init_sp_read': _example_read('独立初始技力', 30),
            'single_encoder_normally': True, 'sp_payload_copy_normally': True,
            'second_max_read': _example_capacity('第二上限', 7, 3),
            'max_sp_write_normally': True, 'controller_reset': _example_reset('初始化控制器')}
    update = {'id': '仅更新cost仍先写Entity上限', 'kind': 'entity_update', 'ordinary_native_path': True,
              'max_read': _example_capacity('仅cost前独立上限', 9, 3),
              'max_sp_write_normally': True,
              'controller_update': {'id': '仅cost控制器', 'kind': 'update_data',
                                    'ordinary_native_path': True, 'only_update_sp_cost': True,
                                    'data': _example_data('更新声明', '不解码的cost乙'),
                                    'can_recover_read': {'id': '不应读取的资格', 'exists': None, 'normal': None, 'value': None},
                                    'second_rate_read': {'id': '不应读取的第二率', 'exists': None, 'normal': None, 'raw': None},
                                    'timer_call_returns_normally': None}}
    negative = {'id': '独立负初始技力不截零', 'kind': 'entity_init', 'ordinary_native_path': True,
                'first_max_read': _example_capacity('负初始第一上限', 10, 2),
                'init_sp_read': _example_read('独立负初始读取', -5),
                'single_encoder_normally': True, 'sp_payload_copy_normally': True,
                'second_max_read': _example_capacity('负初始第二上限', 5, 3),
                'max_sp_write_normally': True, 'controller_reset': _example_reset('负初始控制器')}
    return {'entity_exists': True, 'controller_exists': True, 'precise_timer_identity': True,
            'no_intervening_state_changes': True,
            'state': {'owner_id': '构造前独立owner', 'sp_type': 7,
                      'cost_payload_id': '构造前opaque-cost', 'increments_payload_id': '旧segment',
                      'max_sp': 4, 'timer': {'exists': False, 'period_raw': None, 'remaining_raw': None}},
            'actions': [construct, init, update, negative]}
