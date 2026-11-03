"""One-time byte manifest finalizer; no source parser or application operations."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'public-artifacts-manifest087.json'
HANDOFF = ROOT / 'final-handoff087.json'
assert not MANIFEST.exists() and not HANDOFF.exists(), 'Sealed source package must not be rewritten'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

warning = ROOT / 'choices-checker-preparation-warning087.json'
dump(warning, {
    'version': 1, 'stage': 'Independent source-text checker Python literal compilation',
    'warning_count': 1, 'failed_attempts': 0,
    'actual_stderr': "/workspace/.continuation/p2-gummy-back-parser-source087-official-reader/review_choices_scope087.py:36: SyntaxWarning: invalid escape sequence '\\d'\n  assert \"number=re.match(r'^Skill_?(\\d+)(?:_|$)',name)\" in source\n",
    'actual_checker_status': 'PASS_SOURCE_ONLY_NO_UI_OPTION_COUNT',
    'cause': 'Ordinary Python string contains the literal regular-expression escape while checking source text',
    'source_or_regex_modified': False, 'checker_rerun': False,
    'full_parser_application_API_helper_formatter_tests_Qt_Wine_calls': 0,
    'note': 'Successful source comparison is retained. This warning is not a reader failure.'
})

sealed_at = datetime.now(timezone.utc).isoformat()
receipt_paths = ['source-contract-receipt087.json', 'saved-source-result-review087.json',
                 'choices-source-independent-review087.json', 'official-local-save-times087.json']
for relative in receipt_paths:
    assert (ROOT / relative).is_file()
assert json.loads((ROOT / receipt_paths[0]).read_text())['status'] == 'SOURCE_ONLY_PASS_READER_NOT_EXECUTED_BY_REVIEWER'
assert json.loads((ROOT / receipt_paths[1]).read_text())['status'] == 'PASS_SAVED_SOURCE_ONLY'
assert json.loads((ROOT / receipt_paths[2]).read_text())['status'] == 'PASS_SOURCE_ONLY_NO_UI_OPTION_COUNT'
dump(HANDOFF, {
    'version': 1, 'status': 'FINAL_SEALED_SOURCE_AND_SAVED_ONLY_PASS',
    'sealed_at_utc': sealed_at, 'directory': str(ROOT),
    'official_commit': '8b4844bd4b193ba9e54487ed397a777993cbad56',
    'resource_commit': 'd0b5af0b004b044d322397ce5ae79632b6d9fcdd',
    'official_bundle_SHA256': sha(ROOT / 'official-source/spine-ts/build/spine-core.js'),
    'factory': {'source_path': str(ROOT / 'research_attachment_factory087.js'),
        'bytes': (ROOT / 'research_attachment_factory087.js').stat().st_size,
        'sha256': sha(ROOT / 'research_attachment_factory087.js'),
        'export': 'exports.createLoader = createLoader'},
    'review_receipts': [{'source_path': str(ROOT / name), 'archive_path': name,
                        'bytes': (ROOT / name).stat().st_size, 'sha256': sha(ROOT / name)}
                       for name in receipt_paths],
    'manifest': {'path': str(MANIFEST), 'version': 1, 'self_excluded': True,
        'includes_this_handoff': True},
    'official_raw_source_GET_attempts': 13, 'official_raw_sources_successfully_saved': 12,
    'preparation_diagnostics': [
        {'problem': 'API metadata CONNECT 403', 'failures': 1, 'parser_calls': 0,
         'evidence': 'initial-api-metadata-denial087.json',
         'fidelity': 'Actual error/type strings and observed network settings saved; original full tool stack remains conversation evidence, not a recreated local traceback'},
        {'problem': 'Wrong AttachmentLoader root source path HTTP404', 'failures': 1, 'parser_calls': 0,
         'evidence': 'official-dependency-acquisition087.json', 'fidelity': 'Original full HTTPError traceback saved'},
        {'problem': 'Acquisition script patch addition-prefix error', 'failures': 1, 'parser_calls': 0,
         'evidence': 'initial-dependency-script-preparation-error087.json'},
        {'problem': 'Factory named export versus parent runner receiver', 'actual_execution_failures': 0,
         'parser_calls_before_prevention': 0, 'scope': 'Exact static prevention before execution; parent corrected receiver only'},
        {'problem': 'Python source-literal escape warning', 'warnings': 1, 'failures': 0,
         'evidence': 'choices-checker-preparation-warning087.json', 'rerun': False}
    ],
    'saved_parent_reader_operations': {'Front': 1, 'Back': 1, 'new_reader_errors': 0,
        'Front_exact_prior_duration_version_events_resource_controls': 9,
        'Back_bones': 34, 'Back_slots': 28, 'Back_animations': 5,
        'Back_source_candidates': 2, 'actual_UI_options_measured': False},
    'historical_total_parse_attempts': None, 'historical_visible_failure_lower_bound': 1,
    'historical_reader_identity_or_root_cause_established': False,
    'reviewer_execution_counts': {'bundle': 0, 'compile': 0, 'full_parser': 0,
        'application_API': 0, 'production_helper': 0, 'formatter': 0, 'tests': 0,
        'Qt': 0, 'Wine': 0, 'tracked_mutations': 0},
    'native_game_binding_verified': False, 'EOF_verified': False,
    'texture_atlas_render_geometry_verified': False,
    'product_patch_or_draft_included': False,
    'next_owner': 'Root decides concrete offline source-reference integration; any new audit gets a new external directory.',
    'sealed_files_mutable': False, 'repetition_of_passed_parser_or_control_authorized': False
})

source_origins = {}
for acquisition_name in ['official-minimal-acquisition087.json', 'official-dependency-acquisition087.json',
                         'official-core-bundle-acquisition087.json', 'official-loader-contract-acquisition087.json']:
    acquisition = json.loads((ROOT / acquisition_name).read_text())
    entries = acquisition.get('files', [acquisition['file']] if 'file' in acquisition else [])
    for entry in entries:
        if entry['success']:
            source_origins[entry['archive_path']] = entry['source_path']
for name in ['source-contract-receipt087.json', 'saved-source-result-review087.json',
             'choices-source-independent-review087.json']:
    receipt = json.loads((ROOT / name).read_text())
    for row in receipt.get('parent_source_bindings', []) + receipt.get('input_bindings', []):
        source_origins[row['archive_path']] = row['source_path']
files = []
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path == MANIFEST:
        continue
    relative = str(path.relative_to(ROOT))
    files.append({'source_path': source_origins.get(relative, str(path)),
                  'archive_path': relative, 'bytes': path.stat().st_size, 'sha256': sha(path)})
dump(MANIFEST, {'version': 1, 'status': 'FINAL_STABLE', 'sealed_at_utc': sealed_at,
    'root': str(ROOT), 'file_count': len(files), 'total_bytes': sum(item['bytes'] for item in files),
    'manifest_self_excluded': True, 'handoff_included': True, 'files': files})
for row in files:
    p = ROOT / row['archive_path']
    assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256']
print(json.dumps({'status': 'FINAL_STABLE_NO_FURTHER_WRITES', 'file_count': len(files),
    'total_bytes': sum(item['bytes'] for item in files),
    'manifest_path': str(MANIFEST), 'manifest_sha256': sha(MANIFEST),
    'handoff_path': str(HANDOFF), 'handoff_sha256': sha(HANDOFF)}, ensure_ascii=False))
