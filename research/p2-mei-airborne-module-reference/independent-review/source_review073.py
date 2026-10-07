"""Read-only independent source closure; no gameplay formula inference."""
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).parent
AUTHOR = Path('/workspace/.continuation/p2-mei-airborne-module-reference-073')
receipt = json.loads((AUTHOR / 'source-receipt.json').read_text())
BASE = Path(json.loads((AUTHOR / 'baseline-path.json').read_text())['path'])
expected = {
    'character_table': '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697',
    'battle_equip_table': '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460',
    'uniequip_table': 'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9',
}
raw = {}
for key, digest in expected.items():
    row = receipt['source_files'][key]
    data = Path(row['path']).read_bytes()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'] == digest
    raw[key] = json.loads(data)
assert receipt['baseline_commit'] == '552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9'
for name in ('rouge/data/catalog.json','rouge/operator_engine.py','rouge/reporting.py'):
    git = subprocess.check_output(['git','-C','/workspace/rougezhushou','show',receipt['baseline_commit']+':'+name])
    assert git == (BASE / name).read_bytes()
catalog = json.loads((BASE / 'rouge/data/catalog.json').read_text())
owner = catalog['operators']['char_133_mm']
module = next(m for m in owner['modules'] if m['id'] == 'uniequip_002_mm')
meta = raw['uniequip_table']['equipDict']['uniequip_002_mm']
assert 'uniequip_002_mm' in raw['uniequip_table']['charEquip']['char_133_mm']
assert meta == receipt['exact_owner_binding']['metadata_record']
assert meta['charId'] == 'char_133_mm' and meta['typeName1'] == 'MAR' and meta['typeName2'] == 'X'
assert meta['unlockEvolvePhase'] == 'PHASE_2' and meta['unlockLevel'] == 40
assert module['unlock_elite'] == 2 and module['unlock_level'] == 40
assert module['name'] == meta['uniEquipName']
assert raw['character_table']['char_133_mm']['name'] == owner['name'] == '梅'
phases = raw['battle_equip_table']['uniequip_002_mm']['phases']
assert len(phases) == len(module['levels']) == len(receipt['all_three_module_records']) == 3
selectors = []
for index, phase in enumerate(phases):
    assert phase == receipt['all_three_module_records'][index]['record']
    level = module['levels'][index]
    assert level['parts'] == phase['parts']
    assert level['attributes'] == {row['key']:row['value'] for row in phase['attributeBlackboard']}
    assert level['level'] == phase['equipLevel'] == index + 1
    trait = phase['parts'][0]
    assert trait['target'] == 'TRAIT' and trait['isToken'] is False
    assert trait['validInGameTag'] is None and trait['validInMapTag'] is None
    candidates = trait['overrideTraitDataBundle']['candidates']
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate['unlockCondition'] == {'phase':'PHASE_2','level':40}
    assert candidate['requiredPotentialRank'] == 0
    assert candidate['additionalDescription'] == '攻击空中单位时攻击力提升至<@ba.kw>{atk_scale:0%}</>'
    assert candidate['blackboard'] == [{'key':'atk_scale','value':1.1,'valueStr':None}]
    selectors.append('battle_equip_table.uniequip_002_mm.phases['+str(index)+'].parts[0].overrideTraitDataBundle.candidates[0]')
search = receipt['native_evidence_search']
assert len(search['files']) == 199
assert search['exact_matches'] == []
for name, record in search['files'].items():
    data = Path(name).read_bytes()
    assert len(data) == record['bytes'] and hashlib.sha256(data).hexdigest() == record['sha256']
    hits = [needle for needle in search['needles'] if needle in data.decode(errors='replace')]
    assert hits == record['matching_needles'] == []

out = {
    'status':'source_and_static_design_passed_final_patch_pending',
    'baseline_commit':receipt['baseline_commit'],'game_commit':receipt['game_commit'],
    'raw_source_sha256':expected,'exact_module_levels':3,'exact_owner':'char_133_mm',
    'exact_qualification':{'elite':2,'level':40,'potential_rank':0},
    'original_conditional_parameter':1.1,'source_selectors':selectors,
    'full_module_parts_and_attributes_match':True,'existing_baseline_files_equal_committed_git_blobs':3,
    'retained_native_texts_rehashed_and_exact_id_searched':199,
    'native_search_scope':'Only retained cache text exports; not the complete game installation.',
    'static_design':'Qualified source-only reference after existing numeric calculation, and a report section. No checkbox, multiplier, target inference, complete/scope/clock mutation is authorized.',
    'unknowns':['Actual target airborne state','Native module attachment','Damage composition layer','Actual conditional damage'],
    'no_tracked_edits':True,'no_private_state_reads':True,'no_wine_or_gui':True,
}
path = OUT / 'source-review073.json'
path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':out['status'],'receipt_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
