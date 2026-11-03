"""Read exact static native/metadata/AB identities, never execute the game."""
from pathlib import Path
import argparse,hashlib,json,mmap,struct,runpy

def verify(artifact_dir,game_dir=None):
    root=Path(artifact_dir);read=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
    proof=read('native-proof.json');metadata=read('selected-metadata.json');receipt=read('receipt.json')
    for name,digest in receipt['artifact_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
    for key in ('game_dll_sha256','metadata_sha256'):assert proof[key]==metadata[key]==receipt[key]
    contract=read('prefab-contract.json');prefabs=read('prefab-binding.json');scripts=read('monoscript-binding.json')
    assert hashlib.sha256((root/'prefab-contract.json').read_bytes()).hexdigest()==receipt['runtime_contract_sha256']
    assert not contract['current_runtime_attachment_verified'] and not contract['current_hotfix_equivalence_proven']
    slots={r['name']:{s['slot']:s for s in r['selected_vtable']} for r in metadata['layouts']}
    assert slots['Torappu.Battle.Ability'][33]['method_index']==63064
    assert slots['Torappu.Battle.Ability'][33]['abstract_declaration_only']
    assert not slots['Torappu.Battle.Ability'][33]['actual_concrete_implementation_verified']
    assert slots['Torappu.Battle.EnemySkill'][18]['method_index']==66310
    assert slots['Torappu.Battle.NeverTrigger'][8]['method_index']==75421
    assert slots['Torappu.Battle.NeverTrigger'][13]['method_index']==75422
    methods={r['method']['metadata_method_index']:r for r in proof['methods']}
    getup={i['address']:(i['mnemonic'],i['operands']) for i in methods[66278]['instructions']}
    assert getup['0x1806df81f'][0]=='jge' and getup['0x1806df82f']==('setge','al')
    initial={i['address']:(i['mnemonic'],i['operands']) for i in methods[66302]['instructions']}
    assert initial['0x1806ddf96']==('mov','dword ptr [rbx + 0x40], 0')
    start={i['address']:i for i in methods[66305]['instructions']}
    assert start['0x1806dd3e3']['target']=='0x1806de840'
    assert start['0x1806dd469']['mnemonic']=='call' and start['0x1806dd46e']['mnemonic']=='je'
    assert start['0x1806dd494']['operands']=='dword ptr [rbx + 0x40]' and start['0x1806dd494']['mnemonic']=='inc'
    assert int(start['0x1806dd3e3']['address'],0)<int(start['0x1806dd469']['address'],0)<int(start['0x1806dd494']['address'],0)
    hashes={}
    for source in scripts['sources']:
        for row in source['monoscripts']:
            data=row['data'];key=bytes(data['m_PropertiesHash']['bytes['+str(i)+']'] for i in range(16)).hex()
            hashes.setdefault(key,[]).append((data['m_Namespace'],data['m_ClassName'],data['m_AssemblyName']))
    component_count=0
    for source in prefabs['sources']:
        for prefab in source['selected_prefabs']:
            key=Path(prefab['asset_path']).stem;om={o['path_id']:o for o in prefab['objects']}
            for component in contract['prefabs'][key]['skills']:
                obj=om[component['path_id']];go=om[component['game_object_id']]
                assert obj['read_exact'] and go['read_exact']
                assert go['data']['m_Name']==component['key'] and obj['data']['m_GameObject']['m_PathID']==go['path_id']
                assert hashes[component['script_properties_hash']]==[('Torappu.Battle','EnemySkill','Assembly-CSharp.dll')]
                assert obj['data']['_maxTriggerTime']==component['max_trigger_time']
                assert obj['data']['_overwriteInitCooldown']==component['initial_cooldown_override']
                if component['trigger_class']=='Torappu.Battle.NeverTrigger':
                    trigger=om[obj['data']['_trigger']['m_PathID']]
                    assert hashes[trigger['properties_hash']]==[('Torappu.Battle','NeverTrigger','Assembly-CSharp.dll')]
                component_count+=1
    assert component_count==receipt['exact_enemy_skill_components']==26
    result={'artifact_consistency':True,'native_file_comparison':'unavailable','bundle_file_comparison':'unavailable',
        'game_dll_executed':False,'process_memory_read':False,'private_state_read':False,
        'current_runtime_attachment_verified':False,'current_hotfix_equivalence_proven':False,
        'native_get_name_icall_execution_verified':False}
    if game_dir is None:return result
    game=Path(game_dir);meta=(game/proof['metadata_relative']).read_bytes()
    assert hashlib.sha256(meta).hexdigest()==proof['metadata_sha256'],'metadata hash'
    with (game/proof['game_dll_relative']).open('rb') as handle,mmap.mmap(handle.fileno(),0,access=mmap.ACCESS_READ) as binary:
        assert hashlib.sha256(binary).hexdigest()==proof['game_dll_sha256'],'DLL hash'
        pe=struct.unpack_from('<I',binary,60)[0];count=struct.unpack_from('<H',binary,pe+6)[0]
        osize=struct.unpack_from('<H',binary,pe+20)[0];base=struct.unpack_from('<Q',binary,pe+48)[0]
        sections=[struct.unpack_from('<IIII',binary,pe+24+osize+n*40+8)[1:] for n in range(count)]
        def offset(address):
            rva=address-base
            for start,size,pos in sections:
                if start<=rva<start+size:return pos+rva-start
            raise AssertionError(('outside file-backed section',hex(address)))
        checked=set()
        for method in proof['methods']:
            assert not method['limits']
            for i in method['instructions']:
                raw=bytes.fromhex(i['bytes']);pos=offset(int(i['address'],0));assert pos==int(i['physical_offset'],0)
                assert binary[pos:pos+len(raw)]==raw,i['address'];checked.add((i['address'],i['bytes']))
        for row in metadata['byte_spans']:
            source=binary if row['source']=='dll' else meta;pos=int(row['physical_offset'],0)
            assert source[pos:pos+row['size']].hex()==row['bytes'],row['reason']
        assert len(checked)==receipt['unique_instruction_checks']
    for source in scripts['sources']:
        path=game/'Arknights_Data'/source['source_relative']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==source['source_sha256'],'MonoScript source identity'
    reader=runpy.run_path(str(root/'read_unity_stdlib.py'));ab=game/'Arknights_Data/StreamingAssets/AB/Windows'
    for source in prefabs['sources']:
        raw=(ab/source['source']).read_bytes()
        assert len(raw)==source['source_bytes'] and hashlib.sha256(raw).hexdigest()==source['source_sha256']
        assert hashlib.md5(raw).hexdigest()==source['source_md5']
        _,files=reader['bundle'](raw);objects={}
        for filename,data in files:
            if '.resS' in filename or '.resource' in filename:continue
            parsed=reader['serialized'](data);objects.update({o['path_id']:o for o in parsed['objects']})
        for prefab in source['selected_prefabs']:
            for expected in prefab['objects']:
                actual=objects[expected['path_id']]
                assert actual.get('read_exact') and actual['class_id']==expected['class_id']
                assert actual['data']==expected['data'],(source['source'],prefab['asset_path'],expected['path_id'])
    result.update(native_file_comparison='passed',unique_instruction_checks=len(checked),
        metadata_and_binding_byte_spans=len(metadata['byte_spans']),bundle_file_comparison='passed',
        checked_bundle_sources=len(prefabs['sources']),checked_skill_components=component_count)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--artifact-dir',default=str(Path(__file__).resolve().parent))
    parser.add_argument('--game-dir');parser.add_argument('--output');args=parser.parse_args()
    output=json.dumps(verify(args.artifact_dir,args.game_dir),ensure_ascii=False,indent=2)+'\n'
    if args.output:Path(args.output).write_text(output,encoding='utf-8',newline='\n')
    print(output,end='')
