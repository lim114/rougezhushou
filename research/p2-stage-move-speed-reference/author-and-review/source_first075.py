from pathlib import Path
import subprocess,tarfile,io,hashlib,json,datetime,urllib.request,collections
base=Path(__file__).parent;root=Path('/workspace/rougezhushou')
commit='dbf1e698f56cbba03793ed13769a9f6dae2c5ff6'
snapshot=base/'baseline';snapshot.mkdir(exist_ok=True)
paths=['rouge','scripts/build_previews.py','scripts/build_battle_previews_039.py','scripts/build_battle_references_040.py',
       'research/p2-enemy-rune-selectors','research/p2-aglna-manual-weight','research/p2-environment-and-lifecycle']
status=subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).splitlines()
data=subprocess.check_output(['git','archive',commit,*paths],cwd=root)
with tarfile.open(fileobj=io.BytesIO(data)) as archive:archive.extractall(snapshot,filter='data')
files={str(p.relative_to(snapshot)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(snapshot.rglob('*')) if p.is_file()}
freeze={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_commit':commit,'method':'git archive exact committed public paths',
        'snapshot_includes_root_wip':False,'root_wip_at_observation':status,'file_count':len(files),'files':files}
(base/'baseline-freeze075.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n')
battle=json.loads((snapshot/'rouge/data/battle-previews.json').read_bytes())
normal=battle['stages']['ro6_n_3_6'];emergency=battle['stages']['ro6_e_3_6'];source=emergency['level_source']
path=base/'level_rogue6_3-6.json'
if not path.exists():
    request=urllib.request.Request(source['url'],headers={'User-Agent':'rouge-source-audit'})
    with urllib.request.urlopen(request,timeout=30) as response:
        raw=response.read();status_code=response.status
    path.write_bytes(raw)
else:raw=path.read_bytes();status_code='existing public fixed file reused'
assert len(raw)==source['bytes'] and hashlib.sha256(raw).hexdigest()==source['sha256']
level=json.loads(raw)
assert emergency['runes']==normal['runes']==level['runes']
assert emergency['movement_multiplier']==normal['movement_multiplier']==level['options']['moveMultiplier']==.5
selected=level['runes'][0]
assert selected=={'difficultyMask':'FOUR_STAR','key':'enemy_attribute_mul','professionMask':1023,'buildableMask':'ALL',
    'blackboard':[{'key':'atk','value':1.2,'valueStr':None},{'key':'max_hp','value':1.5,'valueStr':None},{'key':'move_speed','value':1.5,'valueStr':None}]}
assert emergency['difficulty']=='FOUR_STAR' and normal['difficulty']=='NORMAL'
inventory=[]
for sid,stage in battle['stages'].items():
    for index,rune in enumerate(stage['runes']):
        for bi,row in enumerate(rune['blackboard'] or []):
            if rune['key']=='enemy_attribute_mul' and row['key']=='move_speed':
                inventory.append({'stage_id':sid,'stage_difficulty':stage['difficulty'],'rune_index':index,'bb_index':bi,
                    'difficulty_mask':rune['difficultyMask'],'difficulty_mask_matches':rune['difficultyMask'] in ('ALL',stage['difficulty']),
                    'complete_raw_rune':rune,'level_source':stage['level_source']})
assert len(inventory)==2 and sum(i['difficulty_mask_matches'] for i in inventory)==1
search=[];hits=[]
needles=('enemy_attribute_mul','enemy_attackradius_mul','RuneEnemyAttribute','EnemyAttributeRune','RuneEnemyMove','act27sisde_enemy_global_buff')
for p in sorted((root/'.cache/research').rglob('*')):
    if not p.is_file() or p.suffix not in ('.txt','.json','.md'):continue
    content=p.read_bytes();search.append({'path':str(p),'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)})
    text=content.decode(errors='replace')
    for n in needles:
        if n in text:hits.append({'path':str(p),'needle':n,'count':text.count(n)})
fields=json.loads((root/'.cache/research/summon-limit-069/verified-native-fields.json').read_bytes())
enum=[t for t in fields if any(f['name']=='MOVE_SPEED' for f in t.get('fields',[]))]
assert len(enum)==1
row=next(f for f in enum[0]['fields'] if f['name']=='MOVE_SPEED')
sourcefiles=['rouge/spawn_reference.py','rouge/battle_preview.py','rouge/enemy_environment.py','rouge/data/battle-previews.json',
             'rouge/data/previews.json','research/p2-enemy-rune-selectors/RESEARCH.md','research/p2-aglna-manual-weight/NOTE.md',
             'research/p2-environment-and-lifecycle/RESEARCH.md']
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_repository_commit':commit,
    'raw_stage_source':{**source,'path':str(path),'status':status_code,'proxy_and_tls_defaults_preserved':True},
    'precise_parameter_selector':'$.runes[0].blackboard[2]','raw_rune_complete':selected,
    'precise_stage_option_selector':'$.options.moveMultiplier','stage_option_parameter':.5,
    'all_105_stage_runes_scanned_for_this_literal_field':True,'movement_rune_inventory':inventory,
    'native_attribute_enum':{'type':enum[0]['name'],'complete_move_speed_field':row,
        'source_path':str(root/'.cache/research/summon-limit-069/verified-native-fields.json'),
        'source_sha256':hashlib.sha256((root/'.cache/research/summon-limit-069/verified-native-fields.json').read_bytes()).hexdigest(),
        'does_not_prove_enemy_rune_blackboard_writer_or_layer':True},
    'existing_parsed_native_search':{'needles':needles,'files':search,'count':len(search),'hits':hits,
        'scope':'current existing parsed public cache only; no binary acquisition or full-current-client proof'},
    'source_files':{name:files[name] for name in sourcefiles},
    'conclusion':{'old_partial_product_base_times_stage_speed_is_not_an_effective_speed_claim':True,
        'missing_selected_stage_move_speed_parameter_reference':True,
        'raw_parameter_1_5_confirmed':True,'native_rune_target_writer_layer_verified':False,
        'stage_times_rune_compound_speed_verified':False,'full_effective_move_speed_verified':False},
    'narrow_permitted_scope':'bind this exact raw movement parameter to existing selected-stage partial movement reference, qualify raw difficulty mask; preserve old subtotal and effective speed unknown; no new numerical composition',
    'deferred':['native enemy_attribute_mul move_speed writer/target/layer; obtain exact retained/public method body or configuration binding before any math',
                '5_1 enemy_attackradius_mul and remaining env/global scripts; obtain exact body/target/lifecycle, unchanged'],
    'no_tracked_edits':True,'no_private_state_reads_or_resets':True,'no_wine_or_gui_or_native_binary_downloads':True}
(base/'source-receipt075.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print({'commit':commit,'baseline_files':len(files),'raw_stage_sha256':source['sha256'],'source_status':status_code,
       'rune_records':len(inventory),'matched_rune_records':sum(i['difficulty_mask_matches'] for i in inventory),
       'native_files':len(search),'specific_native_hits':hits,'move_speed_enum_type':enum[0]['name'],'enum_default':row['default']})
