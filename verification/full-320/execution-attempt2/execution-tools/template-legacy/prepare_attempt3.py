"""Fresh inactive A3 bundles for root-declared275 Reset repair; no GUI launch.

Copies the actually executed A2 corrected-observer fixture and current30/29.
Never overwrites A1/A2 artifacts, assertions, generators or private state.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CURRENT = ROOT / '.cache/full275-current-attempt3-window'
OLD = ROOT / '.cache/full275-legacy-attempt2-bundle'
OLD_CURRENT = ROOT / '.cache/full275-current-window'
INDICES = [18, 19, 20, 21, 38, 39, 40, 41, 44, 45]
EXCLUDE = {'activation275.json', 'draft-attempt3.json', 'current-source-guard.json',
           'source-freeze.json'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


def text(path):
    return path.read_bytes().decode('utf-8')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def tools(folder):
    return {p.relative_to(folder).as_posix(): sha(p) for p in sorted(folder.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts
            and p.relative_to(folder).as_posix() not in EXCLUDE and p.suffix != '.pyc'}


def assertions(source):
    return [ast.dump(n, include_attributes=False) for n in sorted(
        (n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Assert)),
        key=lambda n: (n.lineno, n.col_offset))]


def maintry(source):
    nodes = [n for n in ast.parse(source).body if isinstance(n, ast.Try)
             and sum(isinstance(v, ast.Assert) for v in ast.walk(n)) == 552]
    if len(nodes) != 1:
        raise ValueError('Exactly the original552-assert maintry is required')
    return ast.get_source_segment(source, nodes[0])


def function(source, name):
    nodes = [n for n in ast.parse(source).body
             if isinstance(n, ast.FunctionDef) and n.name == name]
    if len(nodes) != 1:
        raise ValueError('One original function is required: ' + name)
    return ast.get_source_segment(source, nodes[0])


def copy_exact(source, target):
    if target.exists():
        raise ValueError('Never overwrite an A3 candidate artifact: ' + str(target))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    if sha(source) != sha(target):
        raise ValueError('Copy is not byte-identical')


def verified_active(folder):
    record = json.loads((folder / 'activation275.json').read_bytes())
    if record['binding_ready'] is not True:
        raise ValueError('A3 requires the actual activated previous bundle')
    for name, expected in record['execution_tools_sha256'].items():
        if sha(folder / name) != expected:
            raise ValueError('Actually executed predecessor tool changed: ' + name)
    return record


def replace_single(source, pattern, replacement):
    result, count = re.subn(pattern, replacement, source)
    if count != 1:
        raise ValueError('Exactly one binding line is required: ' + pattern)
    return result


def prepare():
    if (HERE / 'activation275.json').exists() or (CURRENT / 'activation275.json').exists():
        raise ValueError('Retain prior A3 preparation/activation; do not overwrite')
    prior = verified_active(OLD)
    prior_current = verified_active(OLD_CURRENT)
    if prior['tested_worktree_parent_commit'] != prior_current['tested_worktree_parent_commit']:
        raise ValueError('Predecessor parent differs')
    copies = {}
    for old, new in ((OLD, HERE), (OLD_CURRENT, CURRENT)):
        originals = {}
        for name, expected in prior['execution_tools_sha256'].items() if old == OLD else prior_current['execution_tools_sha256'].items():
            copy_exact(old / name, new / name)
            originals[name] = expected
        for name in ('activation275.json', 'current-source-guard.json') if old == OLD else ('activation275.json', 'source-freeze.json'):
            copy_exact(old / name, new / 'previous-attempt2' / name)
        copies[new.relative_to(ROOT).as_posix()] = originals
    original = text(OLD / 'window.py')
    candidate = replace_single(original, r"(?m)^_SOURCE125_GUARD_SHA256 = '[0-9a-f]{64}'$", '_SOURCE125_GUARD_SHA256 = None')
    candidate = replace_single(candidate, r'(?m)^_SOURCE125_MAINTAINED_COUNT = [0-9]+$', '_SOURCE125_MAINTAINED_COUNT = None')
    if (len(assertions(candidate)) != 862 or assertions(candidate) != assertions(original)
            or maintry(candidate) != maintry(original)
            or function(candidate, '_install_narrow_observers100') != function(original, '_install_narrow_observers100')):
        raise ValueError('Original862 AST/552 maintry/observer function changed')
    static = json.loads((OLD / 'static-preservation.json').read_bytes())
    for name, expected in static['case_function_raw_sha256'].items():
        raw = function(candidate, name).replace('\r\n', '\n').encode()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Original case generator changed: ' + name)
    (HERE / 'window.py').write_bytes(candidate.encode('utf-8'))
    launcher = text(HERE / 'launcher125.py')
    for binding in ('WINDOW_SHA256', 'SOURCE125_GUARD_SHA256'):
        launcher = replace_single(launcher, r"(?m)^" + binding + r" = '[0-9a-f]{64}'$", binding + ' = None')
    (HERE / 'launcher125.py').write_bytes(launcher.encode('utf-8'))
    current_audits = {}
    for name in ('window.py', 'window29.py'):
        source = text(OLD_CURRENT / name)
        modified = replace_single(source, r"(?m)^FREEZE_SHA256='[0-9a-f]{64}'$", 'FREEZE_SHA256=None')
        if assertions(source) != assertions(modified):
            raise ValueError('Original current assertions changed: ' + name)
        (CURRENT / name).write_bytes(modified.encode('utf-8'))
        current_audits[name] = {'previous_sha256': sha(OLD_CURRENT / name), 'inactive_sha256': sha(CURRENT / name),
                               'all_original_assert_AST_order_unchanged': True,
                               'assertion_count': len(assertions(source))}
    mapping = json.loads((HERE / 'expected-map125.json').read_bytes())
    if [row['literal_index'] for row in mapping['rows']] != INDICES:
        raise ValueError('Exact original ten bridge indices changed')
    relocation = json.loads((HERE / 'adaptation-before-after.json').read_bytes())['relocations']
    if len(relocation) != 17:
        raise ValueError('Exactly original17 remapped prerequisites are required')
    relocated = []
    for row in relocation:
        prefix = '.cache/full275-legacy-bundle/'
        name = row['new_relative']
        if not name.startswith(prefix):
            raise ValueError('Original17 relocation has an unexpected root')
        local = name[len(prefix):]
        if sha(HERE / local) != row['sha256']:
            raise ValueError('Original17 prerequisite changed')
        relocated.append({**row, 'previous_attempt2_relative': (OLD / local).relative_to(ROOT).as_posix(),
                          'new_attempt3_relative': (HERE / local).relative_to(ROOT).as_posix()})
    symlink = json.loads((CURRENT / 'symlink-capability-275.json').read_bytes())
    if (symlink['creation_succeeded'] is not False or symlink['exception']['winerror'] != 1314
            or symlink['cleanup_pending'] is not False):
        raise ValueError('Actual same-kind1314 evidence is required; no privilege/substitute changes')
    ledger = {'kind': 'SECTION275_RESET_REPAIR_A3_COMPLETE_WINDOW_SCOPE_PREPARATION',
              'status': 'INACTIVE_DRAFT', 'root_source_frozen_by_this_worker': False,
              'gui_executed': False, 'production_or_tests_modified': False,
              'original_attempt2_activation_sha256': sha(OLD / 'activation275.json'),
              'original_current_activation_sha256': sha(OLD_CURRENT / 'activation275.json'),
              'previous_parent_commit': prior['tested_worktree_parent_commit'],
              'previous_root_freeze_relative': prior['root_freeze_relative'],
              'previous_root_freeze_sha256': prior['root_freeze_sha256'],
              'new_root_freeze_must_be_explicitly_bound': True,
              'original862_assert_AST_and_order_unchanged': True,
              'original552_maintry_source_bytes_unchanged': True,
              'case_generators_unchanged': True, 'observer_installer_original_function_bytes_unchanged': True,
              'observer_first_then_normal_constructor_bootstrap_preserved': True,
              'saved_states_required': 52, 'runtime_records_required': 4283,
              'projection_records_required': 42, 'bridge_indices': INDICES,
              'current_original30_must_run_and_preserve_actual_failure': True,
              'current_available29_no_non_symlink_check_omitted': True,
              'hardlink_junction_regular_substitute_used': False,
              'symlink_privilege_changed': False, 'current_assertion_audits': current_audits,
              '17_prerequisite_relocations': relocated,
              'byte_exact_predecessor_tool_copies': copies,
              'owned_supervisor_sha256': sha(HERE / 'supervisor275.py'), 'owned_job_deadline_max_seconds': 1200,
              'model_results_rewritten': False, 'game_api_mocked': False}
    write(HERE / 'attempt3-preservation.json', ledger)
    copy_exact(HERE / 'attempt3-preservation.json', CURRENT / 'attempt3-preservation.json')
    for folder, modes in ((HERE, ['legacy']), (CURRENT, ['current30', 'current29'])):
        write(folder / 'activation275.json', {'status': 'INACTIVE_DRAFT', 'binding_ready': False,
              'runtime_executed': False, 'allowed_modes': modes})
        write(folder / 'draft-attempt3.json', {'status': 'INACTIVE_DRAFT', 'draft_tools_sha256': tools(folder),
              'previous_parent_commit': prior['tested_worktree_parent_commit'],
              'new_root_freeze_required': True, 'original_assertions_unchanged': True,
              'gui_executed': False})
    print(json.dumps({'prepared': True, 'activated': False, 'gui_started': False,
                      'assertions': 862, 'maintry': 552, 'states': 52, 'records': 4283,
                      'current30_and_available29_preserved': True}, ensure_ascii=False))


def maintained_sources():
    result = {}
    for folder in ('rouge', 'tests', 'scripts'):
        for path in sorted((ROOT / folder).rglob('*')):
            if '__pycache__' in path.parts or path.suffix not in ('.py', '.json') or not path.is_file():
                continue
            if path.is_symlink():
                raise ValueError('Maintained public source symlink refused')
            result[path.relative_to(ROOT).as_posix()] = sha(path)
    return dict(sorted(result.items()))


def activate(freeze, parent):
    if git('branch', '--show-current') != 'codex/p2-development' or git('rev-parse', 'HEAD') != parent:
        raise ValueError('Root-declared branch and exact current parent are required')
    for folder in (HERE, CURRENT):
        state = json.loads((folder / 'activation275.json').read_bytes())
        draft = json.loads((folder / 'draft-attempt3.json').read_bytes())
        if state['binding_ready'] or state['status'] != 'INACTIVE_DRAFT':
            raise ValueError('Activate only a fresh inactive A3')
        if parent != draft['previous_parent_commit'] or tools(folder) != draft['draft_tools_sha256']:
            raise ValueError('Reviewed complete A3 tool bytes or parent changed')
    freeze = freeze.resolve()
    if not freeze.is_relative_to(ROOT) or freeze.relative_to(ROOT).as_posix() != 'verification/full-275/source-freeze-reset-repair.json':
        raise ValueError('Use only root explicit275 Reset repair freeze')
    frozen = json.loads(freeze.read_bytes())
    if frozen.get('parent_commit') != parent or frozen.get('root_declared') is not True:
        raise ValueError('Root source-freeze authority/parent declaration required')
    previous = json.loads((ROOT / json.loads((OLD / 'activation275.json').read_bytes())['root_freeze_relative']).read_bytes())
    if not set(previous['selectors']) <= set(frozen['selectors']):
        raise ValueError('Every previous complete selector must remain')
    if not set(previous['source_sha256']) <= set(frozen['source_sha256']):
        raise ValueError('Complete previous frozen public source range must remain')
    for name, expected in frozen['source_sha256'].items():
        relative = Path(name)
        if (not isinstance(name, str) or relative.is_absolute() or '..' in relative.parts
                or '\\' in name or name != relative.as_posix()
                or (name != 'CORE_0.70_VERIFICATION.json' and
                    (not relative.parts or relative.parts[0] not in ('rouge', 'tests', 'scripts')
                     or relative.suffix not in ('.py', '.json')))):
            raise ValueError('Root freeze must contain public maintained source only')
        if (ROOT / relative).is_symlink() or sha(ROOT / name) != expected:
            raise ValueError('Actual root-frozen source drift: ' + name)
    sources = maintained_sources()
    old_guard = json.loads((HERE / 'previous-attempt2/current-source-guard.json').read_bytes())
    additional = {}
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = HERE.relative_to(ROOT).as_posix() + '/'
    for name, expected in old_guard['source_additional_sha256'].items():
        relocated = new_prefix + name[len(old_prefix):] if name.startswith(old_prefix) else name
        if sha(ROOT / relocated) != expected:
            raise ValueError('Exact original additional proof changed: ' + name)
        additional[relocated] = expected
    additional[freeze.relative_to(ROOT).as_posix()] = sha(freeze)
    for name in ('prepare_attempt3.py', 'attempt3-preservation.json'):
        additional[(HERE / name).relative_to(ROOT).as_posix()] = sha(HERE / name)
    if set(frozen['source_sha256']) - (set(sources) | set(additional)):
        raise ValueError('Complete new freeze must be covered by legacy guard')
    delta = {name: {'previous': previous['source_sha256'].get(name), 'current': value}
             for name, value in frozen['source_sha256'].items()
             if value != previous['source_sha256'].get(name)}
    guard = dict(old_guard)
    guard.update(source_sha256=sources, source_additional_sha256=additional,
                 product_commit=parent, tested_worktree_parent_commit=parent,
                 root_freeze_sha256=sha(freeze), root_freeze_source_count=len(frozen['source_sha256']),
                 actual_full275_native_attempt=3, source_freeze_same_as_attempt2=False,
                 root_frozen_reset_repair_delta=delta, runtime_executed=False,
                 source_coverage_complete=True, original_assertions_and_observer_order_preserved=True)
    write(HERE / 'current-source-guard.json', guard)
    guard_sha = sha(HERE / 'current-source-guard.json')
    candidate = text(HERE / 'window.py').replace('_SOURCE125_GUARD_SHA256 = None',
        "_SOURCE125_GUARD_SHA256 = '" + guard_sha + "'", 1).replace('_SOURCE125_MAINTAINED_COUNT = None',
        '_SOURCE125_MAINTAINED_COUNT = ' + str(len(sources)), 1)
    original = text(OLD / 'window.py')
    if (assertions(candidate) != assertions(original) or maintry(candidate) != maintry(original)
            or function(candidate, '_install_narrow_observers100') != function(original, '_install_narrow_observers100')):
        raise ValueError('Activation changed original assertions/maintry/observer source')
    (HERE / 'window.py').write_bytes(candidate.encode('utf-8'))
    launcher = text(HERE / 'launcher125.py').replace('WINDOW_SHA256 = None',
        "WINDOW_SHA256 = '" + sha(HERE / 'window.py') + "'", 1).replace('SOURCE125_GUARD_SHA256 = None',
        "SOURCE125_GUARD_SHA256 = '" + guard_sha + "'", 1)
    (HERE / 'launcher125.py').write_bytes(launcher.encode('utf-8'))
    # The predecessor current freeze remains byte-exact inside previous-attempt2.
    (CURRENT / 'source-freeze.json').write_bytes(freeze.read_bytes())
    (CURRENT / 'root-declared-source-freeze.json').write_bytes(freeze.read_bytes())
    for name in ('window.py', 'window29.py'):
        (CURRENT / name).write_bytes(text(CURRENT / name).replace('FREEZE_SHA256=None',
            "FREEZE_SHA256='" + sha(freeze) + "'", 1).encode('utf-8'))
    if sources != maintained_sources() or git('rev-parse', 'HEAD') != parent:
        raise ValueError('Source changed during activation; never execute this bundle')
    for folder, modes in ((HERE, ['legacy']), (CURRENT, ['current30', 'current29'])):
        write(folder / 'activation275.json', {'status': 'CURRENT275_SOURCE_BOUND_NOT_EXECUTED',
              'binding_ready': True, 'runtime_executed': False, 'allowed_modes': modes,
              'tested_worktree_parent_commit': parent,
              'root_freeze_relative': freeze.relative_to(ROOT).as_posix(),
              'root_freeze_sha256': sha(freeze), 'root_freeze_source_count': len(frozen['source_sha256']),
              'execution_tools_sha256': tools(folder),
              'current_root_source_declared_frozen_by_caller': True,
              'actual_native_attempt': 3, 'source_freeze_same_as_attempt2': False,
              'scope_preserved': {'862_AST': True, '552_maintry': True, '52_states': True,
                                  '4283_records': True, 'original30_and_available29': True}})
    print(json.dumps({'root_bound': True, 'executed': False, 'root_source_files': len(frozen['source_sha256']),
                      'selectors': len(frozen['selectors']), 'legacy_guard_sha256': guard_sha,
                      'source_delta_files': len(delta)}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare', action='store_true')
    group.add_argument('--activate', action='store_true')
    parser.add_argument('--root-declared-freeze', type=Path)
    parser.add_argument('--expected-parent-commit')
    args = parser.parse_args()
    if args.prepare:
        prepare()
    else:
        if args.root_declared_freeze is None or args.expected_parent_commit is None:
            parser.error('Activation requires root final freeze and exact parent')
        activate(args.root_declared_freeze, args.expected_parent_commit)
