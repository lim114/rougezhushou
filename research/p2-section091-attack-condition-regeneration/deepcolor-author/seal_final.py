"""Seal new author evidence and frozen source/code without product calls."""
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = Path('/workspace/rougezhushou')
SOURCE = Path('/workspace/.continuation/future-deepcolor-s1-regeneration-note-source')
V1 = Path('/workspace/.continuation/p2-section091-deepcolor-regeneration-notes-draft')
BASE = '2cbc45f03f99ed4f04b9c7e2612b58542f909168'
MF = OUT / 'public-artifacts-manifest-final.json'
HAND = OUT / 'final-handoff.json'
if MF.exists() or HAND.exists():raise RuntimeError('Final package already sealed')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(name):return json.loads((OUT / name).read_text())
comparison = load('saved-comparison.json')
if comparison['status'] != 'SIX_PUBLIC_OUTCOMES_AND_THREE_TEXTS_PASS':raise RuntimeError('Author comparison not passed')
freeze = load('pre-execution-freeze.json')
for entry in freeze['artifacts']:
    raw = (OUT / entry['path']).read_bytes()
    if len(raw) != entry['bytes'] or sha(raw) != entry['sha256']:raise RuntimeError('Pre-execution frozen artifact drift')
bindings = load('actualroot90-source-binding.json')
immutable = []
for package, name, expected in [(SOURCE, 'public-artifacts-manifest.json', bindings['source23_original_manifest_sha256']),
                                 (V1, 'review-freeze-v1.json', bindings['v1_original_freeze_sha256'])]:
    raw = (package / name).read_bytes()
    if sha(raw) != expected:raise RuntimeError('Original package manifest drift')
    manifest = json.loads(raw)
    for entry in manifest['artifacts']:
        raw = (package / entry['path']).read_bytes()
        if len(raw) != entry['bytes'] or sha(raw) != entry['sha256']:raise RuntimeError('Original immutable source/v1 leaf drift')
    immutable.append({'package_name': package.name, 'manifest': name, 'manifest_sha256': expected,
                       'all_artifact_hashes_exact': True, 'artifact_count': manifest['artifact_count']})
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True)
if head != BASE or status:raise RuntimeError('Root actual baseline changed; stop seal and retain evidence')
receipt = {'status': 'AUTHOR_FINAL_PASS', 'actualroot90_commit': BASE,
           'author_public_API_entries': 6, 'author_explicit_formatter_entries': 3,
           'author_comparison_product_entries': 0, 'syntax_changed_files_passed': 2,
           'new_tests': 0, 'explicit_helper': 0, 'Qt': 0, 'Wine': 0, 'network': 0,
           'root_tracked_mutations': 0, 'root_head': head, 'root_clean': True,
           'original_packages_preserved': immutable,
           'numeric_HPS_fields_timelines_inverse_exact': True,
           'caller_native_JSON_and_both_source_trees_unchanged': True,
           'saved_three_draft_formatter_texts_verified': True,
           'native_tick_actual_total_lifetime_hotupdate_certified': False,
           'independent_review': 'PENDING_DIFFERENT_AGENT', 'merged_section': 91}
(OUT / 'author-final-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
artifacts = []
for path in sorted(OUT.rglob('*')):
    if path.is_file():
        if path.is_symlink():raise RuntimeError('Symlink not allowed')
        rel = path.relative_to(OUT).as_posix()
        if '__pycache__' in path.parts:raise RuntimeError('Unregistered generated Python cache')
        raw = path.read_bytes()
        artifacts.append({'path': rel, 'bytes': len(raw), 'sha256': sha(raw)})
manifest = {'schema_version': 1, 'scope': 'Section91 Deepcolor author part, independent of UI author; strict public source and saved evidence',
            'status': 'FINAL_AUTHOR_PASS_PENDING_INDEPENDENT_REVIEW', 'actualroot90_commit': BASE,
            'artifact_count': len(artifacts), 'artifact_bytes': sum(a['bytes'] for a in artifacts),
            'artifacts': artifacts}
MF.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
handoff = {'status': manifest['status'], 'manifest': MF.name, 'manifest_sha256': sha(MF.read_bytes()),
           'manifest_bytes': MF.stat().st_size, 'artifact_count': manifest['artifact_count'], 'artifact_bytes': manifest['artifact_bytes'],
           'actualroot90_commit': BASE, 'changed_tracked_candidates': ['rouge/operator_engine.py', 'rouge/reporting.py'],
           'patch': 'product-draft.patch', 'inverse': 'product-draft.inverse.patch',
           'validation_code': ['run_public.py', 'compare_saved.py'], 'new_tests': 0,
           'author_budget': {'public_API_entries': 6, 'formatter_entries': 3, 'explicit_helper': 0,
                             'Qt': 0, 'Wine': 0, 'network': 0},
           'original_source23_and_v1_immutable': True, 'product_rules_or_native_clocks_added': False,
           'root_integrates_and_window_verifies': True}
HAND.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': manifest['status'], 'manifest': str(MF), 'manifest_sha256': handoff['manifest_sha256'],
                  'manifest_bytes': MF.stat().st_size, 'artifact_count': manifest['artifact_count'],
                  'artifact_bytes': manifest['artifact_bytes'], 'handoff': str(HAND),
                  'handoff_sha256': sha(HAND.read_bytes()), 'handoff_bytes': HAND.stat().st_size}))
