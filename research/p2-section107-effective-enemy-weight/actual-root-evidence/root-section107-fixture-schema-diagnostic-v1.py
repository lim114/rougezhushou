"""Root actual read-only saved-container diagnosis after Gold attempt1."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

root = Path('/workspace/rougezhushou')
base = Path('/workspace/.continuation')
packet = base / 'section107-window-source-v2'
sys.path.insert(0, str(root))
sys.path.insert(0, str(packet))
from native_evidence import assert_native_equal, freeze, source_map

guard = json.loads((base / 'resume106-applied-source-v1.json').read_bytes())
assert source_map(root) == guard['source_sha256'] and len(guard['source_sha256']) == 749
for name, want in guard['source_additional_sha256'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == want
runner = packet / 'window107.py'
assert hashlib.sha256(runner.read_bytes()).hexdigest() == '9a0b8d82e6712286ef0014e08217ad7b9d386e69051b0f4caebd9b1a7b3c9dd7'
spec = importlib.util.spec_from_file_location('root_fixture107_diagnostic', runner)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
from rouge.run_state import _validate_saved_containers

facts = json.loads((packet / 'fixture-facts.json').read_bytes())
zone = json.loads((root / 'rouge/data/run-config.json').read_bytes())['zones']['zone_1']
rows = []
for case in module.cases(facts):
    saved = module.fixture(case)
    before = freeze(saved)
    original_error = None
    try:
        _validate_saved_containers(saved)
    except ValueError as error:
        original_error = {'type': type(error).__name__, 'message': str(error)}
    assert original_error is not None
    assert_native_equal(saved, before, 'Original rejected fixture preserved')
    saved['config']['zone']['name'] = zone['name']
    corrected_before = freeze(saved)
    _validate_saved_containers(saved)
    assert_native_equal(saved, corrected_before, 'Corrected qualified fixture preserved')
    rows.append({'case': case['id'], 'original_error': original_error,
                 'only_added_path': 'config.zone.name', 'actual_public_name': zone['name'],
                 'corrected_original_validator_passed': True, 'callers_unchanged': True})
assert len(rows) == 13 and source_map(root) == guard['source_sha256']
for name, want in guard['source_additional_sha256'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == want
receipt = {'kind': 'ROOT_ACTUAL_107_PUBLIC_FIXTURE_SCHEMA_DIAGNOSIS',
           'passed': True, 'workflow_complete': True, 'actual_original_validator_calls': 26,
           'actual_old_expected_rejections': 13, 'actual_corrected_qualifications': 13,
           'rows': rows, 'source_sha256': guard['source_sha256'], 'source_drift': [],
           'source_additional_sha256': guard['source_additional_sha256'],
           'window_main_invoked': False, 'product_modified': False,
           'native_windows_game_chat_verified': False}
with (base / 'root-section107-fixture-schema-diagnostic-v1.json').open('x') as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({k: receipt[k] for k in ('passed', 'actual_original_validator_calls',
      'actual_old_expected_rejections', 'actual_corrected_qualifications')}))
