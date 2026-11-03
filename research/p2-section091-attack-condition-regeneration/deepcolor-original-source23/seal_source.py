"""Seal external static lead artifacts without executing project code."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
MANIFEST = OUT / 'public-artifacts-manifest.json'
HANDOFF = OUT / 'final-handoff.json'
if MANIFEST.exists() or HANDOFF.exists():
    raise RuntimeError('The source lead is already sealed')
receipt = json.loads((OUT / 'source-receipt.json').read_text())
files = sorted(p for p in OUT.rglob('*') if p.is_file())
artifacts = []
for path in files:
    if path.is_symlink():
        raise RuntimeError('Symlink is not a public source leaf')
    rel = path.relative_to(OUT).as_posix()
    if rel.startswith('/') or any(part in ('', '.', '..') for part in Path(rel).parts):
        raise RuntimeError('Unsafe source manifest path')
    raw = path.read_bytes()
    artifacts.append({'path': rel, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
for original in receipt['source_files']:
    registered = next(item for item in artifacts if item['path'] == original['archive_path'])
    if registered['bytes'] != original['bytes'] or registered['sha256'] != original['sha256']:
        raise RuntimeError('Source leaf changed before seal')
manifest = {'schema_version': 1, 'scope': 'Future section91 merged-scope source lead only; no product draft or completed section',
            'source_baseline_commit': receipt['root_head_before'],
            'source_git_files': len(receipt['source_files']), 'artifact_count': len(artifacts),
            'artifact_bytes': sum(a['bytes'] for a in artifacts),
            'fresh_application_API_test_formatter_helper_game_parser_download_Qt_Wine_calls': 0,
            'artifacts': artifacts}
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
raw = MANIFEST.read_bytes()
handoff = {'status': 'FINAL_SOURCE_ONLY_LEAD', 'manifest': MANIFEST.name,
           'manifest_bytes': len(raw), 'manifest_sha256': hashlib.sha256(raw).hexdigest(),
           'artifact_count': len(artifacts), 'artifact_bytes': manifest['artifact_bytes'],
           'root_baseline_commit': receipt['root_head_before'],
           'root_tracked_mutations': 0, 'source13_preserved': True,
           'saved_old_real389_preserved': True, 'native_mechanism_claims_added': False,
           'future_section': 'merged into root section91; this packet does not count as a section',
           'future_validation_plan': 'future-validation-plan.json, not executed,3paired scenarios6total public API calls if root authorizes',
           'preparation_attempts': {'first_failed_ambiguous_static_anchor': 1, 'corrected_completion_passed': 1},
           'root_can_transport_only_by_hash': True}
HANDOFF.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': 'SEALED', 'manifest': str(MANIFEST), 'manifest_sha256': handoff['manifest_sha256'],
                  'manifest_bytes': len(raw), 'artifact_count': len(artifacts), 'artifact_bytes': manifest['artifact_bytes'],
                  'handoff': str(HANDOFF), 'handoff_bytes': HANDOFF.stat().st_size,
                  'handoff_sha256': hashlib.sha256(HANDOFF.read_bytes()).hexdigest()}))
