"""Root-only pure saved API evidence reader for section 108; no project imports.

Source authors/reviewers must not execute this file or its native helper.
Only Root actual execution can issue a passed receipt. Native comparisons retain
types, insertion order, float bits and aliases inside each saved graph. Separate
saved records do not establish live aliases between different API invocations.
"""
import argparse
import ast
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
BINDINGS_SHA = 'af8ede496c4fe7800dff9849a80a77829e6351e61d99b41a5ad68095b3fd22a4'
KIND = 'ROOT_ACTUAL_108_PURE_SAVED_API_PAIR_AUDIT'
PHASE_API = {
    'prepare_run': 'rouge.run_modifiers.prepare_run',
    'calculate_damage': 'rouge.damage.calculate_damage',
    'format_estimate': 'rouge.estimate.format_estimate',
    'format_report': 'rouge.reporting.format_report',
    'format_report_technical': 'rouge.reporting.format_report',
    'enemy_preview': 'rouge.battle_preview.enemy_preview',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def regular_bytes(path):
    assert not path.is_symlink() and path.is_file(), str(path)
    return path.read_bytes()


def source_snapshot(root):
    result = {}
    for folder in ('rouge', 'tests', 'scripts'):
        for path in sorted((root / folder).rglob('*')):
            if '__pycache__' in path.parts:
                continue
            if path.is_file() and path.suffix in ('.py', '.json'):
                assert not path.is_symlink(), str(path)
                result[path.relative_to(root).as_posix()] = sha(path.read_bytes())
    return dict(sorted(result.items()))


def record_error(value):
    assert type(value) is dict and list(value) == ['type', 'message', 'traceback']
    assert all(type(value[key]) is str for key in value)
    assert value['type'] and value['traceback']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--bindings', required=True)
    parser.add_argument('--out', required=True)
    options = parser.parse_args()
    root = Path(options.root).resolve()
    packet = Path(__file__).resolve().parent
    output = Path(options.out).absolute()
    assert not output.exists() and not output.is_symlink()
    assert output.resolve() != root and root not in output.resolve().parents
    assert packet != root and root not in packet.parents
    binding_path = Path(options.bindings).absolute()
    binding_raw = regular_bytes(binding_path)
    assert sha(binding_raw) == BINDINGS_SHA
    bindings = json.loads(binding_raw)
    assert bindings['author_Runtime_executed'] is False
    assert bindings['Root_actual_reader_executed'] is False
    references = bindings['references']
    raws = {}
    for name, row in references.items():
        path = Path(row['path'])
        assert path.is_absolute()
        raw = regular_bytes(path)
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name
        raws[name] = raw
    assert raws['original_exit'].strip() == raws['candidate_exit'].strip() == b'0'
    original = json.loads(raws['original_receipt'])
    candidate = json.loads(raws['candidate_receipt'])
    original_manifest = json.loads(raws['original_manifest'])
    fixture = json.loads(raws['candidate_manifest'])
    original_guard = json.loads(raws['original_guard'])
    guard = json.loads(raws['candidate_guard'])
    expected = guard['source_sha256']
    old_expected = original_guard['source_sha256']
    core = guard['source_additional_sha256']['CORE_0.70_VERIFICATION.json']
    assert guard['section'] == 108 and guard['source_count'] == len(expected) == 751
    assert len(old_expected) == 750
    assert source_snapshot(root) == expected
    assert sha(regular_bytes(root / 'CORE_0.70_VERIFICATION.json')) == core
    assert original_guard['source_additional_sha256'] == guard['source_additional_sha256']
    assert set(expected) - set(old_expected) == {'tests/test_zone_environment_input_108.py'}
    assert not (set(old_expected) - set(expected))
    changed = {name for name in old_expected if expected[name] != old_expected[name]}
    assert changed == {'rouge/enemy_environment.py', 'scripts/verify_cloud.py'}
    product_transport = json.loads(raws['product_transport'])
    for row in product_transport['replacements']:
        assert old_expected[row['path']] == row['before_sha256']
        assert expected[row['path']] == row['after_sha256']
        actual = regular_bytes(root / row['path'])
        assert len(actual) == row['after_bytes'] and sha(actual) == row['after_sha256']
        before, after = row['before'].encode(), row['after'].encode()
        assert actual.count(after) == row['exact_occurrences'] == 1
        reverse = actual.replace(after, before, 1)
        assert len(reverse) == row['before_bytes'] and sha(reverse) == row['before_sha256']
    assert expected['tests/test_zone_environment_input_108.py'] == guard['test_source_sha256']
    probe_transport = json.loads(raws['probe_transport'])
    transported = raws['original_runner'].decode('utf-8')
    for change in probe_transport['source_replacements']:
        assert transported.count(change['before']) == change['occurrences'] == 1
        transported = transported.replace(change['before'], change['after'], 1)
    assert transported.encode('utf-8') == raws['candidate_runner']
    for change in reversed(probe_transport['source_replacements']):
        assert transported.count(change['after']) == 1
        transported = transported.replace(change['after'], change['before'], 1)
    assert transported.encode('utf-8') == raws['original_runner']
    assert original_manifest['cases'] == fixture['cases']
    assert original_manifest['previews'] == fixture['previews']
    manifest_common_keys = set(original_manifest) - {
        'kind', 'source_phase_scope', 'target_source_sha256', 'accepted_original_source_counts'}
    assert manifest_common_keys == set(fixture) - {
        'kind', 'source_phase_scope', 'target_source_sha256', 'accepted_candidate_source_counts'}
    for name in manifest_common_keys:
        assert original_manifest[name] == fixture[name], name
    assert fixture['accepted_candidate_source_counts'] == [751]
    assert original_manifest['CORE_snapshot_sha256'] == fixture['CORE_snapshot_sha256'] == core
    for name, pin in fixture['target_source_sha256'].items():
        assert expected[name] == pin
        if name == 'rouge/enemy_environment.py':
            assert original_manifest['target_source_sha256'][name] == old_expected[name]
        else:
            assert original_manifest['target_source_sha256'][name] == pin
    # Messages are obtained from exact pinned candidate Source, not a new mechanism.
    env_tree = ast.parse(regular_bytes(root / 'rouge/enemy_environment.py'))
    value_error_literals = [node.exc.args[0].value for node in ast.walk(env_tree)
        if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call)
        and isinstance(node.exc.func, ast.Name) and node.exc.func.id == 'ValueError'
        and len(node.exc.args) == 1 and isinstance(node.exc.args[0], ast.Constant)
        and type(node.exc.args[0].value) is str]
    container_message = '本局区域配置需要对象。'
    identity_message = '本局区域ID不能用于固定区域查询。'
    assert value_error_literals.count(container_message) == 1
    assert value_error_literals.count(identity_message) == 1
    preview_source = regular_bytes(root / 'rouge/battle_preview.py').decode('utf-8')
    assert "except (ValueError,KeyError) as error:" in preview_source
    assert "entry['environment']=None;entry['context_pending']=['本局环境无法确认：'+str(error)]" in preview_source
    helper_path = packet / 'native_evidence.py'
    assert sha(regular_bytes(helper_path)) == NATIVE_SHA
    sys.dont_write_bytecode = True
    # This imports only the frozen built-in evidence decoder. No project API runs.
    sys.path.insert(0, str(packet))
    from native_evidence import read_record, assert_native_equal
    output.mkdir(parents=True, exist_ok=False)
    receipt = {
        'kind': KIND, 'passed': False, 'workflow_checks_passed': False,
        'product_pass_claimed': False, 'Root_actual_reader_executed': True,
        'author_Runtime_executed': False, 'project_API_executed': False,
        'Qt_executed': False, 'Wine_executed': False, 'native_windows_verified': False,
        'ocr_executed': False, 'game_chat_sampling_executed': False,
        'started_at_UTC': datetime.now(timezone.utc).isoformat(),
        'audit_source_sha256': sha(regular_bytes(Path(__file__))),
        'native_helper_sha256': NATIVE_SHA, 'bindings_sha256': sha(binding_raw),
        'references': references, 'source_count': 751,
        'source_before': expected, 'CORE_before': core,
        'decoded_native_records': 0, 'paired_public_calls': 0,
        'paired_whole_case_callers': 0, 'caller_purity_checks': 0,
        'healthy_full_native_call_pairs': 0, 'healthy_calculation_cases': 0,
        'healthy_preview_pairs': 0, 'complete_formatter_text_pairs': 0,
        'changed_numeric_error_calls': 0, 'changed_numeric_error_cases': 0,
        'changed_preview_pending_pairs': 0, 'changes': [],
        'limits': [
            'Pure saved API record audit; no calculator, formatter, preview, RunState, Qt or Wine executes.',
            'No game/OCR/spawn/zone name/depth or timing mechanism inferred.',
            'Traceback full strings are retained and internally bound; cross-version line numbers are not invariants.',
            'Types, insertion order, float bits and aliases are checked inside saved native graphs.',
            'Records are frozen separately; no live alias assertion between different invocations.',
            'For two intentional preview changes only environment/context_pending change; the remaining fixed preview graph is checked against an actual same-target healthy control.',
            'This does not replace main saved Window/cache/IO audit and does not establish native Windows validation.',
        ],
        'deadline_seconds': 240,
    }
    started = time.perf_counter()
    finished = threading.Event()

    def watchdog():
        if not finished.wait(240):
            with (output / 'timeout.json').open('x', encoding='utf-8') as handle:
                json.dump({'passed': False, 'reason': 'SavedAPIPair240sBudget',
                           'elapsed_seconds': time.perf_counter() - started}, handle)
            os._exit(124)

    threading.Thread(target=watchdog, daemon=True).start()
    try:
        originals = (original, candidate)
        manifests = (original_manifest, fixture)
        guards = (original_guard, guard)
        decoded_sides = []
        calls_sides = []
        for index, (actual, manifest, bound_guard) in enumerate(zip(originals, manifests, guards)):
            side = 'original' if index == 0 else 'candidate'
            expected_kind = 'ROOT_ACTUAL_' + side.upper() + '108_ZONE_CONSUMERS'
            assert actual['kind'] == expected_kind
            assert actual['observation_complete'] is True and actual['observation_only'] is True
            assert actual['product_pass'] is False and actual['author_Runtime_executed'] is False
            for flag in ('native_windows_verified', 'Qt_executed', 'ocr_executed',
                         'game_chat_sampling_executed', 'private_state_access'):
                assert actual[flag] is False
            assert 'fatal_probe_error' not in actual
            assert actual['runner_sha256'] == references[side + '_runner']['sha256']
            assert actual['fixture_manifest_sha256'] == references[side + '_manifest']['sha256']
            assert actual['native_helper_sha256'] == NATIVE_SHA
            assert actual['source_guard_path'] == references[side + '_guard']['path']
            assert actual['source_guard_sha256'] == references[side + '_guard']['sha256']
            assert actual['source_before'] == actual['source_after'] == bound_guard['source_sha256']
            assert actual['CORE_before'] == actual['CORE_after'] == core
            assert actual['source_and_CORE_unchanged'] is True
            assert actual['planned_calculation_cases'] == len(manifest['cases']) == 47
            assert actual['planned_previews'] == len(manifest['previews']) == 8
            assert actual['actual_explicit_consumer_calls'] == len(actual['calls']) == 178
            assert actual['actual_native_records'] == len(actual['native_records']) == 225
            assert actual['consumer_error_count'] == sum(c['error'] is not None for c in actual['calls'])
            assert actual['blocked_phase_count'] == sum(len(r.get('blocked_phases', [])) for r in actual['rows']) == 10
            assert actual['unknown_boundaries'] == manifest['unknown_boundaries']
            native_dir = Path(references[side + '_receipt']['path']).parent / 'native'
            assert not native_dir.is_symlink() and native_dir.is_dir()
            ledger = actual['native_records']
            assert [row['path'] for row in ledger] == [f'{i:06d}.pickle.gz' for i in range(1, 226)]
            assert set(path.name for path in native_dir.iterdir()) == {row['path'] for row in ledger}
            decoded = {}
            for row in ledger:
                assert row['pickle_protocol'] == 4
                raw = regular_bytes(native_dir / row['path'])
                assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
                key = (row['case'], row['phase'])
                assert key not in decoded
                graph = read_record(native_dir, row)
                decoded[key] = (row, graph)
                receipt['decoded_native_records'] += 1
            calls = {}
            for call in actual['calls']:
                key = (call['case'], call['phase'])
                assert key not in calls
                calls[key] = call
                native_row, graph = decoded[key]
                assert native_row == call['native']
                assert native_row['kind'] == 'original-public-consumer'
                assert type(graph) is dict and list(graph) == ['before', 'after', 'result', 'error']
                assert_native_equal(graph['error'], call['error'], side + ':bound-error:' + str(key))
                assert call['returned'] is (call['error'] is None)
                if call['error'] is not None:
                    record_error(call['error'])
                    assert graph['result'] is None
                assert call['api'] == PHASE_API[call['phase']]
                assert call['caller_unchanged'] is True
                assert_native_equal(graph['before'], graph['after'], side + ':purity:' + str(key))
                receipt['caller_purity_checks'] += 1
                assert type(graph['before']) is tuple and len(graph['before']) == 2
                args, kwargs = graph['before']
                assert type(args) is tuple and type(kwargs) is dict
                if type(graph['result']) is dict:
                    assert call['returned_keys'] == list(graph['result'])
                if type(graph['result']) is str:
                    raw_text = graph['result'].encode('utf-8')
                    assert call['text_bytes'] == len(raw_text)
                    assert call['text_sha256'] == sha(raw_text)
            # Complete literal phase traversal and whole-input records, not summaries.
            planned = []
            planned_rows = []
            for case in manifest['cases']:
                cid = case['id']
                planned.extend([(cid, 'prepare_run'), (cid, 'calculate_damage')])
                for phase in ('prepare_run', 'calculate_damage'):
                    graph = decoded[(cid, phase)][1]
                    assert_native_equal(graph['before'], ((case['scenario'],), {}), side + ':literal:' + cid + phase)
                damage_graph = decoded[(cid, 'calculate_damage')][1]
                blocked = damage_graph['error'] is not None
                if not blocked:
                    phases = ['format_estimate', 'format_report']
                    if case['technical_report']:
                        phases.append('format_report_technical')
                    for phase in phases:
                        planned.append((cid, phase))
                        graph = decoded[(cid, phase)][1]
                        assert graph['error'] is None and type(graph['result']) is str
                        kwargs = {'technical': True} if phase == 'format_report_technical' else {}
                        assert_native_equal(graph['before'], ((damage_graph['result'],), kwargs), side + ':saved-result-to-text:' + cid + phase)
                blocks = ([{'phase': 'format_estimate/format_report',
                    'reason': 'Original calculate_damage returned an error; no fabricated result is substituted.'}] if blocked else [])
                planned_rows.append({'id': cid, 'group': case['group'], 'scope_note': case['scope_note'],
                                     'blocked_phases': blocks, 'caller_unchanged': True})
                whole_row, whole_graph = decoded[(cid, 'case-caller')]
                assert whole_row['kind'] == 'whole-case-caller-input'
                assert type(whole_graph) is dict and list(whole_graph) == ['before', 'after']
                assert_native_equal(whole_graph['before'], case['scenario'], side + ':whole-literal:' + cid)
                assert_native_equal(whole_graph['after'], whole_graph['before'], side + ':whole-purity:' + cid)
                receipt['caller_purity_checks'] += 1
            for case in manifest['previews']:
                cid = case['id']
                planned.append((cid, 'enemy_preview'))
                target = case['target']
                graph = decoded[(cid, 'enemy_preview')][1]
                assert_native_equal(graph['before'], ((target['stage_id'], target['enemy_id'],
                    target['level'], case['run_config']), {}), side + ':literal-preview:' + cid)
                planned_rows.append({'id': cid, 'group': 'standalone-fixed-preview', 'scope_note': case['scope_note']})
            assert list(calls) == planned
            assert actual['rows'] == planned_rows
            assert set(decoded) == set(planned) | {(case['id'], 'case-caller') for case in manifest['cases']}
            calls_sides.append(calls)
            decoded_sides.append(decoded)
        old_calls, new_calls = calls_sides
        old_decoded, new_decoded = decoded_sides
        assert list(old_calls) == list(new_calls)
        changed_cases = {}
        # Domain is derived from actual original errors plus exact literal fixtures.
        for case in fixture['cases']:
            cid = case['id']
            problem = old_calls[(cid, 'calculate_damage')]['error']
            if problem is None:
                assert old_calls[(cid, 'prepare_run')]['error'] is None
                receipt['healthy_calculation_cases'] += 1
                continue
            config = case['scenario'].get('run_config') or {}
            zone = config.get('zone')
            assert case['scenario'].get('target_enemy') and config.get('difficulty')
            if zone and type(zone) is not dict:
                message = container_message
                assert problem['type'] == 'AttributeError'
                assert problem['message'] == "'" + type(zone).__name__ + "' object has no attribute 'get'"
            else:
                assert type(zone) is dict and type(zone.get('id')) in (list, dict)
                message = identity_message
                assert problem['type'] == 'TypeError'
                assert problem['message'] == "unhashable type: '" + type(zone['id']).__name__ + "'"
            changed_cases[cid] = message
        assert len(changed_cases) == 10 and receipt['healthy_calculation_cases'] == 37
        receipt['changed_numeric_error_cases'] = len(changed_cases)
        previews = {case['id']: case for case in fixture['previews']}
        changed_previews = {cid: call['error'] for (cid, phase), call in old_calls.items()
                            if phase == 'enemy_preview' and call['error'] is not None}
        assert len(changed_previews) == 2
        control_id = 'falsey-zone-none-preview'
        assert control_id in previews and old_calls[(control_id, 'enemy_preview')]['error'] is None
        control = old_decoded[(control_id, 'enemy_preview')][1]['result']
        assert type(control) is dict and 'environment' in control and 'context_pending' in control
        control_base = {key: value for key, value in control.items() if key not in ('environment', 'context_pending')}
        for key in old_calls:
            cid, phase = key
            old_graph = old_decoded[key][1]
            new_graph = new_decoded[key][1]
            # Joint input graph retains cross-before/after alias structure per record.
            assert_native_equal((new_graph['before'], new_graph['after']),
                (old_graph['before'], old_graph['after']), 'pair:complete-caller:' + str(key))
            receipt['paired_public_calls'] += 1
            if cid in changed_cases:
                assert phase in ('prepare_run', 'calculate_damage')
                old_problem, new_problem = old_graph['error'], new_graph['error']
                assert old_problem is not None and new_problem is not None
                assert old_problem['type'] == old_calls[(cid, 'calculate_damage')]['error']['type']
                assert old_problem['message'] == old_calls[(cid, 'calculate_damage')]['error']['message']
                assert new_problem['type'] == 'ValueError' and new_problem['message'] == changed_cases[cid]
                assert old_graph['result'] is new_graph['result'] is None
                receipt['changed_numeric_error_calls'] += 1
                receipt['changes'].append({'case': cid, 'phase': phase,
                    'original_error': {name: old_problem[name] for name in ('type', 'message')},
                    'candidate_error': {name: new_problem[name] for name in ('type', 'message')}})
            elif cid in changed_previews:
                assert phase == 'enemy_preview' and old_graph['error'] is not None
                assert old_graph['result'] is None and new_graph['error'] is None
                zone = previews[cid]['run_config']['zone']
                message = container_message if type(zone) is not dict else identity_message
                expected_old_type = 'AttributeError' if type(zone) is not dict else 'TypeError'
                assert old_graph['error']['type'] == expected_old_type
                expected_old_message = ("'" + type(zone).__name__ + "' object has no attribute 'get'"
                    if type(zone) is not dict else "unhashable type: '" + type(zone['id']).__name__ + "'")
                assert old_graph['error']['message'] == expected_old_message
                assert previews[cid]['target'] == previews[control_id]['target']
                result = new_graph['result']
                assert type(result) is dict and list(result) == list(control)
                assert result['environment'] is None
                assert_native_equal(result['context_pending'], ['本局环境无法确认：' + message], 'pending:' + cid)
                base = {name: value for name, value in result.items() if name not in ('environment', 'context_pending')}
                assert_native_equal(base, control_base, 'pending:complete-fixed-preview-base:' + cid)
                receipt['changed_preview_pending_pairs'] += 1
                receipt['changes'].append({'case': cid, 'phase': phase,
                    'original_error': {name: old_graph['error'][name] for name in ('type', 'message')},
                    'candidate_environment': None, 'candidate_context_pending': result['context_pending'],
                    'fixed_preview_control_case': control_id,
                    'projected_fields': ['environment', 'context_pending']})
            else:
                assert old_graph['error'] is new_graph['error'] is None
                assert_native_equal(new_graph, old_graph, 'healthy:complete-native-record:' + str(key))
                receipt['healthy_full_native_call_pairs'] += 1
                if phase.startswith('format_'):
                    assert type(old_graph['result']) is type(new_graph['result']) is str
                    receipt['complete_formatter_text_pairs'] += 1
                elif phase == 'enemy_preview':
                    receipt['healthy_preview_pairs'] += 1
        for case in fixture['cases']:
            key = (case['id'], 'case-caller')
            assert_native_equal(new_decoded[key][1], old_decoded[key][1], 'paired:whole-case:' + case['id'])
            receipt['paired_whole_case_callers'] += 1
        assert original['consumer_error_count'] == 22 and candidate['consumer_error_count'] == 20
        assert receipt['decoded_native_records'] == receipt['caller_purity_checks'] == 450
        assert receipt['paired_public_calls'] == 178 and receipt['paired_whole_case_callers'] == 47
        assert receipt['healthy_full_native_call_pairs'] == 156
        assert receipt['complete_formatter_text_pairs'] == 76 and receipt['healthy_preview_pairs'] == 6
        assert receipt['changed_numeric_error_calls'] == 20 and receipt['changed_preview_pending_pairs'] == 2
        receipt['original_consumer_errors'] = original['consumer_error_count']
        receipt['candidate_consumer_errors'] = candidate['consumer_error_count']
        receipt['original_and_candidate_blocked_calculation_cases'] = 10
        receipt['workflow_checks_passed'] = True
        receipt['passed'] = True
    except BaseException as error:
        receipt['passed'] = False
        receipt['workflow_checks_passed'] = False
        receipt['error'] = {'type': type(error).__name__, 'message': str(error),
            'traceback': ''.join(traceback.format_exception(type(error), error, error.__traceback__))}
        raise
    finally:
        try:
            receipt['source_after'] = source_snapshot(root)
            receipt['CORE_after'] = sha(regular_bytes(root / 'CORE_0.70_VERIFICATION.json'))
            receipt['source_and_CORE_unchanged'] = receipt['source_after'] == expected and receipt['CORE_after'] == core
            # Bind exact final receipts, raw exits and both Source packets again.
            for name, row in references.items():
                raw = regular_bytes(Path(row['path']))
                assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name
            assert receipt['source_and_CORE_unchanged'] is True
            assert sha(regular_bytes(helper_path)) == NATIVE_SHA
            assert sha(regular_bytes(binding_path)) == BINDINGS_SHA
            assert sha(regular_bytes(Path(__file__))) == receipt['audit_source_sha256']
        except BaseException as error:
            receipt['passed'] = False
            receipt['workflow_checks_passed'] = False
            receipt['final_guard_error'] = {'type': type(error).__name__, 'message': str(error)}
            raise
        finally:
            receipt['elapsed_seconds'] = time.perf_counter() - started
            with (output / 'receipt.json').open('x', encoding='utf-8') as handle:
                json.dump(receipt, handle, ensure_ascii=False, allow_nan=False, indent=2)
                handle.write('\n')
                handle.flush()
                os.fsync(handle.fileno())
            finished.set()


if __name__ == '__main__':
    main()
