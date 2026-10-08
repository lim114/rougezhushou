"""Verify saved native test proof only; never import project or run its tests."""
import gzip
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
receipt = json.loads((OUT / 'new-tests-independent-receipt088.json').read_bytes())
path = OUT / 'new-tests-native-evidence088.json.gz'
compressed = path.read_bytes()
raw = gzip.decompress(compressed)
assert hashlib.sha256(compressed).hexdigest() == receipt['native_evidence_gzip_sha256']
assert len(compressed) == receipt['native_evidence_gzip_bytes']
assert hashlib.sha256(raw).hexdigest() == receipt['native_evidence_decoded_sha256']
assert len(raw) == receipt['native_evidence_decoded_bytes']
data = json.loads(raw)
assert receipt['status'] == 'PASS' and receipt['methods_run'] == 8
assert receipt['failures'] == receipt['errors'] == receipt['skips'] == 0
events = data['public_call_return_events']
assert len(events) == receipt['counts']['public_function_entries'] == 19
assert all(r['caller_input_typed_before'] == r['caller_input_typed_after'] for r in events)
assert data['catalog_native_sha256_before'] == data['catalog_native_sha256_after']
resets = data['context_reset_return_observations']
assert len(resets) == receipt['counts']['named_condition_leaf_entries']['isolated'] == 27
assert all(r['pending_restored_after_return'] is (False if r['caller'] == 'outer' else None) for r in resets)
workers = sorted({r['thread_name'] for r in resets if r['caller'] == 'thread_case'})
assert len(workers) == 1
output = {'format_version': 1, 'status': 'PASS_SAVED_NATIVE_TEST_PROOF_0PROJECTCALLS',
          'public_return_native_events': 19, 'caller_catalog_native_unchanged': True,
          'finally_reset_observations': 27, 'nested_false_restored': True,
          'outer_none_restored': True, 'worker_threads_observed': workers,
          'thread_evidence_scope': 'MainThread plus one pool worker, no simultaneous two-worker stress claimed.',
          'lossless_gzip_original_bytes': len(raw), 'lossless_gzip_original_sha256': hashlib.sha256(raw).hexdigest(),
          'lossless_gzip_bytes': len(compressed), 'lossless_gzip_sha256': hashlib.sha256(compressed).hexdigest(),
          'new_API_helper_formatter_tests_calls': 0}
target = OUT / 'saved-native-test-proof088.json'
assert not target.exists()
target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(output))
