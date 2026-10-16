"""Strict298 public closeout template. Preview by default; root-only --apply.
Unexecuted preparation. No product imports, Qt/tests, game/chat/private operation or Git mutation.
"""
import argparse,ast
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,re,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'.cache/p3-298-runtime-preparation/closeout-v3'
PARENT='bb4927a2a2760d48882f3945b750053d7a5617fc'
TITLE='六项事件的自然主层已知禁区与已读资料保留'
CANONICAL='scripts/verify_event_node_requirements_window_298.py'
PACKET='research/p3-event-node-requirements-298'
MANIFEST=PACKET+'/source-manifest.json';DATA='rouge/data/event-node-requirements.json'
BUILDER='scripts/build_event_node_requirements_298.py'
BASELINE='verification/sections/298-preparation/before-output.json'
BASELINE_SHA='68f0d3cd7d116ced58046fb4d40570620b066e6c6303c771db687f53d123ca7b'
MANIFEST_SHA='38638685b5b5084cbd3e81ff1c288a6d89c97c67cdc34fa72299a7997aa621ed'
DATA_SHA='f11c6d83a048ffdea14cbccdd1506ff02c3ef35a1cf94f107e30845b2d1deab3'
FULL='verification/full-290/summary.json'
FULL_SHA='2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
RULES={'community_group_024':[1,5,6],'community_group_025':[1,6],
 'community_group_027':[1,2,6],'community_group_028':[1,2,6],
 'community_group_029':[1,2,6],'community_group_037':[1]}
CHECK='documented_node_natural_main_floor'
MAINTAINED_TEST='tests/test_node_catalog.py'
OLD_TEST_SHA='79a65deeb3a49adcede74ab8606ee26763987492f65c4ee35fc72f51d6404916'
FIRST_TEST_SHA='6d5ea92a97a4181a36cdd4b945f19c92fa171cdbb8801c9fece94debc0af3aef'
NEW_TEST_SHA='daebfe930079810c7d057699d8fc3bb4f0f8dee46309df3a624a9b087338436a'
CHANGED_EXISTING={'rouge/node_catalog.py','rouge/event_planning.py','rouge/node_catalog_view.py','rouge/player_node_information.py'}
MODULES=['tests.test_event_node_requirements_298','tests.test_event_node_requirements_integration_298',
 'tests.test_event_node_requirements_view_298','tests.test_node_catalog','tests.test_event_planning',
 'tests.test_player_node_information_286','tests.test_node_catalog_view','tests.test_expedition_integration_297']
PROGRESS_SHA_BEFORE='111962b1622515c494ae81a06ac19b915db797211e926165a9947b80fade8a0b'


def require(value,message):
 if value is not True:raise ValueError('298 closeout prerequisite: '+message)

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
 require(process['section']==298 and process['kind']=='actual_native_window_owned_process_execution'
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
 require(path(main_value).resolve()==(ROOT/'verification/sections/298-main-window.json').resolve()
  and path(focus_value).resolve()==(ROOT/'verification/sections/298-main-window-focus.json').resolve(),
  'strict same-section canonical298 main/focus receipt paths')
 require(main['section']==298 and focus['section']==298
  and main['necessary_receipt_sha256']==digest(necessary_value)
  and main['native_receipt_sha256']==digest(native_value)
  and main['native_receipt']==rel(native_value) and main['necessary_receipt']==rel(necessary_value)
  and focus['main_receipt_sha256']==digest(main_value),
  'actual298 main binds both final evidence receipts; focus binds exact same main bytes')
 require(main['source_sha256_before']==main['source_sha256_after']==fixture['source_sha256_after']
  and set(main['source_sha256_after'])==selected_window_sources(),
  'same final actual native_selected source map stable through original window restart')
 check_map(main['source_sha256_after'],'original298 window final native_selected sources')
 timestamps={name:datetime.fromisoformat(value.replace('Z','+00:00')) for name,value in {
  'started':main['started_utc'],'finished':main['finished_utc'],'focus':focus['at_utc'],
  'necessary_finished':necessary_data['finished_utc'],'native_finished':fixture['finished_at']}.items()}
 require(all(value.tzinfo is not None and value.utcoffset() is not None for value in timestamps.values()),
  'actual main/focus/final-check timestamps are timezone-aware')
 require(timestamps['started']>timestamps['necessary_finished'] and timestamps['started']>timestamps['native_finished']
  and timestamps['finished']>=timestamps['started'] and timestamps['focus']>=timestamps['finished'],
  'original298 restart occurs after both final validations; focus follows completed main receipt')
 require(main['passed'] is True and main['private_file_hash_comparison_count']==5 and main['private_hashes_equal'] is True
  and main['changed_private_paths']==[] and main['private_contents_parsed_copied_or_restored'] is False and main['no_private_restoration'] is True,
  'actual original-window update/private5 hash unchanged, no content parsing/copy/restore')
 require(len(main['visible_windows'])==1,'one visible original project window');visible=main['visible_windows'][0]
 require(visible['visible'] is True and visible['responding'] is True and visible['minimized'] is False and visible['hwnd']>0
  and visible['pid']!=fixture['process_id'],'original window responsive/visible and not fixture')
 require(focus['visible'] is True and focus['pid']==visible['pid'] and focus['hwnd']==focus['actual_foreground']==visible['hwnd'],
  'actual foreground original project window')
 return {'receipt':rel(main_value),'sha256':digest(main_value),'focus_receipt':rel(focus_value),'focus_sha256':digest(focus_value),
  'section':298,'necessary_receipt_sha256':digest(necessary_value),'native_receipt_sha256':digest(native_value),
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
 name='verification/sections/298-preparation/root-visual-review.json';review=load(name)
 require(review['section']==298 and review['kind']=='root_archived_native_images_review'
  and review['actual_images_opened_with_view_image']is True,'root actually reviewed new298 images')
 expected={rel(path(value).with_name(Path(row['path']).name)):row['sha256']for row in window['screenshots']}
 require(review['images']==expected and review['actual_image_count']==len(expected),'root visual review exact all actual images')
 return{'receipt':name,'sha256':digest(name),'actual_root_reviewed_images':len(expected),'helper_performed_visual_review':False}


def packet():
 require(digest(MANIFEST)==MANIFEST_SHA and digest(DATA)==DATA_SHA and digest(BASELINE)==BASELINE_SHA,'fixed298 public source/data and actual prechange baseline exact bytes')
 manifest=load(MANIFEST)
 require(manifest['schema']=='event_node_requirements_source_manifest_v1'and manifest['data_file']==DATA
  and manifest['data_sha256']==DATA_SHA and manifest['runtime_reads_primary_table']is False and len(manifest['files'])==7,
  'actual small runtime source authority, not server execution')
 for name,pin in manifest['files'].items():
  check_map({name:pin['sha256']},'fresh298 source member');require(path(name).stat().st_size==pin['bytes'],'member exact length')
 data=load(DATA)
 require(data['schema']=='event_node_requirements_v1'and set(data['events'])==set(data['expected_events'])==set(RULES)
  and data['current_server_verified']is False and data['actual_server_eligible']is None and data['inventory_updated']is False
  and data['original_entry_restored']is False and data['probability']is None,'six exact event references, all actual effects unknown')
 for identity,floors in RULES.items():
  row=data['events'][identity]
  require(row['event_id']==identity and row['documented_excluded_main_floors']==floors
   and row['node_type']==data['expected_events'][identity]['node_types'][0],'exact source rule/full event identity')
  tech=row['technology_enabling_reference']
  if tech is not None:
   require(tech['role']=='known_enabling_path_only'and tech['necessary_negative_gate_proven']is False
    and tech['inactive_hard_exclusion_supported']is False and tech['actual_account_active']is None,
    'technology is one documented path, never necessary negative gate')
 baseline=load(BASELINE)
 require(baseline['section']==298 and baseline['kind']=='actual_prechange_public_source_execution_no_private_state'and baseline['parent']==PARENT
  and len(baseline['default_player_events'])==38 and len(baseline['default_choice_resources_scenes'])==190
  and len(baseline['non_target_natural_floor3_player_events'])==32 and len(baseline['target_natural_floor6_resources'])==32,
  'actual parent baseline with full default and explicit-context boundaries')
 return{'manifest':MANIFEST,'manifest_sha256':MANIFEST_SHA,'data':DATA,'data_sha256':DATA_SHA,
  'prechange_baseline':BASELINE,'prechange_baseline_sha256':BASELINE_SHA,
  'runtime_source_members':len(manifest['files']),'event_excluded_main_floors':RULES,
  'technology_paths_are_necessary_gates':False,'current_server_or_actual_generation_verified':False}


def selected_window_sources():
 tree=ast.parse(path(CANONICAL).read_text(encoding='utf8'))
 fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='bound_files')
 assignment=next(n for n in fn.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='names'for t in n.targets))
 require(isinstance(assignment.value,ast.Set),'native source literal set')
 constants={'CANONICAL':CANONICAL,'DATA':DATA,'MANIFEST':MANIFEST};names=set()
 for item in assignment.value.elts:
  if isinstance(item,ast.Name):require(item.id in constants,'known native source constant');names.add(constants[item.id])
  else:require(isinstance(item,ast.Constant)and type(item.value)is str,'literal native source path');names.add(item.value)
 names.update(load(MANIFEST)['files']);names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file())
 require({CANONICAL,MANIFEST,DATA,BUILDER,'rouge/event_node_requirements.py',*CHANGED_EXISTING,
  *('tests/'+m.split('.')[-1]+'.py'for m in MODULES[:3])}<=names,'newsource and actual four integration seams bound')
 return names


def necessary(value):
 data=load(value)
 require(data['section']==298 and data['kind']=='necessary_change_related_tests_not_full_suite'and data['exit_code']==0
  and type(data['exit_code'])is int and data.get('timed_out',False)is False and data['source_unchanged']is True
  and data['source_sha256_before']==data['source_sha256_after'],'actual final necessary0/stable, no timeout')
 require(data['modules']==MODULES and data['argv'][1:7]==['-B','-X','utf8','-m','unittest','-v']
  and data['argv'][-len(MODULES):]==MODULES and data['source_commit_before']==PARENT,'actual complete eight change-related modules and exact parent')
 require(data['game_sampling_verified']is False and data['chat_verified']is False and data['full_scope_reduced']is False
  and data['full_suite_rerun']is False,'necessary only, no game/chat/full claims')
 minimum={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/**/*.py')}
 minimum|={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/data/*.json')}
 minimum|={'tests/'+m.split('.')[-1]+'.py'for m in MODULES}|selected_window_sources()|{BASELINE}
 require(minimum<=set(data['source_sha256_after']),'actual necessary producer includes whole selected native/source closure')
 check_map(data['source_sha256_after'],'final necessary')
 prior=load('verification/sections/297.json')['necessary_validation'];require(digest(prior['receipt'])==prior['sha256'],'actual preceding297 receipt')
 old=load(prior['receipt']);require(old['exit_code']==0 and old['source_unchanged']is True,'actual preceding stable source authority')
 kept={n:v for n,v in old['source_sha256_after'].items()if n.startswith('rouge/')and n not in CHANGED_EXISTING
  and(n.endswith('.py')or(n.startswith('rouge/data/')and n.endswith('.json')))}
 require(bool(kept)and all(data['source_sha256_after'].get(n)==v for n,v in kept.items()),'all old product Python/staticJSON except four allowed seams unchanged')
 log=path(value).with_name('stderr.txt');text=path(log).read_text(encoding='utf8');counts=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',text)
 require(len(counts)==1 and int(counts[0][0])>0 and text.rstrip().endswith('OK')and not re.search(r'^(FAIL|ERROR):',text,re.M),'actual original terminal Ran/OK; no prepared count')
 return data,{'receipt':rel(value),'sha256':digest(value),'stderr':rel(log),'stderr_sha256':digest(log),
  'stdout_sha256':digest(path(value).with_name('stdout.txt')),'actual_exit':0,'methods_run':int(counts[0][0]),'seconds':float(counts[0][1]),
  'source_files':len(data['source_sha256_after']),'source_unchanged':True,'modules':MODULES,
  'unchanged_existing_product_Python_static_JSON_files':len(kept),'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),
  'source_author_checks_are_included_subsets_not_added':True}


def native(value,process_value,tests,reviewed_sha):
 data=load(value)
 require(data['section']==298 and data['kind']=='isolated_native_windows_event_node_requirements'and data['passed']is True
  and data['failure']is None and data['qpa']=='windows'and data['qt_exit_code']==0 and type(data['qt_exit_code'])is int
  and data['verification_window_closed']is True,'actual native Windows MainWindow/Qt completion')
 require(type(data['process_id'])is int and data['process_id']>0 and re.fullmatch('[0-9a-f]{64}',reviewed_sha)is not None
  and digest(CANONICAL)==reviewed_sha,'explicit final reviewed canonical script bytes and actual fixture PID')
 tree=ast.parse(path(CANONICAL).read_text(encoding='utf8'))
 labels={n.args[1].value for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='require'
  and len(n.args)>1 and isinstance(n.args[1],ast.Constant)and type(n.args[1].value)is str}
 require(type(data['checks'])is list and len(data['checks'])==len(set(data['checks']))==data['unique_checks']
  and labels<=set(data['checks'])and data['successful_assertion_executions_including_repeated_guards']>=len(data['checks']),
  'all final reviewed meaningful assertions are actually recorded, dynamic counts')
 require(data['source_sha256_before']==data['source_sha256_after']and set(data['source_sha256_after'])==selected_window_sources()
  and data['source_guard_is_selected_not_all_transitive_dependencies']is True,'exact selected source closure stable to native close')
 check_map(data['source_sha256_after'],'final native');joined=join_sources(tests['source_sha256_after'],data['source_sha256_after'])
 require(data['temporary_state_root']is True and data['state_paths_replaced_before_constructor']==['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE']
  and data['private_state_read_copied_or_restored']is False and data['external_entrypoints_blocked_before_original_call']is True,
  'four temporary state paths and external guards before original constructor')
 operations=data['external_operation_attempts']
 require(set(operations)=={'game_enumeration','game_connect','game_capture','game_next_frame','desktop_start','desktop_request','provider_chat','credential_read'}
  and all(type(v)is int and v==0 for v in operations.values()),'all eight external operation attempts zero')
 require(data['game_operated']is False and data['game_captures']==0 and data['chat_sent']is False and data['chat_attempted']is False
  and data['original_project_window_operated_or_restarted']is False and data['actual_process_termination_verified_by_this_script']is False
  and data['owned_supervisor_exit_and_cleanup_required_separately']is True
  and data['launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID']is True,'fixture cannot claim actual game/chat, original-window operations or historical ancestry')
 raw,process=owned_process(process_value,value,data)
 require(data['requested_parent_client_size']==[1050,720]and data['new_forced_no_selection_policy_applied']is False,'actual one client size, existing selection policy retained')
 expected={(identity,floor)for identity in RULES for floor in range(1,7)};rows=data['main_floor_observations']
 require(len(rows)==len(expected)and{(r['event_id'],r['floor'])for r in rows}==expected,'all six events by six main floors actual readings')
 require(all(r['new_check_match']is(r['floor']not in RULES[r['event_id']])and r['actual_server_eligible']is None
  and(r['new_check_match']is not False or r['overall_status']=='excluded')for r in rows),'exact negative facts never promoted to actual generation')
 contexts=data['nonapplicable_and_observed_contexts']
 require(len(contexts)==4 and{r['kind']for r in contexts}=={'unknown_floor','special_region','current_content','historical_title'}
  and all(r['natural_new_check_count']==0 for r in contexts)
  and all(r.get('title_retained')is True for r in contexts if r['kind']in{'current_content','historical_title'}),
  'unknown/special not inferred and current/historical titles kept separately readable')
 refresh=data['same_scope_refresh_observations']
 require(len(refresh)==3 and all(r['same_state']is True and r['technical_scroll']>0 and bool(r['text_selection'])for r in refresh),
  'three actual refreshes preserve real nonzero scroll and nonempty text selection')
 negatives=data['source_negative_fixtures']
 require(len(negatives)==1 and negatives[0]=={'kind':'warm_manifest','manifest':MANIFEST,'damaged_member':MANIFEST,
  'public_clone_only':True,'restored_sha256':MANIFEST_SHA,'actual_server_eligible':None},'real warm public-only source failure/restoration, unknown eligibility')
 expected_images={'directory-excluded','current-title','historical-title','source-unavailable','restored-reading'};images=data['screenshots']
 require(data['screenshot_count']==len(images)==len(expected_images)and{r['name']for r in images}==expected_images,'all representative actual source/manual-reading PNGs')
 handles=set()
 def handle(row):
  require(row['kind']=='parent'and row['qpa']=='windows'and row['process_id']==data['process_id']and type(row['hwnd'])is int
   and row['hwnd']>0 and row['client_size']==[1050,720],'actual fixture owns visible MainWindow and exact client size');handles.add(row['hwnd'])
 require(bool(data['native_observations']),'actual native handle observations')
 for row in data['native_observations']:handle(row)
 for image in images:
  file=raw.with_name(raw.stem+'-'+image['name']+'.png');require(Path(image['path']).resolve()==file.resolve(),'raw screenshot path unchanged')
  blob=path(path(value).with_name(file.name)).read_bytes()
  require(sha256(blob).hexdigest()==image['sha256']and blob[:8]==b'\x89PNG\r\n\x1a\n'and len(blob)>24
   and all(v>0 for v in struct.unpack('>II',blob[16:24])),'exact actual PNG bytes and dimensions');handle(image['native_window'])
 require(len(handles)==1,'all images and observations one actual owned MainWindow')
 return data,{'receipt':rel(value),'sha256':digest(value),'reviewed_native_source_sha256':reviewed_sha,
  'source_selected_files':len(data['source_sha256_after']),'source_unchanged':True,'source_join':joined,'unique_checks':data['unique_checks'],
  'actual_assertion_executions':data['successful_assertion_executions_including_repeated_guards'],'actual_main_floor_readings':len(rows),
  'actual_parent_client_size':[1050,720],'screenshots':len(images),'actual_Qt_exit':0,'owned_process':process,'game_or_chat_verified':False}


def historical_test_migration(tests):
 name='verification/sections/298-preparation/historical-test-migration-final.json';record=load(name)
 original='verification/sections/298-preparation/before/tests/test_node_catalog.py'
 require(record['kind']=='historical_assertion_migration_for_new_documented_main_floor_scope'
  and record['old_source']==original and record['new_source']==MAINTAINED_TEST
  and record['old_sha256']==digest(original)==OLD_TEST_SHA and record['new_sha256']==digest(MAINTAINED_TEST)==NEW_TEST_SHA
  and tests['source_sha256_after'][MAINTAINED_TEST]==NEW_TEST_SHA and record['changed_methods']==['test_172','test_183']
  and record['unchanged_other_test_methods']==30 and record['production_changes_after_first_necessary']is False
  and record['old_failure_preserved']is True and record['coverage_scope_reduced']is False,
  'actual two-method maintenance exact source identity; first real failure retained')
 old=ast.parse(path(original).read_text(encoding='utf8'));new=ast.parse(path(MAINTAINED_TEST).read_text(encoding='utf8'))
 old_fn=next(n for n in ast.walk(old)if isinstance(n,ast.FunctionDef)and n.name=='test_172')
 new_fn=next(n for n in ast.walk(new)if isinstance(n,ast.FunctionDef)and n.name=='test_172')
 for method in('test_172','test_183'):
  original_fn=next(n for n in ast.walk(old)if isinstance(n,ast.FunctionDef)and n.name==method)
  final_fn=next(n for n in ast.walk(new)if isinstance(n,ast.FunctionDef)and n.name==method)
  require(ast.dump(ast.parse(record['methods'][method]['old']).body[0],include_attributes=False)==ast.dump(original_fn,include_attributes=False)
   and ast.dump(ast.parse(record['methods'][method]['new']).body[0],include_attributes=False)==ast.dump(final_fn,include_attributes=False),
   'migration stored exact old/new method AST '+method)
 statement=ast.parse("self.assertTrue(c.event_candidates('先行一步',floor=6)['rows'])").body[0]
 targets=[i for i,n in enumerate(old_fn.body)if ast.dump(n,include_attributes=False)==ast.dump(statement,include_attributes=False)]
 require(len(targets)==1,'one precise old allowance assertion')
 replacement=ast.parse("r=c.event_candidates('先行一步',floor=6)\nself.assertFalse(r['rows'])\nself.assertEqual([e['id']for e in r['excluded']],['community_group_024'])\nself.assertFalse(r['excluded'][0]['natural_requirement_reference']['documented_floor_match'])").body
 at=targets[0];old_fn.body[at:at+1]=replacement
 first_source='verification/sections/298-preparation/first-necessary-source/tests/test_node_catalog.py'
 require(record['first_necessary_source']==first_source and digest(first_source)==record['first_necessary_sha256']==FIRST_TEST_SHA,
  'actual first127 source remains exact initial single-method migration')
 first_tree=ast.parse(path(first_source).read_text(encoding='utf8'))
 require(ast.dump(old,include_attributes=False)==ast.dump(first_tree,include_attributes=False),'first-run module differs from original only by prior test172 migration')
 fn183=next(n for n in ast.walk(old)if isinstance(n,ast.FunctionDef)and n.name=='test_183')
 original_assert=ast.parse("self.assertIn('回滚文明',[e['title']for e in r['event_union']])").body[0]
 indices=[i for i,n in enumerate(fn183.body)if ast.dump(n,include_attributes=False)==ast.dump(original_assert,include_attributes=False)]
 require(len(indices)==1,'one exact obsolete current-type union allowance assertion')
 fn183.body[indices[0]]=ast.parse("self.assertNotIn('回滚文明',[e['title']for e in r['event_union']])").body[0]
 common=ast.parse("self.assertFalse(r['common_event_references'])").body[0]
 after=next(i for i,n in enumerate(fn183.body)if ast.dump(n,include_attributes=False)==ast.dump(common,include_attributes=False))
 fn183.body.insert(after+1,ast.parse("self.assertIn('回滚文明',[e['title']for e in c.route_events(g,['a','b'],floor=3)['event_union']])").body[0])
 require(ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),
  'full module differs only by exact172 boundary replacement and183 floor1 negative/floor3 positive addition;30 other methods unchanged')
 first_value='verification/sections/298-necessary-first/process.json';first=load(first_value)
 require(record['first_necessary_receipt']==first_value and first['section']==298 and first['exit_code']==1 and first['source_unchanged']is True
  and first['source_sha256_before']==first['source_sha256_after']and first['modules']==MODULES
  and first['source_sha256_after'][MAINTAINED_TEST]==FIRST_TEST_SHA,'actual stable127 first-run failure bound to exact old test source')
 first_log=path(first_value).with_name('stderr.txt');log=first_log.read_text(encoding='utf8')
 ran=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',log)
 require(ran and len(ran)==1 and int(ran[0][0])==record['first_actual_methods']==127
  and record['first_actual_failures']==1 and log.rstrip().endswith('FAILED (failures=1)')
  and re.findall(r'^(?:FAIL|ERROR): (.+)$',log,re.M)==['test_183 (tests.test_node_catalog.NodeCatalogTests.test_183)'],
  'first actual127/one failure exact identity+trace retained, never added to final passed methods')
 require(set(first['source_sha256_after'])==set(tests['source_sha256_after'])
  and all(v==tests['source_sha256_after'][n]for n,v in first['source_sha256_after'].items()if n!=MAINTAINED_TEST),
  'only test183 file changed between real first and final source maps, product/native/data/scripts identical')
 earlier_name=record['original_test_172_migration'];earlier=load(earlier_name)
 require(earlier_name=='verification/sections/298-preparation/historical-test-migration.json'
  and earlier['old_sha256']==OLD_TEST_SHA and earlier['new_sha256']==FIRST_TEST_SHA
  and earlier['changed_method']=='test_172'and earlier['product_or_test_failure_claimed']is False,
  'prior proactive one-method migration retained unchanged, separate from actual later failure')
 old_names=set(subprocess.check_output(['git','ls-tree','-r','--name-only',PARENT,'--','tests'],cwd=ROOT,text=True).splitlines())
 changed=set(subprocess.check_output(['git','diff','HEAD','--name-only','--','tests'],cwd=ROOT,text=True).splitlines())
 require(changed&old_names=={MAINTAINED_TEST},'no other old tracked test changes silently admitted')
 return{'receipt':name,'sha256':digest(name),'original_test':original,'original_sha256':OLD_TEST_SHA,
  'final_tested_path':MAINTAINED_TEST,'final_tested_sha256':NEW_TEST_SHA,
  'changed_methods':['test_172','test_183'],'other_methods_preserved':30,'original_allowance_assertions_intentionally_replaced_not_unchanged':True,
  'first_failed_receipt':first_value,'first_failed_receipt_sha256':digest(first_value),'first_failed_stderr':rel(first_log),
  'first_failed_stderr_sha256':digest(first_log),'first_actual_methods':127,'first_actual_failures':1,
  'initial_proactive_migration':earlier_name,'initial_proactive_migration_sha256':digest(earlier_name),
  'first_actual_methods_not_added_to_final_pass_count':True,
  'test183_fixture_is_current_node_types_not_actual_historical_content':True,
  'reason':'Independent explicit new natural-main-floor negative rule changes the documented scope, not all event content/entry rules.',
  'actual_first_failure_retained':True,'production_changes_after_first_necessary':False,'scope_reduced':False}


def promotion(value,tests):
 record=load(value);require(record['section']==298 and record['kind']=='complete_root_functional_scope_source_freeze_before_actual_tests'
  and type(record['promoted'])is dict and type(record['existing_production_changes'])is dict
  and set(record['existing_production_changes'])==CHANGED_EXISTING,'actual root promotion and exact four old integration seams')
 expected={CANONICAL,DATA,MANIFEST,BUILDER,'rouge/event_node_requirements.py',
  *('tests/'+m.split('.')[-1]+'.py'for m in MODULES[:3])}
 expected|={p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file()}
 require(set(record['promoted'])==expected,'complete actual new-path promotion scope, no prefilled count')
 require(record['runtime_READY_sha256']=='67103d296025cf6a6501ccb0483cd5c557eaaaeb5d77ab051fcfe56b74b52970'
  and digest(HERE.parent/'READY.json')==record['runtime_READY_sha256'],'exact frozen runtime preparation, no concurrent rewrite')
 require(record['initial_backend_promotion_receipt']=='verification/sections/298-preparation/promotion.json'
  and record['historical_test_migration']=='verification/sections/298-preparation/historical-test-migration-final.json',
  'original backend promotion and explicit historical test migration pointers retained')
 original_name='verification/sections/298-preparation/root-promotion.json'
 require(record['source_freeze_original']==original_name and record['maintained_test_final']=={'path':MAINTAINED_TEST,'sha256':NEW_TEST_SHA},
  'final promotion binds exact original root freeze and final maintained test')
 initial_record=load(original_name);normalized=deepcopy(record)
 normalized.pop('source_freeze_original');normalized.pop('maintained_test_final')
 normalized['historical_test_migration']='verification/sections/298-preparation/historical-test-migration.json'
 require(normalized==initial_record,'final promotion differs only by explicit two-method maintenance record, original product freeze identical')
 backend=load(record['initial_backend_promotion_receipt'])
 backend_names={DATA,MANIFEST,BUILDER,'rouge/event_node_requirements.py','tests/test_event_node_requirements_298.py'}
 backend_names|={p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file()}
 require(backend['section']==298 and set(backend['promoted'])==backend_names
  and backend['root_integration_pending']is True and backend['author_API_tests_are_subset_not_feature_acceptance']is True
  and all(backend['promoted'][n]==record['promoted'][n]for n in backend_names),'immutable original12 backend entries copied unchanged into full root promotion')
 initial={**record['promoted'],**record['existing_production_changes']}
 for name,pin in initial.items():require(type(pin)is dict and set(pin)=={'sha256','bytes'}and type(pin['bytes'])is int
  and pin['bytes']>0 and re.fullmatch('[0-9a-f]{64}',pin['sha256'])is not None,'exact source-freeze hash/length identity '+name)
 final={name:digest(name)for name in sorted(expected|CHANGED_EXISTING)}
 require(all(tests['source_sha256_after'].get(n)==v for n,v in final.items()),'final promoted feature bytes actually tested')
 migration=historical_test_migration(tests);final[MAINTAINED_TEST]=migration['final_tested_sha256']
 return final,{'receipt':rel(value),'sha256':digest(value),'actual_promoted_paths':len(expected),
  'feature_and_maintenance_paths':len(final),
  'existing_production_paths':len(CHANGED_EXISTING),'historical_test_maintenance':migration,'promoted_feature_paths':len(expected|CHANGED_EXISTING),
  'initial_backend_promotion':record['initial_backend_promotion_receipt'],'initial_backend_promotion_sha256':digest(record['initial_backend_promotion_receipt']),
  'initial_root_promotion':original_name,'initial_root_promotion_sha256':digest(original_name),
  'frozen_runtime_READY_sha256':record['runtime_READY_sha256'],
  'initial_promotion_is_provenance_not_final_acceptance':True,'revisions_since_original_promotion':
   {n:{'original':initial[n]['sha256'],'final_tested':v}for n,v in final.items()if n in initial and initial[n]['sha256']!=v}}


def main(args):
 require(Path(__file__).resolve()==(HERE/'close_section_298.py').resolve(),'canonical cache closeout helper')
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 require(parent==PARENT and branch=='codex/p2-development'and not(ROOT/'verification/sections/298.json').exists(),'exact authorized branch/parent and exclusive receipt')
 source_ref=packet();tests,test_ref=necessary(args.necessary_receipt);feature_map,promotion_ref=promotion(args.promotion_receipt,tests)
 window,window_ref=native(args.window_receipt,args.window_process_receipt,tests,args.native_source_sha256)
 window_ref['root_visual_review']=visual_review(args.window_receipt,window)
 main_ref=original_window(args.main_window_receipt,args.focus_receipt,window,tests,args.necessary_receipt,args.window_receipt)
 full=load(FULL);require(digest(FULL)==FULL_SHA and full['after_section']==290 and full['available_checks_passed']is True
  and full['scope_not_reduced']is True and full['complete_repository_validation']is False,'reuse only original historical290 available full')
 cp=load('DEVELOPMENT_CHECKPOINT.json')
 require(cp['completed_sections']==cp['latest_functional_section']==297 and cp['next_section']==298 and cp['active_section']['section']==298
  and cp['policy']['priority_order']==['P3','P2','P1']and cp['policy']['current_user_batch_target_section']is None
  and cp['policy']['stop_after_section']is None,'current active298/P3-first/no numeric endpoint')
 require(cp['last_full_validation']['after_section']==290 and cp['current_available_full_validation']['section']==290
  and cp['policy']['full_validation_interval']==15 and cp['policy']['full_validation_anchor_section']==125
  and 125+((298-125)//15+1)*15==305,'unchanged full cadence and original290 proof')
 cloud=cp['last_verified_cloud_save'];proof=load(cloud['proof'])
 require(cloud['section']==297 and digest(cloud['proof'])==cloud['proof_sha256']and proof['passed']is True
  and proof['commit']==proof['remote_HEAD']==cloud['commit']and proof['push_primary_exit']==0,'real previous297 ordinary publication')
 docs={n:path(n).read_bytes()for n in('DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','AGENTS.md')}
 progress=path('PROJECT_PROGRESS.md').read_bytes();require(sha256(progress).hexdigest()==PROGRESS_SHA_BEFORE,'remaining todo not falsely retired by six partial negative rules')
 now=datetime.now(timezone(timedelta(hours=8))).isoformat()
 capability=('六项精确事件按文献核对普通自然主层的已知禁区；目录明确列出不符分组，仍可手动阅读。'
  '未知层、特殊区域、已读具体内容及历史读取分开处理，保留已读标题和原文；'
  '科技只标为已证开启途径，不反推未开启就绝不出现。来源失效清除旧禁区结论并回到未知，刷新保留阅读。')
 limits=['只新增文献明确的负条件；允许层数不代表完整生成资格、实际出现、可选或服务器行为。',
  '不补原入口脚本、不产生概率，不清15全局层数/25场景与57选项/10未解析附注或17typed奖励边界。',
  '既有DOM主层过滤独立保留；新的普通自然主层限制不用于内容引用、历史或特殊区域。',
  '全量沿用290原来源，本节只必要与新原生流程，下次305；P3/P2/P1未完成、识别最后，无路线推荐或数字终点。']
 receipt={'section':298,'kind':'functional_section','title':TITLE,'at_Beijing':now,'branch':branch,'prior_commit':parent,
  'remaining_item':'P3节点事件条件与资料对应','new_capability':capability,'files':sorted(feature_map),'source_sha256':feature_map,
  'source_reference':source_ref,'source_promotion':promotion_ref,'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),
  'existing_source_changes_including_test_maintenance':sorted(CHANGED_EXISTING|{MAINTAINED_TEST}),
  'historical_test_maintenance':promotion_ref['historical_test_maintenance'],
  'actual_server_generation_or_inventory_verified':False,'remaining_global_stage_floor_gaps_unchanged':15,
  'original_entry_gaps_unchanged':[25,57],'unparsed_notes_unchanged':10,'typed_named_grant_count_unchanged':17,
  'partial_direct_reference_scope_unchanged':[10,18,58],'whole_map_gaps_unchanged':[81,59],
  'necessary_validation':test_ref,'native_windows_validation':{**window_ref,'original_project_window':main_ref},
  'full_validation':{'receipt':FULL,'sha256':FULL_SHA,'after_section':290,'full_suite_rerun':False,'new298_source_full_validation_claimed':False,
   'next_periodic_section':305,'scope_not_reduced':True,'complete_repository_validation':False},
  'PROJECT_PROGRESS_unchanged_sha256':PROGRESS_SHA_BEFORE,'limits':limits,'next_section':299,'cloud_publication_binding':'enclosing_commit',
  'cloud_published':False,'P3_complete':False,'P2_complete':False}
 history='historical_before298_current_pointers';require(history not in cp,'exclusive298 pointer archive')
 cp[history]={k:deepcopy(cp[k])for k in('current_section_save','current_section_validation','latest_section_environment','active_section','current_batch','cloud_publication_closeout')if k in cp}
 cp.pop('active_section',None);cp.pop('cloud_publication_closeout',None)
 cp.update(completed_sections=298,latest_functional_section=298,next_section=299,batch_status='P3_SECTION298_VALIDATED_AWAITING_PUBLICATION',
  next_full_validation_after=305,next_action='从299继续有证P3剩余事项，无数字终点；下次完整可用全量305。')
 cp['policy']['next_full_validation_after']=305;cp['current_batch_commit_policy']['next_full_validation_after']=305
 cp['current_batch'].update(status=cp['batch_status'],next_section=299,next_section_started=False,receipt='verification/sections/298.json',next_full_validation_after=305,batch_closed=False)
 cp['confirmed_next_stage_direction'].update(last_completed_functional_section=298,next_functional_section_started=False)
 cp['sections'].append({'number':298,'completion_ref':'p3-section-298','topic':TITLE,'verification':'verification/sections/298.json'})
 cp['current_section_save']={'section':298,'verification':'verification/sections/298.json','scope':'current_functional_section',
  'binding':'enclosing_commit','commit_reference':'commit containing298 exact main-floor negative rule integration, actual acceptance, requirements and index'}
 cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_section_validation']={'section':298,'receipt':'verification/sections/298.json','necessary_methods_passed':test_ref['methods_run'],
  'native_isolated_window_checks':window['unique_checks'],'full_suite_rerun':False,'last_full_receipt':FULL,'full_source_is_historical290':True}
 cp['latest_section_environment']={'section':298,'receipt':'verification/sections/298.json',
  'native_windows':f"{test_ref['methods_run']} actual necessary; {window['unique_checks']} unique native;36 main-floor readings;{window_ref['screenshots']} representative PNG; original visible/private5 unchanged",
  'native_game_or_chat_verified':False,'current_section_full_rerun':False,'new_Linux_Wine_full_run':False,'last_full_receipt':FULL}
 cp['functional_sections_since_latest_requirement']=list(dict.fromkeys([*cp['functional_sections_since_latest_requirement'],298]))
 completed=(f'## 功能第298节 · {TITLE}\n\n{now}。{capability}\n\n'
  f"实际{test_ref['methods_run']}必要检查、原生{window['unique_checks']}唯一检查及36主层组合通过；{window_ref['screenshots']}张代表PNG由根代理查看，原项目窗口更新/私人5路径不变。"
  '来源及原回执verification/sections/298.json；不把允许层当生成保证，不减少其它未完入口、奖励或地图待办。'
  '旧test_172迁移为第6层排除边界；test_183在首127项1失败后改为第1层不含/第3层含回滚文明，30其它方法保留原AST。首轮不叠加为通过数。'
  '290全量原来源沿用，下次305，后续299，无数字终点。待普通推送核对。\n\n')
 mutations={'verification/sections/298.json':encode(receipt),'DEVELOPMENT_CHECKPOINT.json':encode(cp),'PROJECT_COMPLETED.md':completed.encode()+docs['PROJECT_COMPLETED.md']}
 wip=docs['WORK_IN_PROGRESS.md'].decode();require('## 功能第297节'in wip,'preserve prior297 history')
 mutations['WORK_IN_PROGRESS.md']=(completed+wip[wip.index('## 功能第297节'):]).encode()
 req=docs['PROJECT_REQUIREMENTS.md'].decode();a,b=req.index('<!-- current-delivery:start -->'),req.index('<!-- current-delivery:end -->')
 block=('<!-- current-delivery:start -->\n## 当前交付与续接 · 第298节\n\n2026-10-16继续P3，无数字终点。'+capability
  +f"实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过；原窗口更新/私人5路径不变。"
  +'完整生成、原入口与实际资格未知；17typed、15/25/57/10与81/59待办保持。290全量原来源/下次305；P3→P2→P1、识别最后，无路线建议。待普通推送核对。\n')
 mutations['PROJECT_REQUIREMENTS.md']=(req[:a]+block+req[b:]).encode()
 agents=docs['AGENTS.md'].decode();a,b=agents.index('## 当前续接 · 第297节'),agents.index('## 当前优先顺序与输出可读性')
 mutations['AGENTS.md']=(agents[:a]+'## 当前续接 · 第298节已完成功能与必要/原生验收\n\n'+capability
  +'来源及实际回执verification/sections/298.json；完整生成及实际资格仍未知，17typed与15/25/57/10待办不变。'
  +'原窗口更新/私人5路径不变；未跑298全量，290完整范围沿用原来源。下一节299/下次305，无数字终点。'
  +'P3→P2→P1、识别最后，不推荐/排序/自动选路；待普通推送核对，源码/要求/验收/索引同提交。\n\n'+agents[b:]).encode()
 require('初次招募时即处于已进阶状态'in mutations['PROJECT_REQUIREMENTS.md'].decode()and'初次招募即处于已进阶状态'in mutations['AGENTS.md'].decode(),'verified直升 terminology preserved')
 require(all(str(i)+'.'in mutations['AGENTS.md'].decode().split('## 当前续接')[0]for i in range(1,6)),'highest five judgment/source requirements preserved')
 archive=ROOT/'verification/sections/298-preparation/closeout-tools';require(not archive.exists(),'exclusive public closeout archive')
 copies={'close_section_298.py':path(HERE/'close_section_298.py').read_bytes(),'CONTRACT.md':path(HERE/'CONTRACT.md').read_bytes()}
 copies.update({'before-'+name:raw for name,raw in docs.items()})
 archive_manifest={'kind':'SECTION298_PUBLIC_CLOSEOUT_TOOLS_NOT_PRIVATE_STATE','files':{n:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}for n,raw in copies.items()},'private_contents_or_hash_lists_copied':False}
 print(json.dumps({'gates_passed':True,'apply_requested':args.apply,'necessary_actual_methods':test_ref['methods_run'],'native_actual_unique_checks':window['unique_checks'],
  'source_join':window_ref['source_join'],'feature_paths':len(feature_map),'planned_public_files':list(mutations),'PROJECT_PROGRESS_modified':False,
  'full_rerun':False,'next_full_section':305,'numeric_endpoint':None,'cloud_published':False},ensure_ascii=False))
 if not args.apply:return
 for name,raw in docs.items():require(path(name).read_bytes()==raw,'document unchanged before apply '+name)
 require(path('PROJECT_PROGRESS.md').read_bytes()==progress,'remaining todo unchanged before apply')
 check_map(tests['source_sha256_after'],'prewrite actual necessary');check_map(window['source_sha256_after'],'prewrite actual native selected sources')
 archive.mkdir(parents=True)
 for name,raw in copies.items():
  with(archive/name).open('xb')as stream:stream.write(raw)
 with(archive/'archive-manifest.json').open('xb')as stream:stream.write(encode(archive_manifest))
 for name,raw in mutations.items():
  target=ROOT/name;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb'if name=='verification/sections/298.json'else'wb')as stream:stream.write(raw)
 print(json.dumps({'section':298,'local_closeout_written':True,'cloud_published':False,'next_section':299,'next_full_section':305}))

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--necessary-receipt',required=True);parser.add_argument('--window-receipt',required=True)
 parser.add_argument('--window-process-receipt',required=True);parser.add_argument('--native-source-sha256',required=True)
 parser.add_argument('--promotion-receipt',default='verification/sections/298-preparation/final-promotion.json')
 parser.add_argument('--main-window-receipt',default='verification/sections/298-main-window.json')
 parser.add_argument('--focus-receipt',default='verification/sections/298-main-window-focus.json')
 parser.add_argument('--apply',action='store_true');main(parser.parse_args())

