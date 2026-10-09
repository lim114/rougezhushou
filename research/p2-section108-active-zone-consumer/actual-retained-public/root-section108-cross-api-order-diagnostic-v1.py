"""Root saved cross-API boundary diagnosis, without project/API/Qt execution."""
from pathlib import Path
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
    packet = BASE / 'section108-window-source-v3'
    assert sha((packet / 'native_evidence.py').read_bytes()) == 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
    guard_raw = (BASE / 'resume107-applied-source-v2.json').read_bytes()
    assert sha(guard_raw) == '409249b384daf8c38d1b7576de70ce8b5e0a4c3a387bba3da07cdb84a5f75de0'
    guard = json.loads(guard_raw)
    before = source_map()
    assert before == guard['source_sha256'] and len(before) == 750
    core = (ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes()
    assert sha(core) == guard['source_additional_sha256']['CORE_0.70_VERIFICATION.json']
    gold_dir = BASE / 'resume108-window-gold-v2'
    receipt_raw = (gold_dir / 'receipt.json').read_bytes()
    assert sha(receipt_raw) == '3da8b76753568d5a1994db04299655d7770dcd51226166abc9568e5706881974'
    receipt = json.loads(receipt_raw)
    assert (BASE / 'resume108-window-gold-v2.exit-code').read_bytes() == b'1\n'
    assert receipt['passed'] is receipt['workflow_complete'] is False
    assert receipt['source_before'] == receipt['source_after'] == before
    assert receipt['source_drift'] == receipt['Qt_errors'] == []
    sys.path.insert(0, str(packet))
    from native_evidence import read_record, write_record, freeze, assert_native_equal
    case = 'accepted-cached-known4_1-legacy-list-main'
    def actual(kind):
        refs = [r for r in receipt['records'] if r['case'] == case and r['kind'] == kind]
        assert len(refs) == 1
        return refs[0], read_record(gold_dir / 'records', refs[0])
    numeric_ref, numeric_record = actual('actual_calculate_result')
    preview_ref, preview_record = actual('actual_independent_enemy_preview')
    assert_native_equal(numeric_record['before'], numeric_record['after'], 'Original numerical caller unchanged')
    assert_native_equal(preview_record['before'], preview_record['after'], 'Original preview caller unchanged')
    assert preview_record['error'] is None
    numeric = numeric_record['result']['run_resolution']['enemy']
    preview = preview_record['result']['environment']
    untouched = freeze((numeric, preview))
    assert type(numeric) is type(preview) is dict
    assert list(numeric)[:3] == ['enemy_id', 'level', 'stage_id']
    assert list(preview)[:3] == ['stage_id', 'enemy_id', 'level']
    assert list(numeric)[3:] == list(preview)[3:]
    assert set(numeric) == set(preview)
    projection = {key: preview[key] for key in numeric}
    assert_native_equal(projection, numeric, 'Full crossAPI native graph with declared identity-prefix order alignment only')
    assert_native_equal((numeric, preview), untouched, 'Both actual original environments remain unchanged')
    out = BASE / 'root-section108-cross-api-order-diagnostic-v1'
    assert not out.exists()
    out.mkdir(); (out / 'records').mkdir()
    record = write_record(out / 'records', 1, {
        'numeric_original_environment': numeric,
        'preview_original_environment': preview,
        'preview_comparison_projection': projection,
        'numeric_original_caller': numeric_record['before'],
        'preview_original_caller': preview_record['before'],
    })
    assert source_map() == before and (ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes() == core
    report = {'kind': 'ROOT_ACTUAL108_SAVED_CROSS_API_IDENTITY_ORDER_DIAGNOSIS',
              'completed': True, 'product_pass': False, 'product_modified': False,
              'failed_Gold_receipt_sha256': sha(receipt_raw), 'failed_Gold_primary': 1,
              'numeric_actual_ref': numeric_ref, 'preview_actual_ref': preview_ref,
              'numeric_keys': list(numeric), 'preview_keys': list(preview),
              'only_different_key_order_domain': ['stage_id', 'enemy_id', 'level'],
              'all_remaining_order_types_floatbits_values_aliases_match': True,
              'both_original_callers_unchanged': True, 'both_original_environments_unchanged': True,
              'saved_unmodified_original_and_explicit_projection_native': record,
              'Source750_CORE_unchanged': True, 'project_API_Qt_Git_executed': False,
              'scope': 'One actual unchanged healthy point through two distinct original API target identity producers; no general map normalization or gameplay mechanism.'}
    with (out / 'report.json').open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__':
    main()
