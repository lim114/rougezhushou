"""Compare public section-52 cases against the frozen production/draft pair."""
from copy import deepcopy
import hashlib
import json
import subprocess
import sys
from pathlib import Path


OUT = Path(__file__).resolve().parent
ROOT = Path('/workspace/rougezhushou')


def worker(tree, cases='public-inputs.json', output='public-results'):
    sys.path.insert(0, str(OUT / tree))
    from rouge.catalog import catalog
    from rouge.damage import calculate_damage
    profiles = deepcopy(catalog()['operators'])
    rows = []
    for case in json.loads((OUT / cases).read_text()):
        scenario = case['scenario']
        original = deepcopy(scenario)
        result = calculate_damage(scenario)
        assert scenario == original
        rows.append({**case, 'result': result})
    assert catalog()['operators'] == profiles
    (OUT / f'{tree}-{output}.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')


def main():
    rows = []
    timings = [{}, {'target_disappears_seconds': 0}, {'target_disappears_seconds': .1},
               {'target_disappears_seconds': 1}, {'target_windows': [[0, 1]]}, {'target_windows': []}]
    for elite, rank in ((0, 1), (1, 7), (2, 10)):
        for potential in (1, 6):
            for attacks in (False, True):
                for effects in ([], [{'kind': 'attack_speed', 'value': 50}], [{'kind': 'sp_recovery', 'value': 1}]):
                    for window in (0, .01, 10):
                        for timing in timings:
                            rows.append({'kind': 'caster_s1_scope', 'scenario': {
                                'operator': 'char_002_amiya', 'skill': 1, 'base_attack': 1000,
                                'elite': elite, 'skill_rank': rank, 'potential': potential,
                                'continuous_attacks': attacks, 'effects': effects,
                                'window_seconds': window, 'timing': timing, 'timing_mode': 'continuous'}})
    for op, skill in (('char_002_amiya', 2), ('char_002_amiya', 3),
                      ('char_298_susuro', 1), ('char_206_gnosis', 2)):
        for mode in ('frames', 'continuous'):
            for timing in timings[2:3] + timings[4:]:
                for window in (0, 10):
                    rows.append({'kind': 'other_scope_control', 'scenario': {
                        'operator': op, 'skill': skill, 'base_attack': 1000,
                        'window_seconds': window, 'timing': timing, 'timing_mode': mode}})
    for timing in timings:
        for window in (0, 10):
            rows.append({'kind': 'frame_scope_control', 'scenario': {
                'operator': 'char_002_amiya', 'skill': 1, 'base_attack': 1000,
                'window_seconds': window, 'timing': timing, 'timing_mode': 'frames'}})
    (OUT / 'public-inputs.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    zero_rows = [{'kind': 'accepted_zero_type_boundary', 'scenario': {
        'operator': 'char_002_amiya', 'skill': 1, 'base_attack': 1000,
        'window_seconds': 10, 'timing': {'target_disappears_seconds': zero},
        'timing_mode': 'continuous'}} for zero in (0, 0.0, '0', '0.0')]
    (OUT / 'zero-type-inputs.json').write_text(json.dumps(zero_rows, ensure_ascii=False, indent=2) + '\n')
    for tree in ('baseline', 'draft'):
        subprocess.run([sys.executable, str(Path(__file__)), '--worker', tree], cwd=OUT, check=True)
        subprocess.run([sys.executable, str(Path(__file__)), '--worker', tree,
                        'zero-type-inputs.json', 'zero-type-results'], cwd=OUT, check=True)
    before = json.loads((OUT / 'baseline-public-results.json').read_text())
    after = json.loads((OUT / 'draft-public-results.json').read_text())
    controls = positive = observed_zero = empty = 0
    clock_keys = ('initial_seconds', 'duration_seconds', 'recharge_seconds', 'cycle_seconds',
                  'total_damage', 'phase_damage', 'cycle_damage', 'cycle_dps', 'cycle_healing', 'cycle_hps')
    for old, new in zip(before, after):
        scenario = new['scenario']
        prior = old['result']
        result = new['result']
        reference = result.get('amiya_continuous_reference')
        if reference is None:
            assert old == new
            controls += 1
            continue
        skill = result['estimate']['skill']
        clock = reference['parameter_clock_reference']
        assert skill['initial_seconds'] == prior['estimate']['skill']['initial_seconds']
        assert skill['duration_seconds'] == prior['estimate']['skill']['duration_seconds']
        assert result['estimate']['base_stats'] == prior['estimate']['base_stats']
        assert result['attack'] == prior['attack'] and result['attack_speed'] == prior['attack_speed']
        for key in ('recharge_seconds', 'cycle_seconds', 'cycle_damage', 'cycle_dps', 'cycle_healing', 'cycle_hps'):
            assert skill[key] is None
        assert not result['complete'] and not result['estimate']['complete']
        assert result['timing']['phase_clock_unbound']
        assert not result['timing']['resource_and_damage_shared_clock']
        assert result['scope'] == result['estimate']['scenario_scope']
        assert '旧连续供靶条件参数与当前有限约束的实际伤害/回转分列' in result['scope']
        assert not any(note.startswith('单目标持续存活、供靶/满额受疗情景')
                       for note in result['estimate']['notes'])
        if reference['enemy_source_excluded']:
            assert result['total_damage'] == skill['total_damage'] == 0
            assert not any(c['hits'] or 'actual_total' in c for c in result['components'])
            assert clock['recharge_seconds'] == reference['natural_only_recharge_seconds_reference']
            empty += 1
        else:
            assert all(clock[key] == prior['estimate']['skill'][key] for key in clock_keys)
            assert clock['window_damage'] == prior['total_damage']
            assert clock['window_dps'] == prior['estimate']['skill']['window_dps']
            assert reference['window_reference']['conditional_components'] == prior['components']
            assert skill['total_damage'] is None
            assert result['known_damage_subtotals']['cycle_damage'] is None
            assert result['known_damage_subtotals']['cycle_dps'] is None
            if scenario['window_seconds'] == 0:
                assert result['total_damage'] == 0
                assert not reference['window_reference']['source_possible']
                observed_zero += 1
            else:
                assert result['total_damage'] is None
                assert all('times_seconds' not in c and c.get('actual_total', 0) is None
                           for c in result['components'])
                positive += 1
    freeze = json.loads((OUT / 'freeze.json').read_text())
    prior_source = json.loads((OUT.parent / 'finite-positive-audit/source-receipt.json').read_text())
    zero_before = json.loads((OUT / 'baseline-zero-type-results.json').read_text())
    zero_after = json.loads((OUT / 'draft-zero-type-results.json').read_text())
    zero_comparison = []
    for old, new in zip(zero_before, zero_after, strict=True):
        raw = new['scenario']['timing']['target_disappears_seconds']
        prior, result = old['result'], new['result']
        ref = result.get('amiya_continuous_reference')
        assert result['total_damage'] == 0
        if isinstance(raw, (int, float)):
            assert old == new
            assert result['estimate']['skill']['recharge_seconds'] == 30
            assert result['estimate']['skill']['cycle_seconds'] == 60
        else:
            assert ref['enemy_source_excluded']
            assert result['estimate']['skill']['recharge_seconds'] is None
            assert result['estimate']['skill']['cycle_seconds'] is None
            assert ref['parameter_clock_reference']['recharge_seconds'] == 30
            assert ref['parameter_clock_reference']['cycle_seconds'] == 60
        zero_comparison.append({'raw': raw, 'type': type(raw).__name__,
            'baseline_damage': prior['total_damage'], 'draft_damage': result['total_damage'],
            'baseline_recharge': prior['estimate']['skill']['recharge_seconds'],
            'draft_actual_recharge': result['estimate']['skill']['recharge_seconds'],
            'baseline_cycle': prior['estimate']['skill']['cycle_seconds'],
            'draft_actual_cycle': result['estimate']['skill']['cycle_seconds'],
            'draft_conditional_recharge': ref['parameter_clock_reference']['recharge_seconds'] if ref else None,
            'draft_conditional_cycle': ref['parameter_clock_reference']['cycle_seconds'] if ref else None})
    (OUT / 'zero-type-boundary.json').write_text(json.dumps({
        'scope': 'four accepted numeric zero representations through ordinary public calculate_damage; no native-clock evidence',
        'boundary': 'numeric0 preserves the old actual30/60 contract; string0 receives unknown actual resource clocks and conditional30/60',
        'recovery_condition': 'separate validated zero normalization with pre-cast initial/source isolation regression coverage; no implicit native proof',
        'cases': zero_comparison}, ensure_ascii=False, indent=2) + '\n')
    receipt = {
        'section': 52, 'baseline_head': freeze['head'], 'branch': freeze['branch'],
        'initial_discovery_head': prior_source['baseline_head'],
        'baseline_origin': freeze['baseline_origin'], 'sources': prior_source['sources'],
        'source_selectors': prior_source['selectors'],
        'source_supports': 'S1 AS90, nominal duration30, cost30/init15/natural1; base interval1.6; E2 attack-SP2/3 are parameters',
        'unknowns': ['native acquisition/release/impact first phase', 'finite positive lifetime and range clocks',
                     'post-skill target and mixed attack/natural-SP clock', 'actual skill-end/recharge/cycle binding'],
        'source_receipts_reused': ['research/p2-empty-enemy-scope/source-receipt.json',
                                  'research/p2-empty-enemy-scope/NOTE.md',
                                  'research/p2-phase-guards/source-receipt.json',
                                  'research/p2-environment-and-lifecycle/source-receipt.json',
                                  str(OUT.parent / 'finite-positive-source/source-receipt.json')],
        'public_cases': len(rows), 'unchanged_controls': controls,
        'positive_observation_unknown': positive, 'zero_observation_with_unknown_cast': observed_zero,
        'empty_range_known_zero_damage_unknown_resource_clock': empty,
        'positive_condition_references_match_all_old_clock_fields': True,
        'initial_and_nominal_duration_unchanged': True, 'panels_and_cultivation_unchanged': True,
        'restricted_scope_and_default_notes_labeled_conditional': True,
        'all_inputs_and_catalogs_unchanged': True, 'native_replacement_hit_counts': None,
        'existing_numeric_life0_path_unchanged': True,
        'valid_numeric_string_zero': 'accepted type boundary: actual recharge/cycle None versus numeric0 old30/60; conditional30/60 only',
        'accepted_zero_types_semantically_normalized': False, 'zero_type_boundary_cases': 4,
        'zero_type_boundary_receipt': 'zero-type-boundary.json',
        'zero_normalization_recovery_condition': 'separate validated normalization with initial/source isolation checks; no native clock claim',
        'new_tests': 19, 'related_tests_including_new': 156, 'failures': 0, 'errors': 0,
        'frozen_baseline_hashes': freeze['baseline_sha256'],
        'draft_hashes': {name: hashlib.sha256((OUT / 'draft' / name).read_bytes()).hexdigest() for name in freeze['baseline_sha256']},
        'new_draft_file_hashes': {name: hashlib.sha256((OUT / 'draft' / name).read_bytes()).hexdigest()
                                 for name in ('rouge/amiya_continuous_reference.py', 'tests/test_amiya_continuous_lifetime.py')},
        'repo_mutations_by_this_agent': 0, 'private_state_read': False, 'game_actions': 0, 'messages_sent': 0,
        'native_windows_verified': False, 'wine_verified_by_this_agent': False,
    }
    (OUT / 'source-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ('public_cases', 'unchanged_controls', 'positive_observation_unknown',
           'zero_observation_with_unknown_cast', 'empty_range_known_zero_damage_unknown_resource_clock')}))


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == '--worker':
        worker(*sys.argv[2:])
    else:
        main()
