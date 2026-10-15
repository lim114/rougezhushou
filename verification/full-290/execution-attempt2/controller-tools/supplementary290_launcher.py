"""Execute exactly one canonical286–290 native public-state window fixture."""
import argparse
import json
from pathlib import Path
import runpy
import sys
import traceback

from full290_runtime_common import ROOT, native, sha, validate_freeze, write_new

SCRIPTS = {
    'p3_286': 'scripts/verify_player_information_window_286.py',
    'p3_287': 'scripts/verify_moving_reward_window_287.py',
    'p3_288': 'scripts/verify_direct_map_window_288.py',
    'p3_289': 'scripts/verify_event_rewards_window_289.py',
    'p3_290': 'scripts/verify_recruitment_results_window_290.py',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=tuple(SCRIPTS), required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--expected-parent-commit', required=True)
    args = parser.parse_args()
    native()
    frozen = validate_freeze(args.expected_parent_commit)
    out = args.out.resolve()
    if (not args.out.is_absolute() or args.out.is_symlink()
            or out.is_relative_to(ROOT) or out.exists()):
        raise ValueError('Use a new owned absolute output outside the repository')
    relative = SCRIPTS[args.mode]
    script = ROOT / relative
    if sha(script) != frozen['source_sha256'][relative]:
        raise ValueError('Canonical native fixture does not match root freeze')
    out.mkdir(parents=True)
    receipt = out / 'p3-window.json'
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / 'scripts'))
    sys.argv = [str(script), '--receipt', str(receipt)]
    #286/288/289/290 preserve their own step timers and lower bounds.287 has
    #its canonical30-second visible window and intentionally no such option.
    if args.mode != 'p3_287':
        sys.argv += ['--visible-ms', '15000']
    argv = list(sys.argv)
    code, error, cleanup, cleanup_error = None, None, None, None
    try:
        runpy.run_path(str(script), run_name='__main__')
    except SystemExit as event:
        code = event.code
    except BaseException as exc:
        code = 1
        error = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
    finally:
        try:
            from qt_verification_cleanup import shutdown_verification_qt
            cleanup = shutdown_verification_qt()
        except BaseException as exc:
            cleanup_error = {'type': type(exc).__name__, 'message': str(exc)}
    source_error = None
    try:
        validate_freeze(args.expected_parent_commit)
    except BaseException as exc:
        source_error = {'type': type(exc).__name__, 'message': str(exc)}
    actual = json.loads(receipt.read_bytes()) if receipt.is_file() else None
    passed = (code == 0 and error is None and cleanup_error is None and source_error is None
              and actual is not None and actual.get('passed') is True)
    record = {
        'kind': 'FULL290_CANONICAL_P3_NATIVE_WINDOW_CLOSURE', 'actual_validation_attempt': 2, 'mode': args.mode,
        'canonical_script': relative, 'canonical_script_sha256': sha(script), 'actual_argv': argv,
        'root_freeze_sha256': sha(ROOT / 'verification/full-290/source-freeze-repair.json'),
        'actual_fixture_exit': code, 'fixture_exception': error,
        'source_validation_error_after': source_error, 'qt_cleanup': cleanup,
        'qt_cleanup_error': cleanup_error, 'actual_receipt_exists': actual is not None,
        'actual_receipt_sha256': sha(receipt) if receipt.is_file() else None,
        'actual_receipt_passed': actual.get('passed') if actual else None,
        'passed': passed, 'actual_window_authority_remains_in_canonical_raw_receipt': True,
        'PNG_visual_inspection_claimed': False, 'game_or_chat_or_private_data_used': False,
        'legacy52_or_current30_29_replaced': False,
    }
    write_new(out / 'supplementary290-source-closure.json', record)
    print(json.dumps({k: v for k, v in record.items() if k not in ('actual_argv', 'qt_cleanup')}, ensure_ascii=False))
    return 0 if passed else code if type(code) is int and code != 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
