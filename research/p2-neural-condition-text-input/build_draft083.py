"""Freeze a public committed package and apply only the scoped text guard."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
COMMIT = 'b5a40f30683bfc0945decaabbd4db5914c28427f'
INITIAL = 'ea7866be6f2a8e89d382ec2982a45f1cb9231141'
old_receipt = OUT / 'freeze-receipt083.json'
if json.loads(old_receipt.read_text())['baseline_commit'] == INITIAL:
    shutil.copy2(old_receipt, OUT / 'initial-ea786-freeze-receipt083.json')
    shutil.copy2(OUT / 'baseline/rouge/operator_engine.py', OUT / 'initial-ea786-operator_engine.py')
files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', COMMIT],
                                cwd=REPO, text=True).splitlines()
rows = {}
for name in files:
    path = Path(name)
    if path.parts[0] not in ('rouge', 'tests', 'scripts') or path.suffix not in ('.py', '.json'):
        continue
    data = subprocess.check_output(['git', 'show', f'{COMMIT}:{name}'], cwd=REPO)
    destination = OUT / 'baseline' / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    rows[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
shutil.copytree(OUT / 'baseline', OUT / 'draft', dirs_exist_ok=True)
old_receipt.write_text(json.dumps({'baseline_commit': COMMIT, 'files': rows,
    'tracked_edits': False, 'API_calls': 0}, indent=2) + '\n')
path = OUT / 'draft/rouge/damage.py'
data = path.read_bytes()
before = b"    result['report']=build_report(scenario,result)\r\n    return result\r\n\r\ndef _evaluate_damage(prepared,wine_phase=None)"
after = b"    result['report']=build_report(scenario,result)\r\n" + (
    b"    # Validate the processed neural scenario after preserving legacy errors.\r\n"
    b"    if scenario['operator'] in ('char_1042_phatm2','char_4204_mantra'):\r\n"
    b"        for field in ('enemy_is_boss','enemy_in_neural_break'):\r\n"
    b"            if isinstance(scenario.get(field),str):\r\n"
    + "                raise ValueError(field+' 不接受文本条件；请使用布尔值。')\r\n".encode('utf-8')
    + b"    return result\r\n\r\ndef _evaluate_damage(prepared,wine_phase=None)"
)
assert data.count(before) == 1
updated = data.replace(before, after)
assert updated.count(b'\n') == updated.count(b'\r\n')
path.write_bytes(updated)
assert (OUT / 'baseline/rouge/operator_engine.py').read_bytes() == (OUT / 'draft/rouge/operator_engine.py').read_bytes()
initial_engine = (OUT / 'initial-ea786-operator_engine.py').read_bytes()
engine = (OUT / 'baseline/rouge/operator_engine.py').read_bytes()
addition = ("            if '微创治疗' in self.tv and isinstance(self.s.get('low_cost_healing_target'),str):\r\n"
            "                raise ValueError('low_cost_healing_target 不接受文本条件；请使用布尔值。')\r\n").encode('utf-8')
# Record the whole committed diff so that the independent old probes need no rerun.
commit_diff = subprocess.check_output(['git', 'diff', INITIAL, COMMIT, '--', 'rouge/operator_engine.py'], cwd=REPO)
(OUT / 'baseline-transition082.patch').write_bytes(commit_diff)
same = []
for name in ('rouge/damage.py', 'rouge/operator_options.py', 'rouge/enemy_environment.py', 'rouge/data/catalog.json'):
    original = subprocess.check_output(['git', 'show', f'{INITIAL}:{name}'], cwd=REPO)
    assert original == (OUT / 'baseline' / name).read_bytes()
    same.append(name)
(OUT / 'draft-freeze083.json').write_text(json.dumps({'baseline_commit': COMMIT,
    'old_probe_commit': INITIAL, 'unchanged_old_probe_files': same,
    'transition_engine_diff_path': 'baseline-transition082.patch',
    'production_changed_files': ['rouge/damage.py'], 'source_threshold_clock_changes': False,
    'baseline_engine_sha256': hashlib.sha256(engine).hexdigest(),
    'draft_damage_sha256': hashlib.sha256(updated).hexdigest(),
    'API_calls': 0}, indent=2) + '\n')
print(json.dumps({'passed': True, 'baseline_commit': COMMIT,
                  'public_source_files': len(rows), 'guard_lines': 5, 'API_calls': 0}))
