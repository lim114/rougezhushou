"""Root-only frozen102 resource observations; Source author never executes.

Observation workflow zero is distinct from product correctness. Exceptions and
partial memory updates are retained at their actual phase. Public JSON/temp
paths only; no OCR, Qt, Wine, private state, sampling, game or chat actions.
"""
import argparse
from copy import deepcopy
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
RUNSTATE_SHA = '98b3b6ea4ad36b36d031064d900bc445c80e5ac50ae2c6eceb16861a68e3a3c7'
GUARD_SHA = '9fd27ca19155f4c81dd02d80c70d6c4ffb032b850d03ca38a5e5c67e201e59f4'
CORE_SHA = 'a75d9497ce34f68de787e3ba99704741f2c873c2c5fa9b5de01e6620b1f00f89'
START, OLD_AT, NEW_AT = 1000.0, 1001.0, 1002.0


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False,
                                    indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def disks(path):
    return {name: {'exists': p.exists(), 'bytes': p.read_bytes() if p.exists() else None}
            for name, p in [('run', path), ('temporary', path.with_suffix('.tmp'))]}


def error_record(error):
    return {'type': type(error).__name__, 'message': str(error),
            'traceback': ''.join(traceback.format_exception(
                type(error), error, error.__traceback__))}


def cases():
    """Explicit public direct-API controls, not alleged natural OCR failures."""
    rows = []
    def add(identity, resources, old=None, config=None, opaque=None):
        observed = {'operators': [], 'relics': {'ids': [], 'icons': [],
                    'count': None, 'source': 'public-resource104'}, 'resources': resources}
        if config is not None:
            observed['config'] = config
        if opaque is not None:
            observed['public_opaque'] = opaque
        rows.append({'id': identity, 'old': {} if old is None else old,
                     'observed': observed, 'captured_at': NEW_AT})
    def old_record(key, value):
        return {key: {'value': value, 'captured_at': OLD_AT,
                      'source': 'public-previous-resource104',
                      'public_opaque': {'nullable': None, 'negative_zero': -0.0}}}
    for key in ('gold', 'parts_count'):
        for label, old in [('no-old', {}), ('old-null', old_record(key, None)),
                           ('old-eight', old_record(key, 8))]:
            add(key + '-missing-value-' + label, {key: {}}, old)
        for label, malformed in [('null', None), ('list', []), ('text', 'public'),
                                  ('integer', 8), ('boolean', False)]:
            add(key + '-malformed-record-' + label, {key: malformed}, old_record(key, 8))
        for label, value in [('zero', 0), ('eight', 8), ('float-eight', 8.0),
                              ('null', None), ('boolean-true', True),
                              ('boolean-false', False), ('text', '8')]:
            record = {'value': value, 'source': 'public-legacy-resource104',
                      'public_opaque': {'null': None, 'negative_zero': -0.0}}
            if key == 'parts_count':
                record['capacity'] = 12
            add(key + '-complete-legacy-' + label, {key: record})
    for label, malformed in [('null', None), ('list', []), ('text', 'public'),
                              ('integer', 8), ('boolean', False)]:
        add('malformed-resources-' + label, malformed,
            {**old_record('gold', 8), **old_record('parts_count', 3)})
    add('unread-empty-map-retains-both', {},
        {**old_record('gold', 8), **old_record('parts_count', 3)})
    add('missing-gold-with-wellformed-parts-peer',
        {'gold': {}, 'parts_count': {'value': 3, 'capacity': 12, 'source': 'public-peer104'}})
    add('malformed-parts-with-wellformed-gold-peer',
        {'parts_count': None, 'gold': {'value': 8, 'source': 'public-peer104'}})
    add('legal-config-before-missing-old-eight-gold', {'gold': {}}, old_record('gold', 8),
        {'difficulty': {'value': 2, 'source': 'public-config-peer104'}})
    add('unknown-invalid-counter-with-wellformed-gold',
        {'public_counter104': {}, 'gold': {'value': 8, 'source': 'public-peer104'}})
    add('unknown-null-counter-with-wellformed-gold',
        {'public_counter104': None, 'gold': {'value': 8, 'source': 'public-peer104'}})
    shared = {'public': [None, -0.0]}
    cycle = []
    cycle.append(cycle)
    add('unused-caller-opaque-alias-and-cycle', {'gold': {'value': 8}},
        opaque={'left': shared, 'right': shared, 'cycle': cycle})
    resource_cycle = []
    resource_cycle.append(resource_cycle)
    add('complete-record-opaque-cycle-original-save-error',
        {'gold': {'value': 8, 'public_cycle': resource_cycle}})
    alias = {'public_values': [None, -0.0]}
    add('complete-record-opaque-alias-original-json-policy',
        {'gold': {'value': 8, 'public_left': alias, 'public_right': alias}})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--guard', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    root, guard_path, out = (Path(value).resolve()
                             for value in (args.root, args.guard, args.out))
    assert not out.exists() and out != root and root not in out.parents
    packet = Path(__file__).resolve().parent
    assert packet != root and root not in packet.parents
    raw_guard = guard_path.read_bytes()
    assert sha(raw_guard) == GUARD_SHA
    guard = json.loads(raw_guard)
    expected = guard['source_sha256']
    assert type(expected) is dict and len(expected) == 746
    assert expected['rouge/run_state.py'] == RUNSTATE_SHA
    extra = guard['source_additional_sha256']
    assert extra == {'CORE_0.70_VERIFICATION.json': CORE_SHA}
    assert sha((root / 'CORE_0.70_VERIFICATION.json').read_bytes()) == CORE_SHA
    helper = packet / 'native_evidence.py'
    assert not helper.is_symlink() and sha(helper.read_bytes()) == NATIVE_SHA
    sys.dont_write_bytecode = True
    from native_evidence import source_map, freeze, assert_native_equal, write_record
    assert source_map(root) == expected
    out.mkdir(parents=True)
    (out / 'public-state').mkdir()
    (out / 'native').mkdir()
    case_rows, native_rows = [], []
    started = time.perf_counter()
    finished = threading.Event()
    active = {'case': None, 'phase': 'preimport'}
    receipt = {'kind': 'ROOT_ACTUAL_ORIGINAL102_RESOURCE_API_OBSERVATIONS',
               'observation_only': True, 'observation_complete': False,
               'product_pass': False, 'author_Source_only': True,
               'runner_sha256': sha(Path(__file__).read_bytes()),
               'native_helper_sha256': NATIVE_SHA,
               'source_guard_path': str(guard_path), 'source_guard_sha256': sha(raw_guard),
               'source_before': expected, 'CORE_before': CORE_SHA,
               'started_at_UTC': datetime.now(timezone.utc).isoformat(),
               'rows': case_rows, 'native_records': native_rows,
               'deadline_seconds': 120, 'private_state_access': False,
               'ocr_Qt_Wine_game_chat_sampling_executed': False,
               'native_windows_verified': False}

    def timeout():
        if not finished.wait(120):
            write_json(out / 'timeout.json', {'product_pass': False, 'active': active,
                       'elapsed_seconds': time.perf_counter() - started})
            os._exit(124)

    def save_native(kind, identity, value):
        metadata = write_record(out / 'native', len(native_rows) + 1, value)
        metadata.update({'kind': kind, 'case': identity})
        native_rows.append(metadata)
        return metadata

    def unchanged(actual, expected_value, label):
        try:
            assert_native_equal(actual, expected_value, label)
            return {'unchanged': True, 'error': None}
        except Exception as error:
            return {'unchanged': False, 'error': error_record(error)}

    threading.Thread(target=timeout, daemon=True).start()
    sys.path.insert(0, str(root))
    try:
        from rouge.run_state import RunState
        controls = cases()
        assert len({case['id'] for case in controls}) == len(controls)
        for case in controls:
            identity = case['id']
            active.update(case=identity, phase='public-fixture')
            directory = out / 'public-state' / identity
            directory.mkdir()
            path = directory / 'run.json'
            saved = {'id': 'public-resource104-' + identity, 'started_at': START,
                     'last_read': OLD_AT, 'operators': {}, 'relics': {},
                     'resources': deepcopy(case['old']), 'config': {}, 'maps': {},
                     'history': [], 'tactical_tools': {}}
            raw = json.dumps(saved, ensure_ascii=False, allow_nan=False, indent=2).encode('utf-8')
            path.write_bytes(raw)
            path.with_suffix('.tmp').write_bytes(b'public-resource104-preexisting-temporary-sentinel\n')
            observed, captured_at = case['observed'], case['captured_at']
            caller_before = freeze((observed, captured_at))
            original_disks = freeze(disks(path))
            row = {'id': identity, 'fixture_sha256': sha(raw),
                   'captured_at': captured_at, 'loader_error': None,
                   'apply_result': None, 'apply_error': None,
                   'summary_before_error': None, 'summary_after_error': None,
                   'restart_error': None, 'restart_summary_error': None}
            case_rows.append(row)
            try:
                active['phase'] = 'loader'
                run = RunState(path)
            except Exception as error:
                row['loader_error'] = error_record(error)
                row['loader_evidence'] = save_native('loader-exception', identity,
                    {'caller_before': caller_before, 'caller_after': (observed, captured_at),
                     'disks_before': original_disks, 'disks_after': disks(path)})
                continue
            row.update(loader_accepted=not run.preserve_unreadable,
                       loaded_run_id=run.state['id'])
            before_state, before_disks = freeze(run.state), freeze(disks(path))
            row['summary_before_state_and_disk'] = save_native('before-views', identity,
                {'state': before_state, 'disks': before_disks})
            active['phase'] = 'summary-before'
            try:
                row['summary_before'] = run.summary()
            except Exception as error:
                row['summary_before_error'] = error_record(error)
            row['summary_before_readonly_state'] = unchanged(run.state, before_state, 'before summary state')
            row['summary_before_readonly_disk'] = unchanged(disks(path), before_disks, 'before summary disk')
            active['phase'] = 'apply'
            try:
                row['apply_result'] = run.apply(observed, captured_at)
            except Exception as error:
                row['apply_error'] = error_record(error)
            row['caller_native_unchanged'] = unchanged((observed, captured_at), caller_before, 'apply caller')
            after_state, after_disks = freeze(run.state), freeze(disks(path))
            row['apply_memory_and_disk'] = save_native('actual-apply', identity,
                {'caller_before': caller_before, 'caller_after': (observed, captured_at),
                 'state_before': before_state, 'state_after': after_state,
                 'disks_before': original_disks, 'disks_after': after_disks,
                 'apply_result': row['apply_result'], 'apply_error': row['apply_error'],
                 'save_issue': run.save_issue, 'preserve_unreadable': run.preserve_unreadable})
            active['phase'] = 'summary-after'
            try:
                row['summary_after'] = run.summary()
            except Exception as error:
                row['summary_after_error'] = error_record(error)
            row['summary_after_readonly_state'] = unchanged(run.state, after_state, 'after summary state')
            row['summary_after_readonly_disk'] = unchanged(disks(path), after_disks, 'after summary disk')
            active['phase'] = 'restart'
            restart_before = freeze(disks(path))
            try:
                restarted = RunState(path)
                row.update(restart_loader_accepted=not restarted.preserve_unreadable,
                           restart_run_id=restarted.state['id'])
                restart_state = freeze(restarted.state)
                row['restart_memory_and_disk'] = save_native('actual-restart', identity,
                    {'state': restart_state, 'disks_before': restart_before, 'disks_after': disks(path),
                     'save_issue': restarted.save_issue,
                     'preserve_unreadable': restarted.preserve_unreadable})
                active['phase'] = 'restart-summary'
                try:
                    row['restart_summary'] = restarted.summary()
                except Exception as error:
                    row['restart_summary_error'] = error_record(error)
                row['restart_summary_readonly_state'] = unchanged(restarted.state, restart_state, 'restart summary state')
                row['restart_summary_readonly_disk'] = unchanged(disks(path), restart_before, 'restart summary disk')
            except Exception as error:
                row['restart_error'] = error_record(error)
            row['caller_after_restart'] = unchanged((observed, captured_at), caller_before, 'restart caller')
            active['phase'] = 'case-complete'
            write_json(out / 'observations.json', receipt)
        receipt['case_count'] = len(case_rows)
        receipt['observation_complete'] = len(case_rows) == len(controls)
    except Exception as error:
        receipt['observer_error'] = {'active': dict(active), **error_record(error)}
    finally:
        receipt['source_after'] = source_map(root)
        receipt['source_drift'] = [name for name in sorted(set(expected) | set(receipt['source_after']))
                                   if expected.get(name) != receipt['source_after'].get(name)]
        receipt['CORE_after'] = sha((root / 'CORE_0.70_VERIFICATION.json').read_bytes())
        receipt['CORE_drift'] = receipt['CORE_after'] != CORE_SHA
        receipt['elapsed_seconds'] = round(time.perf_counter() - started, 6)
        receipt['finished_at_UTC'] = datetime.now(timezone.utc).isoformat()
        finished.set()
        write_json(out / 'observations.json', receipt)
    observer_ok = (receipt['observation_complete'] and 'observer_error' not in receipt
                   and not receipt['source_drift'] and not receipt['CORE_drift'])
    print(json.dumps({'observation_workflow_complete': observer_ok,
                      'product_pass': False, 'case_count': len(case_rows),
                      'observations': str(out / 'observations.json')}, ensure_ascii=False))
    return 0 if observer_ok else 1


if __name__ == '__main__':
    sys.exit(main())
