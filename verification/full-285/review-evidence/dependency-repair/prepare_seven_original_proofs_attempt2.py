"""Root-only additive repair: exactly seven already SHA-declared public proofs.

Preparation agent must not invoke main(). No pinned source/tool/activation/map
is replaced; original attempt1 and its original missing-proof failure stay intact.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / '.cache/full285-preparation'
LEGACY = BASE / 'legacy'
ORIGINAL = ROOT / 'verification/full-275/legacy-window-attempt3/executed-tools'
ATTEMPT1 = Path('C:/Users/李娜/AppData/Local/Temp/rouge-full285-ec254bf0c8a64493986a510420c37811')
FREEZE = ROOT / 'verification/full-285/source-freeze.json'
EXPECTED_NAMES = {
    'original_primary': 'proofs/original-primary.exit-code',
    'original_receipt': 'proofs/original-receipt.json',
    'original_guard': 'proofs/original-guard.json',
    'candidate_primary': 'proofs/candidate-primary.exit-code',
    'candidate_receipt': 'proofs/candidate-receipt.json',
    'candidate_guard': 'proofs/candidate-guard.json',
    'pair_audit': 'proofs/pair-audit.json'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, data):
    with path.open('xb') as file:
        file.write((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
        file.flush()
        os.fsync(file.fileno())


def safe_child(base, name):
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts or relative.as_posix() != name:
        raise ValueError('Proof path must be one canonical declared relative name')
    path = base
    if base.is_symlink():
        raise ValueError('Original proof base must not be a link')
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('No symlink component may replace a proof')
    if not path.resolve().is_relative_to(base.resolve()):
        raise ValueError('Proof escaped the original base')
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply-seven-original-proofs', action='store_true', required=True)
    parser.add_argument('--expected-freeze-sha256', required=True)
    parser.add_argument('--expected-parent-commit', required=True)
    args = parser.parse_args()
    ledger_path = HERE / 'additive-dependency-ledger-attempt2.json'
    failure_path = HERE / 'additive-copy-attempt2-failure.json'
    if ledger_path.exists() or failure_path.exists():
        raise ValueError('Never overwrite a prior actual additive-copy attempt')
    if sha(FREEZE) != args.expected_freeze_sha256:
        raise ValueError('Use the unchanged real final285 freeze')
    frozen = json.loads(FREEZE.read_bytes())
    parent = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    if (frozen.get('section') != 285 or frozen.get('root_declared') is not True
            or parent != args.expected_parent_commit or frozen.get('parent_commit') != parent
            or branch != 'codex/p2-development'):
        raise ValueError('Original final285 branch/parent declaration must remain unchanged')
    binding_path = LEGACY / 'activation275.json'
    binding = json.loads(binding_path.read_bytes())
    actual_control = json.loads((ATTEMPT1 / 'orchestration.json').read_bytes())
    if (actual_control.get('status') != 'all_four_terminal'
            or actual_control['source_freeze_sha256'] != args.expected_freeze_sha256
            or sha(binding_path) != actual_control['bound_bundles']['legacy']['activation_sha256']
            or binding['root_freeze_sha256'] != args.expected_freeze_sha256):
        raise ValueError('Original attempt1/binding identity or terminal evidence changed')
    original_closure = ATTEMPT1 / 'legacy/actual/native275-launcher-closure.json'
    first = json.loads(original_closure.read_bytes())
    if first.get('passed') is not False or first['fixture_exception']['message'] != 'Escaped/nonregular artifact pin':
        raise ValueError('Preserve the genuine exact prior missing-proof failure')
    protected = {**frozen['source_sha256'], **frozen['preparation_tools_sha256'],
                 **{(LEGACY.relative_to(ROOT) / name).as_posix(): digest
                    for name, digest in binding['execution_tools_sha256'].items()},
                 binding_path.relative_to(ROOT).as_posix(): sha(binding_path),
                 FREEZE.relative_to(ROOT).as_posix(): sha(FREEZE)}
    for name, expected in protected.items():
        if sha(ROOT / name) != expected:
            raise ValueError('Do not repair by changing an already pinned file: ' + name)
    mapping_path = LEGACY / 'expected-map125.json'
    mapping = json.loads(mapping_path.read_bytes())
    if sha(mapping_path) != binding['execution_tools_sha256']['expected-map125.json']:
        raise ValueError('Original admission map must remain byte-exact')
    proofs = mapping['proof_files']
    if set(proofs) != set(EXPECTED_NAMES) or any(proofs[key]['path'] != value for key, value in EXPECTED_NAMES.items()):
        raise ValueError('Exactly the original seven proof paths, no substitute')
    values = []
    for key, pin in proofs.items():
        original = safe_child(ORIGINAL, pin['path'])
        target = safe_child(LEGACY, pin['path'])
        raw = original.read_bytes()
        if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
            raise ValueError('Original executed275 proof bytes do not match the unchanged map')
        if target.exists():
            raise ValueError('Only genuinely absent new files may be appended, never overwrite: ' + pin['path'])
        values.append((key, pin, original, target, raw))
    ledger = {'kind': 'FULL285_ADDITIVE_ORIGINAL_PROOF_CLOSURE_ATTEMPT2',
              'checked_at': datetime.now(timezone.utc).isoformat(),
              'producer_sha256': sha(Path(__file__)),
              'original_source_freeze_sha256': args.expected_freeze_sha256,
              'original_parent_commit': parent,
              'original_root_source_count': len(frozen['source_sha256']),
              'original_selector_count': len(frozen['selectors']),
              'original_activation_sha256': sha(binding_path),
              'original_expected_map_sha256': sha(mapping_path),
              'original_attempt1_legacy_failure_sha256': sha(original_closure),
              'original_protected_pin_count': len(protected),
              'original_protected_bytes_changed': False,
              'proofs_are_additive_not_in_original76_activation_tool_list': True,
              'proofs_verified_by_original_runtime_Bridge_map': True,
              'original_attempt1_not_rewritten': True,
              'full_scope_unchanged': {'assertion_AST': 862, 'main_body': 552, 'typed_states': 52,
                                       'runtime_checks': 4283, 'projection_positions': 42,
                                       'exact_bridge_indices': [18, 19, 20, 21, 38, 39, 40, 41, 44, 45]},
              'full_suite_or_window_or_legacy_attempt2_executed': False,
              'validation_passed_claimed': False, 'copied': []}
    try:
        for key, pin, original, target, raw in values:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.parent.is_symlink():
                raise ValueError('Proof parent became a link')
            with target.open('xb') as file:
                file.write(raw)
                file.flush()
                os.fsync(file.fileno())
            if sha(original) != pin['sha256'] or sha(target) != pin['sha256']:
                raise ValueError('Proof bytes changed during exclusive append')
            ledger['copied'].append({'key': key, **pin,
                                     'original_public_path': original.relative_to(ROOT).as_posix(),
                                     'new_additive_path': target.relative_to(ROOT).as_posix()})
        for name, expected in protected.items():
            if sha(ROOT / name) != expected:
                raise ValueError('Protected source/tool bytes changed during additive append: ' + name)
        if sha(original_closure) != ledger['original_attempt1_legacy_failure_sha256']:
            raise ValueError('Original failed execution receipt changed')
        ledger['all_seven_copied_byte_exact'] = len(ledger['copied']) == 7
        write_new(ledger_path, ledger)
        print(json.dumps({'exact_seven_original_proofs_appended': True,
                          'already_pinned_files_modified': False,
                          'attempt2_executed': False,
                          'ledger_sha256': sha(ledger_path)}, ensure_ascii=False))
        return 0
    except BaseException as error:
        ledger['copy_error'] = {'type': type(error).__name__, 'message': str(error)}
        ledger['partial_appended_files_preserved_no_cleanup_or_overwrite'] = True
        write_new(failure_path, ledger)
        raise


if __name__ == '__main__':
    raise SystemExit(main())
