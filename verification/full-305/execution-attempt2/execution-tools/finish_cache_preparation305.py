"""Static/cache source preparation only. Never imports a test or constructs Qt."""
import ast
import difflib
import json
from pathlib import Path
from hashlib import sha256

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def pin(path):
    raw = path.read_bytes(); return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


def new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')
    with path.open('xb') as stream: stream.write(raw)


def main():
    target = BASE / 'candidate/scripts/verify_full_available.py'
    old = target.read_text(encoding='utf8'); tree = ast.parse(old)
    node = next(node for node in tree.body if isinstance(node, ast.Assign)
                and any(isinstance(value, ast.Name) and value.id == 'ADDITIONAL_MODULES' for value in node.targets))
    old_modules = list(ast.literal_eval(node.value))
    additions = ['tests.test_relic_exchange_flow_305', 'tests.test_relic_exchange_flow_view_305']
    if any(module in old_modules for module in additions): raise ValueError('First final preparation only; do not repeat or overwrite.')
    modules = old_modules + additions
    lines = old.splitlines(keepends=True)
    lines[node.lineno - 1:node.end_lineno] = ['ADDITIONAL_MODULES = ' + repr(tuple(modules)) + '\n']
    candidate = ''.join(lines)
    target.write_bytes(candidate.encode('utf8'))
    with (BASE / 'maintained-runner-final.diff').open('x', encoding='utf8') as stream:
        original = (ROOT / 'scripts/verify_full_available.py').read_text(encoding='utf8')
        stream.write(''.join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True), fromfile='actual-old-maintained', tofile='candidate-final305')))
    original_tree = ast.parse(original); final_tree = ast.parse(candidate)
    def named(tree, name): return next(node for node in tree.body if getattr(node, 'name', None) == name)
    def ast_equal(name): return ast.dump(named(original_tree, name), include_attributes=False) == ast.dump(named(final_tree, name), include_attributes=False)
    required = ['source_hashes', 'AvailableResult', 'probe_windows_symlink_prerequisite']
    if not all(ast_equal(name) for name in required): raise ValueError('Original classification/source/probe changed.')
    prior = json.loads((BASE / 'prepared-inputs.json').read_bytes())
    prior['prior_p3_actual_receipts_for_scope_only']['291'] = 'verification/sections/291-window-attempt5/actual/window.json'
    prior['public_promote_candidates']['scripts/verify_full_available.py'] = pin(target)
    prior['305_native_and_modules_pending_root_final_binding'] = {'native': 'scripts/verify_relic_exchange_flow_window_305.py', 'modules': additions,
        'native_exact_bytes_only_from_final_promoted_live_source_at_root_freeze': True}
    prior['missing_new_modules'] = modules
    prior['original_preparation_preserved'] = pin(BASE / 'prepared-inputs.json')
    prior['maintained_runner_final_adaptation'] = {'preserved_original_API_AST': required, 'old_order_preserved_as_prefix': True,
        'added_modules': modules, 'only_actual_maintained_selectors_API_determines_final_count': True}
    new(BASE / 'prepared-inputs-final.json', prior)
    # Parse every prepared controller and candidate. No imports, unit suite,
    # selector expansion, source freeze, activation or native execution.
    parses = {}
    for path in [*BASE.glob('*.py'), * (BASE / 'candidate/scripts').glob('*.py')]:
        ast.parse(path.read_bytes(), filename=str(path)); parses[path.relative_to(BASE).as_posix()] = pin(path)
    new(BASE / 'final-static-source-preparation.json', {'section': 305, 'kind': 'STATIC_SOURCE_PARSE_AND_APPEND_ONLY_PREPARATION',
        'parsed_files': parses, 'old_first467_candidate_preserved': 'first-unsealed-controller-draft/candidate/scripts/verify_full_available.py',
        'declared_tests_or_Qt_run': False, 'root_source_frozen_or_activated': False})
    print(json.dumps({'final_runner': pin(target), 'added_modules': len(modules), 'parsed_files': len(parses),
                      'tests_Qt_or_freeze_started': False}, ensure_ascii=False))


if __name__ == '__main__': main()
