"""Root-only original743 squad reuse observations; author executes no project.

Only public JSON and fresh output paths are used. This is an observation probe,
not a candidate test, full batch verification, or evidence of native Windows.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
import traceback

NATIVE_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
RUNSTATE_SHA = '1b6f66e7f864238880c5214f431da042e94c7fd7def8103352439609bbfd35d9'
RUN_CONFIG_SHA = 'e35262ce5fc74db31ea80704f5689bb05619fd9dc9798a334f8cac3455b4ac99'
CORE_SHA = 'a75d9497ce34f68de787e3ba99704741f2c873c2c5fa9b5de01e6620b1f00f89'
FIXTURE_MANIFEST_SHA = '00afcd6e4ea531e818cf1422a0a98331b1d12bccfb117f6c36219709220903a2'
CASE_COUNT = 17


def sha(value):
    return hashlib.sha256(value).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False,
                                    indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def disk_snapshot(path):
    return {name: {'exists': p.exists(), 'bytes': p.read_bytes() if p.exists() else None}
            for name, p in [('run', path), ('temporary', path.with_suffix('.tmp'))]}


def exception_record(error):
    return {'type': type(error).__name__, 'message': str(error),
            'traceback': ''.join(traceback.format_exception(
                type(error), error, error.__traceback__))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--guard', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    guard_path = Path(args.guard).resolve()
    output = Path(args.out).resolve()
    artifact = Path(__file__).resolve().parent
    assert not output.exists() and output != root and root not in output.parents
    assert artifact != root and root not in artifact.parents
    guard_raw = guard_path.read_bytes()
    guard = json.loads(guard_raw)
    expected = guard.get('source_sha256', guard.get('source_sha256_after'))
    assert type(expected) is dict and len(expected) == 743
    assert expected['rouge/run_state.py'] == RUNSTATE_SHA
    assert expected['rouge/run_config.py'] == RUN_CONFIG_SHA
    assert guard.get('source_additional_sha256') == {'CORE_0.70_VERIFICATION.json': CORE_SHA}
    assert sha((root / 'CORE_0.70_VERIFICATION.json').read_bytes()) == CORE_SHA
    native_path = artifact / 'native_evidence.py'
    assert not native_path.is_symlink() and sha(native_path.read_bytes()) == NATIVE_SHA
    fixture_manifest_path = artifact / 'fixture-manifest.json'
    assert not fixture_manifest_path.is_symlink()
    manifest_raw = fixture_manifest_path.read_bytes()
    assert sha(manifest_raw) == FIXTURE_MANIFEST_SHA
    fixture_manifest = json.loads(manifest_raw)
    cases = fixture_manifest['cases']
    assert type(cases) is list and len(cases) == CASE_COUNT
    assert len({case['id'] for case in cases}) == CASE_COUNT
    for case in cases:
        assert type(case['id']) is str and Path(case['id']).name == case['id']
        assert case['id'] not in ('', '.', '..')
    for row in fixture_manifest['files']:
        name = row['path']
        assert type(name) is str and Path(name).name == name and name not in ('', '.', '..')
        path = artifact / 'fixtures' / name
        assert not path.is_symlink() and path.is_file()
        raw = path.read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    assert set(row['path'] for row in fixture_manifest['files']) == {
        case['saved_file'] for case in cases} | {case['observed_file'] for case in cases}
    sys.dont_write_bytecode = True
    from native_evidence import source_map, freeze, assert_native_equal, write_record
    assert source_map(root) == expected
    output.mkdir(parents=True)
    (output / 'public-state').mkdir()
    (output / 'native').mkdir()
    rows = []
    native_rows = []
    finished = threading.Event()
    active = {'case': 'preimport', 'phase': 'preimport'}
    receipt = {
        'kind': 'ROOT_ACTUAL_ORIGINAL743_SQUAD_REUSE_OBSERVATIONS',
        'observation_only': True, 'product_pass': False, 'observation_complete': False,
        'author_Source_only': True,
        'runner_sha256': sha(Path(__file__).read_bytes()),
        'native_helper_sha256': NATIVE_SHA,
        'fixture_manifest_sha256': FIXTURE_MANIFEST_SHA,
        'source_guard_path': str(guard_path), 'source_guard_sha256': sha(guard_raw),
        'source_before': expected, 'CORE_before': CORE_SHA,
        'started_at_UTC': datetime.now(timezone.utc).isoformat(),
        'deadline_seconds': 120, 'rows': rows, 'native_records': native_rows,
        'private_state_access': False, 'game_chat_sampling_executed': False,
        'ocr_executed': False, 'Qt_executed': False, 'native_windows_verified': False,
    }
    start = time.perf_counter()

    def deadline():
        if not finished.wait(120):
            write_json(output / 'timeout.json', {
                'product_pass': False, 'active': active,
                'elapsed_seconds': time.perf_counter() - start,
                'reason': 'Root120sOriginalLinuxSquadProbeBudget',
            })
            os._exit(124)

    def save_native(kind, case_id, phase, value):
        metadata = write_record(output / 'native', len(native_rows) + 1, value)
        metadata.update({'kind': kind, 'case': case_id, 'phase': phase})
        native_rows.append(metadata)
        return metadata

    threading.Thread(target=deadline, daemon=True).start()
    sys.path.insert(0, str(root))
    try:
        from rouge.run_state import RunState
        from rouge.run_config import confirmed_config

        def observe_reuse(run, path, case_id, phase):
            active['phase'] = phase
            state_before = freeze(run.state)
            disks_before = freeze(disk_snapshot(path))
            context = None
            result = None
            observation = {
                'context_error': None, 'lookup_error': None,
                'context_invoked': True, 'confirmed_config_invoked': False,
            }
            try:
                context = run.recognition_context()
            except Exception as error:
                observation['context_error'] = exception_record(error)
            context_before = freeze(context)
            if observation['context_error'] is None:
                observation['confirmed_config_invoked'] = True
                try:
                    result = confirmed_config(context)
                except Exception as error:
                    observation['lookup_error'] = exception_record(error)
            assert_native_equal(context, context_before, 'confirmed_config preserves context caller')
            assert_native_equal(run.state, state_before, 'reuse view preserves live state')
            assert_native_equal(disk_snapshot(path), disks_before, 'reuse view preserves disk and tmp')
            observation['result'] = result
            observation['native_evidence'] = save_native('actual-reuse-consumer', case_id, phase, {
                'state_before': state_before, 'state_after': run.state,
                'context_before': context_before, 'context_after': context,
                'disks_before': disks_before, 'disks_after': disk_snapshot(path),
                'result': result, 'context_error': observation['context_error'],
                'lookup_error': observation['lookup_error'],
            })
            return observation

        for case in cases:
            case_id = case['id']
            active.update({'case': case_id, 'phase': 'constructor'})
            directory = output / 'public-state' / case_id
            directory.mkdir()
            path = directory / 'run.json'
            saved_raw = (artifact / 'fixtures' / case['saved_file']).read_bytes()
            path.write_bytes(saved_raw)
            path.with_suffix('.tmp').write_bytes(b'public-section103-squad-preexisting-temporary-sentinel\n')
            original_disks = freeze(disk_snapshot(path))
            row = {
                'id': case_id, 'source_scope': case['source_scope'],
                'saved_json_sha256': sha(saved_raw), 'loader_accepted': None,
                'loader_error': None, 'apply_result': None, 'apply_error': None,
                'restart_error': None,
            }
            rows.append(row)
            try:
                run = RunState(path)
            except Exception as error:
                row['loader_error'] = exception_record(error)
                row['loader_evidence'] = save_native('actual-constructor-exception', case_id, 'constructor', {
                    'disks_before': original_disks, 'disks_after': disk_snapshot(path),
                    'loader_error': row['loader_error'],
                })
                write_json(output / 'observations.json', receipt)
                continue
            row['loader_accepted'] = not run.preserve_unreadable
            row['loaded_run_id'] = run.state['id']
            row['loader_evidence'] = save_native('actual-constructor', case_id, 'constructor', {
                'state': run.state, 'disks_before': original_disks,
                'disks_after': disk_snapshot(path), 'preserve_unreadable': run.preserve_unreadable,
            })
            row['cached_reuse'] = observe_reuse(run, path, case_id, 'cached-view')
            active['phase'] = 'authorized-fresh-observation-save'
            observed_raw = (artifact / 'fixtures' / case['observed_file']).read_bytes()
            observed = json.loads(observed_raw)
            captured_at = case['captured_at_after']
            caller_before = freeze((observed, captured_at))
            state_before = freeze(run.state)
            disks_before = freeze(disk_snapshot(path))
            try:
                row['apply_result'] = run.apply(observed, captured_at)
            except Exception as error:
                row['apply_error'] = exception_record(error)
            assert_native_equal((observed, captured_at), caller_before, 'actual apply preserves caller')
            row['disk_phase'] = ('authorized_observation_save' if row['apply_result'] is True
                                 else 'no_successful_observation_save')
            row['apply_evidence'] = save_native('actual-fresh-squad-RunState.apply', case_id, 'authorized-fresh-observation-save', {
                'caller_before': caller_before, 'caller_after': (observed, captured_at),
                'state_before': state_before, 'state_after': run.state,
                'disks_before': disks_before, 'disks_after': disk_snapshot(path),
                'apply_result': row['apply_result'], 'apply_error': row['apply_error'],
            })
            row['fresh_reuse'] = observe_reuse(run, path, case_id, 'fresh-view-after-save')
            active['phase'] = 'restart'
            restart_disks_before = freeze(disk_snapshot(path))
            restarted = None
            try:
                restarted = RunState(path)
            except Exception as error:
                row['restart_error'] = exception_record(error)
                row['restart_evidence'] = save_native('actual-restart-exception', case_id, 'restart', {
                    'disks_before': restart_disks_before, 'disks_after': disk_snapshot(path),
                    'restart_error': row['restart_error'],
                })
            if restarted is not None:
                row['restart_loader_accepted'] = not restarted.preserve_unreadable
                row['restart_run_id'] = restarted.state['id']
                row['restart_evidence'] = save_native('actual-restart', case_id, 'restart', {
                    'state': restarted.state, 'disks_before': restart_disks_before,
                    'disks_after': disk_snapshot(path), 'preserve_unreadable': restarted.preserve_unreadable,
                })
                row['restart_reuse'] = observe_reuse(restarted, path, case_id, 'restart-view')
            write_json(output / 'observations.json', receipt)
        receipt['source_after'] = source_map(root)
        assert receipt['source_after'] == expected
        receipt['CORE_after'] = sha((root / 'CORE_0.70_VERIFICATION.json').read_bytes())
        assert receipt['CORE_after'] == CORE_SHA and guard_path.read_bytes() == guard_raw
        receipt['observation_complete'] = True
    except BaseException as error:
        receipt['fatal'] = exception_record(error)
        raise
    finally:
        finished.set()
        receipt['elapsed_seconds'] = time.perf_counter() - start
        receipt['ended_at_UTC'] = datetime.now(timezone.utc).isoformat()
        write_json(output / 'observations.json', receipt)
    print(json.dumps({'observation_complete': receipt['observation_complete'],
                      'product_pass': False, 'rows': len(rows),
                      'native_records': len(native_rows)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
