"""Freeze exact saved3 preservation and source repair before the remaining five calls."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / 'new8-resume-execution-freeze090.json'
assert not TARGET.exists()

def describe(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

required = {
    'api-ui090-section088-new8-failure.json.gz': '737c83d72ebfda4f8c9c43ca799f8d573ecab493845f4dfbbef4fe0d659a0439',
    'preflight_ui090_section088.py': '42bf58f3a892935862336a2fc04d7bdcc71743b1de768d886d53b4759ceae640',
    'new8-execution-freeze090.json': 'c2e04ce1373cbfa23e96150911879896a6fa03b0f3836036fb8be712198d0b89',
    'saved3-timing-contract-reassertion090.json': '0e8bc9f0ff89398472e570229f5b327c941880e70a6d22a9b21b4a5c5540c4ae',
    'resume_ui090_section088_remaining5.py': '6881c81a2d0ee581f93f436790c1ae9701874337a90af1d76a6ceb4e97ea17fd',
    'review-saved3-prepared-timing/receipt.json': '8c85693e380f1c37bbd8fd0ca2508ffe3f4ac207233d4f34a1998a76b982883e',
    'review-saved3-prepared-timing/manifest.json': 'ae66abdea3a96b13b212bdc3a1faa3acd8330ee9e73d8d4dc38ae00bf2f19887',
    'review-saved3-prepared-timing/expected-prepared-timing8.json': '9228c3780c3c1532aaa6a81d74f4e8d82ac4e538b255644154e2385fca50de5c',
}
for name, digest in required.items():
    assert describe(HERE / name)['sha256'] == digest, name
manifest = HERE / 'review-saved3-prepared-timing/manifest.json'
for row in json.loads(manifest.read_bytes())['files']:
    path = manifest.parent / row['path']
    actual = describe(path)
    assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
proof = json.loads((HERE / 'actual-root089-ui090-source-proof.json').read_bytes())
package = HERE / 'public-schema-actual-root089'
for row in proof['files']:
    if row['source_path'].startswith('rouge/'):
        actual = describe(package / row['source_path'])
        assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
files = [HERE / name for name in required] + [HERE / 'actual-root089-ui090-source-proof.json',
    HERE / 'original-approved-additional8-input-plan090.json', HERE / 'freeze_remaining5_execution090.py']
value = {'format_version': 1,
    'status': 'FROZEN_REASSERTED_SAVED3_SOURCE_EXACT_PREPARED_TIMING_REMAINING5_ONLY',
    'completed_public_requests_retained': 3, 'completed_texts_retained': 9,
    'completed_actual_formatter_entries_retained': 12,
    'remaining_public_requests_maximum': 5, 'remaining_explicit_text_requests': 15,
    'expected_remaining_actual_formatter_entries_if_same_delegate': 20,
    'same_harness_contract_failed_attempts': 1, 'product_failures': 0,
    'actual_new_API_formatter_Qt_Wine_calls_in_freeze': 0,
    'public_source_and_original_inputs_unchanged': True,
    'files': [describe(path) for path in files]}
TARGET.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(describe(TARGET), ensure_ascii=False))
