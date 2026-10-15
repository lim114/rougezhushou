"""First actual necessary284 production invocation and exact public sources."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
output = HERE / 'first-real-related-5'
output.mkdir(exist_ok=False)
paths = ['rouge/operator_engine.py', 'rouge/panel_native_bridge.py', 'tests/test_extended_skill_native_284.py',
         'rouge/panel_native_finalization.py', 'rouge/panel_native_precision.py']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {name: sha(ROOT / name) for name in paths}
for name in paths:
    target = output / 'source' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((ROOT / name).read_bytes())
(output / 'execution-runner.py').write_bytes(Path(__file__).read_bytes())
command = [sys.executable, '-X', 'utf8', '-m', 'unittest', 'tests.test_extended_skill_native_284', '-v']
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
finished = datetime.datetime.now(datetime.timezone.utc).isoformat()
(output / 'stdout.log').write_bytes(result.stdout)
(output / 'stderr.log').write_bytes(result.stderr)
stderr = result.stderr.decode('utf8', errors='replace')
ran = re.search(r'Ran (\d+) tests? in ', stderr)
fail = re.search(r'FAILED \(([^)]+)\)', stderr)
after = {name: sha(ROOT / name) for name in paths}
record = {'kind': 'SECTION284_FIRST_ACTUAL_RELATED_PRODUCTION_INVOCATION',
          'command': command, 'cwd': str(ROOT), 'started_utc': started, 'finished_utc': finished,
          'actual_exit_code': result.returncode, 'actual_tests_run': int(ran.group(1)) if ran else None,
          'raw_failure_summary': fail.group(1) if fail else None,
          'before_sha256': before, 'after_sha256': after, 'source_unchanged_during_run': before == after,
          'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(),
          'stderr_sha256': hashlib.sha256(result.stderr).hexdigest(),
          'scope': 'main actor operand capture and explicit field qualification, not independent math review',
          'legacy174_baseline_not_repeated_by_this_invocation': True,
          'parent38_or_section283_main10_not_repeated': True,
          'private_state_used': False, 'game_or_chat_actions': 0,
          'status': 'pass' if result.returncode == 0 else 'actual_failure'}
(output / 'process.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps(record, ensure_ascii=False)); print(stderr)
sys.exit(result.returncode)
