"""Seal only the authorized external changes and replayable public evidence."""
import difflib
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT.parent / 'p2-haruka-bubble-qualification-audit-after-075'
BASELINE = AUDIT / 'baseline153'
DRAFT = ROOT / 'draft'
pin = json.loads((AUDIT / 'freeze-receipt.json').read_text())
changed = []
for name, receipt in pin['frozen_source_files'].items():
    raw = (BASELINE / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == receipt['sha256']
    if (DRAFT / name).read_bytes() != raw:
        changed.append(name)
assert changed == ['rouge/operator_engine.py'], changed
old_files = set(pin['frozen_source_files'])
new_files = {str(p.relative_to(DRAFT)) for p in DRAFT.rglob('*')
             if p.is_file() and p.suffix in ('.py', '.json', '.md')} - old_files
assert new_files == {'tests/test_haruka_bubble_talent_qualification.py'}, new_files
patch = []
for name in changed:
    before, after = (BASELINE / name).read_bytes(), (DRAFT / name).read_bytes()
    assert b'\r\n' in before and after.count(b'\n') == after.count(b'\r\n')
    patch.append('diff --git a/' + name + ' b/' + name + '\n')
    patch.extend(difflib.unified_diff(before.decode().splitlines(True), after.decode().splitlines(True),
                                      fromfile='a/' + name, tofile='b/' + name))
for name in sorted(new_files):
    patch.extend(['diff --git a/' + name + ' b/' + name + '\n', 'new file mode 100644\n'])
    patch.extend(difflib.unified_diff([], (DRAFT / name).read_text().splitlines(True),
                                      fromfile='/dev/null', tofile='b/' + name))
(ROOT / 'changes.patch').write_bytes(''.join(patch).encode())
for name in ('source-receipt.json', 'initial-public-cases.json', 'freeze-receipt.json', 'collect_source.py'):
    shutil.copyfile(AUDIT / name, ROOT / name)
payload = {}
for name in changed + sorted(new_files):
    raw = (DRAFT / name).read_bytes()
    payload[name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
patch_raw = (ROOT / 'changes.patch').read_bytes()
receipt = {'baseline_commit': pin['baseline_commit'], 'baseline_path': str(BASELINE),
           'baseline_file_count': len(old_files), 'baseline_verified_against_readonly_freeze': True,
           'unchanged_old_files': len(old_files) - len(changed), 'changed_old_files': changed,
           'new_files': sorted(new_files), 'draft_files': payload,
           'patch': {'path': str(ROOT / 'changes.patch'), 'sha256': hashlib.sha256(patch_raw).hexdigest(), 'bytes': len(patch_raw)},
           'production_crlf_preserved': True, 'tracked_or_private_files_modified_by_author': False}
(ROOT / 'draft-freeze.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
