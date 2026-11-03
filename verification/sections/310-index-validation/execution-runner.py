from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, runpy, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/sections/310-index-validation'
OUT.mkdir()

def enc(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')

def read(name):
    return json.loads((ROOT / name).read_bytes())

def sha(name):
    return sha256((ROOT / name).read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

parent = '6e3ffdc262e0934f4203994a9634efb1320f4f05'
assert git('branch', '--show-current').decode().strip() == 'codex/p2-development'
assert git('rev-parse', 'HEAD').decode().strip() == parent
assert git('ls-remote', 'origin', 'refs/heads/codex/p2-development').decode().split()[0] == parent
receipt = 'verification/sections/310.json'
r = read(receipt)
argv = [sys.executable, '-B', '-X', 'utf8', '-m', 'unittest', 'tests.test_cloud_index_sync', '-q']
with (OUT / 'stdout.txt').open('xb') as stdout, (OUT / 'stderr.txt').open('xb') as stderr:
    child = subprocess.Popen(argv, cwd=ROOT, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL)
    code = child.wait()
log = (OUT / 'stderr.txt').read_text('utf8')
passed = code == 0 and 'Ran 25 tests' in log and 'OK' in log
record = {'section': 310, 'passed': passed, 'argv': argv, 'retained_popen_pid': child.pid,
          'actual_exit': code, 'tests_run': 25 if 'Ran 25 tests' in log else None,
          'observed_utc': datetime.now(timezone.utc).isoformat(),
          'script_sha256': sha('scripts/update_cloud_index.py'), 'full_rerun': False}
(OUT / 'process.json').write_bytes(enc(record))
(OUT / 'process.exit').write_text(str(code) + '\n', encoding='ascii')
(OUT / 'execution-runner.py').write_bytes(Path(__file__).read_bytes())
assert passed, log[-5000:]
r['index_validation'] = {'receipt': 'verification/sections/310-index-validation/process.json',
                         'sha256': sha('verification/sections/310-index-validation/process.json'), 'tests_run': 25}
(ROOT / receipt).write_bytes(enc(r))
runpy.run_path(str(ROOT / 'scripts/update_cloud_index.py'))['update'](ROOT)
for name in ('verification/sections/310-necessary-attempt4/process.json',
             'verification/sections/310-native-attempt4/actual/window.json',
             'verification/sections/310-source-attempt4/process.json'):
    value = read(name)
    assert value['passed'] and value['source_sha256_before'] == value['source_sha256_after']
    for member, expected in value['source_sha256_after'].items():
        assert sha(member) == expected, member
for mapping in ('source_sha256', 'validated_source_sha256'):
    for member, expected in r[mapping].items():
        assert sha(member) == expected, member
index = read('CLOUD_INDEX.json')
cp = read('DEVELOPMENT_CHECKPOINT.json')
assert cp['completed_sections'] == cp['latest_functional_section'] == 310 and cp['next_section'] == 311
assert index['current_section_label'] == '第310节 + ' + r['title']
assert index['current_completed_change'] == r['new_capability']
assert cp['policy']['wrap_up_below_usage_percent'] == 15
assert cp['policy']['development_paused_by_latest_user_request'] is False
for member, expected in index['public_pointers'].items():
    assert sha(member) == expected, member
allowed = ['AGENTS.md', 'CLOUD_HANDOFF.md', 'CLOUD_INDEX.json', 'DEVELOPMENT_CHECKPOINT.json',
           'PROJECT_COMPLETED.md', 'PROJECT_PROGRESS.md', 'PROJECT_REQUIREMENTS.md', 'WORK_IN_PROGRESS.md',
           'rouge/battle_view.py', 'rouge/boss_cycle_view.py', 'rouge/boss_cycle_reference.py',
           'rouge/data/boss-cycle-reference.json', 'scripts/build_boss_cycle_reference_310.py',
           'scripts/verify_boss_cycle_window_310.py', 'scripts/verify_full_available.py',
           'tests/test_boss_cycle_reference_310.py', 'tests/test_boss_cycle_view_310.py',
           'tests/test_boss_cycle_integration_310.py', 'research/p3-boss-cycle-310']
allowed.extend(p.relative_to(ROOT).as_posix() for p in (ROOT / 'verification/sections').glob('310*'))
subprocess.run(['git', 'add', '-f', '--', *allowed], cwd=ROOT, check=True)
check = subprocess.run(['git', '-c', 'core.whitespace=cr-at-eol', 'diff', '--cached', '--check'],
                       cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(OUT / 'git-diff-check.txt').write_bytes(check.stdout + check.stderr)
assert check.returncode == 0, (check.stdout + check.stderr).decode('utf8', errors='replace')[-6000:]
(OUT / 'public-stage-review.json').write_bytes(enc({'section': 310, 'root_reviewed': True,
    'code_and_runtime_sources_current': True, 'index_actual_exit': code, 'diff_check_exit': check.returncode,
    'parent_commit': parent, 'private_or_cache_inclusion_allowed': False,
    'full_validation_repeated': False, 'current_section_label': index['current_section_label']}))
subprocess.run(['git', 'add', '-f', '--', OUT.relative_to(ROOT).as_posix()], cwd=ROOT, check=True)
staged = git('diff', '--cached', '--name-only').decode('utf8').splitlines()
assert not any(name.startswith(('.cache/', '.local/')) or name == 'local-settings.json' for name in staged)
assert not git('diff', '--name-only').strip()
assert not git('ls-files', '--others', '--exclude-standard').strip()
subprocess.run(['git', '-c', 'core.whitespace=cr-at-eol', 'diff', '--cached', '--check'], cwd=ROOT, check=True)
print(json.dumps({'section': 310, 'staged_public_files': len(staged), 'index_checks_actual_exit': code,
                  'diff_check_exit': check.returncode, 'code_and_runtime_sources_current': True,
                  'commit_ready_not_pushed': True}, ensure_ascii=False))
