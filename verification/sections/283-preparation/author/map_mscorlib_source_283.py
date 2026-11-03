"""Read file-backed PE codegen tables. Never load or execute the target DLL."""
from pathlib import Path
import bisect
import hashlib
import json
import mmap
import struct

OUT = Path(__file__).resolve().parent
GAME = Path('D:/Hypergryph Launcher/games/Arknights/GameAssembly.dll')
META = GAME.parent/'Arknights_Data/il2cpp_data/Metadata/global-metadata.dat'

metadata = META.read_bytes()
assert struct.unpack_from('<II', metadata) == (0xfab11baf, 29)
names = ['stringLiteral','stringLiteralData','string','events','properties','methods',
         'parameterDefaultValues','fieldDefaultValues','fieldAndParameterDefaultValueData',
         'fieldMarshaledSizes','parameters','fields','genericParameters',
         'genericParameterConstraints','genericContainers','nestedTypes','interfaces',
         'vtableMethods','interfaceOffsets','typeDefinitions','images','assemblies',
         'fieldRefs','referencedAssemblies','attributeData','attributeDataRange',
         'unresolvedVirtualCallParameterTypes','unresolvedVirtualCallParameterRanges',
         'windowsRuntimeTypeNames','windowsRuntimeStrings','exportedTypeDefinitions']
header = {n:struct.unpack_from('<II', metadata, 8+i*8) for i,n in enumerate(names)}
def records(name, fmt):
    offset,size = header[name]
    definition = struct.Struct('<'+fmt)
    assert size % definition.size == 0
    assert offset+size <= len(metadata)
    return list(definition.iter_unpack(metadata[offset:offset+size]))
def string(index):
    offset,size = header['string']; pos=offset+index
    assert offset <= pos < offset+size
    return metadata[pos:metadata.index(0,pos,offset+size)].decode('utf-8')
# Observed custom92-byte records. The inserted field before counts is opaque.
# Only independently cross-checked names, declaring relationships and method ranges
# are consumed; this does not certify the unknown field or a complete v29 schema.
types = records('typeDefinitions','IIiiiiiIiiiiiiiii8HII')
assert all((td[-1] >> 24) == 2 for td in types)
assert all(string(td[0]) is not None and string(td[1]) is not None for td in types)
methods = records('methods','IiiiiI4H')
images = records('images','IiiIiIiIiI')
assert all(0 <= method[1] < len(types) for method in methods)
for type_index, td in enumerate(types):
    first, count = td[9], td[17]
    if count:
        assert 0 <= first and first + count <= len(methods)
        assert all(methods[j][1] == type_index for j in range(first, first + count))
assert all(0 <= image[2] and image[2] + image[3] <= len(types) for image in images)
image = next(i for i in images if string(i[0]) == 'mscorlib.dll')
selected = [(n,m) for n,m in enumerate(methods) if image[2] <= m[1] < image[2]+image[3]]

with GAME.open('rb') as handle, mmap.mmap(handle.fileno(),0,access=mmap.ACCESS_READ) as data:
    assert data[:2] == b'MZ'
    peoff=struct.unpack_from('<I',data,60)[0]
    assert data[peoff:peoff+4] == b'PE\0\0'
    machine,count,_,_,_,optional_size,_ = struct.unpack_from('<HHIIIHH',data,peoff+4)
    assert machine == 0x8664
    optional=peoff+24
    assert struct.unpack_from('<H',data,optional)[0] == 0x20b
    imagebase=struct.unpack_from('<Q',data,optional+24)[0]
    sections=[]
    for n in range(count):
        pos=optional+optional_size+n*40
        virtual_size,rva,raw_size,offset=struct.unpack_from('<IIII',data,pos+8)
        sections.append({'name':data[pos:pos+8].split(b'\0')[0].decode(),
                         'rva':rva,'virtual_size':virtual_size,'raw_size':raw_size,
                         'offset':offset,'characteristics':struct.unpack_from('<I',data,pos+36)[0]})
    def file_offset(rva):
        for s in sections:
            if s['rva'] <= rva < s['rva']+s['raw_size']:
                return s['offset']+rva-s['rva']
        raise ValueError(('Not file-backed RVA',hex(rva)))
    def rva_from_offset(offset):
        for s in sections:
            if s['offset'] <= offset < s['offset']+s['raw_size']:
                return s['rva']+offset-s['offset']
        raise ValueError(('Not file-backed offset',hex(offset)))
    def executable(address):
        rva=address-imagebase
        return any(s['rva'] <= rva < s['rva']+s['raw_size'] and
                   s['characteristics'] & 0x20000000 for s in sections)
    candidates=[]; literal_positions=[]
    start=0
    while (literal:=data.find(b'mscorlib.dll\0',start)) >= 0:
        literal_positions.append(literal);start=literal+1
        needle=struct.pack('<Q',imagebase+rva_from_offset(literal));search=0
        while (pointer:=data.find(needle,search)) >= 0:
            search=pointer+1
            if pointer % 8 or pointer+24 > len(data):continue
            name_address,pointer_count,array_address=struct.unpack_from('<QQQ',data,pointer)
            if pointer_count != len(selected):continue
            try:array_offset=file_offset(array_address-imagebase)
            except ValueError:continue
            if array_offset+pointer_count*8>len(data):continue
            pointers=struct.unpack_from('<'+str(pointer_count)+'Q',data,array_offset)
            # Abstract/generic methods can be null; every nonzero pointer must
            # refer to executable bytes, and every exact metadata token fits.
            nonzero=[p for p in pointers if p]
            if not nonzero or not all(executable(p) for p in nonzero):continue
            if not all(0 < (m[5]&0xffffff) <= pointer_count for _,m in selected):continue
            candidates.append({'module_offset':pointer,'module_rva':rva_from_offset(pointer),
                               'array_offset':array_offset,'array_address':array_address,
                               'method_pointer_count':pointer_count,'pointers':pointers,
                               'nonzero_pointers':len(nonzero)})
    (OUT/'mscorlib-candidate-diagnostics.json').write_text(json.dumps({
        'literal_offsets':literal_positions,'metadata_selected_methods':len(selected),
        'candidates':[{k:v for k,v in c.items() if k!='pointers'} for c in candidates]},indent=2),encoding='utf-8')
    assert len(candidates)==1,('Ambiguous or absent codegen module',len(candidates))
    candidate=candidates[0]
    exception_rva,exception_size=struct.unpack_from('<II',data,optional+112+3*8)
    exception_offset=file_offset(exception_rva)
    assert exception_size%12==0
    functions=list(struct.iter_unpack('<III',data[exception_offset:exception_offset+exception_size]))
    assert functions==sorted(functions)
    starts=[f[0] for f in functions]
    mapped=[]
    for index,method in selected:
        address=candidate['pointers'][(method[5]&0xffffff)-1]
        if not address:continue
        kind=types[method[1]];namespace=string(kind[1]);typename=string(kind[0])
        name=(namespace+'.' if namespace else '')+typename+'$$'+string(method[0])
        rva=address-imagebase;position=bisect.bisect_right(starts,rva)-1
        bounds=functions[position] if position>=0 and functions[position][0]<=rva<functions[position][1] else None
        mapped.append({'Address':address,'Name':name,'metadata_method_index':index,
                       'token':hex(method[5]),'type_index':method[1],
                       'rva':rva,'physical_offset':file_offset(rva),
                       'pdata_function':list(bounds) if bounds else None})
    source_hash=hashlib.sha256(data).hexdigest()
    (OUT/'mscorlib-map.json').write_text(json.dumps({'ScriptMethod':mapped},ensure_ascii=False),encoding='utf-8')
    receipt={'passed':True,'source_game_dll':str(GAME),'game_dll_bytes':len(data),
             'game_dll_sha256':source_hash,'source_metadata':str(META),
             'metadata_sha256':hashlib.sha256(metadata).hexdigest(),
             'image_base':imagebase,'sections':sections,'exception_functions':len(functions),
             'codegen_module':{k:v for k,v in candidate.items() if k!='pointers'},
             'mapped_methods':len(mapped),'unmapped_null_method_pointers':len(selected)-len(mapped),
             'all_nonzero_methods_in_executable_file_sections':True,
             'game_dll_executed':False,'process_memory_read':False,
             'game_private_state_read':False,'mapping_is_behavior_proof':False}
    (OUT/'mscorlib-mapping-verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'mapped':len(mapped),'module':receipt['codegen_module'],
                  'image_base':hex(imagebase),'pdata_functions':len(functions)}))
