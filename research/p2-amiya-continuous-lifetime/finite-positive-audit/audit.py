"""Read-only public reproductions against the frozen section-50 package."""
from copy import deepcopy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT / 'frozen'))
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


freeze = json.loads((OUT / 'freeze.json').read_text())
prior = json.loads((ROOT / 'research/p2-empty-enemy-scope/source-receipt.json').read_text())
tables = {}
sources = {}
for name in ('character_table', 'skill_table'):
    path = ROOT / '.cache/p2-s1-binding' / f'{name}.json'
    expected = prior['sources'][name]['sha256']
    assert sha(path) == expected
    tables[name] = json.loads(path.read_text())
    sources[name] = {**prior['sources'][name], 'current_sha256': expected}
op = tables['character_table']['char_002_amiya']
skill_id = op['skills'][0]['skillId']
assert skill_id == 'skcom_magic_rage[3]'
source_skill = tables['skill_table'][skill_id]['levels'][9]
base = {'operator': 'char_002_amiya', 'skill': 1, 'base_attack': 1000,
        'timing_mode': 'continuous', 'window_seconds': 10}
rows = []
cases = [
    ('continuous supply control', 'control', {}),
    ('finite positive enemy lifetime .1', 'counterexample_family_1', {'target_disappears_seconds': .1}),
    ('finite positive enemy lifetime 1', 'counterexample_family_1_repeat', {'target_disappears_seconds': 1}),
    ('positive owner range [0,1)', 'counterexample_family_2', {'target_windows': [[0, 1]]}),
    ('zero lifetime established control', 'control', {'target_disappears_seconds': 0}),
    ('empty owner range diagnostic', 'counterexample_family_2_empty_boundary', {'target_windows': []}),
]
for label, family, timing in cases:
    scenario = {**base, 'timing': timing}
    original = deepcopy(scenario)
    result = calculate_damage(scenario)
    assert scenario == original
    rows.append({'label': label, 'family': family, 'scenario': scenario,
                 'result': result, 'report_text': format_estimate(result)})
baseline = rows[0]['result']
assert baseline['total_damage'] == 11000
for row in rows[1:4] + rows[5:]:
    result = row['result']
    assert result['total_damage'] == baseline['total_damage']
    assert result['estimate']['skill'] == baseline['estimate']['skill']
    assert result['estimate']['complete'] is True
    assert result['components'] == baseline['components']
zero = rows[4]['result']
assert zero['total_damage'] == 0
assert zero['estimate']['skill']['recharge_seconds'] == 30
assert zero['estimate']['skill']['initial_seconds'] == baseline['estimate']['skill']['initial_seconds'] == 7
(OUT / 'public-reproduction.json').write_text(json.dumps({'cases': rows}, ensure_ascii=False, indent=2) + '\n')
facts = {
    'source_scope': 'original caster Amiya S1 parameters and attack-SP talent; native finite-positive continuous clocks unverified',
    'sources': sources,
    'selectors': {
        'skill_mapping': 'character_table.char_002_amiya.skills[0].skillId',
        'skill': 'skill_table.skcom_magic_rage[3].levels[9]',
        'talent': 'character_table.char_002_amiya.talents[0].candidates[1]',
        'base_interval': 'character_table.char_002_amiya.phases[2].attributesKeyFrames[0].data.baseAttackTime',
    },
    'source_skill': source_skill,
    'source_talent': op['talents'][0]['candidates'][1],
    'base_interval_parameter_seconds': op['phases'][2]['attributesKeyFrames'][0]['data']['baseAttackTime'],
    'reused_receipts': ['research/p2-empty-enemy-scope/source-receipt.json',
                        'research/p2-empty-enemy-scope/NOTE.md',
                        'research/p2-phase-guards/source-receipt.json',
                        'research/p2-environment-and-lifecycle/source-receipt.json'],
    'reused_unknown_statement': 'research/p2-empty-enemy-scope/NOTE.md explicitly preserves finite-positive/nonempty-range continuous calculations as previous parameter references and leaves actual target/attack clocks unknown',
    'continuous_times_provenance': 'AttackTimeline.attacks generates ready+(i+1)*interval; existence of times_seconds does not establish native timing or first-hit phase',
    'native_first_hit_and_release_binding_verified': False,
    'actual_finite_positive_lifecycle_clipping_verified': False,
    'current_claims': {'estimate_complete': True, 'status': '支持范围内估算',
                       'window_damage': 11000, 'cast_damage': 35000,
                       'recharge_seconds': baseline['estimate']['skill']['recharge_seconds'],
                       'cycle_damage': 43000,
                       'scope': baseline['scope']},
    'counterexample_families': 2, 'public_calls': len(rows),
    'no_proposed_native_replacement_counts': True,
    'skill_relative_constraints_do_not_redefine_precast_initial': True,
    'baseline_head': freeze['head'], 'frozen_production_hashes': freeze['sha256'],
    'frozen_package_hashes_match_baseline': all(sha(OUT / 'frozen' / name) == expected for name, expected in freeze['sha256'].items()),
    'repo_mutations_by_this_audit': 0, 'private_state_read': False,
    'game_actions': 0, 'messages_sent': 0, 'network_requests': 0,
}
(OUT / 'source-receipt.json').write_text(json.dumps(facts, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'counterexample_families': 2, 'public_calls': len(rows),
                  'finite_positive_window_damage': 11000, 'finite_positive_cast_damage': 35000,
                  'reported_supported_estimate': True, 'repo_mutations': 0}))
