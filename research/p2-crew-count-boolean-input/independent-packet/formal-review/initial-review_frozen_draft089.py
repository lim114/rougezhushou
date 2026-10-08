"""Read frozen bytes and AST only; never import project modules or run tests."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/p2-crew-count-boolean-089-draft')
REPO = Path('/workspace/rougezhushou')
FREEZE_SHA = '04c9567954f2b7bcd34c2abe1b2b616988400d4193943e94ec4e46e32a8cc248'

def row(path):
    data = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}

freeze_path = AUTHOR / 'draft-freeze089.json'
assert row(freeze_path)['sha256'] == FREEZE_SHA
freeze = json.loads(freeze_path.read_bytes())
snapshots = OUT / 'frozen-draft-snapshots'
snapshots.mkdir(exist_ok=False)
bindings = []
for item in freeze['files'] + [freeze['section_patch'], freeze['registry_proposal']]:
    path = Path(item['source_path'])
    assert path.is_relative_to(AUTHOR)
    actual = row(path)
    assert actual == item, (actual, item)
    destination = snapshots / path.relative_to(AUTHOR)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(path.read_bytes())
    bindings.append({**actual, 'archive_path': destination.relative_to(OUT).as_posix()})
(snapshots / freeze_path.name).write_bytes(freeze_path.read_bytes())

old_path = AUTHOR / 'baseline/rouge/run_state.py'
new_path = AUTHOR / 'draft/rouge/run_state.py'
old, new = old_path.read_bytes(), new_path.read_bytes()
assert hashlib.sha256(old).hexdigest() == freeze['source_run_state_old_sha256']
needle = b"        crew=observed.get('crew_count')\r\n"
guard = b'        if isinstance(crew,bool):crew=None\r\n'
assert old.count(needle) == 1 and old.count(guard) == 0
assert new == old.replace(needle, needle + guard, 1)
assert b'\n' not in old.replace(b'\r\n', b'')
assert b'\n' not in new.replace(b'\r\n', b'')
(snapshots / 'baseline/rouge').mkdir(parents=True, exist_ok=True)
(snapshots / 'baseline/rouge/run_state.py').write_bytes(old)

old_tree, new_tree = ast.parse(old.decode()), ast.parse(new.decode())
old_apply = next(node for node in ast.walk(old_tree)
                 if isinstance(node, ast.FunctionDef) and node.name == 'apply')
new_apply = next(node for node in ast.walk(new_tree)
                 if isinstance(node, ast.FunctionDef) and node.name == 'apply')
new_guard = next(node for node in new_apply.body
                 if isinstance(node, ast.If) and node.lineno == 373)
assert ast.unparse(new_guard.test) == 'isinstance(crew, bool)'
assert len(new_guard.body) == 1 and not new_guard.orelse
assert ast.unparse(new_guard.body[0]) == 'crew = None'
new_apply.body.remove(new_guard)
assert ast.dump(old_tree, include_attributes=False) == ast.dump(new_tree, include_attributes=False)

tests_path = AUTHOR / 'draft/tests/test_run_crew_count_boolean_input.py'
tests_bytes = tests_path.read_bytes()
assert b'\r' not in tests_bytes
tests_tree = ast.parse(tests_bytes.decode())
methods = [node.name for node in ast.walk(tests_tree)
           if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
assert methods == freeze['new_test_methods'] and len(methods) == 7
test_class = next(node for node in tests_tree.body if isinstance(node, ast.ClassDef))
groups = {}
for method in test_class.body:
    if not isinstance(method, ast.FunctionDef) or not method.name.startswith('test_'):
        continue
    loops = [node for node in ast.walk(method) if isinstance(node, ast.For)]
    assert len(loops) <= 1
    groups[method.name] = len(ast.literal_eval(loops[0].iter)) if loops else 1
assert sum(groups.values()) == 12

patch = (AUTHOR / 'section89.patch').read_bytes()
expected = ''.join(difflib.unified_diff(
    old.decode().splitlines(keepends=True), new.decode().splitlines(keepends=True),
    fromfile='a/rouge/run_state.py', tofile='b/rouge/run_state.py'))
expected += ''.join(difflib.unified_diff(
    [], tests_bytes.decode().splitlines(keepends=True),
    fromfile='/dev/null', tofile='b/tests/test_run_crew_count_boolean_input.py'))
assert patch == expected.encode()
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
root_old = subprocess.check_output(['git', '-C', str(REPO), 'show', head + ':rouge/run_state.py'])
assert root_old == old
registry_proposal = json.loads((AUTHOR / 'registry-proposal.json').read_bytes())
registry = subprocess.check_output(['git', '-C', str(REPO), 'show', head + ':scripts/verify_cloud.py'])
assert hashlib.sha256(registry).hexdigest() == registry_proposal['base_sha256']
registry_patch_path = AUTHOR / 'registry-proposal.patch'
registry_patch = registry_patch_path.read_bytes()
assert row(registry_patch_path) == registry_proposal['patch']
added_module = '    "tests.test_run_crew_count_boolean_input",\n'
assert registry.count(b'MODULES = (\n') == 1
proposed = registry.replace(b'MODULES = (\n', b'MODULES = (\n' + added_module.encode(), 1)
assert hashlib.sha256(proposed).hexdigest() == registry_proposal['proposed_sha256']
assert registry_patch == ''.join(difflib.unified_diff(
    registry.decode().splitlines(keepends=True), proposed.decode().splitlines(keepends=True),
    fromfile='a/scripts/verify_cloud.py', tofile='b/scripts/verify_cloud.py')).encode()
(snapshots / 'registry-proposal.patch').write_bytes(registry_patch)
(snapshots / 'current-verify_cloud.py').write_bytes(registry)

receipt = {
    'status': 'PASS_FROZEN_DRAFT_STATIC_ONLY_FORMAL_RUNTIME_PENDING',
    'freeze': row(freeze_path), 'root_commit_at_read': head,
    'root_run_state_bytes_equal_baseline': True,
    'product_change': {'added_CRLF_lines': 1, 'removed_lines': 0,
        'literal': guard.decode().rstrip(), 'inverse_exact_bytes': True,
        'AST_inverse_exact': True, 'standalone_guard_line': 373,
        'raw_observed_unchanged': 'Guard changes only local crew; previous known state count remains; other observation fields still merge.',
        'prior_errors': 'Stale/cross-run early return and personal buff validation precede local crew read; all original code otherwise byte-identical.',
        'nonbool_scope': 'None, int0/int1, float/string and other existing nonbool behavior unchanged; actual producer remains int/None.'},
    'patch_exact_generated_transport': True,
    'registry_single_literal_inverse_exact': True,
    'tests': {'methods': methods, 'scenario_groups_static': groups, 'total_static_groups': 12,
              'runtime_calls': 0, 'author_results_not_yet_formally_imported': True},
    'bindings': bindings,
    'scope': {'RunState_constructor': 0, 'RunState_apply': 0, 'production_helper': 0,
              'damage_app_API': 0, 'formatter': 0, 'tests_executed': 0,
              'network': 0, 'Qt': 0, 'Wine': 0, 'tracked_mutations': 0, 'real_local': 0},
    'no_cross_case_UUID_or_time_normalization': True,
    'formal_remaining': 'Wait final author handoff/manifest and agreed independent fresh/test budget; current static result is not final89 product verification.'}
with (OUT / 'frozen-draft-static-review089.json').open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'status': receipt['status'], 'root_commit': head,
                  'product_lines_added': 1, 'new_test_methods': 7,
                  'test_static_groups': 12, 'application_calls': 0}, ensure_ascii=False))
