"""Root-only original public weight-consumer observations for section 107.

The Source author does not execute this script, the native helper, or project
imports. This observes current production APIs without mocks or numerical PASS
criteria. No Qt, OCR, real settings, capture, game, chat, or private state.
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
MANIFEST_SHA = '4765d0b9e0e47244b53c3dcaa32af45307f1ce7c176d798be859a9299500fa81'


def sha(value):
    return hashlib.sha256(value).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False,
                                    indent=2) + '\n', encoding='utf-8')
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
    options = parser.parse_args()
    root = Path(options.root).resolve()
    guard_path = Path(options.guard).resolve()
    output = Path(options.out).resolve()
    packet = Path(__file__).resolve().parent
    assert not output.exists() and output != root and root not in output.parents
    assert packet != root and root not in packet.parents
    assert not guard_path.is_symlink()
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
    assert manifest['source_regular_py_json_count'] == 748
    assert manifest['CORE_snapshot_sha256'] == core
    assert manifest['groups'] == 3 and len(manifest['cases']) == 14
    assert len(manifest['previews']) == 2
    assert manifest['maximum_public_consumer_calls'] == 74
    assert len({case['id'] for case in manifest['cases']}) == 14
    assert {case['group'] for case in manifest['cases']} == {
        'fixed-weight4', 'fixed-weight5', 'manual-no-fixed-target'}
    for name, pin in manifest['target_source_sha256'].items():
        assert expected[name] == pin and sha((root / name).read_bytes()) == pin
    sys.dont_write_bytecode = True
    from native_evidence import source_map, freeze, assert_native_equal, write_record
    assert source_map(root) == expected
    output.mkdir(parents=True)
    (output / 'native').mkdir()
    calls = []
    rows = []
    loader_calls = []
    native_rows = []
    active = {'case': 'preimport', 'phase': 'preimport'}
    receipt = {
        'kind': 'ROOT_ACTUAL_ORIGINAL105_WEIGHT_CONSUMERS_FOR107',
        'observation_only': True, 'product_pass': False, 'observation_complete': False,
        'author_Runtime_executed': False, 'native_windows_verified': False,
        'Qt_executed': False, 'ocr_executed': False, 'game_chat_sampling_executed': False,
        'private_state_access': False, 'deadline_seconds': 120,
        'started_at_UTC': datetime.now(timezone.utc).isoformat(),
        'runner_sha256': sha(Path(__file__).read_bytes()), 'native_helper_sha256': NATIVE_SHA,
        'fixture_manifest_sha256': MANIFEST_SHA, 'source_guard_path': str(guard_path),
        'source_guard_sha256': sha(guard_raw), 'source_before': expected, 'CORE_before': core,
        'groups': 3, 'planned_calculation_cases': 14, 'planned_previews': 2,
        'maximum_explicit_consumer_calls': 74,
        'call_count_scope': 'Explicit runner consumer invocations; internal production calls are not counted. The one original catalog getter is separately recorded.',
        'rows': rows, 'calls': calls, 'public_loader_calls': loader_calls,
        'native_records': native_rows, 'unknown_boundaries': manifest['unknown_boundaries'],
    }
    finished = threading.Event()
    start = time.perf_counter()

    def deadline():
        if not finished.wait(120):
            write_json(output / 'timeout.json', {
                'product_pass': False, 'active': dict(active),
                'elapsed_seconds': time.perf_counter() - start,
                'reason': 'Root120sOriginalWeightProbeBudget'})
            os._exit(124)

    def save_native(kind, case, phase, value):
        record = write_record(output / 'native', len(native_rows) + 1, value)
        record.update(kind=kind, case=case, phase=phase)
        native_rows.append(record)
        return record

    def observe(case, phase, api, function, args, kwargs=None):
        active.update(case=case, phase=phase)
        if kwargs is None:
            kwargs = {}
        before = freeze((args, kwargs))
        result = None
        problem = None
        try:
            result = function(*args, **kwargs)
        except Exception as error:
            problem = error_record(error)
        after = (args, kwargs)
        native = save_native('original-public-consumer', case, phase,
                             {'before': before, 'after': after,
                              'result': result, 'error': problem})
        row = {'case': case, 'phase': phase, 'api': api, 'returned': problem is None,
               'error': problem, 'native': native, 'caller_unchanged': False}
        calls.append(row)
        assert_native_equal(after, before, case + ':' + phase + ':caller')
        row['caller_unchanged'] = True
        if type(result) is dict:
            row['returned_keys'] = list(result)
            if 'total_damage' in result:
                row['total_damage'] = result['total_damage']
                row['total_healing'] = result.get('total_healing')
                row['complete'] = result.get('complete')
                enemy = result.get('run_resolution', {}).get('enemy')
                if type(enemy) is dict:
                    row['fixed_reference_weight'] = enemy['reference_stats'].get('massLevel')
                    row['reported_environment_weight'] = enemy['stats'].get('massLevel')
                row['original_components'] = result.get('components')
                row['relic_enemy_effects'] = result.get('relic_resolution', {}).get('enemy_effects')
                row['relic_records'] = result.get('relic_resolution', {}).get('records')
        elif type(result) is str:
            raw = result.encode('utf-8')
            row['text_bytes'] = len(raw)
            row['text_sha256'] = sha(raw)
        elif type(result) is tuple and len(result) == 2 and type(result[0]) is dict:
            row['prepared_weight'] = result[0].get('enemy_weight')
            row['prepared_weight_present'] = 'enemy_weight' in result[0]
        return result, problem, row

    threading.Thread(target=deadline, daemon=True).start()
    sys.path.insert(0, str(root))
    try:
        from rouge.catalog import catalog
        from rouge.run_modifiers import prepare_run
        from rouge.relics import prepare as prepare_relics
        from rouge.damage import calculate_damage
        from rouge.estimate import format_estimate
        from rouge.reporting import format_report
        from rouge.battle_preview import enemy_preview
        active.update(case='public-loader', phase='original-catalog')
        profiles = catalog()['operators']
        loader_calls.append({'api': 'rouge.catalog.catalog', 'explicit_calls': 1,
                             'purpose': 'Unmodified original profile input to relics.prepare; no fake profile or source calculation.'})
        save_native('original-public-profile-inputs', 'public-loader', 'catalog-profile-bindings',
                    {key: profiles[key] for key in manifest['catalog_operator_bindings']})
        for key, binding in manifest['catalog_operator_bindings'].items():
            profile = profiles[key]
            assert_native_equal(
                {'id': profile['id'], 'name': profile['name'],
                 'profession': profile['profession'],
                 'skill1_rank10': profile['skills'][0]['levels'][9],
                 'talents': profile['talents']}, binding,
                'original-catalog-source-bindings:' + key)
        for case in manifest['cases']:
            cid = case['id']
            caller = freeze(case['scenario'])
            case_before = freeze(caller)
            row = {'id': cid, 'group': case['group'], 'scope_note': case['scope_note'],
                   'blocked_phases': [], 'caller_unchanged': False}
            rows.append(row)
            prepared, problem, _ = observe(cid, 'prepare_run', 'rouge.run_modifiers.prepare_run',
                                            prepare_run, (caller,))
            if problem is None:
                observe(cid, 'prepare_relics', 'rouge.relics.prepare', prepare_relics,
                        (prepared[0], profiles[caller['operator']]))
            else:
                row['blocked_phases'].append({'phase': 'prepare_relics',
                    'reason': 'Original prepare_run returned an error; no fabricated prepared scenario is substituted.'})
            result, problem, _ = observe(cid, 'calculate_damage', 'rouge.damage.calculate_damage',
                                         calculate_damage, (caller,))
            if problem is None:
                observe(cid, 'format_estimate', 'rouge.estimate.format_estimate',
                        format_estimate, (result,))
                observe(cid, 'format_report', 'rouge.reporting.format_report',
                        format_report, (result,))
                if case['technical_report']:
                    observe(cid, 'format_report_technical', 'rouge.reporting.format_report',
                            format_report, (result,), {'technical': True})
            else:
                row['blocked_phases'].append({'phase': 'format_estimate/format_report',
                    'reason': 'Original calculate_damage returned an error; no fabricated result is substituted.'})
            save_native('whole-case-caller-input', cid, 'case-caller',
                        {'before': case_before, 'after': caller})
            assert_native_equal(caller, case_before, cid + ':whole-case-caller')
            row['caller_unchanged'] = True
        for case in manifest['previews']:
            target = case['target']
            observe(case['id'], 'enemy_preview', 'rouge.battle_preview.enemy_preview',
                    enemy_preview, (target['stage_id'], target['enemy_id'],
                                    target['level'], case['run_config']))
            rows.append({'id': case['id'], 'group': 'standalone-fixed-preview',
                         'scope_note': case['scope_note']})
        assert len(calls) <= manifest['maximum_public_consumer_calls']
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
            receipt['actual_explicit_consumer_calls'] = len(calls)
            receipt['actual_explicit_public_loader_calls'] = sum(
                item['explicit_calls'] for item in loader_calls)
            receipt['actual_native_records'] = len(native_rows)
            receipt['consumer_error_count'] = sum(item['error'] is not None for item in calls)
            receipt['blocked_phase_count'] = sum(len(item.get('blocked_phases', [])) for item in rows)
            write_json(output / 'observations.json', receipt)
            finished.set()


if __name__ == '__main__':
    main()
