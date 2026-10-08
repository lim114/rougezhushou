import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OFFICIAL = Path('/workspace/.continuation/p2-gummy-back-parser-source087-official-reader')
MANIFEST = ROOT / 'public-artifacts-manifest087.json'
HANDOFF = ROOT / 'final-handoff087.json'
if MANIFEST.exists() or HANDOFF.exists():
    raise RuntimeError('Do not modify or overwrite a final seal')
official_manifest = OFFICIAL / 'public-artifacts-manifest087.json'
official_handoff = OFFICIAL / 'final-handoff087.json'
if not official_manifest.exists() or not official_handoff.exists():
    raise RuntimeError('Wait for the official-source independent seal before sealing the composite handoff')
files = []
for base, prefix in ((ROOT, ''), (OFFICIAL, 'official-reader/')):
    for path in sorted(base.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(base)
        if base == ROOT and (relative.parts[0] == 'git-metadata' or path in (MANIFEST, HANDOFF)):
            continue
        if '__pycache__' in relative.parts or path.name.endswith('.pyc'):
            continue
        raw = path.read_bytes()
        files.append({'source_path': str(path), 'archive_path': prefix + relative.as_posix(), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
assert len({item['archive_path'] for item in files}) == len(files)
manifest = {
    'format_version': 1, 'status': 'sealed external source operation; not a product section',
    'numbered_section': False, 'files': files, 'bytes': sum(item['bytes'] for item in files),
    'resource_files_reacquired': 2, 'full_skeleton_parser_calls': 2, 'full_skeleton_parser_failures': 0,
    'application_API_calls': 0, 'project_helper_calls': 0, 'tests': 0, 'Qt': 0, 'Wine': 0,
    'tracked_edits': 0, 'product_drafts_or_patches': 0,
    'excluded_working_metadata': 'git-metadata/ contains the new public filtered Git working objects; commit object, path listing, inventories and exact acquisition commands are archived instead',
}
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
manifest_raw = MANIFEST.read_bytes()
handoff = {
    'version': 1, 'sealed_at': datetime.now(timezone.utc).isoformat(),
    'status': 'source proven; Back readSkeletonData returned five animations; bounded reference candidates ready for root review',
    'numbered_section': False,
    'manifest': {'source_path': str(MANIFEST), 'archive_path': MANIFEST.name, 'bytes': len(manifest_raw), 'sha256': hashlib.sha256(manifest_raw).hexdigest()},
    'artifact_count': len(files), 'artifact_bytes': manifest['bytes'],
    'official_source_manifest': {'source_path': str(official_manifest), 'archive_path': 'official-reader/' + official_manifest.name, 'bytes': official_manifest.stat().st_size, 'sha256': hashlib.sha256(official_manifest.read_bytes()).hexdigest()},
    'official_source_handoff': {'source_path': str(official_handoff), 'archive_path': 'official-reader/' + official_handoff.name, 'bytes': official_handoff.stat().st_size, 'sha256': hashlib.sha256(official_handoff.read_bytes()).hexdigest()},
    'source_findings': 'source-findings087.json',
    'key_evidence': ['git-acquisition-receipt.json', 'fixed-commit-object.txt', 'fixed-two-paths-ls-tree.txt', 'header-only-receipt.json', 'parse-Front-operation.json', 'parse-Back-operation.json', 'front-control-receipt.json', 'choices-source-scope-receipt.json'],
    'source_operations': {'resource_files_reacquired': 2, 'full_official_reader_calls': 2, 'reader_failures': 0, 'Front_saved_control_records': 9, 'Back_animations': 5, 'source_conservative_candidates': 2},
    'application_and_product_operations': {'calculate_API_calls': 0, 'project_helper_calls': 0, 'formatter_calls': 0, 'tests': 0, 'Qt': 0, 'Wine': 0, 'tracked_edits': 0, 'product_drafts_or_patches': 0},
    'unknowns': ['historical reader identity/root cause/attempt total', 'final reader byte offset/EOF', 'atlas/render/geometry', 'native binding, clock, collision, ending and recovery'],
    'generic_Skill_scope': 'Literal source name Skill has no skill number and is not a skill UI choice; do not bind it to S1/S2. Attack is an optional reference, not a verified native normal attack binding.',
    'restart': 'No more source downloads or parser calls are needed. Root may start a separately authorized product stage from the sealed raw five Back animations; preserve unknowns and do not fill missing names from Front.',
}
HANDOFF.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'manifest_sha256': hashlib.sha256(manifest_raw).hexdigest(), 'handoff_sha256': hashlib.sha256(HANDOFF.read_bytes()).hexdigest(), 'files': len(files), 'bytes': manifest['bytes']}, indent=2))
