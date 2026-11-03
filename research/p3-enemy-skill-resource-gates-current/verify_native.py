"""Verify immutable static bytes only. No execution or current-hook claims."""
from pathlib import Path
import argparse,hashlib,json,mmap,struct

def verify(artifact_dir,game_dir=None):
    root=Path(artifact_dir);read=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
    proof=read('native-proof.json');metadata=read('selected-metadata.json');receipt=read('receipt.json')
    for name,digest in receipt['artifact_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
    for key in ('game_dll_sha256','metadata_sha256'):assert proof[key]==metadata[key]==receipt[key]
    assert not proof['current_hotfix_equivalence_proven'] and not proof['game_dll_executed']
    binding=read('resource-binding.json')
    assert binding['no_hp_epsilon_used'] and not binding['initial_lower_zero_clamp_applied']
    assert not binding['actual_prefab_override_verified'] and not binding['actual_modifier_acceptance_verified']
    methods={row['method']['metadata_method_index']:row for row in proof['methods']}
    gate=methods[220483]['instructions']
    assert [(i['mnemonic'],i['operands']) for i in gate]==[('cmp','rcx, rdx'),('setge','al'),('ret','')]
    assert next(i for i in methods[66310]['instructions'] if i['address']=='0x1806dd7b9')['target']=='0x185ed91b0'
    definitions={row['method_definition_index']:row for row in metadata['methods']}
    assert definitions[66301]['parameters']==[
        {'name':'data','type':'Torappu.LevelData+EnemyData+ESkillData'},
        {'name':'owner','type':'Torappu.Battle.Enemy'}]
    assert definitions[66301]['slot']==15
    assert definitions[220503]['parameters']==[{'name':'value','type':'System.Int32'}]
    assert definitions[220498]['parameters']==[{'name':'value','type':'System.Single'}]
    assert definitions[25973]['parameters']==[{'name':'newPeriod','type':'Torappu.FP'},
        {'name':'waitFirstPeriod','type':'System.Boolean'}]
    layouts={r['name']:{f['name']:(f['offset'],f['type']) for f in r['fields']} for r in metadata['layouts']}
    assert layouts['Torappu.LevelData+EnemyData+ESkillData']['spCost']==(36,'System.Int32')
    assert layouts['Torappu.LevelData+EnemyData+ESkillData']['initCooldown']==(32,'System.Single')
    assert layouts['Torappu.Battle.EnemySkill']['m_spCost']==(60,'System.Int32')
    assert layouts['Torappu.Battle.EnemySkill']['<owner>k__BackingField']==(136,'Torappu.Battle.Enemy')
    assert layouts['Torappu.Battle.Entity']['m_sp']==(80,'Torappu.ObscuredFP')
    assert layouts['Torappu.Battle.Entity']['<maxSp>k__BackingField']==(376,'System.Int32')
    initial={i['address']:(i['mnemonic'],i['operands']) for i in methods[66624]['instructions']}
    assert initial['0x1806f5677']==('cmp','ebx, eax') and initial['0x1806f5679']==('cmovl','eax, ebx')
    assert initial['0x1806f5685']==('cvtdq2ps','xmm1, xmm1')
    assert initial['0x1806f56a7']==('movups','xmmword ptr [rdi + 0x50], xmm1')
    initcd={i['address']:(i['mnemonic'],i['operands']) for i in methods[66302]['instructions']}
    assert initcd['0x1806ddf9d'][0]=='jge'
    result={'artifact_consistency':True,'native_file_comparison':'unavailable','game_dll_executed':False,
        'process_memory_read':False,'private_state_read':False,'current_hotfix_equivalence_proven':False,
        'actual_current_controller_verified':False,'actual_modifier_acceptance_verified':False}
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
        result.update(native_file_comparison='passed',unique_instruction_checks=len(checked),
            metadata_and_binding_byte_spans=len(metadata['byte_spans']))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--artifact-dir',default=str(Path(__file__).resolve().parent))
    parser.add_argument('--game-dir');parser.add_argument('--output');args=parser.parse_args()
    output=json.dumps(verify(args.artifact_dir,args.game_dir),ensure_ascii=False,indent=2)+'\n'
    if args.output:Path(args.output).write_text(output,encoding='utf-8',newline='\n')
    print(output,end='')
