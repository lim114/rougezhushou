from pathlib import Path
from hashlib import sha256
import json,importlib.util

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent;SOURCE=ROOT/'.cache/p3-309-boss-lifecycle-research'
visible=json.loads((OUT/'seven-complete-visible-cards.json').read_text(encoding='utf-8'))
data=json.loads((SOURCE/'player-reading-data-candidate.json').read_text(encoding='utf-8'))
original=json.loads((SOURCE/'selected-original-records.json').read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('read_dom_307',ROOT/'scripts/build_choice_annotations_307.py')
dom=importlib.util.module_from_spec(spec);spec.loader.exec_module(dom)
doc=dom.Document((SOURCE/'boss-complete.html').read_text(encoding='utf-8'))
notes=[]
for index,node in enumerate(doc.nodes):
 if node.tag=='span'and'display:none'in node.attrs.get('style','').replace(' ','')and'从灾厄形态'in dom.text(node):
  text=dom.text(node).strip()
  if not any(r['text']==text for r in notes):notes.append({'kind':'document_explanatory_tooltip_not_default_visible_body','text':text,'source_node_ordinal':index,'attributes':node.attrs})
assert len(notes)==1
skill_rows=visible['cards'][:6]
phase_reviews=[]
for phase in data['phases']:
 explicit=[skill['skill_id']for skill,card in zip(data['skills'],skill_rows)if phase['name']in card['documented_mode_labels']]
 phase_reviews.append({'phase_id':phase['phase_id'],'document_name':phase['name'],
  'candidate_skill_ids':phase['skill_ids'],'independently_extracted_explicit_skill_ids':explicit,
  'mapping_matches_complete_header_labels':phase['skill_ids']==explicit,
  'scope':'Only explicitly labelled documentary skills; empty list never proves no abilities or hidden scripts.',
  'candidate_summary_review':'Supported as documentary reading, not an actual mode/current instance claim.'})
assert all(p['mapping_matches_complete_header_labels']for p in phase_reviews)
byid={t['transition_id']:t for t in data['transitions']}
evidence={
 'first_to_calamity1':{'card_index':6,'quote':'被击倒后进行持续3.6秒的重生，回复100%生命值，重生结束时由第一形态进入灾厄形态(一)（或由第二形态进入灾厄形态(二)）并获得最大生命值+50%，攻击力+20%的增益（不会被重生清除）'},
 'calamity1_to_second':{'card_index':0,'quote':'※若技能未被打断，结束时获得1.63秒强制缴械，该强制缴械结束后自身由灾厄形态(一)进入第二形态（或由灾厄形态(二)进入第三形态）'},
 'second_to_calamity2':{'card_index':6,'quote':'被击倒后进行持续3.6秒的重生，回复100%生命值，重生结束时由第一形态进入灾厄形态(一)（或由第二形态进入灾厄形态(二)）并获得最大生命值+50%，攻击力+20%的增益（不会被重生清除）'},
 'calamity2_to_third':{'card_index':0,'quote':'※若技能未被打断，结束时获得1.63秒强制缴械，该强制缴械结束后自身由灾厄形态(一)进入第二形态（或由灾厄形态(二)进入第三形态）'},
 'third_to_calamity2':{'card_index':2,'quote':'技能结束时回到灾厄形态(二)'},
 'third_to_flying':{'card_index':3,'quote':'技能结束时获得近地悬浮并进入飞行形态，15秒内自身无法触发技能【降落】'},
 'flying_to_third':{'card_index':5,'quote':'技能结束时解除近地悬浮，回到第三形态'}}
reviews=[]
for key,record in evidence.items():
 assert record['quote']in visible['cards'][record['card_index']]['complete_visible_effect']
 reviews.append({'transition_id':key,'candidate':byid[key],'evidence':record,
  'condition_and_destination_documented':True,
  'not_rebirth_annotation_source':notes[0]if key in('calamity2_to_third','third_to_calamity2')else None,
  'actual_execution_or_exact_timeline_proven':False})
raw=original['enemy_database_complete_record']['Value'][0]['enemyData']
talents={row['key']:row['value']for row in raw['talentBlackboard']}
fires=[(i,s)for i,s in enumerate(raw['skills'])if s['prefabKey']=='Fire']
fired=[{'raw_skill_index':i,'prefabKey':s['prefabKey'],'cooldown':s['cooldown'],
 'duration_extend':next(b['value']for b in s['blackboard']if b['key']=='duration_extend')}for i,s in fires]
assert {k:talents[k]for k in('reborn_1.max_hp','reborn_1.atk','reborn_2.max_hp','reborn_2.atk')}=={'reborn_1.max_hp':.5,'reborn_1.atk':.2,'reborn_2.max_hp':1.,'reborn_2.atk':.3}
assert all(r['duration_extend']==10. and r['cooldown']==1. for r in fired)
assert len(fires)==2 and sum(s['prefabKey']=='Fireball'for s in raw['skills'])==2
assert '11秒'in visible['cards'][0]['complete_visible_effect']and'（存疑）'in visible['cards'][0]['complete_visible_effect']
assert any('生命值最高的干员'in t for t in original['canonical_enemy_complete']['abilities'])
review={'kind':'SECTION309_FINAL_INDEPENDENT_SOURCE_REVIEW_NOT_RUNTIME_ACCEPTANCE',
 'mode_extraction_error_confirmed':True,'error':'Cutting header at first newline retained skill name but dropped every following bracketed mode label.',
 'correction':'Extract all [] labels from complete ak-card__title subtree, not split first line; crosscheck complete source HTML card and frozen complete_DOM. Do not edit original frozen source record.',
 'phase_skill_reviews':phase_reviews,'transition_reviews':reviews,
 'additional_document_tooltip_notes':notes,
 'difference_field_review':[
  {'difference_id':'second_rebirth_value_basis','all_fields_present_in_complete_raw_record':True,
   'raw_values':{k:talents[k]for k in('reborn_1.max_hp','reborn_1.atk','reborn_2.max_hp','reborn_2.atk')},
   'document_quote':evidence['first_to_calamity1']['quote'],'mutual_incompatibility_proven':False,'base_stacking_execution_semantics_verified':False},
  {'difference_id':'extension_clock_basis','all_fields_present_in_complete_raw_record':True,'raw_Fire_records':fired,
   'document_quote':'消耗1层【延长灾厄】以额外增加11秒持续时间','mutual_incompatibility_proven':False,
   'ten_plus_one_explanation_verified':False,'clock_execution_verified':False},
  {'difference_id':'highest_hp_selection_wording','overview_quote':'选中全场生命值最高的干员',
   'detail_quote':'选择全场范围内最大生命值最高的我方干员 > 自身为主目标',
   'uncertain_clause_quote':'以主目标为中心（存疑）','source_wording_difference_present':True,'actual_target_or_center_verified':False},
  {'difference_id':'raw_mode_index_binding','raw_skill_keys':list(raw['skills'][0]),
   'raw_prefab_keys_in_order':[s['prefabKey']for s in raw['skills']],
   'duplicate_records_present':True,'engine_mode_attachment_or_inheritance_verified':False}],
 'important_nonblocking_corrections':['first.skill_ids=[]仅表示文献技能卡没有第一形态标签，不可显示为没有技能。',
  '第三形态无额外天赋或能力不等于没有共同能力；飞行子形态不应转译为第四条血。',
  '中间形态kind等是阅读分类，不是新增的引擎状态枚举或当前状态识别。',
  '灾厄二与第三不经重生的依据是文献tooltip注释；应标明是说明注而不是默认可见正文。',
  '主目标离场造成中断与时长重设有明确文献；不能据此编造实际重新施放时钟或确定下次目标。'],
 'numeric_use':'All numbers are literal documentary or fixed-field references; no stage stats, damage, countdown, extra HP bars or runtime timing derived.',
 'new_blocking_source_issue_other_than_missing_modes':False,
 'frozen_source_files_unchanged':all(sha256((SOURCE/name).read_bytes()).hexdigest()==pin['sha256']for name,pin in json.loads((SOURCE/'HANDOFF.json').read_text(encoding='utf-8'))['files'].items()),
 'Qt_tests_Git_or_production_executed':False}
p=OUT/'source-review.json';p.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'phase_mappings':len(phase_reviews),'transitions':len(reviews),'difference_reviews':4,'frozen_unchanged':review['frozen_source_files_unchanged'],'sha256':sha256(p.read_bytes()).hexdigest()},ensure_ascii=False))
