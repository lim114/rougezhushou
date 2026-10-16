"""Create cache303 ordinary-publication tools, without running them or Git."""
from pathlib import Path
import json
import runpy

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.cache/p3-303-publication-prep';OUT.mkdir(exist_ok=True)
convert=runpy.run_path(str(ROOT/'.cache/prepare_tools_303.py'))['convert']
PARENT='c2b78e4aa4136fe739067b5ccf9d13b595142320'
def replace(source,old,new):
 if source.count(old)!=1:raise ValueError('Exact reviewed source seam changed: '+old[:90])
 return source.replace(old,new,1)
for name in ('stage_section','push_section','verify_publication','finish_publication'):
 source=(ROOT/f'verification/sections/302-publication-tools/{name}_302.py').read_text(encoding='utf8')
 source=convert(source).replace('87a622eea314ccce49712121fd42683eb2e7e463',PARENT)
 if name=='stage_section':
  source=replace(source,"'WORK_IN_PROGRESS.md','rouge/node_catalog_view.py']",
   "'WORK_IN_PROGRESS.md','PROJECT_PROGRESS.md','rouge/data/fixed-landmark-references.json',"
   "'tests/test_direct_landmark_294.py','tests/test_map_projection_048.py']")
  source=replace(source,"assert section['only_existing_production_sources_changed']==section['existing_source_changes_including_test_maintenance']==['rouge/node_catalog_view.py']\nassert section['old_tracked_test_maintenance']is False",
   "assert section['only_existing_production_sources_changed']==['rouge/data/fixed-landmark-references.json']\n"
   "assert set(section['existing_source_changes_including_test_maintenance'])=={'rouge/data/fixed-landmark-references.json','tests/test_direct_landmark_294.py','tests/test_map_projection_048.py'}\n"
   "assert set(section['old_tracked_test_maintenance'])=={'tests/test_direct_landmark_294.py','tests/test_map_projection_048.py'}")
  source=replace(source,"assert set(promotion['existing_production_changes'])=={'rouge/node_catalog_view.py'}",
   "assert set(promotion['existing_production_changes'])=={'rouge/data/fixed-landmark-references.json'}\n"
   "assert set(promotion['historical_test_maintenance'])==set(section['old_tracked_test_maintenance'])")
  source=replace(source,"assert promotion['parent_commit']==PARENT and promotion['old_tests_modified']is False",
   "assert promotion['parent_commit']==PARENT and promotion['old_tests_modified']is True and promotion['old_test_maintenance_scope_exact']is True\n"
   "assert set(section['validated_source_sha256'])==set(section['source_sha256'])|set(promotion['historical_test_maintenance'])")
  source=replace(source,"for name,pin in {**promotion['promoted'],**promotion['existing_production_changes']}.items():\n assert type(pin)is str and digest(name)==pin==section['source_sha256'][name]",
   "for name,pin in {**promotion['promoted'],**promotion['existing_production_changes'],**promotion['historical_test_maintenance']}.items():\n"
   " assert type(pin)is str and digest(name)==pin==section['validated_source_sha256'][name]")
  source=replace(source,"assert section['partial_direct_reference_scope_unchanged']==[10,18,58] and section['whole_map_gaps_unchanged']==[81,59]",
   "assert section['partial_direct_reference_scope_before']==[10,18,58] and section['partial_direct_reference_scope']==[12,21,107] and section['whole_map_gaps_unchanged']==[81,59]")
  a=source.index("assert section['source_reference']['fixed_choice_count']")
  b=source.index("for label in ('necessary_validation'",a)
  source=source[:a]+"""assert section['source_reference']['accepted_points']==49 and section['source_reference']['rejected_or_unknown_points']==40
assert section['source_reference']['all89_original_requests_preserved']is True
change=section['PROJECT_PROGRESS_change']
assert digest('PROJECT_PROGRESS.md')==change['after_sha256']
old=git(['show','HEAD:PROJECT_PROGRESS.md'])
assert sha256(old).hexdigest()==change['before_sha256']
assert old.decode('utf8').count(change['before_fragment'])==1
assert old.decode('utf8').replace(change['before_fragment'],change['after_fragment'],1).encode('utf8')==(ROOT/'PROJECT_PROGRESS.md').read_bytes()
"""+source[b:]
  source=source.replace("'old_tracked_tests_changed':False","'old_tracked_tests_changed':True,'old_maintenance_paths':sorted(promotion['historical_test_maintenance'])")
 elif name=='verify_publication':
  source=replace(source,"{'tests.test_ritual_weakening_303','tests.test_ritual_weakening_view_303','tests.test_ritual_weakening_integration_303'}<=set(necessary['modules'])",
   "{'tests.test_direct_landmark_303','tests.test_direct_landmark_294','tests.test_map_projection_048'}<=set(necessary['modules']) and len(necessary['modules'])==5")
  source=replace(source,"assert section['remaining_global_stage_floor_gaps_unchanged']==15 and section['unparsed_notes_unchanged']==10 and section['old_tracked_test_maintenance']is False",
   "assert section['remaining_global_stage_floor_gaps_unchanged']==15 and section['unparsed_notes_unchanged']==10\n"
   "assert set(section['old_tracked_test_maintenance'])=={'tests/test_direct_landmark_294.py','tests/test_map_projection_048.py'}")
  source=replace(source,"assert section['only_existing_production_sources_changed']==['rouge/node_catalog_view.py']",
   "assert section['only_existing_production_sources_changed']==['rouge/data/fixed-landmark-references.json']")
  source=replace(source,"assert section['partial_direct_reference_scope_unchanged']==[10,18,58]and section['whole_map_gaps_unchanged']==[81,59]",
   "assert section['partial_direct_reference_scope_before']==[10,18,58]and section['partial_direct_reference_scope']==[12,21,107]and section['whole_map_gaps_unchanged']==[81,59]")
  a=source.index("assert section['source_reference']['fixed_choice_count']");b=source.index('expected=dict(',a)
  source=source[:a]+"assert section['source_reference']['all89_original_requests_preserved']is True and section['source_reference']['accepted_points']==49 and section['source_reference']['rejected_or_unknown_points']==40\n"+source[b:]
  source=replace(source,"for mapping in(section['source_sha256'],necessary['source_sha256_after'],window['source_sha256_after']):",
   "for mapping in(section['validated_source_sha256'],necessary['source_sha256_after'],window['source_sha256_after']):")
  a=source.index(" 'scope':(");b=source.index(" 'necessary_methods_actual':",a)
  source=source[:a]+""" 'scope':('Complete89 first readings by two isolated-context agents are retained;49 accepted and40 rejected/unknown. '+
  'Only original A pixels within the unchanged exact4px Euclidean gate are appended; no mean, fit or adjustment. '+
  'New partial ground centers cover the fixed maps of ro6_b_6 and ro6_n_2_3 plus the explicitly bound emergency alias. '+
  'Old58 whole records and regular12image24stage dictionary are unchanged; partial totals are12images21stages107points. '+
  'Whole-map81/59 gaps, highland/portal/offset/actual-position and inverse/segment limits remain. '+
  'Two old tests have exact documented compatibility maintenance; unchanged18 and8 method ASTs are preserved. '+
  'Actual local public historical inputs have exact public counterparts and dual before/after source guards; no private historical sample claimed. '+
  'Only fixed direct-reference runtime data changes; no product Python or route advice is added. '+
  'Historical290 full validation remains historical; publication does not add a functional section.'),
"""+source[b:]
  a=source.index(" 'fixed_choice_count':");b=source.index(" 'original_entry_gaps_unchanged':",a)
  source=source[:a]+""" 'all89_original_requests_preserved':True,'accepted_direct_points':49,'rejected_or_unknown_points':40,
 'prior_partial_direct_scope':[10,18,58],'partial_direct_reference_scope':[12,21,107],
 'old58_complete_records_unchanged':True,'regular12_images24_stages_unchanged':True,
 'old_typed_reward_contract_unchanged':True,'typed_named_grant_count_unchanged':17,
 'old_resource_and_player_information_production_pipelines_not_modified':True,
 'unparsed_notes_unchanged':10,'actual_server_generation_or_inventory_verified':False,
 'old_tracked_tests_changed':True,'old_test_maintenance_paths':sorted(section['old_tracked_test_maintenance']),
 'PROJECT_PROGRESS_only_exact_scope_fragment_replaced':True,
"""+source[b:]
  source=replace(source,"'remaining_global_stage_floor_gaps_unchanged':15,'partial_direct_reference_scope_unchanged':[10,18,58],",
   "'remaining_global_stage_floor_gaps_unchanged':15,")
 # push and finish preserve the already-successful ordinary2push byte readback workflow.
 target=OUT/f'{name}_303.py';target.write_text(source,encoding='utf8');compile(source,str(target),'exec')
 if name in('stage_section','verify_publication'):
  target.with_suffix('.py.txt').write_text(source,encoding='utf8')
baseline={'section':303,'parent_commit':PARENT,'branch':'codex/p2-development','next_section':304,
 'last_full_is_historical_after_section':290,'next_full_after_section':305,'numeric_continuation_target':None,
 'only_existing_production_source':'rouge/data/fixed-landmark-references.json',
 'historical_test_maintenance_paths':['tests/test_direct_landmark_294.py','tests/test_map_projection_048.py'],
 'partial_reference_scope_before':[10,18,58],'partial_reference_scope_after':[12,21,107],
 'PROGRESS_change':'only exact parenthetical scope; no finished-item summary added',
 'source_counts_dynamic_from_actual_promotion':True,'preparation_is_not_acceptance_or_publication':True}
(OUT/'BASELINE.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Four cache303 publication scripts compiled; none executed.')
