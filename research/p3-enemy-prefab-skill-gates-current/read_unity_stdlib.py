"""Research-only, read-only focused UnityFS/type-tree decoder.

Format references: UnityPy 1.25.4 MIT (licensed copy in vendor), AssetStudio
CommonString.cs, official LZ4 block format. No optional codec shims or fake
decodes: unsupported formats and incomplete object reads raise explicitly.
"""
from pathlib import Path
import json,struct,hashlib,traceback
OUT=Path(__file__).resolve().parent
COMMON={int(k):v for k,v in json.loads((OUT/'common-strings.json').read_text(encoding='utf-8')).items()}
class Reader:
    def __init__(self,data,endian='>'):self.data=data;self.pos=0;self.endian=endian
    def take(self,n):
        assert n>=0 and self.pos+n<=len(self.data),(self.pos,n,len(self.data))
        d=self.data[self.pos:self.pos+n];self.pos+=n;return d
    def get(self,fmt):return struct.unpack(self.endian+fmt,self.take(struct.calcsize(fmt)))[0]
    def cstr(self):
        end=self.data.index(0,self.pos);raw=self.take(end-self.pos+1);return raw[:-1].decode('utf-8')
    def align(self,n=4):self.pos=(self.pos+n-1)//n*n
def lz4(raw,size,arknights_variant=False):
    r=Reader(raw,'<');out=bytearray()
    while r.pos<len(raw):
        token=r.get('B');n=(token&15) if arknights_variant else token>>4
        if n==15:
            while True:
                x=r.get('B');n+=x
                if x!=255:break
        assert len(out)+n<=size
        out.extend(r.take(n))
        if r.pos==len(raw):break
        offset=int.from_bytes(r.take(2),'big' if arknights_variant else 'little');assert 0<offset<=len(out)
        n=(token>>4) if arknights_variant else token&15
        if n==15:
            while True:
                x=r.get('B');n+=x
                if x!=255:break
        n+=4;assert len(out)+n<=size
        for _ in range(n):out.append(out[-offset])
    assert len(out)==size,(len(out),size)
    return bytes(out)
def decompress(raw,size,flags):
    mode=flags&63
    if mode==0:assert len(raw)==size;return raw
    if mode in (2,3):return lz4(raw,size)
    if mode==4:return lz4(raw,size,True)  # Ark-Unpacker src/lz4ak/Block.py v2.5.04+ exact format
    raise NotImplementedError(('unsupported compression',mode))
def bundle(raw):
    r=Reader(raw);assert r.cstr()=='UnityFS'
    version=r.get('I');player=r.cstr();engine=r.cstr()
    size=r.get('q');packed=r.get('I');unpacked=r.get('I');flags=r.get('I')
    assert version==8 and size==len(raw) and not flags&0x400, (version,size,len(raw),flags)
    r.align(16);start=r.pos
    if flags&0x80:r.pos=len(raw)-packed
    info=Reader(decompress(r.take(packed),unpacked,flags))
    if flags&0x80:r.pos=start
    info.take(16);blocks=[(info.get('I'),info.get('I'),info.get('H')) for _ in range(info.get('i'))]
    dirs=[(info.get('q'),info.get('q'),info.get('I'),info.cstr()) for _ in range(info.get('i'))]
    assert info.pos==len(info.data)
    if flags&0x200:r.align(16)
    payload=b''.join(decompress(r.take(c),u,f) for u,c,f in blocks)
    assert r.pos==(len(raw)-packed if flags&0x80 else len(raw)),(r.pos,len(raw),packed)
    return {'bundle_version':version,'engine':engine,'player':player,'flags':flags,'blocks':blocks,'dirs':[{'offset':o,'size':n,'flags':f,'name':name} for o,n,f,name in dirs]},[(name,payload[o:o+n]) for o,n,f,name in dirs]
def typetree(r,version):
    count=r.get('i');nstrings=r.get('i');assert 0<count<100000 and 0<=nstrings<10000000
    nodes=[]
    for _ in range(count):
        ver=r.get('H');level=r.get('B');flags=r.get('B');typ=r.get('I');name=r.get('I');size=r.get('i');index=r.get('i');meta=r.get('i');ref=r.get('Q')
        nodes.append({'version':ver,'level':level,'flags':flags,'type':typ,'name':name,'size':size,'index':index,'meta':meta,'reference_hash':ref,'children':[]})
    strings=r.take(nstrings)
    def resolve(offset):
        if offset&0x80000000:
            key=offset&0x7fffffff
            if key not in COMMON:raise ValueError(('unknown common string',key))
            return COMMON[key]
        return strings[offset:strings.index(0,offset)].decode('utf-8')
    stack=[]
    for node in nodes:
        node['type']=resolve(node['type']);node['name']=resolve(node['name'])
        while stack and stack[-1]['level']>=node['level']:stack.pop()
        if stack:stack[-1]['children'].append(node)
        stack.append(node)
    return nodes[0]
PRIMITIVES={'SInt8':'b','UInt8':'B','char':'B','short':'h','SInt16':'h','unsigned short':'H','UInt16':'H','int':'i','SInt32':'i','unsigned int':'I','UInt32':'I','Type*':'I','long long':'q','SInt64':'q','unsigned long long':'Q','UInt64':'Q','FileSize':'Q','float':'f','double':'d','bool':'?'}
def value(node,r):
    typ=node['type'];align=bool(node['meta']&0x4000)
    if typ in PRIMITIVES:v=r.get(PRIMITIVES[typ])
    elif typ=='string':
        n=r.get('i');assert 0<=n<=len(r.data);v=r.take(n).decode('utf-8');r.align()
    elif typ=='TypelessData':
        n=r.get('i');assert 0<=n<=len(r.data);raw=r.take(n);v={'bytes':n,'sha256':hashlib.sha256(raw).hexdigest()}
    elif typ in ('ReferencedObject','ManagedReferencesRegistry','ReferencedObjectData'):raise NotImplementedError(('managed references',typ))
    elif node['children'] and node['children'][0]['type']=='Array':
        array=node['children'][0];align|=bool(array['meta']&0x4000)
        n=r.get('i');assert 0<=n<1000000,n
        v=[value(array['children'][1],r) for _ in range(n)]
    else:v={child['name']:value(child,r) for child in node['children']}
    if align:r.align()
    return v
def serialized(raw):
    r=Reader(raw);metadata_size=r.get('I');file_size=r.get('I');version=r.get('I');data_offset=r.get('I')
    endian=r.get('B');r.take(3)
    assert version==22,version
    metadata_size=r.get('I');file_size=r.get('q');data_offset=r.get('q');unknown=r.get('q')
    assert file_size==len(raw),(file_size,len(raw))
    r.endian='>' if endian else '<';engine=r.cstr();platform=r.get('i');enabled=r.get('?')
    assert enabled,'No serialized type tree; need real metadata, do not guess'
    types=[]
    for _ in range(r.get('i')):
        class_id=r.get('i');stripped=r.get('?');scriptindex=r.get('h');scriptid=r.take(16).hex() if class_id==114 else None;typehash=r.take(16).hex()
        tree=typetree(r,version)
        dependencies=[r.get('i') for _ in range(r.get('i'))]
        types.append({'class_id':class_id,'script_type_index':scriptindex,'script_id':scriptid,'old_type_hash':typehash,'tree':tree,'dependencies':dependencies})
    objects=[]
    for _ in range(r.get('i')):
        r.align();path_id=r.get('q');start=r.get('q')+data_offset;size=r.get('I');typeindex=r.get('i')
        objects.append({'path_id':path_id,'byte_start':start,'byte_size':size,'type_index':typeindex,'class_id':types[typeindex]['class_id']})
    scripts=[]
    for _ in range(r.get('i')):
        local_index=r.get('i');r.align();identifier=r.get('q');scripts.append({'local_index':local_index,'identifier':identifier})
    externals=[]
    for _ in range(r.get('i')):externals.append({'empty':r.cstr(),'guid':r.take(16).hex(),'type':r.get('i'),'path':r.cstr()})
    reftypes=r.get('i');assert reftypes==0,reftypes
    userinfo=r.cstr();assert r.pos<=data_offset
    for obj in objects:
        o=Reader(raw[obj['byte_start']:obj['byte_start']+obj['byte_size']],r.endian)
        try:
            obj['data']=value(types[obj['type_index']]['tree'],o)
            assert o.pos==obj['byte_size'],('read incomplete',o.pos,obj['byte_size'])
            obj['read_exact']=True
        except Exception as exc:obj['error']=repr(exc);obj['data']=None
    return {'version':version,'engine':engine,'platform':platform,'type_tree_enabled':enabled,'metadata_bytes':metadata_size,'data_offset':data_offset,'types':types,'scripts':scripts,'externals':externals,'objects':objects}
