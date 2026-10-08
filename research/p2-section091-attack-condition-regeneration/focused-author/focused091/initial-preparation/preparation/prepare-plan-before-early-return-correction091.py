"""Source-only plan generation from frozen91 author packets; no product imports."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
UI=Path('/workspace/.continuation/p2-continuous-attack-controls-091-ui-candidate')
DEEP=Path('/workspace/.continuation/p2-section091-deepcolor-regeneration-notes-author')
def sha(b):return hashlib.sha256(b).hexdigest()
def f(p):return {'source_path':str(p),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
def save(name,obj):
    p=HERE/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n');return f(p)

expected={
 'rouge/app.py':UI/'candidate/rouge/app.py',
 'scripts/verify_damage_ui.py':UI/'candidate/scripts/verify_damage_ui.py',
 'rouge/operator_engine.py':DEEP/'draft-tree/rouge/operator_engine.py',
 'rouge/reporting.py':DEEP/'draft-tree/rouge/reporting.py',
}
for p in expected.values():ast.parse(p.read_text())
binding={k:f(v) for k,v in expected.items()}
assert binding['rouge/app.py']['sha256']=='fa27d6eceaf88f8caf1bc4e994641c6d110884ee9fbf673ab7d46a355cc41143'
save('frozen-authors-and-expected-four-targets091.json',{'format_version':1,'status':'FROZEN_AUTHOR_SOURCES_NOT_YET_ROOT_APPLIED','author_base':'2cbc45f03f99ed4f04b9c7e2612b58542f909168','expected_integrated_target_files':binding,'UI_author_manifest':f(UI/'ui-author-public-manifest091.json'),'UI_focused_plan':f(UI/'focused-MainWindow-plan091.json'),'Deep_author_manifest':f(DEEP/'public-artifacts-manifest-final.json'),'Deep_saved_once_three_results':f(DEEP/'public-draft.json'),'Deep_saved_positive_actual_text':f(DEEP/'draft-text-1.txt'),'source34_manifest':f(Path('/workspace/.continuation/p2-continuous-attack-control-visibility091-source/manifest-source091.json')),'source23_manifest':f(Path('/workspace/.continuation/future-deepcolor-s1-regeneration-note-source/public-artifacts-manifest.json')),'all_prior_API_test_Qt_Wine_calls_repeated':False})

rows=[]
def add(id,kind,owner,skill=None,elite=2,level=60,rank=10,checked=True,visible=True,**extra):
    rows.append({'id':id,'kind':kind,'owner':owner,'skill':skill,'training':{'elite':elite,'level':level,'potential':1,'trust':100,'module_id':None,'module_level':0},'skill_rank':rank,'checked':checked,'expected_row_visible':visible,**extra})
add('mechanist-default-true','train','mechanist',1,checked=True,explicit_click=True)
add('mechanist-toggle-false','toggle','mechanist',1,checked=False)
add('amiya-E2-retains-false','train','char_002_amiya',1,level=80,checked=False)
add('amiya-E2-toggle-true','toggle','char_002_amiya',1,level=80)
add('amiya-E2-toggle-false','toggle','char_002_amiya',1,level=80,checked=False,screenshot='wine-focused-continuous-091.png')
add('chen3-67-false','train','char_1050_chen3',3,level=90,checked=False,relic_ids=['rogue_6_relic_legacy_67'])
add('chen3-67-toggle-true','toggle','char_1050_chen3',3,level=90,relic_ids=['rogue_6_relic_legacy_67'])
add('chen3-remove-67-retain-true','relic_change','char_1050_chen3',3,level=90,relic_ids=[])
add('chen3-reselect-67-retain-true','relic_change','char_1050_chen3',3,level=90,relic_ids=['rogue_6_relic_legacy_67'])
add('silverash-natural-no-attack-credit','train','silverash',3,relic_ids=[])
add('amiya-run-E0-talent-ineligible','run_training','char_002_amiya',1,elite=0,level=50,rank=7)
add('amiya-run-E1-talent-ineligible','run_training','char_002_amiya',1,elite=1,level=70,rank=7)
add('gummy-natural-retired118-reference-only','train','char_196_sunbr',1,relic_ids=['rogue_6_relic_legacy_118'])
add('hsgma-received-hidden-true','train','char_1044_hsgma2',1,level=90,visible=False)
add('hsgma-received-hidden-toggle-false','toggle','char_1044_hsgma2',1,level=90,checked=False,visible=False)
add('amiya-natural-return-retains-false','train','char_002_amiya',1,level=80,checked=False)
add('unimplemented-Lancet-no-skills-hidden-false','train','char_285_medic2',None,elite=0,level=1,rank=None,checked=False,visible=False,numerical_result_expected=False,early_status_fragment='技能伤害规则尚未实现')
add('unimplemented-hidden-toggle-true','toggle','char_285_medic2',None,elite=0,level=1,rank=None,visible=False,numerical_result_expected=False,early_status_fragment='技能伤害规则尚未实现')
add('empty-overview-placeholder-hidden-true','overview',None,None,elite=0,level=1,rank=None,visible=False,numerical_result_expected=False,early_status_fragment='本局总览暂无已确认招募干员')
add('attack-return-retains-true','train','mechanist',1)
for id,skill,window,relics,rate in [('deep-S1-base30',1,30,[],70),('deep-S1-rose81-window10',1,10,['rogue_6_relic_legacy_81'],84),('deep-S1-rose81-zero-window',1,0,['rogue_6_relic_legacy_81'],84),('deep-S2-no-S1-note-leak',2,10,['rogue_6_relic_legacy_81'],None)]:
    add(id,'deep','char_110_deepcl',skill,level=70,window_seconds=window,relic_ids=relics,summon_count=2,expected_regeneration_per_token_rate=rate,expected_regeneration_selected_rate=None if rate is None else rate*2,explicit_click=True,**({'screenshot':'wine-focused-deepcolor-091.png'} if id=='deep-S1-rose81-window10' else {}))
assert len(rows)==24
save('focused-window-state-plan091.json',{'format_version':1,'status':'SOURCE_ONLY_PLANNED_24_FOCUSED_STATES_NOT_GUI_PASS','rows':rows,'planned_states':24,'planned_numerical_states':21,'planned_early_status_states':3,'explicit_button_requests':5,'planned_explicit_three_text_requests':63,'actual_automatic_calculation_and_formatter_entries':'measure actual main-thread entries; do not infer from 24 states or 5 explicit buttons','baseline_style':'One real isolated MainWindow, no all87skills/4217/full90 replay; sequential representative control transitions only','fixed_common_inputs':{'timing_mode':'continuous','window_seconds':30.0,'enemy_defense':0.0,'enemy_resistance':0.0,'healing_targets':1,'deployment_elapsed_seconds':0.0,'manual_base_attack':'omitted; readonly automatic','module_id':None,'module_level':0,'relic_ids':[],'timing':'empty JSON editor, no invented event clock'},'row_label':'普攻回技力条件','checkbox_tooltip':'声明估算时是否持续普攻；自然回复技能也可能通过适用的天赋或藏品使用此条件。显示此项不表示必有额外技力。未核验的技力来源仅作资料参考，未知回转保持未知。','early_return_existing_damage_result_policy':'Existing app leaves prior damage_result on early return; record it as stale, current visible status and zero numerical entries. Never label it as a new numerical result or format it into fresh three texts.','Deep_zero_GUI_native_count':2,'Deep_author_string_count_case_reexecuted':False,'standalone_implemented_skill_None_case':'Not fabricated: genuine selected Lancet has zero skills and unimplemented early gate, empty overview is actual None; no catalog or fake skill combo edit.','alternate_Amiya_form_optional_not_in_budget':'Existing alternate IDs are genuine, but no conversion or attachment mechanism inferred; representative plan uses caster qualification stages only.','native_windows_game_clock_certification':False,'fresh_prep_product_calls':0})
print('source-only24stateplan; product calls 0')
