"""Pure-file v29 registration + enum constants; never runs game code.

Layouts reference the pinned Il2CppDumper MIT source retained beside this file.
"""
from pathlib import Path
import json,struct,hashlib
OUT=Path(__file__).resolve().parent
GAME=Path('D:/Hypergryph Launcher/games/Arknights/GameAssembly.dll')
META=GAME.parent/'Arknights_Data/il2cpp_data/Metadata/global-metadata.dat'
meta=META.read_bytes();binary=GAME.read_bytes()
assert struct.unpack_from('<II',meta)==(0xfab11baf,29)
H=['stringLiteral','stringLiteralData','string','events','properties','methods','parameterDefaultValues','fieldDefaultValues','fieldAndParameterDefaultValueData','fieldMarshaledSizes','parameters','fields','genericParameters','genericParameterConstraints','genericContainers','nestedTypes','interfaces','vtableMethods','interfaceOffsets','typeDefinitions','images','assemblies','fieldRefs','referencedAssemblies','attributeData','attributeDataRange','unresolvedVirtualCallParameterTypes','unresolvedVirtualCallParameterRanges','windowsRuntimeTypeNames','windowsRuntimeStrings','exportedTypeDefinitions']
header={n:struct.unpack_from('<II',meta,8+i*8) for i,n in enumerate(H)}
def records(name,fmt):
    off,size=header[name];s=struct.Struct('<'+fmt);assert size%s.size==0
    return list(s.iter_unpack(meta[off:off+size]))
def string(index):
    off,size=header['string'];start=off+index;assert off<=start<off+size
    return meta[start:meta.index(0,start)].decode('utf-8')
types=records('typeDefinitions','IIiiiiiIiiiiiiiii8HII');fields=records('fields','IiI');methods=records('methods','IiiiiI4H');vtable=records('vtableMethods','I')
defaults={x[0]:x for x in records('fieldDefaultValues','iii')}
peoff=struct.unpack_from('<I',binary,60)[0];assert binary[peoff:peoff+4]==b'PE\0\0'
count=struct.unpack_from('<H',binary,peoff+6)[0];optsize=struct.unpack_from('<H',binary,peoff+20)[0]
opt=binary[peoff+24:peoff+24+optsize];base=struct.unpack_from('<Q',opt,24)[0]
sections=[]
for i in range(count):
    h=binary[peoff+24+optsize+i*40:peoff+24+optsize+(i+1)*40];vs,rva,rs,off=struct.unpack_from('<IIII',h,8)
    sections.append({'name':h[:8].split(b'\0')[0].decode(),'rva':rva,'rawsize':rs,'offset':off,'characteristics':struct.unpack_from('<I',h,36)[0]})
def offset(va):
    rva=va-base
    for s in sections:
        if s['rva']<=rva<s['rva']+s['rawsize']:return s['offset']+rva-s['rva']
    raise ValueError(('outside physical PE',hex(va)))
def pointer_table(va,n):
    p=offset(va);return struct.unpack_from('<'+str(n)+'Q',binary,p)
# A registration has adjacent fieldOffsetsCount/typeDefinitionsSizesCount.
# Candidate must also validate its typesCount and all type pointers physically.
needle=struct.pack('<Q',len(types));candidates=[];cursor=0
while True:
    hit=binary.find(needle,cursor)
    if hit<0:break
    cursor=hit+1
    if hit<80 or hit+48>len(binary):continue
    if binary[hit+16:hit+24]!=needle:continue
    regpos=hit-80
    vals=struct.unpack_from('<16Q',binary,regpos)
    try:
        typecnt,typetable=vals[6:8];fieldcnt,fieldtable=vals[10:12]
        if not (100000<typecnt<1000000 and fieldcnt==len(types)):continue
        tp=pointer_table(typetable,typecnt)
        for p in tp:offset(p)
        fp=pointer_table(fieldtable,fieldcnt)
        for p in fp:
            if p:offset(p)
        candidates.append({'physical_offset':regpos,'values':vals,'types':tp,'fields':fp})
    except (ValueError,struct.error):continue
assert len(candidates)==1,[(x['physical_offset'],x['values'][:12]) for x in candidates]
reg=candidates[0]
native_types=[struct.unpack_from('<QI',binary,offset(p)) for p in reg['types']]
native_pointer_index={p:i for i,p in enumerate(reg['types'])}
def native_type(index):
    data,bits=native_types[index];kind=(bits>>16)&255
    return {'index':index,'data':data,'bits':hex(bits),'kind':kind,'attrs':bits&65535,'byref':bool(bits&(1<<29))}
def type_def_name(index):
    td=types[index];name=string(td[0]);ns=string(td[1])
    if td[3]>=0:return typename(td[3])+'+'+name
    return (ns+'.' if ns else '')+name
def typename(index):
    t=native_type(index)
    primitive={1:'System.Void',2:'System.Boolean',3:'System.Char',4:'System.SByte',5:'System.Byte',6:'System.Int16',7:'System.UInt16',8:'System.Int32',9:'System.UInt32',10:'System.Int64',11:'System.UInt64',12:'System.Single',13:'System.Double',14:'System.String',24:'System.IntPtr',25:'System.UIntPtr',28:'System.Object'}
    if t['kind'] in primitive:return primitive[t['kind']]
    if t['kind'] in (17,18):
        return type_def_name(t['data'])
    if t['kind']==21:
        tp,ci,mi,cached=struct.unpack_from('<4Q',binary,offset(t['data']))
        assert tp in native_pointer_index
        generic=typename(native_pointer_index[tp]);argc,argv=struct.unpack_from('<2Q',binary,offset(ci))
        assert 0<argc<32
        args=[]
        for ap in pointer_table(argv,argc):
            assert ap in native_pointer_index;args.append(typename(native_pointer_index[ap]))
        return generic+'<'+','.join(args)+'>'
    if t['kind'] in (15,16,29):
        assert t['data'] in native_pointer_index
        return typename(native_pointer_index[t['data']])+{15:'*',16:'&',29:'[]'}[t['kind']]
    return 'Il2CppKind'+str(t['kind'])+'('+str(t['data'])+')'
def compressed_unsigned(pos):
    a=meta[pos];pos+=1
    if a&128==0:return a,pos
    if a&192==128:return ((a&127)<<8)|meta[pos],pos+1
    if a&224==192:return ((a&63)<<24)|(meta[pos]<<16)|(meta[pos+1]<<8)|meta[pos+2],pos+3
    if a==240:return struct.unpack_from('<I',meta,pos)[0],pos+4
    if a==254:return 0xfffffffe,pos
    if a==255:return 0xffffffff,pos
    raise ValueError(('invalid compressed integer',a,pos))
def default_value(fi):
    if fi not in defaults:return None
    _,ti,di=defaults[fi]
    if di<0:return None
    pos=header['fieldAndParameterDefaultValueData'][0]+di;kind=native_type(ti)['kind']
    if kind in (8,9):
        v,end=compressed_unsigned(pos)
        if kind==8:
            if v==0xffffffff:v=-2147483648
            else:v=-(v//2+1) if v&1 else v//2
    elif kind in (2,4,5,6,7,10,11,12,13):
        fmt={2:'?',4:'b',5:'B',6:'h',7:'H',10:'q',11:'Q',12:'f',13:'d'}[kind]
        v=struct.unpack_from('<'+fmt,meta,pos)[0];end=pos+struct.calcsize(fmt)
    else:return {'unknown_kind':kind,'position':pos}
    return {'value':v,'type':typename(ti),'data_index':di,'raw':meta[pos:end].hex()}
selected=[]
terms=['BuffData','GlobalBuff','GlobalBuffData','BuffLifeType','BuffOverrideType','AttributeType','FormulaItem','BuffLifeTimeType','LifeTimeType','StandardEvent','AttrModifier','AttributeModifier','CharacterAttribute','BattleSide','CardBuff','DeckBuff','BuffTrigger','Battle.Buff','Battle.Entity','Battle.Cost','BattleCostManager','RuntimeCost','Battle.Character','Battle.Timer','Decklike','Blackboard','AddRemainingAmmo','GBuff','Battle.Attributes','CharAttributes','Battle.Card','ObscuredAttributesSnapshot','Battle.Deck','BattleFormula','PeriodicTimer','Torappu.FP','Torappu.MathUtil','Battle.BattleController','Torappu.AttributesData','Torappu.AttributeMetaAttribute','Roguelike.RoguelikeBattleManager','ZoneIntoBuff']
terms += ['Battle.BattleOptions','CastSkillWithLimitTimes','AbilityEventCounter','SpController','Battle.Roguelike.RoguelikeInput','Battle.Roguelike.BasicRelic']
terms += ['AbnormalFlag','DoubleBuffered','Battle.BasicSkill','Battle.CastSkill','BattleRoguelikeRelicBuff']
for ti,td in enumerate(types):
    name=string(td[0]);ns=string(td[1]);is_enum=bool(td[25]&2)
    # Also retain battle enums whose field names identify action events.
    fnames=[string(fields[fi][0]) for fi in range(td[8],td[8]+td[19])]
    fullname=type_def_name(ti)
    if fullname not in ('Torappu.AttributesData','AttributesKeyFrame','Torappu.AttributesData+FieldMeta','Torappu.AttributeMetaAttribute','Torappu.FP'):continue

    fp=reg['fields'][ti];offsets=struct.unpack_from('<'+str(td[19])+'i',binary,offset(fp)) if fp and td[19] else []
    fs=[]
    for j,fi in enumerate(range(td[8],td[8]+td[19])):
        firow=fields[fi];fs.append({'name':string(firow[0]),'field_index':fi,'type':typename(firow[1]),'native_type':native_type(firow[1]),'offset':offsets[j] if offsets else None,'default':default_value(fi)})
    ms=[]
    for mi in range(td[9],td[9]+td[17]):
        m=methods[mi];ms.append({'name':string(m[0]),'method_index':mi,'token':hex(m[5]),'slot':m[8],'flags':hex(m[6]),'parameter_count':m[9]})
    vs=[]
    for j in range(td[22]):
        encoded=vtable[td[14]+j][0];kind=encoded>>29;idx=(encoded&0x1ffffffe)>>1
        entry={'slot':j,'encoded':hex(encoded),'usage_type':kind,'decoded_index':idx}
        if kind==3 and idx<len(methods):
            m=methods[idx];entry['method']=type_def_name(m[1])+'$$'+string(m[0])
        vs.append(entry)
    selected.append({'name':fullname,'type_index':ti,'enum':is_enum,'element_type':typename(td[5]) if is_enum else None,'fields':fs,'methods':ms,'vtable':vs})
receipt={'source_metadata_sha256':hashlib.sha256(meta).hexdigest(),'source_game_dll_sha256':hashlib.sha256(binary).hexdigest(),'metadata_registration_physical_offset':hex(reg['physical_offset']),'metadata_registration_values':[hex(v) for v in reg['values']],'type_count':len(types),'native_types_count':len(native_types),'selected':selected,'dll_executed':False,'process_memory_read':False}
(OUT/'metadata-native-fields.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
# Read encoded usage data in selected disassembly windows, backed by pinned
# Metadata.GetEncodedIndexType/GetDecodedMethodIndex routines.
literal_records=records('stringLiteral','II');lits=[]
for jsonfile in ['parent-chained.json','blackboard-timers.json','container-periodic.json','precise.json','timer-helpers.json','attributes-override.json','override-real.json','queue-priority.json','global-life.json','births.json','unit-birth.json','register-born.json','unit-ammo-tick.json','ammo-count-core.json','ammo-counter.json','ammo-limit-life.json','relic-input-order.json','sp-tick-gate.json','sp-recover.json','sp-doapply.json','character-sp-order.json','ammo-helper-sp-final.json']:
    if not (OUT/jsonfile).exists():continue
    for win in json.loads((OUT/jsonfile).read_text(encoding='utf-8'))['method_windows']:
        for ins in win['instructions']:
            for ref in ins['rip_refs']:
                encoded=struct.unpack_from('<I',bytes.fromhex(ref['raw16']))[0]
                kind=(encoded&0xe0000000)>>29;index=(encoded&0x1ffffffe)>>1
                if kind==1 and index<len(native_types):
                    lits.append({'method':win['method']['Name'],'instruction':ins['address'],'address':ref['address'],'encoded':hex(encoded),'type_index':index,'type':typename(index)})
                elif kind==5 and index<len(literal_records):
                    size,di=literal_records[index];pos=header['stringLiteralData'][0]+di
                    lits.append({'method':win['method']['Name'],'instruction':ins['address'],'address':ref['address'],'encoded':hex(encoded),'literal_index':index,'string':meta[pos:pos+size].decode('utf-8')})
(OUT/'parent-string-literals.json').write_text(json.dumps(lits,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'registration':hex(reg['physical_offset']),'types':len(native_types),'selected':len(selected),'literal_count':len(lits)},ensure_ascii=False))
