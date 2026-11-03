"""Read-only independent original source and exact frozen transport review."""
import ast
import hashlib
import json
import subprocess
import sys
import textwrap
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-haruka-repeat-text-input-084')
REPO = Path('/workspace/rougezhushou')
sha = lambda value: hashlib.sha256(value).hexdigest()
sealed = json.loads((AUTHOR / 'review-freeze84.json').read_bytes())
assert sha((AUTHOR / 'review-freeze84.json').read_bytes()) == '39a94eed44a24b6add84f874e970310aaae5f9b7d7ed8f5b8d577d19ac38dd19'
freeze = json.loads((AUTHOR / 'freeze-receipt.json').read_bytes())
assert freeze['baseline_commit'] == sealed['baseline_commit'] == 'b5a40f30683bfc0945decaabbd4db5914c28427f'
assert len(freeze['files']) == 720
specs = list(freeze['files'])
batch = subprocess.run(['git', 'cat-file', '--batch'], cwd=REPO,
    input=''.join(sealed['baseline_commit'] + ':' + rel + '\n' for rel in specs).encode(),
    capture_output=True, check=True).stdout
offset = 0
unchanged = 0
for rel in specs:
    end = batch.index(b'\n', offset)
    header = batch[offset:end].split()
    assert len(header) == 3 and header[1] == b'blob', (rel, header)
    length = int(header[2]); raw = batch[end + 1:end + 1 + length]
    offset = end + 2 + length
    saved = (AUTHOR / 'frozen' / rel).read_bytes()
    assert raw == saved and sha(saved) == freeze['files'][rel]['sha256']
    assert len(saved) == freeze['files'][rel]['bytes']
    draft = (AUTHOR / 'draft' / rel).read_bytes()
    if rel != 'rouge/damage.py':
        assert draft == saved, rel
        unchanged += 1
assert offset == len(batch) and unchanged == 719
old = (AUTHOR / 'frozen/rouge/damage.py').read_bytes()
new = (AUTHOR / 'draft/rouge/damage.py').read_bytes()
guard = ("    if scenario['operator']=='char_4202_haruka' and scenario['skill']==2 and isinstance(scenario.get('haruka_repeat'),str):\r\n"
         "        raise ValueError('haruka_repeat 不接受文本条件；请使用布尔值。')\r\n").encode()
assert new.count(guard) == 1 and new.replace(guard, b'', 1) == old
assert sha(old) == sealed['damage_before_sha256'] and sha(new) == sealed['damage_after_sha256']
assert old.count(b'\n') == old.count(b'\r\n') and new.count(b'\n') == new.count(b'\r\n')
old_func = next(n for n in ast.parse(old.decode()).body if isinstance(n, ast.FunctionDef) and n.name == '_evaluate_damage_once')
new_func = next(n for n in ast.parse(new.decode()).body if isinstance(n, ast.FunctionDef) and n.name == '_evaluate_damage_once')
assert isinstance(new_func.body[-1], ast.Return)
assert ast.unparse(new_func.body[-3]) == "result['report'] = build_report(scenario, result)"
assert ast.dump(new_func.body[-2], include_attributes=False) == ast.dump(ast.parse(textwrap.dedent(guard.decode())).body[0], include_attributes=False)
new_func.body.pop(-2)
assert ast.dump(new_func, include_attributes=False) == ast.dump(old_func, include_attributes=False)
test = (AUTHOR / 'draft/tests/test_haruka_repeat_text_input.py').read_bytes()
assert test == (AUTHOR / 'test_haruka_repeat_text_input.py').read_bytes() and sha(test) == sealed['test_sha256']
methods = [n.name for n in ast.walk(ast.parse(test.decode())) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
assert len(methods) == 8
patch = (AUTHOR / 'section84.patch').read_bytes()
assert sha(patch) == sealed['patch_sha256']
stat = subprocess.check_output(['git', 'apply', '--numstat', str(AUTHOR / 'section84.patch')], cwd=REPO, text=True)
assert stat == '2\t0\trouge/damage.py\n117\t0\ttests/test_haruka_repeat_text_input.py\n'
applycheck = subprocess.run(['git', '--git-dir=' + str(REPO / '.git'), '--work-tree=' + str(AUTHOR / 'frozen'),
    'apply', '--check', str(AUTHOR / 'section84.patch')], cwd=AUTHOR / 'frozen', capture_output=True, text=True)
assert applycheck.returncode == 0, applycheck.stderr
source_raw = (AUTHOR / 'source-receipt84.json').read_bytes()
assert sha(source_raw) == sealed['source_receipt_sha256']
source = json.loads(source_raw)
tables = {}
for name, proof in source['source_files'].items():
    data = Path(proof['path']).read_bytes()
    assert sha(data) == proof['sha256'] and len(data) == proof['bytes']
    tables[name] = json.loads(data)
assert len(tables) == 4
owner = tables['character_table']['char_4202_haruka']
skill = tables['skill_table']['skchr_haruka_2']
module = tables['battle_equip_table']['uniequip_002_haruka']
meta = tables['uniequip_table']['equipDict']['uniequip_002_haruka']
assert owner == source['complete_raw_character'] and skill == source['complete_raw_s2_skill']
assert module == source['complete_raw_module'] and meta == source['complete_raw_module_meta']
assert owner['skills'][1]['skillId'] == 'skchr_haruka_2'
assert owner['skills'][1]['unlockCond'] == {'phase': 'PHASE_1', 'level': 1}
sys.path.insert(0, str(AUTHOR / 'frozen'))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
projected = catalog()['operators']['char_4202_haruka']
assert projected['skills'][1]['unlock_elite'] == 1
atks = [.15, .15, .15, .20, .20, .20, .25, .30, .35, .40]
assert len(skill['levels']) == len(source['s2_rank_bindings']) == 10
for rank, (raw, current, proof) in enumerate(zip(skill['levels'], projected['skills'][1]['levels'], source['s2_rank_bindings'], strict=True), 1):
    values = {b['key']: b['value'] for b in raw['blackboard']}
    assert proof == {'rank': rank, 'complete_raw_level': raw}
    assert values == current['values'] and raw['description'] == current['description']
    assert values['atk'] == atks[rank - 1] and values['haruka_s_2[first].atk'] == 0
    assert '第二次及以后使用时攻击力' in raw['description'] and '持续时间无限' in raw['description']
for raw_group, current_group in zip(owner['talents'], projected['talents'], strict=True):
    for raw, current in zip(raw_group['candidates'], current_group, strict=True):
        assert raw['name'] == current['name'] and raw['description'] == current['description']
        assert int(raw['unlockCondition']['phase'][-1]) == current['phase']
        assert raw['unlockCondition']['level'] == current['level']
        assert raw['requiredPotentialRank'] == current['potential_rank']
        assert {b['key']: b['value'] for b in raw['blackboard']} == current['values']
projected_module = projected['modules'][0]
assert projected_module['id'] == 'uniequip_002_haruka' and projected_module['unlock_elite'] == 2 and projected_module['unlock_level'] == 60
assert meta['charId'] == projected['id'] and meta['unlockLevel'] == 60
for raw, current in zip(module['phases'], projected_module['levels'], strict=True):
    assert raw['parts'] == current['parts'] and raw['equipLevel'] == current['level']
    assert {b['key']: b['value'] for b in raw['attributeBlackboard']} == current['attributes']
for proof in source['actual_source_helper_selections']:
    talents, parts = selected_talents(projected, proof['scenario'])
    assert talents == proof['selected_talents'] and parts == proof['module_parts']
    assert any(t['name'] == '扶摇花火' for t in talents) == (proof['scenario']['elite'] == 2)
assert len(source['actual_source_helper_selections']) == 6
engine = (AUTHOR / 'frozen/rouge/operator_engine.py').read_text()
start = engine.index("        elif op=='char_4202_haruka':")
end = engine.index('\n        elif ', start + 1)
consumer = engine[start:end]
assert consumer == source['actual_consumer']
assert engine.count("self.s.get('haruka_repeat',False)") == 1
assert "if self.n==2:\n                    repeat=self.s.get('haruka_repeat',False)" in consumer
assert "if repeat:mode='infinite';duration=window if window is not None else 30" in consumer
assert "attack=self.base*(1+self.atk_bonus+(bb['atk'] if repeat else 0))+self.atk_flat" in consumer
assert "('haruka_repeat','二技能第二次及以后开启',False,1,(2,))" in (AUTHOR / 'frozen/rouge/operator_options.py').read_text()
app = (AUTHOR / 'frozen/rouge/app.py').read_text()
assert 'widget=QCheckBox(label);widget.setChecked(default)' in app
assert 'scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()' in app
readonly_dir = OUT.with_name('p2-after-082-readonly-consumer-boundaries')
readonly_manifest = json.loads((readonly_dir / 'public-artifacts-manifest.json').read_bytes())
readonly_files = []
for proof in readonly_manifest['files']:
    path = Path(proof['source_path']); data = path.read_bytes()
    assert sha(data) == proof['sha256'] and len(data) == proof['bytes']
    readonly_files.append(proof)
assert len(readonly_files) == 4
for name in ['make-root-transport84.py', 'root-current-source-084.py']:
    helper = (AUTHOR / name).read_text()
    ast.parse(helper)
    assert 'calculate_damage(' not in helper
    if name.startswith('make'):
        assert "'--check'" in helper and '--expected-current-damage-sha' in helper
    else:
        assert '--expected-prior-damage-sha' in helper
receipt = {'status': 'PASS', 'baseline_commit': sealed['baseline_commit'],
    'frozen_git_object_files_checked': 720, 'unchanged_old_draft_files': 719,
    'exact_product_change': 'Two CRLF guard lines after completed core report, before return; E1 S2 consumer independent of E2 flower talent',
    'original_tables_rehashed': source['source_files'], 'full_original_character_skill_module_meta_equal': True,
    'actual_S2_rank_bindings': 10, 'actual_helper_selections_rechecked': 6,
    'test_method_count': 8, 'patch_numstat': stat, 'frozen_readonly_applycheck_exit': 0,
    'unknowns_retained': source['unknowns_retained'], 'readonly_boundary_four_files': readonly_files,
    'transport_helpers_ast_read_only_reviewed_not_executed': True,
    'calculate_damage_calls': 0, 'tracked_edits': False, 'GUI_Wine': False}
(OUT / 'independent-source-static084.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in receipt.items() if k not in ('original_tables_rehashed', 'readonly_boundary_four_files')}, ensure_ascii=False))
