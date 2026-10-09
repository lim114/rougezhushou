"""Retain the old test's exact duration-free fixture and all 52 paired records."""
import ast
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent
ADAPTATION = Path('/workspace/.continuation/p2-report095-token-duration-test-adaptation-v1')
TREE = ADAPTATION / 'isolated-candidate'
OLD = ADAPTATION / 'original-test_token_duration_reference.py'
spec = importlib.util.spec_from_file_location('duration095_typed_codec',
    '/workspace/.continuation/p2-report095-candidate-v1/author-matrix-worker095.py')
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)


def source_hashes(names):
    return {name: hashlib.sha256((TREE / name).read_bytes()).hexdigest() for name in names}


def main():
    records = ROOT / 'paired-duration095-records.json.gz'
    receipt_path = ROOT / 'paired-duration095-receipt.json'
    assert not records.exists() and not receipt_path.exists()
    guard = json.loads((ADAPTATION / 'isolated-source-095-adaptation.json').read_text())
    expected = guard['source_sha256_after']
    assert source_hashes(expected) == expected and len(expected) == 735
    sys.path.insert(0, str(TREE))
    from rouge.catalog import catalog
    from rouge.damage import calculate_damage
    from rouge.reporting import format_report
    from tests.test_token_duration_reference import scenario, TOKEN
    # Extract the unchanged original test's cases-building AST, not guessed inputs.
    tree = ast.parse(OLD.read_bytes())
    method = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and
        node.name == 'test_all_public_numeric_stats_damage_and_clocks_are_unchanged')
    setup = ast.Module(body=method.body[:2], type_ignores=[])
    namespace = {'scenario': scenario}
    exec(compile(ast.fix_missing_locations(setup), str(OLD), 'exec'), namespace)
    cases = namespace['cases']
    assert len(cases) == 52
    catalog()  # Public immutable-source cache initialization before paired counters.
    rows, totals_actual, totals_baseline = [], Counter(), Counter()
    def execute(caller):
        calls = Counter()
        events = {'entry_calls': 0, 'return_events': 0}
        def profile(frame, event, argument):
            if event == 'call' and frame.f_globals.get('__name__', '').startswith('rouge.'):
                calls[frame.f_globals['__name__'] + '.' + frame.f_code.co_qualname] += 1
            if frame.f_code is calculate_damage.__code__:
                if event == 'call':
                    events['entry_calls'] += 1
                    events['actual_entry_caller'] = codec.native_graph(frame.f_locals['scenario'])
                elif event == 'return':
                    events['return_events'] += 1
                    events['actual_return_native'] = codec.native_graph(argument)
        before = codec.native_graph(caller)
        sys.setprofile(profile)
        try:
            native = calculate_damage(caller)
            texts = {'normal': format_report(native), 'technical': format_report(native, technical=True),
                'structured': json.dumps({'scenario': caller, 'result': native}, ensure_ascii=False, indent=2)}
        finally:
            sys.setprofile(None)
        saved = codec.native_graph(native)
        assert type(native) is dict and saved == events['actual_return_native']
        assert before == codec.native_graph(caller) == events['actual_entry_caller']
        assert events['entry_calls'] == events['return_events'] == 1
        codec.restored_graph(saved)
        return native, {'caller_before': before, 'caller_after': codec.native_graph(caller),
            'actual_API_entry_return': events, 'native_result': saved, 'actual_three_texts': texts,
            'actual_Rouge_call_counts_by_qualname': dict(calls)}
    metadata_exclusions = (
        'rouge.reporting.', 'rouge.module_source_reference.',
        'rouge.summons.duration_reference', 'rouge.summons._duration_rules',
    )
    for index, args in enumerate(cases):
        actual_caller, baseline_caller = deepcopy(args), deepcopy(args)
        actual, saved_actual = execute(actual_caller)
        # Exactly the established old test fixture; no full runner/API replacement.
        with patch('rouge.summons.duration_reference', return_value=None):
            baseline, saved_baseline = execute(baseline_caller)
        source_actual = actual['report']['selected_module_source_reference']
        source_baseline = baseline['report']['selected_module_source_reference']
        duration_links = [link for link in source_actual['existing_coverage']['report_sections']
            if link['section_id'] == 'token_duration_' + TOKEN]
        assert len(duration_links) == 1
        link = duration_links[0]
        assert actual['report']['sections'][int(link['path'].rsplit('/', 1)[1])]['id'] == 'token_duration_' + TOKEN
        assert '/token_duration_references' in source_actual['existing_coverage']['native_paths']
        assert not any(link['section_id'] == 'token_duration_' + TOKEN
            for link in source_baseline['existing_coverage']['report_sections'])
        assert '/token_duration_references' not in source_baseline['existing_coverage']['native_paths']
        # Preserve the exact established duration-reference removals only.
        actual.pop('token_duration_references')
        duration_indexes = [i for i, block in enumerate(actual['report']['sections'])
            if block['id'] == 'token_duration_' + TOKEN]
        assert len(duration_indexes) == 1
        actual['report']['sections'].pop(duration_indexes[0])
        for token in actual['relic_token_stats']:
            token.pop('duration_reference', None)
        assert 'token_duration_references' not in baseline
        assert all('duration_reference' not in token for token in baseline['relic_token_stats'])
        for result in (actual, baseline):
            report = result['report']
            assert sum(block['id'] == 'selected_module_source' for block in report['sections']) == 1
            assert report['sections'][-1]['id'] == 'selected_module_source'
            assert report['sections'][-1]['metrics'] == []
            report.pop('selected_module_source_reference')
            report['sections'].pop()
        stripped_actual, stripped_baseline = codec.native_graph(actual), codec.native_graph(baseline)
        assert stripped_actual == stripped_baseline, 'old complete native/types/order/alias changed'
        actual_math = {key: value for key, value in saved_actual['actual_Rouge_call_counts_by_qualname'].items()
            if not key.startswith(metadata_exclusions)}
        baseline_math = {key: value for key, value in saved_baseline['actual_Rouge_call_counts_by_qualname'].items()
            if not key.startswith(metadata_exclusions)}
        assert actual_math == baseline_math, 'nonmetadata/nonreport actual function call vectors changed'
        totals_actual.update(saved_actual['actual_Rouge_call_counts_by_qualname'])
        totals_baseline.update(saved_baseline['actual_Rouge_call_counts_by_qualname'])
        rows.append({'index': index, 'original_scenario': args, 'actual': saved_actual,
            'original_duration_free_test_fixture_baseline': saved_baseline,
            'old_duration_removal_and_exact_new_report_removal_actual_native': stripped_actual,
            'old_duration_removal_and_exact_new_report_removal_baseline_native': stripped_baseline,
            'actual_truthful_duration_link': link, 'baseline_has_no_fictitious_duration_link': True,
            'nonmetadata_nonreport_actual_function_call_maps_exact': True})
    assert source_hashes(expected) == expected
    with gzip.open(records, 'wt', encoding='utf-8', compresslevel=6) as archive:
        json.dump({'format_version': 1, 'scope': 'Same original52 input matrix and explicitly labeled old duration-free unit test fixture; no original2628 success replay, no model or native Windows claim.',
            'source_guard': expected, 'rows': rows}, archive, ensure_ascii=False)
    receipt = {'format_version': 1, 'status': 'PASS_ACTUAL52_PAIRED_DURATION_METADATA_REPORT_BOUNDARY',
        'passed': True, 'completed_section_increment': 0, 'paired_states': 52,
        'actual_API_entries': totals_actual['rouge.damage.calculate_damage'],
        'baseline_fixture_API_entries': totals_baseline['rouge.damage.calculate_damage'],
        'actual_three_text_requests_each_side': 156, 'actual_caller_before_after_and_entry_exact': True,
        'complete_old_native_types_float_hex_key_order_alias_after_precise_removal_exact': True,
        'generic_source_actual_duration_link_valid_baseline_does_not_virtualize_link': True,
        'actual_nonmetadata_nonreport_call_vectors_exact_each_pair': True,
        'actual_Rouge_call_counts': dict(totals_actual), 'baseline_fixture_Rouge_call_counts': dict(totals_baseline),
        'precise_call_count_exclusions': list(metadata_exclusions),
        'count_exclusion_reason': 'Original fixture intentionally omits duration_reference and its pinned metadata loader/nested candidate selectors; reporting and new source presentation naturally depend on metadata presence. All other Rouge functions remain counted/comparison-exact.',
        'maintained_source_hashes': 735, 'source_drift': [],
        'actual_primary_exit_status': 'fresh caller shell captures external exit-code file',
        'records': str(records), 'bytes': records.stat().st_size,
        'sha256': hashlib.sha256(records.read_bytes()).hexdigest(),
        'root_fresh_selected_and_actual_window_full095': 'PENDING, not established here',
        'Qt_Wine_private_network': 0}
    assert receipt['actual_API_entries'] == receipt['baseline_fixture_API_entries'] == 52
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: receipt[key] for key in ('status', 'passed', 'paired_states', 'actual_API_entries',
        'baseline_fixture_API_entries', 'actual_three_text_requests_each_side', 'bytes', 'sha256')}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
