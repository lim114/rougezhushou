"""Readonly source closure for already declared Wisdel count controls."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
p = Path(__file__).resolve().parent
root = Path('/workspace/rougezhushou')
package = p/'frozen62'
freeze = json.loads((p/'freeze62.json').read_text())
head = freeze['baseline_head']
assert all(hashlib.sha256((package/rel).read_bytes()).hexdigest() == sha
           for rel, sha in freeze['public_source_hashes'].items())
sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.operator_options import OPTIONS

sources, raw = {}, {}
for name, expected in [('character_table', '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
                       ('skill_table', '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca')]:
    path = root/'.cache/p2-s1-binding'/(name+'.json')
    blob = path.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == expected
    sources[name] = {'path': str(path), 'bytes': len(blob), 'sha256': expected,
                     'actual_bytes_rehashed': True, 'new_download': False,
                     'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'}
    raw[name] = json.loads(blob)

op, token = 'char_1035_wisdel', 'token_10035_wisdel_wward'
profile = catalog()['operators'][op]
selectors = {'character_table.'+op+'.talents': raw['character_table'][op]['talents'],
             'character_table.'+token+'.phases': raw['character_table'][token]['phases'],
             'character_table.'+token+'.skills': raw['character_table'][token]['skills'],
             'character_table.'+token+'.talents': raw['character_table'][token]['talents']}
checks = []
for number, skill in enumerate(profile['skills'], 1):
    assert raw['character_table'][op]['skills'][number-1]['skillId'] == skill['id']
    source = raw['skill_table'][skill['id']]
    selectors['skill_table.'+skill['id']+'.levels'] = source['levels']
    for rank in range(1, 11):
        values = {row['key']: row['value'] for row in source['levels'][rank-1]['blackboard']}
        assert values == skill['levels'][rank-1]['values']
        checks.append({'skill': number, 'rank': rank, 'id': skill['id'], 'blackboard_match': True})
for skill_id in {row['skillId'] for row in raw['character_table'][token]['skills']}:
    selectors['skill_table.'+skill_id+'.levels'] = raw['skill_table'][skill_id]['levels']
attribute_checks = []
mapping = {'maxHp': 'hp', 'atk': 'attack', 'def': 'defense', 'magicResistance': 'resistance',
           'attackSpeed': 'attack_speed', 'baseAttackTime': 'interval', 'blockCnt': 'block_count',
           'cost': 'deployment_cost', 'respawnTime': 'redeploy_seconds'}
for elite, phase in enumerate(profile['tokens'][token]['phases']):
    source_phase = raw['character_table'][token]['phases'][elite]
    for source, normalized in zip(source_phase['attributesKeyFrames'], phase['frames']):
        assert source['level'] == normalized['level']
        for source_key, key in mapping.items():
            assert source['data'][source_key] == normalized[key]
        attribute_checks.append({'elite': elite, 'level': normalized['level'], 'attribute_fields_checked': len(mapping)})
controls = [entry for entry in OPTIONS[op] if entry[0] in ('ghost_count', 'ghost_casts')]
assert controls == [('ghost_count', '在场魂灵之影数量', 0, 3, (1, 2, 3)),
                    ('ghost_casts', '窗口内命中当前目标的魂灵施放次数', 0, 1000, (1, 2, 3))]
app = (package/'rouge/app.py').read_text()
assert 'widget=QSpinBox();widget.setRange(0,maximum);widget.setValue(default)' in app
engine = (package/'rouge/operator_engine.py').read_text()
assert "ghosts=self.option('ghost_count',0,maximum=3,integer=True)" in engine
assert "cast_count=self.option('ghost_casts',0,maximum=1000,integer=True)" in engine
assert "if cast_count and window==0:" in engine
assert "'ghost_casts_requested':int(self.s.get('ghost_casts',0)) if self.s.get('ghost_count',0) else 0" in engine
assert "'ghost_declared_count_damage_reference':int(self.s.get('ghost_casts',0))*" in engine
receipt_names = []
for rel in ('research/p2-wisdel-ghost-clock/source-receipt.json',
            'research/p2-wisdel-ghost-clock/RESEARCH.md',
            'research/p2-wisdel-secondary/source-receipt.json',
            'research/p2-wisdel-secondary/RESEARCH.md'):
    blob = subprocess.check_output(['git', '-C', str(root), 'show', head+':'+rel])
    name = rel.replace('/', '-')
    (p/name).write_bytes(blob)
    receipt_names.append({'tracked_path': rel, 'head': head, 'copy': name,
                          'sha256': hashlib.sha256(blob).hexdigest(),
                          'historical_receipt_not_new_native_verification': True})
(p/'pinned-wisdel-selectors.json').write_text(json.dumps(selectors, ensure_ascii=False, indent=2)+'\n')
receipt = {'discovery_baseline_head': head, 'sources': sources, 'controls': controls,
           'skill_rank_checks': checks, 'token_attribute_checks': attribute_checks,
           'all_thirty_skill_blackboards_match': True, 'real_integer_controls': True,
           'query_contract': {'ghost_count': 'all three Wisdel skill plans, existing finite nonnegative integer, maximum3',
                              'ghost_casts': 'only when parsed ghost_count >0, existing finite nonnegative integer, maximum1000',
                              'zero_window_positive_casts': 'existing ValueError; preserve',
                              'other_operators': 'both fields unused; preserve',
                              'integer_raw_bool': 'section61 query guard; preserve active and inactive gates'},
           'manual_input_ranges_not_new_native_caps': True,
           'candidate': 'finisher gate uses raw ghost_count truthiness and both fields int(raw ghost_casts); legal decimal aliases fail and parsed-zero ghosts wrongly expose inactive casts',
           'reused_receipts': receipt_names, 'selectors': 'pinned-wisdel-selectors.json',
           'unknowns_preserved': ['actual independent cast times', 'random SP regeneration schedule',
                                  'full cast/recharge attribution', 'secondary shadow lifecycle',
                                  'random independence', 'native/current hotfix attachment'],
           'production_edits': 0, 'patch_written': False, 'private_state_read': False,
           'native_validation': False, 'new_game_mechanism': False}
(p/'source-closure.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'baseline_head': head, 'skill_ranks_checked': len(checks),
                  'token_frames_checked': len(attribute_checks), 'sourceclosure': True,
                  'production_edits': 0}))
