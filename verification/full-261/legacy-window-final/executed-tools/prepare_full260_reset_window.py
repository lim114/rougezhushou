"""Inactive full-scope maintenance window with only a False-to-None reset hook.

The old831 assertions,552-assert functional try and all old expectations remain
identical. Never runs Wine; activation is separate after section260 maintenance.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
spec = importlib.util.spec_from_file_location('_legacy_full245_activation', BASE / 'activate_full245_window.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
module.SECTION = 260


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(bundle):
    proof = json.loads((BASE / 'control-reset-proof.json').read_bytes())
    if proof.get('actual_Wine_Qt_MainWindow_tests_passed') != 3:
        raise ValueError('Independent real control/consumer proof has not passed.')
    actual_class = ROOT / 'rouge/susuro_healing_view.py'
    if digest(actual_class) != proof['class_source_sha256']:
        raise ValueError('The independently checked actual recipient class changed.')
    module.prepare(bundle)
    shutil.copyfile(BASE / 'control_reset_compat.py', bundle / 'control_reset_compat.py')
    shutil.copyfile(BASE / 'control-reset-proof.json', bundle / 'control-reset-proof.json')
    compat_sha = digest(bundle / 'control_reset_compat.py')
    window = (bundle / 'window.py').read_text(encoding='utf-8')
    window = window.replace("'after_section':245", "'after_section':260").replace("'after_section': 245", "'after_section': 260")
    bootstrap = '''
# BEGIN SOURCE-BOUND FALSE-ONLY RATIO RESET HARNESS
import atexit as _reset_exit260
import importlib.util as _reset_import260
_reset_path260 = Path(__file__).with_name('control_reset_compat.py')
if hashlib.sha256(_reset_path260.read_bytes()).hexdigest() != '%s':
    raise AssertionError('False-only reset harness source changed')
_reset_spec260 = _reset_import260.spec_from_file_location('_actual_ratio_reset260', _reset_path260)
_reset_module260 = _reset_import260.module_from_spec(_reset_spec260)
_reset_spec260.loader.exec_module(_reset_module260)
_reset_restore260, _reset_write260, _reset_ledger260 = _reset_module260.install(ROOT, '%s', OUT)
_reset_exit260.register(_reset_restore260)
_reset_exit260.register(_reset_write260)
# END SOURCE-BOUND FALSE-ONLY RATIO RESET HARNESS
''' % (compat_sha, proof['class_source_sha256'])
    marker = '\ntry:\n    for name in (\'PySide6.QtWidgets\''
    if window.count(marker) != 1:
        raise ValueError('Original main functional try bootstrap boundary is ambiguous.')
    window = window.replace(marker, '\n' + bootstrap + marker)
    (bundle / 'window.py').write_text(window, encoding='utf-8')
    supervisor = (bundle / 'supervisor125.py').read_text(encoding='utf-8').replace("'after_section': 245", "'after_section': 260")
    (bundle / 'supervisor125.py').write_text(supervisor, encoding='utf-8')
    audit = module.audit(window)
    audit.update(false_reset_harness_only=True, unknown_ratio_kept_None=True,
                 true_or_numeric_ratio_alias_supported=False, actual_consumer_qualified_stays_unknown=True,
                 old_expected_values_modified=False, raw_calculation_results_rewritten=False,
                 independent_reset_proof_sha256=digest(bundle / 'control-reset-proof.json'))
    module.write_json(bundle / 'static-preservation.json', audit)
    record = json.loads((bundle / 'activation.json').read_bytes())
    record.update(candidate_after_section=260, purpose='maintenance_after_functional_section260',
                  false_only_reset_source_sha256=compat_sha,
                  independent_reset_proof_sha256=digest(bundle / 'control-reset-proof.json'),
                  original245_failure_preserved='verification/full-245/old-window evidence',
                  draft_sha256={name: digest(bundle / name) for name in
                                ('window.py', 'launcher125.py', 'supervisor125.py', 'bridge125.py', 'expected-map125.json',
                                 'control_reset_compat.py', 'control-reset-proof.json')})
    module.write_json(bundle / 'activation.json', record)
    return audit


def activate(bundle, expected_parent_commit):
    proof = json.loads((bundle / 'control-reset-proof.json').read_bytes())
    if digest(ROOT / 'rouge/susuro_healing_view.py') != proof['class_source_sha256']:
        raise ValueError('Recipient class changed after its independent proof; revalidate before activation.')
    writer = module.write_json

    def write_current_guard(path, value):
        if path.name == module.OUTPUT_GUARD_NAME:
            for name in ('control_reset_compat.py', 'control-reset-proof.json'):
                relative = (bundle / name).relative_to(ROOT).as_posix()
                value['source_additional_sha256'][relative] = digest(bundle / name)
            value.pop('pending_functional_section_source', None)
            value.update(maintenance_after_section=260, functional_section_count_increased=False,
                         false_only_ratio_reset_compatibility=True,
                         raw_calculation_results_modified=False, original_expectations_modified=False,
                         scope='Actual frozen maintenance worktree after functional section260; product_commit is its parent HEAD, not a completed maintenance commit.')
        writer(path, value)
    module.write_json = write_current_guard
    try:
        return module.activate(bundle, expected_parent_commit)
    finally:
        module.write_json = writer


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument('--prepare', action='store_true')
    operation.add_argument('--activate', action='store_true')
    parser.add_argument('--expected-parent-commit')
    args = parser.parse_args(); bundle = args.bundle.resolve()
    if not bundle.is_relative_to((ROOT / 'work').resolve()):
        raise ValueError('Future maintenance candidate stays in work/.')
    if args.activate and not args.expected_parent_commit:
        raise ValueError('Root frozen maintenance parent HEAD is required for activation.')
    print(json.dumps(prepare(bundle) if args.prepare else activate(bundle, args.expected_parent_commit), ensure_ascii=False))
