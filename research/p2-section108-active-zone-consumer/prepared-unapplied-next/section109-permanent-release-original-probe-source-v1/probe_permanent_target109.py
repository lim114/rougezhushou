"""Root-only bounded original public observations of permanent release and enemy hits.

The Source author compiles this file without executing it or importing a project,
API, native helper or codec. No numerical PASS or new game-clock oracle is used.
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
MANIFEST_SHA = 'd16a6f29996304f9de3bbc570c004e38c153548512169ce93dad0be33fb95227'


def sha(value):
    return hashlib.sha256(value).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode('utf-8')
    with temporary.open('wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def error_record(error):
    return {'type': type(error).__name__, 'message': str(error),
            'traceback': ''.join(traceback.format_exception(
                type(error), error, error.__traceback__))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--guard', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--stage', choices=('focused',), default='focused')
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--limit', type=int)
    options = parser.parse_args()
    root = Path(options.root).resolve()
    guard_path = Path(options.guard).resolve()
    output = Path(options.out).resolve()
    packet = Path(__file__).resolve().parent
    assert not output.exists() and output != root and root not in output.parents
    assert output != packet and packet not in output.parents
    assert packet != root and root not in packet.parents
    assert not guard_path.is_symlink()
    guard_raw = guard_path.read_bytes()
    guard = json.loads(guard_raw)
    expected = guard.get('source_sha256', guard.get('source_sha256_after'))
    assert type(expected) is dict and expected
    assert all(type(name) is str and type(pin) is str and len(pin) == 64
               for name, pin in expected.items())
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
    assert manifest['required_future_whole_source_count'] is None
    assert manifest['required_future_whole_guard_sha256'] is None
    assert manifest['CORE_sha256'] == core
    assert set(manifest['stages']) == {'focused'}
    assert manifest['stages']['focused']['case_count'] == 40
    for name, pin in manifest['stable_original_source_sha256'].items():
        assert expected[name] == pin and sha((root / name).read_bytes()) == pin
    stage = manifest['stages'][options.stage]
    all_cases = stage['cases']
    assert len(all_cases) == stage['case_count']
    assert len({case['id'] for case in all_cases}) == len(all_cases)
    assert 0 <= options.start < len(all_cases)
    limit = stage['default_limit'] if options.limit is None else options.limit
    assert 1 <= limit <= 40
    end = min(len(all_cases), options.start + limit)
    cases = all_cases[options.start:end]
    sys.dont_write_bytecode = True
    from native_evidence import source_map, freeze, assert_native_equal, write_record
    assert source_map(root) == expected
    output.mkdir(parents=True)
    (output / 'native').mkdir()
    calls = []
    rows = []
    native_rows = []
    active = {'case': 'preimport', 'phase': 'preimport'}
    receipt = {
        'kind': 'ROOT_ACTUAL_ORIGINAL109_PERMANENT_RELEASE_SOURCE',
        'observation_only': True, 'product_pass': False, 'observation_complete': False,
        'selected_window_complete': False, 'full_stage_complete': False,
        'author_runtime_executed': False, 'native_windows_verified': False,
        'Qt_executed': False, 'ocr_executed': False, 'game_chat_sampling_executed': False,
        'private_state_access': False, 'deadline_seconds': 120,
        'started_at_UTC': datetime.now(timezone.utc).isoformat(),
        'runner_sha256': sha(Path(__file__).read_bytes()), 'native_helper_sha256': NATIVE_SHA,
        'fixture_manifest_sha256': MANIFEST_SHA, 'source_guard_path': str(guard_path),
        'source_guard_sha256': sha(guard_raw), 'source_before': expected, 'CORE_before': core,
        'actual_bound_source_count': len(expected), 'future_count_was_not_projected': True,
        'stage': options.stage, 'stage_total_cases': len(all_cases),
        'selected_start_index': options.start, 'selected_end_index_exclusive': end,
        'planned_selected_cases': len(cases), 'maximum_explicit_consumer_calls': 3 * len(cases),
        'maximum_native_records': 4 * len(cases), 'next_case_index': options.start,
        'call_count_scope': manifest['explicit_call_count_scope'],
        'rows': rows, 'calls': calls, 'native_records': native_rows,
        'unknown_boundaries': manifest['unknown_boundaries'],
        'parent_extended_inventory_is_not_required_here': True,
    }
    finished = threading.Event()
    start = time.perf_counter()

    def deadline():
        if not finished.wait(120):
            write_json(output / 'timeout.json', {
                'product_pass': False, 'observation_complete': False,
                'active': dict(active), 'elapsed_seconds': time.perf_counter() - start,
                'stage': options.stage, 'last_completed_next_case_index': receipt['next_case_index'],
                'actual_explicit_consumer_calls': len(calls), 'actual_native_records': len(native_rows),
                'reason': 'Root120sOriginalPermanentReleaseProbeBudget',
                'resume_rule': 'Retain this output/raw124. Use a fresh output and fresh actual unchanged guard; never append or backfill this receipt.'})
            os._exit(124)

    def save_native(kind, case, phase, value):
        record = write_record(output / 'native', len(native_rows) + 1, value)
        record.update(kind=kind, case=case, phase=phase)
        with (output / 'native' / 'index.jsonl').open('a', encoding='utf-8') as index:
            index.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n')
            index.flush()
            os.fsync(index.fileno())
        native_rows.append(record)
        return record

    def observe(case, phase, api, function, args):
        active.update(case=case, phase=phase)
        before = freeze(args)
        kwargs = {}
        before_kwargs = freeze(kwargs)
        result = None
        problem = None
        try:
            result = function(*args, **kwargs)
        except Exception as error:
            problem = error_record(error)
        native = save_native('original-public-consumer', case, phase,
                             {'before': before, 'after': args,
                              'kwargs_before': before_kwargs, 'kwargs_after': kwargs,
                              'result': result, 'error': problem})
        row = {'case': case, 'phase': phase, 'api': api, 'returned': problem is None,
               'error': problem, 'native': native, 'caller_unchanged': False,
               'complete_returned_value_in_native': True, 'actual_kwargs_in_native': True,
               'kwargs_unchanged': False}
        calls.append(row)
        assert_native_equal(args, before, case + ':' + phase + ':caller')
        row['caller_unchanged'] = True
        assert_native_equal(kwargs, before_kwargs, case + ':' + phase + ':kwargs')
        row['kwargs_unchanged'] = True
        if type(result) is dict:
            row['returned_keys'] = list(result)
        elif type(result) is str:
            raw = result.encode('utf-8')
            row['text_bytes'] = len(raw)
            row['text_sha256'] = sha(raw)
        return result, problem

    def checkpoint(index):
        receipt['next_case_index'] = index
        write_json(output / 'checkpoint.json', {
            'product_pass': False, 'stage': options.stage, 'source_guard_path': str(guard_path),
            'source_guard_sha256': sha(guard_raw), 'runner_sha256': receipt['runner_sha256'],
            'fixture_manifest_sha256': MANIFEST_SHA,
            'selected_start_index': options.start, 'selected_end_index_exclusive': end,
            'next_case_index': index, 'completed_selected_cases': len(rows),
            'actual_explicit_consumer_calls': len(calls), 'actual_native_records': len(native_rows),
            'elapsed_seconds': time.perf_counter() - start,
            'native_index_path': 'native/index.jsonl',
            'last_completed_native_record': native_rows[-1] if native_rows else None,
            'guard_after_still_pending': True,
            'resume_rule': 'Retain original receipts. Root may continue the next slice in a fresh output under a fresh actual complete guard; output is never overwritten.'})

    threading.Thread(target=deadline, daemon=True).start()
    sys.path.insert(0, str(root))
    completed = False
    try:
        from rouge.damage import calculate_damage
        from rouge.estimate import format_estimate
        from rouge.reporting import format_report
        for offset, case in enumerate(cases):
            cid = case['id']
            caller = freeze(case['scenario'])
            case_before = freeze(caller)
            row = {'id': cid, 'group': case['group'], 'scope_note': case['scope_note'],
                   'blocked_phases': [], 'caller_unchanged': False}
            result, problem = observe(cid, 'calculate_damage', 'rouge.damage.calculate_damage',
                                      calculate_damage, (caller,))
            if problem is None:
                observe(cid, 'format_estimate', 'rouge.estimate.format_estimate',
                        format_estimate, (result,))
                observe(cid, 'format_report', 'rouge.reporting.format_report',
                        format_report, (result,))
            else:
                row['blocked_phases'].append({'phase': 'format_estimate/format_report',
                    'reason': 'Original calculate_damage returned an error; no fabricated result is substituted.'})
            save_native('whole-case-caller-input', cid, 'case-caller',
                        {'before': case_before, 'after': caller})
            assert_native_equal(caller, case_before, cid + ':whole-case-caller')
            row['caller_unchanged'] = True
            rows.append(row)
            checkpoint(options.start + offset + 1)
        assert len(calls) <= receipt['maximum_explicit_consumer_calls']
        assert len(native_rows) <= receipt['maximum_native_records']
        completed = True
    except Exception as error:
        receipt['fatal_probe_error'] = error_record(error)
        raise
    finally:
        try:
            receipt['source_after'] = source_map(root)
            receipt['CORE_after'] = sha((root / 'CORE_0.70_VERIFICATION.json').read_bytes())
            assert receipt['source_after'] == expected and receipt['CORE_after'] == core
            receipt['source_and_CORE_unchanged'] = True
            receipt['observation_complete'] = completed
            receipt['selected_window_complete'] = completed
            receipt['full_stage_complete'] = completed and options.start == 0 and end == len(all_cases)
        except Exception as error:
            receipt['fatal_guard_after_error'] = error_record(error)
            raise
        finally:
            receipt['elapsed_seconds'] = time.perf_counter() - start
            receipt['last_active'] = dict(active)
            receipt['actual_completed_cases'] = len(rows)
            receipt['actual_explicit_consumer_calls'] = len(calls)
            receipt['actual_native_records'] = len(native_rows)
            receipt['consumer_error_count'] = sum(item['error'] is not None for item in calls)
            receipt['blocked_phase_count'] = sum(len(item['blocked_phases']) for item in rows)
            write_json(output / 'observations.json', receipt)
            finished.set()


if __name__ == '__main__':
    main()
