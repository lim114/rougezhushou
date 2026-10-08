"""Build an explicit archival list without full checkouts or runtime artifacts."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
names = [
    'NOTE.md', 'handoff.json', 'baseline-path.json', 'changes.patch', 'draft-freeze.json',
    'source-receipt.json', 'collect_source.py', 'freeze-receipt.json', 'initial-public-cases.json',
    'new-and-related-tests.log', 'validation.json', 'public_matrix.py', 'compare_matrix.py',
    'public-baseline.json.gz', 'public-draft.json.gz', 'matrix-comparison.json',
    'freeze_artifacts.py', 'seal_public.py', 'finalize_artifacts.py', 'draft/rouge/operator_engine.py',
    'draft/tests/test_haruka_bubble_talent_qualification.py',
]
if (ROOT / 'independent').exists():
    names.extend(str(p.relative_to(ROOT)) for p in sorted((ROOT / 'independent').rglob('*'))
                 if p.is_file())
files = []
for name in names:
    path = ROOT / name
    raw = path.read_bytes()
    files.append({'source_path': str(path), 'archive_path': name,
                  'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
receipt = {'format_version': 1, 'section': 76, 'status': 'FINAL_SEALED',
           'baseline_commit': '153b5dbf15d6567746047cbdea7f8d00a6879f3a',
           'public_artifacts_only': True, 'full_checkouts_included': False,
           'manifest_self_excluded': True, 'file_count': len(files),
           'total_bytes': sum(v['bytes'] for v in files), 'files': files}
(ROOT / 'public-artifacts-manifest.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'file_count': receipt['file_count'], 'total_bytes': receipt['total_bytes'],
                  'manifest_sha256': hashlib.sha256((ROOT / 'public-artifacts-manifest.json').read_bytes()).hexdigest()}))
