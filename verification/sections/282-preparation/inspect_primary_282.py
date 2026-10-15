"""282 candidate file-only source inventory. No DLL execution or memory read."""
import json, hashlib, struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RESEARCH=ROOT/'.cache/research'
reader=RESEARCH/'p2-native-current-263/read_metadata_static.py'
ns={'__file__':str(reader)}
exec(compile(reader.read_text(encoding='utf8').split('selected=[]\n')[0],str(reader),'exec'),ns)
sha=lambda b:hashlib.sha256(b).hexdigest()
report={'dll_sha256':sha(ns['binary']),'metadata_sha256':sha(ns['meta']),
        'file_only':True,'game_dll_executed':False,'process_memory_read':False}
switch=[]
for attr in range(7,16):
    va=0x1806f79bc+(attr-7)*4
    off=ns['offset'](va);raw=ns['binary'][off:off+4]
    target=0x180000000+struct.unpack('<i',raw)[0]
    switch.append({'attribute':attr,'address':hex(va),'physical_offset':off,'raw_hex':raw.hex(),'target':hex(target)})
report['entity_dirty_switch']=switch
names={'Torappu.Battle.Attributes','Torappu.Battle.Entity','Torappu.Battle.Unit','Torappu.Battle.Character','Torappu.AttributeType'}
types=[]
for ti,td in enumerate(ns['types']):
    name=ns['type_def_name'](ti)
    if name not in names:continue
    fields=[]
    for ordinal,fi in enumerate(range(td[8],td[8]+td[19])):
        row=ns['fields'][fi];fname=ns['string'](row[0])
        if name=='Torappu.AttributeType' or any(k in fname.lower() for k in ('attribute','spcontroller','dirty','recover')):
            pointer=ns['reg']['fields'][ti]
            fieldoff=struct.unpack_from('<i',ns['binary'],ns['offset'](pointer)+ordinal*4)[0] if pointer else None
            fields.append({'index':fi,'name':fname,'type':ns['typename'](row[1]),'offset':fieldoff,'default':ns['default_value'](fi)})
    types.append({'type_index':ti,'name':name,'fields':fields})
report['types']=types
method_names=[]
parameters=ns['records']('parameters','Iii')
for mi in (64269,64290,64291,66699,76035,77706):
    m=ns['methods'][mi]
    method_names.append({'index':mi,'name':ns['type_def_name'](m[1])+'$$'+ns['string'](m[0]),
                         'return_type':ns['typename'](m[2]),'slot':m[8],
                         'parameters':[{'index':pi,'name':ns['string'](parameters[pi][0]),'type':ns['typename'](parameters[pi][2])} for pi in range(m[3],m[3]+m[9])]})
report['method_metadata']=method_names
(HERE/'primary-inventory-282.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'switch':switch,'methods':method_names,'types':[(t['name'],len(t['fields'])) for t in types]},ensure_ascii=False,indent=2))
