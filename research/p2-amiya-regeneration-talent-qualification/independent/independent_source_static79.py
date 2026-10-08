"""Review actual pinned medical form originals and frozen two-line source."""
import hashlib
import json
from pathlib import Path

REVIEW = Path(__file__).resolve().parent
AUTHOR = REVIEW.with_name('p2-amiya-regeneration-talent-qualification-079')
BASE = Path(json.loads((AUTHOR / 'baseline-path.json').read_text())['source_path'])
DRAFT = AUTHOR / 'draft'
freeze = json.loads((AUTHOR / 'freeze-receipt.json').read_text())
hashes = {}
for rel, expected in freeze['frozen_source_files'].items():
    raw = (BASE / rel).read_bytes()
    assert len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['sha256'], rel
    if rel != 'rouge/operator_engine.py':
        assert (DRAFT / rel).read_bytes() == raw, rel
old = (BASE / 'rouge/operator_engine.py').read_bytes()
new = (DRAFT / 'rouge/operator_engine.py').read_bytes()
before = b"                emit('\xe8\xaf\x9a\xe6\x8c\x9a\xe6\x9c\x9f\xe8\xae\xb8\xe6\x9c\xac\xe4\xbd\x93\xe7\x94\x9f\xe5\x91\xbd\xe5\x9b\x9e\xe5\xa4\x8d',self.stats['hp']*self.talent('\xe8\xaf\x9a\xe6\x8c\x9a\xe6\x9c\x9f\xe8\xae\xb8','hp_recovery_per_sec_by_max_hp_ratio'),\r\n                     'regeneration',duration)"
after = "                regeneration_seconds=duration if '诚挚期许' in self.tv else 0.0\r\n".encode() + before.replace(b"'regeneration',duration)", b"'regeneration',regeneration_seconds)")
assert old.count(before) == 1 and old.replace(before, after) == new
assert b'\n' not in new.replace(b'\r\n', b'')
source = json.loads((AUTHOR / 'source-receipt79.json').read_text())
originals = {}
for name, meta in source['actual_original_sources'].items():
    p = Path(meta['source_path'])
    raw = p.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == meta['sha256'] and len(raw) == meta['bytes']
    originals[name] = json.loads(raw)
    hashes[str(p)] = {'sha256': meta['sha256'], 'bytes': len(raw)}
patch = originals['char_patch_table']
assert 'char_1037_amiya3' in patch['infos']['char_002_amiya']['tmplIds']
form = patch['patchChars']['char_1037_amiya3']
assert form['profession'] == 'MEDIC' and form['subProfessionId'] == 'incantationmedic'
assert patch['patchDetailInfoList']['char_1037_amiya3']['infoParam'] == '医疗'
catalog = json.loads((DRAFT / 'rouge/data/catalog.json').read_text())['operators']['char_1037_amiya3']
assert catalog['profession'] == 'medic' and catalog['subprofession_id'] == form['subProfessionId']
for group, actual in zip(form['talents'], catalog['talents']):
    expected = [{'phase': int(c['unlockCondition']['phase'].split('_')[1]),
                 'level': c['unlockCondition']['level'], 'potential_rank': c['requiredPotentialRank'],
                 'name': c['name'], 'description': c['description'],
                 'values': {x['key']: x['value'] for x in c['blackboard']}} for c in group['candidates']]
    assert expected == actual
assert len(form['talents']) == 1
assert [(c['unlockCondition']['phase'], c['unlockCondition']['level'])
        for c in form['talents'][0]['candidates']] == [('PHASE_1', 1), ('PHASE_2', 1)]
assert [c['blackboard'][1]['value'] for c in form['talents'][0]['candidates']] == [.015, .025]
levels = 0
for binding, skill in zip(form['skills'], catalog['skills']):
    assert binding['skillId'] == skill['id']
    original = originals['skill_table'][skill['id']]
    assert len(skill['levels']) == len(original['levels']) == 10
    for rawlevel, level in zip(original['levels'], skill['levels']):
        assert level['values'] == {x['key']: x['value'] for x in rawlevel['blackboard']}
        for key in ('name', 'duration', 'description'):
            assert level[key] == rawlevel[key]
        levels += 1
uni = originals['uniequip_table']
assert 'uniequip_002_amiya3' in uni['charEquip']['char_1037_amiya3']
meta = uni['equipDict']['uniequip_002_amiya3']
assert meta['charId'] == 'char_002_amiya' and meta['tmplId'] == 'char_1037_amiya3'
assert meta['unlockEvolvePhase'] == 'PHASE_2' and meta['unlockLevel'] == 50
assert source['all_three_module_complete_records'] == originals['battle_equip_table']['uniequip_002_amiya3']
receipt = {'status': 'PASS', 'baseline_commit': freeze['baseline_commit'],
           'baseline_files_hash_verified': len(freeze['frozen_source_files']),
           'old_draft_files_unchanged': len(freeze['frozen_source_files']) - 1,
           'only_exact_two_line_engine_change_CRLF_preserved': True,
           'exact_raw_medical_form_no_base_name_fallback': True,
           'talent_gate_E1L1_E2L1': True, 'exact_original_skill_levels': levels,
           'module_exact_baseChar_plus_medicalTmpl_E2L50_three_parts': True,
           'actual_original_hashes': hashes, 'calculation_GUI_Wine_native_calls': 0,
           'HP0_unavailable_no_fabricated_verified_rule': True}
(REVIEW / 'independent-source-static79.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in receipt.items() if k != 'actual_original_hashes'}))
