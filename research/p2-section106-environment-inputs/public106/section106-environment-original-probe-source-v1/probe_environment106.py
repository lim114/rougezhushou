"""Root-only observations of completed105 public environment consumers.

The Source author never executes this script or its helper/project imports.
Expected product errors are recorded, not converted into test success. No Qt,
OCR, real settings, desktop client, private run, game or network is accessed.
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
MANIFEST_SHA = '2e8f3e9b74a84cb9d4ef7cee49df8bc8510c6b2bc3e09afd74b94d6af32ce217'


def sha(value):
    return hashlib.sha256(value).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False,
                                    indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def disks(path):
    return {name: {'exists': item.exists(),
                   'bytes': item.read_bytes() if item.exists() else None}
            for name, item in [('run', path), ('temporary', path.with_suffix('.tmp'))]}


def error_record(error):
    return {'type': type(error).__name__, 'message': str(error),
            'traceback': ''.join(traceback.format_exception(
                type(error), error, error.__traceback__))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--guard', required=True)
    parser.add_argument('--out', required=True)
    options = parser.parse_args()
    root = Path(options.root).resolve()
    guard_path = Path(options.guard).resolve()
    output = Path(options.out).resolve()
    packet = Path(__file__).resolve().parent
    assert not output.exists() and output != root and root not in output.parents
    assert packet != root and root not in packet.parents
    guard_raw = guard_path.read_bytes()
    guard = json.loads(guard_raw)
    expected = guard.get('source_sha256', guard.get('source_sha256_after'))
    assert type(expected) is dict and len(expected) == 748
    additional = guard.get('source_additional_sha256')
    assert type(additional) is dict and set(additional) == {'CORE_0.70_VERIFICATION.json'}
    core = additional['CORE_0.70_VERIFICATION.json']
    assert type(core) is str and len(core) == 64
    assert sha((root / 'CORE_0.70_VERIFICATION.json').read_bytes()) == core
    helper_path = packet / 'native_evidence.py'
    assert not helper_path.is_symlink() and sha(helper_path.read_bytes()) == NATIVE_SHA
    manifest_path = packet / 'fixture-manifest.json'
    assert not manifest_path.is_symlink()
    manifest_raw = manifest_path.read_bytes()
    assert sha(manifest_raw) == MANIFEST_SHA
    manifest = json.loads(manifest_raw)
    assert len(manifest['cached_cases']) == 22 and len(manifest['direct_cases']) == 11
    for name, pin in manifest['target_source_sha256'].items():
        assert expected[name] == pin and sha((root / name).read_bytes()) == pin
    assert len({case['id'] for case in manifest['cached_cases'] + manifest['direct_cases']}) == 33
    for item in manifest['files']:
        name = item['path']
        assert type(name) is str and Path(name).name == name and name not in ('', '.', '..')
        path = packet / 'fixtures' / name
        assert not path.is_symlink() and path.is_file()
        raw = path.read_bytes()
        assert len(raw) == item['bytes'] and sha(raw) == item['sha256']
    assert {item['path'] for item in manifest['files']} == {
        case['saved_file'] for case in manifest['cached_cases']}
    sys.dont_write_bytecode = True
    from native_evidence import source_map, freeze, assert_native_equal, write_record
    assert source_map(root) == expected
    output.mkdir(parents=True)
    (output / 'native').mkdir()
    (output / 'public-state').mkdir()
    calls = []
    rows = []
    native_rows = []
    active = {'case': 'preimport', 'phase': 'preimport'}
    receipt = {
        'kind': 'ROOT_ACTUAL_ORIGINAL105_ENVIRONMENT_OBSERVATIONS_FOR106',
        'observation_only': True, 'product_pass': False, 'observation_complete': False,
        'author_Runtime_executed': False, 'native_windows_verified': False,
        'Qt_executed': False, 'ocr_executed': False, 'game_chat_sampling_executed': False,
        'private_state_access': False, 'deadline_seconds': 120,
        'started_at_UTC': datetime.now(timezone.utc).isoformat(),
        'runner_sha256': sha(Path(__file__).read_bytes()), 'native_helper_sha256': NATIVE_SHA,
        'fixture_manifest_sha256': MANIFEST_SHA, 'source_guard_path': str(guard_path),
        'source_guard_sha256': sha(guard_raw), 'source_before': expected, 'CORE_before': core,
        'cached_cases': 22, 'direct_cases': 11, 'rows': rows, 'calls': calls,
        'native_records': native_rows,
    }
    finished = threading.Event()
    start = time.perf_counter()

    def deadline():
        if not finished.wait(120):
            write_json(output / 'timeout.json', {'product_pass': False, 'active': active,
                'elapsed_seconds': time.perf_counter() - start, 'reason': 'Root120sOriginalProbeBudget'})
            os._exit(124)

    def save_native(kind, case, phase, value):
        record = write_record(output / 'native', len(native_rows) + 1, value)
        record.update(kind=kind, case=case, phase=phase)
        native_rows.append(record)
        return record

    def observe(case, phase, function, args, run=None, path=None):
        active.update(case=case, phase=phase)
        before = freeze((args, run.state if run is not None else None,
                         disks(path) if path is not None else None))
        result = None
        problem = None
        try:
            result = function(*args)
        except Exception as error:
            problem = error_record(error)
        after = (args, run.state if run is not None else None,
                 disks(path) if path is not None else None)
        native = save_native('pure-public-consumer', case, phase,
                             {'before': before, 'after': after, 'result': result, 'error': problem})
        assert_native_equal(after, before, case + ':' + phase + ':caller/state/disks')
        row = {'case': case, 'phase': phase, 'returned': problem is None,
               'error': problem, 'native': native, 'caller_state_disks_unchanged': True}
        if type(result) is dict:
            row['returned_keys'] = list(result)
            if 'total_damage' in result:
                row['total_damage'] = result['total_damage']
                row['total_healing'] = result.get('total_healing')
            if phase.endswith('confirmed_config'):
                row['reusable_fields'] = list(result)
        elif type(result) in (str, int, float, bool) or result is None:
            row['returned_value'] = result
        calls.append(row)
        return result, problem, row

    threading.Thread(target=deadline, daemon=True).start()
    sys.path.insert(0, str(root))
    try:
        from rouge.run_state import RunState
        from rouge.run_config import confirmed_config, difficulty_value
        from rouge.damage import calculate_damage
        from rouge.battle_preview import enemy_preview
        base = manifest['base_calculation']
        for case in manifest['direct_cases']:
            cid = case['id']
            caller = {**base, 'target_enemy': case['target'],
                      'run_config': {'difficulty': {'value': 2, 'source': 'public-normal-control'}}}
            observe(cid, 'direct_calculate_damage', calculate_damage, (caller,))
            if type(case['target']) is dict and case['target']:
                target = case['target']
                observe(cid, 'direct_enemy_preview', enemy_preview,
                        (target['stage_id'], target['enemy_id'], target['level'], caller['run_config']))
            rows.append({'id': cid, 'kind': 'direct', 'target': case['target']})
        for case in manifest['cached_cases']:
            cid = case['id']
            active.update(case=cid, phase='loader')
            directory = output / 'public-state' / cid
            directory.mkdir()
            path = directory / 'run.json'
            raw = (packet / 'fixtures' / case['saved_file']).read_bytes()
            path.write_bytes(raw)
            path.with_suffix('.tmp').write_bytes(b'public106-original-temporary-sentinel\n')
            before_disks = freeze(disks(path))
            run = RunState(path)
            assert not run.preserve_unreadable, 'fixture must reach accepted-cache consumer'
            assert_native_equal(disks(path), before_disks, 'accepted loader preserves original files')
            row = {'id': cid, 'kind': 'cached', 'loader_accepted': True,
                   'input_json_sha256': sha(raw), 'loader_disks_unchanged': True}
            rows.append(row)
            save_native('accepted-loader', cid, 'loader', {'state': run.state, 'disks': disks(path)})
            observe(cid, 'cached_summary', run.summary, (), run, path)
            context, context_error, _ = observe(cid, 'cached_recognition_context',
                                                run.recognition_context, (), run, path)
            if context_error is None:
                observe(cid, 'cached_confirmed_config', confirmed_config, (context,), run, path)
            difficulty = run.state['config']['difficulty']
            observe(cid, 'cached_difficulty_value', difficulty_value, (difficulty,), run, path)
            caller = {**base, 'run_config': run.state['config']}
            observe(cid, 'cached_calculate_damage', calculate_damage, (caller,), run, path)
            observed = json.loads(json.dumps(manifest['fresh_observation'], ensure_ascii=False))
            at = manifest['fresh_capture_at']
            fresh_before = freeze((observed, at))
            state_before = freeze(run.state)
            active.update(case=cid, phase='fresh_apply')
            try:
                applied = run.apply(observed, at)
                apply_error = None
            except Exception as error:
                applied = None
                apply_error = error_record(error)
            assert_native_equal((observed, at), fresh_before, 'fresh apply caller unchanged')
            row.update(fresh_apply_result=applied, fresh_apply_error=apply_error)
            row['fresh_apply_native'] = save_native('authorized-apply-save-phase', cid, 'fresh_apply',
                {'caller_before': fresh_before, 'caller_after': (observed, at),
                 'state_before': state_before, 'state_after': run.state,
                 'disks_before': before_disks, 'disks_after': disks(path),
                 'result': applied, 'error': apply_error})
            if applied is not True:
                continue
            observe(cid, 'fresh_summary', run.summary, (), run, path)
            fresh_context, problem, _ = observe(cid, 'fresh_recognition_context',
                                                run.recognition_context, (), run, path)
            if problem is None:
                observe(cid, 'fresh_confirmed_config', confirmed_config, (fresh_context,), run, path)
            observe(cid, 'fresh_calculate_damage', calculate_damage,
                    ({**base, 'run_config': run.state['config']},), run, path)
            disk_json = json.loads(path.read_text(encoding='utf-8'))
            persisted_disks = freeze(disks(path))
            restarted = RunState(path)
            assert not restarted.preserve_unreadable
            assert_native_equal(restarted.state, disk_json, 'reload equals real persisted JSON graph')
            assert_native_equal(disks(path), persisted_disks, 'reload pure files unchanged')
            row['restart_json_and_disks_unchanged'] = True
            save_native('real-RunState-restart', cid, 'restart',
                        {'persisted_JSON': disk_json, 'restarted': restarted.state, 'disks': disks(path)})
            restart_context, problem, _ = observe(cid, 'restart_recognition_context',
                    restarted.recognition_context, (), restarted, path)
            if problem is None:
                observe(cid, 'restart_confirmed_config', confirmed_config,
                        (restart_context,), restarted, path)
            observe(cid, 'restart_calculate_damage', calculate_damage,
                    ({**base, 'run_config': restarted.state['config']},), restarted, path)
        receipt['observation_complete'] = True
    except Exception as error:
        receipt['fatal_probe_error'] = error_record(error)
        raise
    finally:
        try:
            receipt['source_after'] = source_map(root)
            receipt['CORE_after'] = sha((root / 'CORE_0.70_VERIFICATION.json').read_bytes())
            assert receipt['source_after'] == expected and receipt['CORE_after'] == core
            receipt['source_and_CORE_unchanged'] = True
        finally:
            receipt['elapsed_seconds'] = time.perf_counter() - start
            receipt['last_active'] = dict(active)
            receipt['actual_public_consumer_calls'] = len(calls)
            receipt['actual_native_records'] = len(native_rows)
            write_json(output / 'observations.json', receipt)
            finished.set()


if __name__ == '__main__':
    main()
