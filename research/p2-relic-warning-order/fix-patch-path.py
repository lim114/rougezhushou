import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).parent
ROOT = Path('/workspace/rougezhushou')
sha = lambda data: hashlib.sha256(data).hexdigest()
patch = OUT / 'relic-warning-order-081.patch'
original = patch.read_bytes()
freeze = OUT / 'author-frozen-receipt.json'
original_freeze = freeze.read_bytes()
with (OUT / 'relic-warning-order-081-before-path-fix.patch').open('xb') as f:
    f.write(original)
with (OUT / 'author-frozen-before-path-fix.json').open('xb') as f:
    f.write(original_freeze)
wrong = b'diff --git atests/test_relic_warning_order.py btests/test_relic_warning_order.py\n'
correct = b'diff --git a/tests/test_relic_warning_order.py b/tests/test_relic_warning_order.py\n'
assert original.count(wrong) == 1
assert original.count(b'+++ btests/test_relic_warning_order.py\n') == 1
updated = original.replace(wrong, correct).replace(b'+++ btests/test_relic_warning_order.py\n',
                                                   b'+++ b/tests/test_relic_warning_order.py\n')
patch.write_bytes(updated)
numstat = subprocess.check_output(['git', 'apply', '--numstat', str(patch)], cwd=ROOT, text=True)
paths = [line.split('\t')[-1] for line in numstat.splitlines()]
assert paths == ['rouge/relics.py', 'tests/test_relic_warning_order.py'], paths
check = subprocess.run(['git', '-c', 'core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol',
                        'apply', '--check', str(patch)], cwd=ROOT, capture_output=True, text=True)
assert check.returncode == 0, check.stderr
receipt = {'status': 'author_patch_path_preparation_corrected', 'passed': True,
           'failure': 'Initial test patch path lacked the a/ and b/ prefix separators; independent git apply --numstat rejected its intended location before root integration.',
           'attempt': 1, 'product_failure': False, 'tracked_mutation': False,
           'old_patch_sha256': sha(original), 'new_patch_sha256': sha(updated),
           'only_header_transport_paths_changed': True, 'numstat': numstat,
           'git_apply_check_passed': True, 'check_stdout': check.stdout, 'check_stderr': check.stderr,
           'root_actual_apply_executed': False, 'source_tests_matrices_rerun': False,
           'original_freeze_sha256': sha(original_freeze)}
with (OUT / 'patch-path-preparation-receipt.json').open('x', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
proof = json.loads(original_freeze)
proof['patch_sha256'] = sha(updated)
proof['patch_path_preparation_corrected'] = True
proof['patch_path_preparation_receipt_sha256'] = sha((OUT / 'patch-path-preparation-receipt.json').read_bytes())
freeze.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
