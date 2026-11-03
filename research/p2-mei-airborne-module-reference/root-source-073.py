import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from rouge.catalog import catalog
r=json.loads(Path('/workspace/.continuation/p2-mei-airborne-module-reference-073/source-receipt.json').read_text());raw={}
for name,source in r['source_files'].items():
 b=Path(source['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==source['sha256'] and len(b)==source['bytes'];raw[name]=json.loads(b)
module_id='uniequip_002_mm';owner='char_133_mm';metadata=raw['uniequip_table']['equipDict'][module_id];assert metadata['charId']==owner and module_id in raw['uniequip_table']['charEquip'][owner]
p=catalog()['operators'][owner];m=next(m for m in p['modules'] if m['id']==module_id)
assert m['unlock_elite']==2 and m['unlock_level']==metadata['unlockLevel']==40
strict=lambda obj:json.dumps(obj,sort_keys=True,separators=(',',':'))
for normalized,original in zip(m['levels'],raw['battle_equip_table'][module_id]['phases']):
 assert strict(normalized['parts'])==strict(original['parts'])
 assert strict(normalized['attributes'])==strict({row['key']:row['value'] for row in original['attributeBlackboard']})
 part=original['parts'][0];c=part['overrideTraitDataBundle']['candidates'][0]
 assert part['target']=='TRAIT' and not part['isToken'] and part['validInMapTag'] is None and part['validInGameTag'] is None
 assert c['unlockCondition']=={'phase':'PHASE_2','level':40} and c['blackboard'][0]['value']==1.1
 assert c['additionalDescription']=='攻击空中单位时攻击力提升至<@ba.kw>{atk_scale:0%}</>'
print(json.dumps({'section':73,'passed':True,'all_three_raw_sources_rehashed':True,'all_three_module_parts_attributes_strict_json_same':True,'owner_and_unlock':{'id':owner,'elite':2,'level':40},'source_condition_only':True,'trait_attachment_composition_target_unknown':True,'native_validation':False}))
