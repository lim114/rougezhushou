from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, runpy, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/sections/311-index-validation-pause'
OUT.mkdir()

def enc(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')

def read(name):
    return json.loads((ROOT / name).read_bytes())

def sha(name):
    return sha256((ROOT / name).read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

parent = '09f5ec9888342f03bbb8c8fd4b56c96e29e3d7a2'
assert git('branch', '--show-current').decode().strip() == 'codex/p2-development'
assert git('rev-parse', 'HEAD').decode().strip() == parent
assert git('ls-remote', 'origin', 'refs/heads/codex/p2-development').decode().split()[0] == parent
receipt = 'verification/sections/311.json'
r = read(receipt)
argv = [sys.executable, '-B', '-X', 'utf8', '-m', 'unittest', 'tests.test_cloud_index_sync', '-q']
with (OUT / 'stdout.txt').open('xb') as stdout, (OUT / 'stderr.txt').open('xb') as stderr:
    child = subprocess.Popen(argv, cwd=ROOT, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL)
    code = child.wait()
log = (OUT / 'stderr.txt').read_text('utf8')
passed = code == 0 and 'Ran 25 tests' in log and 'OK' in log
record = {'section': 311, 'passed': passed, 'argv': argv, 'retained_popen_pid': child.pid,
          'actual_exit': code, 'tests_run': 25 if 'Ran 25 tests' in log else None,
          'observed_utc': datetime.now(timezone.utc).isoformat(),
          'script_sha256': sha('scripts/update_cloud_index.py'), 'full_rerun': False}
(OUT / 'process.json').write_bytes(enc(record))
(OUT / 'process.exit').write_text(str(code) + '\n', encoding='ascii')
(OUT / 'execution-runner.py').write_bytes(Path(__file__).read_bytes())
assert passed, log[-5000:]
r['index_validation'] = {'receipt': 'verification/sections/311-index-validation-pause/process.json',
                         'sha256': sha('verification/sections/311-index-validation-pause/process.json'), 'tests_run': 25}
(ROOT / receipt).write_bytes(enc(r))
runpy.run_path(str(ROOT / 'scripts/update_cloud_index.py'))['update'](ROOT)
for name in ('verification/sections/311-necessary-attempt3/process.json',
             'verification/sections/311-native-attempt1/actual/window.json',
             'verification/sections/311-source-attempt3/process.json'):
    value = read(name)
    assert value['passed'] and value['source_sha256_before'] == value['source_sha256_after']
    for member, expected in value['source_sha256_after'].items():
        assert sha(member) == expected, member
for mapping in ('source_sha256', 'validated_source_sha256'):
    for member, expected in r[mapping].items():
        assert sha(member) == expected, member
index = read('CLOUD_INDEX.json')
cp = read('DEVELOPMENT_CHECKPOINT.json')
assert cp['completed_sections'] == cp['latest_functional_section'] == 311 and cp['next_section'] == 312
assert index['current_section_label'] == '第311节 + ' + r['title']
assert index['current_completed_change'] == r['new_capability']
assert cp['policy']['wrap_up_below_usage_percent'] == 15
assert cp['policy']['development_paused_by_latest_user_request'] is False
for member, expected in index['public_pointers'].items():
    assert sha(member) == expected, member
allowed = ['.gitattributes', 'AGENTS.md', 'CLOUD_HANDOFF.md', 'CLOUD_INDEX.json', 'DEVELOPMENT_CHECKPOINT.json',
           'PROJECT_COMPLETED.md', 'PROJECT_PROGRESS.md', 'PROJECT_REQUIREMENTS.md', 'WORK_IN_PROGRESS.md',
           'rouge/battle_view.py', 'rouge/boss_hunt_view.py', 'rouge/boss_hunt_reference.py',
           'rouge/data/boss-hunt-reference.json', 'scripts/build_boss_hunt_reference_311.py',
           'scripts/verify_boss_hunt_window_311.py', 'scripts/verify_full_available.py',
           'tests/test_boss_hunt_reference_311.py', 'tests/test_boss_hunt_view_311.py',
           'tests/test_boss_hunt_integration_311.py', 'research/p3-boss-hunt-311']
allowed.extend(p.relative_to(ROOT).as_posix() for p in (ROOT / 'verification/sections').glob('311*'))
subprocess.run(['git', 'add', '-f', '--', *allowed], cwd=ROOT, check=True)
check = subprocess.run(['git', '-c', 'core.whitespace=cr-at-eol', 'diff', '--cached', '--check'],
                       cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(OUT / 'git-diff-check.txt').write_bytes(check.stdout + check.stderr)
assert check.returncode == 0, (check.stdout + check.stderr).decode('utf8', errors='replace')[-6000:]
(OUT / 'public-stage-review.json').write_bytes(enc({'section': 311, 'root_reviewed': True,
    'code_and_runtime_sources_current': True, 'index_actual_exit': code, 'diff_check_exit': check.returncode,
    'parent_commit': parent, 'private_or_cache_inclusion_allowed': False,
    'full_validation_repeated': False, 'current_section_label': index['current_section_label']}))
subprocess.run(['git', 'add', '-f', '--', OUT.relative_to(ROOT).as_posix()], cwd=ROOT, check=True)
staged = git('diff', '--cached', '--name-only').decode('utf8').splitlines()
assert not any(name.startswith(('.cache/', '.local/')) or name == 'local-settings.json' for name in staged)
assert not git('diff', '--name-only').strip()
assert not git('ls-files', '--others', '--exclude-standard').strip()
subprocess.run(['git', '-c', 'core.whitespace=cr-at-eol', 'diff', '--cached', '--check'], cwd=ROOT, check=True)
print(json.dumps({'section': 311, 'staged_public_files': len(staged), 'index_checks_actual_exit': code,
                  'diff_check_exit': check.returncode, 'code_and_runtime_sources_current': True,
                  'commit_ready_not_pushed': True}, ensure_ascii=False))
