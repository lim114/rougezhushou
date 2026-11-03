"""Readonly Shu S3 condition source and producer closure."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
p = Path(__file__).resolve().parent
root = Path('/workspace/rougezhushou')
package = p/'frozen64'
freeze = json.loads((p/'freeze64.json').read_text())
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
op = 'char_2025_shu'
skill = catalog()['operators'][op]['skills'][2]
entry = raw['character_table'][op]['skills'][2]
assert entry['skillId'] == skill['id'] == 'skchr_shu_3'
assert entry['unlockCond'] == {'phase': 'PHASE_2', 'level': 1}
assert skill['unlock_elite'] == 2
checks = []
levels = raw['skill_table'][skill['id']]['levels']
for rank in range(1, 11):
    original = levels[rank-1]
    values = {row['key']: row['value'] for row in original['blackboard']}
    assert values == skill['levels'][rank-1]['values']
    assert '有地面敌人处于播种地块时技能范围内的我方单位' in original['description']
    checks.append({'rank': rank, 'blackboard_match': True, 'e_atk': values['e_atk'],
                   'e_attack_speed': values['e_attack_speed'], 'description': original['description']})
control = next(row for row in OPTIONS[op] if row[0] == 'enemy_on_sown_tile')
assert control == ('enemy_on_sown_tile', '敌人在播种地块', False, 1, (3,))
app = (package/'rouge/app.py').read_text()
assert 'widget=QCheckBox(label);widget.setChecked(default)' in app
assert 'scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()' in app
assert "choices=[i+1 for i,s in enumerate(profile['skills']) if s.get('unlock_elite',i)<=elite]" in app
damage = (package/'rouge/damage.py').read_text()
assert "if profile['skills'][skill-1].get('unlock_elite',skill-1)>elite or (elite<2 and rank>7):" in damage
engine = (package/'rouge/operator_engine.py').read_text()
nodes = [node for node in ast.walk(ast.parse(engine)) if isinstance(node, ast.Call)
         and isinstance(node.func, ast.Attribute) and node.func.attr == 'get'
         and node.args and isinstance(node.args[0], ast.Constant)
         and node.args[0].value == 'enemy_on_sown_tile']
assert len(nodes) == 1
selector = {'character_table.char_2025_shu.skills[2]': entry,
            'skill_table.skchr_shu_3.levels': levels}
(p/'pinned-s3-selectors.json').write_text(json.dumps(selector, ensure_ascii=False, indent=2)+'\n')
prior = 'research/p2-shu-periodic-sp-reference/source-receipt060.json'
blob = subprocess.check_output(['git', '-C', str(root), 'show', head+':'+prior])
(p/'reused-periodic-sp-source-receipt.json').write_bytes(blob)
receipt = {'discovery_baseline_head': head, 'sources': sources,
           'exact_ground_enemy_condition': levels[9]['description'],
           'ten_skill_rank_checks': checks, 'control': control,
           'actual_gate': 'qualified Shu S3 non-normal plan else branch; normal plan/S1/S2/other owner do not read this field',
           'actual_raw_read': {'file': 'rouge/operator_engine.py', 'line': nodes[0].lineno,
                               'source': ast.get_source_segment(engine, nodes[0])},
           'qualification': {'raw_skill_unlock': entry['unlockCond'], 'normalized_unlock_elite': skill['unlock_elite'],
                             'api_skill_unlock_check_precedes_engine': True,
                             'qt_skill_choices_filter_unlock_elite': True,
                             'not_inferred_from_talent_four_sui_gate': True},
           'qt_producer': {'true_checkbox': True, 'default': False, 'applicable_skills': [3],
                           'scenario_value_source': 'widget.isChecked()', 'producer_type': 'bool',
                           'no_current_state_read_or_ui_executed': True},
           'narrow_suggestion': 'Reject only string values at the already queried Shu non-normal S3 branch before raw truthiness; keep bool, number0/1, null and existing nonstring contracts. Preserve unlocked-skill validation priority and inactive fields.',
           'window_gate': 'S3 branch reads the condition even if observation/target lifetime is zero; do not infer actual ground coverage or event timing from either boundary',
           'periodic_source_reuse': {'path': prior, 'head': head, 'sha256': hashlib.sha256(blob).hexdigest(),
                                    'historical_qualified_reuse_not_new_native_proof': True},
           'unknowns_preserved': ['actual ground enemy presence', 'actual sown tile placement/coverage',
                                  'conditional buff attachment/times', 'teleport events',
                                  'four_sui periodic first pulse, origin/reset, blocked credit',
                                  'native/current hotfix attachment'],
           'scope_exclusions': ['three_professions/three_same_profession belongs to68', 'cooperative belongs to69'],
           'production_edits': 0, 'patch_written': False, 'private_state_read': False,
           'native_validation': False, 'new_game_mechanism': False}
(p/'source-closure.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'baseline_head': head, 'skill_ranks_checked': 10,
                  'only_raw_field_read_line': nodes[0].lineno, 'sourceclosure': True,
                  'production_edits': 0}))
