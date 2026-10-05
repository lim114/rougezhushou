"""Reproduce only the S1 types, virtual bindings and literal keys from disk."""
from pathlib import Path
import hashlib,json,struct
OUT=Path(__file__).resolve().parent
reader=OUT.parent/'p1-native-runtime-054/read_metadata_static.py'
scope={'__file__':str(reader),'__name__':'_bounded_metadata'}
exec(compile(reader.read_text(encoding='utf-8').split('selected=[]\n')[0],str(reader),'exec'),scope)
wanted={
    'Torappu.Battle.Abilities.MultiMeleeAttack',
    'Torappu.Battle.Abilities.MultiMeleeAttack+<OnWaitForTriggerDelta>d__38',
    'Torappu.Battle.Abilities.EasyToStartAbility',
    'Torappu.Battle.Abilities.AbstractAnimatedAbility',
    'Torappu.Battle.AbilityStandard',
    'Torappu.Battle.AbilityStandard+<_DoCast>d__85',
    'Torappu.Battle.ReplacementSkillFixed',
    'Torappu.Battle.ReplacementSkill',
    'Torappu.Battle.AsyncUtil+<WaitForFixedSeconds>d__0',
}
selected=[]
for ti,td in enumerate(scope['types']):
    name=scope['type_def_name'](ti)
    if name not in wanted:continue
    pointer=scope['reg']['fields'][ti]
    offsets=struct.unpack_from('<'+str(td[18])+'i',scope['binary'],scope['offset'](pointer)) if pointer and td[18] else []
    fields=[{'name':scope['string'](scope['fields'][fi][0]),
        'type':scope['typename'](scope['fields'][fi][1]),'offset':offsets[j] if offsets else None}
        for j,fi in enumerate(range(td[8],td[8]+td[18]))]
    slots=[]
    for slot in range(td[21]):
        enc=scope['vtable'][td[14]+slot][0];kind=enc>>29;index=(enc&0x1ffffffe)>>1
        row={'slot':slot,'usage_type':kind,'decoded_index':index}
        if kind==3 and index<len(scope['methods']):
            m=scope['methods'][index];row['method']=scope['type_def_name'](m[1])+'$$'+scope['string'](m[0])
        slots.append(row)
    selected.append({'name':name,'type_index':ti,'parent':scope['typename'](td[4]) if td[4]>=0 else None,
                     'fields':fields,'vtable':slots})
assert {row['name'] for row in selected}==wanted,wanted-{row['name'] for row in selected}
literal_records=scope['records']('stringLiteral','II');literals=[]
for cfg in sorted(OUT.glob('*-cfg.json')):
    data=json.loads(cfg.read_text(encoding='utf-8'))
    for method in data['methods']:
        for ins in method['instructions']:
            for ref in ins.get('rip_data',[]):
                if 'uint32' not in ref:continue
                enc=ref['uint32'];kind=enc>>29;idx=(enc&0x1ffffffe)>>1
                if kind!=5 or idx>=len(literal_records):continue
                size,index=literal_records[idx];start=scope['header']['stringLiteralData'][0]+index
                value=scope['meta'][start:start+size].decode('utf-8')
                literals.append({'cfg':cfg.name,'method':method['method']['Name'],'instruction':ins['address'],
                                 'literal_address':ref['address'],'literal':value})
result={'source_metadata_sha256':hashlib.sha256(scope['meta']).hexdigest(),
    'source_game_dll_sha256':hashlib.sha256(scope['binary']).hexdigest(),'selected':selected,
    'literal_keys':literals,'dll_executed':False,'process_memory_read':False}
(OUT/'reproduced-metadata.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'types':len(selected),'literal_keys':len(literals)},ensure_ascii=False))
