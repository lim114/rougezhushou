"""Independent byte inverse and static AST contract; no imports of product code."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
SNAP = OUT / 'snapshots'
AUTHOR = Path('/workspace/.continuation/p2-continuous-attacks-text-088-draft')
REPO = Path('/workspace/rougezhushou')
freeze = json.loads((SNAP / 'review-freeze088.json').read_bytes())
index = json.loads((SNAP / 'fixed-source-index088.json').read_bytes())
assert index['baseline_commit'] == freeze['baseline_revision']
assert len(index['files']) == index['file_count'] == 125
meta = subprocess.check_output(['git', '-C', str(REPO), 'ls-tree', '-r', index['baseline_commit'], '--', 'rouge'])
git_files = {}
for line in meta.splitlines():
    left, path = line.split(b'\t', 1)
    path = path.decode()
    if path.endswith(('.py', '.json')):
        git_files[path] = left.decode().split()[2]
assert set(git_files) == {row['path'] for row in index['files']}
changed_names = {name for name in freeze['product_and_test_files']
                 if name.startswith('rouge/') and name != 'rouge/condition_inputs.py'}
unchanged, index_bindings = [], []
for row in index['files']:
    old = (AUTHOR / 'baseline' / row['path']).read_bytes()
    assert len(old) == row['bytes'] and hashlib.sha256(old).hexdigest() == row['sha256']
    blob = hashlib.sha1(b'blob ' + str(len(old)).encode() + b'\0' + old).hexdigest()
    assert blob == row['blob'] == git_files[row['path']]
    new = (AUTHOR / 'draft' / row['path']).read_bytes()
    if row['path'] not in changed_names:
        assert new == old
        unchanged.append(row['path'])
    index_bindings.append({'path': row['path'], 'old_sha256': row['sha256'],
        'git_blob': blob, 'draft_sha256': hashlib.sha256(new).hexdigest()})
assert len(unchanged) == 119 and len(changed_names) == 6
assert {path.relative_to(AUTHOR / 'draft').as_posix()
    for path in (AUTHOR / 'draft/rouge').rglob('*') if path.is_file() and path.suffix in ('.py', '.json')} == set(git_files) | {'rouge/condition_inputs.py'}

inverses = {}
for name in changed_names:
    old = (SNAP / 'baseline-source' / name).read_bytes()
    new = (SNAP / 'product' / name).read_bytes()
    candidate = new
    nl = b'\n' if name.endswith('amiya_continuous_reference.py') else b'\r\n'
    imports = {'rouge/sp_events.py': b'from .condition_inputs import read_continuous_attacks, observe_continuous_attacks',
        'rouge/damage.py': b'from .condition_inputs import validate_continuous_attacks'}
    import_line = imports.get(name, b'from .condition_inputs import read_continuous_attacks') + nl
    assert candidate.count(import_line) == 1
    candidate = candidate.replace(import_line, b'', 1)
    replacements = []
    if name == 'rouge/operator_engine.py':
        replacements = [(b"read_continuous_attacks(self.s,active=lambda:any(r['kind']=='attack_sp' for r in self.s.get('_relic_rules',[])))", b"self.s.get('continuous_attacks',True)", 1),
            (b'read_continuous_attacks(self.s)', b"self.s.get('continuous_attacks',True)", 5)]
    elif name == 'rouge/estimate.py':
        replacements = [(b'read_continuous_attacks(scenario)', b"scenario.get('continuous_attacks',True)", 3)]
    elif name == 'rouge/timing.py':
        replacements = [(b"read_continuous_attacks(scenario,active=lambda:increment+sum(r['value'] for r in scenario.get('_relic_rules',[]) if r['kind']=='attack_sp')>0)", b"scenario.get('continuous_attacks',True)", 1)]
    elif name == 'rouge/sp_events.py':
        replacements = [(b'read_continuous_attacks(scenario, active=native_attack > 0)', b"scenario.get('continuous_attacks', True)", 1),
            (b'observe_continuous_attacks(attacks)', b'attacks', 1)]
    elif name == 'rouge/amiya_continuous_reference.py':
        replacements = [(b'read_continuous_attacks(scenario)', b"scenario.get('continuous_attacks', True)", 1)]
    else:
        replacements = [(b'@validate_continuous_attacks\r\n', b'', 1)]
    for before, after, count in replacements:
        assert candidate.count(before) == count, (name, before)
        candidate = candidate.replace(before, after)
    assert candidate == old
    assert (b'\r\n' in old) == (nl == b'\r\n')
    if nl == b'\r\n':
        assert b'\n' not in old.replace(b'\r\n', b'') and b'\n' not in new.replace(b'\r\n', b'')
    inverses[name] = {'old_sha256': hashlib.sha256(old).hexdigest(), 'new_sha256': hashlib.sha256(new).hexdigest(),
        'inverse_byte_exact': True, 'original_line_ending': nl.decode().replace('\r', 'CR').replace('\n', 'LF')}

old_reads, new_reads, placements = {}, {}, []
for name in sorted(changed_names):
    old_tree = ast.parse((SNAP / 'baseline-source' / name).read_bytes())
    new_tree = ast.parse((SNAP / 'product' / name).read_bytes())
    old_reads[name] = sum(bool(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and node.func.attr == 'get' and node.args and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == 'continuous_attacks') for node in ast.walk(old_tree))
    readers = [node for node in ast.walk(new_tree) if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name) and node.func.id == 'read_continuous_attacks']
    new_reads[name] = len(readers)
    placements.extend({'path': name, 'line': node.lineno, 'call': ast.unparse(node)} for node in readers)
assert sum(old_reads.values()) == sum(new_reads.values()) == 12
assert old_reads == new_reads
helper_tree = ast.parse((SNAP / 'product/rouge/condition_inputs.py').read_bytes())
functions = {node.name: node for node in helper_tree.body if isinstance(node, ast.FunctionDef)}
observer = functions['observe_continuous_attacks']
assert isinstance(observer.body[-1], ast.Return) and ast.unparse(observer.body[-1].value) == 'value'
assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'get'
    and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == 'continuous_attacks'
    for node in ast.walk(observer))
read = functions['read_continuous_attacks']
assert ast.unparse(read.body[0]) == "return observe_continuous_attacks(scenario.get('continuous_attacks', True), active=active)"
set_calls = [node for node in ast.walk(helper_tree) if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
    and node.func.value.id == '_pending' and node.func.attr == 'set']
assert sorted(ast.unparse(node.args[0]) for node in set_calls) == ['False', 'True']
context_call = next(node for node in ast.walk(helper_tree) if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Name) and node.func.id == 'ContextVar')
assert next(keyword.value.value for keyword in context_call.keywords if keyword.arg == 'default') is None
isolated = next(node for node in ast.walk(functions['validate_continuous_attacks'])
    if isinstance(node, ast.FunctionDef) and node.name == 'isolated')
tried = next(node for node in isolated.body if isinstance(node, ast.Try))
assert not tried.handlers and ast.unparse(tried.finalbody[0]) == '_pending.reset(token)'
assert ast.unparse(tried.body[0]) == 'result = compute(*args, **kwargs)'
assert ast.unparse(tried.body[-1]) == 'return result'
damage_tree = ast.parse((SNAP / 'product/rouge/damage.py').read_bytes())
core = next(node for node in damage_tree.body if isinstance(node, ast.FunctionDef) and node.name == '_evaluate_damage_once')
assert [ast.unparse(node) for node in core.decorator_list] == ['validate_continuous_attacks']
assert isinstance(core.body[-1], ast.Return)
sp_tree = ast.parse((SNAP / 'product/rouge/sp_events.py').read_bytes())
tail_branch = next(node for node in ast.walk(sp_tree) if isinstance(node, ast.If)
    and ast.unparse(node.test) == 'ready is not None and wait_next_attack')
assert sum(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    and node.func.id == 'observe_continuous_attacks' for node in ast.walk(tail_branch)) == 1
tests_tree = ast.parse((SNAP / 'test_continuous_attacks_text_input.py').read_bytes())
tests = [node.name for node in ast.walk(tests_tree) if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
assert len(tests) == 8
source_scope = {
    'standalone': 'Context defaultNone skips active evaluation/marking; raw identity and legacy truthiness return unchanged.',
    'core': 'False/True private state and finally.reset token; result computed through originalcore report and83–86 guards before text rejection. Existing core errors win; no allouter-phase priority claim.',
    'event_outgoing': 'Initial reader marks scopedstr only native_attack>0; original stream/wait gate unchanged.',
    'event_tail': 'Additional observer of existing raw attacks only inside original ready is not None and wait_next_attack branch; no new scenario.get, no speculative readiness/clock.',
    'event_incoming': 'native_attack0 waitFalse ignores field; waitTrue readyNone also avoids tail. Existing incoming event credit and math are byte preserved.',
    'periodic': 'Original incoming_interval is not None branch wins including0. Outgoing reader marks only positive existing increment+attack_sp rule sum; original wait-slot branch independent.',
    'Amiya': 'attach_result actually exposes attack_sp_enabled_in_reference; original early no-reference return maintained; E0/E1 reference can consume even when no attackcredit. Actual acquisition/impact/recharge/cycle fields remainNone/native bindingFalse.'}
receipt = {'status': 'PASS_STATIC_FROZEN_SOURCE_BYTE_AST_AND_SCOPE_ONLY',
    'baseline_git_commit': index['baseline_commit'], 'all125_bytes_and_actual_commit_blobs_bound': True,
    'old_draft_unchanged_files': 119, 'old_six_exact_inverses': inverses,
    'old_get_count_by_file': old_reads, 'new_reader_count_by_file': new_reads,
    'total_old_get': 12, 'total_reader': 12, 'extra_tail_observer': 1, 'extra_scenario_get': 0,
    'reader_placements': placements, 'private_context_immutable_and_reset': True,
    'standalone_raw_value_identity': True, 'test_methods_source_only': tests,
    'contract_scope': source_scope, 'git125_source_bindings': index_bindings,
    'new_calls': {'calculate_API': 0, 'production_helper': 0, 'formatter': 0, 'tests': 0,
        'network': 0, 'binary_source_parser': 0, 'Qt': 0, 'Wine': 0, 'tracked': 0},
    'static_AST_read_only': True, 'author_comparators_not_executed': True}
with (OUT / 'static-source-review088.json').open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'status': receipt['status'], 'old_source_inverse': 6, 'reads': 12,
    'tail_observer': 1, 'unchanged125_baseline_files': 119, 'new_application_calls': 0}))
