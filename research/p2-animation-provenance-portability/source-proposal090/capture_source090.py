"""Freeze existing committed leaf evidence for a source-only proposal.

This script does not run a skeleton reader, generator, application or tests.
"""
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
RELATIVE_FILES = [
    'AGENTS.md', 'CLOUD_HANDOFF.md',
    'scripts/build_original_animation_048.py',
    'scripts/build_animation_selection_048.py',
    'rouge/animation_reference.py',
    'rouge/data/original-animation-references.json',
    'tests/test_original_animation_048.py',
    'tests/test_gummy_back_animation_reference.py',
    PREFIX + 'generate_additive_data.py',
    PREFIX + 'root_current_source087.py',
    PREFIX + 'data-generation-receipt.json',
    PREFIX + 'final-public-artifacts-manifest087.json',
    PREFIX + 'NOTE.md',
    PACKET + 'public-artifacts-manifest087.json',
    PACKET + 'parse-Back-result.json',
    PACKET + 'parse-Back-operation.json',
    PACKET + 'reacquired/Back/char_196_sunbr.skel',
    PACKET + 'history/original-animation-references.json.gz',
    PACKET + 'official-reader/official-source/spine-ts/build/spine-core.js',
]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(name, value):
    path = OUT / name
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def safe_path(value):
    parts = PurePosixPath(value).parts
    assert value and not value.startswith('/') and '\\' not in value
    assert all(p not in ('.', '..') and ':' not in p for p in parts)
    assert str(PurePosixPath(value)) == value


captured = []
for rel in RELATIVE_FILES:
    safe_path(rel)
    raw = subprocess.check_output(['git', 'show', BASE + ':' + rel], cwd=ROOT)
    # Do not silently snapshot concurrent tracked edits.
    assert (ROOT / rel).read_bytes() == raw, rel
    target = OUT / 'source-snapshots' / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(raw)
    captured.append({'repository_path': rel, 'snapshot_path': str(target.relative_to(OUT)),
                     'bytes': len(raw), 'sha256': digest(raw),
                     'matches_actual_git_commit': BASE})

snap = OUT / 'source-snapshots'
packet = snap / PACKET
source_manifest_raw = (packet / 'public-artifacts-manifest087.json').read_bytes()
source_manifest = json.loads(source_manifest_raw)
source_manifest_sha = digest(source_manifest_raw)
assert source_manifest_sha == 'db2679793321d9d4a0f817757c53d93f88a16c4d4261f65f54223f69fb8b5265'
required = [
    'parse-Back-result.json', 'parse-Back-operation.json',
    'reacquired/Back/char_196_sunbr.skel',
    'history/original-animation-references.json.gz',
    'official-reader/official-source/spine-ts/build/spine-core.js',
]
leaves = []
for rel in required:
    entries = [item for item in source_manifest['files'] if item['archive_path'] == rel]
    assert len(entries) == 1, rel
    raw = (packet / rel).read_bytes()
    item = entries[0]
    assert len(raw) == item['bytes'] and digest(raw) == item['sha256'], rel
    leaves.append({'archive_path': rel, 'bytes': len(raw), 'sha256': digest(raw),
                   'matches_original_source_packet_manifest': True,
                   'original_source_path_is_historical_metadata_only': item['source_path']})

baseline_raw = gzip.decompress((packet / 'history/original-animation-references.json.gz').read_bytes())
receipt = json.loads((snap / PREFIX / 'data-generation-receipt.json').read_bytes())
assert len(baseline_raw) == receipt['old_bytes'] and digest(baseline_raw) == receipt['old_sha256']
current_raw = (snap / 'rouge/data/original-animation-references.json').read_bytes()
assert len(current_raw) == receipt['new_bytes'] and digest(current_raw) == receipt['new_sha256']
source = json.loads((packet / 'parse-Back-result.json').read_bytes())
data = json.loads(current_raw)
back_records = [r for r in data['operators']['char_196_sunbr']['records'] if r['orientation'] == 'Back']
assert [r['animation'] for r in back_records] == ['Attack', 'Default', 'Idle', 'Skill', 'Start']
write_json('source-read-receipt090.json', {
    'format_version': 1, 'status': 'SOURCE_ONLY_POSITIVE_MAINTENANCE_GAP',
    'baseline_commit': BASE, 'tracked_edits': 0, 'product_drafts': 0,
    'source_skeleton_parser_calls': 0, 'downloads': 0, 'application_API_calls': 0,
    'project_helper_calls': 0, 'formatter_calls': 0, 'tests': 0, 'Qt': 0, 'Wine': 0,
    'captured_committed_files': captured,
    'original_301_manifest_entries_metadata_only': 301,
    'original_102_manifest_entries_metadata_only': len(source_manifest['files']),
    'only_required_source_leaves_rehashed': leaves,
    'source_packet_manifest_sha256': source_manifest_sha,
    'existing_baseline_gzip_is_authentic_historical_evidence_not_reconstructed': {
        'decompressed_bytes': len(baseline_raw), 'decompressed_sha256': digest(baseline_raw)},
    'current_data_bytes': len(current_raw), 'current_data_sha256': digest(current_raw),
    'current_counts_read_only': data['counts'],
    'saved_extraction_five_animations_read_only': source['animations'],
    'current_back_records_read_only': back_records,
    'positive_gap': [
        'Committed historical generator dereferences an absolute external PACKET path.',
        'Committed historical generator dereferences baseline/rouge/data absent from its archive.',
        'Existing all-skeleton integrity test depends on an intentionally unmigrated timing-048 cache.',
        'Historical root checker also fixes section86 registry/source bytes and is not a durable provenance CLI.'
    ],
    'absence_observations': {
        'archived_generator_baseline_json_exists': (ROOT / PREFIX / 'baseline/rouge/data/original-animation-references.json').exists(),
        'historical_timing048_download_manifest_exists': (ROOT / '.cache/research/timing-048/skeleton-downloads.json').exists()
    },
    'not_claimed': ['Fresh parser success', 'Full 301/102 artifact verification',
                    'Native binding', 'Rendering or atlas/texture geometry',
                    'EOF consumption', 'Historical parser identity or root cause',
                    'Original 64-skeleton cache restoration']
})
print(json.dumps({'status': 'source-only frozen', 'captured_files': len(captured),
                  'necessary_source_leaves_checked': len(leaves), 'product_drafts': 0,
                  'application_API_project_helper_test_parser_download_Qt_Wine_calls': 0}))
