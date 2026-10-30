"""Run one fresh425 component after exact source/activation guards only."""
import argparse
import json
import os
from pathlib import Path
import runpy
import sys
import traceback

from full425_common import BASE, ROOT, bound, sha, write_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', required=True); parser.add_argument('--out', type=Path, required=True)
    for name in ('expected-parent-commit', 'freeze-sha256', 'activation-sha256'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    data, activation = bound(args.expected_parent_commit, args.freeze_sha256, args.activation_sha256)
    if args.mode not in ('offline', 'legacy', 'current30', 'current29', *data['p3_scripts']):
        raise ValueError('Only explicitly frozen complete components are allowed.')
    out = args.out.resolve()
    if not args.out.is_absolute() or out.is_relative_to(ROOT) or out.exists(): raise ValueError('Fresh owned external component output required.')
    diagnostic=args.mode in data['diagnostic_layout_modes']
    os.environ.pop('ROUGE_DIAGNOSTIC_LAYOUT',None);os.environ.pop('ROUGE_DIAGNOSTIC_OUTPUT',None)
    if diagnostic:
        os.environ['ROUGE_DIAGNOSTIC_LAYOUT']='1';os.environ['ROUGE_DIAGNOSTIC_OUTPUT']=str(out)
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
        if data['p3_script_options'][args.mode].get('explicit_current_source_freeze'):
            argv.extend(['--source-freeze', str(__import__('full425_common').FREEZE)])
        if data['p3_script_options'][args.mode]['accepts_visible_ms'] and not data['p3_script_options'][args.mode].get('use_canonical_visible_default'):
            argv.extend(['--visible-ms', str(data['p3_script_options'][args.mode]['visible_ms'])])
    code = None; error = None; cleanup = None; cleanup_error = None
    sys.path[:0] = [str(ROOT), str(ROOT / 'scripts'), str(target.parent)]
    sys.argv = argv
    # The original historical UI fixture assumes an empty game-window list.
    # Isolate only that external dependency, like the maintained public-native
    # fixtures do. This does not test actual enumeration or game integration.
    enumeration_isolation = None
    enumeration_patches = []
    if args.mode == 'legacy':
        import rouge.capture as capture_module
        import rouge.app as app_module
        from unittest.mock import patch
        enumeration_isolation = {'kind': 'EXPLICIT_LEGACY_PUBLIC_UI_ENUMERATION_FIXTURE',
            'fixture_calls': 0, 'real_desktop_enumeration_called': False,
            'real_desktop_no_game_claimed': False, 'synthetic_empty_game_list': True,
            'game_or_capture_integration_verified': False,
            'original_552_body_and_862_assertions_unchanged': True,
            'reason': 'Original first attempt failed solely because the user game is open; no request to close or operate it. Preserve the full UI/calculation assertions in an explicitly isolated external environment.',
            'original_first_failure': 'verification/full-425/execution-attempt1/legacy/actual/wine-ui-100.json'}
        def isolated_game_windows():
            enumeration_isolation['fixture_calls'] += 1
            return []
        originals = [(capture_module, 'list_game_windows', capture_module.list_game_windows),
                     (app_module, 'list_game_windows', app_module.list_game_windows)]
        for module, name, original in originals:
            item = patch.object(module, name, isolated_game_windows)
            item.start(); enumeration_patches.append(item)
    try:
        runpy.run_path(str(target), run_name='__main__')
        code = 0  # Normal interpreter return; the actual receipt must independently pass.
    except SystemExit as event:
        code = event.code if type(event.code) is int else 0 if event.code is None else 1
    except BaseException as event:
        code = 1; error = {'type': type(event).__name__, 'message': str(event), 'traceback': traceback.format_exc()}
    finally:
        # The original full offline/legacy launchers own their established cleanup.
        # Canonical supplements can leave wrappers alive until this explicit end.
        if args.mode in data['p3_scripts']:
            try:
                from qt_verification_cleanup import shutdown_verification_qt
                cleanup = shutdown_verification_qt()
            except BaseException as event:
                cleanup_error = {'type': type(event).__name__, 'message': str(event), 'traceback': traceback.format_exc()}
    if enumeration_isolation is not None:
        for item in reversed(enumeration_patches): item.stop()
        enumeration_isolation['original_references_restored'] = all(getattr(module, name) is original for module, name, original in originals)
        enumeration_isolation['component_actual_fixture_exit'] = code
        write_new(out / 'legacy-enumeration-isolation.json', enumeration_isolation)
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
    record = {'section': 425, 'kind': 'FULL425_ACTUAL_COMPONENT_SOURCE_CLOSURE', 'mode': args.mode,
              'actual_target': str(target), 'actual_target_sha256': sha(target), 'actual_argv': argv,
              'root_freeze_sha256': args.freeze_sha256, 'activation_sha256': args.activation_sha256,
              'actual_fixture_exit': code, 'fixture_exception': error, 'source_guard_exception_after': after_error,
              'qt_cleanup': cleanup, 'qt_cleanup_error': cleanup_error,
              'actual_receipt_exists': raw is not None, 'actual_receipt_file': receipt_path.name,
              'actual_receipt_sha256': sha(receipt_path) if raw is not None else None,
              'actual_receipt_passed': raw_passed, 'component_automated_passed': passed,
              'diagnostic_layout_explicitly_requested':diagnostic,
              'diagnostic_layout_does_not_claim_default_player_presentation':True,
              'PNG_visual_inspection_claimed': False, 'historical_Windows_game_chat_verified': False}
    out.mkdir(parents=True, exist_ok=True)
    write_new(out / 'full425-source-closure.json', record)
    print(json.dumps({key: record[key] for key in ('mode', 'actual_fixture_exit', 'actual_receipt_exists', 'component_automated_passed')}, ensure_ascii=False))
    return 0 if passed else code if type(code) is int and code != 0 else 1


if __name__ == '__main__': raise SystemExit(main())
