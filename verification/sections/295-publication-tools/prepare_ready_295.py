"""Only pure AST/public byte and schema checks. Never executes output publication tools."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
scripts=['stage_section_295.py','push_section_295.py','verify_publication_295.py','finish_publication_295.py']
for name in scripts:
 source=(HERE/name).read_text(encoding='utf8');ast.parse(source,filename=name)
 assert 'parents[2]'in source and "['git','commit'"not in source and '--force'not in source
 assert '48eeb454e23fffee084fe7b6c7f9667b9216131d'not in source
stage=(HERE/scripts[0]).read_text(encoding='utf8')
tree=ast.parse(stage);tracked=next(ast.literal_eval(n.value)for n in tree.body
 if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='tracked'for t in n.targets))
assert tracked==['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json',
 'PROJECT_COMPLETED.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/node_catalog_view.py','rouge/player_node_information.py']
assert "'.html'"in stage and "'PROJECT_PROGRESS.md'"not in str(tracked)
assert "'HEAD:refs/heads/codex/p2-development'"in(HERE/scripts[1]).read_text()
section=json.loads((ROOT/'verification/sections/295.json').read_bytes())
assert section['section']==295 and section['prior_commit']=='e517095f388baad3aa7824dbd5b9dee6a68fb450'
assert section['cloud_published']is False and section['next_section']==296
assert section['typed_named_grant_count_unchanged']==17 and section['original_entry_gaps_unchanged']==[25,57]
assert sha256((ROOT/'PROJECT_PROGRESS.md').read_bytes()).hexdigest()==section['PROJECT_PROGRESS_unchanged_sha256']
actuals={}
for key in('necessary_validation','native_windows_validation'):
 ref=section[key];raw=(ROOT/ref['receipt']).read_bytes()
 assert sha256(raw).hexdigest()==ref['sha256']
 value=json.loads(raw);assert value['source_sha256_before']==value['source_sha256_after']
 for name,expected in value['source_sha256_after'].items():
  assert not name.startswith(('.cache/','.local/'))and name!='local-settings.json'
  assert sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
 actuals[key]=value
necessary=actuals['necessary_validation'];native=actuals['native_windows_validation']
assert necessary['exit_code']==0 and native['passed']is True and native['qt_exit_code']==0
assert set(native['source_sha256_after'])<=set(necessary['source_sha256_after'])
assert all(necessary['source_sha256_after'][n]==v for n,v in native['source_sha256_after'].items())
names=scripts+['prepare_tools_295.py','prepare_ready_295.py','RUN_PLAN.md','BASELINE.json']
result={'kind':'SECTION295_PUBLICATION_CACHE_PREPARATION_ONLY','prepared_utc':datetime.now(timezone.utc).isoformat(),
 'static_AST_and_actual_public_schema_checked':True,'publication_tools_executed':False,
 'Git_mutation_commit_push_or_GUI_tests_executed_by_preparation':False,
 'parent_commit':'e517095f388baad3aa7824dbd5b9dee6a68fb450',
 'functional_commit':None,'metadata_commit':None,'remote_ref':None,'publication_passed':None,
 'observed_existing_validation_only':{'necessary_methods':section['necessary_validation']['methods_run'],
  'necessary_source_files':len(necessary['source_sha256_after']),'native_unique_checks':native['unique_checks'],
  'native_repeated_assertions':native['successful_assertion_executions_including_repeated_guards'],
  'native_source_files':len(native['source_sha256_after'])},
 'functional_tracked_allowlist':tracked,'PROJECT_PROGRESS_staged':False,'explicit_HTML_allowed':True,
 'files':{name:{'sha256':sha256((HERE/name).read_bytes()).hexdigest(),'bytes':(HERE/name).stat().st_size}for name in names}}
with(HERE/'READY.json').open('xb')as f:f.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'cache_preparation_only':True,'all_four_scripts_AST_valid':True,
 'publication_or_Git_mutation_executed':False,'READY_sha256':sha256((HERE/'READY.json').read_bytes()).hexdigest(),
 'script_sha256':{n:result['files'][n]['sha256']for n in scripts}}))
