"""Static/public-read READY only. Do not execute generated publication scripts."""
import ast
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT='bb4927a2a2760d48882f3945b750053d7a5617fc'
SCRIPTS=['stage_section_298.py','push_section_298.py','verify_publication_298.py','finish_publication_298.py']
DOCS=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md']
PROD=['rouge/event_planning.py','rouge/node_catalog.py','rouge/node_catalog_view.py','rouge/player_node_information.py']
TEST='tests/test_node_catalog.py'
EXPECTED='daebfe930079810c7d057699d8fc3bb4f0f8dee46309df3a624a9b087338436a'
load=lambda name:json.loads((ROOT/name).read_bytes())
digest=lambda name:sha256((ROOT/name).read_bytes()).hexdigest()

sources={}
for name in SCRIPTS:
 text=(HERE/name).read_text(encoding='utf8');compile(ast.parse(text,filename=name),name,'exec')
 assert 'parents[2]'in text and '--force'not in text and "['git','commit'"not in text
 assert 'expedition'not in text and 'beacon'not in text and 'test_documented_item_integration_295.py'not in text
 assert '7706a982b84fe64148da87d6d073786704c188d1'not in text
 sources[name]=text
stage=ast.parse(sources[SCRIPTS[0]])
tracked=next(ast.literal_eval(n.value)for n in stage.body if isinstance(n,ast.Assign)
 and any(isinstance(t,ast.Name)and t.id=='tracked'for t in n.targets))
assert tracked==DOCS+PROD+[TEST]and len(tracked)==12 and 'PROJECT_PROGRESS.md'not in tracked
assert "'HEAD:refs/heads/codex/p2-development'"in sources[SCRIPTS[1]]
baseline=json.loads((HERE/'BASELINE.json').read_bytes())
for name,pin in baseline['files'].items():
 raw=(ROOT/'.cache/p3-297-publication-prep'/name).read_bytes()
 assert sha256(raw).hexdigest()==pin['sha256']and len(raw)==pin['bytes']
promotion=load(baseline['promotion_receipt'])
assert digest(baseline['promotion_receipt'])==baseline['promotion_receipt_sha256']
assert promotion['section']==298 and len(promotion['promoted'])==15
assert set(promotion['existing_production_changes'])==set(PROD)
assert promotion['maintained_test_final']=={'path':TEST,'sha256':EXPECTED}
migration=load(baseline['historical_test']['migration'])
assert digest(baseline['historical_test']['migration'])==baseline['historical_test']['migration_sha256']
assert migration['new_sha256']==EXPECTED==digest(TEST)and migration['changed_methods']==['test_172','test_183']
assert migration['unchanged_other_test_methods']==30 and migration['first_actual_methods']==127 and migration['first_actual_failures']==1
assert migration['old_failure_preserved']is True and migration['coverage_scope_reduced']is False
raw_logs=baseline['raw_author_logs_exact8'];extra=baseline['separate_pinned_research_exit']
assert len(raw_logs)==8 and set(extra)=={'verification/sections/298-preparation/map-camera-research/cfg.exit'}
for name,expected in {**raw_logs,**extra}.items():assert digest(name)==expected
assert digest(baseline['separate_pinned_research_exit_manifest'])==baseline['separate_pinned_research_exit_manifest_sha256']
for entry in(ROOT/'verification/sections').iterdir():
 if not entry.name.startswith('298'):continue
 for path in[entry]if entry.is_file()else entry.rglob('*'):
  assert not path.is_symlink()
  if path.is_file():
   relative=path.relative_to(ROOT).as_posix()
   assert path.suffix in{'.json','.log','.md','.png','.py','.txt','.diff','.stderr','.stdout','.html'}or relative in raw_logs or relative in extra,relative
   assert path.stat().st_size<20_000_000
necessary_name='verification/sections/298-necessary-final/process.json';necessary=load(necessary_name)
assert necessary['section']==298 and necessary['exit_code']==0 and necessary['source_commit_before']==PARENT
assert necessary['source_unchanged']is True and necessary['source_sha256_before']==necessary['source_sha256_after']
text=(ROOT/necessary_name).with_name('stderr.txt').read_text(encoding='utf8')
counts=re.findall(r'Ran (\d+) tests in ',text)
assert counts==['127']and text.rstrip().endswith('OK')
expected_map={name:pin['sha256']for name,pin in{**promotion['promoted'],**promotion['existing_production_changes']}.items()}
expected_map[TEST]=EXPECTED
assert len(expected_map)==20 and len(necessary['source_sha256_after'])==381
for name,expected in necessary['source_sha256_after'].items():
 assert not name.startswith(('.cache/','.local/'))and name!='local-settings.json'
 assert digest(name)==expected,name
assert all(necessary['source_sha256_after'][name]==expected for name,expected in expected_map.items())
assert 'tests.test_event_node_requirements_integration_298'in necessary['modules']
files=SCRIPTS+['prepare_tools_298.py','prepare_ready_298.py','RUN_PLAN.md','BASELINE.json']
result={'kind':'SECTION298_PUBLICATION_CACHE_PREPARATION_ONLY',
 'prepared_utc':datetime.now(timezone.utc).isoformat(),'static_AST_and_current_public_necessary_source_checked':True,
 'publication_tools_executed':False,'Git_mutation_commit_push_Qt_tests_executed_by_preparation':False,
 'parent_commit':PARENT,'functional_commit':None,'metadata_commit':None,'remote_ref':None,'publication_passed':None,
 'final_section_receipt_required_at_execution':'verification/sections/298.json',
 'native_final_and_original_main_evidence_not_consumed_or_marked_pass_by_preparation':True,
 'native_validation_passed':None,'main_window_validation_passed':None,
 'final_receipt_schema_reference':'.cache/p3-298-runtime-preparation/closeout-v3/close_section_298.py',
 'all_final_actual_maps_reloaded_and_Git_blobs_checked_by_execution_tools':True,
 'observed_existing_necessary_only':{'receipt':necessary_name,'sha256':digest(necessary_name),'methods':int(counts[0]),
  'source_files':len(necessary['source_sha256_after']),'actual_exit':necessary['exit_code'],
  'first127_one_failure_not_added_to_final_success':True,'not_new_validation_executed_by_preparation':True},
 'functional_tracked_allowlist':tracked,'PROJECT_PROGRESS_staged':False,
 'new_promoted_entries':15,'existing_production_entries':4,'final_feature_and_maintenance_source_entries':20,
 'raw_author_logs_exact8':raw_logs,'separate_pinned_research_exit':extra,
 'next_section':299,'full_validation_is_historical_after_section':290,'next_full_validation_after':305,
 'files':{name:{'sha256':sha256((HERE/name).read_bytes()).hexdigest(),'bytes':(HERE/name).stat().st_size}for name in files}}
with(HERE/'READY.json').open('xb')as stream:stream.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'preparation_only':True,'exit_contract':'no publication PASS',
 'READY_sha256':sha256((HERE/'READY.json').read_bytes()).hexdigest(),
 'script_sha256':{name:result['files'][name]['sha256']for name in SCRIPTS}}))
