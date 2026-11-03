"""Prepare public frozen source evidence; no section completion or Git staging."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import subprocess

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
PACKET = LOCAL / 'section095-static-archive-plan-v1'
ARCHIVE = ROOT / 'research/p2-section095-selected-module-source-report'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT,
                               text=True).strip() == 'codex/p2-development'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                               text=True).strip() == 'f509d186e501bfcfd042e45b46e398ec756840ec'
assert json.loads((ROOT / 'DEVELOPMENT_CHECKPOINT.json').read_bytes())['completed_sections'] == 94
guard_path = LOCAL / 'root-source-095-v2.json'
assert sha(guard_path) == '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
guard = json.loads(guard_path.read_bytes())
actual = {p.relative_to(ROOT).as_posix(): sha(p)
          for name in ('rouge', 'tests', 'scripts')
          for p in sorted((ROOT / name).rglob('*'))
          if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
assert actual == guard['source_sha256_after'] and len(actual) == 735
assert (LOCAL / 'root-window-095-v2.exit-code').read_bytes() == b'1\n'
assert json.loads(Path('/workspace/.compat/wine-module-report-window-095.json').read_bytes())['passed'] is False
mf_path = PACKET / 'public-artifacts-manifest-static-archive-plan095.json'
plan_path = PACKET / 'static-archive-plan095.json'
handoff_path = PACKET / 'handoff-static-archive-plan095.json'
assert sha(mf_path) == 'c9ee35a6671ccfb629c6cf3f027944da912a905ac0302f253005425e5206593b'
assert sha(plan_path) == 'fe6a6fe08ebe7630996667042f184f28c0789a311fd78a30146139ef23f362ee'
assert sha(handoff_path) == 'bb4bac14a3e989b04f5e7a1ddca6e2eb466e83ee0435f4274c0df295e3fedce3'
plan = json.loads(plan_path.read_bytes())
mf = json.loads(mf_path.read_bytes())
assert plan['section'] == 95 and plan['completed_section_increment'] == 0
assert len(plan['files']) == 101 and len(mf['files']) == 2
rows = plan['files'] + mf['files'] + [
    {'source_path': str(p), 'archive_relative_path': 'section095-static-archive-plan/' + p.name,
     'bytes': p.stat().st_size, 'sha256': sha(p)} for p in (mf_path, handoff_path)]
assert len(rows) == len({row['archive_relative_path'] for row in rows}) == 105
for row in rows:
    relative = PurePosixPath(row['archive_relative_path'])
    assert not relative.is_absolute() and relative.as_posix() == row['archive_relative_path']
    assert relative.parts and '..' not in relative.parts and '\\' not in row['archive_relative_path']
    source = Path(row['source_path'])
    assert source.is_absolute() and source.is_file() and not source.is_symlink()
    assert source.resolve().is_relative_to(LOCAL)
    assert source.stat().st_size == row['bytes'] and sha(source) == row['sha256']
assert not ARCHIVE.exists()
ARCHIVE.mkdir(parents=True, exist_ok=False)
for row in rows:
    source = Path(row['source_path'])
    target = ARCHIVE / row['archive_relative_path']
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(source.read_bytes())
    assert target.stat().st_size == row['bytes'] and sha(target) == row['sha256']
physical = {p.relative_to(ARCHIVE).as_posix() for p in ARCHIVE.rglob('*') if p.is_file()}
assert physical == {row['archive_relative_path'] for row in rows}
assert not (ARCHIVE / 'archive-manifest.json').exists()
assert not (ROOT / 'verification/sections/095.json').exists()
receipt = {'format_version': 1, 'status': 'PUBLIC_STATIC095_PAYLOADS_PREPARED_NOT_COMPLETED_NOT_STAGED',
           'archive_path': str(ARCHIVE), 'prepared_files': len(rows),
           'bytes': sum(row['bytes'] for row in rows), 'exact_source_payloads': True,
           'source_guard_sha256': sha(guard_path), 'original_failed_selected_retained': True,
           'actual_first_Wine_failed': True, 'section095_completed': False,
           'full095_runtime_PASS': False, 'Git_staging_commit_push': False,
           'next_action': 'Append actual source-approved attempt2/window/saved/PNG evidence; complete95 only after all required gates pass.'}
with (LOCAL / 'root-static-archive-prepared095.json').open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps(receipt, ensure_ascii=False))
