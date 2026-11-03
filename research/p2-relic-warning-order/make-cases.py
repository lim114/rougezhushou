import json
from pathlib import Path

OUT = Path(__file__).parent
ROSE, CROWN, MEAL = ('rogue_6_relic_legacy_' + str(n) for n in (81, 82, 83))
cases = []

def add(label, operator='char_1037_amiya3', skill=1, **values):
    cases.append({'label': label, 'scenario': {'operator': operator, 'skill': skill,
                 'base_attack': 1000, 'window_seconds': 10, **values}})

for mode in ('frames', 'continuous'):
    for skill in (1, 2):
        for module in (1, 2, 3):
            add(f'80-reproduction-{mode}-S{skill}-M{module}', skill=skill, elite=2,
                level=50, skill_rank=10, timing_mode=mode,
                module_id='uniequip_002_amiya3', module_level=module, relic_ids=[ROSE, CROWN])
add('empty-relic-list', relic_ids=[])
add('single-rose', relic_ids=[ROSE])
add('single-crown', relic_ids=[CROWN])
add('single-duplicate', relic_ids=[ROSE, ROSE])
add('pair-duplicates', relic_ids=[ROSE, CROWN, ROSE, CROWN])
add('pair-reversed', relic_ids=[CROWN, ROSE])
add('three-relics', relic_ids=[ROSE, CROWN, MEAL])
add('zero-window-unknown-held', window_seconds=0, relic_ids=[ROSE, CROWN])
add('empty-targets-unknown-held', timing={'target_windows': []}, relic_ids=[ROSE, CROWN])
add('unlocked-talent-unknown-held', elite=0, level=1, skill_rank=1, relic_ids=[ROSE, CROWN])
for operator, skill in [('char_110_deepcl', 2), ('kaltsit', 2), ('mechanist', 3), ('char_328_cammou', 2)]:
    add('rules-effects-token-' + operator, operator=operator, skill=skill,
        relic_ids=[ROSE, CROWN, 'rogue_6_relic_legacy_5'],
        effects=[{'kind': 'attack_pct', 'value': .1}])
add('unknown-prefix-untouched', relic_ids=['unknown_relic_for_order_test', ROSE, CROWN])
add('single-conflict-group', operator='mechanist', skill=3,
    relic_ids=['rogue_6_relic_legacy_61', 'rogue_6_relic_legacy_62'])
add('three-conflict-groups', operator='mechanist', skill=3,
    relic_ids=['rogue_6_relic_legacy_61', 'rogue_6_relic_legacy_62', ROSE, CROWN])
add('effects-conflict-group', operator='mechanist', skill=3,
    relic_ids=[ROSE, CROWN, 'rogue_6_relic_legacy_104', 'rogue_6_relic_fight_21'])
add('inapplicable-scope', operator='char_110_deepcl', skill=2, relic_ids=['rogue_6_relic_legacy_80'])
add('old-error-negative-window', window_seconds=-1, relic_ids=[ROSE, CROWN])
add('old-error-fractional-recipients', healing_targets=1.5, relic_ids=[ROSE, CROWN])
add('old-error-invalid-bound', char_buff_ids='not-a-list', relic_ids=[ROSE, CROWN])
add('old-error-invalid-context', operator='mechanist', skill=3,
    relic_ids=['rogue_6_relic_legacy_24'], relic_context='not-a-dict')
assert len({json.dumps(c['scenario'], sort_keys=True) for c in cases}) == len(cases)
with (OUT / 'public-cases.json').open('x', encoding='utf-8') as f:
    json.dump(cases, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'cases': len(cases)}))
