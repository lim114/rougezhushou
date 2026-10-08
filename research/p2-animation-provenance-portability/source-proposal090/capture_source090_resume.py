"""Resume source-only evidence capture after detecting two ignored public leaves."""
from pathlib import Path, PurePosixPath
import gzip
import hashlib
import json
import subprocess

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
BASE = '1ce970fd30aa3b42d8ef787cde02513f05682b66'
PREFIX = 'research/p2-gummy-back-animation-reference/'
PACKET = PREFIX + 'source-packet087/'
SNAP = OUT / 'source-snapshots'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(name, value):
    with (OUT / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


captured = []
for path in sorted(SNAP.rglob('*')):
    if not path.is_file():
        continue
    rel = path.relative_to(SNAP).as_posix()
    raw = path.read_bytes()
    old = subprocess.check_output(['git', 'show', BASE + ':' + rel], cwd=ROOT)
    assert raw == old == (ROOT / rel).read_bytes(), rel
    captured.append({'repository_path': rel, 'snapshot_path': path.relative_to(OUT).as_posix(),
                     'bytes': len(raw), 'sha256': sha(raw),
                     'evidence_status': 'actual_git_bytes_at_' + BASE})
assert len(captured) == 18

raw = subprocess.check_output(['git', 'show', BASE + ':.gitignore'], cwd=ROOT)
with (SNAP / '.gitignore').open('xb') as stream:
    stream.write(raw)
captured.append({'repository_path': '.gitignore', 'snapshot_path': 'source-snapshots/.gitignore',
                 'bytes': len(raw), 'sha256': sha(raw), 'evidence_status': 'actual_git_bytes_at_' + BASE})

packet = SNAP / PACKET
manifest_raw = (packet / 'public-artifacts-manifest087.json').read_bytes()
manifest = json.loads(manifest_raw)
assert sha(manifest_raw) == 'db2679793321d9d4a0f817757c53d93f88a16c4d4261f65f54223f69fb8b5265'
ignored = []
for suffix in ('js', 'd.ts'):
    rel = 'official-reader/official-source/spine-ts/build/spine-core.' + suffix
    repository_path = PACKET + rel
    entry = next(e for e in manifest['files'] if e['archive_path'] == rel)
    result = subprocess.run(['git', 'cat-file', '-e', BASE + ':' + repository_path], cwd=ROOT, capture_output=True)
    assert result.returncode == 128, repository_path
    ignore = subprocess.check_output(['git', 'check-ignore', '-v', repository_path], cwd=ROOT).decode().strip()
    raw = (ROOT / repository_path).read_bytes()
    assert len(raw) == entry['bytes'] and sha(raw) == entry['sha256']
    path = SNAP / repository_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)
    item = {'repository_path': repository_path, 'snapshot_path': path.relative_to(OUT).as_posix(),
            'bytes': len(raw), 'sha256': sha(raw),
            'evidence_status': 'existing_working_tree_public_source_not_in_commit',
            'git_cat_file_exit': result.returncode, 'git_ignore_evidence': ignore,
            'matches_original_manifest': True, 'newly_downloaded_or_generated': False}
    captured.append(item)
    ignored.append(item)

required = [
    'parse-Back-result.json', 'parse-Back-operation.json',
    'reacquired/Back/char_196_sunbr.skel',
    'history/original-animation-references.json.gz',
    'official-reader/official-source/spine-ts/build/spine-core.js',
    'official-reader/official-source/spine-ts/build/spine-core.d.ts',
]
checked = []
for name in required:
    entries = [e for e in manifest['files'] if e['archive_path'] == name]
    assert len(entries) == 1, name
    entry = entries[0]
    raw = (packet / name).read_bytes()
    assert len(raw) == entry['bytes'] and sha(raw) == entry['sha256']
    checked.append({'archive_path': name, 'bytes': len(raw), 'sha256': sha(raw),
                    'matches_source_manifest': True})

baseline_raw = gzip.decompress((packet / 'history/original-animation-references.json.gz').read_bytes())
receipt = json.loads((SNAP / PREFIX / 'data-generation-receipt.json').read_bytes())
assert len(baseline_raw) == receipt['old_bytes'] and sha(baseline_raw) == receipt['old_sha256']
current_raw = (SNAP / 'rouge/data/original-animation-references.json').read_bytes()
assert len(current_raw) == receipt['new_bytes'] and sha(current_raw) == receipt['new_sha256']
source = json.loads((packet / 'parse-Back-result.json').read_bytes())
data = json.loads(current_raw)
save('source-read-receipt090.json', {
    'format_version': 1, 'status': 'SOURCE_ONLY_POSITIVE_MAINTENANCE_GAP',
    'baseline_commit': BASE, 'captured_files': captured,
    'original_301_manifest_metadata_entries_read': 301,
    'original_102_source_manifest_metadata_entries_read': len(manifest['files']),
    'necessary_source_leaves_verified_only': checked,
    'untracked_manifest_public_leaves': ignored,
    'source_packet_manifest_sha256': sha(manifest_raw),
    'historical_baseline_gzip_is_existing_real_evidence_not_reconstructed': {
        'decompressed_bytes': len(baseline_raw), 'decompressed_sha256': sha(baseline_raw)},
    'current_data_bytes': len(current_raw), 'current_data_sha256': sha(current_raw),
    'current_counts_read_only': data['counts'],
    'saved_extraction_animations_read_only': source['animations'],
    'current_back_records_read_only': [r for r in data['operators']['char_196_sunbr']['records'] if r['orientation'] == 'Back'],
    'absence_observations': {
        'archived_generator_baseline_data_exists': (ROOT / PREFIX / 'baseline/rouge/data/original-animation-references.json').exists(),
        'historical_timing048_download_manifest_exists': (ROOT / '.cache/research/timing-048/skeleton-downloads.json').exists()},
    'tracked_edits': 0, 'product_drafts': 0, 'source_skeleton_parser_calls': 0,
    'downloads': 0, 'application_API_calls': 0, 'project_helper_calls': 0,
    'formatter_calls': 0, 'tests': 0, 'Qt': 0, 'Wine': 0,
    'not_claimed': ['Full 301/102 archive audit', 'New parser success',
                    'Native binding', 'Rendering/atlas/texture geometry',
                    'EOF consumption', 'Historical parser identity/root cause',
                    'Original 64-skeleton cache reconstruction']})
save('preparation-diagnostics090.json', {
    'format_version': 1,
    'initial_capture_failure': {
        'command': 'python capture_source090.py', 'exit_code': 1,
        'failure': 'git show baseline:.../spine-ts/build/spine-core.js returned 128 because the existing public leaf is ignored and untracked',
        'committed_files_copied_before_stop': 18,
        'dependent_verification_or_product_actions_after_failure': 0,
        'resolution': 'Preserved initial script and copied files; resumed with explicit actual-Git versus untracked-working-source classification, without changing tracked files'},
    'initial_discovery_path_error': {
        'path': 'research/p2-gummy-back-animation-reference/root-current-source087.py',
        'failure': 'Optional rg read found no hyphenated path; actual underscore filename discovered through rg --files',
        'application_source_parser_or_test_calls': 0},
    'large_discovery_output_truncation': {
        'observed': True, 'resolution': 'Used targeted summaries and bounded leaf reads; no source or application actions repeated'},
    'product_failures': 0, 'source_skeleton_parser_failures': 0,
    'same_problem_capture_failures': 1,
    'source_operation_only': True})
print(json.dumps({'status': 'source-only frozen', 'files': len(captured),
                  'actual_git_files': 19, 'working_source_untracked_files': 2,
                  'necessary_source_leaves': 6, 'tracked_edits_or_product_drafts': 0,
                  'application_project_helper_test_source_parser_download_Qt_Wine_calls': 0}))
