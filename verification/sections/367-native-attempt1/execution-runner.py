"""Copy to .cache/run367.py; run explicit local checks only after installation."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import argparse, json, os, re, subprocess, sys, traceback

ROOT = Path(__file__).resolve().parents[1]
NEW_SELECTORS = ('tests.test_current_cannot_367', 'tests.test_current_cannot_view_367')
SELECTORS = (*NEW_SELECTORS, 'tests.test_current_battle_view_314',
             'tests.test_current_reward_integration_315',
             'tests.test_current_node_readers_view_332.CurrentNodeReadersView332Tests.test_changed_catalogue_selection_repeated_open_and_unrelated_types_close',
             'tests.test_current_node_readers_view_332.CurrentNodeReadersView332Tests.test_real_bridge_damage_and_optional_current_reader_loss_keep_catalogue_text')


def enc(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('kind', choices=('source', 'necessary', 'native'))
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    if args.attempt < 1: raise ValueError('Positive unique attempt required')
    if not (ROOT / 'rouge/current_cannot_reference.py').is_file():
        raise RuntimeError('Run the installed .cache/run367.py, after candidate integration')
    output = ROOT / f'verification/sections/367-{args.kind}-attempt{args.attempt}'
    output.mkdir()  # Never overwrite any earlier attempt.
    sys.path.insert(0, str(ROOT))
    before = {}; after = {}; child = None; code = None; failure = None; native = None
    argv = []; started = datetime.now(timezone.utc).isoformat()
    try:
        from scripts.verify_current_cannot_window_367 import bound_files
        before = bound_files()
        prefix = [sys.executable, '-B', '-X', 'utf8']
        if args.kind == 'source':
            argv = prefix + ['scripts/build_current_cannot_367.py', '--source-root', str(ROOT), '--output-root', str(ROOT), '--check']
        elif args.kind == 'necessary':
            argv = prefix + ['-m', 'unittest', '-v', *SELECTORS]
        else:
            argv = prefix + ['scripts/verify_current_cannot_window_367.py', '--receipt', str(output / 'actual/window.json'), '--visible-ms', '120000']
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', QT_QPA_PLATFORM='windows' if args.kind == 'native' else 'offscreen')
        with (output / 'stdout.txt').open('xb') as stdout, (output / 'stderr.txt').open('xb') as stderr:
            child = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, env=env)
            code = child.wait()
        path = output / 'actual/window.json'
        if path.is_file(): native = json.loads(path.read_bytes())
        after = bound_files()
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    log_path = output / 'stderr.txt'
    log = log_path.read_text('utf8', errors='replace') if log_path.exists() else ''
    match = re.search(r'Ran (\d+) tests? in ([\d.]+)s', log)
    success = failure is None and code == 0 and bool(before) and before == after
    if args.kind == 'necessary': success = success and match is not None and int(match[1]) > 0
    if args.kind == 'native': success = success and native is not None and native.get('passed') is True
    record = {'section': 367, 'kind': args.kind, 'argv': argv,
              'retained_popen_pid': child.pid if child else None, 'actual_observed_exit': code, 'exit_code': code,
              'start_utc': started, 'finish_utc': datetime.now(timezone.utc).isoformat(),
              'source_sha256_before': before, 'source_sha256_after': after,
              'source_unchanged': bool(before) and before == after,
              'source_guard_is_selected_not_all_transitive_dependencies': True,
              'methods_ran': int(match[1]) if match else None,
              'selectors': list(SELECTORS) if args.kind == 'necessary' else None,
              'full_validation_rerun': False, 'passed': bool(success), 'failure': failure,
              'descendant_job_closure_claimed': False, 'outer_process_timeout_provided_by_this_wrapper': False,
              'section_completed_or_published': False, 'batch_pause_state_changed': False}
    if native is not None:
        path = output / 'actual/window.json'
        record.update(actual_fixture_pid=native.get('process_id'), window_receipt=path.relative_to(ROOT).as_posix(),
                      window_receipt_sha256=sha256(path.read_bytes()).hexdigest(), window_passed=native.get('passed'),
                      PID_equality_assumed=False)
    (output / 'process.json').write_bytes(enc(record))
    (output / 'process.exit').write_text(('unknown' if code is None else str(code)) + '\n', encoding='ascii')
    (output / 'execution-runner.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({k: v for k, v in record.items() if not k.startswith('source_sha256')}, ensure_ascii=False))
    if native is not None:
        print(json.dumps({'native_checks': native.get('unique_checks'), 'native_failure': native.get('failure')}, ensure_ascii=False))
    if not success and log: print(log[-9000:])
    return 0 if success else 1


if __name__ == '__main__': raise SystemExit(main())
