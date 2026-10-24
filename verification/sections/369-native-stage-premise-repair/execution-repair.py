from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from rouge import current_boss_documents as model,current_battle_reference as battle
p=R/'scripts/verify_current_boss_documents_window_369.py';raw=p.read_bytes();s=raw.decode('utf8')
packet=model.packet();related=model.related_entities(model.reference('ro6_b_4','0'),'0')
assert [(r['key'],r['entity_id'])for r in related]==[('1','enemy_2146_cadesd'),('2','enemy_2137_shsdgo')]
independent=[]
for level_key,level in packet['data']['originals']['levels'].items():
 for index,ref in enumerate(level['enemyDbRefs']):
  if ref['id']in('enemy_2146_cadesd_2','enemy_2146_cadesd_3'):
   independent.append({'level_key':level_key,'key':str(index),'id':ref['id'],'useDb':ref['useDb'],'raw_binding':ref})
assert [(r['level_key'],r['key'],r['id'],r['useDb'])for r in independent]==[('levels/obt/roguelike/ro6/level_rogue6_b-4-b.json','7','enemy_2146_cadesd_2',False),('levels/obt/roguelike/ro6/level_rogue6_b-4-b.json','8','enemy_2146_cadesd_3',False)]
old="""                    requests=[r for r in model.related_entities(panel.result,'0')if r['entity_id']in('enemy_2146_cadesd_2','enemy_2146_cadesd_3')]
                    require(len(requests)==2,'both_independent_hunt_related_entities_kept_without_DB_alias')
                    for request in requests:
                        row=open_exact('ro6_b_4','0');choose(panel.related,request);old_dialog=dialog;QTest.mouseClick(panel.related_button,Qt.MouseButton.LeftButton);gui.processEvents()
                        require(battle_panel.enemy_key==request['key']and not old_dialog.isVisible()and battle_panel.boss_documents_button.isHidden(),'independent_hunt_entity_opens_only_exact_current_enemy_without_alias_document');related_readings.append({'source_stage':'ro6_b_4','request':request,'actual_selected_key':battle_panel.enemy_key,'complete_document_available':False})"""
new="""                    requests=model.related_entities(panel.result,'0')
                    require([(r['key'],r['entity_id'])for r in requests]==[('1','enemy_2146_cadesd'),('2','enemy_2137_shsdgo')],'hunt_related_entities_match_real_same_stage_references_and_exclude_other_variant_independent_entities')
                    for request in requests:
                        row=open_exact('ro6_b_4','0');choose(panel.related,request);old_dialog=dialog;QTest.mouseClick(panel.related_button,Qt.MouseButton.LeftButton);gui.processEvents()
                        supported=model.target_available('ro6_b_4',request['key'])
                        selected=next(e for e in battle_panel.result['enemies']if e['key']==request['key'])
                        binding=base['data']['originals']['levels'][battle_panel.result['level_key']]['enemyDbRefs'][int(request['key'])]
                        require(battle_panel.stage_id=='ro6_b_4'and battle_panel.enemy_key==request['key']and battle_panel.enemy_combo.currentData()==request['key']and selected['id']==request['entity_id']and selected['raw_binding']==binding and not old_dialog.isVisible()and battle_panel.boss_documents_button.isVisible()==supported,'same_stage_hunt_entity_opens_exact_current_enemy_with_document_only_when_qualified');related_readings.append({'source_stage':'ro6_b_4','request':request,'actual_selected_key':battle_panel.enemy_key,'complete_document_available':supported})"""
assert s.count(old)==1;s=s.replace(old,new)
old="""                        open_battle(sid);select_parent_enemy(battle_panel.result['enemies'][0]['key']);require(battle_panel.boss_documents_button.isHidden(),'unsupported_pursuit_or_DLC1_same_name_stage_has_no_migrated_entry')"""
new=old+"""
                        if sid=='ro6_b_4_b':
                            original=base['data']['originals']['levels'][battle_panel.result['level_key']]
                            for key,entity_id in(('7','enemy_2146_cadesd_2'),('8','enemy_2146_cadesd_3')):
                                binding=original['enemyDbRefs'][int(key)];select_parent_enemy(key)
                                selected=next(e for e in battle_panel.result['enemies']if e['key']==key)
                                comparison=next(e for e in base['data']['database_comparison']if e['enemy_id']==entity_id)
                                require(binding['id']==entity_id and binding['useDb']is False and selected['id']==entity_id and selected['raw_binding']==binding and comparison['independent_level_entity']is True and comparison['database_record_present']is False and comparison['substitution_permitted']is False,'both_original_independent_hunt_entities_retained_in_actual_variant_without_DB_alias')
                                require(battle_panel.stage_id==sid and battle_panel.enemy_key==key and battle_panel.enemy_combo.currentData()==key and battle_panel.boss_documents_button.isHidden()and model.reference(sid,key)is None,'unmigrated_independent_variant_ordinary_enemy_selectable_without_borrowed_mechanism_entry')
                                independent_readings.append({'stage_id':sid,'level_key':battle_panel.result['level_key'],'key':key,'enemy_id':entity_id,'useDb':binding['useDb'],'raw_binding':deepcopy(binding),'database_record_present':False,'complete_document_available':False,'selected_via_ordinary_current_enemy_control':True})"""
assert s.count(old)==1;s=s.replace(old,new)
old='source_failures=[];related_readings=[];dialog_close_observations=[]'
assert s.count(old)==1;s=s.replace(old,'source_failures=[];related_readings=[];independent_readings=[];dialog_close_observations=[]')
old="'actual_related_readings':related_readings,'same_identity_refresh_observations'"
assert s.count(old)==1;s=s.replace(old,"'actual_related_readings':related_readings,'actual_unmigrated_independent_readings':independent_readings,'same_identity_refresh_observations'")
ast.parse(s)
out=R/'verification/sections/369-native-stage-premise-repair';out.mkdir()
(out/'before-verify_current_boss_documents_window_369.py').write_bytes(raw)
p.write_text(s,encoding='utf8',newline='\n')
record={'section':369,'actual_failed_native_receipt':'verification/sections/369-native-attempt2/actual/window.json','actual_failed_native_exit':1,'actual_error':'wrong test premise: independent hunt entities required in ro6_b_4 instead of their actual ro6_b_4_b variant','real_same_stage_related_entities':related,'real_independent_entities':independent,'correction':['test exact current ro6_b_4 related pain and proto bindings, retaining qualified versus unqualified mechanism distinction','add exact ordinary selection of independent keys7/8 in actual ro6_b_4_b, no DB substitution or migrated mechanism entry','keep all other original scenario checks, original budget and seven images'],'product_model_or_parameters_changed':False,'unavailable_full_documents_added':False,'prior_70_require_AST_proof_scope':'previous reference/schema repair only; this stage-premise correction intentionally replaces two invalid assertions and adds two independent-variant assertions','native_budget_unchanged_ms':180000,'before_sha256':sha256(raw).hexdigest(),'after_sha256':sha256(p.read_bytes()).hexdigest(),'necessary_rerun_required_for_changed_selected_harness_hash':True,'at_utc':datetime.now(timezone.utc).isoformat()}
(out/'repair-scope.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(out/'execution-repair.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'harness_wrong_stage_premise_corrected_not_validated':True,'same_stage_related_keys':['1','2'],'independent_variant':'ro6_b_4_b','independent_keys':['7','8'],'product_unchanged':True}))
