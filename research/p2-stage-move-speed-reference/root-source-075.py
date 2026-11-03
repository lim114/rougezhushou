import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from rouge.battle_preview import battle_data,enemy_preview

p=Path('/workspace/.continuation/p2-stage-move-speed-075/level_rogue6_3-6.json');b=p.read_bytes()
expected='2d2e89306c3d3c4a2a6c21f71b3828f66cb7a7996ab149faaad043d4867e8296'
assert len(b)==233958 and hashlib.sha256(b).hexdigest()==expected
raw=json.loads(b);stages=battle_data()['stages'];assert len(stages)==105
matches=[]
for sid,stage in stages.items():
    found=[r for r in stage.get('runes',[]) if r.get('key')=='enemy_attribute_mul' and any(x.get('key')=='move_speed' for x in r.get('blackboard',[]))]
    if found:matches.append(sid)
assert sorted(matches)==['ro6_e_3_6','ro6_n_3_6']
for sid in matches:
    stage=stages[sid];assert stage['runes']==raw['runes']
    assert stage['movement_multiplier']==raw['options']['moveMultiplier']==.5
    source=stage['level_source'];assert source['sha256']==expected and source['bytes']==len(b)
    assert source['url']=='https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/levels/obt/roguelike/ro6/level_rogue6_3-6.json'
stage=stages['ro6_e_3_6'];assert stage['difficulty']=='FOUR_STAR'
rune=raw['runes'][0];assert (rune['key'],rune['difficultyMask'],rune['professionMask'],rune['buildableMask'])==('enemy_attribute_mul','FOUR_STAR',1023,'ALL')
assert rune['blackboard'][2]=={'key':'move_speed','value':1.5,'valueStr':None}
count=0
for entry in stage['enemies']:
    result=enemy_preview(stage['id'],entry['id'],entry['level']);m=result['movement_reference'];r=m['stage_move_speed_rune_reference']
    assert r['source']==stage['level_source'] and r['source_selector']=='$.runes[0].blackboard[2]' and r['parameter']==1.5
    assert r['combined_with_stage_multiplier_speed'] is None and r['native_target_writer_layer_verified'] is False and m['complete_effective_speed_verified'] is False
    if m['base_attribute'] is not None:assert m['base_times_stage_speed']==m['base_attribute']*.5
    count+=1
print(json.dumps({'section':75,'passed':True,'original_sha256':expected,'original_bytes':len(b),'all_stage_variants_checked':105,'two_source_records_full_runes_verified':matches,'exact_selected_enemy_references':count,'raw_parameter':1.5,'old_stage_multiplier':.5,'numerical_rune_composition_applied':False,'native_target_writer_layer_verified':False,'private_or_live_state_used':False},ensure_ascii=False))
