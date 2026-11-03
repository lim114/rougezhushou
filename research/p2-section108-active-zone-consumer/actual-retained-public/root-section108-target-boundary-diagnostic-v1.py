"""Root actual saved-input diagnosis; no project or Qt execution."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import sys

BASE = Path('/workspace/.continuation')
ROOT = Path('/workspace/rougezhushou')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def source_map():
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
            for folder in ('rouge', 'tests', 'scripts')
            for p in sorted((ROOT / folder).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}

def main():
    packet = BASE / 'section108-window-source-v2'
    assert sha((packet / 'native_evidence.py').read_bytes()) == 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
    guard_raw = (BASE / 'resume107-applied-source-v2.json').read_bytes()
    assert sha(guard_raw) == '409249b384daf8c38d1b7576de70ce8b5e0a4c3a387bba3da07cdb84a5f75de0'
    guard = json.loads(guard_raw)
    before = source_map()
    assert before == guard['source_sha256'] and len(before) == 750
    core = (ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes()
    assert sha(core) == guard['source_additional_sha256']['CORE_0.70_VERIFICATION.json']
    receipt_path = BASE / 'resume108-window-gold-v1/receipt.json'
    receipt_raw = receipt_path.read_bytes()
    assert sha(receipt_raw) == 'cd06286e583dab141451d1191a9760349120aebff2513fb773c2d2654744524a'
    receipt = json.loads(receipt_raw)
    assert (BASE / 'resume108-window-gold-v1.exit-code').read_bytes() == b'1\n'
    assert receipt['passed'] is receipt['workflow_complete'] is False
    assert receipt['source_before'] == receipt['source_after'] == before
    assert receipt['Qt_errors'] == receipt['source_drift'] == []
    assert len(receipt['records']) == 17 and receipt['rows'] == receipt['windows'] == []
    sys.path.insert(0, str(packet))
    from native_evidence import read_record, assert_native_equal
    record_ref = receipt['records'][-1]
    native = read_record(BASE / 'resume108-window-gold-v1/records', record_ref)
    assert native['kind'] == 'actual_calculate_result'
    assert_native_equal(native['after'], native['before'], 'Actual original caller preserved')
    actual = native['before']['args'][0]['target_enemy']
    tree = ast.parse((packet / 'window108.py').read_bytes())
    assignments = [n for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'TARGET' for t in n.targets)]
    assert len(assignments) == 1
    declared = ast.literal_eval(assignments[0].value)
    assert actual == declared and list(actual) == ['enemy_id', 'level', 'stage_id']
    assert list(declared) == ['stage_id', 'enemy_id', 'level']
    assert all(type(actual[k]) is type(v) for k, v in declared.items())
    failure = None
    try:
        assert_native_equal(actual, declared, 'Existing exact order identity boundary')
    except AssertionError as error:
        failure = repr(error)
    assert failure is not None
    proposed = {k: declared[k] for k in actual}
    assert_native_equal(actual, proposed, 'Observed real boundary expected order')
    assert source_map() == before and (ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes() == core
    out = BASE / 'root-section108-target-boundary-diagnostic-v1.json'
    assert not out.exists()
    result = {'kind': 'ROOT_ACTUAL108_SAVED_TARGET_BOUNDARY_DIAGNOSIS',
              'completed': True, 'product_pass': False, 'product_modified': False,
              'checked_at_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'failed_Gold_receipt_sha256': sha(receipt_raw), 'failed_Gold_primary': 1,
              'actual_native_ref': record_ref, 'actual_callee_input_target': actual,
              'actual_keys': list(actual), 'Source_expected_target': declared,
              'Source_expected_keys': list(declared), 'same_scalar_values_and_types': True,
              'original_order_assertion_reproduced': failure,
              'proposed_expected_target': proposed, 'new_expected_order_exact_native_match': True,
              'source_count': len(before), 'Source_CORE_unchanged': True,
              'project_API_Qt_Git_executed': False,
              'scope': 'One already saved genuine calculator input; no new UI run, no universal Qt map-order mechanism inferred.'}
    with out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
