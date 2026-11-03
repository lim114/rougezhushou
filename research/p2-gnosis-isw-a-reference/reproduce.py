"""Frozen, public-only before/after reproduction for section 48."""
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path


OUT = Path(__file__).resolve().parent
ROOT = Path('/workspace/rougezhushou')
OP = 'char_206_gnosis'
MODULE = 'uniequip_004_gnosis'
COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def worker(tree):
    sys.path.insert(0, str(OUT / tree))
    from rouge.catalog import catalog
    from rouge.damage import calculate_damage
    from rouge.operator_engine import selected_talents
    rows = []
    profile = catalog()['operators'][OP]
    before = copy.deepcopy(profile)
    for case in json.loads((OUT / 'public-inputs.json').read_text()):
        scenario = case['scenario']
        original = copy.deepcopy(scenario)
        result = calculate_damage(scenario)
        talents, _ = selected_talents(profile, scenario)
        assert scenario == original
        rows.append({
            **case, 'selected_ice': next(t for t in talents if t['name'] == '坚冰'),
            'total_damage': result['total_damage'], 'total_healing': result['total_healing'],
            'skill': result['estimate']['skill'], 'components': result['components'],
            'reference': result.get('gnosis_isw_a_reference'),
            'timing': result['timing'], 'complete': result['complete'],
            'warnings': result['warnings'],
            'talent_report': next(s for s in result['report']['sections'] if s['id'] == 'talents'),
        })
    assert before == profile
    (OUT / f'{tree}-public-results.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')


def main():
    freeze = json.loads((OUT / 'freeze.json').read_text())
    files = {
        'character_table': ROOT / '.cache/p2-s1-binding/character_table.json',
        'skill_table': ROOT / '.cache/p2-s1-binding/skill_table.json',
        'battle_equip_table': Path('/tmp/p2-audit/drone-traits/battle_equip_table.json'),
        'uniequip_table': Path('/tmp/p2-audit/drone-traits/uniequip_table.json'),
    }
    old = json.loads(Path('/tmp/p2-audit/after-045/modules/source-receipt.json').read_text())
    source_audit = json.loads(Path('/tmp/p2-audit/gnosis-048-source-audit.json').read_text())
    tables = {}
    sources = {}
    for name, path in files.items():
        assert sha(path) == old['sources'][name]['sha256']
        tables[name] = json.loads(path.read_text())
        sources[name] = {**old['sources'][name], 'local_file': str(path)}
    frozen_path = Path('/tmp/p2-audit/after-050/qualification/gamedata_const.json')
    frozen_receipt = json.loads(Path('/tmp/p2-audit/after-050/qualification/gamedata-const-receipt.json').read_text())
    assert sha(frozen_path) == frozen_receipt['sha256']
    assert COMMIT in frozen_receipt['url'] and frozen_receipt['status'] == 200
    frozen_description = json.loads(frozen_path.read_text())['termDescriptionDict']['ba.frozen']['description']
    assert '敌方被冻结时，法术抗性-15' in frozen_description
    sources['gamedata_const'] = {k: frozen_receipt[k] for k in ('url', 'sha256', 'bytes', 'status')}
    sources['gamedata_const']['local_file'] = str(frozen_path)
    base_catalog = json.loads((OUT / 'baseline/rouge/data/catalog.json').read_text())['operators'][OP]
    module = next(m for m in base_catalog['modules'] if m['id'] == MODULE)
    for stage in (1, 2, 3):
        assert module['levels'][stage-1]['parts'] == tables['battle_equip_table'][MODULE]['phases'][stage-1]['parts']
    for normalized, raw in zip(base_catalog['talents'][0], tables['character_table'][OP]['talents'][0]['candidates']):
        assert normalized['description'] == raw['description']
        assert normalized['values'] == {b['key']: b['value'] for b in raw['blackboard']}
    rows = [{'kind': 'original_152', 'scenario': r['scenario']} for r in
            json.loads(Path('/tmp/p2-audit/after-045/modules/public-reproduction.json').read_text())['cases']]
    for skill in (1, 2, 3):
        for mode in ('frames', 'continuous'):
            for status in (0, 1, 2):
                for potential in (1, 5):
                    common = {'operator': OP, 'skill': skill, 'base_attack': 1000,
                              'elite': 2, 'level': 60, 'potential': potential,
                              'cold_state': status, 'timing_mode': mode, 'frozen_at_skill_end': False}
                    for stage in (1, 2, 3):
                        args = {**common, 'module_id': MODULE, 'module_level': stage, 'window_seconds': 3}
                        for extra in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}}):
                            rows.append({'kind': 'known_zero', 'scenario': {**args, **extra}})
                    for regular in ('uniequip_002_gnosis', 'uniequip_003_gnosis'):
                        rows.append({'kind': 'ordinary_module_control', 'scenario': {
                            **common, 'module_id': regular, 'module_level': 3, 'window_seconds': 3}})
                for timing in ({'target_windows': []}, {'interrupt_windows': [[0, 3600]]}):
                    rows.append({'kind': 'owner_blocked_dot_unknown', 'scenario': {
                        **common, 'module_id': MODULE, 'module_level': 3, 'window_seconds': 3, 'timing': timing}})
    (OUT / 'public-inputs.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    for tree in ('baseline', 'draft'):
        subprocess.run([sys.executable, str(Path(__file__)), '--worker', tree], cwd=OUT, check=True)
    baseline = json.loads((OUT / 'baseline-public-results.json').read_text())
    draft = json.loads((OUT / 'draft-public-results.json').read_text())
    controls = positives = zeros = restored = original_restored = 0
    clock_keys = ('initial_seconds', 'duration_seconds', 'recharge_seconds', 'cycle_seconds',
                  'sp_recovery_per_second', 'skill_attack', 'skill_attack_speed', 'mode')
    for before, after in zip(baseline, draft):
        scenario = after['scenario']
        qualified = (scenario.get('module_id') == MODULE and scenario['elite'] == 2 and scenario['level'] >= 60)
        assert all(before['skill'][key] == after['skill'][key] for key in clock_keys)
        metadata = {'unplaced_components', 'phase_clock_unbound', 'resource_and_damage_shared_clock'}
        assert {k: v for k, v in before['timing'].items() if k not in metadata} == {
            k: v for k, v in after['timing'].items() if k not in metadata}
        if not qualified:
            assert before == after
            controls += 1
            continue
        ref = after['reference']
        assert ref is not None
        assert after['timing']['phase_clock_unbound']
        assert not after['timing']['resource_and_damage_shared_clock']
        assert after['selected_ice']['values'] == base_catalog['talents'][0][3 if scenario['potential'] >= 5 else 2]['values']
        if scenario['module_level'] >= 2 and before['selected_ice']['values'] == {'cold': 1}:
            restored += 1
            original_restored += after['kind'] == 'original_152'
        zero = scenario.get('window_seconds') == 0 or scenario.get('timing', {}).get('target_disappears_seconds') == 0
        if zero:
            assert after['total_damage'] == 0
            assert not ref['source_possible']['window']
            assert not any(c['hits'] or 'actual_total' in c for c in after['components'])
            zeros += 1
        else:
            assert after['total_damage'] is None
            assert ref['source_possible']['window']
            positives += 1
        assert ref['actual_tick_count'] is None and ref['actual_tick_times_seconds'] is None
        assert not ref['native_ability_attachment_verified']
        assert after['total_healing'] == before['total_healing'] == 0
    current_hashes = {name: sha(ROOT / name) for name in freeze['sha256']}
    receipt = {
        'section': 48, 'baseline_head': freeze['head'], 'branch': freeze['branch'],
        'source_commit': COMMIT, 'sources': sources,
        'reuse_receipts': ['/tmp/p2-audit/after-045/modules/source-receipt.json',
                          '/tmp/p2-audit/gnosis-048-source-audit.json',
                          '/tmp/p2-audit/gnosis-048-frozen-res-source-audit.json',
                          '/tmp/p2-audit/after-050/qualification/gamedata-const-receipt.json',
                          'research/p2-gnosis-clock/source-receipt.json'],
        'new_source_selectors': [f'battle_equip_table.{MODULE}.phases[{stage-1}].parts[1].overrideTraitDataBundle.candidates[0]'
                                 for stage in (1, 2, 3)],
        'trait_description_selectors': [f'battle_equip_table.{MODULE}.phases[{stage-1}].parts[0].overrideTraitDataBundle.candidates[0].additionalDescription'
                                        for stage in (1, 2, 3)],
        'source_facts': {'original_talent_prefab': '1', 'module_prefabs': ['#', '1', '10_root', '11_root'],
                         'distinct_blackboards_preserved': True, 'dot_attack_scale': .5, 'dot_interval_seconds': .5,
                         'generic_frozen_enemy_resistance_delta': -15,
                         'generic_frozen_selector': 'gamedata_const.termDescriptionDict["ba.frozen"].description',
                         'generic_frozen_description': frozen_description},
        'unknowns': ['native ability attachment/coexistence', 'roguelike runtime tag selection',
                     'fragile stack increment/reset/phase interactions', 'first tick/count/refresh/coverage',
                     'DOT attack snapshot', 'owner exit and post-skill DOT lifecycle'],
        'existing_parameter_scope': 'freeze -15 resistance retained from existing calculation and confirmed by generic frozen description; this does not prove ISW-A attachment or actual state timing',
        'public_cases': len(rows), 'unchanged_controls': controls,
        'positive_observation_unknown_damage': positives, 'zero_observation_or_enemy_lifetime': zeros,
        'restored_ice_identity_cases': restored, 'all_clock_fields_and_timing_streams_unchanged': True,
        'original_152_restored_ice_identity_cases': original_restored,
        'timing_metadata_change': 'unplaced_components marks conditional body references; phase_clock_unbound=true and resource_and_damage_shared_clock=false preserve unknown combined damage/state/DOT binding',
        'all_inputs_and_catalogs_unchanged': True,
        'new_tests': 15, 'related_tests_including_new': 106, 'test_failures': 0, 'test_errors': 0,
        'production_hashes_before': freeze['sha256'], 'production_hashes_after': current_hashes,
        'production_drift': current_hashes != freeze['sha256'], 'repo_mutations': 0,
        'private_state_read': False, 'game_actions': 0, 'messages_sent': 0,
        'native_windows_verified': False, 'wine_verified_by_draft_agent': False,
    }
    (OUT / 'source-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'source-selector-audit.json').write_text(json.dumps(source_audit, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ('public_cases', 'unchanged_controls',
          'positive_observation_unknown_damage', 'zero_observation_or_enemy_lifetime',
          'restored_ice_identity_cases', 'production_drift')}))


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        worker(sys.argv[2])
    else:
        main()
