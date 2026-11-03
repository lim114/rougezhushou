"""Prepare then explicitly bind legacy full window to a frozen current source.

Never runs Wine, edits production, weakens assertions or changes old expectations.
Activation must be requested separately after the root freezes section245 source.
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
LEGACY = ROOT / 'verification/full-140/activated-window'
SECTION = 245
OLD_COUNT = 809
OLD_GUARD = '9efbc31c30e33da2f696b7e483b970025d5964156bfb23b9e4653d6e813347ea'
OLD_WINDOW = '4e3da39eb94a92cb717b0e627a5ce17a3d8c23f2ddf91ff43313e6f153fd05a6'
OUTPUT_GUARD_NAME = 'current-source-guard.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def original_window():
    raw = (LEGACY / 'window.py').read_bytes()
    if sha(raw) != OLD_WINDOW:
        raise ValueError('The original full140 window source changed.')
    return raw.decode('utf-8')


def assert_vector(text):
    tree = ast.parse(text)
    nodes = sorted((node for node in ast.walk(tree) if isinstance(node, ast.Assert)),
                   key=lambda node: (node.lineno, node.col_offset))
    return [ast.dump(node, include_attributes=False) for node in nodes]


def functional_try(text):
    tree = ast.parse(text)
    matches = [node for node in tree.body if isinstance(node, ast.Try)
               and sum(isinstance(value, ast.Assert) for value in ast.walk(node)) == 552]
    if len(matches) != 1:
        raise ValueError('The original552-assert functional try identity is ambiguous.')
    return ast.get_source_segment(text, matches[0])


def audit(candidate):
    original = original_window()
    old, current = assert_vector(original), assert_vector(candidate)
    if len(old) != 831 or current != old:
        raise ValueError('The original831 assertion ASTs or their order changed.')
    old_try, current_try = functional_try(original), functional_try(candidate)
    if current_try != old_try:
        raise ValueError('Original552-assert functional try bytes changed.')
    mapping = json.loads((LEGACY / 'expected-map125.json').read_bytes())
    indices = [row['literal_index'] for row in mapping['rows']]
    if indices != [18, 19, 20, 21, 38, 39, 40, 41, 44, 45]:
        raise ValueError('The exact ten historical documentary admissions changed.')
    return {'status': 'PASS_STATIC_ASSERTIONS_AND_FUNCTIONAL_TRY_PRESERVED',
            'original_basis_section': 140, 'candidate_after_section': SECTION,
            'original_assertions': 831, 'candidate_assertions': len(current),
            'assertion_AST_order_sha256': sha(json.dumps(old, separators=(',', ':')).encode()),
            'original_functional_try_assertions': 552,
            'functional_try_bytes_sha256': sha(old_try.encode()),
            'original_functional_try_bytes_unchanged': True,
            'literal_indices_preserved': indices,
            'expected_runtime_checks_if_complete': 4283,
            'expected_saved_states_if_complete': 52,
            'runtime_executed': False, 'product_pass_claimed': False,
            'native_windows_verified': False,
            'scope': 'Static source preservation only; successful full runtime counts cannot be inferred.'}


def draft_texts():
    text = original_window()
    replacements = [
        ("_SOURCE125_GUARD_SHA256 = '" + OLD_GUARD + "'", '_SOURCE125_GUARD_SHA256 = None'),
        ('_SOURCE125_MAINTAINED_COUNT = 809', '_SOURCE125_MAINTAINED_COUNT = None'),
        ("'after_section': 140", "'after_section': 245"),
        ("'after_section':140", "'after_section':245"),
    ]
    for before, after in replacements:
        if before not in text:
            raise ValueError('Expected exact activation-only metadata was not found: ' + before)
        text = text.replace(before, after)
    launcher = (LEGACY / 'launcher125.py').read_text(encoding='utf-8')
    launcher = launcher.replace("WINDOW_SHA256 = '" + OLD_WINDOW + "'", 'WINDOW_SHA256 = None')
    launcher = launcher.replace("SOURCE125_GUARD_SHA256 = '" + OLD_GUARD + "'", 'SOURCE125_GUARD_SHA256 = None')
    if 'WINDOW_SHA256 = None' not in launcher or 'SOURCE125_GUARD_SHA256 = None' not in launcher:
        raise ValueError('Inactive launcher bindings were not obtained.')
    supervisor = (LEGACY / 'supervisor125.py').read_text(encoding='utf-8').replace("'after_section': 140", "'after_section': 245")
    return text, launcher, supervisor


def prepare(bundle):
    bundle.mkdir(parents=True, exist_ok=False)
    window, launcher, supervisor = draft_texts()
    for name, text in [('window.py', window), ('launcher125.py', launcher), ('supervisor125.py', supervisor)]:
        (bundle / name).write_text(text, encoding='utf-8')
    for name in ('bridge125.py', 'expected-map125.json'):
        shutil.copyfile(LEGACY / name, bundle / name)
    mapping = json.loads((LEGACY / 'expected-map125.json').read_bytes())
    for pin in mapping['proof_files'].values():
        relative = Path(pin['path'])
        if relative.is_absolute() or '..' in relative.parts or relative.parts[0] != 'proofs':
            raise ValueError('Historical proof path escaped its public namespace.')
        path = LEGACY / relative
        raw = path.read_bytes()
        if len(raw) != pin['bytes'] or sha(raw) != pin['sha256']:
            raise ValueError('Historical measured proof bytes changed: ' + pin['path'])
        target = bundle / relative; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    static = audit(window)
    write_json(bundle / 'static-preservation.json', static)
    write_json(bundle / 'activation.json', {
        'status': 'INACTIVE_DRAFT', 'candidate_after_section': SECTION,
        'binding_ready': False, 'runtime_executed': False,
        'original_basis_window_sha256': OLD_WINDOW,
        'draft_sha256': {name: sha((bundle / name).read_bytes()) for name in
                         ('window.py', 'launcher125.py', 'supervisor125.py', 'bridge125.py', 'expected-map125.json')},
        'source_guard_created': False, 'product_pass_claimed': False,
        'activation_requirement': 'Root must freeze section245 source and explicitly request activation.'})
    return static


def current_sources():
    result = {}
    for folder in ('rouge', 'tests', 'scripts'):
        for path in sorted((ROOT / folder).rglob('*')):
            relative = path.relative_to(ROOT)
            if '__pycache__' in relative.parts or path.suffix not in ('.py', '.json'):
                continue
            if path.is_symlink():
                raise ValueError('Maintained source symlink is not accepted: ' + str(relative))
            if path.is_file():
                result[relative.as_posix()] = sha(path.read_bytes())
    return dict(sorted(result.items()))


def git(*arguments):
    return subprocess.check_output(['git', *arguments], cwd=ROOT, text=True).strip()


def activate(bundle, expected_parent_commit):
    record = json.loads((bundle / 'activation.json').read_bytes())
    if record['status'] != 'INACTIVE_DRAFT' or record['binding_ready']:
        raise ValueError('Only a fresh inactive draft can be activated.')
    for name, digest in record['draft_sha256'].items():
        if sha((bundle / name).read_bytes()) != digest:
            raise ValueError('Prepared source changed before activation: ' + name)
    if git('branch', '--show-current') != 'codex/p2-development':
        raise ValueError('The active development branch is wrong.')
    parent = git('rev-parse', 'HEAD')
    if parent != expected_parent_commit:
        raise ValueError('Root frozen parent commit differs from actual HEAD.')
    maintained = current_sources()
    old_guard = json.loads((ROOT / 'verification/full-140/source-guard.json').read_bytes())
    additional = {name: sha((ROOT / name).read_bytes()) for name in old_guard['source_additional_sha256']}
    bridge = {name: sha((bundle / name).read_bytes()) for name in ('bridge125.py', 'expected-map125.json')}
    guard = {'section': SECTION, 'product_commit': parent, 'tested_worktree_parent_commit': parent,
             'pending_functional_section_source': SECTION, 'source_sha256': maintained,
             'source_additional_sha256': additional, 'full125_113_bridge_sha256': bridge,
             'basis_section': 140, 'old140_source_guard_reused': False,
             'scope': 'Actual frozen maintained worktree source; product_commit is its parent HEAD, not a claim that pending245 is already committed.',
             'native_windows_verified': False, 'runtime_executed': False}
    write_json(bundle / OUTPUT_GUARD_NAME, guard)
    guard_digest = sha((bundle / OUTPUT_GUARD_NAME).read_bytes())
    text = (bundle / 'window.py').read_text(encoding='utf-8')
    text = text.replace('_SOURCE125_GUARD_SHA256 = None', "_SOURCE125_GUARD_SHA256 = '" + guard_digest + "'")
    text = text.replace('_SOURCE125_MAINTAINED_COUNT = None', '_SOURCE125_MAINTAINED_COUNT = ' + str(len(maintained)))
    static = audit(text)
    (bundle / 'window.py').write_text(text, encoding='utf-8')
    window_digest = sha((bundle / 'window.py').read_bytes())
    launcher = (bundle / 'launcher125.py').read_text(encoding='utf-8')
    launcher = launcher.replace('WINDOW_SHA256 = None', "WINDOW_SHA256 = '" + window_digest + "'")
    launcher = launcher.replace('SOURCE125_GUARD_SHA256 = None', "SOURCE125_GUARD_SHA256 = '" + guard_digest + "'")
    (bundle / 'launcher125.py').write_text(launcher, encoding='utf-8')
    if current_sources() != maintained or git('rev-parse', 'HEAD') != parent:
        raise ValueError('Production source changed while activating the current guard.')
    write_json(bundle / 'static-preservation.json', static)
    record.update(status='CURRENT_SOURCE_BOUND_NOT_EXECUTED', binding_ready=True,
                  tested_worktree_parent_commit=parent, maintained_source_count=len(maintained),
                  actual_guard_sha256=guard_digest, runtime_executed=False, product_pass_claimed=False,
                  actual_source_sha256={name: sha((bundle / name).read_bytes()) for name in
                                       ('window.py', 'launcher125.py', 'supervisor125.py', 'bridge125.py', 'expected-map125.json')})
    write_json(bundle / 'activation.json', record)
    return {'status': record['status'], 'maintained_source_count': len(maintained),
            'guard_sha256': guard_digest, 'window_sha256': window_digest,
            'runtime_executed': False, 'product_pass_claimed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument('--prepare', action='store_true')
    operation.add_argument('--activate', action='store_true')
    parser.add_argument('--expected-parent-commit')
    args = parser.parse_args(); bundle = args.bundle.resolve()
    if not bundle.is_relative_to((ROOT / 'work').resolve()):
        raise ValueError('The draft/activation bundle must remain in project work/.')
    if args.activate and not re.fullmatch('[0-9a-f]{40}', args.expected_parent_commit or ''):
        raise ValueError('Activation requires root supplied exact parent HEAD.')
    print(json.dumps(prepare(bundle) if args.prepare else activate(bundle, args.expected_parent_commit), ensure_ascii=False))
