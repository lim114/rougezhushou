"""Verify bounded wine first-event evidence from public disk files only.

CFG_REQUESTS is the reproduction recipe: pass each address as --address to
.cache/research/p1-native-cost-054/extract_cfg.py and use --output
../phatm2-first-event-070/<key>. Then rerun read_metadata.py and this file.
"""
import hashlib,json,struct
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
OLD=OUT.parent/'phatm2-s1-069'
BASE=Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')
CFG_REQUESTS={
 'event-cfg':['0x18061f140','0x18061f220','0x180624780','0x18070eb70','0x180ed36c0','0x180ed3920','0x180ed3d10','0x180ed3cb0'],
 'event-wait-cfg':['0x180663640','0x180aaacd0','0x180aaad90','0x180aa7050','0x180aa6f00','0x180ed71d0'],
 'frame-order-cfg':['0x1805fee80','0x180620ca0','0x180625270','0x180624d20','0x18063b320','0x180aaa7a0'],
 'late-tick-cfg':['0x1808c3310','0x180aa9850'],
 'predicate-cfg':['0x180708060','0x18066e6f0'],
 'schedule-cfg':['0x1805e4ee0','0x180629cf0','0x180615cb0','0x180615d40','0x1808c3140','0x180a0b8b0'],
 'start-cfg':['0x1805e5c10','0x180669f00','0x180e91340','0x180e91470','0x180ec8150','0x180ed3800'],
 'wait-attack-cfg':['0x18066a060','0x180e7b950','0x180ec8bf0','0x180ec77b0','0x180e928e0','0x180ed6a00','0x18066cdd0'],
}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 old=read(OLD/'native-proof.json');assert old['passed']
 art=read(OUT/'art.json');manifest=read(BASE/'hot_update_list.json')
 assert art['installed_base_version']==manifest['versionId']=='26-08-16-14-00-43_415873'
 item=next(x for x in manifest['abInfos'] if x['name']==art['source_name'])
 raw=(BASE/art['source_name']).read_bytes()
 assert art['source_name']=='chararts/char_1042_phatm2.ab'
 assert len(raw)==item['abSize']==art['source_bytes']==7160299
 assert hashlib.md5(raw).hexdigest()==item['md5']=='79f60304324db3d1712aa855f3ce176b'
 assert hashlib.sha256(raw).hexdigest()==art['source_sha256']=='f8a5ddfd7a326194225d09ccaf54585da2ba882fa9e072d3d4e3ca7d83b2e766'
 assert not art['dll_executed'] and not art['process_memory_read'] and not art['private_state_read']
 f=art['files'][0];assert f['objects']==100 and f['read_exact']==97 and len(f['components'])==27
 assert all(c['read_exact'] for c in f['components'])
 components={c['path_id']:c for c in f['components']}
 scripts=read(ROOT/'.cache/research/p1-native-runtime-054/monoscripts-public-tpk-055.json')
 bindings={}
 for src in scripts['sources']:
  for row in src['monoscripts']:
   d=row['data'];h=bytes(d['m_PropertiesHash'][f'bytes[{i}]'] for i in range(16)).hex()
   bindings.setdefault(h,set()).add((d['m_Namespace']+'.'+d['m_ClassName']).strip('.'))
 expected_types={20:'Torappu.Battle.CharacterAnimator',19:'Spine.Unity.SkeletonAnimation',14:'Spine.Unity.SkeletonDataAsset'}
 for index,name in expected_types.items():assert bindings[f['types'][index]['old_type_hash']]=={name}
 path='dyn/battle/prefabs/skins/character/char_1042_phatm2/defaultskin.prefab'
 container=next(c for c in f['assetbundle'][0]['data']['m_Container'] if c['first']==path)
 root_id=container['second']['asset']['m_PathID'];assert root_id==-7456859797188275225
 animator=components[5395107965992408039]['data'];assert animator['m_GameObject']['m_PathID']==root_id
 animation=next(x for x in animator['_animations'] if x['animKey']=='Skill_1')
 assert animation=={'animKey':'Skill_1','animName':'Skill_1','loop':0,'speed':1.0,'ignoreMissing':1}
 library=read(ROOT/'rouge/data/original-animation-references.json')
 assert library['source_commit']=='d0b5af0b004b044d322397ce5ae79632b6d9fcdd' and library['fps']==30
 wine=next(o for o in library['operators'].values() if o['id']=='char_1042_phatm2')
 assets={r['path_id']:r for r in f['textassets']};refs=[]
 expected_ids={'Front':(997924176756249575,-1841130023594453041,-1005696099493026627),
               'Back':(8116843474029482983,-4082353809600318584,7761050131639854937)}
 for orientation,(skeleton_id,data_id,text_id) in expected_ids.items():
  assert animator['_'+orientation.lower()]['skeleton']['m_PathID']==skeleton_id
  skeleton=components[skeleton_id];assert skeleton['type_index']==19
  assert skeleton['data']['skeletonDataAsset']['m_PathID']==data_id
  data=components[data_id];assert data['type_index']==14
  assert data['data']['skeletonJSON']['m_PathID']==text_id
  for k in ['skeletonDataModifiers','fromAnimation','toAnimation']:assert data['data'][k]==[]
  r=next(r for r in wine['records'] if r['orientation']==orientation and r['animation']=='Skill_1')
  original=ROOT/f'.cache/research/timing-048/char_1042_phatm2-{orientation}.skel'
  assert sha(original)==assets[text_id]['sha256']==r['source']['sha256']
  assert original.stat().st_size==assets[text_id]['bytes']==r['source']['bytes']
  assert len(r['events'])==1 and r['events'][0]['name']=='OnAttack' and r['events'][0]['seconds']==0.5
  assert r['events'][0]['representation_normalized_frames_30hz']==15
  assert r['duration']['representation_normalized_frames_30hz']==48
  assert struct.pack('<f',r['duration']['seconds'])==struct.pack('<f',1.6)
  refs.append({'orientation':orientation,'asset_id':text_id,'sha256':assets[text_id]['sha256'],
               'on_attack_seconds':0.5,'animation_seconds_float32':r['duration']['seconds'],
               'resource_event_frames':15,'resource_animation_frames':48})
 config=read(OLD/'skill-prefabs.json');assert config['source_sha256']==old['bundle_sha256']
 prefab=config['selected_prefabs'][0]
 attack=next(o for o in prefab['objects'] if o['path_id']==1442620349020702503)['data']
 for k,v in {'_timeMode':0,'_cooldownKey':'duration','_animKey':'Skill_1','_downAnimKey':'',
             '_upAnimKey':'','_maxAnimScale':1.0,'_waitForAttackEvent':1,
             '_waitAttackEventForAllAttacks':0,'_interuptIfTargetDead':0,
             '_triggerDelta':0.4000000059604645}.items():assert attack[k]==v,(k,attack.get(k))
 metadata=read(OUT/'metadata.json');types={t['name']:t for t in metadata['selected']}
 fields={name:{f['name']:f for f in t['fields']} for name,t in types.items()}
 assert fields['Torappu.Battle.Entity+Event']['ON_ATTACK_EVENT']['default']['value']==19
 assert fields['Torappu.Battle.Abilities.AbstractAnimatedAbility+TimeMode']['FROM_ATTACK_SPEED']['default']['value']==0
 assert fields['Torappu.Battle.Abilities.AbstractAnimatedAbility']['m_animScale']['offset']==0x1b0
 assert fields['Torappu.Battle.Abilities.AbstractAnimatedAbility']['m_animScale']['type']=='System.Single'
 assert fields['Torappu.Battle.Abilities.AbstractAnimatedAbility']['m_attackTime']['offset']==0x1a8
 assert fields['Torappu.Battle.Abilities.EasyToStartAbility']['m_receivedEvent']['offset']==0x120
 assert fields['Torappu.Battle.CoroutineSimulator+RuntimeHandler+Routine']['firstTouch']['offset']==0x10
 assert fields['Torappu.Battle.BattleController']['m_globalBuffs']['offset']==0x68
 def slot(name,n):return next(r for r in types[name]['vtable'] if r['slot']==n)['method']
 assert slot('Torappu.Battle.Character',28)=='Torappu.Battle.Unit$$OnLateTick'
 assert slot('Torappu.Battle.Character',161)=='Torappu.Battle.Character$$get_animator'
 assert slot('Torappu.Battle.CharacterAnimator',30)=='Torappu.Battle.CharacterAnimator$$OnTick'
 assert slot('Torappu.Battle.CharacterAnimator',27)=='Torappu.Battle.SpineAnimator$$UpdateTimeScale'
 method_addresses={m['name']:m['address'] for t in types.values() for m in t['methods']}
 assert method_addresses['Torappu.Battle.AsyncUtil+<WaitWhileForFixedSeconds>d__6$$MoveNext']=='0x18066e6f0'
 literals=metadata['literal_references']
 assert any(r['method']=='Torappu.Battle.SpineAnimator$$_OnEvent' and r['value']=='OnAttack' for r in literals)
 assert any(r['value']=='Torappu.Battle.Abilities.EasyToStartAbility$$_OnReceiveEvent' for r in literals)
 assert any(r['value']=='Torappu.Battle.SpineAnimator$$_OnEvent' for r in literals)
 cfgs=[OUT/(key+'.json') for key in CFG_REQUESTS]
 first=read(cfgs[0]);dll=Path(first['source_game_dll'])
 native_metadata=dll.parent/'Arknights_Data/il2cpp_data/Metadata/global-metadata.dat'
 dh,mh=sha(dll),sha(native_metadata)
 assert dh==old['dll_sha256']==metadata['source_game_dll_sha256']
 assert mh==old['metadata_sha256']==metadata['source_metadata_sha256']
 count=0;methods=0;ins={}
 for p in cfgs:
  c=read(p);assert c['dll_sha256']==dh and c['metadata_sha256']==mh
  assert {hex(m['method']['Address']) for m in c['methods']}==set(CFG_REQUESTS[p.stem])
  with dll.open('rb') as stream:
   for m in c['methods']:
    assert m['cfg_bounded_traversal_finished'] and not m['limits'];methods+=1
    for i in m['instructions']:
     b=bytes.fromhex(i['bytes']);stream.seek(int(i['physical_offset'],16))
     assert stream.read(len(b))==b;count+=1;ins[i['address']]=i
 # Exact verified call sites and virtual dispatch offsets establishing the late animation chain.
 def instruction(address,mnemonic,operands):
  r=ins[address];assert r['mnemonic']==mnemonic and r['operands']==operands,(address,r)
 instruction('0x18063bc9f','call','0x180669f00')
 instruction('0x18063bd40','call','0x1808c3310')
 instruction('0x1808c349e','mov','r9, qword ptr [r8 + 0x2f8]')
 instruction('0x1808c34ac','call','r9')
 instruction('0x180aa98d0','mov','rax, qword ptr [rdx + 0xb48]')
 instruction('0x180aa9928','mov','rax, qword ptr [r8 + 0x318]')
 instruction('0x180aa9936','call','rax')
 instruction('0x180625442','call','0x185d144b0')
 instruction('0x18066e80a','call','rax')
 instruction('0x180ed3d53','mov','byte ptr [rbx + 0x120], 1')
 instruction('0x180ec8e38','call','0x18070eb70')
 instruction('0x18070ecfc','jmp','0x180663640')
 instruction('0x180ec77ef','mov','rax, qword ptr [rbx + 0x1a8]')
 paths=[*cfgs,*OUT.glob('*-cfg.txt'),*OUT.glob('*.py'),OUT/'metadata.json',OUT/'art.json',OUT/'REPORT.md',
        OLD/'native-proof.json',OLD/'skill-prefabs.json',OLD/'scale-cast-cfg.json',OLD/'wait-cfg.json',
        OLD/'delta-iterator-cfg.json',OLD/'float-round-cfg.json',
        ROOT/'rouge/data/original-animation-references.json',
        ROOT/'.cache/research/timing-048/char_1042_phatm2-Front.skel',
        ROOT/'.cache/research/timing-048/char_1042_phatm2-Back.skel',
        ROOT/'.cache/research/p1-native-runtime-054/monoscripts-public-tpk-055.json',
        ROOT/'.cache/research/p1-native-runtime-054/read_metadata_static.py',
        ROOT/'.cache/research/p1-runtime-source-054/read_unity_stdlib.py',
        ROOT/'.cache/research/p1-native-cost-054/extract_cfg.py']
 assert all(p.exists() for p in paths)
 for p in [OLD/'skill-prefabs.json',OLD/'scale-cast-cfg.json',OLD/'wait-cfg.json',
           OLD/'delta-iterator-cfg.json',OLD/'float-round-cfg.json']:
  assert sha(p)==old['source_sha256'][p.relative_to(ROOT).as_posix()]
 proof={'passed':True,'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
        'dll_sha256':dh,'metadata_sha256':mh,'art_bundle_sha256':art['source_sha256'],
        'native_methods_verified':methods,'native_instructions_verified':count,
        'generic_art_objects_read_exact':97,'art_objects':100,'monobehaviours_read_exact':27,
        'base_original_prefab_animation_binding_proven':True,'base_original_references':refs,
        'default_native_event_id':19,'default_native_order':'CoroutineSimulator.SimulateTick before Unit.OnLateTick -> CharacterAnimator.OnTick -> SkeletonAnimation.Update',
        'raw_duration_source':'FROM_ATTACK_SPEED -> Entity.attackTime -> FP attack interval, not rounded cadence or blackboard duration',
        'anim_scale_type':'float32; FP.AsFloat divided by animation duration, clamped 0.1..1 for actual S1 prefab',
        'normal_nested_iterator_bridge_extra_ticks':0,
        'first_touch_immediate_false_scheduler_boundary_exists':True,
        'exact_first_damage_frame_proven':False,'uniform_extra_first_frame_proven':False,
        'actual_skin_binding_proven':False,'bake_muzzle_actual_validity_proven':False,
        'current_hotfix_equivalence_proven':False,'full_skill_lifecycle_verified':False,
        'numerical_model_changed':False,'game_dll_executed':False,'game_actions':0,
        'process_memory_read':False,'private_state_read':False,'chat_messages_sent':0}
 (OUT/'proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in proof.items() if k not in ['source_sha256','base_original_references']},ensure_ascii=False))
if __name__=='__main__':main()
