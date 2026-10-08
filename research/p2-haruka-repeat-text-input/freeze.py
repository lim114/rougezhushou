import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).parent
ROOT = Path('/workspace/rougezhushou')
BASE = 'b5a40f30683bfc0945decaabbd4db5914c28427f'
files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE, 'rouge', 'tests', 'scripts'],
                                cwd=ROOT, text=True).splitlines()
files = [p for p in files if p.endswith(('.py', '.json'))]
proofs = {}
for name in files:
    data = subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT)
    path = OUT / 'frozen' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(data)
    proofs[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
receipt = {'passed': True, 'baseline_commit': BASE, 'file_count': len(files), 'files': proofs,
           'captured_git_objects_only': True, 'live_worktree_not_read_for_probes': True,
           'tracked_edits': False, 'new_api_calls': 0, 'gui_executed': False, 'wine_executed': False}
with (OUT / 'freeze-receipt.json').open('x', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'passed': True, 'file_count': len(files), 'baseline_commit': BASE}))
