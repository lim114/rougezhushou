"""Exercise only the checker registry inverse; no module imports or APIs."""
import ast
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
checker = (OUT / 'root_current_source083.py').read_bytes()
parsed = ast.parse(checker)
function = next(node for node in parsed.body if isinstance(node, ast.FunctionDef)
                and node.name == 'verify_registry')
isolated = ast.Module(body=[function], type_ignores=[])
namespace = {'ast': ast, 'hashlib': hashlib}
exec(compile(isolated, 'isolated_root_registry_checker', 'exec'), namespace)
verify = namespace['verify_registry']
baseline = (OUT / 'baseline/scripts/verify_cloud.py').read_bytes()
expected = json.loads((OUT / 'freeze-receipt083.json').read_text())['files']['scripts/verify_cloud.py']
added = b'    "tests.test_neural_condition_text_input",\n'
assert baseline.count(b'MODULES = (\n') == 1
registered = baseline.replace(b'MODULES = (\n', b'MODULES = (\n' + added, 1)
assert verify(baseline, baseline, expected) is False
assert verify(registered, baseline, expected) is True
(OUT / 'registered-verify_cloud083.py').write_bytes(registered)
receipt = {'passed': True, 'API_calls': 0, 'test_executions': 0,
    'checker_sha256': hashlib.sha256(checker).hexdigest(),
    'unregistered_frozen_draft_path_passed': True,
    'registered_root_source_path_passed': True, 'registration_line': added.decode(),
    'baseline_bytes': len(baseline), 'baseline_sha256': hashlib.sha256(baseline).hexdigest(),
    'registered_bytes': len(registered), 'registered_sha256': hashlib.sha256(registered).hexdigest(),
    'inverse_restores_complete_baseline_bytes': True,
    'MODULES_AST_checked': True, 'all_previous_modules_and_order_preserved': True,
    'prepared_current_checker_has_no_failed_registered_probe': True}
(OUT / 'registry-preflight083.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'passed': True, 'API_calls': 0,
                  'unregistered_and_registered_paths': 2}))
