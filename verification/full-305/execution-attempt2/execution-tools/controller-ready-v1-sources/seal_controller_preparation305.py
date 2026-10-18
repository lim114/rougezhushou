"""Seal static/cache tool preparation; no source freeze, activation or tests."""
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys
from full305_common import BASE, ROOT, public, sha, write_new
from activate_full305 import replace_assignment, preservation


def pin(path): return {'sha256': sha(path), 'bytes': path.stat().st_size}


def main():
    if (BASE / 'CONTROLLER_READY.json').exists(): raise FileExistsError('Preserve frozen preparation READY; use a reviewed new revision.')
    checks = []
    def require(value, label):
        if not value: raise ValueError(label)
        checks.append(label)
    prepared = json.loads((BASE / 'prepared-inputs-final.json').read_bytes())
    path = BASE / 'candidate/scripts/verify_full_available.py'
    api = {'__file__': str(ROOT / 'scripts/verify_full_available.py'), '__name__': '_305_maintained_selector_API_only'}
    sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT)]
    exec(compile(path.read_bytes(), str(path), 'exec'), api)
    selectors = api['maintained_selectors']()
    original = json.loads(public('verification/full-290/source-freeze-final-A3.json').read_bytes())['selectors']
    require(selectors[:len(original)] == original and len(original) == 430, 'Complete original430 ordered selector prefix')
    require(len(selectors) == len(set(selectors)), 'No selector duplication')
    actual_new = sorted('tests.' + file.stem for file in (ROOT / 'tests').glob('test_*.py')
                        if file.relative_to(ROOT).as_posix() not in json.loads(public('verification/full-290/source-freeze-final-A3.json').read_bytes())['source_sha256'])
    require(all(module in selectors for module in actual_new), 'Every actually present post290 module including305 included')
    require(all(module in selectors for module in ('tests.test_relic_exchange_flow_305', 'tests.test_relic_exchange_flow_view_305')), 'Exact two305 modules')
    for mode, entries in prepared['template_bundle_sha256'].items():
        require(len(entries) == (84 if mode == 'legacy' else 18), 'Complete original' + mode + ' tool map')
        require(all(sha(BASE / ('template-' + mode) / name) == value for name, value in entries.items()), 'Exact original' + mode + ' tool bytes')
    for name in ('verify_direct_map_window_294', 'verify_curiosity_node_rules_window_304'):
        before = ast.parse(public('scripts/' + name + '.py').read_bytes())
        after = ast.parse((BASE / 'candidate/scripts' / (name + '_full305.py')).read_bytes())
        def assertions(tree): return [ast.dump(node, include_attributes=False) for node in sorted((node for node in ast.walk(tree) if isinstance(node, ast.Assert)), key=lambda node: (node.lineno, node.col_offset))]
        def requires(tree): return [ast.dump(node, include_attributes=False) for node in sorted((node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'require'), key=lambda node: (node.lineno, node.col_offset))]
        require(assertions(before) == assertions(after), name + ' all original Assert AST/order')
        require(requires(before) == requires(after), name + ' all original require calls/order')
    before = (BASE / 'template-legacy/window.py').read_bytes()
    after = replace_assignment(replace_assignment(before, '_SOURCE125_GUARD_SHA256', '0' * 64), '_SOURCE125_MAINTAINED_COUNT', 99999)
    proof = preservation(before, after, {'_SOURCE125_GUARD_SHA256', '_SOURCE125_MAINTAINED_COUNT'})
    require(proof['assert_AST_count'] == 862, 'Bound legacy preserves all862 and every nonbinding AST')
    text = after.decode('utf8'); tree = ast.parse(text)
    bodies = [node for node in tree.body if isinstance(node, ast.Try) and sum(isinstance(item, ast.Assert) for item in ast.walk(node)) == 552]
    require(len(bodies) == 1 and sha256(ast.get_source_segment(text, bodies[0]).encode('utf8')).hexdigest() == '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922', 'Exact original552 physical main body')
    static = json.loads((BASE / 'template-legacy/static-preservation.json').read_bytes())
    for name, expected in static['case_function_raw_sha256'].items():
        node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
        require(sha256(ast.get_source_segment(text, node).encode('utf8')).hexdigest() == expected, 'Original generator' + name)
    for name in ('window.py', 'window29.py'):
        raw = (BASE / 'template-current' / name).read_bytes()
        require(preservation(raw, replace_assignment(raw, 'FREEZE_SHA256', '0' * 64), {'FREEZE_SHA256'})['all_nonbinding_AST_identical'], 'Current' + name + ' all nonbinding AST')
    require(sha(BASE / 'supervisor305.py') == 'b073d86b1ddb6d697278380e34b29fd3887a8ea14448f29ffd8a8852dc4b2309', 'Exact actual successful mature owned supervisor')
    parses = {}
    for path in sorted([*BASE.glob('*.py'), *(BASE / 'candidate/scripts').glob('*.py')]):
        ast.parse(path.read_bytes(), filename=str(path)); parses[path.relative_to(BASE).as_posix()] = pin(path)
    require(len(parses) >= 15, 'All current controller/candidate Python statically parsed')
    report = {'section': 305, 'kind': 'STATIC_PREPARATION_ONLY_NO_TEST_OR_NATIVE_EXECUTION', 'checks': checks,
        'actual_static_checks': len(checks), 'actual_selector_API_count': len(selectors), 'original_prefix_count': len(original),
        'actual_added_modules': selectors[len(original):], 'parsed_sources': parses,
        'legacy_raw_labels_and_original_auditor_preserved': True, 'preparation_first_scope_preflight_exit1_due_unpromoted_canonical_adapters_not_product_failure': True,
        'no_source_freeze_activation_suite_or_Qt_window_execution': True,
        'root_still_must_promote_reviewed_maintenance_candidates_then_declare_actual_source': True}
    write_new(BASE / 'controller-static-preparation.json', report)
    names = set(parses)
    names.update(['PLAN.json', 'READY.json', 'prepared-inputs.json', 'prepared-inputs-final.json', 'environment-inventory.json',
        'legacy-static-preservation.json', 'controller-static-preparation.json', 'selected-source-contract-preflight.json',
        'maintained-runner.diff', 'maintained-runner-final.diff', 'native294-adaptation.diff', 'native304-adaptation.diff',
        'wsl-list.stderr.bin', 'wsl-list.stdout.bin', 'RUN_PLAN.md', 'SOURCE_AND_RECEIPT_SCHEMA.md', 'README.md',
        'final-static-source-preparation.json', 'PREPARATION_NOTES.md'])
    for mode, entries in prepared['template_bundle_sha256'].items(): names.update('template-' + mode + '/' + name for name in entries)
    # Keep the exact first unsealed draft and its first467 candidate as historical
    # preparation evidence; it was never activated/executed and cannot be used.
    names.update(path.relative_to(BASE).as_posix() for path in (BASE / 'first-unsealed-controller-draft').rglob('*') if path.is_file())
    files = {name: pin(BASE / name) for name in sorted(names)}
    ready = {'section': 305, 'kind': 'FULL305_CONTROLLER_CACHE_READY_NOT_EXECUTED', 'files': files,
        'actual_current_selector_API_count': len(selectors), 'native_component_count_after305_root_binding': 20,
        'public_promote_candidates': prepared['public_promote_candidates'],
        'entrypoints': {'declare': 'declare_freeze305.py', 'activate': 'activate_full305.py',
            'execute_explicit_only': 'run_full305_controller.py', 'archive': 'archive_full305.py'},
        'source_receipt_contract': 'SOURCE_AND_RECEIPT_SCHEMA.md', 'run_plan': 'RUN_PLAN.md',
        'runtime_execution_or_source_freeze_started': False, 'actual_full305_available_checks_passed': None,
        'Linux_WSL_Wine_private_original_Windows_verified': False,
        'owned_job_empty_claim_scope': 'actual assigned Job only; Popen-before-Assign startup race retained and disclosed',
        'global_mutex_or_automatic_retries_claimed': False}
    write_new(BASE / 'CONTROLLER_READY.json', ready)
    print(json.dumps({'controller_ready_sha256': sha(BASE / 'CONTROLLER_READY.json'), 'files': len(files),
                      'actual_selectors': len(selectors), 'static_checks': len(checks), 'full_tests_or_Qt_started': False}, ensure_ascii=False))


if __name__ == '__main__': main()
