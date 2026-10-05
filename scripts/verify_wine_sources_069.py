"""Seal the bounded wine S1 source research; no numerical model is changed."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.cache/research/phatm2-s1-069'
BASE=Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    config=read(OUT/'skill-prefabs.json');manifest=read(BASE/'hot_update_list.json')
    item=next(e for e in manifest['abInfos'] if e['name']==config['source_name'])
    raw=(BASE/config['source_name']).read_bytes()
    assert config['base_version']==manifest['versionId']=='26-08-16-14-00-43_415873'
    assert len(raw)==item['abSize']==config['source_bytes']
    assert hashlib.md5(raw).hexdigest()==item['md5']==config['source_md5']
    assert hashlib.sha256(raw).hexdigest()==config['source_sha256']
    assert all(s['object_count']==s['read_exact_count'] for s in config['parse_stats'])
    prefab=config['selected_prefabs'];assert len(prefab)==1
    prefab=prefab[0];assert prefab['asset_path'].endswith('/skchr_phatm2_1.prefab')
    attack=next(o for o in prefab['objects'] if o['path_id']==1442620349020702503)
    script=read(ROOT/'.cache/research/p1-native-runtime-054/monoscripts-public-tpk-055.json')
    bindings={}
    for src in script['sources']:
        for row in src['monoscripts']:
            d=row['data'];h=bytes(d['m_PropertiesHash'][f'bytes[{i}]'] for i in range(16)).hex()
            bindings.setdefault(h,set()).add((d['m_Namespace']+'.'+d['m_ClassName']).strip('.'))
    h=prefab['types'][attack['type_index']]['old_type_hash']
    assert h=='3b48c5e1f0d3c2bebcc7b66d81f8193d'
    assert bindings[h]=={'Torappu.Battle.Abilities.MultiMeleeAttack'}
    expected={'_waitForAttackEvent':1,'_interuptIfTargetDead':0,'_additionalTimes':1,
        '_waitAttackEventForAllAttacks':0,'_maxAnimScale':1.0,'_animKey':'Skill_1',
        '_triggerDelta':0.4000000059604645,'_minPostDelay':0.0,'_refreshTimesOnCastStart':0,
        '_refreshTimesOnCheckAnotherSpell':0}
    for key,value in expected.items():assert attack['data'][key]==value,(key,attack['data'].get(key))
    metadata=read(OUT/'reproduced-metadata.json')
    fields={t['name']:{f['name']:f['offset'] for f in t['fields']} for t in metadata['selected']}
    assert fields['Torappu.Battle.Abilities.MultiMeleeAttack']['m_triggerDelta']==0x240
    assert fields['Torappu.Battle.Abilities.AbstractAnimatedAbility']['m_animScale']==0x1b0
    assert fields['Torappu.Battle.Abilities.EasyToStartAbility']['m_cachedDuration']==0x118
    assert fields['Torappu.Battle.Abilities.EasyToStartAbility']['m_realStartTime']==0x128
    keys=[row['literal'] for row in metadata['literal_keys']]
    assert 'times' in keys and 'hit_interval' in keys
    op=read(ROOT/'rouge/data/catalog.json')['operators']['char_1042_phatm2']
    assert op['skills'][0]['id']=='skchr_phatm2_1'
    assert all(level['values']['times']==2 and 'hit_interval' not in level['values'] for level in op['skills'][0]['levels'])
    cfgs=sorted(OUT.glob('*-cfg.json'));count=0;methods=0
    assert len(cfgs)==6
    first=read(cfgs[0]);dll=Path(first['source_game_dll'])
    meta=dll.parent/'Arknights_Data/il2cpp_data/Metadata/global-metadata.dat'
    dh,mh=sha(dll),sha(meta)
    assert metadata['source_game_dll_sha256']==dh and metadata['source_metadata_sha256']==mh
    for p in cfgs:
        cfg=read(p);assert cfg['dll_sha256']==dh and cfg['metadata_sha256']==mh
        with dll.open('rb') as f:
            for method in cfg['methods']:
                assert method['cfg_bounded_traversal_finished'] and not method['limits']
                methods+=1
                for row in method['instructions']:
                    data=bytes.fromhex(row['bytes']);f.seek(int(row['physical_offset'],16))
                    assert f.read(len(data))==data;count+=1
    paths=[*cfgs,*[p for p in OUT.glob('*.py')],OUT/'reproduced-metadata.json',
        OUT/'skill-prefabs.json',ROOT/'rouge/data/catalog.json',Path(__file__),
        ROOT/'.cache/research/p1-native-runtime-054/monoscripts-public-tpk-055.json',
        ROOT/'.cache/research/p1-native-runtime-054/read_metadata_static.py',
        ROOT/'.cache/research/p1-runtime-source-054/read_unity_stdlib.py',
        ROOT/'.cache/research/p1-native-cost-054/extract_cfg.py']
    proof={'passed':True,'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
        'bundle_sha256':config['source_sha256'],'parsed_objects':sum(s['object_count'] for s in config['parse_stats']),
        'native_methods_verified':methods,'native_instructions_verified':count,
        'dll_sha256':dh,'metadata_sha256':mh,'prefab_type':next(iter(bindings[h])),
        'prefab_settings':expected,'documented_relative_wait':'max(1, round_even(float32(triggerDelta * animScale) / deltaPlayTime)) fixed yields',
        'numerical_model_changed':False,'full_skill_lifecycle_verified':False,
        'current_hotfix_equivalence_proven':False,'live_panel_pair_verified':False,
        'game_actions':0,'process_memory_read':False,'private_state_read':False}
    (OUT/'native-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in proof.items() if k not in ('source_sha256','prefab_settings')},ensure_ascii=False))

if __name__=='__main__':main()
