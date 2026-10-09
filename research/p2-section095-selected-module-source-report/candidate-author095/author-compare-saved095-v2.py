"""Saved-only complete frozen94/candidate comparison; zero project runtime calls."""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', required=True)
    parser.add_argument('--worker', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    folder, worker = Path(args.directory), Path(args.worker)
    output = Path(args.output)
    assert not output.exists(), 'never overwrite saved-review prefix'
    module_spec = importlib.util.spec_from_file_location('saved095_native_codec', worker)
    codec = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(codec)  # stdlib definitions only; guarded main not run.
    assert not any(name == 'rouge' or name.startswith('rouge.') for name in sys.modules)
    plan_path = folder / 'matrix-plan095.json'
    plan = json.loads(plan_path.read_text())
    checks, groups, source_rows = Counter(), Counter(), []
    expected_texts = 0
    outcome_counts = Counter()
    source_prefix = '\n\n【所选模组 · 原件资料与覆盖边界】\n'
    technical_prefix = '\n\n【所选模组原件追溯】\n'
    def load_receipt(side):
        rc = folder / (side + '-run.exit-code')
        assert rc.read_text().strip() == '0', 'actual primary shell status must be captured zero'
        p = folder / (side + '-receipt.json')
        r = json.loads(p.read_text())
        assert r['passed'] and r['workflow_complete'] and r['unexpected_outcomes'] == 0
        assert r['states'] == len(plan['cases']) == r['actual_API_entries']
        assert r['plan_sha256'] == hashlib.sha256(plan_path.read_bytes()).hexdigest()
        records = folder / (side + '-records.jsonl.gz')
        assert records.stat().st_size == r['native_records_bytes']
        assert hashlib.sha256(records.read_bytes()).hexdigest() == r['native_records_sha256']
        source_rows.append({'receipt': str(p), 'receipt_sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
            'records': str(records), 'bytes': records.stat().st_size, 'sha256': r['native_records_sha256'],
            'captured_primary_exit_code_file': str(rc), 'captured_primary_exit_code': 0})
        return r, records
    baseline_receipt, baseline_path = load_receipt('baseline')
    candidate_receipt, candidate_path = load_receipt('candidate')
    def remove_exact_notes_block(text):
        assert text.count(source_prefix) == 1, 'exact new notes-only section must occur once'
        start = text.index(source_prefix)
        end = text.find('\n\n【', start + len(source_prefix))
        assert end > start, 'new source notes block must end before existing explanatory/todo section'
        return text[:start] + text[end:]
    result = {'format_version': 1, 'status': 'RUNNING_SAVED_ONLY_COMPLETE_NATIVE_AND_TEXT_COMPARISON',
              'passed': False, 'project_calls': 0, 'completed_section_increment': 0,
              'limitations': ['External Linux calculations and real formatter requests; no actual UI/Wine/nativeWindows/game/chat.',
                  'Current pinned wine clocks are deployment; retained phase-envelope branch separately tested using an explicit unknown-clock test-only fixture.']}
    try:
        with gzip.open(baseline_path, 'rt', encoding='utf-8') as base_stream, gzip.open(candidate_path, 'rt', encoding='utf-8') as new_stream:
            old_header, new_header = json.loads(next(base_stream)), json.loads(next(new_stream))
            assert old_header['kind'] == new_header['kind'] == 'header'
            assert old_header['source_sha256_before'] == baseline_receipt['source_sha256_after']
            assert new_header['source_sha256_before'] == candidate_receipt['source_sha256_after']
            assert old_header['maintained_sources'] == 732 and new_header['maintained_sources'] == 735
            checks['source_header_receipt_bindings'] += 2
            for index, case in enumerate(plan['cases']):
                result['current_case'] = case['id']
                old, new = json.loads(next(base_stream)), json.loads(next(new_stream))
                assert old['kind'] == new['kind'] == 'state'
                assert old['index'] == new['index'] == index
                assert old['id'] == new['id'] == case['id']
                assert old['scenario'] == new['scenario'] == case['scenario']
                assert old['expected_error'] == new['expected_error'] == case['expected_error']
                for row in (old, new):
                    before = codec.restored_graph(row['caller_before'])
                    after = codec.restored_graph(row['caller_after'])
                    assert row['caller_before'] == row['caller_after']
                    assert row['actual_API_entry_return']['entry_caller'] == row['caller_before']
                    assert row['actual_API_entry_return']['entry_calls'] == 1
                    assert row['actual_API_entry_return']['return_events'] == 1
                    checks['caller_and_actual_API_entry_snapshots'] += 1
                    assert before == after == case['scenario']
                assert old['caller_before'] == new['caller_before']
                assert old['outcome'] == new['outcome']
                old_math = {key: value for key, value in old['actual_project_calls'].items()
                    if not key.startswith(('rouge.reporting.', 'rouge.module_source_reference.'))}
                new_math = {key: value for key, value in new['actual_project_calls'].items()
                    if not key.startswith(('rouge.reporting.', 'rouge.module_source_reference.'))}
                assert old_math == new_math, 'non-report project function invocation counts changed'
                checks['non_report_project_call_map_exact'] += 1
                if old['outcome'] == 'original_API_exception':
                    assert case['expected_error']
                    assert old['error'] == new['error'], 'original exception class/args/message/order changed'
                    codec.restored_graph(old['error']['args'])
                    assert old['actual_API_entry_return']['return_event_native'] == new['actual_API_entry_return']['return_event_native']
                    checks['original_exception_prefix_exact'] += 1
                else:
                    assert not case['expected_error']
                    old_native = codec.restored_graph(old['native_result'])
                    new_native = codec.restored_graph(new['native_result'])
                    for row in (old, new):
                        assert row['native_result'] == row['actual_API_entry_return']['return_event_native']
                    old_texts, new_texts = old['three_texts'], new['three_texts']
                    assert set(old_texts) == set(new_texts) == {'normal', 'technical', 'structured'}
                    assert old_texts['structured'] == json.dumps({'scenario': case['scenario'], 'result': old_native}, ensure_ascii=False, indent=2)
                    assert new_texts['structured'] == json.dumps({'scenario': case['scenario'], 'result': new_native}, ensure_ascii=False, indent=2)
                    expected_texts += 3
                    if not case['scenario'].get('module_id'):
                        assert 'selected_module_source_reference' not in new_native['report']
                        assert old['native_result'] == new['native_result']
                        assert old_texts == new_texts
                        checks['no_module_complete_native_and_three_texts_exact'] += 1
                    else:
                        report = new_native['report']
                        assert 'selected_module_source_reference' not in old_native['report']
                        assert len(report) == len(old_native['report']) + 1
                        ref = report.pop('selected_module_source_reference')
                        assert ref['module_id'] == case['scenario']['module_id']
                        assert ref['module_level'] == case['scenario']['module_level']
                        assert ref['raw_phase']['equipLevel'] == ref['module_level']
                        assert list(ref['raw_phase']) == ['equipLevel', 'parts', 'attributeBlackboard', 'tokenAttributeBlackboard']
                        assert report['sections'][-1]['id'] == 'selected_module_source'
                        assert report['sections'][-1]['metrics'] == []
                        assert sum(block['id'] == 'selected_module_source' for block in report['sections']) == 1
                        block = report['sections'].pop()  # Preserve the original sections container/alias graph.
                        assert not any('https://' in note or 'http://' in note for note in block['notes'])
                        assert codec.native_graph(new_native) == old['native_result'], 'complete native typed/order/alias comparison failed'
                        assert remove_exact_notes_block(new_texts['normal']) == old_texts['normal']
                        tail = technical_prefix + json.dumps(ref, ensure_ascii=False, indent=2)
                        assert new_texts['technical'].count(technical_prefix) == 1
                        assert new_texts['technical'].endswith(tail)
                        new_technical = new_texts['technical'][:-len(tail)]
                        assert remove_exact_notes_block(new_technical) == old_texts['technical']
                        assert json.dumps({'scenario': case['scenario'], 'result': new_native}, ensure_ascii=False, indent=2) == old_texts['structured']
                        checks['selected_module_full_native_exact_except_two_additions'] += 1
                        checks['normal_existing_text_exact_except_bounded_source_block'] += 1
                        checks['technical_existing_text_exact_except_bounded_source_block_and_exact_tail'] += 1
                        checks['structured_existing_text_exact_except_two_report_additions'] += 1
                        checks['exact_raw_technical_trace'] += 1
                    checks['returned_dict_full_native_inverse'] += 2
                groups[case['group']] += 1
                outcome_counts[old['outcome']] += 1
                checks['complete_state_bindings'] += 1
            old_tail, new_tail = json.loads(next(base_stream)), json.loads(next(new_stream))
            assert old_tail['kind'] == new_tail['kind'] == 'tail'
            for row, receipt in ((old_tail, baseline_receipt), (new_tail, candidate_receipt)):
                tail_expected = dict(receipt)
                tail_expected.pop('native_records_bytes')
                tail_expected.pop('native_records_sha256')
                assert row['receipt'] == tail_expected
            assert base_stream.read() == new_stream.read() == ''
        assert dict(groups) == plan['group_counts']
        assert outcome_counts['returned_dict'] == baseline_receipt['returned_dict_states'] == candidate_receipt['returned_dict_states']
        assert outcome_counts['original_API_exception'] == baseline_receipt['original_API_exception_states'] == candidate_receipt['original_API_exception_states']
        assert expected_texts == baseline_receipt['actual_three_text_requests'] == candidate_receipt['actual_three_text_requests']
        result.update(status='PASS_SAVED_ONLY_COMPLETE_FROZEN094_VS_CANDIDATE095', passed=True,
            states=len(plan['cases']), actual_returned_dict_states=outcome_counts['returned_dict'],
            actual_original_API_exception_states=outcome_counts['original_API_exception'],
            actual_API_entries_per_tree=len(plan['cases']), actual_three_text_requests_per_tree=expected_texts,
            group_counts=dict(groups), actual_project_call_counts_baseline=baseline_receipt['actual_project_calls'],
            actual_project_call_counts_candidate=candidate_receipt['actual_project_calls'],
            checks=dict(checks), input_records=source_rows, plan_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest(),
            allowance='Only exact report.selected_module_source_reference and one final notes-only selected_module_source block; technical exact appended JSON tail. All old native types/key order/alias, source math calls, report schema/sections/metrics/notes/errors/callers/text and no-module outputs exact.')
    except Exception as error:
        result.update(status='FAIL_SAVED_ONLY_COMPLETE_NATIVE_AND_TEXT_COMPARISON',
                      error_class=type(error).__name__, error_message=str(error),
                      completed_states=checks['complete_state_bindings'], checks=dict(checks))
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        raise
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('status', 'passed', 'states', 'actual_returned_dict_states',
        'actual_original_API_exception_states', 'actual_API_entries_per_tree', 'actual_three_text_requests_per_tree',
        'project_calls')}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
