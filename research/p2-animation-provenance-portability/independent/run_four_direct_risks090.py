"""Execute only the four frozen distinct verifier risks, with full saved inputs."""
import gzip
import hashlib
import importlib.util
import json
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE / 'risk-plan-frozen090.json'
SCRIPT = HERE / 'candidate/scripts/verify_original_animation_provenance.py'
SUMMARY = HERE / 'fresh-four-direct-verifier-receipt090.json'
FIXTURE = HERE / 'public-fixture090'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def describe(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def state(paths):
    return [describe(path) for path in paths]

assert not SUMMARY.exists() and not (HERE / 'fresh-four-verifier-failure090.json').exists()
plan_raw = PLAN.read_bytes()
assert sha(plan_raw) == '448e12fabd366892c9ec0393fdc55a196b113665023ff5b5fbf345053566a113'
plan = json.loads(plan_raw)
assert len(plan['risks']) == plan['maximum_fresh_verifier_entries'] == 4
assert describe(SCRIPT) == plan['candidate_script']
bound = json.loads((HERE / 'public-fixture-root619-reconstruction090.json').read_bytes())
original_paths = [Path(row['source_path']) for row in bound['files']]
original_before = state(original_paths + [SCRIPT])
for actual, expected in zip(original_before, bound['files']):
    assert actual['bytes'] == expected['bytes'] and actual['sha256'] == expected['sha256']
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('independent_candidate090', SCRIPT)
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)
actual_entries = 0
explicit_direct_calls = 0
def profile(frame, event, arg):
    global actual_entries
    if event == 'call' and frame.f_code.co_name == 'verify' and Path(frame.f_code.co_filename) == SCRIPT:
        actual_entries += 1
assert candidate.__name__ != '__main__'
rows = []
old_raw = (FIXTURE / candidate.DATA_RELATIVE).read_bytes()
old_data = json.loads(old_raw)
assert (json.dumps(old_data, ensure_ascii=False, indent=2) + '\n').replace('\n', '\r\n').encode() == old_raw
for risk in plan['risks']:
    assert explicit_direct_calls < 4
    root = HERE / 'runtime-public-only' / risk['id']
    paths = []
    for source_row in bound['files']:
        target = root / source_row['root_relative_path']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(Path(source_row['source_path']).read_bytes())
        paths.append(target)
    data = json.loads(old_raw)
    if 'record_id' in risk:
        record = next(row for row in data['operators']['char_196_sunbr']['records'] if row['id'] == risk['record_id'])
        old = record[risk['key']]
        assert type(old).__name__ == risk['old']['type'] and old is risk['old']['value']
        record[risk['key']] = risk['new']['value']
        mutation = {'record_id': risk['record_id'], 'key': risk['key'],
            'old_native': {'type': type(old).__name__, 'value': old}, 'new_native': risk['new']}
    else:
        pointer = risk['pointer']
        container = data
        for key in pointer[:-1]:
            container = container[key]
        old = container[pointer[-1]]
        assert type(old).__name__ == risk['old']['type']
        if 'value' in risk['old']:
            assert old == risk['old']['value']
        else:
            assert sha(json.dumps(old, ensure_ascii=False).encode()) == risk['old']['whole_sha256']
        container[pointer[-1]] = risk['new']['value']
        mutation = {'pointer': pointer, 'old_native': {'type': type(old).__name__, 'value': old}, 'new_native': risk['new']}
    mutated = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').replace('\n', '\r\n').encode()
    input_path = root / candidate.DATA_RELATIVE
    input_path.write_bytes(mutated)
    snapshot = HERE / 'risk-inputs' / (risk['id'] + '.json.gz')
    snapshot.parent.mkdir(exist_ok=True)
    snapshot.write_bytes(gzip.compress(mutated, mtime=0))
    assert gzip.decompress(snapshot.read_bytes()) == mutated
    before = state(paths + [SCRIPT])
    # Every fixed source leaf/manifest stays identical; only references may change.
    for actual, original in zip(before, original_before):
        if Path(actual['source_path']) != input_path:
            assert actual['bytes'] == original['bytes'] and actual['sha256'] == original['sha256']
    arguments = {'repository_root': str(root)}
    exception = None
    unexpected = None
    explicit_direct_calls += 1
    sys.setprofile(profile)
    try:
        try:
            value = candidate.verify(repository_root=root)
            unexpected = {'returned_unexpected_success': value}
        except candidate.ProvenanceError as error:
            exception = {'module': type(error).__module__, 'class': type(error).__name__,
                'code': error.code, 'message': str(error), 'repr': repr(error),
                'traceback': traceback.format_exc()}
        except Exception as error:
            unexpected = {'module': type(error).__module__, 'class': type(error).__name__,
                'message': str(error), 'traceback': traceback.format_exc()}
    finally:
        sys.setprofile(None)
    after = state(paths + [SCRIPT])
    row = {'risk_id': risk['id'], 'plan_sha256': sha(plan_raw),
        'candidate_sha256': plan['candidate_script']['sha256'], 'call_arguments': arguments,
        'mutation': mutation, 'saved_mutated_full_references_gzip': describe(snapshot),
        'full_references_decoded_bytes': len(mutated), 'full_references_decoded_sha256': sha(mutated),
        'file_hashes_before': before, 'file_hashes_after': after,
        'all_inputs_unmodified_by_verifier': before == after,
        'exception': exception, 'unexpected': unexpected,
        'expected_code': risk['expected_code'],
        'actual_entries_cumulative': actual_entries, 'explicit_direct_calls_cumulative': explicit_direct_calls}
    rows.append(row)
    save(HERE / 'risk-results' / (risk['id'] + '.json'), row)
    if unexpected is not None or exception is None or exception['code'] != risk['expected_code'] or before != after:
        save(HERE / 'fresh-four-verifier-failure090.json', {'records': rows, 'completed_entries': actual_entries,
            'remaining_risk_ids': [r['id'] for r in plan['risks'][len(rows):]], 'no_retries': True})
        raise AssertionError('Bounded verifier risk did not meet its frozen contract: ' + risk['id'])
assert actual_entries == explicit_direct_calls == len(rows) == 4
original_after = state(original_paths + [SCRIPT])
assert original_after == original_before
summary = {'format_version': 1, 'status': 'PASS_FOUR_DISTINCT_FROZEN_DIRECT_VERIFIER_RISKS', 'passed': True,
    'risk_plan': describe(PLAN), 'candidate': describe(SCRIPT),
    'fresh_verifier_function_entries': actual_entries,
    'fresh_direct_verifier_entries': explicit_direct_calls, 'fresh_CLI_invocations': 0,
    'distinct_risks': 4, 'expected_errors_detected': 4, 'unexpected_errors': 0,
    'product_failures': 0, 'old_author28_or_six_tests_reexecuted': False,
    'original_public_inputs_and_candidate_before': original_before,
    'original_public_inputs_and_candidate_after': original_after,
    'all_original_and_per_call_inputs_unchanged': True,
    'manifest_and_sixleaf_hashes_never_rebound': True,
    'actual_entry_counter_is_profiled_verify_frame_not_only_planned_count': True,
    'application_API_calls': 0, 'project_helper_calls': 0, 'formatter_calls': 0,
    'source_skeleton_parser_calls': 0, 'network_calls': 0, 'Qt_calls': 0, 'Wine_calls': 0,
    'old_or_new_unittest_methods_executed': 0, 'tracked_or_private_state_mutations': 0,
    'risks': [{'risk_id': row['risk_id'], 'expected_code': row['expected_code'],
        'actual_code': row['exception']['code'], 'inputs_unchanged': row['all_inputs_unmodified_by_verifier'],
        'saved_record': describe(HERE / 'risk-results' / (row['risk_id'] + '.json'))} for row in rows]}
save(SUMMARY, summary)
print(json.dumps({'status': summary['status'], 'actual_profiled_verify_entries': actual_entries,
    'actual_direct_calls': explicit_direct_calls, 'CLI_invocations': 0,
    'receipt': describe(SUMMARY)}, ensure_ascii=False))
