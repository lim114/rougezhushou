"""Complete cost prefixes with fixed integer-consensus dependency, no actual cost/SP."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

LINKS_SHA256 = '930571f11b823bf14097068ac65f492bc0c3b49e6810bd02523acd6296e3d1d8'
MANIFEST_SHA256 = 'a481e3b8ffa339a6c3a96050c08d2cee3f6f9abf78275b61d50317216c9bac26'
SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / 'research/p2-skill-data-cost-consensus-281'
DEPENDENCY_CORES = {
    'legacy': ('skill_data_cost_reference.py', '7cd8eee14c217c46419b5ac70bbcfe14f63e67a5687b7974d8718ae60618077a'),
    'consensus': ('skill_cost_rounding_consensus.py', '86853e05e770e17d8cdbaabe14d4fb9f13e576efea378333b5470a39ec78aa77'),
}
_BOUND_MODULES = {}
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



def _binding():
    result = {'valid': False, 'status': 'source_unavailable', 'proof_sha256': None,
              'method_count': None, 'byte_span_count': None, 'components': {}}
    try:
        manifest_raw = (SOURCE_DIRECTORY / 'source_manifest.json').read_bytes()
        links_raw = (SOURCE_DIRECTORY / 'source-links.json').read_bytes()
        if hashlib.sha256(manifest_raw).hexdigest() != MANIFEST_SHA256:
            return {**result, 'status': 'manifest_sha_mismatch'}, None
        if hashlib.sha256(links_raw).hexdigest() != LINKS_SHA256:
            return {**result, 'status': 'source_links_sha_mismatch'}, None
        manifest, links = json.loads(manifest_raw), json.loads(links_raw)
        if manifest['source_links_sha256'] != LINKS_SHA256 or links['unique_native_method_count'] != 32 or links['original_byte_span_count'] != 4034:
            return {**result, 'status': 'source_contract_mismatch'}, None
        for filename, expected in manifest['support_files_sha256'].items():
            if hashlib.sha256((SOURCE_DIRECTORY / filename).read_bytes()).hexdigest() != expected:
                return {**result, 'status': 'support_file_sha_mismatch'}, None
        modules = {}
        for key, (filename, expected) in DEPENDENCY_CORES.items():
            path = Path(__file__).resolve().parent / filename
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected or links['components'][key]['core_sha256'] != expected:
                return {**result, 'status': key + '_core_sha_mismatch'}, None
            cache_key = (str(path), expected)
            if cache_key not in _BOUND_MODULES:
                spec = importlib.util.spec_from_file_location('_281_fixed_' + key, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                _BOUND_MODULES[cache_key] = module
            modules[key] = _BOUND_MODULES[cache_key]
        components = {key: module.source_data() for key, module in modules.items()}
        if not all(value['valid'] for value in components.values()):
            return {**result, 'status': 'dependency_source_invalid', 'components': components}, None
        packet_root = SOURCE_DIRECTORY.parent
        proofs = {}
        for key, component in links['components'].items():
            directory = packet_root / component['source_directory']
            for filename, expected in component['source_files_sha256'].items():
                if hashlib.sha256((directory / filename).read_bytes()).hexdigest() != expected:
                    return {**result, 'status': key + '_packet_sha_mismatch'}, None
            if components[key]['proof_sha256'] != component['proof_sha256']:
                return {**result, 'status': key + '_proof_binding_mismatch'}, None
            proofs[key] = json.loads((directory / 'source-proof.json').read_bytes())
        if (proofs['legacy']['dll_sha256'] != proofs['consensus']['dll_sha256']
                or proofs['legacy']['metadata_sha256'] != proofs['consensus']['metadata_sha256']):
            return {**result, 'status': 'different_original_source_versions'}, None
        original_methods = {(row['method']['Address'], row['method'].get('metadata_method_index')): row['reachable_bytes_sha256']
                            for row in proofs['legacy']['methods']}
        if any(original_methods.get((row['method']['Address'], row['method'].get('metadata_method_index')))
               != row['reachable_bytes_sha256'] for row in proofs['consensus']['methods']):
            return {**result, 'status': 'consensus_methods_not_original_subset'}, None
        return {'valid': True, 'status': 'pinned_public_workflow_and_consensus_reference', 'proof_sha256': LINKS_SHA256,
                'method_count': 32, 'byte_span_count': 4034, 'components': components}, modules
    except (OSError, ValueError, TypeError, KeyError, ImportError):
        return result, None


def source_data():
    return _binding()[0]


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



def _empty_row(action, receiver):
    row = {'id': action['id'], 'kind': action['kind'], 'called': False if receiver is False else None,
           'normal': False if receiver is False else None, 'status': 'source_unqualified',
           'stages': [{'name': name, 'called': False if receiver is False else None, 'normal': None, 'reference': None}
                      for name in STAGES[action['kind']]],
           'arithmetic_reference': None, 'encoder_argument_reference': None, 'stored_prefixes': [], 'update_arguments': None,
           'calculation_route': 'source_unqualified', 'consensus_reference': None, **{name: None for name in UNKNOWNS}}
    return row


def _complete(row, name, normal, reference=None):
    names = [stage['name'] for stage in row['stages']]
    index = names.index(name)
    row['stages'][index].update(called=True, normal=normal, reference=deepcopy(reference) if normal is True else None)
    if normal is not True:
        row.update(normal=normal, status='prefix_failed' if normal is False else 'prefix_normality_unknown')
        if normal is False:
            for stage in row['stages'][index + 1:]:
                stage.update(called=False, normal=None, reference=None)
        return False
    return True


def _single_tail(row, action, consensus_module):
    decoded = next(stage for stage in row['stages'] if stage['name'] == 'cost_decode')
    if decoded['called'] is not True or decoded['normal'] is not True:
        return
    for stage in row['stages'][8:]:
        stage.update(called=None, normal=None, reference=None)
    row.update(normal=None, status='numeric_tail_unknown', arithmetic_reference=None,
               encoder_argument_reference=None, stored_prefixes=[], update_arguments=None)
    operation = 'add' if action['kind'] == 'rune_add' else 'mul'
    reference = consensus_module.single_cost_consensus_reference(operation, action['cost_decode']['value'], action['modifier_read']['bits'])
    if reference is None:
        row['status'] = 'consensus_component_invalidated'
        return
    if not _complete(row, 'single_conversion', action['single_conversion_normally'],
                     {'candidates': reference['cost_conversion_candidates'], 'exact': reference['int32_to_single_exact']}):
        return
    cases = [{**{key: value for key, value in case.items() if key not in ('rounded_int32_reference', 'status')},
              'status': 'normal_or_zero_Single_candidate_reference' if case['result_bits_candidates'] else case['status']}
             for case in reference['cases']]
    arithmetic = {'operation': operation, 'cost_int32': action['cost_decode']['value'], 'modifier_bits': action['modifier_read']['bits'],
                  'possible_operation_bits': reference['possible_operation_bits'], 'cases': cases,
                  'all_operations_exact': reference['all_operations_exact']}
    if not _complete(row, 'single_arithmetic', action['single_arithmetic_normally'], arithmetic):
        return
    row['arithmetic_reference'] = deepcopy(arithmetic)
    if not _complete(row, 'round', action['round_normally'], reference):
        return
    row['consensus_reference'] = deepcopy(reference)
    integer = reference['integer_consensus_reference']
    row['encoder_argument_reference'] = integer
    argument = {'argument': integer, 'argument_known': integer is not None,
                'argument_candidates': reference['integer_candidates'], 'returned_payload': None}
    if not _complete(row, 'encode', action['encode_normally'], argument):
        return
    if not _complete(row, 'store', action['store_normally'], {'byte_count': 20}):
        return
    row['stored_prefixes'].append({'field': 'spCost', 'byte_count': 20,
                                   'payload_identity': action['encoded_payload_identity'], 'decoded_value': None})
    row.update(normal=True, status='consensus_cost_store_prefix_complete' if integer is not None else 'opaque_integer_cost_store_prefix_complete')


def skill_data_cost_consensus_reference(payload):
    _validate(payload)
    source, modules = _binding()
    if not source['valid']:
        rows = [_empty_row(action, payload['receiver_exists']) for action in payload['actions']]
    else:
        base = modules['legacy'].skill_data_cost_reference(payload)
        if not base['source']['valid']:
            source = {**source, 'valid': False, 'status': 'legacy_component_invalidated'}
            rows = [_empty_row(action, payload['receiver_exists']) for action in payload['actions']]
        else:
            rows = deepcopy(base['rows'])
            for action, row in zip(payload['actions'], rows):
                single = action['kind'] in SINGLE_KINDS
                row.update(calculation_route='single_consensus_numeric_tail' if single else 'legacy_non_single_reference', consensus_reference=None)
                if single:
                    _single_tail(row, action, modules['consensus'])
            after, _ = _binding()
            if not after['valid']:
                source = {**after, 'status': 'source_invalidated_during_workflow'}
                rows = [_empty_row(action, payload['receiver_exists']) for action in payload['actions']]
    return {'kind': 'skill_data_cost_consensus_reference', 'source': source, 'payload': deepcopy(payload),
            'rows': rows, **{name: None for name in UNKNOWNS}}


def public_example():
    source, modules = _binding()
    if not source['valid']:
        raise ValueError('fixed public source dependencies unavailable')
    old = modules['legacy'].public_example()
    selected = [deepcopy(action) for action in old['actions'] if action['kind'] in ('scale_cost', 'replace_cost')]
    prototype = next(action for action in old['actions'] if action['kind'] == 'rune_mul')

    def single(label, cost, bits, kind='rune_mul'):
        action = deepcopy(prototype)
        original_id = action['id']
        action['id'] = label
        action['kind'] = kind
        for key, value in action.items():
            if isinstance(value, dict) and 'id' in value:
                value['id'] = label + '.' + key
        action['cost_decode']['value'] = cost
        action['modifier_read']['bits'] = bits
        action['encoded_payload_identity'] = label + '.opaque20'
        if kind == 'relic_mul':
            action['modifier_read'].pop('found')
        return action

    rows = [single('public.consensus_two_to_store', 10, 0x3e4ccccd),
            single('public.zero_or_one_opaque_store', 10, 0x3d4ccccd),
            single('public.relic_1_05_to_store', 20, 0x3f866666, 'relic_mul'),
            single('public.add_inexact_to_store', 10, 0x3dcccccd, 'rune_add'),
            single('public.unknown_decoded_operand_opaque_store', None, 0x3f000000),
            single('public.independent_next_decode101', 101, 0x3f000000)]
    rows[4]['modifier_read']['bits'] = None
    unknown = single('public.round_normality_unknown', 10, 0x3e4ccccd)
    unknown['round_normally'] = None
    rows.append(unknown)
    return {'receiver_exists': True, 'actions': rows + selected}
