"""Verify SUM-Y's exact token modifier against pinned public files."""
import hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'.cache/research/summon-068'
BASE=Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    paths=[DIR/'read_equips.py',DIR/'deepcl-equip-prefabs.json',
        ROOT/'.cache/research/p1-runtime-source-054/read_unity_stdlib.py',
        ROOT/'.cache/research/p1-native-runtime-054/monoscripts-public-tpk-055.json',
        ROOT/'.cache/research/p1-native-runtime-054/metadata-native-fields.json',
        ROOT/'.cache/game-data/battle_equip_table.json',
        ROOT/'.cache/research/relic-panel-056/REPORT.md',
        ROOT/'.cache/research/relic-panel-056/native-evidence.json',
        ROOT/'.cache/research/sp-attributes-066/sp-application-cfg.json',
        ROOT/'.cache/research/attribute-boundaries-065/attribute-range-cfg.json',Path(__file__)]
    prefab=read(paths[1]);manifest=read(BASE/'hot_update_list.json')
    entry=next(e for e in manifest['abInfos'] if e['name']==prefab['source_name'])
    raw=(BASE/prefab['source_name']).read_bytes()
    assert manifest['versionId']==prefab['base_version']=='26-08-16-14-00-43_415873'
    assert len(raw)==entry['abSize']==prefab['source_bytes']
    assert hashlib.md5(raw).hexdigest()==entry['md5']==prefab['source_md5']
    assert hashlib.sha256(raw).hexdigest()==prefab['source_sha256']
    assert all(s['object_count']==s['read_exact_count'] for s in prefab['parse_stats'])
    scripts=read(paths[3]);types={}
    for source in scripts['sources']:
        for obj in source['monoscripts']:
            d=obj['data'];h=bytes(d['m_PropertiesHash'][f'bytes[{i}]'] for i in range(16)).hex()
            types.setdefault(h,set()).add((d['m_Namespace']+'.'+d['m_ClassName']).strip('.'))
    table=read(paths[5])['uniequip_002_deepcl'];bindings=[]
    for stage,value in ((2,.1),(3,.15)):
        part=next(p for p in table['phases'][stage-1]['parts'] if p['isToken'])
        assert part['target']=='TALENT'
        candidate=part['addOrOverrideTalentDataBundle']['candidates'][0]
        assert candidate['prefabKey']=='10' and candidate['blackboard']==[{'key':'max_hp','value':value,'valueStr':None}]
        p=next(p for p in prefab['selected_prefabs'] if p['asset_path'].endswith('/'+part['resKey']+'.prefab'))
        components=[o for o in p['objects'] if o['class_id']==114]
        passive=next(o for o in components if '_buffs' in o['data'])
        loader=next(o for o in components if '_overwriteTalentKey' in o['data'])
        assert loader['data']['_overwriteTalentKey']=='10'
        names={}
        for kind,obj in [('passive',passive),('talent',loader)]:
            names[kind]=sorted(types[p['types'][obj['type_index']]['old_type_hash']])
            assert len(names[kind])==1
        assert names['passive']==['Torappu.Battle.Abilities.PassiveBuffAbility']
        assert names['talent']==['Torappu.Battle.Talent']
        assert passive['data']['_selector']['m_PathID']==0
        buff=passive['data']['_buffs'][0]
        assert len(passive['data']['_buffs'])==1 and buff['templateKey']=='empty'
        assert buff['disableOverride']==1 and buff['maxStackCnt']==1 and buff['lifeTimeType']==2
        assert buff['attributes']['attributeModifiers']==[{'attributeType':0,'formulaItem':1,
            'value':0.0,'loadFromBlackboard':1,'fetchBaseValueFromSourceEntity':0}]
        bindings.append({'stage':stage,'value':value,'resource':part['resKey'],'token':True,
            'component_id':passive['path_id'],'types':names,'modifier':buff['attributes']['attributeModifiers'][0]})
    metadata=read(paths[4])
    for typename,key,value in [('Torappu.AttributeType','MAX_HP',0),
        ('Torappu.AttributeModifierData+AttributeModifier+FormulaItemType','MULTIPLIER',1)]:
        t=next(t for t in metadata['selected'] if t['name']==typename)
        assert next(f['default']['value'] for f in t['fields'] if f['name']==key)==value
    cfgs=[read(p) for p in paths[8:10]];dll=Path(cfgs[0]['source_game_dll'])
    meta=dll.parent/'Arknights_Data/il2cpp_data/Metadata/global-metadata.dat'
    dh,mh=sha(dll),sha(meta);count=0
    for cfg in cfgs:
        assert cfg['dll_sha256']==dh==metadata['source_game_dll_sha256']
        assert cfg['metadata_sha256']==mh==metadata['source_metadata_sha256']
        with dll.open('rb') as f:
            for method in cfg['methods']:
                assert method['cfg_bounded_traversal_finished'] and not method['limits']
                for row in method['instructions']:
                    data=bytes.fromhex(row['bytes']);f.seek(int(row['physical_offset'],16));assert f.read(len(data))==data
                    count+=1
    proof={'passed':True,'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
        'bundle_sha256':prefab['source_sha256'],'parsed_objects':sum(s['object_count'] for s in prefab['parse_stats']),
        'bindings':bindings,'native_instructions_verified':count,'dll_sha256':dh,'metadata_sha256':mh,
        'formula':'round_even(rune_adjusted_token_hp) * max(0, 1 + ordinary_hp_pct + module_hp_pct)',
        'ordinary_layer_evidence_reused':True,'concurrent_limit_verified':False,
        'current_hotfix_equivalence_proven':False,'live_panel_pair_verified':False,
        'game_actions':0,'process_memory_read':False,'private_state_read':False}
    (DIR/'native-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in proof.items() if k not in ('source_sha256','bindings')}))

if __name__=='__main__':main()
