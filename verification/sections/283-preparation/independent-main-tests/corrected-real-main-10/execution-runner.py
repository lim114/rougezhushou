"""Archive only the necessary real main-caller suite; no production writes."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
output = args.output.resolve()
assert output.is_relative_to(HERE.resolve()), 'keep raw outputs in this task cache'
output.mkdir(exist_ok=False)
test = HERE / 'test_panel_native_main_283.py'
names = ['rouge/panel_native_finalization.py', 'rouge/panel_native_precision.py', 'rouge/panel_native_bridge.py',
         'rouge/relic_attributes.py', 'rouge/damage.py', 'rouge/estimate.py', 'rouge/operator_engine.py',
         'rouge/relics.py', 'rouge/calibration.py', 'rouge/reporting.py', 'rouge/offline_tools_view.py']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {name: sha(ROOT / name) for name in names}
for name in names:
    target = output / 'source' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((ROOT / name).read_bytes())
(output / 'test-source.py').write_bytes(test.read_bytes())
(output / 'execution-runner.py').write_bytes(Path(__file__).read_bytes())
command = [sys.executable, '-X', 'utf8', str(test), '-v']
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
actual = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
finished = datetime.datetime.now(datetime.timezone.utc).isoformat()
(output / 'stdout.log').write_bytes(actual.stdout)
(output / 'stderr.log').write_bytes(actual.stderr)
stderr = actual.stderr.decode('utf8', errors='replace')
ran = re.search(r'Ran (\d+) tests? in ', stderr)
fail = re.search(r'FAILED \(([^)]+)\)', stderr)
after = {name: sha(ROOT / name) for name in names}
receipt = {'kind': 'SECTION283_INDEPENDENT_MAIN_CALLER_ACTUAL_INVOCATION',
           'command': command, 'cwd': str(ROOT), 'started_utc': started, 'finished_utc': finished,
           'actual_exit_code': actual.returncode, 'actual_tests_run': int(ran.group(1)) if ran else None,
           'actual_failure_summary': fail.group(1) if fail else None,
           'source_sha256_before': before, 'source_sha256_after': after, 'source_unchanged': before == after,
           'test_sha256': sha(test), 'stdout_sha256': hashlib.sha256(actual.stdout).hexdigest(),
           'stderr_sha256': hashlib.sha256(actual.stderr).hexdigest(),
           'independent_scope': 'main caller and calibration reuse contract; source-failure downgrade',
           'numeric_dependency_authored_by_this_reviewer': True,
           'numeric_dependency_or_parent38_or_legacy33_reaudited': False,
           'production_modified': False, 'game_or_chat_actions': 0, 'private_state_used': False,
           'status': 'pass' if actual.returncode == 0 else 'actual_failure'}
(output / 'process.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps(receipt, ensure_ascii=False)); print(stderr)
sys.exit(actual.returncode)
