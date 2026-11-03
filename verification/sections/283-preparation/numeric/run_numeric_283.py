"""Archive the first actual numeric preparation invocation and exact inputs."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
output = HERE / 'first-real-numeric'
output.mkdir(exist_ok=False)
test = HERE / 'verify_numeric_283.py'
core = HERE / 'rouge/panel_native_precision.py'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {'test': sha(test), 'core': sha(core)}
for path, name in [(test, 'test-source.py'), (core, 'core-source.py'),
                   (Path(__file__), 'execution-runner.py')]:
    (output / name).write_bytes(path.read_bytes())
command = [sys.executable, '-X', 'utf8', str(test)]
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
actual = subprocess.run(command, cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
finished = datetime.datetime.now(datetime.timezone.utc).isoformat()
(output / 'stdout.log').write_bytes(actual.stdout)
(output / 'stderr.log').write_bytes(actual.stderr)
result = {'kind': 'SECTION283_NUMERIC_PREPARATION_ACTUAL_INVOCATION',
          'command': command, 'cwd': str(HERE), 'started_utc': started, 'finished_utc': finished,
          'actual_exit_code': actual.returncode,
          'test_and_core_sha256_before': before,
          'test_and_core_sha256_after': {'test': sha(test), 'core': sha(core)},
          'test_and_core_unchanged': before == {'test': sha(test), 'core': sha(core)},
          'stdout_sha256': hashlib.sha256(actual.stdout).hexdigest(),
          'stderr_sha256': hashlib.sha256(actual.stderr).hexdigest(),
          'is_final_independent_test_or_production_acceptance': False,
          'game_or_chat_actions': 0, 'private_state_used': False}
(output / 'process.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps(result, ensure_ascii=False))
print(actual.stderr.decode('utf8', errors='replace'))
sys.exit(actual.returncode)
