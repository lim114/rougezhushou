"""Check frozen software statement, actual reused original selectors, transport paths."""
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-relic-warning-order-081')
freeze = json.loads((AUTHOR / 'freeze-receipt.json').read_text())
sealed = json.loads((AUTHOR / 'author-frozen-receipt.json').read_text())
hashes = {}
for relative, expected in freeze['fixed_files'].items():
    original = (AUTHOR / 'baseline' / relative).read_bytes()
    assert hashlib.sha256(original).hexdigest() == expected['sha256'] and len(original) == expected['bytes']
    if relative != 'rouge/relics.py':
        assert original == (AUTHOR / 'draft' / relative).read_bytes()
old = (AUTHOR / 'baseline/rouge/relics.py').read_bytes()
new = (AUTHOR / 'draft/rouge/relics.py').read_bytes()
before = (freeze['old_line'] + '\r\n').encode()
after = (freeze['new_line'] + '\r\n').encode()
assert old.count(before) == 1 and old.replace(before, after) == new
assert new.count(b'\r\n') == new.count(b'\n')
assert hashlib.sha256(new).hexdigest() == sealed['draft_relics_sha256']
for name, key in [('relic-warning-order-081.patch', 'patch_sha256'),
                  ('source-receipt.json', 'source_receipt_sha256'),
                  ('comparison-receipt.json', 'comparison_receipt_sha256'),
                  ('draft/tests/test_relic_warning_order.py', 'new_test_sha256')]:
    raw = (AUTHOR / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == sealed[key]
    hashes[name] = {'sha256': sealed[key], 'bytes': len(raw)}
source = json.loads((AUTHOR / 'source-receipt.json').read_text())
raw = Path(source['original_source']['path']).read_bytes()
assert hashlib.sha256(raw).hexdigest() == source['original_source']['sha256']
assert len(raw) == source['original_source']['bytes']
data = json.loads(raw)['details']['rogue_6']
model_path = AUTHOR / 'baseline/rouge/data/relic-mechanics.json'
assert hashlib.sha256(model_path.read_bytes()).hexdigest() == source['existing_mechanics_sha256']
model = json.loads(model_path.read_bytes())
for rid, row in source['selectors'].items():
    assert row['raw_relic'] == data['relics'][rid]
    assert row['raw_params'] == data['relicParams'][rid]
    assert model['relics'][rid]['raw_buffs'] == data['relics'][rid]['buffs']
    assert model['relics'][rid]['relic_params'] == data['relicParams'][rid]
    assert model['relics'][rid]['effects'] == row['existing_model_effects']
    assert all(e['stacking'] == 'unverified' for e in row['existing_model_effects'])
patch = AUTHOR / 'relic-warning-order-081.patch'
paths = subprocess.run(['git', 'apply', '--numstat', str(patch)], capture_output=True, text=True, check=True)
assert paths.stdout.splitlines() == ['1\t1\trouge/relics.py', '103\t0\ttests/test_relic_warning_order.py']
apply = subprocess.run(['git', 'apply', '--check', str(patch)], cwd=AUTHOR / 'baseline', capture_output=True, text=True)
assert apply.returncode == 0, apply.stderr
receipt = {'status': 'PASS', 'baseline_files_verified': len(freeze['fixed_files']),
           'old_draft_files_unchanged': len(freeze['fixed_files']) - 1,
           'single_CRLF_statement_only': True, 'exact_reused_original_selectors': 3,
           'numeric_and_unknown_models_unchanged': True,
           'corrected_patch_paths': paths.stdout.splitlines(), 'git_apply_check_exit_code': apply.returncode,
           'patch_preparation_error_retained_by_author': True,
           'frozen_artifacts': hashes, 'source_original': source['original_source'],
           'public_API_GUI_Wine_calls': 0, 'tracked_or_author_mutations': False}
(OUT / 'independent-source-static081.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('frozen_artifacts', 'source_original')}))
