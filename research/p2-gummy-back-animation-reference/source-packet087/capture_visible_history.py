import gzip
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASELINE = '9ef5a469673502754db3be320a8eece9a7fd18d4'
PROJECT = Path('/workspace/rougezhushou')
TARGETS = {
    'rouge/data/original-animation-references.json': None,
    'scripts/build_original_animation_048.py': None,
    'scripts/build_animation_selection_048.py': None,
    'PROJECT_COMPLETED.md': [(837, 845)],
    'PROJECT_PROGRESS.md': [(10, 16)],
    'WORK_IN_PROGRESS.md': [(1233, 1251)],
    'BATCH_0.48.md': [(1, 22)],
}
records = []
for rel, ranges in TARGETS.items():
    data = subprocess.check_output(['git', '-C', str(PROJECT), 'show', f'{BASELINE}:{rel}'])
    blob = subprocess.check_output(['git', '-C', str(PROJECT), 'rev-parse', f'{BASELINE}:{rel}']).decode().strip()
    assert hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest() == blob
    record = {'repository_path': rel, 'baseline_commit': BASELINE, 'original_bytes': len(data), 'original_sha256': hashlib.sha256(data).hexdigest(), 'git_blob_sha1': blob}
    if rel.endswith('original-animation-references.json'):
        dest = ROOT / 'history' / 'original-animation-references.json.gz'
        dest.parent.mkdir(parents=True, exist_ok=True)
        packed = gzip.compress(data, compresslevel=9, mtime=0)
        dest.write_bytes(packed)
        restored = gzip.decompress(packed)
        assert restored == data
        record.update({'snapshot_path': str(dest), 'snapshot_bytes': len(packed), 'snapshot_sha256': hashlib.sha256(packed).hexdigest(), 'compression': 'gzip9/mtime0', 'decompressed_bytes': len(restored), 'decompressed_sha256': hashlib.sha256(restored).hexdigest()})
        doc = json.loads(data)
        selected = {'version': 1, 'baseline_commit': BASELINE, 'source_commit': doc['source_commit'], 'counts': doc['counts'], 'binding_status': doc['binding_status'], 'default_numeric_behavior_changed': doc['default_numeric_behavior_changed'], 'operator': doc['operators']['char_196_sunbr']}
        (ROOT / 'history' / 'gummy-visible-production-record.json').write_text(json.dumps(selected, ensure_ascii=False, indent=2) + '\n')
    elif ranges:
        text = data.decode('utf-8')
        lines = text.splitlines()
        excerpts = [{'first_line': first, 'last_line': last, 'text': '\n'.join(lines[first - 1:last])} for first, last in ranges]
        dest = ROOT / 'history' / (Path(rel).name + '.selected-lines.json')
        dest.write_text(json.dumps({'version': 1, **record, 'excerpts': excerpts}, ensure_ascii=False, indent=2) + '\n')
        record['snapshot_path'] = str(dest)
        record['snapshot_scope'] = 'selected line ranges; not reconstructed historical receipts'
    else:
        dest = ROOT / 'history' / Path(rel).name
        dest.write_bytes(data)
        record['snapshot_path'] = str(dest)
        record['snapshot_scope'] = 'full tracked public source at fixed baseline'
    records.append(record)
receipt = {
    'version': 1, 'baseline_commit': BASELINE, 'source_files': records,
    'visible_historical_parse_failure_lower_bound': 1,
    'visible_historical_failure': 'Back: Error: boneData cannot be null.',
    'historical_attempt_total': None,
    'historical_attempt_total_status': 'unknown; original timing-048 cache and parser logs were not migrated',
    'historical_reader_identity': None,
    'historical_reader_identity_status': 'unknown; BATCH_0.48 points to absent evidence.json, not a visible fixed reader receipt',
    'historical_cache_reconstructed': False,
    'application_calls': 0, 'full_skeleton_parser_calls': 0,
}
(ROOT / 'visible-history-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'source_files': len(records), 'visible_historical_parse_failure_lower_bound': 1, 'historical_attempt_total': None}, indent=2))
