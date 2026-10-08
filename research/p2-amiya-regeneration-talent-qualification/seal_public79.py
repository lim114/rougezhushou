"""Explicit stable public archival manifest; whole copies are excluded."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
names = ['NOTE.md', 'handoff.json', 'validation79.json', 'baseline-path.json',
    'changes79.patch', 'draft-freeze79.json', 'freeze-receipt.json', 'freeze79.py',
    'source-receipt79.json', 'collect_source79.py', 'char_patch_table.json',
    'char-patch-source-download.json', 'excluded-neighbor-leads.json',
    'amiya-regeneration-initial-public.json', 'amiya-regeneration-initial-summary.json',
    'initial-draft-diff-paths.json', 'author-first-tests79.log', 'new-and-related-tests79.log',
    'public_matrix79.py', 'compare_matrix79.py', 'public-baseline79.json.gz',
    'public-draft79.json.gz', 'matrix-comparison79.json', 'seal_public79.py', 'finalize79.py',
    'draft/rouge/operator_engine.py', 'draft/tests/test_amiya_regeneration_talent_qualification.py']
if (ROOT / 'independent').exists():
    names.extend(str(p.relative_to(ROOT)) for p in sorted((ROOT / 'independent').rglob('*')) if p.is_file())
files = []
for name in names:
    p = ROOT / name
    raw = p.read_bytes()
    files.append({'source_path': str(p), 'archive_path': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
receipt = {'format_version': 1, 'section': 79, 'status': 'FINAL_SEALED',
    'baseline_commit': '4dd778488c96864a778ccbc25c0cf11cddfa5d86',
    'public_artifacts_only': True, 'whole_source_trees_included': False,
    'manifest_self_excluded': True, 'file_count': len(files),
    'total_bytes': sum(f['bytes'] for f in files), 'files': files}
(ROOT / 'public-artifacts-manifest.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'file_count': len(files), 'total_bytes': receipt['total_bytes'],
    'manifest_sha256': hashlib.sha256((ROOT / 'public-artifacts-manifest.json').read_bytes()).hexdigest()}))
