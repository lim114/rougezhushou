"""Reproduce selected native types, slots, literals and addresses using disk only."""
from pathlib import Path
import hashlib,json,struct
OUT=Path(__file__).resolve().parent
reader=OUT.parent/'p1-native-runtime-054/read_metadata_static.py'
scope={'__file__':str(reader),'__name__':'_bounded_metadata'}
exec(compile(reader.read_text(encoding='utf-8').split('selected=[]\n')[0],str(reader),'exec'),scope)
mapping=json.loads((OUT.parent/'p1-native-mapping-054/mapping-verification.json').read_text(encoding='utf-8'))
assert hashlib.sha256(scope['binary']).hexdigest()==mapping['game_dll_sha256']
assert hashlib.sha256(scope['meta']).hexdigest()==mapping['metadata_sha256']
module=mapping['codegen_module'];pointers=scope['pointer_table'](module['array_address'],module['method_pointer_count'])
wanted={'Torappu.Battle.AbilityStandard','Torappu.Battle.AbilityStandard+<_DoCast>d__85',
 'Torappu.Battle.Abilities.MultiMeleeAttack','Torappu.Battle.Abilities.AbstractAnimatedAbility',
 'Torappu.Battle.Abilities.AbstractBasicAttack','Torappu.Battle.Abilities.EasyToStartAbility',
 'Torappu.Battle.Character','Torappu.Battle.Entity','Torappu.Battle.EventListener',
 'Torappu.Battle.BattleController','Torappu.Battle.ObjectManager','Torappu.Battle.BattleFormula',
 'Torappu.Battle.AbilityStandard+Event','Torappu.Battle.Entity+Event',
 'Torappu.Battle.SpineAnimator+AnimationData','Torappu.Battle.UnitAnimator',
 'Torappu.Battle.Abilities.AbstractAnimatedAbility+TimeMode',
 'Torappu.Battle.Abilities.EasyToStartAbility+<WaitForNextEvent>d__15',
 'Torappu.Battle.StandardEvent','Torappu.Battle.Animator','Torappu.Battle.BasicAnimator','Torappu.Battle.Unit',
 'Torappu.Battle.SpineAnimator','Torappu.Battle.CharacterAnimator','Torappu.Battle.ModeSkinHolder'}
selected=[]
for ti,td in enumerate(scope['types']):
 name=scope['type_def_name'](ti)
 if not (name in wanted or name.startswith('Torappu.Battle.CoroutineSimulator') or
     name.startswith('Torappu.Battle.Abilities.MultiMeleeAttack+<OnWaitForPreDelay>') or
     name.startswith('Torappu.Battle.Abilities.EasyToStartAbility+<OnWaitForPreDelay>') or
     name.startswith('Torappu.Battle.AsyncUtil+<WaitWhileForFixedSeconds>')):continue
 pointer=scope['reg']['fields'][ti]
 offsets=struct.unpack_from('<'+str(td[18])+'i',scope['binary'],scope['offset'](pointer)) if pointer and td[18] else []
 fields=[{'name':scope['string'](scope['fields'][fi][0]),'type':scope['typename'](scope['fields'][fi][1]),
   'offset':offsets[j] if offsets else None,'default':scope['default_value'](fi)}
   for j,fi in enumerate(range(td[8],td[8]+td[18]))]
 methods=[]
 for mi in range(td[9],td[9]+td[16]):
  m=scope['methods'][mi];address=pointers[(m[5]&0xffffff)-1] if (m[5]&0xffffff)<=len(pointers) else None
  methods.append({'name':name+'$$'+scope['string'](m[0]),'metadata_method_index':mi,'token':hex(m[5]),'slot':m[8],
    'address':hex(address) if address else None})
 slots=[]
 for slot in range(td[21]):
  enc=scope['vtable'][td[14]+slot][0];kind=enc>>29;index=(enc&0x1ffffffe)>>1
  row={'slot':slot,'usage_type':kind,'decoded_index':index}
  if kind==3 and index<len(scope['methods']):
   m=scope['methods'][index];row['method']=scope['type_def_name'](m[1])+'$$'+scope['string'](m[0])
  slots.append(row)
 selected.append({'name':name,'type_index':ti,'parent':scope['typename'](td[4]) if td[4]>=0 else None,
     'fields':fields,'methods':methods,'vtable':slots})
literal_records=scope['records']('stringLiteral','II');references=[]
for cfg in sorted(OUT.glob('*-cfg.json')):
 for method in json.loads(cfg.read_text(encoding='utf-8'))['methods']:
  for ins in method['instructions']:
   for ref in ins.get('rip_data',[]):
    if 'uint32' not in ref:continue
    enc=ref['uint32'];kind=enc>>29;idx=(enc&0x1ffffffe)>>1
    if kind==5 and idx<len(literal_records):
     size,index=literal_records[idx];start=scope['header']['stringLiteralData'][0]+index
     value=scope['meta'][start:start+size].decode('utf-8')
    elif kind==1 and idx<len(scope['native_types']):value=scope['typename'](idx)
    elif kind==3 and idx<len(scope['methods']):
     m=scope['methods'][idx];value=scope['type_def_name'](m[1])+'$$'+scope['string'](m[0])
    else:continue
    references.append({'cfg':cfg.name,'method':method['method']['Name'],'instruction':ins['address'],
      'literal_address':ref['address'],'kind':kind,'value':value})
result={'source_metadata_sha256':hashlib.sha256(scope['meta']).hexdigest(),
 'source_game_dll_sha256':hashlib.sha256(scope['binary']).hexdigest(),
 'selected':selected,'literal_references':references,'dll_executed':False,'process_memory_read':False}
(OUT/'metadata.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'types':[r['name'] for r in selected],'references':len(references)},ensure_ascii=False))
