"""Verify bounded source receipts and every captured DLL instruction; --replay rebuilds this batch only."""
from pathlib import Path
import argparse,hashlib,json,mmap,subprocess,sys
OUT=Path(__file__).resolve().parent;RESEARCH=OUT.parent
parser=argparse.ArgumentParser();parser.add_argument('--replay',action='store_true');args=parser.parse_args()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
cfgs=sorted(OUT.glob('*-cfg.json'))
if args.replay:
 for path in cfgs:
  command=[sys.executable,str(OUT/'extract_cfg.py'),'--output',path.stem]
  names=[];addresses=[]
  for method in read(path)['methods']:
   name=method['method']['Name']
   if name.startswith('unmapped_'):addresses.append(hex(method['method']['Address']))
   elif name not in names:names.append(name)
  for name in names:command+=['--name',name]
  for address in addresses:command+=['--address',address]
  subprocess.run(command,check=True,capture_output=True)
 for name in ['read_metadata.py','read_global_ep_scale.py','read_s1_buff_template.py']:
  subprocess.run([sys.executable,str(OUT/name)],check=True,capture_output=True)
verification=read(RESEARCH/'p1-native-mapping-054/mapping-verification.json')
mapping_path=RESEARCH/'p1-native-mapping-054/script.json';mapping=read(mapping_path)['ScriptMethod']
game=Path(verification['source_game_dll']);metadata=read(OUT/'metadata.json')
assert metadata['dll_executed'] is False and metadata['process_memory_read'] is False
assert metadata['source_game_dll_sha256']==verification['game_dll_sha256']
assert metadata['source_metadata_sha256']==verification['metadata_sha256']
types={row['name']:row for row in metadata['selected']}
def field(type_name,name,offset):
 assert next(x for x in types[type_name]['fields'] if x['name']==name)['offset']==offset
def slot(type_name,index,name):
 assert next(x for x in types[type_name]['vtable'] if x['slot']==index)['method']==name
def enum(type_name,name,value):
 assert next(x for x in types[type_name]['fields'] if x['name']==name)['default']['value']==value
enum('Torappu.Battle.DamageType','MAGICAL',2);enum('Torappu.Battle.ElementType','SANITY',1)
enum('Torappu.Battle.AbilityStandard+Event','ON_SPELL_ON',4)
enum('Torappu.Battle.UnitDataFlowConfig+DataType','TALENT',0);enum('Torappu.Battle.UnitDataFlowConfig+DataType','SKILL',1)
enum('Torappu.Battle.UnitDataFlowConfig+ModifyType','ASSIGN',0);enum('Torappu.Battle.UnitDataFlowConfig+FormulaType','TWO',0)
for index,name in [(27,'Torappu.Battle.Abilities.MultiMeleeAttack$$DoSetData'),(81,'Torappu.Battle.AbilityStandard$$OnSpellStart'),(106,'Torappu.Battle.Abilities.AbstractAnimatedAbility$$CreateDamageNode'),(108,'Torappu.Battle.Abilities.AbstractAnimatedAbility$$CreateElementDamageNode')]:slot('Torappu.Battle.Abilities.MultiMeleeAttack',index,name)
slot('Torappu.Battle.ReplacementSkillFixed',51,'Torappu.Battle.NextAttackOrCombatSkill$$AssignData')
for name in ['Torappu.Battle.Entity','Torappu.Battle.Character','Torappu.Battle.Enemy']:slot(name,132,'Torappu.Battle.Entity$$OnTakeEPDamage')
for name in ['ApplyDamage','ApplyElementDamage']:slot('Torappu.Battle.Action.Nodes+'+name,6,'Torappu.Battle.Action.Nodes+'+name+'$$Execute')
field('Torappu.Battle.Character','m_dataFlowConfig',0x478)
field('Torappu.Battle.Abilities.AbstractBasicAttack','m_actions',0x1f8)
field('Torappu.Battle.Abilities.AbstractAnimatedAbility','m_epDamageNode',0x1c0)
field('Torappu.Battle.Action.Nodes+ApplyElementDamage','m_epDamageRatio',0x68)
field('Torappu.Battle.Action.Nodes+ApplyElementDamage','m_epDamageScale',0x70)
field('Torappu.Battle.Buff','m_blackboard',0xb8)
skill_path=RESEARCH/'phatm2-s1-069/skill-prefabs.json';skill=read(skill_path)
assert sha(skill_path)=='f1aea1bb843ace8f65f244e69eac9f7362a98067e7efc6912ddf6d214a476ecd'
prefab=next(x for x in skill['selected_prefabs'] if x['asset_path'].endswith('/skchr_phatm2_1.prefab'))
ability=next(x for x in prefab['objects'] if x['path_id']==1442620349020702503)
assert ability['read_exact']
for key,value in {'_damageType':2,'_extraDamageType':0,'_elementDamageType':1,'_epDamageRatio':0.0,'_splitDamage':0,'_attackType':1,'_atkScale':1.0,'_atkScaleKey':'atk_scale'}.items():assert ability['data'][key]==value
active=ability['data']['_activeBuffs'];assert len(active)==1
assert active[0]['templateKey']=='phatm2_s_1[unmove]' and active[0]['durationKey']=='unmove'
character_path=RESEARCH/'phatm2-s1-069/character-prefabs.json';character=read(character_path)
assert sha(character_path)=='b6da07ba588d57a68a203e51679270a601620a39a359d82ae15a07dc45925660'
serial=character['sources'][0]['files'][0]['serialized']
dataflow=next(x for x in serial['objects'] if x['path_id']==2090084769798240522)
assert dataflow['read_exact'] and serial['types'][dataflow['type_index']]['old_type_hash']=='93998a60fc75d8c5eae26c6cf07a393f'
config=dataflow['data']['_config'];assert len(config)==1
for key,value in {'_formulaType':0,'_acceptEmptyBB':0,'_validateSkillIndices':1,'_skillIndices':[0],'_source':0,'_sourceTalentKey':'1','_sourceKey':'attack@ep_damage_ratio','_target':1,'_targetKey':'ep_damage_ratio','_overrideRangeId':0,'_type':0}.items():assert config[0][key]==value
scripts=read(RESEARCH/'p1-native-runtime-054/monoscripts-public-tpk-055.json');matches=[]
for source in scripts['sources']:
 for row in source['monoscripts']:
  d=row['data'];h=d.get('m_PropertiesHash',{})
  if h and bytes(h['bytes['+str(i)+']'] for i in range(16)).hex()=='93998a60fc75d8c5eae26c6cf07a393f':matches.append(d)
assert len(matches)==1 and matches[0]['m_ClassName']=='UnitDataFlowConfig' and matches[0]['m_Namespace']=='Torappu.Battle'
template=read(OUT/'s1-unmove-template.json');items=template['matches'][0]['template']['eventToActions']['_items']
assert len(items)==1 and items[0]['key']==68
nodes=json.loads(items[0]['value']['SerializedState']);assert len(nodes)==1
assert nodes[0]=={'_filterElementType':True,'_elementType':'SANITY','_filterApplyWay':False,'_applyWayFilter':'NONE','_isOneMinus':False,'_isStackable':False,'_isValidStackCnt':False,'$type':'Torappu.Battle.Action.Nodes+EpDamageScale'}
public_base=Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')
for source in [skill,character['sources'][0],template,read(OUT/'global-ep-scale-prefab.json')]:assert sha(public_base/source['source_name'])==source['source_sha256']
all_cfgs=cfgs+[RESEARCH/'phatm2-actions-070'/name for name in ['action-entry.json','run-actions.json','apply-actions.json']]
all_mapping=mapping+read(RESEARCH/'p1-native-runtime-054/supplement-map.json')['ScriptMethod']+read(RESEARCH/'p1-native-cost-054/helper-map.json')['ScriptMethod']
ins_by_address={};checked=[]
with game.open('rb') as file,mmap.mmap(file.fileno(),0,access=mmap.ACCESS_READ) as binary:
 assert hashlib.sha256(binary).hexdigest()==verification['game_dll_sha256']
 for path in all_cfgs:
  cfg=read(path)
  assert cfg['dll_sha256']==verification['game_dll_sha256'] and cfg['mapping_sha256']==sha(mapping_path)
  assert cfg['file_only'] and cfg['game_dll_executed'] is False and cfg['process_memory_read'] is False and cfg['current_hotfix_equivalence_proven'] is False
  for method in cfg['methods']:
   assert method['limits']==[] and method['cfg_bounded_traversal_finished']
   assert len(method['instructions'])==method['instruction_count']
   raw_code=b''.join(bytes.fromhex(i['bytes']) for i in method['instructions'])
   assert len(raw_code)==method['reachable_instruction_bytes'] and hashlib.sha256(raw_code).hexdigest()==method['reachable_bytes_sha256']
   m=method['method']
   if m['metadata_method_index'] is not None:assert any(x['Address']==m['Address'] and x['Name']==m['Name'] and x['metadata_method_index']==m['metadata_method_index'] for x in all_mapping)
   for ins in method['instructions']:
    offset=int(ins['physical_offset'],0);raw=bytes.fromhex(ins['bytes'])
    assert binary[offset:offset+len(raw)]==raw,(path,ins['address'])
    ins_by_address[ins['address']]=ins
    for ref in ins.get('rip_data',[]):
     address=int(ref['address'],0);rva=address-verification['image_base']
     s=next(s for s in verification['sections'] if s['rva']<=rva<s['rva']+s['raw_size'])
     physical=s['offset']+rva-s['rva'];assert binary[physical:physical+8].hex()==ref['bytes8']
   checked.append({'cfg':path.relative_to(RESEARCH).as_posix(),'method':method['method']['Name'],'address':hex(method['method']['Address']),'instructions':method['instruction_count'],'reachable_bytes_sha256':method['reachable_bytes_sha256']})
anchors=[]
def anchor(address,mnemonic,operand_fragment=None,target=None):
 row=ins_by_address[address];assert row['mnemonic']==mnemonic
 if operand_fragment is not None:assert operand_fragment in row['operands'],(address,row)
 if target is not None:assert row['target']==target
 anchors.append({'address':address,'mnemonic':mnemonic,'operands':row['operands'],'target':row.get('target')})
for address,target in [('0x180a11403','0x180ac6c40'),('0x180a117fd','0x180ac6990'),('0x180ac1fd9','0x182310c70'),('0x180ac360c','0x18230f270'),('0x18096338a','0x18091a1c0'),('0x18091a4ec','0x1823110f0'),('0x18091a7e4','0x1805ea280'),('0x180e7b59a','0x18230fed0'),('0x180ec7b2c','0x18102c5f0'),('0x180ec71aa','0x18102dce0'),('0x180e7b75f','0x18053c2c0'),('0x180e7b7ee','0x18053c2c0'),('0x180e7b827','0x18053c2c0'),('0x18102c23f','0x1806fd120'),('0x18102d9b2','0x1806fd120'),('0x1806fd810','0x18070ce70'),('0x180707d95','0x180685e40'),('0x1806860f7','0x1806939e0'),('0x180693a7a','0x180699360'),('0x18069967b','0x181155c10'),('0x181036e03','0x1823100d0'),('0x181036f24','0x186312770'),('0x181036f33','0x1808a3fc0'),('0x18102d160','0x180664700'),('0x18066477d','0x18070ea30')]:anchor(address,'call',target=target)
for address,mnemonic,operand in [('0x180e8c9c2','cmp','edi, 4'),('0x180e8c9d4','mov','[rbx + 0x1f8]'),('0x180e7b7fa','mov','ecx, 0x6c'),('0x1810c6023','mov','al, 1'),('0x181155169','mov','al, 1'),('0x180693a69','mov','r8d, 0x44'),('0x18070d107','mov','ecx, 0x84'),('0x18070d116','call','0x180005890'),('0x181155d7a','inc',None)]:anchor(address,mnemonic,operand)
literals=metadata['encoded_references'];assert any(x.get('literal')=='ep_damage_scale' and x['instruction']=='0x181036dea' for x in literals)
proof={'batch':'0.70 P2 phatm2 S1 damage action static closure','file_only':True,'game_dll_executed':False,'process_memory_read':False,'private_files_read':False,'current_hotfix_equivalence_proven':False,'source_game_dll_sha256':verification['game_dll_sha256'],'source_metadata_sha256':metadata['source_metadata_sha256'],'mapping_sha256':sha(mapping_path),'actual_ability_path_id':ability['path_id'],'actual_unit_dataflow_path_id':dataflow['path_id'],'unit_dataflow_config':config[0],'actual_unmove_template':template['matches'][0],'native_anchors':anchors,'verified_methods':checked,'method_count':len(checked),'instruction_count':sum(x['instructions'] for x in checked),'own_method_count':sum(x['cfg'].startswith('phatm2-damage-070/') for x in checked),'own_instruction_count':sum(x['instructions'] for x in checked if x['cfg'].startswith('phatm2-damage-070/')),'scope_conclusions':['Actual S1 native action list is ApplyDamage, AlwaysNext, ApplyElementDamage when selected talent attack ratio is positive.','Life-damage modifier submission precedes direct SANITY modifier submission in each synchronous ON_SPELL_ON action pass.','Talent 1 attack@ep_damage_ratio is copied to skill 0 ep_damage_ratio through UnitDataFlowConfig and actual ReplacementSkillFixed AssignData inheritance.','Direct SANITY uses current source atk times ep_damage_ratio; its base is separate from MAGICAL final life damage and skill atk_scale.','Actual S1 unmove template binds event 68 to EpDamageScale: received SANITY modifier value is multiplied by buff blackboard ep_damage_scale.'],'remaining_boundaries':['No current XLua/hotfix equivalence.','Node/callback ordering is native synchronous dispatch evidence, not a live game trace or global tick scheduling proof.','AbilityAttachment.Apply interface dispatch and eventual Buff initialization/blackboard copy are not fully expanded here; actual S1 template binding and skill scalar source are established, but first-hit buff attachment success/refresh interaction is not independently proved by this batch.','Target death, immunity, cancellation, burst, splash talent, rounding and unrelated callbacks are outside this bounded closure.'],'inputs':{str(p.relative_to(RESEARCH)):sha(p) for p in [skill_path,character_path,OUT/'metadata.json',OUT/'s1-unmove-template.json',OUT/'global-ep-scale-prefab.json',RESEARCH/'p1-native-runtime-054/monoscripts-public-tpk-055.json']}}
(OUT/'native-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'verified':True,'method_count':proof['method_count'],'instruction_count':proof['instruction_count'],'own_method_count':proof['own_method_count'],'own_instruction_count':proof['own_instruction_count'],'native_anchors':len(anchors),'replayed':args.replay,'game_dll_executed':False,'process_memory_read':False},ensure_ascii=False))
