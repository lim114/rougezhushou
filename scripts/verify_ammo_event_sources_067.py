"""Seal native count-event calls and actual counter type/config bindings."""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
DIR=ROOT/'.cache/research/ammo-events-067'
BASE=Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    paths=[ROOT/name for name in (
        '.cache/research/ammo-events-067/count-callback-cfg.json',
        '.cache/research/p1-native-runtime-054/metadata-native-fields.json',
        '.cache/research/p1-native-runtime-054/metadata-attack-055.json',
        '.cache/research/p1-native-runtime-054/monoscripts-public-tpk-055.json',
        '.cache/research/p1-native-runtime-054/selected-ammo-public-prefabs.json',
        '.cache/research/p1-native-runtime-054/selected-ammo-counter-config.json',
        '.cache/research/p1-ammo-independent-055/first-batch-public-prefabs.json',
        '.cache/research/p1-ammo-independent-055/first-batch-contract.json',
        '.cache/research/p1-native-runtime-054/read_metadata_static.py',
        '.cache/research/p1-native-cost-054/extract_cfg.py',
        '.cache/research/p1-angel-s2-055/REPORT.md',
        '.cache/research/p1-angel-s2-055/s2-actual-script-types.json',
        '.cache/research/p1-angel-s2-055/VERIFICATION.json',
        'rouge/ammo_counter.py','rouge/relic_events.py','tests/test_ammo_events_067.py')]
    paths.append(Path(__file__))
    cfg=read(paths[0]);fields=read(paths[1]);events=read(paths[2]);scripts=read(paths[3])
    dll=Path(cfg['source_game_dll']);meta=dll.parent/'Arknights_Data/il2cpp_data/Metadata/global-metadata.dat'
    assert sha(dll)==cfg['dll_sha256']==fields['source_game_dll_sha256']=='6edbc00b11e016c8935bbc45f158d5363f63d35038b0a69f8297612235e533ce'
    assert sha(meta)==cfg['metadata_sha256']==fields['source_metadata_sha256']=='ee7f1239e1cff67620a7964d651189dbb5c98e13699169096be2a907fd541118'
    with dll.open('rb') as stream:
        for method in cfg['methods']:
            assert method['cfg_bounded_traversal_finished'] and not method['limits']
            for row in method['instructions']:
                stream.seek(int(row['physical_offset'],16))
                assert stream.read(len(bytes.fromhex(row['bytes']))).hex()==row['bytes']
    ins={x['address']:x for m in cfg['methods'] for x in m['instructions']}
    assertions={
        '0x180f521e9':('cmp','edi, dword ptr [rbx + 0x20]'),
        '0x180f521ee':('movzx','ebp, byte ptr [rbx + 0x5c]'),
        '0x180f52253':('cmp','edi, dword ptr [rbx + 0x20]'),
        '0x180f52258':('cmp','byte ptr [rbx + 0x5b], 0'),
        '0x180f52291':('movzx','eax, byte ptr [rbx + 0x33]'),
        '0x180f522a6':('mov','ecx, 0x10'),
        '0x180f522ab':('mov','rdx, rbx'),
        '0x180f522ae':('call','0x180005840'),
        '0x18000586d':('mov','r8, qword ptr [rax + rdx*8 + 0x138]'),
        '0x180005887':('jmp','r8'),
        '0x180f517fa':('mov','byte ptr [rbx + 0x5b], 1'),
        '0x180f51830':('add','eax, edi'),
        '0x180f51837':('mov','dword ptr [rbx + 0x48], eax'),
        '0x180f51a8f':('cmp','byte ptr [rbx + 0x59], cl'),
        '0x180f51a94':('xor','eax, eax'),
        '0x180f51a9c':('mov','eax, dword ptr [rbx + 0x2c]'),
        '0x180f522c1':('mov','dword ptr [rbx + 0x59], 0'),
        '0x180f52329':('xor','edx, edx'),
        '0x180f5232b':('mov','word ptr [rbx + 0x59], 0'),
        '0x180f52334':('mov','byte ptr [rbx + 0x5b], 0'),
        '0x180f51f29':('mov','byte ptr [rbx + 0x5c], 0'),
    }
    for address,pair in assertions.items():assert (ins[address]['mnemonic'],ins[address]['operands'])==pair,address
    counter=next(t for t in fields['selected'] if t['name']=='Torappu.Battle.Abilities.AbilityEventCounter')
    assert next(v['method'] for v in counter['vtable'] if v['slot']==16).endswith('$$DealCountEvent')
    offsets={f['name']:f['offset'] for f in counter['fields']}
    for name,offset in {'_countEvent':32,'_expendPerTrigger':44,'_ignoreTriggerOnce':51,
        'm_eventCount':72,'m_notCountNext':89,'m_triggerOnce':91,'m_ignoreCountEventUntilCastEnd':92}.items():
        assert offsets[name]==offset
    enum=next(t for t in events['selected'] if t['name']=='Torappu.Battle.AbilityStandard+Event')
    enum={f['name']:f['default']['value'] for f in enum['fields'] if f.get('default')}
    assert {k:enum[k] for k in ('ON_DETACHED','ON_CAST_END','ON_SPELL_ON','ON_SPELL_END','ON_ATTACK_FINISH')}=={
        'ON_DETACHED':1,'ON_CAST_END':3,'ON_SPELL_ON':4,'ON_SPELL_END':5,'ON_ATTACK_FINISH':6}
    byhash={}
    for source in scripts['sources']:
        assert sha(Path(source['source_path']))==source['source_sha256']
        for obj in source['monoscripts']:
            assert obj['read_exact']
            digest=bytes(obj['data']['m_PropertiesHash']['bytes['+str(i)+']'] for i in range(16)).hex()
            byhash.setdefault(digest,[]).append(obj['data'])
    public=read(paths[4])['sources']+read(paths[6])['sources']
    configs=read(paths[5])['counters']+read(paths[7])['counters']
    bindings={('kaltsit',2):['char_1052_kalts2/Modes/s2/Body/Attack'],
        ('mechanist',1):['char_4230_mcnist/Modes/S1/Body/Attack'],
        ('char_1035_wisdel',3):['char_1035_wisdel/Modes/S3/Body/Attack/MainAttack'],
        ('char_1041_angel2',1):['char_1041_angel2/Modes/S1/Body/Attack'],
        ('char_1041_angel2',2):['char_1041_angel2/Modes/S2/Body/Attack','char_1041_angel2/Modes/S2_Down/Body/Attack'],
        ('char_1041_angel2',3):['char_1041_angel2/Modes/S3/Body/Attack/Common','char_1041_angel2/Modes/S3_Down/Body/Attack/Common']}
    from rouge.ammo_counter import _CONSUMPTION_BINDINGS
    assert set(bindings)==set(_CONSUMPTION_BINDINGS)
    checks=[]
    for binding,hierarchies in bindings.items():
        for hierarchy in hierarchies:
            config=next(x for x in configs if x['hierarchy']==hierarchy)
            source=next(x for x in public if x['source_name']==config['source_name'])
            assert sha(BASE/source['source_name'])==source['source_sha256']==config['source_sha256']
            serial=next(f['serialized'] for f in source['files'] if any(o['path_id']==config['path_id'] for o in f['serialized']['objects']))
            obj=next(o for o in serial['objects'] if o['path_id']==config['path_id'])
            assert obj['read_exact'] and obj['data']==config['counter_data']
            h=serial['types'][obj['type_index']]['old_type_hash']
            matches=byhash[h];assert len(matches)==1
            assert matches[0]['m_ClassName']=='AbilityEventCounter' and matches[0]['m_Namespace']=='Torappu.Battle.Abilities'
            data=obj['data']
            value=(data['_countEvent'],data['_expendPerTrigger'],bool(data['_ignoreTriggerOnce']),bool(data['_resetWhenAttackFinished']))
            assert value==_CONSUMPTION_BINDINGS[binding]
            checks.append({'operator':binding[0],'skill':binding[1],'hierarchy':hierarchy,
                'source_name':source['source_name'],'source_sha256':source['source_sha256'],
                'component_path_id':obj['path_id'],'unique_type_hash':h,'binding':value})
    result={'passed':True,'dll_sha256':sha(dll),'metadata_sha256':sha(meta),
        'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
        'complete_native_methods':len(cfg['methods']),
        'instructions_checked':sum(m['instruction_count'] for m in cfg['methods']),
        'native_count_callback_slot':16,'configuration_bindings':checks,
        'bound_skills':len(bindings),'verified_component_instances':len(checks),
        'prior_missing_count_dispatch_resolved':True,'numeric_formula_changes':False,
        'full_ability_event_producer_timeline_proven':False,'special_refill_paths_enabled':False,
        'current_hotfix_equivalence_proven':False,'file_only':True,
        'dll_executed':False,'game_process_memory_read':False}
    (DIR/'native-proof.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','configuration_bindings')}))


if __name__=='__main__':main()
