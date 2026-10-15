"""Run the unchanged complete offline suite only after root290 binding.

This file is prepared, not executed as a suite by the preparation worker.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if sys.platform != 'win32' or args.root.resolve() != ROOT:
        raise ValueError('Exact native Windows project root required')
    out = args.out.resolve()
    if not args.out.is_absolute() or out.is_relative_to(ROOT) or out.exists():
        raise ValueError('Use a fresh absolute receipt path outside the repository')
    binding = json.loads((HERE / 'activation275.json').read_bytes())
    if binding['status'] != 'CURRENT290_SOURCE_BOUND_NOT_EXECUTED' or binding['binding_ready'] is not True:
        raise ValueError('Root must declare/bind final290 before any full suite')
    for name, expected in binding['execution_tools_sha256'].items():
        if sha(HERE / name) != expected:
            raise ValueError('Reviewed runtime tool changed: ' + name)
    freeze = ROOT / binding['root_freeze_relative']
    if sha(freeze) != binding['root_freeze_sha256']:
        raise ValueError('Root source-freeze bytes changed')
    frozen = json.loads(freeze.read_bytes())
    for name, expected in {**frozen['source_sha256'], **frozen['supplemental_public_inputs_sha256']}.items():
        if sha(ROOT / name) != expected:
            raise ValueError('Frozen source changed: ' + name)
    sys.argv = [str(ROOT / 'scripts/verify_full_available.py'), '--output', str(out)]
    code, error = None, None
    try:
        runpy.run_path(str(ROOT / 'scripts/verify_full_available.py'), run_name='__main__')
    except SystemExit as event:
        code = event.code
    except BaseException as exc:
        code = 1
        error = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
    drift = [name for name, expected in {**frozen['source_sha256'], **frozen['supplemental_public_inputs_sha256']}.items() if sha(ROOT / name) != expected]
    raw = json.loads(out.read_bytes()) if out.is_file() else None
    record = {'kind': 'SECTION290_ACTUAL_NATIVE_OFFLINE_FREEZE_CLOSURE',
              'actual_suite_exit': code, 'exception': error,
              'actual_receipt_exists': raw is not None,
              'root_freeze_sha256': binding['root_freeze_sha256'], 'source_drift': drift,
              'suite_source_map_matches_root_freeze': bool(raw and raw['source_sha256'] == frozen['source_sha256']),
              'actual_selector_list_matches_root_freeze': bool(raw and raw['selectors'] == frozen['selectors']),
              'actual_suite_receipt_sha256': sha(out) if out.is_file() else None,
              'Linux_Wine_or_game_chat_history_verified': False,
              'unavailable_records_are_not_passed': True, 'root_full_source_scope_reduced': False}
    passed = (code == 0 and not error and not drift and raw is not None
              and record['suite_source_map_matches_root_freeze'] and record['actual_selector_list_matches_root_freeze']
              and raw['available_checks_passed'] is True)
    record['available_checks_passed'] = passed
    out.parent.mkdir(parents=True, exist_ok=True)
    closure = out.with_name('offline290-source-closure.json')
    with closure.open('x', encoding='utf8') as file:
        json.dump(record, file, ensure_ascii=False, indent=2)
        file.write('\n')
    return 0 if passed else code if type(code) is int and code != 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
