"""Reproduce bounded damage type fields, vtables, constants and literal keys."""
from pathlib import Path
import hashlib,json,struct
OUT=Path(__file__).resolve().parent
reader=OUT.parent/'p1-native-runtime-054/read_metadata_static.py'
scope={'__file__':str(reader),'__name__':'_bounded_metadata'}
exec(compile(reader.read_text(encoding='utf-8').split('selected=[]\n')[0],str(reader),'exec'),scope)
wanted={
 'Torappu.Battle.Abilities.AbstractAnimatedAbility',
 'Torappu.Battle.Abilities.EasyToStartAbility',
 'Torappu.Battle.Abilities.MultiMeleeAttack',
 'Torappu.Battle.Abilities.MeleeAttack',
 'Torappu.Battle.Abilities.AbstractBasicAttack',
 'Torappu.Battle.Action.ActionNode',
 'Torappu.Battle.Action.Nodes+ApplyDamage',
 'Torappu.Battle.Action.Nodes+ApplyElementDamage',
 'Torappu.Battle.DamageType',
 'Torappu.Battle.ElementType',
 'Torappu.Battle.AbilityStandard+Event',
 'Torappu.Battle.UnitDataFlowConfig',
 'Torappu.Battle.Action.Nodes+AlwaysNext',
 'Torappu.Battle.BasicSkill',
 'Torappu.Battle.ReplacementSkillFixed',
 'Torappu.Battle.Character',
 'Torappu.Battle.Ability',
 'Torappu.Battle.Action.Nodes+UpdateAttackElementDamageScale',
 'Torappu.Battle.Action.Nodes+EpDamageScale',
 'Torappu.Battle.Modifier',
 'Torappu.Battle.BattleFormula',
 'Torappu.Battle.Entity',
 'Torappu.Battle.Buff',
 'Torappu.Battle.Enemy',
}
selected=[]
for ti,td in enumerate(scope['types']):
 name=scope['type_def_name'](ti)
 if name not in wanted and not ('UnitDataFlowConfig+' in name or 'Battle.Action' in name and any(q in name for q in ['DamageViaAttr','DamageApplyConfig','ElementDamage','AttackType','DamageType'])):continue
 pointer=scope['reg']['fields'][ti]
 offsets=struct.unpack_from('<'+str(td[18])+'i',scope['binary'],scope['offset'](pointer)) if pointer and td[18] else []
 fs=[{'name':scope['string'](scope['fields'][fi][0]),'type':scope['typename'](scope['fields'][fi][1]),'offset':offsets[j] if offsets else None,'default':scope['default_value'](fi)} for j,fi in enumerate(range(td[8],td[8]+td[18]))]
 slots=[]
 for slot in range(td[21]):
  enc=scope['vtable'][td[14]+slot][0];kind=enc>>29;index=(enc&0x1ffffffe)>>1
  row={'slot':slot,'usage_type':kind,'decoded_index':index}
  if kind==3 and index<len(scope['methods']):
   m=scope['methods'][index];row['method']=scope['type_def_name'](m[1])+'$$'+scope['string'](m[0])
  slots.append(row)
 ms=[]
 for mi in range(td[9],td[9]+td[16]):
  m=scope['methods'][mi];ms.append({'name':scope['string'](m[0]),'method_index':mi,'slot':m[8],'parameter_count':m[9]})
 selected.append({'name':name,'type_index':ti,'parent':scope['typename'](td[4]) if td[4]>=0 else None,'fields':fs,'methods':ms,'vtable':slots})
assert wanted<={row['name'] for row in selected}, wanted-{row['name'] for row in selected}
literal_records=scope['records']('stringLiteral','II');refs=[]
for cfg in sorted(OUT.glob('*-cfg.json')):
 for method in json.loads(cfg.read_text(encoding='utf-8'))['methods']:
  for ins in method['instructions']:
   for ref in ins.get('rip_data',[]):
    enc=ref['uint32'];kind=enc>>29;idx=(enc&0x1ffffffe)>>1
    row={'cfg':cfg.name,'method':method['method']['Name'],'instruction':ins['address'],'reference_address':ref['address'],'usage_type':kind,'index':idx}
    if kind==5 and idx<len(literal_records):
     size,index=literal_records[idx];start=scope['header']['stringLiteralData'][0]+index
     row['literal']=scope['meta'][start:start+size].decode('utf-8')
    elif kind==1 and idx<len(scope['native_types']):row['type']=scope['typename'](idx)
    else:continue
    refs.append(row)
result={'source_metadata_sha256':hashlib.sha256(scope['meta']).hexdigest(),'source_game_dll_sha256':hashlib.sha256(scope['binary']).hexdigest(),'selected':selected,'encoded_references':refs,'dll_executed':False,'process_memory_read':False}
(OUT/'metadata.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'types':len(selected),'encoded_references':len(refs)},ensure_ascii=False))
