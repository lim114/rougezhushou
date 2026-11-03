"""Copy the sealed explicit section95 plan; never infer manifests or completion."""
import hashlib
import json
import stat
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
PACK = LOCAL / 'p2-section095-focused-source-append-plan-v3'
ARCHIVE = ROOT / 'research/p2-section095-selected-module-source-report'

def check(path, row):
    assert stat.S_ISREG(path.lstat().st_mode) and path.resolve() == path, path
    data = path.read_bytes()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], path
    return data

def ref(path):
    b = path.read_bytes()
    return {'path': str(path), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == 'f509d186e501bfcfd042e45b46e398ec756840ec'
assert json.loads((ROOT / 'DEVELOPMENT_CHECKPOINT.json').read_bytes())['completed_sections'] == 94
assert not (ARCHIVE / 'archive-manifest.json').exists() and not (ROOT / 'verification/sections/095.json').exists()
for name in ('root-window-095-attempt2', 'root-saved-focused095-review'):
    assert (LOCAL / (name + '.exit-code')).read_bytes() == b'0\n'
for name in ('root-saved-focused095-review.json', 'root-focused095-visual-review.json'):
    assert json.loads((LOCAL / name).read_bytes())['passed'] is True
mf_path = PACK / 'public-artifacts-manifest-archive-append095.json'
assert ref(mf_path)['sha256'] == '07deee3ed8f90ec642473106252376c916666c2f98c1826f618f5b55c1761712'
mf = json.loads(mf_path.read_bytes())
for name, row in mf['artifacts'].items():
    assert PurePosixPath(name).name == name
    check(PACK / name, row)
plan_path = PACK / 'archive-append-plan095.json'
plan = json.loads(plan_path.read_bytes())
assert plan['section'] == 95 and plan['repository_archive_base_path'] == str(ARCHIVE)
rows = plan['files']
assert len(rows) == 271
existing = set()
names = set()
for row in rows:
    name = row['canonical_relative_archive_path']
    path = PurePosixPath(name)
    assert not path.is_absolute() and '..' not in path.parts and str(path) == name and name not in names
    names.add(name)
    source = Path(row['source_path'])
    assert source.is_relative_to(LOCAL) or source.is_relative_to(Path('/workspace/.compat'))
    check(source, row)
    target = ARCHIVE / name
    if row['root_archiver_action'] == 'skip_existing_exact':
        check(target, row)
        existing.add(name)
    else:
        assert row['root_archiver_action'] == 'append_new_exclusive_create' and not target.exists(), target
assert len(existing) == 105
assert {p.relative_to(ARCHIVE).as_posix() for p in ARCHIVE.rglob('*') if p.is_file()} == existing
assert not any(p.is_symlink() for p in ARCHIVE.rglob('*'))
for name in [*mf['artifacts'], mf_path.name, 'handoff-archive-append095.json']:
    source = PACK / name
    target = ARCHIVE / 'section095-focused-archive-append-plan-v3' / name
    assert not target.exists() and stat.S_ISREG(source.lstat().st_mode)
for row in rows:
    if row['root_archiver_action'] == 'append_new_exclusive_create':
        target = ARCHIVE / row['canonical_relative_archive_path']
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(check(Path(row['source_path']), row))
        check(target, row)
for name in [*mf['artifacts'], mf_path.name, 'handoff-archive-append095.json']:
    source = PACK / name
    target = ARCHIVE / 'section095-focused-archive-append-plan-v3' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(source.read_bytes())
    assert target.read_bytes() == source.read_bytes()
for row in rows:
    check(ARCHIVE / row['canonical_relative_archive_path'], row)
files = [p for p in ARCHIVE.rglob('*') if p.is_file()]
assert len(files) == 277
report = {'format_version': 1, 'status': 'ACTUAL_FOCUSED095_PAYLOADS_APPENDED_NOT_COMPLETED_NOT_STAGED',
          'archive': str(ARCHIVE), 'physical_files': len(files), 'all_271_plan_payloads_exact': True,
          'own_sealed_plan_files': 6, 'copied_new_payloads': 166, 'unchanged_existing_payloads': 105,
          'plan_manifest': ref(mf_path), 'source_plan': ref(plan_path), 'completed_sections': 94,
          'section095_completed': False, 'full095_available_PASS': False, 'commit_push': False}
out = LOCAL / 'root-focused-archive-prepared095.json'
with out.open('x', encoding='utf-8') as stream:
    json.dump(report, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps(report, ensure_ascii=False))
