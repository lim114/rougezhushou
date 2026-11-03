"""Verify medical-form base and exact three INC-X ratio data-only replacements."""
import hashlib,json,sys
from pathlib import Path

checkout=Path(sys.argv[1])
out=Path(__file__).parent
originals=Path('/workspace/.continuation/p2-after-070-source-audit/originals')
paths={
    'char_patch_table':(out/'char_patch_table.json','d1850d5aeec1a9246a0531e88c167e66745644957662c8272fc764f54904c57e'),
    'battle_equip_table':(originals/'battle_equip_table.json','006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
    'uniequip_table':(originals/'uniequip_table.json','b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9'),
    'skill_table':(Path('/workspace/rougezhushou/.cache/p2-s1-binding/skill_table.json'),'86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca')}
tables={};receipts={}
for name,(path,expected) in paths.items():
    data=path.read_bytes();sha=hashlib.sha256(data).hexdigest();assert sha==expected,(name,sha)
    tables[name]=json.loads(data);receipts[name]={'path':str(path),'sha256':sha,'bytes':len(data)}
cat=json.loads((checkout/'rouge/data/catalog.json').read_text())['operators']['char_1037_amiya3']
raw=tables['char_patch_table']['patchChars']['char_1037_amiya3']
assert raw['profession']=='MEDIC' and raw['subProfessionId']=='incantationmedic'
assert 'char_1037_amiya3' in tables['char_patch_table']['infos']['char_002_amiya']['tmplIds']
assert raw['trait']==cat['trait'] and len(raw['trait']['candidates'])==1
base=raw['trait']['candidates'][0]
assert base['unlockCondition']=={'phase':'PHASE_0','level':1} and base['requiredPotentialRank']==0
assert base['blackboard']==[{'key':'scale','value':.5,'valueStr':None}]
uni=tables['uniequip_table']['equipDict']['uniequip_002_amiya3']
module=cat['modules'][0]
assert len(cat['modules'])==1 and module['id']=='uniequip_002_amiya3' and module['type']=='INC-X'
assert uni['charId']=='char_002_amiya' and uni['tmplId']==cat['id']
assert uni['unlockEvolvePhase']=='PHASE_2' and uni['unlockLevel']==50
assert module['unlock_elite']==2 and module['unlock_level']==50
battle=tables['battle_equip_table']['uniequip_002_amiya3']
assert len(battle['phases'])==len(module['levels'])==3
for i,phase in enumerate(battle['phases']):
    normalized=module['levels'][i]
    assert phase['equipLevel']==normalized['level']==i+1 and normalized['parts']==phase['parts']
    assert normalized['attributes']=={b['key']:b['value'] for b in phase['attributeBlackboard']}
    parts=[p for p in phase['parts'] if p['target']=='TRAIT_DATA_ONLY'];assert len(parts)==1
    part=parts[0]
    assert part['isToken'] is False and part['resKey'] is None
    assert part['validInGameTag'] is None and part['validInMapTag'] is None
    candidates=part['overrideTraitDataBundle']['candidates'];assert len(candidates)==1
    candidate=candidates[0]
    assert candidate['unlockCondition']=={'phase':'PHASE_2','level':50} and candidate['requiredPotentialRank']==0
    assert candidate['overrideDescripton']==base['overrideDescripton']
    assert candidate['blackboard']==[{'key':'scale','value':.6,'valueStr':None}]
    assert candidate['prefabKey'] is None and candidate['rangeId'] is None and candidate['additionalDescription'] is None
ranks=0
for skill,original in zip(cat['skills'],raw['skills'],strict=True):
    assert skill['id']==original['skillId']
    levels=tables['skill_table'][original['skillId']]['levels']
    for level,original_level in zip(skill['levels'],levels,strict=True):
        assert level['values']=={entry['key']:entry['value'] for entry in original_level['blackboard']}
        assert level['description']==original_level['description'];ranks+=1
assert ranks==20
print(json.dumps({'passed':True,'source_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
                  'files':receipts,'medical_form_exact':True,'base_ratio':.5,'module_ratio':.6,
                  'same_trait_description':True,'three_complete_parts_and_attributes_exact':True,
                  'module_gate':'PHASE_2 level50 P1','skill_rank_records':ranks,
                  'native_attachment_chain_or_clock_verified':False},ensure_ascii=False))
