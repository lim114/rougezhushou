"""Inactive Source: Root-only final 108 report/spec preparation, never product execution.

All runtime inputs are independently pinned by Root after terminal receipts exist.
No successful output is written before every mandatory terminal/Saved/public gate.
The separate, byte-pinned saver owns tracked archive/checkpoint writes; the existing
publisher owns Git. This file imports only the standard library.
"""
import argparse
import ast
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path

BASE = Path('/workspace/.continuation')
ROOT = Path('/workspace/rougezhushou')
SELECTOR = 'tests.test_zone_environment_input_108'
TEST_PATH = 'tests/test_zone_environment_input_108.py'
TEST_SHA = 'da7a739664f19e55186a8e12581bbb72c85a08a4d1640c9299bcd51943ba8b59'
TEST107_SHA = '2c5eab4be5f484ca3eaf45d19eeb1f1067661a36c42ea41297a5ad1ec22ecc51'
OLD_GUARD_SHA = '409249b384daf8c38d1b7576de70ce8b5e0a4c3a387bba3da07cdb84a5f75de0'
CORE_SHA = 'a75d9497ce34f68de787e3ba99704741f2c873c2c5fa9b5de01e6620b1f00f89'
ORIGINAL_SHA = 'caadc9ecfd748e1172820abe460735b0563210e1c25312482e0d2a541ac5a790'
WINDOW_SHA = 'c4404868fec6c81d09eea18a33603b0ed1ca3c2dcabcab6f183f039494a08bc5'
GOLD_SHA = '847ded287d8c355933e0babd4888e5d269b99b130e932519047dd4dd12798a48'
AUDIT_SHA = 'f46f0fea6456020c50830ed30ab420bebf53c2f89c0993316aeb944c638c1ef8'
HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
FACT_SHA = 'af66d1b06a98b46660a501c67144a074c330213d05c11c0241d28be63dda42d9'
TRANSPORT_SHA = '7df1d49d0927c33b59a67dc005cad7ef0fb300d92f7c75327f2839c4b2cfbb2c'
RELATED_SHA = 'ebb4b0b8201ff2fe103abc93a9f065b2c744489c180e01659ed6609ac70ab0a9'
FALSE_WINDOW = ('native_windows_verified', 'private_state_access', 'game_chat_sampling_executed',
                'natural_OCR_producer_verified', 'malformed_saved_cache_admission_claimed')
FALSE_SAVED = ('project_API_formatter_numeric_Qt_tests_Wine_Git_executed', 'saved_inputs_written',
               'native_windows_verified', 'natural_OCR_producer_verified',
               'malformed_saved_cache_admission_verified', 'individual_three_formatter_prepost_verified',
               'cross_separate_freeze_live_alias_verified', 'JSON_preserves_live_aliases_verified',
               'second_MainWindow_reopen_verified')
PIN_KEYS = ('source_guard', 'apply_source', 'apply_primary', 'apply_log',
            'selected_log', 'selected_primary',
            'related_linux_receipt', 'related_linux_primary', 'related_linux_log',
            'related_wine_receipt', 'related_wine_primary', 'related_wine_log',
            'candidate_API_receipt', 'candidate_API_primary', 'candidate_API_log',
            'gold_receipt', 'gold_primary', 'gold_log',
            'candidate_receipt', 'candidate_primary', 'candidate_log',
            'window_runner', 'saved_source', 'saved_receipt', 'saved_primary', 'saved_log',
            'bindings', 'binder_primary', 'binder_log', 'visual',
            'API_pair_source', 'API_pair_bindings', 'API_pair_receipt', 'API_pair_primary', 'API_pair_log')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def safe(path):
    original = Path(path)
    assert original.is_absolute() and '..' not in original.parts and not original.is_symlink()
    assert all(not parent.is_symlink() for parent in original.parents)
    path = original.resolve()
    assert BASE in path.parents and ROOT not in path.parents
    assert all(part not in ('.local', '.venv', '.git', '__pycache__', 'private', 'credentials') for part in path.parts)
    return path


def bound(pin, expected=None):
    assert type(pin) is dict and set(pin) == {'path', 'bytes', 'sha256'}
    assert type(pin['bytes']) is int and pin['bytes'] >= 0
    assert type(pin['sha256']) is str and len(pin['sha256']) == 64
    path = safe(pin['path'])
    assert path.is_file()
    if expected is not None:
        assert path == Path(expected).resolve()
    raw = path.read_bytes()
    assert len(raw) == pin['bytes'] and sha(raw) == pin['sha256'], str(path)
    return raw


def pin(path):
    path = safe(path)
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}


def source_map():
    values = {}
    for folder in ('rouge', 'tests', 'scripts'):
        for path in sorted((ROOT / folder).rglob('*')):
            if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts:
                assert not path.is_symlink()
                values[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    return values


def assignment(raw, name):
    found = [n for n in ast.parse(raw).body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    assert len(found) == 1
    return ast.literal_eval(found[0].value)


def summary(value):
    keys = ('tests_run', 'tests_passed', 'skipped', 'unavailable_parent_count', 'failures', 'errors')
    assert all(type(value[key]) is int and value[key] >= 0 for key in keys)
    return {**{key: value[key] for key in keys}, 'unavailable_records': len(value['unavailable'])}


def source_receipt(value, expected, additional, before='source_before', after='source_after'):
    assert value[before] == value[after] == expected
    assert value['source_additional_before'] == value['source_additional_after'] == additional
    assert value['source_drift'] == []


def terminal(value):
    assert value['passed'] is value['workflow_complete'] is True
    assert 'failure' not in value


def ledger(receipt, root, domain):
    """Byte/ledger validation only; this builder never decodes native records."""
    rows = receipt[domain]
    assert type(rows) is list and rows
    names = [row['path'] for row in rows]
    assert len(set(names)) == len(names)
    entries = []
    for index, row in enumerate(rows, 1):
        assert row['path'] == '%06d.pickle.gz' % index
        path = safe(Path(root) / row['path'])
        raw = path.read_bytes()
        assert raw.startswith(b'\x1f\x8b') and len(raw) == row['bytes'] and sha(raw) == row['sha256']
        entries.append((path, pin(path)))
    actual = {p.name for p in Path(root).iterdir() if p.is_file()}
    assert actual == set(names) and all(not p.is_symlink() and p.is_file() for p in Path(root).iterdir())
    return entries


def main():
    parser = argparse.ArgumentParser()
    for key in ('inputs', 'inputs-sha256', 'spec', 'report'):
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    packet = Path(__file__).resolve().parent
    inputs_path = safe(args.inputs)
    inputs_raw = inputs_path.read_bytes()
    assert sha(inputs_raw) == args.inputs_sha256
    inputs = json.loads(inputs_raw)
    assert inputs['kind'] == 'ROOT_ACTUAL108_FINAL_SAVE_INPUTS_V1'
    assert inputs['actual_runtime_ready'] is True and inputs['Source_only'] is False
    assert set(inputs['pins']) == set(PIN_KEYS)
    pins = inputs['pins']
    raws = {key: bound(pins[key]) for key in PIN_KEYS}
    for key in PIN_KEYS:
        if key.endswith('_primary'):
            assert raws[key] == b'0\n', key
    # Each actual dataset primary/log belongs to that dataset's public directory;
    # another successful process's raw0 is never accepted as its primary receipt.
    for label, filename in (('gold', 'receipt.json'), ('candidate', 'receipt.json'), ('candidate_API', 'observations.json')):
        receipt_path = Path(pins[label + '_receipt']['path'])
        assert receipt_path.name == filename
        assert Path(pins[label + '_primary']['path']) == receipt_path.parent.with_suffix('.exit-code')
        assert Path(pins[label + '_log']['path']) == receipt_path.parent.with_suffix('.log')
    for environment in ('linux', 'wine'):
        receipt_path = Path(pins['related_' + environment + '_receipt']['path'])
        assert receipt_path.name.startswith('resume108-related-' + environment + '-') and receipt_path.suffix == '.json'
        assert Path(pins['related_' + environment + '_primary']['path']) == receipt_path.with_suffix('.exit-code')
        assert Path(pins['related_' + environment + '_log']['path']) == receipt_path.with_suffix('.log')
    selected_path = Path(pins['selected_log']['path'])
    assert selected_path.name.startswith('resume108-selected-') and selected_path.suffix == '.log'
    assert Path(pins['selected_primary']['path']) == selected_path.with_suffix('.exit-code')
    spec_path, report_path = safe(args.spec), safe(args.report)
    assert spec_path == BASE / 'root-section108-save-spec-v1.json'
    assert report_path == BASE / 'section108-actual-report-v1.md'
    assert not spec_path.exists() and not report_path.exists() and inputs_path not in (spec_path, report_path)

    # Every Source-only archive leaf was individually listed and sealed before use.
    plan_path = packet / 'public-files-source-plan.json'
    plan = json.loads(plan_path.read_bytes())
    assert plan['kind'] == 'SOURCE_ONLY_108_EXPLICIT_PUBLIC_ARCHIVE_PLAN'
    assert plan['Runtime_executed'] is plan['product_pass'] is False
    assert plan['prepared_unapplied_next']['runtime_executed'] is plan['prepared_unapplied_next']['product_pass'] is False
    assert all(plan['prepared_unapplied_next'][name] is None for name in ('actual_focused109', 'actual_permanent109', 'actual_full110', 'actual_section109_applied_guard', 'actual_section110_guard'))
    entries, destinations = [], set()
    def add(path, destination, expected_pin=None):
        path = safe(path)
        target = Path(destination)
        assert not target.is_absolute() and '..' not in target.parts and target.as_posix() not in destinations
        assert all(part not in ('__pycache__', '.git', '.local', '.venv', 'private') for part in target.parts)
        meta = expected_pin or pin(path)
        bound(meta, path)
        destinations.add(target.as_posix())
        entries.append({'source': str(path), 'destination': target.as_posix(), 'source_pin': meta})
    for row in plan['files']:
        add(row['pin']['path'], row['destination'], row['pin'])

    # Source750 -> 751 is exactly enemy_environment, cloud prepend, and one test.
    old_raw = (BASE / 'resume107-applied-source-v2.json').read_bytes()
    assert sha(old_raw) == OLD_GUARD_SHA
    old = json.loads(old_raw)
    guard = json.loads(raws['source_guard'])
    expected, additional = guard['source_sha256'], guard['source_additional_sha256']
    assert guard['section'] == 108 and guard['source_count'] == len(expected) == 751
    assert len(old['source_sha256']) == 750
    assert additional == old['source_additional_sha256'] == {'CORE_0.70_VERIFICATION.json': CORE_SHA}
    assert set(expected) - set(old['source_sha256']) == {TEST_PATH} and not set(old['source_sha256']) - set(expected)
    assert {name for name in old['source_sha256'] if old['source_sha256'][name] != expected[name]} == {
        'rouge/enemy_environment.py', 'scripts/verify_cloud.py'}
    assert set(guard['changed_paths']) == {'rouge/enemy_environment.py', 'scripts/verify_cloud.py', TEST_PATH}
    assert expected[TEST_PATH] == TEST_SHA and expected['tests/test_aglna_gravity_weight_107.py'] == TEST107_SHA
    assert guard['prior_complete_source_guard_sha256'] == OLD_GUARD_SHA
    assert guard['applier_source_sha256'] == sha(raws['apply_source'])
    assert guard['candidate_packet_manifest_sha256'] == sha((BASE / 'section108-active-zone-consumer-source-v1/SOURCE_MANIFEST.json').read_bytes())
    assert guard['exact_local_transport_sha256'] == TRANSPORT_SHA
    assert guard['original_actual_zone_observations_sha256'] == ORIGINAL_SHA
    assert guard['window_source_sha256'] == sha(raws['window_runner']) == WINDOW_SHA
    assert guard['actual_healthy_Gold_receipt_sha256'] == sha(raws['gold_receipt']) == GOLD_SHA
    assert pins['gold_receipt']['path'] == guard['actual_healthy_Gold_receipt_path']
    assert pins['gold_receipt']['path'] == str(BASE / 'resume108-window-gold-v3/receipt.json')
    assert guard['runtime_checks_passed_claimed'] is guard['native_windows_verified'] is False
    assert source_map() == expected and sha((ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes()) == CORE_SHA
    cloud = assignment((ROOT / 'scripts/verify_cloud.py').read_bytes(), 'MODULES')
    full_raw = (ROOT / 'scripts/verify_full_available.py').read_bytes()
    full_extra = assignment(full_raw, 'NEW_MODULES')
    assert len(cloud) == guard['cloud_selectors_after'] == 119 and cloud[0] == SELECTOR and cloud.count(SELECTOR) == 1
    assert len(full_extra) == 41 and sha(full_raw) == old['source_sha256']['scripts/verify_full_available.py']
    core_raw = (ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes()
    union = list(dict.fromkeys(json.loads(core_raw)['test_modules'] + list(full_extra) + list(cloud)))
    assert len(union) == guard['full_selector_union_after'] == 242 and guard['full_NEW_MODULES_unchanged'] is True
    test_raw = (ROOT / TEST_PATH).read_bytes()
    assert sha(test_raw) == TEST_SHA
    assert sum(isinstance(n, ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(ast.parse(test_raw))) == 16
    prior_raw = (BASE / 'section107-publication-v1.json').read_bytes()
    prior = json.loads(prior_raw)
    assert prior['section'] == 107 and prior['local_HEAD'] == prior['remote_HEAD'] == guard['baseline_HEAD']
    assert prior['commit_primary_exit'] == prior['push_primary_exit'] == 0 and prior['clean'] is True
    assert prior['source_files'] == 750 and guard['actual_prior_publication'] == prior
    assert guard['actual_prior_publication_sha256'] == sha(prior_raw)
    checkpoint = json.loads((ROOT / 'DEVELOPMENT_CHECKPOINT.json').read_bytes())
    closure = json.loads((ROOT / 'verification/full-105/closure.json').read_bytes())
    assert checkpoint['completed_sections'] == 107 and checkpoint['next_section'] == 108
    assert checkpoint['full_validation_due'] is False
    assert checkpoint['last_full_validation'] == checkpoint['current_full105_checkpoint'] == closure
    assert closure['after_section'] == 105 and closure['batch_validation_closed'] is True
    assert closure['full095_deferred_preserved'] is True and closure['old095_complete_function_vector_measured'] is False
    assert checkpoint['current_full095_checkpoint']['status'] == 'DEFERRED_NOT_FULLPASS'
    assert checkpoint['current_full095_checkpoint']['completed_section_increment'] == 0
    assert checkpoint['next_full_validation_after'] == checkpoint['current_batch_commit_policy']['next_full_validation_after'] == 110

    # Availability classifiers, skip/U counts, and selected counts remain actual.
    assert sha((BASE / 'root-section108-related-v1.py').read_bytes()) == RELATED_SHA
    related = {}
    for environment in ('linux', 'wine'):
        value = json.loads(raws['related_' + environment + '_receipt'])
        assert value['section'] == 108 and value['available_checks_passed'] is True
        assert value['failures'] == value['errors'] == 0 and value['source_drift'] == []
        assert value['source_sha256'] == value['source_after'] == expected
        assert value['source_additional_sha256'] == value['source_additional_after'] == additional
        assert value['original_assertions_and_classifier_unchanged'] is True
        assert value['wine_compatibility'] is (environment == 'wine')
        assert value['native_windows_game_chat_verified'] is False and SELECTOR in value['selectors']
        summary(value)
        related[environment] = value
    selected_lines = raws['selected_log'].decode().splitlines()
    selected = json.loads(next(line for line in reversed(selected_lines) if line.startswith('{"passed"')))
    assert selected['passed'] is True and selected['failures'] == selected['errors'] == 0
    # Selected receipt has no Source map. A genuine surrounding guard is checked,
    # and this limitation remains explicit in the report rather than invented.

    original_path = BASE / 'section108-original-zone-actual-linux-v2/observations.json'
    original_raw = original_path.read_bytes()
    assert sha(original_raw) == ORIGINAL_SHA
    original, API = json.loads(original_raw), json.loads(raws['candidate_API_receipt'])
    for value, mapping, raw_guard, kind in (
        (original, old['source_sha256'], old_raw, 'ROOT_ACTUAL_ORIGINAL108_ZONE_CONSUMERS'),
        (API, expected, raws['source_guard'], 'ROOT_ACTUAL_CANDIDATE108_ZONE_CONSUMERS')):
        assert value['kind'] == kind and value['observation_only'] is True and value['product_pass'] is False
        assert value['observation_complete'] is value['source_and_CORE_unchanged'] is True
        assert value['source_before'] == value['source_after'] == mapping
        assert value['source_guard_sha256'] == sha(raw_guard)
        assert value['CORE_before'] == value['CORE_after'] == CORE_SHA
        assert value['planned_calculation_cases'] == 47 and value['planned_previews'] == 8
        assert value['actual_explicit_consumer_calls'] == len(value['calls'])
        assert value['actual_native_records'] == len(value['native_records'])
        assert value['consumer_error_count'] == sum(row['error'] is not None for row in value['calls'])
        assert value['blocked_phase_count'] == sum(len(row.get('blocked_phases', [])) for row in value['rows'])
        assert len(value['rows']) == 55 and len({(c['case'], c['phase']) for c in value['calls']}) == len(value['calls'])
        for flag in ('native_windows_verified', 'Qt_executed', 'ocr_executed', 'game_chat_sampling_executed', 'private_state_access'):
            assert value[flag] is False
    assert original['actual_explicit_consumer_calls'] == 178 and original['actual_native_records'] == 225
    assert original['consumer_error_count'] == 22 and original['blocked_phase_count'] == 10
    assert [(r['id'], r.get('group')) for r in API['rows']] == [(r['id'], r.get('group')) for r in original['rows']]
    assert API['runner_sha256'] == sha((BASE / 'section108-zone-candidate-probe-source-v1/probe_zone108.py').read_bytes())
    assert API['fixture_manifest_sha256'] == sha((BASE / 'section108-zone-candidate-probe-source-v1/fixture-manifest.json').read_bytes())

    gold, candidate = json.loads(raws['gold_receipt']), json.loads(raws['candidate_receipt'])
    for phase, value, mapping, raw_guard in (('gold', gold, old['source_sha256'], old_raw),
                                           ('candidate', candidate, expected, raws['source_guard'])):
        terminal(value)
        assert value['kind'] == 'ROOT_ACTUAL_108_REAL_MAINWINDOW' and value['phase'] == phase
        assert value['runner_sha256'] == WINDOW_SHA and value['fixture_facts_sha256'] == FACT_SHA and value['transport_sha256'] == TRANSPORT_SHA
        assert value['original_receipt_sha256'] == ORIGINAL_SHA and value['original_guard_sha256'] == OLD_GUARD_SHA
        assert value['source_guard_sha256'] == sha(raw_guard)
        source_receipt(value, mapping, additional)
        assert len(value['rows']) == 43 and len(value['windows']) == 2 and value['Qt_errors'] == []
        assert len({row['id'] for row in value['rows']}) == 43 and value['deadline_seconds'] == 450
        assert 0 < value['elapsed_seconds'] < 450
        for flag in FALSE_WINDOW:
            assert value[flag] is False
    assert len(gold['pngs']) == 0 and len(candidate['pngs']) == 4
    assert candidate['actual_gold_receipt_sha256'] == sha(raws['gold_receipt'])
    assert [(row['id'], row['changed']) for row in gold['rows']] == [(row['id'], row['changed']) for row in candidate['rows']]

    # Main Saved independently decodes original API and BOTH Window ledgers.
    # It does not validate candidate API: the separate API pair receipt is required.
    bindings_raw = raws['bindings']
    bindings = json.loads(bindings_raw)
    assert bindings['kind'] == 'ROOT_ACTUAL108_SAVED_ARTIFACT_BINDINGS_V1' and bindings['actual_runtime_ready'] is True
    bind_keys = {
        'audit_Source': 'saved_source', 'window_runner': 'window_runner',
        'gold_receipt': 'gold_receipt', 'gold_primary': 'gold_primary',
        'candidate_receipt': 'candidate_receipt', 'candidate_primary': 'candidate_primary',
        'candidate_guard': 'source_guard', 'visual': 'visual'}
    for key, source in bind_keys.items():
        assert bindings[key] == pins[source]
    for key, path in {'original_receipt': original_path, 'original_guard': BASE / 'resume107-applied-source-v2.json',
                      'gold_guard': BASE / 'resume107-applied-source-v2.json',
                      'original_primary': BASE / 'section108-original-zone-actual-linux-v2.exit-code'}.items():
        bound(bindings[key], path)
    for value in bindings.values():
        if type(value) is dict and {'path', 'bytes', 'sha256'} <= set(value):
            bound(value)
    assert sha(raws['saved_source']) == AUDIT_SHA
    compile(raws['saved_source'], pins['saved_source']['path'], 'exec')
    for name, wanted in (('WINDOW', WINDOW_SHA), ('ORIGINAL', ORIGINAL_SHA), ('CORE', CORE_SHA), ('TEST', TEST_SHA), ('HELPER', HELPER_SHA)):
        assert assignment(raws['saved_source'], name) == wanted
    saved = json.loads(raws['saved_receipt'])
    terminal(saved)
    assert saved['kind'] == 'ROOT_ACTUAL_108_PURE_SAVED_READBACK'
    assert saved['audit_Source_sha256'] == AUDIT_SHA and saved['bindings_sha256'] == sha(bindings_raw)
    source_receipt(saved, expected, additional)
    for flag in FALSE_SAVED:
        assert saved[flag] is False
    counts = {'original': len(original['native_records']), 'gold': len(gold['records']), 'candidate': len(candidate['records'])}
    assert saved['actual_decoded_records_by_dataset'] == counts
    assert len(saved['decoded_records']) == sum(counts.values())
    assert all(row['safe_native_hash_decode_verified'] is True for row in saved['decoded_records'])
    assert saved['actual_Window_records_by_phase'] == {p: counts[p] for p in ('gold', 'candidate')}
    assert saved['actual_Window_numeric_calls_by_phase'] == {p: v['actual_numeric_calls'] for p, v in (('gold', gold), ('candidate', candidate))}
    assert len(saved['original_API_checks']) == len(original['calls'])
    assert len(saved['snapshot_checks']) == 86 and len(saved['memory_admission_checks']) == 80
    assert len(saved['legal_observation_checks']) == len(saved['restart_checks']) == 4
    assert len(saved['Gold_points']) == 43
    assert sum(row['complete_same_input_Gold_equal'] is True for row in saved['Gold_points']) == 33
    assert sum(row['changed_error_preserves_raw_Gold'] is True for row in saved['Gold_points']) == 10
    assert len(saved['PNG_checks']) == 4 and all(row['Root_actually_viewed'] is True for row in saved['PNG_checks'])
    for field, kind in (('UI_pure_checks', 'pure_actual_UI_step'), ('formatter_group_checks', 'pure_actual_three_formatter_group'),
                        ('cross_API_boundary_checks', 'actual_cross_API_identity_order_boundary')):
        assert len(saved[field]) == sum(row['kind'] == kind for value in (gold, candidate) for row in value['records'])
    visual = json.loads(raws['visual'])
    terminal(visual)
    assert visual['kind'] == 'ROOT_ACTUAL108_FOUR_PNG_VISUAL_READBACK'
    assert visual['candidate_receipt_sha256'] == sha(raws['candidate_receipt'])
    assert visual['native_windows_game_chat_verified'] is False and len(visual['pngs']) == 4
    for png, seen in zip(candidate['pngs'], visual['pngs']):
        assert {key: seen[key] for key in png} == png and seen['actually_viewed'] is True
        assert type(seen['visual_observation']) is str and seen['visual_observation']
        path = safe(Path(pins['candidate_receipt']['path']).parent / png['file'])
        assert '/' not in png['file'] and path.suffix == '.png'
        raw = path.read_bytes()
        assert raw.startswith(b'\x89PNG\r\n\x1a\n') and len(raw) == png['bytes'] and sha(raw) == png['sha256']
        add(path, 'actual-window-candidate/' + png['file'])

    # Mandatory separate API pair receipt: actual schema uses workflow_checks_passed,
    # scalar counters and CORE guards (not the MainSaved workflow_complete schema).
    pair_source_sha = 'e37e1f246ba356ca01c7306eba9a3c257cbcb9860bc716cc8429c258412b2c29'
    pair_bindings_sha = 'af8ede496c4fe7800dff9849a80a77829e6351e61d99b41a5ad68095b3fd22a4'
    assert sha(raws['API_pair_source']) == pair_source_sha
    assert sha(raws['API_pair_bindings']) == pair_bindings_sha
    compile(raws['API_pair_source'], pins['API_pair_source']['path'], 'exec')
    assert assignment(raws['API_pair_source'], 'KIND') == 'ROOT_ACTUAL_108_PURE_SAVED_API_PAIR_AUDIT'
    assert assignment(raws['API_pair_source'], 'BINDINGS_SHA') == pair_bindings_sha
    assert assignment(raws['API_pair_source'], 'NATIVE_SHA') == HELPER_SHA
    pair = json.loads(raws['API_pair_receipt'])
    assert pair['kind'] == 'ROOT_ACTUAL_108_PURE_SAVED_API_PAIR_AUDIT'
    assert pair['passed'] is pair['workflow_checks_passed'] is pair['Root_actual_reader_executed'] is True
    assert all(name not in pair for name in ('error', 'final_guard_error', 'failure'))
    assert pair['audit_source_sha256'] == pair_source_sha and pair['bindings_sha256'] == pair_bindings_sha
    assert pair['native_helper_sha256'] == HELPER_SHA and pair['source_count'] == 751
    assert pair['source_before'] == pair['source_after'] == expected
    assert pair['CORE_before'] == pair['CORE_after'] == CORE_SHA and pair['source_and_CORE_unchanged'] is True
    for flag in ('product_pass_claimed', 'author_Runtime_executed', 'project_API_executed',
                 'Qt_executed', 'Wine_executed', 'native_windows_verified', 'ocr_executed', 'game_chat_sampling_executed'):
        assert pair[flag] is False
    pair_bindings = json.loads(raws['API_pair_bindings'])
    assert pair_bindings['kind'] == 'SOURCE_ONLY_108_SAVED_API_PAIR_BINDINGS'
    assert pair_bindings['author_Runtime_executed'] is pair_bindings['Root_actual_reader_executed'] is pair_bindings['product_pass'] is False
    assert pair['references'] == pair_bindings['references']
    for meta in pair['references'].values():
        bound(meta)
    assert pair['references']['original_receipt'] == pin(original_path)
    assert pair['references']['candidate_receipt'] == pins['candidate_API_receipt']
    assert pair['references']['candidate_exit'] == pins['candidate_API_primary']
    assert pair['references']['candidate_guard'] == pins['source_guard']
    assert pair['decoded_native_records'] == pair['caller_purity_checks'] == len(original['native_records']) + len(API['native_records'])
    assert pair['paired_public_calls'] == len(original['calls']) == len(API['calls'])
    assert pair['paired_whole_case_callers'] == 47
    assert pair['changed_numeric_error_calls'] == 20 and pair['changed_numeric_error_cases'] == 10
    assert pair['changed_preview_pending_pairs'] == 2 and len(pair['changes']) == 22
    assert pair['healthy_full_native_call_pairs'] + pair['changed_numeric_error_calls'] + pair['changed_preview_pending_pairs'] == pair['paired_public_calls']
    assert pair['healthy_calculation_cases'] == 37 and pair['healthy_preview_pairs'] == 6
    assert pair['complete_formatter_text_pairs'] == 76
    assert pair['original_consumer_errors'] == original['consumer_error_count'] == 22
    assert pair['candidate_consumer_errors'] == API['consumer_error_count'] == 20
    assert pair['original_and_candidate_blocked_calculation_cases'] == API['blocked_phase_count'] == 10
    assert pair['deadline_seconds'] == 240 and 0 < pair['elapsed_seconds'] < 240

    # Two real failures and diagnoses are immutable historical gates, not raw0/PASS.
    attempts = []
    for attempt, digest in ((1, 'cd06286e583dab141451d1191a9760349120aebff2513fb773c2d2654744524a'),
                            (2, '3da8b76753568d5a1994db04299655d7770dcd51226166abc9568e5706881974')):
        directory = BASE / ('resume108-window-gold-v%d' % attempt)
        raw = (directory / 'receipt.json').read_bytes()
        failed = json.loads(raw)
        assert sha(raw) == digest and (BASE / ('resume108-window-gold-v%d.exit-code' % attempt)).read_bytes() == b'1\n'
        assert failed['passed'] is failed['workflow_complete'] is False and len(failed['rows']) == len(failed['windows']) == 0
        source_receipt(failed, old['source_sha256'], additional)
        assert failed['Qt_errors'] == []
        attempts.append({'attempt': attempt, 'primary': 1, 'status': 'FAILED_PUBLIC_TEST_RUNNER_CONTRACT_NOT_PRODUCT_PASS',
                         'receipt': pin(directory / 'receipt.json'), 'completed_windows': len(failed['windows']),
                         'snapshots': len(failed['rows']), 'native_records': len(failed['records']),
                         'actual_numeric_calls': failed['actual_numeric_calls'], 'failure': failed['failure'], 'elapsed_seconds': failed['elapsed_seconds']})
    attempts.append({'attempt': 3, 'primary': 0, 'status': 'ACTUAL_COMPLETE_GOLD', 'receipt': pins['gold_receipt'],
                     'completed_windows': len(gold['windows']), 'snapshots': len(gold['rows']),
                     'native_records': len(gold['records']), 'actual_numeric_calls': gold['actual_numeric_calls'], 'elapsed_seconds': gold['elapsed_seconds']})
    for name, kind in (('root-section108-target-boundary-diagnostic-v1.json', 'ROOT_ACTUAL108_SAVED_TARGET_BOUNDARY_DIAGNOSIS'),
                       ('root-section108-cross-api-order-diagnostic-v1/report.json', 'ROOT_ACTUAL108_SAVED_CROSS_API_IDENTITY_ORDER_DIAGNOSIS')):
        value = json.loads((BASE / name).read_bytes())
        assert value['kind'] == kind and value['completed'] is True
        assert value['product_pass'] is value['product_modified'] is value['project_API_Qt_Git_executed'] is False
    qrect = json.loads((BASE / 'section108-qt-rect-center-public-source-v1/SOURCE_EVIDENCE.json').read_bytes())
    assert qrect['actual_PNG_negative_coordinates_observed'] is qrect['Qt_executed'] is qrect['Window_c440_changed'] is False
    transport = json.loads((BASE / 'section108-saved-readback-source-v2/qrect-center-exact-transport.json').read_bytes())
    old_audit = (BASE / 'section108-saved-readback-source-v1/audit108.py').read_bytes()
    assert old_audit.count(transport['before'].encode()) == 1
    assert old_audit.replace(transport['before'].encode(), transport['after'].encode(), 1) == raws['saved_source']
    assert transport['after_sha256'] == AUDIT_SHA and transport['Window_runner_changed'] is transport['actual_Window_attempt_added'] is False

    # Native files are selected only from validated public receipt ledgers. Never
    # copy a whole temporary cache, user profile, private state or runtime folder.
    for label, value, root, domain in (
        ('original-API', original, original_path.parent / 'native', 'native_records'),
        ('candidate-API', API, Path(pins['candidate_API_receipt']['path']).parent / 'native', 'native_records'),
        ('window-Gold3', gold, Path(pins['gold_receipt']['path']).parent / 'records', 'records'),
        ('window-candidate', candidate, Path(pins['candidate_receipt']['path']).parent / 'records', 'records')):
        for path, meta in ledger(value, root, domain):
            add(path, 'actual-native/' + label + '/' + path.name, meta)
    for attempt in (1, 2):
        root = BASE / ('resume108-window-gold-v%d' % attempt)
        failed = json.loads((root / 'receipt.json').read_bytes())
        for path, meta in ledger(failed, root / 'records', 'records'):
            add(path, 'actual-native/failed-window-Gold%d/' % attempt + path.name, meta)
    for key, meta in pins.items():
        add(meta['path'], 'actual-final-inputs/' + key + Path(meta['path']).suffix, meta)
    add(inputs_path, 'actual-final-inputs/root-final-save-inputs.json', pin(inputs_path))
    for row in inputs.get('additional_public_files', []):
        assert type(row) is dict and set(row) == {'pin', 'destination'}
        path = safe(row['pin']['path'])
        assert path.name.startswith(('root-section108-', 'root-resume108-', 'resume108-', 'section108-')) or any(
            parent.name.startswith(('section108-', 'resume108-')) for parent in path.parents if parent != BASE)
        assert path.suffix in ('.json', '.py', '.md', '.diff', '.log', '.exit-code', '.h')
        assert row['destination'].startswith('additional-public-108/')
        add(path, row['destination'], row['pin'])
    self_manifest = json.loads((packet / 'SOURCE_MANIFEST.json').read_bytes())
    for name, meta in self_manifest['files'].items():
        path = packet / name
        assert path.is_file() and not path.is_symlink() and len(path.read_bytes()) == meta['bytes'] and sha(path.read_bytes()) == meta['sha256']
        add(path, 'final-save-Source/' + name)
    add(packet / 'SOURCE_MANIFEST.json', 'final-save-Source/SOURCE_MANIFEST.json')

    # Recheck every final pin and maintained Source around the final JSON gates.
    assert source_map() == expected and sha((ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes()) == CORE_SHA
    assert Path(pins['source_guard']['path']).read_bytes() == raws['source_guard']
    for key in PIN_KEYS:
        assert bound(pins[key]) == raws[key]
    for row in entries:
        bound(row['source_pin'], row['source'])
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    text = (f'本局区域consumer输入资格收口；原falsey/inactive、knownID优先、portal已有深度继承、grade0/4与未知pending保持。16个新增API测试方法；'
            f'Linux相关{related["linux"]["tests_run"]}/{related["linux"]["tests_passed"]}PASS/skip{related["linux"]["skipped"]}/U{related["linux"]["unavailable_parent_count"]}父项；'
            f'Wine相关{related["wine"]["tests_run"]}/{related["wine"]["tests_passed"]}PASS/skip{related["wine"]["skipped"]}/U{related["wine"]["unavailable_parent_count"]}父项；'
            f'精选119登记、{selected["tests_run"]}实际运行/skip{selected["skipped"]}，均0失败0错误。'
            f'第三次Gold实际成功（前两raw1保留），Gold/候选各43快照、2窗口；33完整健康Gold同输入点、10明确错误/pending变化点；'
            f'主Saved解码{len(saved["decoded_records"])}原件，另独立API配对解码{pair["decoded_native_records"]}原件/{pair["paired_public_calls"]}消费者；四图实际查看，Source751+CORE守恒。')
    report = f'''# 第108节本局区域consumer输入资格

{stamp}（北京时间）。本报告只有全部实际raw0、完整Source、两份独立Saved、实际四图绑定齐备后才生成；本脚本不执行产品、测试、Qt、Wine或Git，也不填写未来commit。

{text}

原API caadc仍是observation-only/product_passFalse：47计算case+8preview、{original['actual_explicit_consumer_calls']}显式消费者、{len(original['native_records'])}native、{original['consumer_error_count']}原异常、{original['blocked_phase_count']}实际阻断。候选API同样是观察原件：{API['actual_explicit_consumer_calls']}消费者、{len(API['native_records'])}native、{API['consumer_error_count']}明确异常、{API['blocked_phase_count']}实际阻断。异常输入的20个数值消费明确ValueError保留，两个preview按原pending合同返回；不要求错误观察数为0，不把运行raw0冒称产品全部机制正确。独立API配对Saved核验原/候选完整健康输出、三formatter/control与既有全部caller；20明确错误改变、2preview pending改变，其余{pair['healthy_full_native_call_pairs']}完整消费者保原，原异常、blocked与全部native都保留。主Saved读回只消费原API与两个窗口，绝不将它误称候选API配对证明。两份Saved合计{len(saved['decoded_records'])+pair['decoded_native_records']}次解码，其中{len(original['native_records'])}个原API原件在两份审计重复读回；唯一公开native原件为{len(original['native_records'])+len(API['native_records'])+len(gold['records'])+len(candidate['records'])}件，不把总解码次数称作独立原件数。

变更只在原confirmed target+grade消费分支，为truthy非dict区域和不可hash的区域ID提供明确ValueError；未放宽Savedname/ID/schema，未清洗原caller、缓存或未确认区域，不补zone深度、mode或游戏公式。已知zone1..6/4_1仍优先于陈旧main；falsey、未启用/无target、grade0/4的原路径、portal未知与原Boolean资格保持。合法fresh公开观察先main4_1建立4，随后portal输入6按既有RunState保持已知4并实际save/reload；旧合法缓存main[6]原typed值和原文件/tmp bytes保留，消费者只用knownID。

Gold1实际raw1：0完成窗口/0快照、17native、10实际numeric、24.0418508秒；Gold2实际raw1：0窗口/0快照、23native、11实际numeric、51.0915963秒。两次均原测试工具的identity insertion-order预期问题，两个Root纯Saved诊断证明真实原callers/结果未改，v4仅按两个独立API各自声明顺序对三scalar身份前缀作单独比较拷贝，保所有余下键顺序、类型、floatbits、值、alias和各自完整Gold原件。第三次Gold完成{len(gold['rows'])}快照/{len(gold['windows'])}窗口/{len(gold['records'])}native/{gold['actual_numeric_calls']}实际numeric/{gold['elapsed_seconds']}秒；候选完成{len(candidate['rows'])}快照/{len(candidate['windows'])}窗口/{len(candidate['records'])}native/{candidate['actual_numeric_calls']}实际numeric/{candidate['elapsed_seconds']}秒。候选与第三Gold使用同一c440完整runner，不将Source版本数计额外运行。

43快照为40个明确公开内存consumer输入、1个真实合法原缓存、2个真实合法fresh保存；仅两个健康constructor。坏内存输入在健康构造之后明确赋入config，不走Saved/OCR资格、不写盘；恢复原合法图后才close。Saved的86快照/80内存admission/4合法观察/4直接RunState重载及实际共同UI/三formatter组逐条读回；33健康完整图相等，10原错误转明确错误/pending仍完整保原caller/durable/disks。共同UI步{len(saved['UI_pure_checks'])}、共同三formatter组{len(saved['formatter_group_checks'])}、独立API身份比较边界{len(saved['cross_API_boundary_checks'])}均来自实际ledger。主Saved的preview_checks统计桶实际为空（reader未append该桶）；真实独立preview输入/输出/formatter由完整native遍历及43snapshot逐点核验，不把空桶伪写成执行次数。

Saved reader v1→v2仅QRect.center整数公式校正，公开Qt官方v6.9.3 qrect.h和精确局部逆向证据一并归档。C++整数除法向零，不能用Python负数floor替代；这是reader Source取证修正，实际负坐标观察没有发生，c440窗口未改，没有额外Gold或产品修复计数。原inactive模板保持readyFalse且仍含历史v1引用，实际freshbindings必须精确绑定真正执行的v2/f46 reader，不借模板的未来空项作为验证。

四图由Root实际查看，绑定真实候选PNG bytes/hash、当前文本、anchor、viewport或QLabel；不把runner的Root_visual_verifiedFalse改作看图证明。窗口共同step及共同三formatter组纯度已验证；逐formatter独立prepost、跨分freeze原内存alias、JSON保alias、第二MainWindow重开、自然OCR、非法Saved缓存准入、原生Windows硬件、游戏/聊天均没有验证。unknown portal/pending、动态地图buff/召唤物/绝对时钟与其他未实现P2/P3仍按资料保留未知。

新增cloud119只prepend108；full NEW41和原helper字节不变，原union自动变242。相关Linux/Wine原AvailableResult的skip/U父项分别保留，不计PASS；本节没有冒称完整全量。精选日志自身无完整Source-map，最终Source751+CORE在真实pipeline完成后及最终receipt检查前后守恒，不能伪称精选自身前后带map。last full105和旧95三次deferred原封保留；下一五节节点110全量与总结。本节归档与实际commit/push由独立Root saver/publisher完成，之后按用户要求收束。断点next109、nextfull110保留；109还要原focused/permanent实际证据，此次不启动、不预计完成。已封存的109 focused/permanent原probe、风险限定draft与Source独审，以及110 adapter/完整窗口草稿/独审，均单列prepared-unapplied-next逐叶归档，Runtime/actual guard/结果仍NULL、未编入和未执行，不计完成小节。
'''
    report_raw = report.encode()
    assert report_path.as_posix() not in {r['source'] for r in entries}
    entries.append({'source': str(report_path), 'destination': 'REPORT_ZH.md',
                    'source_pin': {'path': str(report_path), 'bytes': len(report_raw), 'sha256': sha(report_raw)}})
    receipt = {'implemented_scope': guard['scope'], 'new_test_methods': 16,
               'related_linux': summary(related['linux']), 'related_wine': summary(related['wine']),
               'actual_selected_log': pins['selected_log'], 'actual_selected_primary': pins['selected_primary'],
               'selected_tests': selected, 'selected_receipt_has_its_own_fullSource_map': False,
               'current751_CORE_guard_verified_after_actual_pipeline_and_around_final_receipt_checks': True,
               'Gold_attempts': attempts, 'Gold_windows': len(gold['windows']), 'candidate_windows': len(candidate['windows']),
               'Gold_snapshots': len(gold['rows']), 'candidate_snapshots': len(candidate['rows']),
               'Gold_native': len(gold['records']), 'candidate_native': len(candidate['records']),
               'Gold_actual_numeric_calls': gold['actual_numeric_calls'], 'candidate_actual_numeric_calls': candidate['actual_numeric_calls'],
               'API_original_observation': {k: original[k] for k in ('actual_explicit_consumer_calls', 'actual_native_records', 'consumer_error_count', 'blocked_phase_count')},
               'API_candidate_observation': {k: API[k] for k in ('actual_explicit_consumer_calls', 'actual_native_records', 'consumer_error_count', 'blocked_phase_count')},
               'API_observation_is_product_PASS': False, 'main_Saved_decoded_records': len(saved['decoded_records']),
               'independent_API_paired_Saved_decoded_records': pair['decoded_native_records'], 'API_paired_consumers': pair['paired_public_calls'],
               'total_Saved_decode_operations': len(saved['decoded_records']) + pair['decoded_native_records'],
               'repeated_original_API_records_in_two_audits': len(original['native_records']),
               'unique_native_records_in_both_API_and_Window_domains': len(original['native_records']) + len(API['native_records']) + len(gold['records']) + len(candidate['records']),
               'complete_same_input_UI_Gold_points': 33, 'intended_changed_UI_points': 10,
               'Saved_UI_snapshots': len(saved['snapshot_checks']), 'public_memory_admissions': len(saved['memory_admission_checks']),
               'legal_observation_saves': len(saved['legal_observation_checks']), 'actual_close_direct_RunState_records': len(saved['restart_checks']),
               'four_pngs_actually_viewed': True, 'new_source_files': 1, 'source_count': 751,
               'cloud_selectors': 119, 'full_NEW_MODULES_unchanged': True, 'full_union_selectors': 242,
               'window_per_UI_step_prepost_saved_verified': True, 'common_three_formatter_group_prepost_saved_verified': True,
               'individual_formatter_prepost_saved_verified': False, 'cross_separate_freeze_live_alias_verified': False,
               'JSON_preserves_live_aliases_verified': False, 'second_MainWindow_reopen_verified': False,
               'natural_OCR_producer_verified': False, 'malformed_saved_cache_admission_verified': False,
               'actual_negative_QRect_coordinates_observed': False, 'reader_v2_correction_changed_Window_or_product': False,
               'new_game_or_dynamic_portal_mechanism_verified': False, 'native_windows_game_chat_verified': False,
               'full095_deferred_preserved': True, 'last_full_validation_preserved_after_section': 105, 'next_full_validation_after': 110,
               'actual_final_window_runner': pins['window_runner'], 'actual_final_Saved_Source': pins['saved_source'],
               'actual_Saved_receipt': pins['saved_receipt'], 'actual_Saved_bindings': pins['bindings'],
               'actual_independent_API_paired_Source': pins['API_pair_source'], 'actual_independent_API_paired_receipt': pins['API_pair_receipt'],
               'prepared_unapplied_next_Source_only': plan['prepared_unapplied_next']}
    spec = {'section': 108, 'topic': '本局区域consumer输入资格', 'archive': 'research/p2-section108-active-zone-consumer',
            'source_guard': pins['source_guard']['path'], 'exit_files': [pins[k]['path'] for k in PIN_KEYS if k.endswith('_primary')],
            'pass_receipts': [pins[k]['path'] for k in ('saved_receipt', 'API_pair_receipt', 'visual')],
            'public_evidence': entries, 'previous_publication': str(BASE / 'section107-publication-v1.json'),
            'next_action': '108实际commit/push后按用户要求收束；恢复断点next109，先真实focused/permanent原API再推进owner空供靶族，nextfull110全量和总结；lastfull105及95deferred保留，未知游戏机制不编造。',
            'archive_readme': '# 第108节本局区域consumer输入资格\n\n实际范围与局限见REPORT_ZH.md。两次真实Gold raw1、第三真实Gold、两份原Saved诊断、完整公开Source历史、Qt官方QRect公开证据及reader v1/v2均逐leaf列明。观察原件product_passFalse不冒称PASS；不归档私有目录或未结束输出。',
            'section_receipt': receipt, 'completed_paragraph': text,
            'work_paragraph': text + ' 当前归档后真实commit/push并按用户要求收束；断点109未动工、110为下一全量节点。'}
    # First writes: all terminal/Saved/image/retained-failure/public Source gates
    # above passed. Output remains off-repo; no tracked write or Git invocation.
    with report_path.open('xb') as stream:
        stream.write(report_raw)
    with spec_path.open('x', encoding='utf-8') as stream:
        json.dump(spec, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'spec': str(spec_path), 'public_files': len(entries), 'source_files': len(expected)}))


if __name__ == '__main__':
    main()
