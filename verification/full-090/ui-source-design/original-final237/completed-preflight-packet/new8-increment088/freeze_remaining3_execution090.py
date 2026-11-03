"""Freeze the fully closed preparation map; only the last three requests may run."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / 'new8-final3-execution-freeze090.json'

def describe(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

parser = argparse.ArgumentParser()
parser.add_argument('--independent-manifest', required=True)
parser.add_argument('--independent-receipt', required=True)
args = parser.parse_args()
manifest = Path(args.independent_manifest)
receipt = Path(args.independent_receipt)
assert not TARGET.exists()
assert receipt.exists() and manifest.exists()
for row in json.loads(manifest.read_bytes())['files']:
    relative = Path(row['path'])
    assert not relative.is_absolute() and '..' not in relative.parts
    actual = describe(manifest.parent / relative)
    assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
expected = {
    'api-ui090-section088-new8-failure.json.gz': '737c83d72ebfda4f8c9c43ca799f8d573ecab493845f4dfbbef4fe0d659a0439',
    'api-ui090-section088-new8-resume-failure.json.gz': '2fdc67eaeee4c4ca4fbef4c0373845ccdd9d599d473759100ddaa79e773d746a',
    'resume_ui090_section088_remaining3.py': '384712959c98d11e456c91f96d91f0d05d1a9d79e0e04224bdc4383b558e4fcf',
    'original-approved-additional8-input-plan090.json': '31beb7f95a256172591226127562324be6625317fd1ad406baa84851130dd521',
}
for name, digest in expected.items():
    assert describe(HERE / name)['sha256'] == digest, name
proof = json.loads((HERE / 'actual-root089-ui090-source-proof.json').read_bytes())
for row in proof['files']:
    if row['source_path'].startswith('rouge/'):
        actual = describe(HERE / 'public-schema-actual-root089' / row['source_path'])
        assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
own = HERE / 'saved5-full-preparation-contract-reassertion090.json'
assert json.loads(own.read_bytes())['status'] == 'PASS_FULL_SAVED5_NATIVE_REPORT_AND_SOURCE_DEFINED_PREPARATION_REASSERTION_ZERO_CALLS'
files = [HERE / name for name in expected] + [own, manifest, receipt,
    HERE / 'remaining3-preassert-checkpoint-ordering-proof090.json',
    HERE / 'actual-root089-ui090-source-proof.json', HERE / 'freeze_remaining3_execution090.py']
value = {'format_version': 1,
    'status': 'FROZEN_FULL_PREPARATION_SOURCE_MAP_SAVED5_REASSERTED_ONLY_REMAINING3_PENDING',
    'completed_actual_public_requests_preserved': 5,
    'completed_explicit_text_requests_preserved': 15,
    'completed_actual_formatter_entries_preserved': 20,
    'remaining_actual_public_requests_maximum': 3,
    'remaining_explicit_text_requests_maximum': 9,
    'expected_remaining_actual_formatter_entries_if_delegate_unchanged': 12,
    'same_prepared_shape_harness_failed_attempts': 2,
    'product_failures': 0, 'third_unresolved_same_problem_defer_required': True,
    'whole_caller_native_unchanged_required': True,
    'full_prepared_native_trace_saved_with_actual_source_defined_transformations': True,
    'API_helpers_formatter_RunState_constructor_apply_Qt_Wine_tests_calls_in_freeze': 0,
    'files': [describe(path) for path in files]}
TARGET.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(describe(TARGET), ensure_ascii=False))
