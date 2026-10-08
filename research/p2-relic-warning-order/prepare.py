import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).parent
BASE = '9b7cfba08319d64175a7f51a94f339ce225bc76c'
files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE, 'rouge', 'tests', 'scripts'], cwd=ROOT, text=True).splitlines()
files = [p for p in files if p.endswith(('.py', '.json'))]
proof = {}
for path in files:
    data = subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
    for tree in ['baseline', 'draft']:
        dest = OUT / tree / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('xb') as f:
            f.write(data)
    proof[path] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
engine = OUT / 'draft/rouge/relics.py'
old = engine.read_bytes()
old_line = b"    for group in {r.get('group') for r in candidates if r.get('stacking')=='unverified'}:\r\n"
new_line = b"    for group in dict.fromkeys(r.get('group') for r in candidates if r.get('stacking')=='unverified'):\r\n"
assert old.count(old_line) == 1
assert old.count(b'\r\n') == old.count(b'\n')
new = old.replace(old_line, new_line)
engine.write_bytes(new)
patch = subprocess.run(['git', 'diff', '--no-index', '--', str(OUT / 'baseline/rouge/relics.py'), str(engine)], stdout=subprocess.PIPE, check=False)
assert patch.returncode == 1
with (OUT / 'relic-warning-order-081.patch').open('xb') as f:
    f.write(patch.stdout.replace(str(OUT / 'baseline/').encode(), b'').replace(str(OUT / 'draft/').encode(), b''))
receipt = {'passed': True, 'baseline_commit': BASE, 'fixed_files': proof,
           'file_count': len(proof), 'changed_file': 'rouge/relics.py',
           'old_sha256': hashlib.sha256(old).hexdigest(), 'new_sha256': hashlib.sha256(new).hexdigest(),
           'old_line': old_line.decode().rstrip(), 'new_line': new_line.decode().rstrip(),
           'crlf_preserved': new.count(b'\r\n') == new.count(b'\n'),
           'source_080_matrices_untouched': True, 'tracked_edits': False}
with (OUT / 'freeze-receipt.json').open('x', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'passed': True, 'file_count': len(proof), 'old_sha256': receipt['old_sha256'],
                  'new_sha256': receipt['new_sha256']}))
