"""Decode v29 field attributes from public installation bytes, no game execution.

Serialization reference: pinned Il2CppDumper v6.7.46 MIT sources beside this
file. Reuse the existing pure-file metadata/type registration reader only up
to its first output loop. This bounded reader rejects unsupported value types.
"""
from pathlib import Path
import hashlib,json,struct

OUT=Path(__file__).resolve().parent
source=OUT/'read_metadata_static.py'
ns={'__file__':str(source)}
exec(compile(source.read_text(encoding='utf-8').split('selected=[]\n')[0],str(source),'exec'),ns)
verification=json.loads((OUT/'mapping-verification.json').read_text(encoding='utf-8'))
sha=lambda data:hashlib.sha256(data).hexdigest()
assert sha(ns['meta'])==verification['metadata_sha256']
assert sha(ns['binary'])==verification['game_dll_sha256']
images=ns['records']('images','10i');ranges=ns['records']('attributeDataRange','II')
meta=ns['meta'];types=ns['types'];fields=ns['fields'];methods=ns['methods'];string=ns['string']
ti=next(i for i in range(len(types)) if ns['type_def_name'](i)=='Torappu.AttributesData');td=types[ti]
image=next(im for im in images if im[2]<=ti<im[2]+im[3])
indices={ranges[i][0]:i for i in range(image[8],image[8]+image[9])}
mapping=json.loads((OUT/'script.json').read_text(encoding='utf-8'))['ScriptMethod']
rows=[]
def signed(pos):
    value,pos=ns['compressed_unsigned'](pos)
    return (-(value//2+1) if value&1 else value//2),pos
def value(pos):
    kind=meta[pos];pos+=1;enum=None
    if kind==0x55:
        index,pos=signed(pos);native=ns['native_type'](index)
        enum=ns['typename'](index)
        kind=ns['native_type'](types[native['data']][5])['kind']
    if kind==8:val,pos=signed(pos)
    elif kind==12:val=struct.unpack_from('<f',meta,pos)[0];pos+=4
    elif kind==2:val=bool(meta[pos]);pos+=1
    else:raise ValueError(('Unsupported custom attribute kind',kind,pos))
    return {'kind':kind,'enum':enum,'value':val},pos
for fi in range(td[8],td[8]+td[19]):
    name=string(fields[fi][0])
    if name not in ('maxHp','atk','def','magicResistance','cost','attackSpeed','baseAttackTime','blockCnt'):continue
    idx=indices[fields[fi][2]];start=ns['header']['attributeData'][0]+ranges[idx][1]
    end=ns['header']['attributeData'][0]+ranges[idx+1][1]
    count,pos=ns['compressed_unsigned'](start);ctors=struct.unpack_from('<'+str(count)+'i',meta,pos);pos+=4*count
    attributes=[]
    for ctor in ctors:
        argc,pos=ns['compressed_unsigned'](pos);fc,pos=ns['compressed_unsigned'](pos);pc,pos=ns['compressed_unsigned'](pos)
        assert fc==pc==0
        args=[]
        for _ in range(argc):arg,pos=value(pos);args.append(arg)
        method=methods[ctor];assert string(method[0])=='.ctor' and method[9]==argc
        bound=[m for m in mapping if m['metadata_method_index']==ctor]
        attr_type=ns['type_def_name'](method[1])
        if attr_type=='Torappu.AttributeMetaAttribute':assert len(bound)==1
        else:assert attr_type=='Newtonsoft.Json.JsonIgnoreAttribute' and argc==0
        attributes.append({'type':attr_type,'constructor_index':ctor,
            'constructor_address':hex(bound[0]['Address']) if bound else None,'arguments':args})
    assert pos==end,(name,pos,end)
    own=[a for a in attributes if a['type']=='Torappu.AttributeMetaAttribute'];assert len(own)==1

    assert own[0]['arguments'][0]['enum']=='Torappu.AttributeType'
    rows.append({'field':name,'field_token':hex(fields[fi][2]),'physical_offset':start,
        'raw_hex':meta[start:end].hex(),'fully_consumed':True,'attributes':attributes})
receipt={'passed':True,'dll_sha256':verification['game_dll_sha256'],'metadata_sha256':verification['metadata_sha256'],
    'assembly':string(image[0]),'fields':rows,'reader_sha256':sha(Path(__file__).read_bytes()),
    'base_reader_sha256':sha(source.read_bytes()),'game_executed':False,'process_memory_read':False,
    'source_note':'ctor native body must separately establish the second argument as minimum, not default value'}
(OUT/'interpolation-field-attributes.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'fields':[(r['field'],r['attributes'][0]['constructor_address']) for r in rows]}))
