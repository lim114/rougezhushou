"""Audit saved public evidence; optionally compare the exact installed static files.

No DLL loading, process memory, game interaction or private runtime state.
Without --game-dir, only artifact integrity/contract consistency is checked.
"""
from pathlib import Path
import argparse,hashlib,json,struct

HERE=Path(__file__).resolve().parent
def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(name):return json.loads((HERE/name).read_text(encoding='utf8'))
def check(condition,label):
    if not condition:raise ValueError(label)
def verify(contract_path,game_dir=None):
    proof=read('native-proof.json');metadata=read('selected-metadata.json');receipt=read('receipt.json')
    manifest=read('artifact-manifest.json')
    for name,expected in manifest['files_sha256'].items():
        check(Path(name).name==name,'artifact filename must be local')
        check(digest(HERE/name)==expected,'artifact checksum mismatch: '+name)
    check(digest(contract_path)==receipt['contract_sha256'],'runtime contract checksum mismatch')
    contract=json.loads(contract_path.read_text(encoding='utf8'))
    expected={m['name']:m for key in ('methods','initialization_methods') for m in contract['native_evidence'][key]}
    check(len(expected)==len(proof['methods'])==10,'expected ten selected native methods')
    unique=set();total=0
    for method in proof['methods']:
        info=method['method'];row=expected[info['Name']]
        check(not method['limits'] and method['cfg_bounded_traversal_finished'],'incomplete direct CFG')
        instructions=method['instructions'];raw=b''.join(bytes.fromhex(i['bytes']) for i in instructions)
        check(len(instructions)==row['instructions']==method['instruction_count'],'instruction count mismatch')
        check(hashlib.sha256(raw).hexdigest()==row['reachable_bytes_sha256']==method['reachable_bytes_sha256'],'reachable byte digest mismatch')
        check(int(row['address'],16)==info['Address'],'method address mismatch')
        check(len(raw)==method['reachable_instruction_bytes'],'reachable byte size mismatch')
        total+=len(instructions)
        for i in instructions:unique.add((i['physical_offset'],i['bytes']))
    check(total==len(unique)==863,'expected 863 selected unique instructions')
    check(proof['game_dll_sha256']==metadata['game_dll_sha256']==receipt['dll_sha256']==contract['native_evidence']['dll_sha256'],'DLL version binding mismatch')
    check(proof['metadata_sha256']==metadata['metadata_sha256']==receipt['metadata_sha256']==contract['native_evidence']['metadata_sha256'],'metadata version binding mismatch')
    check(metadata['type_definition_bytes']==92 and not metadata['unknown_type_definition_uint32_offset64_interpreted'],'type layout scope mismatch')
    spans={(s['file'],s['physical_offset'],len(bytes.fromhex(s['bytes']))):bytes.fromhex(s['bytes']) for s in metadata['byte_bindings']}
    def bound(row):return spans[(row['file'],row['physical_offset'],row['size'])]
    def name(row):return bound(row).rstrip(b'\0').decode('utf8')
    layouts={t['name']:t for t in metadata['selected']}
    check(len(layouts)==6,'expected six selected field layouts')
    for t in layouts.values():
        definition=struct.unpack('<IIiiiiiIiiiiiiiiI8HII',bound(t['metadata_type_binding']))
        check(len(t['fields'])==definition[19],'field count mismatch')
        for index,f in enumerate(t['fields']):
            raw=struct.unpack('<IiI',bound(f['metadata_field_binding']))
            check(f['field_index']==definition[8]+index and raw[1]==f['native_type_index'],'field range/type-index mismatch')
            check(name(f['name_binding'])==f['name'],'field name mismatch')
            if 'offset_binding' in f:check(struct.unpack('<i',bound(f['offset_binding']))[0]==f['offset'],'field offset mismatch')
            if 'default_value_binding' in f:
                dr=struct.unpack('<iii',bound(f['default_record_binding']))
                check(dr[0]==f['field_index'] and dr[2]==f['default']['data_index'],'enum default record mismatch')
                check(bound(f['default_value_binding']).hex()==f['default']['raw'],'enum default raw mismatch')
                kind=(struct.unpack('<QI',bound(f['default_native_type_binding']))[1]>>16)&255
                encoded=bound(f['default_value_binding'])
                check(kind==8 and len(encoded)==1 and encoded[0]<128,'selected enum default shape differs from verified Int32 form')
                value=-(encoded[0]//2+1) if encoded[0]&1 else encoded[0]//2
                check(value==f['default']['value'],'enum default decoded value mismatch')
    bindings={m['name']:m for m in metadata['selected_methods']}
    for m in proof['methods']:
        info=m['method'];b=bindings[info['Name']];raw=struct.unpack('<IiiiiI4H',bound(b['method_binding']))
        check(raw[1]==info['type_index'] and raw[5]==int(info['token'],16),'method metadata identity mismatch')
        check(name(b['name_binding'])==info['Name'].split('$$')[-1],'method metadata name mismatch')
    fields={key:{f['name']:f for f in value['fields']} for key,value in layouts.items()}
    check(fields['Torappu.EnemyDatabase+EnemyData']['spData']['offset']==contract['native_evidence']['source_sp_offset']==168,'source SP offset mismatch')
    check(fields['Torappu.LevelData+EnemyData']['spData']['offset']==contract['native_evidence']['computed_sp_offset']==120,'computed SP offset mismatch')
    for field,expected_offset in (('maxChargeTime',32),('spCost',52),('initSp',72),('increment',92)):
        check(fields['Torappu.SpData'][field]['offset']==expected_offset,'runtime scalar offset mismatch')
    enums={f['name']:f['default']['value'] for f in layouts['Torappu.SpType']['fields'] if f['default']}
    check(enums==contract['rules']['initialization']['sp_types'],'SP enum contract mismatch')
    native='not_requested';physical=0
    if game_dir is not None:
        dll=game_dir/proof['game_dll_relative'];meta=game_dir/proof['metadata_relative']
        check(digest(dll)==proof['game_dll_sha256'],'installed DLL SHA mismatch; this evidence has a different baseline')
        check(digest(meta)==proof['metadata_sha256'],'installed metadata SHA mismatch; this evidence has a different baseline')
        with dll.open('rb') as code,meta.open('rb') as data:
            for m in proof['methods']:
                for i in m['instructions']:
                    raw=bytes.fromhex(i['bytes']);code.seek(int(i['physical_offset'],16))
                    check(code.read(len(raw))==raw,'physical instruction mismatch '+i['address']);physical+=1
            for s in metadata['byte_bindings']:
                stream=code if s['file']=='dll' else data;raw=bytes.fromhex(s['bytes']);stream.seek(s['physical_offset'])
                check(stream.read(len(raw))==raw,'selected metadata/field-offset byte mismatch')
        native='passed'
    return {'public_artifact_consistency':'passed','native_static_file_comparison':native,
        'methods':10,'selected_instructions':total,'physical_instructions_rechecked':physical,
        'selected_metadata_byte_spans':len(metadata['byte_bindings']),
        'current_hotfix_equivalence_proven':False,'runtime_controller_verified':False,
        'game_dll_executed':False,'process_memory_read':False,'private_state_read':False,
        'limits':['Saved direct CFG and field byte bindings do not establish runtime hook activation or dynamic indirect-call semantics.',
            'Without --game-dir, no comparison with an installed DLL/metadata is claimed.']}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract',type=Path,default=HERE.parents[1]/'rouge/data/enemy-sp-inheritance-reference.json')
    parser.add_argument('--game-dir',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=verify(args.contract,args.game_dir)
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:args.output.write_text(text+'\n',encoding='utf8')
    print(text)
if __name__=='__main__':main()
