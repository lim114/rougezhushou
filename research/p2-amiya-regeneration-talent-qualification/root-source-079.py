import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from rouge.catalog import catalog
from rouge.operator_options import OPTIONS

inputs={
 'char_patch_table':('/workspace/.continuation/p2-amiya-regeneration-talent-qualification-079/char_patch_table.json','d1850d5aeec1a9246a0531e88c167e66745644957662c8272fc764f54904c57e'),
 'skill_table':('.cache/p2-s1-binding/skill_table.json','86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'),
 'battle_equip_table':('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json','006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
 'uniequip_table':('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json','b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9')}
tables={};proof={}
for key,(path,digest) in inputs.items():
 b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==digest;tables[key]=json.loads(b);proof[key]={'sha256':digest,'bytes':len(b)}
op='char_1037_amiya3';patch=tables['char_patch_table'];original=patch['patchChars'][op];p=catalog()['operators'][op]
assert op in patch['infos']['char_002_amiya']['tmplIds']
assert patch['patchDetailInfoList'][op]['patchId']==op and patch['patchDetailInfoList'][op]['infoParam']=='医疗'
assert original['profession']=='MEDIC' and original['subProfessionId']==p['subprofession_id']=='incantationmedic'
assert p['trait']==original['trait']
phase={'PHASE_0':0,'PHASE_1':1,'PHASE_2':2};skills=0;talents=0
for current,native in zip(p['skills'],original['skills'],strict=True):
 assert current['id']==native['skillId'] and current['unlock_elite']==phase[native['unlockCond']['phase']]
 for rank,raw in zip(current['levels'],tables['skill_table'][current['id']]['levels'],strict=True):
  assert rank['description']==raw['description'] and rank['values']=={b['key']:b['value'] for b in raw['blackboard']};skills+=1
for group,native in zip(p['talents'],original['talents'],strict=True):
 for current,raw in zip(group,native['candidates'],strict=True):
  assert current=={'phase':phase[raw['unlockCondition']['phase']],'level':raw['unlockCondition']['level'],'potential_rank':raw['requiredPotentialRank'],'name':raw['name'],'description':raw['description'],'values':{b['key']:b['value'] for b in raw['blackboard']}};talents+=1
module=p['modules'][0];mid='uniequip_002_amiya3';assert module['id']==mid
meta=tables['uniequip_table']['equipDict'][mid]
assert (meta['charId'],meta['tmplId'],meta['unlockEvolvePhase'],meta['unlockLevel'])==('char_002_amiya',op,'PHASE_2',50)
assert mid in tables['uniequip_table']['charEquip'][op]
assert (module['unlock_elite'],module['unlock_level'])==(2,50)
for current,raw in zip(module['levels'],tables['battle_equip_table'][mid]['phases'],strict=True):
 assert current['parts']==raw['parts'] and current['attributes']=={b['key']:b['value'] for b in raw['attributeBlackboard']}
print(json.dumps({'section':79,'passed':True,'original_source_selector':'char_patch_table.patchChars.'+op,'form_ownership_selector':'char_patch_table.infos.char_002_amiya.tmplIds','exact_medical_form':True,'raw_hashes':proof,'skill_ranks_verified':skills,'talent_selectors_verified':talents,'complete_module_levels_verified':len(module['levels']),'controls':OPTIONS.get(op,[]),'account_unlock_and_native_clock_validation':False},ensure_ascii=False))
