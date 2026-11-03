"""Prepare inactive full261 window; bind only after Root freezes the worktree.

Uses the committed successful current-contract full260 source, preserving every
862 assert AST, original552 main try bytes, all cases, 52 states, 42 projection
records and the exact ten historical admissions. Does not execute a window.
"""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASIS_REL = 'verification/full-260/legacy-window-final/executed-tools'
BASIS_WINDOW_SHA = 'a0c6039840a1ae4ee25d45edc52811389edfd91a7f9f791209eafd68512821a5'
BASIS_GUARD_SHA = '4613258a87abaae51bed3beed2cedb44b2ad123cb4fcbb2b638eac5fbbaa263b'
CURRENT_AST_SHA = '941167ef87b6367ae031c585f183b92002224717f3abeb93fa99a70c14291fe1'
MAIN_SHA = '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922'
OLD_WORK_PREFIX = 'work/validation-audit/full260-current-window-attempt4-bundle/'
HELPERS = {'require_warning_order085', 'require_susuro_checkbox085'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(path):
    return sha(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def vector(text, exclude_helpers=False):
    tree = ast.parse(text)
    spans = [(n.lineno, n.end_lineno) for n in tree.body
             if isinstance(n, ast.FunctionDef) and n.name in HELPERS]
    nodes = sorted((n for n in ast.walk(tree) if isinstance(n, ast.Assert)),
                   key=lambda n: (n.lineno, n.col_offset))
    return [ast.dump(n, include_attributes=False) for n in nodes if not exclude_helpers
            or not any(a <= n.lineno <= b for a, b in spans)]


def functional_try(text):
    matches = [n for n in ast.parse(text).body if isinstance(n, ast.Try)
               and sum(isinstance(a, ast.Assert) for a in ast.walk(n)) == 552]
    if len(matches) != 1:
        raise ValueError('Complete552-assert main try is ambiguous')
    return ast.get_source_segment(text, matches[0])


def normalized(text):
    text, count = re.subn(r"(?m)^_SOURCE125_GUARD_SHA256 = (?:None|'[0-9a-f]{64}')$",
                          '_SOURCE125_GUARD_SHA256 = <binding>', text)
    if count != 1:
        raise ValueError('Exactly one guard binding is required')
    text, count = re.subn(r'(?m)^_SOURCE125_MAINTAINED_COUNT = (?:None|[0-9]+)$',
                          '_SOURCE125_MAINTAINED_COUNT = <binding>', text)
    if count != 1:
        raise ValueError('Exactly one source-count binding is required')
    return text.replace("'after_section': 261", "'after_section': 260").replace(
        "'after_section':261", "'after_section':260")


def basis():
    p = ROOT / BASIS_REL
    if digest(p / 'window.py') != BASIS_WINDOW_SHA or digest(p / 'current-source-guard.json') != BASIS_GUARD_SHA:
        raise ValueError('Committed successful full260 basis changed')
    return p


def audit(bundle):
    base = basis()
    original = (base / 'window.py').read_text(encoding='utf-8')
    current = (bundle / 'window.py').read_text(encoding='utf-8')
    old_vector, new_vector = vector(original), vector(current)
    if len(new_vector) != 862 or new_vector != old_vector:
        raise ValueError('All current862 assertion AST/order must be unchanged')
    ast_sha = sha(json.dumps(new_vector, separators=(',', ':')).encode())
    if ast_sha != CURRENT_AST_SHA:
        raise ValueError('Current862 AST pin mismatch')
    main = functional_try(current)
    if main != functional_try(original) or sha(main.encode()) != MAIN_SHA:
        raise ValueError('Original552 main try bytes changed')
    if normalized(current) != normalized(original):
        raise ValueError('Window bytes outside binding/section metadata changed')
    frozen = json.loads((base / 'static-preservation.json').read_bytes())
    for relative, expected in frozen['original42_projection_and_exact10_bridge_fixture_sha256'].items():
        if digest(bundle / relative) != expected:
            raise ValueError('42projection/exact10 fixture changed: ' + relative)
    mapping = json.loads((bundle / 'expected-map125.json').read_bytes())
    if [r['literal_index'] for r in mapping['rows']] != [18, 19, 20, 21, 38, 39, 40, 41, 44, 45]:
        raise ValueError('Historical ten admissions changed')
    current_tree = ast.parse(current)
    for name, expected in frozen['case_function_raw_sha256'].items():
        nodes = [n for n in current_tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
        if len(nodes) != 1 or sha(ast.get_source_segment(current, nodes[0]).encode()) != expected:
            raise ValueError('Original complete case generator changed: ' + name)
    frozen.update(candidate_after_section=261, basis_successful_full260_attempt=4,
                  unchanged_current862_assertions=True, unchanged_original_assertions_outside_helpers=len(vector(current, True)),
                  current_assertion_AST_order_sha256=ast_sha,
                  source_outside_binding_constants_and_section_metadata_unchanged=True,
                  runtime_executed=False, product_pass_claimed=False, native_windows_verified=False)
    frozen.pop('actual_full260_attempt', None)
    return frozen


def current_sources():
    result = {}
    for folder in ('rouge', 'tests', 'scripts'):
        for p in sorted((ROOT / folder).rglob('*')):
            relative = p.relative_to(ROOT)
            if '__pycache__' in relative.parts or p.suffix not in ('.py', '.json'):
                continue
            if p.is_symlink():
                raise ValueError('Maintained source symlink is not accepted: ' + str(relative))
            if p.is_file():
                result[relative.as_posix()] = digest(p)
    return dict(sorted(result.items()))


def prepare(bundle):
    base = basis()
    shutil.copytree(base, bundle)
    (bundle / 'current-source-guard.json').unlink()
    current = (bundle / 'window.py').read_text(encoding='utf-8')
    current = current.replace("_SOURCE125_GUARD_SHA256 = '" + BASIS_GUARD_SHA + "'", '_SOURCE125_GUARD_SHA256 = None')
    current = current.replace('_SOURCE125_MAINTAINED_COUNT = 1096', '_SOURCE125_MAINTAINED_COUNT = None')
    current = current.replace("'after_section': 260", "'after_section': 261").replace("'after_section':260", "'after_section':261")
    (bundle / 'window.py').write_text(current, encoding='utf-8')
    launcher = (bundle / 'launcher125.py').read_text(encoding='utf-8')
    launcher = launcher.replace("WINDOW_SHA256 = '" + BASIS_WINDOW_SHA + "'", 'WINDOW_SHA256 = None')
    launcher = launcher.replace("SOURCE125_GUARD_SHA256 = '" + BASIS_GUARD_SHA + "'", 'SOURCE125_GUARD_SHA256 = None')
    if 'WINDOW_SHA256 = None' not in launcher or 'SOURCE125_GUARD_SHA256 = None' not in launcher:
        raise ValueError('Launcher bindings were not cleared')
    (bundle / 'launcher125.py').write_text(launcher, encoding='utf-8')
    supervisor = (bundle / 'supervisor125.py').read_text(encoding='utf-8').replace("'after_section': 260", "'after_section': 261")
    (bundle / 'supervisor125.py').write_text(supervisor, encoding='utf-8')
    static = audit(bundle)
    write(bundle / 'static-preservation.json', static)
    write(bundle / 'activation261.json', {'status': 'INACTIVE_DRAFT', 'binding_ready': False,
          'section': 261, 'runtime_executed': False, 'basis_window_sha256': BASIS_WINDOW_SHA,
          'basis_guard_sha256': BASIS_GUARD_SHA, 'prepare_tool_sha256': digest(Path(__file__)),
          'draft_sha256': {p.relative_to(bundle).as_posix(): digest(p) for p in sorted(bundle.rglob('*'))
                           if p.is_file() and p.name != 'activation261.json'},
          'activation_requirement': 'Root declares current261 production source frozen; bind expected HEAD separately.'})
    return static


def activate(bundle, parent):
    record = json.loads((bundle / 'activation261.json').read_bytes())
    if record['status'] != 'INACTIVE_DRAFT' or record['binding_ready']:
        raise ValueError('Only fresh inactive bundle may be activated')
    if git('branch', '--show-current') != 'codex/p2-development' or git('rev-parse', 'HEAD') != parent:
        raise ValueError('Root frozen branch/parent HEAD differs')
    if record['prepare_tool_sha256'] != digest(Path(__file__)):
        raise ValueError('Preparation/activation tool changed')
    for relative, expected in record['draft_sha256'].items():
        if digest(bundle / relative) != expected:
            raise ValueError('Prepared source changed before activation: ' + relative)
    static = audit(bundle)
    base_guard = json.loads((basis() / 'current-source-guard.json').read_bytes())
    additional = {}
    for relative, expected in base_guard['source_additional_sha256'].items():
        p = bundle / relative[len(OLD_WORK_PREFIX):] if relative.startswith(OLD_WORK_PREFIX) else ROOT / relative
        if p.is_symlink() or digest(p) != expected:
            raise ValueError('Current-contract source proof changed: ' + relative)
        additional[p.relative_to(ROOT).as_posix()] = expected
    for relative in ('.cache/game-data/receipt.json', '.cache/research/battle-039/image-receipt.json',
                     '.cache/research/timing-048/skeleton-downloads.json',
                     'work/261-validation/public/fresh-source-indexes.json'):
        p = ROOT / relative
        if p.is_symlink():
            raise ValueError('Public index proof symlink')
        additional[relative] = digest(p)
    sources = current_sources()
    guard = copy.deepcopy(base_guard)
    guard.update(section=261, product_commit=parent, tested_worktree_parent_commit=parent,
                 source_sha256=sources, source_additional_sha256=additional,
                 basis_successful_full260_attempt=4, maintenance_after_section=260,
                 actual_full261_attempt=1, old140_source_guard_reused=False,
                 scope='Frozen current261 repair worktree, parent HEAD label; full current-contract legacy scope. No native game or Windows claim.',
                 native_windows_verified=False, runtime_executed=False)
    guard.pop('actual_full260_attempt', None)
    write(bundle / 'current-source-guard.json', guard)
    guard_sha = digest(bundle / 'current-source-guard.json')
    window = (bundle / 'window.py').read_text(encoding='utf-8')
    window = window.replace('_SOURCE125_GUARD_SHA256 = None', "_SOURCE125_GUARD_SHA256 = '" + guard_sha + "'")
    window = window.replace('_SOURCE125_MAINTAINED_COUNT = None', '_SOURCE125_MAINTAINED_COUNT = ' + str(len(sources)))
    (bundle / 'window.py').write_text(window, encoding='utf-8')
    window_sha = digest(bundle / 'window.py')
    launcher = (bundle / 'launcher125.py').read_text(encoding='utf-8')
    launcher = launcher.replace('WINDOW_SHA256 = None', "WINDOW_SHA256 = '" + window_sha + "'")
    launcher = launcher.replace('SOURCE125_GUARD_SHA256 = None', "SOURCE125_GUARD_SHA256 = '" + guard_sha + "'")
    (bundle / 'launcher125.py').write_text(launcher, encoding='utf-8')
    static = audit(bundle)
    if current_sources() != sources or git('rev-parse', 'HEAD') != parent:
        raise ValueError('Maintained source/HEAD changed while binding')
    for relative, expected in additional.items():
        if digest(ROOT / relative) != expected:
            raise ValueError('Additional source proof drift while binding: ' + relative)
    write(bundle / 'static-preservation.json', static)
    record.update(status='CURRENT_SOURCE_BOUND_NOT_EXECUTED', binding_ready=True,
                  parent_head=parent, maintained_source_count=len(sources), additional_source_count=len(additional),
                  guard_sha256=guard_sha, window_sha256=window_sha,
                  activated_sha256={p.relative_to(bundle).as_posix(): digest(p) for p in sorted(bundle.rglob('*'))
                                    if p.is_file() and p.name != 'activation261.json'})
    write(bundle / 'activation261.json', record)
    return {k: record[k] for k in ('status', 'parent_head', 'maintained_source_count',
                                  'additional_source_count', 'guard_sha256', 'window_sha256')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', required=True, type=Path)
    op = parser.add_mutually_exclusive_group(required=True)
    op.add_argument('--prepare', action='store_true')
    op.add_argument('--activate', action='store_true')
    parser.add_argument('--expected-parent-commit')
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    if not bundle.is_relative_to(ROOT / 'work/261-validation'):
        raise ValueError('Only261 validation work directory is authorized')
    if args.activate and not re.fullmatch('[0-9a-f]{40}', args.expected_parent_commit or ''):
        raise ValueError('Expected frozen parent HEAD is required')
    print(json.dumps(prepare(bundle) if args.prepare else activate(bundle, args.expected_parent_commit), ensure_ascii=False))
