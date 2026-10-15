"""Independent285 fixture preparation/binding only; never launches a window.

The root must separately finish285 and declare its exact final source freeze.
Historical executed tools, assertions and raw receipts are never overwritten.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEGACY = HERE / 'legacy'
CURRENT = HERE / 'current'
OLD = ROOT / 'verification/full-275/legacy-window-attempt3/executed-tools'
OLD_CURRENT = ROOT / 'verification/full-275/current-window-attempt3/executed-tools'
INDICES = [18, 19, 20, 21, 38, 39, 40, 41, 44, 45]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf8'))


def source(path):
    return path.read_bytes().decode('utf8')


def replace_one(text, pattern, replacement):
    text, count = re.subn(pattern, replacement, text)
    if count != 1:
        raise ValueError('One binding assignment required: ' + pattern)
    return text


def assertions(text):
    return [ast.dump(n, include_attributes=False) for n in sorted(
        (n for n in ast.walk(ast.parse(text)) if isinstance(n, ast.Assert)),
        key=lambda n: (n.lineno, n.col_offset))]


def function(text, name):
    matches = [n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name]
    if len(matches) != 1:
        raise ValueError('One original function required: ' + name)
    return ast.get_source_segment(text, matches[0])


def maintry(text):
    matches = [n for n in ast.parse(text).body if isinstance(n, ast.Try)
               and sum(isinstance(v, ast.Assert) for v in ast.walk(n)) == 552]
    if len(matches) != 1:
        raise ValueError('The original552 assertion maintry is required')
    return ast.get_source_segment(text, matches[0])


def tools(folder):
    return {p.relative_to(folder).as_posix(): sha(p) for p in sorted(folder.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'
            and p.name not in ('activation275.json', 'draft285.json')}


def preserved():
    a, b = source(OLD / 'window.py'), source(LEGACY / 'window.py')
    if (len(assertions(a)) != 862 or assertions(a) != assertions(b)
            or maintry(a) != maintry(b)
            or function(a, '_install_narrow_observers100') != function(b, '_install_narrow_observers100')):
        raise ValueError('Original862 AST/552 body/observer function changed')
    static = json.loads((OLD / 'static-preservation.json').read_bytes())
    for name, expected in static['case_function_raw_sha256'].items():
        if hashlib.sha256(function(b, name).replace('\r\n', '\n').encode()).hexdigest() != expected:
            raise ValueError('Original case generator changed: ' + name)
    for name in ('window.py', 'window29.py'):
        if assertions(source(OLD_CURRENT / name)) != assertions(source(CURRENT / name)):
            raise ValueError('Original current window assertion changed: ' + name)
    if [r['literal_index'] for r in json.loads((LEGACY / 'expected-map125.json').read_bytes())['rows']] != INDICES:
        raise ValueError('Exact original10 admissions changed')


def prepare():
    if LEGACY.exists() or CURRENT.exists():
        raise ValueError('Never overwrite a prepared or used285 bundle')
    originals, alterations = {}, {}
    for old, new in ((OLD, LEGACY), (OLD_CURRENT, CURRENT)):
        new.mkdir()
        for path in sorted(old.iterdir()):
            if not path.is_file() or path.name in ('activation275.json', 'current-source-guard.json',
                                                   'source-freeze.json', 'root-declared-source-freeze.json'):
                continue
            shutil.copyfile(path, new / path.name)
            originals[(new.relative_to(HERE) / path.name).as_posix()] = sha(path)
        # Old authority is archival only, never mistaken for a new binding.
        for name in ('activation275.json', 'current-source-guard.json') if old == OLD else ('activation275.json', 'source-freeze.json'):
            target = new / 'baseline275' / name
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(old / name, target)
    relocations = json.loads((OLD / 'adaptation-before-after.json').read_bytes())['relocations']
    if len(relocations) != 17:
        raise ValueError('All17 original dependencies required')
    original_prefix = '.cache/full275-legacy-bundle/'
    for row in relocations:
        if not row['new_relative'].startswith(original_prefix):
            raise ValueError('Unexpected original prerequisite root')
        leaf = row['new_relative'][len(original_prefix):]
        src, target = OLD / leaf, LEGACY / leaf
        if sha(src) != row['sha256']:
            raise ValueError('Original prerequisite mismatch: ' + leaf)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        originals['legacy/' + leaf] = sha(src)
    # Copy every old same-bundle supplemental source used by its complete guard.
    old_guard = json.loads((OLD / 'current-source-guard.json').read_bytes())
    old_prefix = '.cache/full275-legacy-attempt3-bundle/'
    for name, expected in old_guard['source_additional_sha256'].items():
        if not name.startswith(old_prefix):
            continue
        leaf = name[len(old_prefix):]
        if sha(OLD / leaf) != expected:
            raise ValueError('Original additional source mismatch: ' + leaf)
        if not (LEGACY / leaf).exists():
            (LEGACY / leaf).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(OLD / leaf, LEGACY / leaf)
        originals['legacy/' + leaf] = expected
    window = source(LEGACY / 'window.py')
    window = replace_one(window, r"(?m)^_SOURCE125_GUARD_SHA256 = '[0-9a-f]{64}'$", '_SOURCE125_GUARD_SHA256 = None')
    window = replace_one(window, r'(?m)^_SOURCE125_MAINTAINED_COUNT = [0-9]+$', '_SOURCE125_MAINTAINED_COUNT = None')
    (LEGACY / 'window.py').write_bytes(window.encode('utf8'))
    launcher = source(LEGACY / 'launcher125.py')
    for name in ('WINDOW_SHA256', 'SOURCE125_GUARD_SHA256'):
        launcher = replace_one(launcher, r"(?m)^" + name + r" = '[0-9a-f]{64}'$", name + ' = None')
    (LEGACY / 'launcher125.py').write_bytes(launcher.encode('utf8'))
    for name in ('window.py', 'window29.py'):
        text = replace_one(source(CURRENT / name), r"(?m)^FREEZE_SHA256='[0-9a-f]{64}'$", 'FREEZE_SHA256=None')
        (CURRENT / name).write_bytes(text.encode('utf8'))
    for folder in (LEGACY, CURRENT):
        text = source(folder / 'launcher275.py')
        text = replace_one(text, r'(?m)^ROOT=HERE.parents\[1\]$', "ROOT=next(p for p in (HERE,*HERE.parents) if (p/'rouge/app.py').is_file())")
        text = text.replace('CURRENT275_SOURCE_BOUND_NOT_EXECUTED', 'CURRENT285_SOURCE_BOUND_NOT_EXECUTED')
        text = text.replace('SECTION275_ACTUAL_NATIVE_FIXTURE_LAUNCHER_CLOSURE', 'SECTION285_ACTUAL_NATIVE_FIXTURE_LAUNCHER_CLOSURE')
        (folder / 'launcher275.py').write_bytes(text.encode('utf8'))
    text = source(LEGACY / 'supervisor275.py')
    text = replace_one(text, r'(?m)^    root=Path\(__file__\).resolve\(\).parents\[2\]$',
                       "    root=next(p for p in (Path(__file__).resolve().parent,*Path(__file__).resolve().parents) if (p/'rouge/app.py').is_file())")
    text = text.replace('SECTION275_ACTUAL_WINDOWS_OWNED_POPEN_SUPERVISION', 'SECTION285_ACTUAL_WINDOWS_OWNED_POPEN_SUPERVISION')
    (LEGACY / 'supervisor275.py').write_bytes(text.encode('utf8'))
    preserved()
    for folder in (LEGACY, CURRENT):
        for path in folder.glob('*.py'):
            compile(path.read_bytes(), str(path), 'exec')
        write(folder / 'activation275.json', {'status': 'INACTIVE_DRAFT', 'binding_ready': False,
              'actual_section': 285, 'runtime_executed': False})
    for name, previous_sha in originals.items():
        current_sha = sha(HERE / name)
        if previous_sha != current_sha:
            alterations[name] = {'original_sha256': previous_sha, 'draft_sha256': current_sha}
    ledger = {'kind': 'FULL285_INACTIVE_WINDOW_PREPARATION', 'status': 'INACTIVE_DRAFT',
              'original_files_sha256': originals, 'permitted_path_binding_label_alterations': alterations,
              '17_prerequisites': relocations, 'original862_assert_AST_order_unchanged': True,
              'original552_maintry_and_generators_unchanged': True,
              'observer_then_normal_constructor_bootstrap_order_preserved': True,
              'required_scope': {'states': 52, 'records': 4283, 'projections': 42,
                                 'bridge_indices': INDICES, 'empty_trace_rows': 26,
                                 'current30_attempt': True, 'separate_current29': True},
              'root_source_frozen': False, 'GUI_or_full_suite_executed': False,
              'game_or_chat_or_private_state_used': False,
              'inherited_native275_and_wine_filenames_are_not_actual_platform_authority': True}
    write(HERE / 'draft-preservation-285.json', ledger)
    for folder in (LEGACY, CURRENT):
        write(folder / 'draft285.json', {'status': 'INACTIVE_DRAFT', 'tools_sha256': tools(folder),
                                        'prepare_script_sha256': sha(Path(__file__))})
    print(json.dumps({'prepared': True, 'activated': False, 'executed': False, 'assertions': 862,
                      'maintry': 552, 'prerequisites': 17, 'scope_not_reduced': True}))


def maintained():
    return {p.relative_to(ROOT).as_posix(): sha(p) for name in ('rouge', 'tests', 'scripts')
            for p in sorted((ROOT / name).rglob('*')) if p.is_file() and '__pycache__' not in p.parts
            and p.suffix in ('.py', '.json') and not p.is_symlink()}


def selectors():
    def literal(path, name):
        values = [n.value for n in ast.parse(path.read_bytes()).body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
        if len(values) != 1:
            raise ValueError('Expected one literal selector assignment: ' + name)
        return list(ast.literal_eval(values[0]))
    core = json.loads((ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes())['test_modules']
    return list(dict.fromkeys(core + literal(ROOT / 'scripts/verify_full_available.py', 'NEW_MODULES')
                             + literal(ROOT / 'scripts/verify_cloud.py', 'MODULES')))


def activate(freeze, parent):
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
    if git('branch', '--show-current') != 'codex/p2-development' or git('rev-parse', 'HEAD') != parent:
        raise ValueError('Exact current branch/parent required')
    freeze = freeze.resolve()
    if freeze != ROOT / 'verification/full-285/source-freeze.json':
        raise ValueError('Only root-declared final285 freeze is accepted')
    declaration = json.loads(freeze.read_bytes())
    if declaration.get('root_declared') is not True or declaration.get('parent_commit') != parent:
        raise ValueError('Root freeze authority/parent not declared')
    previous = json.loads((ROOT / 'verification/full-275/source-freeze-reset-repair.json').read_bytes())
    if not set(previous['selectors']) <= set(declaration['selectors']):
        raise ValueError('Original complete selector scope omitted')
    if declaration['selectors'] != selectors():
        raise ValueError('Root freeze must bind the complete current selector union, including actual283-285 additions')
    if not set(previous['source_sha256']) <= set(declaration['source_sha256']):
        raise ValueError('Original full source scope omitted')
    for name, expected in declaration['source_sha256'].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or (ROOT / name).is_symlink() or sha(path) != expected:
            raise ValueError('Root freeze mismatch: ' + name)
    for folder in (LEGACY, CURRENT):
        if json.loads((folder / 'activation275.json').read_bytes())['binding_ready'] is not False:
            raise ValueError('Never overwrite a bound or used bundle')
        draft = json.loads((folder / 'draft285.json').read_bytes())
        if tools(folder) != draft['tools_sha256'] or sha(Path(__file__)) != draft['prepare_script_sha256']:
            raise ValueError('Reviewed draft bytes changed')
    sources = maintained()
    guard = json.loads((OLD / 'current-source-guard.json').read_bytes())
    old_prefix = '.cache/full275-legacy-attempt3-bundle/'
    additional = {}
    for name, expected in guard['source_additional_sha256'].items():
        if name.startswith(old_prefix):
            name = (LEGACY.relative_to(ROOT) / name[len(old_prefix):]).as_posix()
            expected = sha(ROOT / name)
        if sha(ROOT / name) != expected:
            raise ValueError('Original supplemental dependency changed: ' + name)
        additional[name] = expected
    for path in (freeze, Path(__file__), HERE / 'draft-preservation-285.json'):
        additional[path.relative_to(ROOT).as_posix()] = sha(path)
    if set(declaration['source_sha256']) - (set(sources) | set(additional)):
        raise ValueError('Frozen source omitted from actual fixture guard')
    guard.update(source_sha256=sources, source_additional_sha256=additional,
                 product_commit=parent, tested_worktree_parent_commit=parent,
                 root_freeze_sha256=sha(freeze), root_freeze_source_count=len(declaration['source_sha256']),
                 actual_section=285, actual_full285_native_attempt=1, runtime_executed=False,
                 inherited275_fields_are_historical_only=True, source_coverage_complete=True)
    write(LEGACY / 'current-source-guard.json', guard)
    guard_sha = sha(LEGACY / 'current-source-guard.json')
    text = source(LEGACY / 'window.py').replace('_SOURCE125_GUARD_SHA256 = None', "_SOURCE125_GUARD_SHA256 = '" + guard_sha + "'", 1)
    text = text.replace('_SOURCE125_MAINTAINED_COUNT = None', '_SOURCE125_MAINTAINED_COUNT = ' + str(len(sources)), 1)
    (LEGACY / 'window.py').write_bytes(text.encode('utf8'))
    text = source(LEGACY / 'launcher125.py').replace('WINDOW_SHA256 = None', "WINDOW_SHA256 = '" + sha(LEGACY / 'window.py') + "'", 1)
    text = text.replace('SOURCE125_GUARD_SHA256 = None', "SOURCE125_GUARD_SHA256 = '" + guard_sha + "'", 1)
    (LEGACY / 'launcher125.py').write_bytes(text.encode('utf8'))
    shutil.copyfile(freeze, CURRENT / 'source-freeze.json')
    for name in ('window.py', 'window29.py'):
        (CURRENT / name).write_bytes(source(CURRENT / name).replace('FREEZE_SHA256=None', "FREEZE_SHA256='" + sha(freeze) + "'", 1).encode('utf8'))
    preserved()
    if sources != maintained() or git('rev-parse', 'HEAD') != parent:
        raise ValueError('Source changed during binding')
    for folder, modes in ((LEGACY, ['legacy']), (CURRENT, ['current30', 'current29'])):
        write(folder / 'activation275.json', {'status': 'CURRENT285_SOURCE_BOUND_NOT_EXECUTED',
              'binding_ready': True, 'runtime_executed': False, 'actual_section': 285,
              'allowed_modes': modes, 'tested_worktree_parent_commit': parent,
              'root_freeze_relative': freeze.relative_to(ROOT).as_posix(), 'root_freeze_sha256': sha(freeze),
              'root_freeze_source_count': len(declaration['source_sha256']),
              'execution_tools_sha256': tools(folder), 'scope_not_reduced': True,
              'inherited275_filenames_and_raw_headers_not_actual_platform_authority': True})
    print(json.dumps({'root_bound': True, 'executed': False, 'source_count': len(declaration['source_sha256']),
                      'selector_count': len(declaration['selectors']), 'guard_sha256': guard_sha}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--activate', action='store_true')
    parser.add_argument('--root-declared-freeze', type=Path)
    parser.add_argument('--expected-parent-commit')
    args = parser.parse_args()
    if args.prepare:
        prepare()
    else:
        if args.root_declared_freeze is None or args.expected_parent_commit is None:
            parser.error('Activation needs root final285 freeze and exact current parent')
        activate(args.root_declared_freeze, args.expected_parent_commit)
