"""Root-only bounded public calculation observation, with native caller evidence."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
import traceback

BASE = Path('/workspace/.continuation')
HELPER = BASE / 'section109-empty-target-original-probe-source-v1/native_evidence.py'
HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'

def digest(path):
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, allow_nan=False, indent=2)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
    os.replace(temporary, path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--guard', required=True)
    parser.add_argument('--fixture', required=True)
    parser.add_argument('--fixture-sha256', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--phase', choices=('original', 'candidate'), required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve(); out = Path(args.out).resolve()
    guard_path = Path(args.guard).resolve(); fixture_path = Path(args.fixture).resolve()
    assert not out.exists() and root not in out.parents and BASE in out.parents
    assert digest(HELPER)['sha256'] == HELPER_SHA
    assert digest(fixture_path)['sha256'] == args.fixture_sha256
    guard = json.loads(guard_path.read_text()); fixture = json.loads(fixture_path.read_text())
    cases = fixture['stages']['focused']['cases'] if 'stages' in fixture else fixture['cases']
    assert 0 < len(cases) <= 100 and len({case['id'] for case in cases}) == len(cases)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(HELPER.parent))
    from native_evidence import source_map, freeze, assert_native_equal, write_record
    expected = guard['source_sha256']; additional = guard['source_additional_sha256']
    def check_source():
        assert source_map(root) == expected
        for relative, sha in additional.items(): assert digest(root / relative)['sha256'] == sha
    check_source()
    out.mkdir(); (out / 'native').mkdir()
    records = []; calls = []; rows = []; finished = threading.Event()
    started = time.perf_counter()
    receipt = {'kind': 'ROOT_ACTUAL_PUBLIC_API_THREE_FORMATTER_OBSERVATION', 'phase': args.phase,
        'observation_only': True, 'product_pass': False, 'observation_complete': False,
        'runner': digest(Path(__file__).resolve()), 'fixture': digest(fixture_path),
        'guard': digest(guard_path), 'source_before': expected, 'CORE_before': additional,
        'records': records, 'calls': calls, 'rows': rows, 'deadline_seconds': 120,
        'native_windows_game_chat_verified': False, 'private_state_access': False}
    def timeout():
        if not finished.wait(120):
            write_json(out / 'timeout.json', {'completed_cases': len(rows), 'elapsed_seconds': time.perf_counter() - started, 'product_pass': False})
            os._exit(124)
    threading.Thread(target=timeout, daemon=True).start()
    def save(kind, case, phase, value):
        meta = write_record(out / 'native', len(records) + 1, value)
        meta.update(kind=kind, case=case, phase=phase); records.append(meta)
        with (out / 'native/index.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(meta, ensure_ascii=False) + '\n'); handle.flush(); os.fsync(handle.fileno())
        return meta
    def observe(case, phase, function, values):
        before = freeze(values); result = None; error = None
        try: result = function(*values)
        except Exception as problem:
            error = {'type': type(problem).__name__, 'message': str(problem), 'traceback': traceback.format_exc()}
        meta = save('actual-public-consumer', case, phase, {'before': before, 'after': values, 'result': result, 'error': error})
        assert_native_equal(values, before, case + ':' + phase)
        calls.append({'case': case, 'phase': phase, 'native': meta, 'error': error, 'caller_unchanged': True})
        return result, error
    sys.path.insert(0, str(root))
    try:
        from rouge.damage import calculate_damage
        from rouge.estimate import format_estimate
        from rouge.reporting import format_report
        for case in cases:
            caller = freeze(case['scenario']); before = freeze(caller)
            result, error = observe(case['id'], 'calculate_damage', calculate_damage, (caller,))
            if error is None:
                observe(case['id'], 'format_estimate', format_estimate, (result,))
                observe(case['id'], 'format_report', format_report, (result,))
                observe(case['id'], 'format_report_technical', lambda value: format_report(value, technical=True), (result,))
            save('whole-case-caller', case['id'], 'caller', {'before': before, 'after': caller})
            assert_native_equal(caller, before, case['id'] + ':whole-caller')
            rows.append({'id': case['id'], 'calculate_error': error, 'formatters_blocked': error is not None})
            write_json(out / 'checkpoint.json', {'completed_cases': len(rows), 'next_case_index': len(rows), 'observation_complete': False, 'source_guard_after_pending': True})
        check_source(); receipt['observation_complete'] = True
    except Exception:
        receipt['fatal_error'] = traceback.format_exc(); raise
    finally:
        try:
            check_source(); receipt['source_after'] = source_map(root)
            receipt['CORE_after'] = {relative: digest(root / relative)['sha256'] for relative in additional}
            receipt['source_and_CORE_unchanged'] = True
        finally:
            receipt['elapsed_seconds'] = time.perf_counter() - started
            receipt['actual_completed_cases'] = len(rows); receipt['actual_public_calls'] = len(calls)
            receipt['actual_native_records'] = len(records)
            receipt['consumer_error_count'] = sum(call['error'] is not None for call in calls)
            write_json(out / 'observations.json', receipt); finished.set()

if __name__ == '__main__': main()
