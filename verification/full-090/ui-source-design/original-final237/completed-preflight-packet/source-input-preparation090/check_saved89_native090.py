"""Type/hex/order proof for exact saved public mappings; no RunState imports."""
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESIGN = HERE / 'saved89-five-state-UI-consumer-design090.json'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def native(node):
    kind = node['type']
    if kind == 'dict':
        return {native(key): native(value) for key, value in node['items']}
    if kind == 'list':
        return [native(value) for value in node['items']]
    if kind == 'tuple':
        return tuple(native(value) for value in node['items'])
    if kind == 'float':
        return float.fromhex(node['hex'])
    if kind == 'NoneType':
        assert node['value'] is None
        return None
    if kind in ('bool', 'int', 'str'):
        value = node['value']
        assert type(value).__name__ == kind
        return value
    raise AssertionError('Unsupported saved native type ' + kind)

def signature(value):
    if isinstance(value, dict):
        return ('dict', tuple((signature(key), signature(item)) for key, item in value.items()))
    if isinstance(value, list):
        return ('list', tuple(signature(item) for item in value))
    if isinstance(value, tuple):
        return ('tuple', tuple(signature(item) for item in value))
    if isinstance(value, float):
        return ('float', value.hex())
    return (type(value).__name__, value)

design = json.loads(DESIGN.read_bytes())
original = Path(design['original_saved38']['source_path']).read_bytes()
assert sha(original) == design['original_saved38']['sha256']
records = {row['sequence']: row for row in json.loads(gzip.decompress(original))['records']}
proofs = []
for row in design['selected_saved_records']:
    original_row = records[row['saved_sequence']]
    assert sha(json.dumps(original_row, ensure_ascii=False, separators=(',', ':')).encode()) == row['record_original_json_sha256']
    observed = native(row['observed_native'])
    state = native(row['state_native'])
    assert signature(observed) == signature(row['observed']) == signature(original_row['observed_before'])
    assert signature(state) == signature(row['state']) == signature(original_row['state_after'])
    assert type(observed.get('crew_count')).__name__ == row['crew_observed_type']
    assert type(state['crew_count']).__name__ == row['crew_stored_type']
    assert all(member['sources'] == {} for member in state['operators'].values())
    assert all(type(member['present']) is bool for member in state['operators'].values())
    assert all(type(member['fields']['elite']) is int and type(member['fields']['level']) is int for member in state['operators'].values())
    proofs.append({'saved_sequence': row['saved_sequence'], 'observed_crew_type': row['crew_observed_type'],
        'stored_crew_type': row['crew_stored_type'], 'native_float_hex_and_all_types_order_exact': True,
        'native_member_present_bool_and_cultivation_fields_int': True,
        'stored_sources_are_original_empty_maps_not_actual_OCR_claim': True,
        'selected_source_is_synthetic_saved_public_test_state': True})
out = {'status': 'PASS_FIVE_ORIGINAL_SAVED89_NATIVE_PUBLIC_MAPPINGS_ONLY', 'records': proofs,
    'public_state_projection_count': 5, 'RunState_constructor_calls': 0, 'RunState_apply_calls': 0,
    'application_API_helpers_formatter_tests_Qt_Wine_calls': 0,
    'original38_phase_not_reexecuted': True, 'UUID_timestamp_or_any_field_normalized': False,
    'actual_GUI_membership_training_or_apply_pipeline_pass_claimed': False}
(HERE / 'saved89-native-proof090.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': out['status'], 'records': 5, 'new_project_calls': 0,
    'sha256': sha((HERE / 'saved89-native-proof090.json').read_bytes())}))
