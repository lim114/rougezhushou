"""Verify only file-backed bytes and labels; never load/execute game code."""
import argparse,hashlib,json,mmap,struct
from pathlib import Path

def verify(artifact_dir,game_dir=None):
    root=Path(artifact_dir)
    read=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
    proof=read('native-proof.json');bindings=read('metadata-bindings.json');receipt=read('receipt.json')
    for name,expected in receipt['artifact_sha256'].items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,('artifact hash',name)
    for field in ('game_dll_sha256','metadata_sha256'):
        assert proof[field]==bindings[field]==receipt[field],field
    assert not proof['game_dll_executed'] and not proof['current_hotfix_equivalence_proven']
    assert not receipt['runtime_binding_verified'] and not receipt['current_hotfix_equivalence_proven']
    for method in proof['methods']:assert not method['limits']
    checks={'artifact_consistency':True,'native_file_comparison':'unavailable' if game_dir is None else 'requested',
        'game_dll_executed':False,'process_memory_read':False,'private_state_read':False,
        'current_hotfix_equivalence_proven':False,'runtime_binding_verified':False}
    if game_dir is None:return checks
    game=Path(game_dir);meta=(game/proof['metadata_relative']).read_bytes()
    assert hashlib.sha256(meta).hexdigest()==proof['metadata_sha256'],'metadata hash'
    assert struct.unpack_from('<II',meta)==(0xfab11baf,29),'metadata version'
    with (game/proof['game_dll_relative']).open('rb') as handle,mmap.mmap(handle.fileno(),0,access=mmap.ACCESS_READ) as binary:
        assert hashlib.sha256(binary).hexdigest()==proof['game_dll_sha256'],'DLL hash'
        pe=struct.unpack_from('<I',binary,60)[0];assert binary[pe:pe+4]==b'PE\0\0'
        count=struct.unpack_from('<H',binary,pe+6)[0];opt_size=struct.unpack_from('<H',binary,pe+20)[0]
        base=struct.unpack_from('<Q',binary,pe+24+24)[0];sections=[]
        for n in range(count):
            vs,rva,size,pos=struct.unpack_from('<IIII',binary,pe+24+opt_size+n*40+8)
            sections.append((rva,size,pos))
        def offset(address):
            rva=address-base
            for start,size,pos in sections:
                if start<=rva<start+size:return pos+rva-start
            raise AssertionError(('not file backed',hex(address)))
        checked=set()
        for method in proof['methods']:
            for i in method['instructions']:
                pos=offset(int(i['address'],0));raw=bytes.fromhex(i['bytes'])
                assert pos==int(i['physical_offset'],0),(i['address'],'physical offset')
                assert binary[pos:pos+len(raw)]==raw,('instruction',i['address'])
                checked.add((i['address'],i['bytes']))
        for row in bindings['byte_spans']:
            src=binary if row['source']=='dll' else meta;pos=int(row['physical_offset'],0)
            assert src[pos:pos+row['size']].hex()==row['bytes'],('span',row['reason'])
        vals=[int(v,0) for v in bindings['metadata_registration_values']]
        h=bindings['metadata_header_offsets'];formats=bindings['record_formats']
        def string(index):
            pos=h['string'][0]+index;return meta[pos:meta.index(0,pos)].decode('utf-8')
        def td(index):
            fmt='<'+formats['typeDefinitions'];return struct.unpack_from(fmt,meta,h['typeDefinitions'][0]+index*struct.calcsize(fmt))
        def native_name(index):
            ptr=struct.unpack_from('<Q',binary,offset(vals[7])+index*8)[0]
            data,bits=struct.unpack_from('<QI',binary,offset(ptr));kind=(bits>>16)&255
            if kind in (17,18):return type_name(data)
            return 'Il2CppKind'+str(kind)+'('+str(data)+')'
        def type_name(index):
            t=td(index);name=string(t[0])
            if t[3]>=0:return native_name(t[3])+'+'+name
            namespace=string(t[1]);return namespace+'.'+name if namespace else name
        for row in bindings['methods']:
            fmt='<'+formats['methods'];raw=struct.unpack_from(fmt,meta,h['methods'][0]+row['method_definition_index']*struct.calcsize(fmt))
            assert type_name(raw[1])+'$$'+string(raw[0])==row['method'],('method label',row['method'])
            assert raw[9]==row['parameter_count'] and hex(raw[5])==row['token'],row['method']
        for row in bindings['layouts']:
            raw=td(row['type_index']);assert type_name(row['type_index'])==row['type_name']
            assert hex(raw[7])==row['type_attributes'] and bool(raw[7]&0x2000)==row['serializable_type_flag']
            for f in row['fields']:
                ff=struct.unpack_from('<'+formats['fields'],meta,h['fields'][0]+f['field_index']*12)
                assert string(ff[0])==f['name'],('field label',f['name'])
        for usage in bindings['encoded_usages']:
            encoded=int(usage['encoded'],0)
            assert encoded>>29==usage['usage_type'] and (encoded&0x1ffffffe)>>1==usage['decoded_index']
            if usage['usage_type']==6:
                pos=int(usage['method_spec_physical_offset'],0)
                raw=struct.unpack_from('<iii',binary,pos)
                assert pos==offset(vals[9])+usage['decoded_index']*12
                assert raw[0]==usage['method_definition_index'] and binary[pos:pos+12].hex()==usage['method_spec_bytes']
                for index,key in ((raw[1],'class_inst'),(raw[2],'method_inst')):
                    inst=usage.get(key)
                    assert (index<0)==(inst is None)
                    if inst:
                        assert inst['index']==index
                        ptr=struct.unpack_from('<Q',binary,offset(vals[3])+index*8)[0]
                        assert ptr==int(inst['address'],0)
                        argc,argv=struct.unpack_from('<2Q',binary,offset(ptr))
                        pointers=struct.unpack_from('<'+'Q'*argc,binary,offset(argv))
                        assert [hex(p) for p in pointers]==inst['argument_pointers']
        assert len(checked)==receipt['unique_physical_instruction_checks']
        checks.update(native_file_comparison='passed',unique_physical_instruction_checks=len(checked),
            metadata_and_binding_byte_spans=len(bindings['byte_spans']))
    return checks

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--artifact-dir',default=str(Path(__file__).resolve().parent))
    parser.add_argument('--game-dir');parser.add_argument('--output');args=parser.parse_args()
    result=verify(args.artifact_dir,args.game_dir)
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:Path(args.output).write_text(text,encoding='utf-8',newline='\n')
    print(text,end='')
