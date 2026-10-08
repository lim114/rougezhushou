"""Verify the integrated 83 source and saved evidence without API evaluation.

Usage: python root_current_source083.py [repository] [output-json]
Run against the actual clean root 83 tree, before later guards change damage.py.
"""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/workspace/rougezhushou')
DEST = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT / 'root-current-source083.json'
freeze = json.loads((OUT / 'freeze-receipt083.json').read_text())
formal = json.loads((OUT / 'formal-draft-freeze083.json').read_text())
receipt = json.loads((OUT / 'source-receipt083.json').read_text())
rows = []
for name, expected in freeze['files'].items():
    data = (REPO / name).read_bytes()
    actual = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    if name == 'rouge/damage.py':
        expected = formal['files'][name]
    assert actual == expected, (name, 'unexpected current source bytes')
    rows.append({'path': name, **actual})
name = 'tests/test_neural_condition_text_input.py'
data = (REPO / name).read_bytes()
assert {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()} == formal['files'][name]
rows.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
damage = (REPO / 'rouge/damage.py').read_bytes()
assert damage.count(b'\n') == damage.count(b'\r\n')
text = damage.decode('utf-8').replace('\r\n', '\n')
tree = ast.parse(text)
evaluate = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                and node.name == '_evaluate_damage_once')
assert isinstance(evaluate.body[-1], ast.Return)
guard = evaluate.body[-2]
assert ast.unparse(guard.test) == "scenario['operator'] in ('char_1042_phatm2', 'char_4204_mantra')"
loop = guard.body[0]
assert ast.unparse(loop.iter) == "('enemy_is_boss', 'enemy_in_neural_break')"
check = loop.body[0]
assert ast.unparse(check.test) == 'isinstance(scenario.get(field), str)'
assert isinstance(check.body[0], ast.Raise)
assert ast.unparse(evaluate.body[-3]) == "result['report'] = build_report(scenario, result)"
engine = (REPO / 'rouge/operator_engine.py').read_text()
assert "threshold=2000 if self.s.get('enemy_is_boss') else 1000" in engine
assert 'initial=self.option(\'initial_neural_buildup\',0,maximum=threshold)' in engine
assert "'preexisting_break_assumed':bool(self.s.get('enemy_in_neural_break'))" in engine
assert engine.count('self.neural(') == 3
enemy = (REPO / 'rouge/enemy_environment.py').read_text()
assert "scenario['enemy_is_boss']=record['level_type']=='BOSS'" in enemy
assert "scenario,run_resolution=prepare_run(scenario)" in text
options = (REPO / 'rouge/operator_options.py').read_text()
option_ast = ast.parse(options)
option_assignment = next(node for node in option_ast.body if isinstance(node, ast.Assign)
                         and any(isinstance(t, ast.Name) and t.id == 'OPTIONS' for t in node.targets))
option_rows = ast.literal_eval(option_assignment.value)
for owner, skills in (('char_1042_phatm2', (1, 2, 3)), ('char_4204_mantra', (1, 2))):
    selected = {row[0]: row for row in option_rows[owner]}
    for field in ('enemy_is_boss', 'enemy_in_neural_break'):
        assert selected[field][2] is False and selected[field][4] == skills
app = (REPO / 'rouge/app.py').read_text()
assert 'widget=QCheckBox(label);widget.setChecked(default)' in app
assert 'if owner==op and self.skill.currentData() in skills:' in app
assert 'scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()' in app
raw = []
for name, expected in receipt['raw_sources'].items():
    path = Path(expected['path'])
    content = path.read_bytes()
    actual = {'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
    assert actual['bytes'] == expected['bytes'] and actual['sha256'] == expected['sha256']
    raw.append({'name': name, 'path': str(path), **actual})
cat = json.loads((REPO / 'rouge/data/catalog.json').read_text())
previews = json.loads((REPO / 'rouge/data/previews.json').read_text())
targets = []
for sid, eid, level_type in (('ro6_e_1_2', 'enemy_1093_ccsbr', 'NORMAL'),
                              ('ro6_b_3', 'enemy_2143_shwksc', 'BOSS')):
    assert sid in cat['stages']
    records = [record for record in previews['stages'][sid]['possible_enemies']
               if record['id'] == eid and record['level'] == 0]
    assert len(records) == 1 and records[0]['level_type'] == level_type
    targets.append({'stage_id': sid, 'enemy_id': eid, 'level': 0,
                    'source_level_type': level_type,
                    'processed_enemy_is_boss': records[0]['level_type'] == 'BOSS',
                    'proof': 'Pinned unique target record and unchanged identity overwrite statement; no helper/API run.'})
saved = json.loads((OUT / 'saved-comparison083.json').read_text())
assert saved['passed'] and saved['saved_pairs'] == 432
assert len(saved['accepted_to_explicit_text_error']) == 116
assert len(saved['whole_record_same_accepted']) == 256 and len(saved['exact_same_olderrors']) == 60
current = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
result = {'passed': True, 'API_calls': 0, 'current_commit': current,
    'author_baseline_commit': freeze['baseline_commit'], 'verified_current_files': rows,
    'raw_originals': raw, 'selected_targets': targets,
    'same_engine_82_and_relics_81': True, 'guard_after_existing_report': True,
    'thresholds_and_clocks_changed': False, 'new_public_fields': False,
    'GUI_or_Wine_executed': False, 'saved_pairs': 432,
    'all_unchanged_records_include_JSON_and_three_text_reports': True}
DEST.parent.mkdir(parents=True, exist_ok=True)
DEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'passed': True, 'API_calls': 0, 'current_files': len(rows),
                  'raw_originals': len(raw), 'selected_targets': len(targets)}))
