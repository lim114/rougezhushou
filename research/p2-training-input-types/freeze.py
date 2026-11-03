import datetime
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).parent
BASE = OUT / 'baseline'
DRAFT = OUT / 'draft'
assert not BASE.exists() and not DRAFT.exists(), 'Preserve existing frozen evidence.'
shutil.copytree(ROOT / 'rouge', BASE / 'rouge', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
test_names = ['test_damage.py', 'test_summon_limits_069.py', 'test_wang_token_module_reference.py',
              'test_token_manual_attributes.py', 'test_token_duration_reference.py']
(BASE / 'tests').mkdir()
for name in test_names:
    shutil.copy2(ROOT / 'tests' / name, BASE / 'tests' / name)
shutil.copytree(BASE, DRAFT)

def digest(path):
    b = path.read_bytes()
    return {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}

manifest = {str(p.relative_to(BASE)): digest(p) for p in BASE.rglob('*') if p.is_file()}
for name, entry in manifest.items():
    assert digest(ROOT / name) == entry, f'Live source changed while freezing {name}'
status = subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
receipt = {'freeze_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'baseline_head': head,
           'baseline_status': status.splitlines(), 'includes_uncommitted_section50_timing': 'rouge/timing.py' in status,
           'source_root': str(ROOT), 'frozen_root': str(BASE), 'draft_root': str(DRAFT),
           'frozen_files': manifest, 'new_validation_required_after_tmp_loss': True,
           'old_tmp_receipts_reused_as_new_runs': False}
(OUT / 'baseline-freeze.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'head': head, 'status': status.splitlines(), 'frozen_files': len(manifest)}, ensure_ascii=False))
