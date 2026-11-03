"""Seal source/saved-only artifacts once; no project imports or execution."""
import datetime
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
MANIFEST = OUT / 'public-manifest088.json'
HANDOFF = OUT / 'handoff-final088.json'
assert not MANIFEST.exists() and not HANDOFF.exists()

def row(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'archive_path': path.relative_to(OUT).as_posix(),
        'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

intake = json.loads((OUT / 'frozen-intake088.json').read_bytes())
source = json.loads((OUT / 'static-source-review088.json').read_bytes())
saved = json.loads((OUT / 'saved60-review088.json').read_bytes())
assert intake['original_files_verified'] == 89 and intake['original_bytes_verified'] == 1871550
assert source['status'].startswith('PASS_') and source['total_reader'] == source['total_old_get'] == 12
assert saved['status'].startswith('PASS_') and (saved['pairs'], saved['new_rejections'], saved['whole_native_JSON_three_text_same'], saved['exact_old_errors']) == (60, 23, 32, 5)
diagnostic = {'status': 'LOCAL_PREPARATION_EVIDENCE_RETAINED_SOURCE_PRODUCT_UNCHANGED',
    'manifest_basename_discovery': intake['initial_local_discovery'],
    'saved_Gummy_inactive_reader_scope': {'failed_attempts': 1, 'corrected_attempt': 'PASS',
        'initial_script': row(OUT / 'initial-boundary-review_saved60_088.py'),
        'initial_log': row(OUT / 'initial-boundary-saved-review088.log'),
        'false_assertion': 'Gummy19–22 no observer',
        'actual_saved_source_bound': 'One read return per19–22, pendingFalse; no active event tail inferred.',
        'source_product_or_saved_results_modified': False, 'project_calls': 0},
    'output_truncation_boundary': intake['initial_output_truncation_scope'],
    'passed_source_checker_repeated': False, 'failed_saved_checker_retry_only': True,
    'author_comparators_or_source16_executed': False,
    'same_problem_three_failure_limit_exceeded': False,
    'new_application_calls': 0,
    'source_code_parse_scope': 'Python AST static read only, no application/binary animation source parser invoked.'}
with (OUT / 'preparation-diagnostics088.json').open('x', encoding='utf-8') as stream:
    json.dump(diagnostic, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
handoff = {'status': 'FINAL_SEALED_PASS_INDEPENDENT088_SOURCE_AND_SAVED60_ONLY',
    'packet_root': str(OUT), 'manifest': str(MANIFEST),
    'intake_receipt': row(OUT / 'frozen-intake088.json'),
    'source_receipt': row(OUT / 'static-source-review088.json'),
    'saved60_receipt': row(OUT / 'saved60-review088.json'),
    'preparation_diagnostics': row(OUT / 'preparation-diagnostics088.json'),
    'author_manifest_sha256': intake['manifest_sha256'],
    'author_freeze_sha256': '10e5e8bcbc3e6a8a74e838d5ddd12638a3574230385a876a0c6d03a7c98baf99',
    'author_handoff_sha256': '7092e9b91019882657f797fc25aa89a2c9337fe1b19e5b40b60b730ae441e7b8',
    'counts': {'original_author_files_hash_verified': 89, 'original_bytes': 1871550,
        'old_source_exact_inverses': 6, 'baseline125_actual_git_blobs': 125, 'unchanged_draft119': 119,
        'original_get_and_new_reader': 12, 'extra_raw_tail_observer': 1, 'extra_scenario_get': 0,
        'saved_pairs': 60, 'text_rejections': 23, 'whole_beforeJSON_native_JSON_three_text_same': 32, 'exact_old_errors': 5},
    'actual_new_calls': saved['new_calls_this_review'],
    'author_format_ledger_not_our_calls': saved['author_calls_only'],
    'limitations': ['Private core scope preserves core errors; no allouter-phase priority guarantee.',
        'Raw catalog tree not separately saved: full-native catalog SHA before/after/crossside proof only.',
        'Gummy/event publicreference controls do not prove event tail; original8 scoped helper controls supply that boundary.',
        'Native clocks, acquisition/impact times and attribution remain unknown.',
        'Test source static only here; parent owns fresh API/helper/new8 execution.',
        'ThreadPoolExecutor source parameter does not prove two-worker concurrency pressure.'],
    'immutable_old_packets': ['sourceprep17', 'child13', 'author89', 'source16', '089', '087', 'UI085'],
    'parent_next': 'Hash-import this packet and combine with parent independent fresh/runtime proof; root sole integration/validation.',
    'stop_writing_all_listed_files': True,
    'seal_time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
with HANDOFF.open('x', encoding='utf-8') as stream:
    json.dump(handoff, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
files = sorted(path for path in OUT.rglob('*') if path.is_file() and path != MANIFEST)
assert all(not path.is_symlink() for path in files)
rows = [row(path) for path in files]
manifest = {'version': 1, 'status': handoff['status'], 'files': rows,
    'file_count': len(rows), 'total_bytes': sum(item['bytes'] for item in rows),
    'manifest_self_excluded': True, 'handoff_included': True, 'project_calls_at_seal': 0, 'immutable': True}
with MANIFEST.open('x', encoding='utf-8') as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
for item in rows:
    assert row(Path(item['source_path'])) == item
print(json.dumps({'status': handoff['status'], 'manifest': row(MANIFEST), 'handoff': row(HANDOFF),
    'source_receipt': row(OUT / 'static-source-review088.json'),
    'saved60_receipt': row(OUT / 'saved60-review088.json'),
    'file_count': len(rows), 'total_bytes': manifest['total_bytes'], 'new_project_calls': 0}))
