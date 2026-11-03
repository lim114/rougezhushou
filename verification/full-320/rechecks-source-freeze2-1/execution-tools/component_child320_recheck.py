"""Run one fresh320 component after exact source/activation guards only."""
import argparse
import json
import os
from pathlib import Path
import runpy
import sys
import traceback

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'.cache/full320-attempt2-prep'))
from full320_common import BASE, ROOT, bound, sha, write_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', required=True); parser.add_argument('--out', type=Path, required=True)
    for name in ('expected-parent-commit', 'freeze-sha256', 'activation-sha256'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    data, activation = bound(args.expected_parent_commit, args.freeze_sha256, args.activation_sha256)
    if args.mode not in ('p3_298','p3_311','p3_312'):
        raise ValueError('Only explicitly frozen complete components are allowed.')
    out = args.out.resolve()
    if not args.out.is_absolute() or out.is_relative_to(ROOT) or out.exists(): raise ValueError('Fresh owned external component output required.')
    if args.mode == 'offline':
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        target = ROOT / 'scripts/verify_full_available.py'; out.mkdir(parents=True)
        receipt_path = out / 'windows-offline.json'
        argv = [str(target), '--output', str(receipt_path), '--verbosity', '2']
    elif args.mode in ('legacy', 'current30', 'current29'):
        os.environ['QT_QPA_PLATFORM'] = 'windows'
        bundle = BASE / ('bound-legacy' if args.mode == 'legacy' else 'bound-current')
        target = bundle / 'launcher275.py'
        argv = [str(target), '--root', str(ROOT), '--out', str(out), '--mode', args.mode]
        receipt_path = out / ('wine-ui-100.json' if args.mode == 'legacy' else 'window.json')
    else:
        os.environ['QT_QPA_PLATFORM'] = 'windows'
        relative = data['p3_scripts'][args.mode]; target = ROOT / relative
        if sha(target) != data['source_sha256'][relative]: raise ValueError('Frozen canonical native script changed.')
        out.mkdir(parents=True); receipt_path = out / 'window.json'
        argv = [str(target), '--receipt', str(receipt_path)]
        if data['p3_script_options'][args.mode]['accepts_visible_ms']:
            argv.extend(['--visible-ms', '300000' if args.mode=='p3_311' else '120000'])  # 311 timing diagnosis with profiling;298/312 original defaults.
    code = None; error = None; cleanup = None; cleanup_error = None
    import cProfile,pstats
    profiler=cProfile.Profile() if args.mode=='p3_311' else None
    if profiler is not None:profiler.enable()
    sys.path[:0] = [str(ROOT), str(ROOT / 'scripts'), str(target.parent)]
    sys.argv = argv
    try:
        runpy.run_path(str(target), run_name='__main__')
        code = 0  # Normal interpreter return; the actual receipt must independently pass.
    except SystemExit as event:
        code = event.code if type(event.code) is int else 0 if event.code is None else 1
    except BaseException as event:
        code = 1; error = {'type': type(event).__name__, 'message': str(event), 'traceback': traceback.format_exc()}
    finally:
        if profiler is not None:
            profiler.disable()
            rows=[]
            for (filename,line,name),(primitive,calls,internal,cumulative,callers) in pstats.Stats(profiler).stats.items():
                path=Path(filename)
                if path.is_absolute() and path.is_relative_to(ROOT) and path.parts and path.suffix=='.py':
                    rows.append({'file':path.relative_to(ROOT).as_posix(),'line':line,'function':name,'calls':calls,'primitive_calls':primitive,'internal_seconds':internal,'cumulative_seconds':cumulative})
            rows.sort(key=lambda x:x['cumulative_seconds'],reverse=True)
            write_new(out/'timing-profile-public-functions.json',{'kind':'observed_cProfile_not_a_performance_PASS','profile_overhead_present':True,'complete_product_and_fixture_source_unchanged':True,'functions':rows[:100]})
        # The original full offline/legacy launchers own their established cleanup.
        # Canonical supplements can leave wrappers alive until this explicit end.
        if args.mode in data['p3_scripts']:
            try:
                from qt_verification_cleanup import shutdown_verification_qt
                cleanup = shutdown_verification_qt()
            except BaseException as event:
                cleanup_error = {'type': type(event).__name__, 'message': str(event), 'traceback': traceback.format_exc()}
    after_error = None
    try: bound(args.expected_parent_commit, args.freeze_sha256, args.activation_sha256)
    except BaseException as event:
        after_error = {'type': type(event).__name__, 'message': str(event), 'traceback': traceback.format_exc()}
    raw = json.loads(receipt_path.read_bytes()) if receipt_path.is_file() else None
    if args.mode == 'offline':
        raw_passed = bool(raw and raw.get('available_checks_passed') is True
                          and raw.get('source_sha256') == data['source_sha256'] and raw.get('selectors') == data['selectors']
                          and raw.get('failures') == raw.get('errors') == 0 and raw.get('source_drift') == [])
    else:
        raw_passed = bool(raw and raw.get('passed') is True)
    passed = code == 0 and error is None and cleanup_error is None and after_error is None and raw_passed
    record = {'section': 320, 'kind': 'FULL320_SAME_SOURCE_ORIGINAL298_DEADLINE_RECHECK_CLOSURE', 'mode': args.mode,
              'actual_target': str(target), 'actual_target_sha256': sha(target), 'actual_argv': argv,
              'root_freeze_sha256': args.freeze_sha256, 'activation_sha256': args.activation_sha256,
              'actual_fixture_exit': code, 'fixture_exception': error, 'source_guard_exception_after': after_error,
              'qt_cleanup': cleanup, 'qt_cleanup_error': cleanup_error,
              'actual_receipt_exists': raw is not None, 'actual_receipt_file': receipt_path.name,
              'actual_receipt_sha256': sha(receipt_path) if raw is not None else None,
              'actual_receipt_passed': raw_passed, 'component_automated_passed': passed,
              'PNG_visual_inspection_claimed': False, 'historical_Windows_game_chat_verified': False}
    out.mkdir(parents=True, exist_ok=True)
    write_new(out / 'full320-source-closure.json', record)
    print(json.dumps({key: record[key] for key in ('mode', 'actual_fixture_exit', 'actual_receipt_exists', 'component_automated_passed')}, ensure_ascii=False))
    return 0 if passed else code if type(code) is int and code != 0 else 1


if __name__ == '__main__': raise SystemExit(main())
