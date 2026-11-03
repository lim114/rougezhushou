"""Capture one fixed Git bridge; never import or call prepare_run/resolve_enemy."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-after086-finite-input-source')
ROOT = Path('/workspace/rougezhushou')
BASE = '2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'
name = 'rouge/run_modifiers.py'
raw = subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT)
text = raw.decode().replace('\r\n', '\n')
function = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == 'prepare_run')
assert ast.unparse(function.body[-2]) == 'resolve_enemy(scenario, resolution)'
assert ast.unparse(function.body[-1]) == 'return (scenario, resolution)'
assert any(isinstance(n, ast.ImportFrom) and n.module == 'enemy_environment'
    and any(a.name == 'resolve_enemy' for a in n.names) for n in function.body)
guards = json.loads((AUTHOR / 'guard-function-excerpts.json').read_bytes())
prepare = next(n for n in guards if n['source_path'] == 'rouge/damage.py' and n['function'] == '_prepare_damage')
tree = ast.parse(prepare['source'])
calls = [(n.func.id, n.lineno) for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
positions = {name: min(line for call, line in calls if call == name)
    for name in ('operator_attributes', 'prepare_run', 'resolve_relics', 'prepare_attribute_runes')}
assert positions['operator_attributes'] < positions['prepare_run'] < positions['resolve_relics'] < positions['prepare_attribute_runes']
receipt = {'status': 'PASS_STATIC_FIXED_RUN_BRIDGE', 'fixed_commit': BASE, 'git_path': name,
    'whole_git_blob_sha256': hashlib.sha256(raw).hexdigest(), 'whole_git_blob_bytes': len(raw),
    'git_blob': subprocess.check_output(['git', 'rev-parse', BASE + ':' + name], cwd=ROOT, text=True).strip(),
    'function': 'prepare_run', 'line': function.lineno, 'end_line': function.end_lineno,
    'source': ast.get_source_segment(text, function),
    'prepare_damage_local_call_lines_relative_to_excerpt': positions,
    'bridge_evidence': 'Public preparation calls prepare_run before relic/rune/engine evaluation; prepare_run calls resolve_enemy on copied scenario then returns that same scenario for later numeric guards.',
    'condition_boundary': 'resolve_enemy target identity branch and ignored manual-field policy remain those in archived fixed enemy_environment.py. No full runtime or fresh identity/numeric combinations executed.',
    'new_API_project_helpers_tests_Qt_Wine_tracked': 0}
(OUT / 'run-preparation-bridge085.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in receipt.items() if k != 'source'}, ensure_ascii=False))
