"""Bind an external Deepcolor draft to the actual completed root90 baseline."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
SOURCE = Path('/workspace/.continuation/future-deepcolor-s1-regeneration-note-source')
V1 = Path('/workspace/.continuation/p2-section091-deepcolor-regeneration-notes-draft')
BASE = '2cbc45f03f99ed4f04b9c7e2612b58542f909168'
SOURCE_HASH = '706ed3f8242bed04909778ed15dc582b486e7479b96ae2cbf6c9a4074c012389'
V1_HASH = 'f99f02f82e19961cbb16d7d18f45eaabf1c0d74c84a70f85274faec2a8a88b78'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def write_json(name, value):
    p = OUT / name
    if p.exists():
        raise RuntimeError('Existing author artifact: ' + name)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

head = git('rev-parse', 'HEAD').decode().strip()
if head != BASE or git('status', '--porcelain') or git('branch', '--show-current').decode().strip() != 'codex/p2-development':
    raise RuntimeError('Actual root90 baseline not exact/clean/on authorized branch')
source_raw = (SOURCE / 'public-artifacts-manifest.json').read_bytes()
v1_raw = (V1 / 'review-freeze-v1.json').read_bytes()
if sha(source_raw) != SOURCE_HASH or sha(v1_raw) != V1_HASH:
    raise RuntimeError('Immutable source/v1 manifest drift')
source = json.loads(source_raw)
v1 = json.loads(v1_raw)
for package, manifest in ((SOURCE, source), (V1, v1)):
    for entry in manifest['artifacts']:
        raw = (package / entry['path']).read_bytes()
        if len(raw) != entry['bytes'] or sha(raw) != entry['sha256']:
            raise RuntimeError('Immutable package leaf drift: ' + entry['path'])

paths = [p for p in git('ls-tree', '-r', '--name-only', BASE, 'rouge').decode().splitlines()
         if p.endswith(('.py', '.json'))]
if not paths:
    raise RuntimeError('No actual public calculation source files')
source_entries = []
for rel in paths:
    raw = git('show', BASE + ':' + rel)
    if raw != (ROOT / rel).read_bytes():
        raise RuntimeError('Root source changed during transport: ' + rel)
    for tree in ('baseline-tree', 'draft-tree'):
        target = OUT / tree / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise RuntimeError('Existing author tree leaf: ' + str(target))
        target.write_bytes(raw)
    source_entries.append({'repository_path': rel, 'bytes': len(raw), 'sha256': sha(raw),
                           'git_blob': git('rev-parse', BASE + ':' + rel).decode().strip()})

changed = ('rouge/operator_engine.py', 'rouge/reporting.py')
bindings = []
for rel in changed:
    baseline = (OUT / 'baseline-tree' / rel).read_bytes()
    if baseline != (V1 / 'baseline' / rel).read_bytes():
        raise RuntimeError('V1 draft input differs from actualroot90: ' + rel)
    drafted = (V1 / 'draft' / rel).read_bytes()
    (OUT / 'draft-tree' / rel).write_bytes(drafted)
    ast.parse(drafted.decode())
    bindings.append({'repository_path': rel, 'actualroot90_baseline_bytes': len(baseline),
                     'actualroot90_baseline_sha256': sha(baseline),
                     'v1_source_baseline_equals_actualroot90': True,
                     'draft_bytes': len(drafted), 'draft_sha256': sha(drafted),
                     'syntax': 'AST_PARSE_PASS'})
for name in ('product-draft.patch', 'product-draft.inverse.patch'):
    shutil.copyfile(V1 / name, OUT / name)
for name, raw in [('source23-manifest.json', source_raw), ('unexecuted-v1-freeze.json', v1_raw)]:
    (OUT / name).write_bytes(raw)
shutil.copyfile(SOURCE / 'future-validation-plan.json', OUT / 'validation-plan.json')
write_json('actualroot90-source-binding.json', {
    'status': 'ACTUALROOT90_SOURCE_TRANSPORT_PASS', 'actualroot90_commit': BASE,
    'root_branch': 'codex/p2-development', 'source23_original_manifest_sha256': SOURCE_HASH,
    'source23_original_immutable': True, 'v1_original_freeze_sha256': V1_HASH,
    'v1_original_immutable': True, 'calculation_dependency_git_files': len(source_entries),
    'source_entries': source_entries, 'product_changes': bindings,
    'other_dependency_files_exact': len(source_entries) - len(changed),
    'root_head_after_transport': git('rev-parse', 'HEAD').decode().strip(),
    'root_status_after_transport': git('status', '--porcelain').decode(),
    'root_tracked_mutations': 0, 'product_API_executed_yet': 0,
    'syntax_changed_source_files_passed': 2, 'new_test_files': 0,
    'native_clock_presence_lifetime_hotupdate_claims': 0,
})
pre = []
for p in sorted(OUT.rglob('*')):
    if p.is_file():
        raw = p.read_bytes()
        pre.append({'path': p.relative_to(OUT).as_posix(), 'bytes': len(raw), 'sha256': sha(raw)})
write_json('pre-execution-freeze.json', {
    'status': 'FROZEN_BEFORE_SIX_PUBLIC_API_ENTRIES', 'actualroot90_commit': BASE,
    'artifact_count': len(pre), 'artifact_bytes': sum(x['bytes'] for x in pre), 'artifacts': pre,
    'budget': {'baseline_public_API': 3, 'draft_public_API': 3, 'total_public_API': 6,
               'draft_formatter': 3, 'baseline_formatter': 0, 'new_tests': 0},
    'unknown_native_regeneration_actual_total': True,
})
print(json.dumps({'status': 'BOUND_AND_FROZEN_BEFORE_EXECUTION', 'actualroot90': BASE,
                  'calculation_git_files': len(source_entries), 'product_changed_files': 2,
                  'syntax_files_passed': 2, 'public_API_yet': 0}))
