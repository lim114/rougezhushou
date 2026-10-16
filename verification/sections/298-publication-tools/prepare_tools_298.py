"""Prepare four publication scripts only. Do not execute their Git or document actions."""
import ast
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'.cache/p3-297-publication-prep'
PARENT='bb4927a2a2760d48882f3945b750053d7a5617fc'
OLD_PARENT='7706a982b84fe64148da87d6d073786704c188d1'
TEST='tests/test_node_catalog.py'
TEST_SHA='daebfe930079810c7d057699d8fc3bb4f0f8dee46309df3a624a9b087338436a'
PROD=['rouge/event_planning.py','rouge/node_catalog.py','rouge/node_catalog_view.py','rouge/player_node_information.py']
DOCS=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md']
baseline={}


def read(name):
 raw=(OLD/name).read_bytes();baseline[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
 return raw.decode('utf8').replace('297','298').replace(OLD_PARENT,PARENT)


def once(text,old,new):
 assert text.count(old)==1,old
 return text.replace(old,new,1)


def block(text,start,end,replacement):
 a=text.index(start);b=text.index(end,a)
 return text[:a]+replacement+text[b:]


def save(name,text):
 compile(ast.parse(text,filename=name),name,'exec')
 assert OLD_PARENT not in text and 'expedition' not in text and 'beacon' not in text
 assert 'test_documented_item_integration_295.py'not in text
 with(HERE/name).open('xb')as stream:stream.write(text.encode('utf8'))


promotion_name='verification/sections/298-preparation/final-promotion.json'
raw=(ROOT/promotion_name).read_bytes();promotion_sha=sha256(raw).hexdigest();promotion=json.loads(raw)
assert len(promotion['promoted'])==15 and set(promotion['existing_production_changes'])==set(PROD)
assert promotion['maintained_test_final']=={'path':TEST,'sha256':TEST_SHA}
migration_name='verification/sections/298-preparation/historical-test-migration-final.json'
migration_sha=sha256((ROOT/migration_name).read_bytes()).hexdigest()
raw_logs={}
for folder in ('first-real-pure-api-tests','first-real-source-build','known-floor-context-final-pure-api-tests','second-real-source-build'):
 for stream in ('stdout','stderr'):
  name=f'verification/sections/298-preparation/author-source-model/{folder}/{stream}'
  raw_logs[name]=sha256((ROOT/name).read_bytes()).hexdigest()
assert len(raw_logs)==8
camera_exit='verification/sections/298-preparation/map-camera-research/cfg.exit'
camera_manifest='verification/sections/298-preparation/map-camera-research/research-manifest.json'
camera=json.loads((ROOT/camera_manifest).read_bytes())
assert sha256((ROOT/camera_exit).read_bytes()).hexdigest()==camera['files']['cfg.exit']['sha256']
extra_logs={camera_exit:camera['files']['cfg.exit']['sha256']}

text=read('stage_section_297.py')
text=block(text,'tracked=[',"assert set(git(['diff','--name-only'])",'tracked='+repr(DOCS+PROD+[TEST])+'\n')
start="promotion_raw=(ROOT/"
end="for entry in (ROOT/'verification/sections').iterdir():"
new=(f"promotion_raw=(ROOT/{promotion_name!r}).read_bytes()\n"
 f"assert sha256(promotion_raw).hexdigest()=={promotion_sha!r}\n"
 "promotion=json.loads(promotion_raw)\n"
 f"assert len(promotion['promoted'])==15 and set(promotion['existing_production_changes'])==set({PROD!r})\n"
 f"maintenance_path={TEST!r}\n"
 f"migration_raw=(ROOT/{migration_name!r}).read_bytes()\n"
 f"assert sha256(migration_raw).hexdigest()=={migration_sha!r}\n"
 "migration=json.loads(migration_raw)\n"
 f"assert migration['new_source']==maintenance_path and migration['new_sha256']=={TEST_SHA!r}\n"
 "assert sha256((ROOT/maintenance_path).read_bytes()).hexdigest()==migration['new_sha256']\n"
 "assert migration['changed_methods']==['test_172','test_183'] and migration['unchanged_other_test_methods']==30\n"
 "assert migration['first_actual_failures']==1 and migration['coverage_scope_reduced'] is False\n"
 f"raw_archived_logs={raw_logs!r}\n"
 f"pinned_research_exit={extra_logs!r}\n"
 "assert len(raw_archived_logs)==8 and len(pinned_research_exit)==1\n"
 "raw_archived_logs.update(pinned_research_exit)\n"
 "new=[name for name in {*promotion['promoted'],*promotion['existing_production_changes']} if name not in tracked]\n")
text=block(text,start,end,new)
text=block(text,"assert section['only_existing_production_sources_changed']",'progress=(ROOT/',
 f"assert section['only_existing_production_sources_changed']=={PROD!r}\n"
 f"assert section['existing_source_changes_including_test_maintenance']==sorted({PROD!r}+[maintenance_path])\n"
 "assert set(section['source_sha256'])==set(promotion['promoted'])|set(promotion['existing_production_changes'])|{maintenance_path}\n"
 "assert len(section['source_sha256'])==20 and section['source_sha256'][maintenance_path]==migration['new_sha256']\n"
 "assert section['historical_test_maintenance']['final_tested_sha256']==migration['new_sha256']\n"
 "assert section['remaining_global_stage_floor_gaps_unchanged']==15 and section['unparsed_notes_unchanged']==10\n"
 "assert section['actual_server_generation_or_inventory_verified'] is False\n"
 "assert section['typed_named_grant_count_unchanged']==17 and section['original_entry_gaps_unchanged']==[25,57]\n")
for prefix in ("section['next_section']","cp['next_section']","index['next_section']"):
 text=once(text,prefix+'==298',prefix+'==299')
save('stage_section_298.py',text)
save('push_section_298.py',read('push_section_297.py'))

text=read('verify_publication_297.py')
text=once(text,"section['next_section']==298","section['next_section']==299")
text=once(text,"cp['next_section']==298","cp['next_section']==299")
text=once(text,"'next_section':298","'next_section':299")
text=once(text,"idx=text.index('## 功能第296节')","idx=text.index('## 功能第297节')")
text=block(text,"assert section['unparsed_notes_unchanged']", "assert section['remaining_global_stage_floor_gaps_unchanged']",
 "assert section['unparsed_notes_unchanged']==10\n"
 f"assert section['source_sha256'][{TEST!r}]=={TEST_SHA!r}\n"
 "assert len(section['source_sha256'])==20 and section['historical_test_maintenance']['final_tested_sha256']==section['source_sha256']['tests/test_node_catalog.py']\n"
 "assert 'tests.test_event_node_requirements_integration_298' in necessary['modules']\n"
 "assert 'test_all_default_190_resource_and_38_player_outputs_remain_exact_parent_bytes' in (ROOT/'tests/test_event_node_requirements_integration_298.py').read_text(encoding='utf8')\n")
text=block(text," 'scope':("," 'necessary_methods_actual':",
 " 'scope':('Functional298 adds source-bound natural-main-floor restrictions for six exact event identities, '+\n"
 " 'with manual reading of excluded references and two documented technology enabling paths; inactive technology '+\n"
 " 'is not a proven hard exclusion. Content/history/special/unknown contexts preserve their distinct scope. '+\n"
 " 'Source loss reverts restriction conclusions to unknown; no actual server generation or inventory is claimed. Actual '+\n"
 " str(section['necessary_validation']['methods_run'])+' necessary methods and '+str(window['unique_checks'])+\n"
 " ' unique native checks, '+str(window['screenshot_count'])+' representative PNGs. '+\n"
 " 'Original first127/1F remains archived; final necessary count is not added to the first count. '+\n"
 " 'Metadata adds no functional section; historical290 full coverage is not relabelled298.'),\n")
text=once(text," 'old_resource_query_count_unchanged':190,'other_event_player_output_count_unchanged':37,\n 'unparsed_notes_unchanged':10,'actual_dispatch_return_inventory_or_cultivation_verified':False,",
 " 'default_resource_query_count_unchanged':190,'default_event_player_output_count_unchanged':38,\n"
 " 'unparsed_notes_unchanged':10,'actual_server_generation_or_inventory_verified':False,")
text=once(text,"'待普通推送核对，源码/要求/回执/索引同提交。'","'待普通推送核对。'")
text=once(text,"'待普通推送核对真实远端，源码/要求/验收/索引同提交。'","'待普通推送核对，源码/要求/验收/索引同提交。'")
save('verify_publication_298.py',text)

text=read('finish_publication_297.py')
text=once(text,"cp['next_section']==index['next_section']==298","cp['next_section']==index['next_section']==299")
text=once(text,"'next_section':298","'next_section':299")
text=once(text,'next298 only after','next299 only after')
save('finish_publication_298.py',text)

value={'kind':'ADAPTED_FROM_ACTUAL297_STRICT_PUBLICATION_CHAIN','files':baseline,
 'old_tools_modified':False,'new_tools_executed':False,'promotion_receipt':promotion_name,
 'promotion_receipt_sha256':promotion_sha,'new_promoted_entries':15,'existing_production_entries':4,
 'final_feature_and_test_maintenance_source_entries':20,'tracked_public_entries':12,
 'historical_test':{'path':TEST,'final_sha256':TEST_SHA,'migration':migration_name,'migration_sha256':migration_sha},
 'raw_author_logs_exact8':raw_logs,'separate_pinned_research_exit':extra_logs,
 'separate_pinned_research_exit_manifest':camera_manifest,
 'separate_pinned_research_exit_manifest_sha256':sha256((ROOT/camera_manifest).read_bytes()).hexdigest(),
 'promotion_hashes_do_not_substitute_for_final_actual_validation_maps':True}
with(HERE/'BASELINE.json').open('xb')as stream:stream.write((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'cached_scripts_generated':4,'AST_compile_only':True,'publication_Git_Qt_tests_executed':False}))
