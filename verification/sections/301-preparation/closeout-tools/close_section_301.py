"""Strict section301 public-evidence closeout. Preview default; root-only --apply.
No Qt/tests, game/chat/private operations or Git mutation. Missing actual evidence fails.
"""
import argparse,ast,runpy
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,re,struct,subprocess
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
HERE=ROOT/'.cache/p3-301-closeout/revision2'
PARENT='5607cbc46c9cf17a841939a778a247e6e1a2a371'
TITLE='16条精确节点选项的13种具名物品图文阅读'
CANONICAL='scripts/verify_named_reward_items_window_301.py'
PACKET='research/p3-named-reward-items-301';MANIFEST=PACKET+'/source-manifest.json';DATA='rouge/data/named-reward-items.json'
MANIFEST_SHA='a7501b82da0c9e3fa75809656f371f20a43c196eeef2cd37cfd388c16f185374'
DATA_SHA='437684110f9e1190e1e7b681ef14f9d20ceb17e45e814a769244cca1a072353c'
BUILDER='scripts/build_named_reward_items_301.py'
FULL='verification/full-290/summary.json';FULL_SHA='2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
CHANGED_EXISTING={'rouge/node_catalog_view.py'}
REQUIRED_MODULES={'tests.test_named_reward_items_301','tests.test_named_reward_items_view_301','tests.test_named_reward_integration_301'}
PROGRESS_SHA_BEFORE='111962b1622515c494ae81a06ac19b915db797211e926165a9947b80fade8a0b'
TEST_REPAIR_PATH='tests/test_documented_item_integration_295.py'
TEST_BEFORE_SHA='4e946fd3579f37bc3f222f855f9c23811c1279c946a4345431161ed141fcc2f9'
TEST_AFTER_SHA='53b54f8f3524ca9aa5ecfec976af0231aba9113e6e1b32e380d71ef89926e3cc'
TEST_REPAIR_PROOF='verification/sections/301-preparation/historical295-query-guard/migration.json'
TEST_REPAIR_PROOF_SHA='9367f7dc8c1e49065eb8a9aef443155ea34448204b730e809cf95cefed7c3f35'


def historical_test_maintenance():
 proof=load(TEST_REPAIR_PROOF);require(digest(TEST_REPAIR_PROOF)==TEST_REPAIR_PROOF_SHA,'exact reviewed test guard migration proof')
 require(proof['test_file']==TEST_REPAIR_PATH and proof['old_test_sha256']==TEST_BEFORE_SHA and proof['new_test_sha256']==TEST_AFTER_SHA,
  'migration binds exact original and candidate test bytes')
 original_path='verification/sections/301-preparation/first-necessary-source/'+TEST_REPAIR_PATH
 old_raw=path(original_path).read_bytes();new_raw=path(TEST_REPAIR_PATH).read_bytes()
 require(sha256(old_raw).hexdigest()==TEST_BEFORE_SHA and sha256(new_raw).hexdigest()==TEST_AFTER_SHA,'retained original test and final exact new guard')
 original=ast.parse(old_raw.decode('utf8'));current=ast.parse(new_raw.decode('utf8'))
 def methods(tree):
  return{n.name:n for c in tree.body if isinstance(c,ast.ClassDef)for n in c.body if isinstance(n,ast.FunctionDef)and n.name.startswith('test_')}
 def canonical(node):return ast.dump(node,include_attributes=False)
 a,b=methods(original),methods(current)
 changed=[n for n in a if canonical(a[n])!=canonical(b[n])]
 target='test_every_reward_query_including_target_is_exactly_unchanged'
 require(set(a)==set(b)and len(a)==9 and changed==[target],'all9 methods kept, one historical source guard changed,8 unchanged')
 require(all(canonical(x)==canonical(y)for x,y in zip(a[target].body[:-1],b[target].body[:len(a[target].body)-1])),
  'original38 reward loop and original baseline/hash assertions remain exact AST prefix')
 normalized=deepcopy(current)
 ast_imports=[n for n in normalized.body if isinstance(n,ast.Import)and len(n.names)==1 and n.names[0].name=='ast']
 require(len(ast_imports)==1 and not any(isinstance(n,ast.Import)and any(x.name=='ast'for x in n.names)for n in original.body),'one added ast import')
 normalized.body.remove(ast_imports[0])
 for c in normalized.body:
  if isinstance(c,ast.ClassDef):
   for i,n in enumerate(c.body):
    if isinstance(n,ast.FunctionDef)and n.name==target:c.body[i]=deepcopy(a[target])
 require(canonical(normalized)==canonical(original),'all module/class helpers/imports outside new ast and target method unchanged')
 baseline_name='verification/sections/295-preparation/pre295-query-baseline.json';baseline=load(baseline_name)
 require(digest(baseline_name)==proof['original_baseline_sha256']=='50799b7758d235963e97f3c844211abcce9cfcb3caf5b3be16a69495a347bb27',
  'original295 baseline bound and untouched')
 prior_name='verification/sections/298-preparation/before/rouge/node_catalog.py'
 require(digest(prior_name)==baseline['node_catalog_sha256']==proof['prior_full_source_sha256'],'complete real pre298 source still binds old hash')
 def reward_function(name):
  return next(n for n in ast.parse(path(name).read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef)and n.name=='event_reward_options')
 require(canonical(reward_function(prior_name))==canonical(reward_function('rouge/node_catalog.py')),'entire original/current reward query FunctionDef AST unchanged')
 first_name='verification/sections/301-necessary-attempt1/process.json';first=load(first_name)
 require(digest(first_name)==proof['source_first_failure_receipt_sha256']and first['section']==301 and first['exit_code']==1
  and first['timed_out']is False and first['source_unchanged']is True,'actual first99 failed original guard, not discarded or relabelled')
 stderr=path(first_name).with_name('stderr.txt').read_text(encoding='utf8')
 require('Ran 99 tests in 40.362s'in stderr and stderr.rstrip().endswith('FAILED (failures=1)')and ('FAIL: '+target)in stderr,
  'exact first failure scope and real terminal preserved')
 require(first['source_sha256_after'][TEST_REPAIR_PATH]==TEST_BEFORE_SHA,'first actual executed original test bytes')
 return{'receipt':TEST_REPAIR_PROOF,'sha256':TEST_REPAIR_PROOF_SHA,'test_file':TEST_REPAIR_PATH,
  'old_test_sha256':TEST_BEFORE_SHA,'new_test_sha256':TEST_AFTER_SHA,'test_methods':9,'changed_methods':1,'unchanged_test_method_AST':8,
  'all_other_module_and_class_AST_unchanged_except_ast_import':True,'original38_loop_and_baseline_unchanged':True,
  'prior_full_source':prior_name,'prior_full_source_sha256':digest(prior_name),'current_reward_function_AST_unchanged':True,
  'first_necessary_receipt':first_name,'first_necessary_receipt_sha256':digest(first_name),'first_actual_methods':99,'first_actual_exit':1,
  'first_actual_failures':1,'first_methods_added_to_final_pass_count':False,'production_or_reward_data_changed_for_repair':False}


def require(value,message):
 if value is not True:raise ValueError('301 closeout prerequisite: '+message)

def path(value):
 p=Path(value);p=p if p.is_absolute() else ROOT/p
 require(p.resolve().is_relative_to(ROOT.resolve()) and not p.is_symlink(),'regular public repository path')
 require(p.is_file(),'public file exists: '+str(value));return p

def rel(value):return path(value).resolve().relative_to(ROOT.resolve()).as_posix()

def digest(value):return sha256(path(value).read_bytes()).hexdigest()

def load(value):return json.loads(path(value).read_bytes())

def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')

def check_map(values,label):
 require(isinstance(values,dict) and bool(values),label+' nonempty map')
 for name,expected in values.items():
  require(isinstance(name,str) and not Path(name).is_absolute() and '..' not in Path(name).parts and '\\' not in name
    and isinstance(expected,str) and re.fullmatch('[0-9a-f]{64}',expected) is not None,label+' safe relative SHA path')
  require(digest(name)==expected,label+' final live exact bytes: '+name)

def owned_process(value,window_value,window):
 process=load(value);child=process['child_argv']
 require(len(child)==9 and Path(child[0]).resolve()==(ROOT/'.venv/Scripts/python.exe').resolve()
  and child[1:4]==['-B','-X','utf8'] and Path(child[4]).resolve()==(ROOT/CANONICAL).resolve()
  and child[5]=='--receipt' and child[7]=='--visible-ms' and re.fullmatch('[0-9]+',child[8])is not None and 0<int(child[8])<=120000,'canonical actual child argv, not a cache or synthetic result')
 raw=Path(child[6]);require(raw.is_absolute() and raw.name==path(window_value).name,'raw/public receipt basename preserved')
 require(process['section']==301 and process['kind']=='actual_native_window_owned_process_execution'
  and process['status']=='completed' and type(process['exit_code']) is int and process['exit_code']==0
  and type(process['child_primary_exit']) is int and process['child_primary_exit']==0 and process['timed_out'] is False
  and process['owned_job_no_live_execution_verified'] is True and process['source_before_after_unchanged'] is True
  and process['window_receipt_sha256']==digest(window_value),'actual supervisor+primary child0, owned job empty, exact report')
 argv=process['argv'];require(argv.count('--')==1 and argv[argv.index('--')+1:]==child
  and argv.count('--status')==1 and argv.count('--timeout')==1,'actual supervisor/child argv exact correspondence')
 status=Path(argv[argv.index('--status')+1]);require(status.is_absolute() and status.name==process['supervisor_receipt']=='supervisor.json'
  and 0<float(argv[argv.index('--timeout')+1])<=3690,'bounded owned supervisor raw status')
 spath=path(value).with_name('supervisor.json');sup=load(spath)
 require(sup['status']=='completed' and sup['argv']==child and type(sup['pid']) is int and sup['pid']>0
  and sup['supervisor_exit']==process['exit_code']==0 and sup['child_primary_exit']==process['child_primary_exit']==0
  and sup['timed_out'] is False and sup['owned_handle_retained'] is True and sup['owned_job_assigned'] is True
  and sup['owned_job_no_live_execution_verified'] is True and sup['global_process_termination'] is False
  and sup['game_operations']==sup['chat_requests']==0 and not sup.get('launch_or_supervision_error'),
  'original retained-Popen/owned-job terminal record, no invented natural all-descendant exit')
 sources=[Path(arg) for arg in argv[1:argv.index('--')] if isinstance(arg,str) and arg.endswith('.py')]
 require(len(sources)==1 and digest(sources[0])==process['supervisor_sha256']==sup['supervisor_sha256'],'actual supervisor source exact bytes')
 for channel in ('stdout','stderr'):
  row=sup[channel];require(Path(row['file']).name==row['file'],'public original log basename')
  log=spath.with_name(row['file']);require(digest(log)==row['sha256'] and path(log).stat().st_size==row['bytes'],'actual supervisor raw '+channel)
 return raw,{'receipt':rel(value),'sha256':digest(value),'supervisor_receipt':rel(spath),'supervisor_sha256':digest(spath),
  'actual_supervisor_exit':0,'actual_primary_child_exit':0,'owned_job_no_live_execution_verified':True,
  'supervisor_child_launch_pid':sup['pid'],'fixture_reported_pid':window['process_id'],'same_pid_required':False,
  'historical_ancestry_or_fixture_job_membership_verified':False,
  'cleanup':{'active_after_primary_child_exit':sup.get('owned_job_active_processes_after_child_exit'),
    'descendants_live_before_cleanup':sup.get('owned_descendants_still_live'),'termination_scope_recorded':sup.get('termination_scope'),
    'all_descendants_natural_exit_claimed':False}}

def original_window(main_value,focus_value,fixture,necessary_data,necessary_value,native_value):
 main,focus=load(main_value),load(focus_value)
 require(path(main_value).resolve()==(ROOT/'verification/sections/301-main-window.json').resolve()
  and path(focus_value).resolve()==(ROOT/'verification/sections/301-main-window-focus.json').resolve(),
  'strict same-section canonical301 main/focus receipt paths')
 require(main['section']==301 and focus['section']==301
  and main['necessary_receipt_sha256']==digest(necessary_value)
  and main['native_receipt_sha256']==digest(native_value)
  and main['native_receipt']==rel(native_value) and main['necessary_receipt']==rel(necessary_value)
  and focus['main_receipt_sha256']==digest(main_value),
  'actual301 main binds both final evidence receipts; focus binds exact same main bytes')
 require(main['source_sha256_before']==main['source_sha256_after']==fixture['source_sha256_after']
  and set(main['source_sha256_after'])==selected_window_sources(),
  'same final actual native_selected source map stable through original window restart')
 check_map(main['source_sha256_after'],'original301 window final native_selected sources')
 timestamps={name:datetime.fromisoformat(value.replace('Z','+00:00')) for name,value in {
  'started':main['started_utc'],'finished':main['finished_utc'],'focus':focus['at_utc'],
  'necessary_finished':necessary_data['finished_utc'],'native_finished':fixture['finished_at']}.items()}
 require(all(value.tzinfo is not None and value.utcoffset() is not None for value in timestamps.values()),
  'actual main/focus/final-check timestamps are timezone-aware')
 require(timestamps['started']>timestamps['necessary_finished'] and timestamps['started']>timestamps['native_finished']
  and timestamps['finished']>=timestamps['started'] and timestamps['focus']>=timestamps['finished'],
  'original301 restart occurs after both final validations; focus follows completed main receipt')
 require(main['passed'] is True and main['private_file_hash_comparison_count']==5 and main['private_hashes_equal'] is True
  and main['changed_private_paths']==[] and main['private_contents_parsed_copied_or_restored'] is False and main['no_private_restoration'] is True,
  'actual original-window update/private5 hash unchanged, no content parsing/copy/restore')
 require(len(main['visible_windows'])==1,'one visible original project window');visible=main['visible_windows'][0]
 require(visible['visible'] is True and visible['responding'] is True and visible['minimized'] is False and visible['hwnd']>0
  and visible['pid']!=fixture['process_id'],'original window responsive/visible and not fixture')
 require(focus['visible'] is True and focus['pid']==visible['pid'] and focus['hwnd']==focus['actual_foreground']==visible['hwnd'],
  'actual foreground original project window')
 return {'receipt':rel(main_value),'sha256':digest(main_value),'focus_receipt':rel(focus_value),'focus_sha256':digest(focus_value),
  'section':301,'necessary_receipt_sha256':digest(necessary_value),'native_receipt_sha256':digest(native_value),
  'native_selected_current_source_unchanged':True,'started_after_final_necessary_and_native':True,'focus_after_main_finished':True,
  'private_hash_comparisons':5,'changed_private_paths':0,'visible_responsive_foreground':True,'private_contents_read_by_helper':False}

def join_sources(necessary_map,native_map):
 common=set(necessary_map)&set(native_map);extra=set(native_map)-set(necessary_map)
 require(bool(common)and all(necessary_map[n]==native_map[n]for n in common),'all common necessary/native source bytes match')
 additional={}
 for name in sorted(extra):
  require(name.startswith('research/')and Path(name).suffix in{'.html','.json','.md','.png'},
   'native-only extra must be an existing public source document, never omitted product code or new runtime data')
  require(digest(name)==native_map[name],'actual native-only document still current')
  parent_bytes=subprocess.check_output(['git','show',PARENT+':'+name],cwd=ROOT)
  require(sha256(parent_bytes).hexdigest()==native_map[name],'native-only document exact unchanged parent bytes')
  additional[name]={'sha256':native_map[name],'native_actual_before_after_guarded':True,
   'current_file_verified':True,'parent_blob_verified':True,'parent_commit':PARENT,'absent_from_necessary_map':True}
 return{'necessary_source_files':len(necessary_map),'native_selected_source_files':len(native_map),
  'common_source_files':len(common),'native_is_subset_of_necessary':not bool(extra),
  'additional_native_document_sources':additional,'joined_source_files':len(set(necessary_map)|set(native_map)),
  'arbitrary_missing_sources_permitted':False}

def visual_review(value,window):
 name='verification/sections/301-preparation/root-visual-review.json';review=load(name)
 require(review['section']==301 and review['kind']=='root_archived_native_images_review'
  and review['actual_images_opened_with_view_image']is True,'root actually reviewed new301 images')
 expected={rel(path(value).with_name(Path(row['path']).name)):row['sha256']for row in window['screenshots']}
 require(review['images']==expected and review['actual_image_count']==len(expected),'root visual review exact all actual images')
 return{'receipt':name,'sha256':digest(name),'actual_root_reviewed_images':len(expected),'helper_performed_visual_review':False}

def selected_window_sources():
 # The already-reviewed canonical script has no product/Qt import at module scope.
 # Its explicit public-byte bound_files() is the actual producer, not guessed counts.
 result=runpy.run_path(str(path(CANONICAL)))['bound_files']()
 check_map(result,'canonical selected public source producer')
 return set(result)

def preparation_archive(value):
 record=load(value);require(record['section']==301 and type(record['files'])is dict and bool(record['files']),'public preparation archive exact section and nonempty inventory')
 base=path(value).parent
 for name,pin in record['files'].items():
  require(type(name)is str and not Path(name).is_absolute()and'..'not in Path(name).parts and'\\'not in name,'relative public preparation member')
  member=base/name
  require(digest(member)==pin['sha256']and path(member).stat().st_size==pin['bytes'],'exact retained preparation/first evidence '+name)
 return{'receipt':rel(value),'sha256':digest(value),'member_count':len(record['files']),
  'preparation_or_author_checks_added_to_product_pass_count':False}

def necessary(value):
 data=load(value)
 require(data['section']==301 and data['kind']=='necessary_change_related_tests_not_full_suite'
  and type(data['exit_code'])is int and data['exit_code']==0 and data.get('timed_out',False)is False
  and data['source_unchanged']is True and data['source_sha256_before']==data['source_sha256_after'],'actual final necessary0/stable')
 modules=data['modules'];require(type(modules)is list and len(modules)==len(set(modules))and REQUIRED_MODULES<=set(modules)
  and data['argv'][1:7]==['-B','-X','utf8','-m','unittest','-v']and data['argv'][7:]==modules
  and data['source_commit_before']==PARENT,'complete actual selected modules include all three new contracts; exact parent')
 require(data['game_sampling_verified']is False and data['chat_verified']is False and data['full_scope_reduced']is False
  and data['full_suite_rerun']is False,'necessary only, not full/game/chat')
 minimum={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/**/*.py')}
 minimum|={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/data/*.json')}
 minimum|={'tests/'+m.split('.')[-1]+'.py'for m in modules}|selected_window_sources()|{BUILDER,'verification/sections/298-preparation/before/rouge/node_catalog.py'}
 require(minimum<=set(data['source_sha256_after']),'actual necessary map covers product Python/data and all selected native/source files')
 check_map(data['source_sha256_after'],'actual necessary source')
 previous=load('verification/sections/300.json')['necessary_validation'];require(digest(previous['receipt'])==previous['sha256'],'previous necessary exact public source')
 old=load(previous['receipt']);kept={n:v for n,v in old['source_sha256_after'].items()if n.startswith('rouge/')and n not in CHANGED_EXISTING
  and(n.endswith('.py')or(n.startswith('rouge/data/')and n.endswith('.json')))}
 require(bool(kept)and all(data['source_sha256_after'].get(n)==v for n,v in kept.items()),'all old product Python/staticJSON except sole parent panel unchanged')
 tracked_tests=set(subprocess.check_output(['git','ls-tree','-r','--name-only',PARENT,'--','tests'],cwd=ROOT,text=True).splitlines())
 changed_tests=set(subprocess.check_output(['git','diff','HEAD','--name-only','--','tests'],cwd=ROOT,text=True).splitlines())
 require(tracked_tests&changed_tests=={TEST_REPAIR_PATH},'only exact historical295 guard test maintained');repair=historical_test_maintenance()
 first_record=load('verification/sections/301-necessary-attempt1/process.json')
 require(modules==first_record['modules'],'same complete ordered9 modules after minimal guard migration')
 first=first_record['source_sha256_after'];final=data['source_sha256_after']
 require(set(final)==set(first)|{'verification/sections/298-preparation/before/rouge/node_catalog.py'},'same complete necessary source frame plus exact original-source input')
 require({n for n in first if final[n]!=first[n]}=={TEST_REPAIR_PATH}and final[TEST_REPAIR_PATH]==TEST_AFTER_SHA,
  'all first-run product/data/native bytes unchanged; only exact historical test guard source differs')
 log=path(value).with_name('stderr.txt');text=log.read_text(encoding='utf8');counts=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',text)
 require(len(counts)==1 and int(counts[0][0])>0 and text.rstrip().endswith('OK')and not re.search(r'^(FAIL|ERROR):',text,re.M),'actual Ran/OK original result')
 return data,{'receipt':rel(value),'sha256':digest(value),'stderr':rel(log),'stderr_sha256':digest(log),
  'stdout_sha256':digest(path(value).with_name('stdout.txt')),'actual_exit':0,'methods_run':int(counts[0][0]),'seconds':float(counts[0][1]),
  'source_files':len(data['source_sha256_after']),'source_unchanged':True,'modules':modules,
  'unchanged_existing_product_Python_static_JSON_files':len(kept),'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),
  'old_tracked_test_maintenance':True,'historical_test_guard':repair,'author_preparation_checks_are_subsets_not_added':True}

def necessary_attempt_history(final_value):
 result=[];final=path(final_value).resolve()
 for record_path in sorted((ROOT/'verification/sections').glob('301-necessary-*/process.json')):
  if record_path.resolve()==final:continue
  record=load(record_path);require(record['section']==301,'same-section actual necessary history only')
  stderr=record_path.with_name('stderr.txt');text=path(stderr).read_text(encoding='utf8')
  match=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',text)
  ending=re.findall(r'FAILED \(([^)]+)\)',text)
  result.append({'receipt':rel(record_path),'sha256':digest(record_path),'stderr':rel(stderr),'stderr_sha256':digest(stderr),
   'actual_exit':record['exit_code'],'timed_out':record.get('timed_out',False),
   'observed_methods':int(match[-1][0])if match else None,'observed_failure_summary':ending[-1]if ending else None,
   'source_before_after_unchanged':record['source_sha256_before']==record['source_sha256_after'],
   'counts_added_to_final_methods_passed':False,'prior_attempt_not_relabelled_as_final':True})
 return result

def promotion(value,tests,reviewed_sha):
 record=load(value)
 require(record['section']==301 and record['parent_commit']==PARENT and record['old_tests_modified']is True
  and set(record['existing_production_changes'])==CHANGED_EXISTING,'exact sole old production seam and parent')
 expected={CANONICAL,DATA,MANIFEST,BUILDER,'rouge/named_reward_items.py','rouge/named_reward_items_view.py',
  *('tests/'+m.split('.')[-1]+'.py'for m in REQUIRED_MODULES)}
 expected|={p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file()}
 require(set(record['promoted'])==expected and record.get('native_script_pending',False)is False,'complete actual new functionality promotion includes canonical native')
 for name,pin in record['promoted'].items():
  require(type(pin)is str and digest(name)==pin,'exact promoted public byte '+name)
 for name,pin in record['existing_production_changes'].items():
  require(type(pin)is str and digest(name)==pin,'exact sole old panel final byte')
  parent_bytes=subprocess.check_output(['git','show',PARENT+':'+name],cwd=ROOT)
  require(sha256(parent_bytes).hexdigest()==record['before_existing_sha256'][name],'actual parent seam before bytes')
 require(record['existing_test_maintenance']=={TEST_REPAIR_PATH:TEST_AFTER_SHA}and record['before_test_sha256']=={TEST_REPAIR_PATH:TEST_BEFORE_SHA},
  'exact sole historical test maintenance and before bytes')
 require(record['repair_proof']=={'receipt':TEST_REPAIR_PROOF,'sha256':TEST_REPAIR_PROOF_SHA},'promotion binds reviewed exact migration proof')
 require(digest(TEST_REPAIR_PATH)==TEST_AFTER_SHA,'actual final historical guard bytes')
 historical_test_maintenance()
 require(digest(CANONICAL)==reviewed_sha,'final explicitly reviewed native source')
 final={n:digest(n)for n in sorted(expected|CHANGED_EXISTING|{TEST_REPAIR_PATH})}
 require(all(tests['source_sha256_after'].get(n)==v for n,v in final.items()),'all final functional sources in actual necessary map')
 return final,{'receipt':rel(value),'sha256':digest(value),'new_functional_paths_including_final_native':len(expected),
  'feature_paths_including_existing':len(final)-1,'functional_source_paths':len(final)-1,'validated_source_paths_including_test_maintenance':len(final),'old_test_is_maintenance_not_new_functionality':True,'canonical_native_separately_bound':{'path':CANONICAL,'sha256':reviewed_sha},
  'existing_production_paths':1,'existing_test_maintenance_paths':1,'old_tracked_test_maintenance':True,'promotion_is_provenance_not_acceptance':True}

def packet():
 require(digest(MANIFEST)==MANIFEST_SHA and digest(DATA)==DATA_SHA,'fixed301 authority/data exact bytes')
 manifest=load(MANIFEST);data=load(DATA)
 require(manifest['schema']=='named_reward_items_source_manifest_v1'and manifest['data_file']==DATA
  and manifest['data_sha256']==DATA_SHA and manifest['runtime_reads_complete_primary_table']is False
  and manifest['runtime_verifies_complete_build_original_bytes']is False
  and manifest['all_package_runtime_members_required_for_each_target_query']is True,'full package failclosed, selected runtime vs build originals')
 for name,pin in manifest['files'].items():
  check_map({name:pin['sha256']},'complete public build/runtime source');require(path(name).stat().st_size==pin['bytes'],'exact source byte length')
 require(set(manifest['runtime_files'])<=set(manifest['files'])and set(manifest['runtime_files']).isdisjoint(manifest['build_authority_files']),
  'runtime selected and original build authorities not conflated')
 require(all(v==manifest['files'][n]for n,v in manifest['runtime_files'].items()),'runtime pin equals source inventory pin')
 rows=data['choices'];events={r['event_id']for r in rows};items=data['items'];icons=data['icons']
 counts={'original_typed':len(data['expected_original_rewards']),'bound_choices':len(rows),'events':len(events),'items':len(items),
  'relics':len(data['relics']),'scraps':sum(v['type']=='SCRAP'for v in items.values())}
 require(counts==manifest['counts']=={'original_typed':17,'bound_choices':16,'events':10,'items':13,'relics':12,'scraps':1},'exact fixed16/10/13 reading scope, original17 unchanged')
 require(len({(r['event_id'],r['scene_key'],r['choice_key'])for r in rows})==16
  and all(r['reference_id']==r['choice_key']and r['quantity_reference']is None for r in rows),'unique exact choice tuples, no unknown quantity default')
 require(all(r['original_choice_id']!='choice_ro6_rest_4'for r in rows)and data['unbound_original_choice_ids_not_restored']==['choice_ro6_rest_4'],
  'unbound ticket not restored by image reading')
 require(data['inventory_updated']is False and data['current_server_verified']is False and data['original_entry_restored']is False,'no actual run/server/entry conclusion')
 require(set(icons)==set(items)and all(icons[k]['item_id']==k and icons[k]['icon_id']==v['iconId']for k,v in items.items()),'exact original item/icon identities')
 baseline=load(PACKET+'/prior-38-reward-query-baseline.json');require(len(baseline['queries'])==38 and baseline['existing_typed_count']==17,'complete original38 query baseline bound')
 return{'manifest':MANIFEST,'manifest_sha256':MANIFEST_SHA,'data':DATA,'data_sha256':DATA_SHA,
  'source_members':len(manifest['files']),'runtime_fresh_members':len(manifest['runtime_files']),
  'runtime_fresh_bytes_including_manifest':sum(p['bytes']for p in manifest['runtime_files'].values())+path(MANIFEST).stat().st_size,
  'runtime_verifies_complete_original_bytes':False,'complete_build_originals_retained_and_hash_verified_at_closeout':True,
  'fixed_choice_count':16,'fixed_event_count':10,'fixed_item_count':13,'fixed_relic_count':12,'fixed_scrap_count':1,
  'original_typed_count':17,'prior_reward_query_count':38,'whole_package_failclosed_on_any_runtime_member':True,
  'actual_quantity_claim_held_effect_or_eligibility_verified':False}

def native(value,process_value,tests,reviewed_sha):
 data=load(value)
 require(data['section']==301 and data['kind']=='isolated_native_windows_named_reward_items_reader'and data['passed']is True
  and data['failure']is None and data['qpa']=='windows'and type(data['qt_exit_code'])is int and data['qt_exit_code']==0
  and data['verification_window_closed']is True,'actual complete native Windows reader, Qt0 and closed')
 require(type(data['process_id'])is int and data['process_id']>0 and digest(CANONICAL)==reviewed_sha,'actual fixture PID and canonical source byte')
 tree=ast.parse(path(CANONICAL).read_text(encoding='utf8'))
 labels={n.args[1].value for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='require'
  and len(n.args)>1 and isinstance(n.args[1],ast.Constant)and type(n.args[1].value)is str}
 require(type(data['checks'])is list and len(data['checks'])==len(set(data['checks']))==data['unique_checks']
  and labels<=set(data['checks'])and data['successful_assertion_executions_including_repeated_guards']>=len(data['checks']),'all reviewed native labels actually recorded, dynamic counts')
 require(data['source_sha256_before']==data['source_sha256_after']and set(data['source_sha256_after'])==selected_window_sources()
  and data['source_guard_is_selected_not_all_transitive_dependencies']is True,'selected source map exact and stable')
 require(TEST_REPAIR_PATH not in data['source_sha256_after'],'historical guard test is outside unchanged actual native selected source closure');check_map(data['source_sha256_after'],'native301');joined=join_sources(tests['source_sha256_after'],data['source_sha256_after'])
 require(data['temporary_state_root']is True and data['state_paths_replaced_before_constructor']==['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE']
  and data['private_state_read_copied_or_restored']is False and data['external_entrypoints_blocked_before_original_call']is True,'temp four paths before constructor; no private copy/read')
 ops=data['external_operation_attempts'];require(set(ops)=={'game_enumeration','game_connect','game_capture','game_next_frame','desktop_start','desktop_request','provider_chat','credential_read'}
  and all(type(v)is int and v==0 for v in ops.values()),'eight actual external attempt counters zero')
 require(data['game_operated']is False and data['game_captures']==0 and data['chat_sent']is False and data['chat_attempted']is False
  and data['original_project_window_operated_or_restarted']is False and data['actual_process_termination_verified_by_this_script']is False
  and data['owned_supervisor_exit_and_cleanup_required_separately']is True
  and data['launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID']is True
  and data['actual_reward_quantity_claim_held_effect_eligibility_verified']is False,'no actual game/effect/ancestry/terminal claims from fixture')
 raw,process=owned_process(process_value,value,data)
 require(data['requested_parent_client_size']==[1050,720]and data['requested_dialog_client_size']==[900,680],'actual requested parent and reader sizes')
 rows=data['actual_choice_readings'];expected_rows=load(DATA)['choices'];expected_icons=load(DATA)['icons']
 tuples={(r['event_id'],r['scene_key'],r['choice_key'])for r in expected_rows}
 require(len(rows)==16 and{(r['event_id'],r['scene_key'],r['choice_key'])for r in rows}==tuples
  and len({r['event_id']for r in rows})==10,'all16 exact tuples from10events actually read')
 for row in rows:
  expected=next(r for r in expected_rows if(r['event_id'],r['scene_key'],r['choice_key'])==(row['event_id'],row['scene_key'],row['choice_key']))
  require(all(row[k]==expected[k]for k in('reference_id','original_choice_id','item_id','item_kind','condition_text'))
   and row['icon_file']==expected_icons[row['item_id']]['file']and row['icon_sha256']==expected_icons[row['item_id']]['sha256']
   and row['actual_reward']is None and row['actual_quantity']is None and row['inventory_updated']is False,'each actual row complete identity/condition/exact icon, no actual reward')
 require(data['actual_distinct_item_images']==expected_icons,'13 exact original icon objects actually decoded and shown')
 refresh=data['same_scope_refresh_observations'];require(len(refresh)==4 and{r['path']for r in refresh}=={
  'unselected_parent','selected_dialog','selected_parent','selected_same_reference'}
  and all(r['source_scroll']>0 and r['source_selection']and r['parent_unchanged']is True for r in refresh)
  and sum(r['choice']is None for r in refresh)==1,'actual unselected and3selected refreshes preserve reader and parent')
 icon=expected_icons['rogue_6_scrap_G_12']
 require(data['source_negative_fixtures']==[{'kind':'warm_nonselected_icon','damaged_member':icon['file'],'public_clone_only':True,
  'all_target_references_unknown':True,'restored_sha256':icon['sha256'],'actual_reward':None}],
  'nonselected image damage invalidates whole package, restoration does not reselect')
 history=data['historical_readings'];require(len(history)==1 and history[0]['event_id']=='community_group_005'
  and history[0]['choice_key']=='community_group_005:scene:0:choice:2'and history[0]['historical_reference_only']is True
  and history[0]['caller_graph_unchanged']is True and history[0]['actual_eligible']is None,'historical title remains manual reference, graph and eligibility preserved')
 names={'player-ordinary-multi-item','player-repeated-item-condition','player-scrap-cage-controller','player-deep-scene-dog-sap','player-deep-scene-burned-civilization'}
 images=data['screenshots'];require(data['screenshot_count']==len(images)==len(names)and{r['name']for r in images}==names
  and all(r['direct_player_text']is True and r['exact_icon_visible']is True for r in images),'five actual player images include unique exact visible item icons')
 handles={}
 def handle(row):
  sizes={'parent':[1050,720],'dialog':[900,680]}
  require(row['kind']in sizes and row['client_size']==sizes[row['kind']]and row['qpa']=='windows'
   and type(row['hwnd'])is int and row['hwnd']>0 and row['process_id']==data['process_id'],'real exact native owned HWND/PID/size')
  handles.setdefault(row['kind'],set()).add(row['hwnd'])
 require(bool(data['native_observations']),'actual native HWND observations')
 for row in data['native_observations']:handle(row)
 for image in images:
  file=raw.with_name(raw.stem+'-'+image['name']+'.png');require(Path(image['path']).resolve()==file.resolve(),'exact raw screenshot source path')
  blob=path(path(value).with_name(file.name)).read_bytes()
  require(sha256(blob).hexdigest()==image['sha256']and blob[:8]==b'\x89PNG\r\n\x1a\n'and len(blob)>24
   and all(v>0 for v in struct.unpack('>II',blob[16:24])),'actual PNG bytes/dimensions');handle(image['native_window'])
 require(set(handles)=={'parent','dialog'}and all(len(s)==1 for s in handles.values())and len(set.union(*handles.values()))==2,'distinct actual main and modeless reader handles')
 return data,{'receipt':rel(value),'sha256':digest(value),'reviewed_native_source_sha256':reviewed_sha,
  'source_selected_files':len(data['source_sha256_after']),'source_unchanged':True,'source_join':joined,'native_selected_source_excludes_historical_test_maintenance':True,'native_runtime_and_production_sources_unchanged_across_test_only_repair':True,
  'unique_checks':data['unique_checks'],'actual_assertion_executions':data['successful_assertion_executions_including_repeated_guards'],
  'representative_images':len(images),'screenshots':len(images),'actual_player_reader_images':len(images),
  'actual_Qt_exit':0,'owned_process':process,'actual_claim_quantity_held_effect_or_eligibility_verified':False,'game_or_chat_verified':False}

def main(args):
 require(Path(__file__).resolve()==(HERE/'close_section_301.py').resolve(),'canonical cache closeout helper')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 require(branch=='codex/p2-development'and parent==PARENT and not(ROOT/'verification/sections/301.json').exists(),'exact authorized branch/parent; exclusive301 receipt')
 require(digest(CANONICAL)==args.native_source_sha256,'approved native bytes checked before its selected-source producer')
 source_ref=packet();archive_ref=preparation_archive(args.preparation_archive_manifest);tests,test_ref=necessary(args.necessary_receipt)
 feature_map,promotion_ref=promotion(args.promotion_receipt,tests,args.native_source_sha256)
 window,window_ref=native(args.window_receipt,args.window_process_receipt,tests,args.native_source_sha256)
 window_ref['root_visual_review']=visual_review(args.window_receipt,window)
 main_ref=original_window(args.main_window_receipt,args.focus_receipt,window,tests,args.necessary_receipt,args.window_receipt)
 full=load(FULL);require(digest(FULL)==FULL_SHA and full['after_section']==290 and full['available_checks_passed']is True
  and full['scope_not_reduced']is True and full['complete_repository_validation']is False,'only original historical290 available full reused')
 cp=load('DEVELOPMENT_CHECKPOINT.json')
 require(cp['completed_sections']==cp['latest_functional_section']==300 and cp['next_section']==301 and cp['active_section']['section']==301
  and cp['policy']['priority_order']==['P3','P2','P1']and cp['policy']['current_user_batch_target_section']is None
  and cp['policy']['stop_after_section']is None,'active301/P3-first/no numeric endpoint')
 require(cp['last_full_validation']['after_section']==290 and cp['current_available_full_validation']['section']==290
  and cp['policy']['full_validation_interval']==15 and cp['policy']['full_validation_anchor_section']==125
  and 125+((301-125)//15+1)*15==305,'unchanged full cadence/original290 proof')
 cloud=cp['last_verified_cloud_save'];proof=load(cloud['proof'])
 require(cloud['section']==300 and digest(cloud['proof'])==cloud['proof_sha256']and proof['passed']is True
  and proof['commit']==proof['remote_HEAD']==cloud['commit']and proof['push_primary_exit']==0,'actual previous300 ordinary publication')
 docs={n:path(n).read_bytes()for n in('DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','AGENTS.md')}
 progress=path('PROJECT_PROGRESS.md').read_bytes();require(sha256(progress).hexdigest()==PROGRESS_SHA_BEFORE,'remaining work not falsely retired by fixed source candidate reading')
 now=datetime.now(timezone(timedelta(hours=8))).isoformat()
 capability=('10个事件的16条精确选项可手动查看13种具名物品的原图标、用途、完整说明与解锁原文；'
  '重复物品的不同条件分开保留，区分12种收藏品和1种零件，默认未选，手选即显示图文。'
  '同范围刷新保留阅读；换范围或任一运行期资料/图标失效清旧图文，恢复后重新手选，不写本局或勾选计算藏品。')
 limits=['13种物品图文是阅读能力，不是13种新奖励机制；原17typed与38reward query保持，数量、完整池、本局资格/领取/持有/生效及当前服务器一致性仍未知。',
  'choice_ro6_rest_4仍未绑定，不补原入口；图鉴解锁说明不是当前选项门槛。笼控器是零件，无relic对象，不借相似图片。',
  '运行期fresh约3.14MB精选资料/目录/17记录/38query基线/代码/13图，完整17.9MB原表复用300公开文件只在构建核对；不是每call重读完整原表。',
  '不减少17typed奖励、15全局层数、25场景/57选项、10未解析附注、完整地图81/59或逐格10图18关58点的剩余边界。',
  '本节必要与原生流程；290全量仅沿用原来源，下次305。P3/P2/P1未完成、识别最后，无路线推荐或数字终点。']
 receipt={'section':301,'kind':'functional_section','title':TITLE,'at_Beijing':now,'branch':branch,'prior_commit':parent,
  'remaining_item':'P3既有具名奖励的完整图文与精确节点选项对应','new_capability':capability,
  'files':sorted(feature_map),'source_sha256':feature_map,'source_reference':source_ref,'source_promotion':promotion_ref,'preparation_archive':archive_ref,
  'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),'existing_source_changes_including_test_maintenance':sorted(CHANGED_EXISTING|{TEST_REPAIR_PATH}),
  'old_tracked_test_maintenance':True,'historical_test_maintenance':historical_test_maintenance(),'actual_server_generation_or_inventory_verified':False,
  'remaining_global_stage_floor_gaps_unchanged':15,'original_entry_gaps_unchanged':[25,57],'unparsed_notes_unchanged':10,
  'typed_named_grant_count_unchanged':17,'partial_direct_reference_scope_unchanged':[10,18,58],'whole_map_gaps_unchanged':[81,59],
  'necessary_validation':test_ref,'necessary_attempt_history':necessary_attempt_history(args.necessary_receipt),'native_windows_validation':{**window_ref,'original_project_window':main_ref},
  'full_validation':{'receipt':FULL,'sha256':FULL_SHA,'after_section':290,'full_suite_rerun':False,'new301_source_full_validation_claimed':False,
   'next_periodic_section':305,'scope_not_reduced':True,'complete_repository_validation':False},
  'PROJECT_PROGRESS_unchanged_sha256':PROGRESS_SHA_BEFORE,'limits':limits,'next_section':302,
  'cloud_publication_binding':'enclosing_commit','cloud_published':False,'P3_complete':False,'P2_complete':False}
 history='historical_before301_current_pointers';require(history not in cp,'exclusive301 pointer archive')
 cp[history]={k:deepcopy(cp[k])for k in('current_section_save','current_section_validation','latest_section_environment','active_section','current_batch','cloud_publication_closeout')if k in cp}
 cp.pop('active_section',None);cp.pop('cloud_publication_closeout',None)
 cp.update(completed_sections=301,latest_functional_section=301,next_section=302,batch_status='P3_SECTION301_VALIDATED_AWAITING_PUBLICATION',
  next_full_validation_after=305,next_action='从302继续有证P3剩余事项，无数字终点；下次完整可用全量305。')
 cp['policy']['next_full_validation_after']=305;cp['current_batch_commit_policy']['next_full_validation_after']=305
 cp['current_batch'].update(status=cp['batch_status'],next_section=302,next_section_started=False,receipt='verification/sections/301.json',next_full_validation_after=305,batch_closed=False)
 cp['confirmed_next_stage_direction'].update(last_completed_functional_section=301,next_functional_section_started=False)
 cp['sections'].append({'number':301,'completion_ref':'p3-section-301','topic':TITLE,'verification':'verification/sections/301.json'})
 cp['current_section_save']={'section':301,'verification':'verification/sections/301.json','scope':'current_functional_section',
  'binding':'enclosing_commit','commit_reference':'commit containing301 exact named reward item reader, real acceptance, requirements and index'}
 cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_section_validation']={'section':301,'receipt':'verification/sections/301.json','necessary_methods_passed':test_ref['methods_run'],
  'native_isolated_window_checks':window['unique_checks'],'full_suite_rerun':False,'last_full_receipt':FULL,'full_source_is_historical290':True}
 cp['latest_section_environment']={'section':301,'receipt':'verification/sections/301.json',
  'native_windows':f"{test_ref['methods_run']} actual necessary; {window['unique_checks']} unique native; {window_ref['screenshots']} representative PNG including player text; original visible/private5 unchanged",
  'native_game_or_chat_verified':False,'current_section_full_rerun':False,'new_Linux_Wine_full_run':False,'last_full_receipt':FULL}
 cp['functional_sections_since_latest_requirement']=list(dict.fromkeys([*cp['functional_sections_since_latest_requirement'],301]))
 completed=(f'## 功能第301节 · {TITLE}\n\n{now}。{capability}\n\n'
  f"实际{test_ref['methods_run']}必要检查、原生{window['unique_checks']}唯一检查通过；{window_ref['screenshots']}张代表PNG由根代理查看，包含重复物品条件、零件及深层场景选项的玩家正文和图标；原项目窗口更新/私人5路径不变。"
  '来源及原回执verification/sections/301.json；16选项与13物品只是既有资料阅读，不推本局实际领取、持有或生效，不减少其它入口、奖励或地图待办。'
  '伴随维护旧295整文件guard为原件SHA与奖励函数AST守卫，原38对照保持；首99失败原件保留不计入最终通过数。290全量原来源沿用，下次305，后续302，无数字终点。待普通推送核对。\n\n')
 mutations={'verification/sections/301.json':encode(receipt),'DEVELOPMENT_CHECKPOINT.json':encode(cp),'PROJECT_COMPLETED.md':completed.encode()+docs['PROJECT_COMPLETED.md']}
 wip=docs['WORK_IN_PROGRESS.md'].decode();require('## 功能第300节'in wip,'preserve prior300 history')
 mutations['WORK_IN_PROGRESS.md']=(completed+wip[wip.index('## 功能第300节'):]).encode()
 req=docs['PROJECT_REQUIREMENTS.md'].decode();a,b=req.index('<!-- current-delivery:start -->'),req.index('<!-- current-delivery:end -->')
 block=('<!-- current-delivery:start -->\n## 当前交付与续接 · 第301节\n\n2026-10-16继续P3，无数字终点。'+capability
  +f"实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过；原窗口更新/私人5路径不变。"
  +'固定物品说明不等于本局领取、生效、数量或概率；17typed、15/25/57/10与81/59待办保持。290全量原来源/下次305；P3→P2→P1、识别最后，无路线建议。待普通推送核对。\n')
 mutations['PROJECT_REQUIREMENTS.md']=(req[:a]+block+req[b:]).encode()
 agents=docs['AGENTS.md'].decode();a,b=agents.index('## 当前续接 · 第300节'),agents.index('## 当前优先顺序与输出可读性')
 mutations['AGENTS.md']=(agents[:a]+'## 当前续接 · 第301节已完成功能与必要/原生验收\n\n'+capability
  +'来源及实际回执verification/sections/301.json；实际领取、持有、数量与生效仍未知，17typed与15/25/57/10待办不变。'
  +'原窗口更新/私人5路径不变；未跑301全量，290完整范围沿用原来源。下一节302/下次305，无数字终点。'
  +'P3→P2→P1、识别最后，不推荐/排序/自动选路；待普通推送核对，源码/要求/验收/索引同提交。\n\n'+agents[b:]).encode()
 require('初次招募时即处于已进阶状态'in mutations['PROJECT_REQUIREMENTS.md'].decode()and'初次招募即处于已进阶状态'in mutations['AGENTS.md'].decode(),'verified直升 terminology preserved')
 require(all(str(i)+'.'in mutations['AGENTS.md'].decode().split('## 当前续接')[0]for i in range(1,6)),'highest five judgment/source requirements preserved')
 archive=ROOT/'verification/sections/301-preparation/closeout-tools';require(not archive.exists(),'exclusive closeout source archive')
 copies={'close_section_301.py':path(HERE/'close_section_301.py').read_bytes(),'CONTRACT.md':path(HERE/'CONTRACT.md').read_bytes()}
 copies.update({'before-'+name:raw for name,raw in docs.items()})
 archive_manifest={'kind':'SECTION301_PUBLIC_CLOSEOUT_TOOLS_NOT_PRIVATE_STATE','files':{n:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}for n,raw in copies.items()},'private_contents_or_hash_lists_copied':False}
 print(json.dumps({'gates_passed':True,'apply_requested':args.apply,'necessary_actual_methods':test_ref['methods_run'],'native_actual_unique_checks':window['unique_checks'],
  'source_join':window_ref['source_join'],'functional_source_paths':len(feature_map)-1,'validated_source_paths_including_test_maintenance':len(feature_map),'planned_public_files':list(mutations),'PROJECT_PROGRESS_modified':False,
  'full_rerun':False,'next_full_section':305,'numeric_endpoint':None,'cloud_published':False},ensure_ascii=False))
 if not args.apply:return
 for name,raw in docs.items():require(path(name).read_bytes()==raw,'document unchanged before apply '+name)
 require(path('PROJECT_PROGRESS.md').read_bytes()==progress,'remaining work unchanged before apply')
 check_map(tests['source_sha256_after'],'prewrite actual necessary');check_map(window['source_sha256_after'],'prewrite actual native')
 archive.mkdir(parents=True)
 for name,raw in copies.items():
  with(archive/name).open('xb')as stream:stream.write(raw)
 with(archive/'archive-manifest.json').open('xb')as stream:stream.write(encode(archive_manifest))
 for name,raw in mutations.items():
  target=ROOT/name;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb'if name=='verification/sections/301.json'else'wb')as stream:stream.write(raw)
 print(json.dumps({'section':301,'local_closeout_written':True,'cloud_published':False,'next_section':302,'next_full_section':305}))

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--necessary-receipt',required=True);parser.add_argument('--window-receipt',required=True)
 parser.add_argument('--window-process-receipt',required=True);parser.add_argument('--native-source-sha256',required=True)
 parser.add_argument('--promotion-receipt',default='verification/sections/301-preparation/final-promotion.json')
 parser.add_argument('--preparation-archive-manifest',default='verification/sections/301-preparation/preparation-archive-manifest.json')
 parser.add_argument('--main-window-receipt',default='verification/sections/301-main-window.json')
 parser.add_argument('--focus-receipt',default='verification/sections/301-main-window-focus.json')
 parser.add_argument('--apply',action='store_true');main(parser.parse_args())
