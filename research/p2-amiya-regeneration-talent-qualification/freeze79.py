"""Verify frozen base bytes and seal only the authorized external two files."""
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'p2-after-076-condition-eligibility-audit' / 'baseline4dd'
DRAFT = ROOT / 'draft'
pin = json.loads((ROOT / 'freeze-receipt.json').read_text())
changed = []
for name, record in pin['frozen_source_files'].items():
    raw = (BASE / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record['sha256']
    if (DRAFT / name).read_bytes() != raw:
        changed.append(name)
assert changed == ['rouge/operator_engine.py'], changed
new = {str(p.relative_to(DRAFT)) for p in DRAFT.rglob('*') if p.is_file()
       and p.suffix in ('.py', '.json', '.md')} - set(pin['frozen_source_files'])
assert new == {'tests/test_amiya_regeneration_talent_qualification.py'}
patch = []
for name in changed:
    a, b = (BASE / name).read_bytes(), (DRAFT / name).read_bytes()
    assert a.count(b'\n') == a.count(b'\r\n') and b.count(b'\n') == b.count(b'\r\n')
    patch.append('diff --git a/' + name + ' b/' + name + '\n')
    patch.extend(difflib.unified_diff(a.decode().splitlines(True), b.decode().splitlines(True),
        fromfile='a/' + name, tofile='b/' + name))
for name in sorted(new):
    patch.extend(['diff --git a/' + name + ' b/' + name + '\n', 'new file mode 100644\n'])
    patch.extend(difflib.unified_diff([], (DRAFT / name).read_text().splitlines(True),
        fromfile='/dev/null', tofile='b/' + name))
(ROOT / 'changes79.patch').write_bytes(''.join(patch).encode())
files = {}
for name in changed + sorted(new):
    raw = (DRAFT / name).read_bytes()
    files[name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
raw = (ROOT / 'changes79.patch').read_bytes()
receipt = {'baseline_commit': pin['baseline_commit'], 'baseline_file_count': len(pin['frozen_source_files']),
    'baseline_path': str(BASE), 'unchanged_old_files': len(pin['frozen_source_files']) - len(changed),
    'changed_old_files': changed, 'new_files': sorted(new), 'draft_files': files,
    'patch': {'source_path': str(ROOT / 'changes79.patch'), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)},
    'old_source_crlf_preserved': True, 'author_tracked_mutations': False}
(ROOT / 'draft-freeze79.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
