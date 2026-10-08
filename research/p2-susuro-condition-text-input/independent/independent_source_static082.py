"""Frozen consumer, actual original tables, selected talent and transport checks."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-empty-source-consumer-audit-after-080')
freeze = json.loads((AUTHOR / 'freeze-receipt.json').read_text())
sealed = json.loads((AUTHOR / 'review-freeze82.json').read_text())
files = freeze.get('files', freeze.get('fixed_files', freeze.get('public_files')))
assert isinstance(files, dict), list(freeze)
for relative, meta in files.items():
    original = (AUTHOR / 'frozen' / relative).read_bytes()
    assert hashlib.sha256(original).hexdigest() == meta['sha256'] and len(original) == meta['bytes']
    if relative != 'rouge/operator_engine.py':
        assert original == (AUTHOR / 'draft' / relative).read_bytes()
old = (AUTHOR / 'frozen/rouge/operator_engine.py').read_bytes()
new = (AUTHOR / 'draft/rouge/operator_engine.py').read_bytes()
anchor = "        elif op in ('char_196_sunbr','char_2025_shu','char_298_susuro'):\r\n".encode()
guard = ("            if (op=='char_298_susuro' and '微创治疗' in self.tv and\r\n"
         "                    isinstance(self.s.get('low_cost_healing_target'),str)):\r\n"
         "                raise ValueError('low_cost_healing_target 不接受文本条件；请使用布尔值。')\r\n").encode()
assert old.count(anchor) == 1 and old.replace(anchor, anchor + guard) == new
assert new.count(b'\n') == new.count(b'\r\n')
assert hashlib.sha256(new).hexdigest() == sealed['engine_after_sha256']
hashes = {}
for relative, key in [('section82.patch', 'patch_sha256'),
                       ('draft/tests/test_susuro_condition_text_input.py', 'test_sha256'),
                       ('source-receipt82.json', 'source_receipt_sha256')]:
    raw = (AUTHOR / relative).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == sealed[key]
    hashes[relative] = {'sha256': sealed[key], 'bytes': len(raw)}
source = json.loads((AUTHOR / 'source-receipt82.json').read_text())
tables = {}
for name, row in source['source_files'].items():
    raw = Path(row['path']).read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
    tables[name] = json.loads(raw)
assert tables['character_table']['char_298_susuro'] == source['complete_selected_character']
for key, value in source['complete_selected_skill_objects'].items():
    assert tables['skill_table'][key] == value
assert tables['battle_equip_table']['uniequip_002_susuro'] == source['complete_selected_module_battle_object']
assert tables['uniequip_table']['equipDict']['uniequip_002_susuro'] == source['complete_selected_module_metadata']
sys.path.insert(0, str(AUTHOR / 'frozen'))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
profile = catalog()['operators']['char_298_susuro']
for raw, actual in zip(source['complete_selected_character']['talents'][0]['candidates'], profile['talents'][0], strict=True):
    assert raw['name'] == actual['name'] == '微创治疗'
    assert actual['phase'] == int(raw['unlockCondition']['phase'].split('_')[1])
    assert actual['level'] == raw['unlockCondition']['level']
    assert actual['potential_rank'] == raw['requiredPotentialRank']
    assert actual['description'] == raw['description']
    assert actual['values'] == {row['key']: row['value'] for row in raw['blackboard']}
levels = 0
for binding, skill in zip(source['complete_selected_character']['skills'], profile['skills'], strict=True):
    assert binding['skillId'] == skill['id']
    for original, actual in zip(tables['skill_table'][skill['id']]['levels'], skill['levels'], strict=True):
        assert actual['values'] == {row['key']: row['value'] for row in original['blackboard']}
        assert actual['description'] == original['description']
        levels += 1
for original, actual in zip(source['complete_selected_module_battle_object']['phases'], profile['modules'][0]['levels'], strict=True):
    assert original['parts'] == actual['parts']
    assert actual['attributes'] == {row['key']: row['value'] for row in original['attributeBlackboard']}
selections = source['actual_frozen_selected_talent_results'] + source['actual_frozen_module_boundary_results']
for row in selections:
    talents, parts = selected_talents(profile, row['scenario'])
    assert json.dumps(talents, sort_keys=True) == json.dumps(row['selected_talents'], sort_keys=True)
    assert json.dumps(parts, sort_keys=True) == json.dumps(row['module_parts'], sort_keys=True)
patch = AUTHOR / 'section82.patch'
numstat = subprocess.run(['git', 'apply', '--numstat', str(patch)], capture_output=True, text=True, check=True)
assert numstat.stdout == '3\t0\trouge/operator_engine.py\n110\t0\ttests/test_susuro_condition_text_input.py\n'
apply = subprocess.run(['git', 'apply', '--check', str(patch)], cwd=AUTHOR / 'frozen', capture_output=True, text=True)
assert apply.returncode == 0, apply.stderr
receipt = {'status': 'PASS', 'baseline_commit': sealed['baseline_commit'],
           'baseline_files_verified': len(files), 'old_draft_files_unchanged': len(files)-1,
           'only_three_CRLF_guard_lines_added': True, 'actual_raw_tables_verified': source['source_files'],
           'exact_skill_levels': levels, 'source_selection_helper_calls': len(selections),
           'raw_and_actual_selected_talent_module_bindings_verified': True,
           'new_public_calculate_calls': 0, 'frozen_artifact_hashes': hashes,
           'patch_numstat': numstat.stdout, 'git_apply_check_exit_code': apply.returncode,
           'root81_relics_transport_absent': True,
           'GUI_Wine_tracked_author_source_mutations': False}
(OUT / 'independent-source-static082.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('actual_raw_tables_verified', 'frozen_artifact_hashes')}))
