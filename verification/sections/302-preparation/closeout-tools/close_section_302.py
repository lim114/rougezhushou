"""Strict section302 public-evidence closeout. Preview default; root-only --apply.
No Qt/tests, game/chat/private operations or Git mutation. Missing actual evidence fails.
"""
import argparse,ast,runpy
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,re,struct,subprocess
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
HERE=ROOT/'.cache/p3-302-closeout'
PARENT='87a622eea314ccce49712121fd42683eb2e7e463'
TITLE='调谐仪式六个交付选项与三种首领削弱资料'
CANONICAL='scripts/verify_ritual_weakening_window_302.py'
PACKET='research/p3-ritual-weakening-302';MANIFEST=PACKET+'/source-manifest.json';DATA='rouge/data/ritual-weakening.json'
MANIFEST_SHA='bb1ab31f0e41e7015d303368292d28a752f539e78f7b80be90329adb24f97182'
DATA_SHA='3e0533e212927bd9b50dd8f4f183ca97c5c02187f396a20718b049d7b7951138'
BUILDER='scripts/build_ritual_weakening_302.py'
FULL='verification/full-290/summary.json';FULL_SHA='2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
CHANGED_EXISTING={'rouge/node_catalog_view.py'}
REQUIRED_MODULES={'tests.test_ritual_weakening_302','tests.test_ritual_weakening_view_302','tests.test_ritual_weakening_integration_302'}
PROGRESS_SHA_BEFORE='111962b1622515c494ae81a06ac19b915db797211e926165a9947b80fade8a0b'
def require(value,message):
 if value is not True:raise ValueError('302 closeout prerequisite: '+message)

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
 require(process['section']==302 and process['kind']=='actual_native_window_owned_process_execution'
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
 require(path(main_value).resolve()==(ROOT/'verification/sections/302-main-window.json').resolve()
  and path(focus_value).resolve()==(ROOT/'verification/sections/302-main-window-focus.json').resolve(),
  'strict same-section canonical302 main/focus receipt paths')
 require(main['section']==302 and focus['section']==302
  and main['necessary_receipt_sha256']==digest(necessary_value)
  and main['native_receipt_sha256']==digest(native_value)
  and main['native_receipt']==rel(native_value) and main['necessary_receipt']==rel(necessary_value)
  and focus['main_receipt_sha256']==digest(main_value),
  'actual302 main binds both final evidence receipts; focus binds exact same main bytes')
 require(main['source_sha256_before']==main['source_sha256_after']==fixture['source_sha256_after']
  and set(main['source_sha256_after'])==selected_window_sources(),
  'same final actual native_selected source map stable through original window restart')
 check_map(main['source_sha256_after'],'original302 window final native_selected sources')
 timestamps={name:datetime.fromisoformat(value.replace('Z','+00:00')) for name,value in {
  'started':main['started_utc'],'finished':main['finished_utc'],'focus':focus['at_utc'],
  'necessary_finished':necessary_data['finished_utc'],'native_finished':fixture['finished_at']}.items()}
 require(all(value.tzinfo is not None and value.utcoffset() is not None for value in timestamps.values()),
  'actual main/focus/final-check timestamps are timezone-aware')
 require(timestamps['started']>timestamps['necessary_finished'] and timestamps['started']>timestamps['native_finished']
  and timestamps['finished']>=timestamps['started'] and timestamps['focus']>=timestamps['finished'],
  'original302 restart occurs after both final validations; focus follows completed main receipt')
 require(main['passed'] is True and main['private_file_hash_comparison_count']==5 and main['private_hashes_equal'] is True
  and main['changed_private_paths']==[] and main['private_contents_parsed_copied_or_restored'] is False and main['no_private_restoration'] is True,
  'actual original-window update/private5 hash unchanged, no content parsing/copy/restore')
 require(len(main['visible_windows'])==1,'one visible original project window');visible=main['visible_windows'][0]
 require(visible['visible'] is True and visible['responding'] is True and visible['minimized'] is False and visible['hwnd']>0
  and visible['pid']!=fixture['process_id'],'original window responsive/visible and not fixture')
 require(focus['visible'] is True and focus['pid']==visible['pid'] and focus['hwnd']==focus['actual_foreground']==visible['hwnd'],
  'actual foreground original project window')
 return {'receipt':rel(main_value),'sha256':digest(main_value),'focus_receipt':rel(focus_value),'focus_sha256':digest(focus_value),
  'section':302,'necessary_receipt_sha256':digest(necessary_value),'native_receipt_sha256':digest(native_value),
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
 name='verification/sections/302-preparation/root-visual-review.json';review=load(name)
 require(review['section']==302 and review['kind']=='root_archived_native_images_review'
  and review['actual_images_opened_with_view_image']is True,'root actually reviewed new302 images')
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
 record=load(value);require(record['section']==302 and type(record['files'])is dict and bool(record['files']),'public preparation archive exact section and nonempty inventory')
 base=path(value).parent
 for name,pin in record['files'].items():
  require(type(name)is str and not Path(name).is_absolute()and'..'not in Path(name).parts and'\\'not in name,'relative public preparation member')
  member=base/name
  require(digest(member)==pin['sha256']and path(member).stat().st_size==pin['bytes'],'exact retained preparation/first evidence '+name)
 return{'receipt':rel(value),'sha256':digest(value),'member_count':len(record['files']),
  'preparation_or_author_checks_added_to_product_pass_count':False}

def necessary(value):
 data=load(value)
 require(data['section']==302 and data['kind']=='necessary_change_related_tests_not_full_suite'
  and type(data['exit_code'])is int and data['exit_code']==0 and data.get('timed_out',False)is False
  and data['source_unchanged']is True and data['source_sha256_before']==data['source_sha256_after'],'actual final necessary0/stable')
 modules=data['modules'];require(type(modules)is list and len(modules)==len(set(modules))and REQUIRED_MODULES<=set(modules)
  and data['argv'][1:7]==['-B','-X','utf8','-m','unittest','-v']and data['argv'][7:]==modules
  and data['source_commit_before']==PARENT,'complete actual selected modules include all three new contracts; exact parent')
 require(data['game_sampling_verified']is False and data['chat_verified']is False and data['full_scope_reduced']is False
  and data['full_suite_rerun']is False,'necessary only, not full/game/chat')
 minimum={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/**/*.py')}
 minimum|={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/data/*.json')}
 minimum|={'tests/'+m.split('.')[-1]+'.py'for m in modules}|selected_window_sources()|{BUILDER}
 require(minimum<=set(data['source_sha256_after']),'actual necessary map covers product Python/data and all selected native/source files')
 check_map(data['source_sha256_after'],'actual necessary source')
 previous=load('verification/sections/301.json')['necessary_validation'];require(digest(previous['receipt'])==previous['sha256'],'previous necessary exact public source')
 old=load(previous['receipt']);kept={n:v for n,v in old['source_sha256_after'].items()if n.startswith('rouge/')and n not in CHANGED_EXISTING
  and(n.endswith('.py')or(n.startswith('rouge/data/')and n.endswith('.json')))}
 require(bool(kept)and all(data['source_sha256_after'].get(n)==v for n,v in kept.items()),'all old product Python/staticJSON except sole parent panel unchanged')
 tracked_tests=set(subprocess.check_output(['git','ls-tree','-r','--name-only',PARENT,'--','tests'],cwd=ROOT,text=True).splitlines())
 changed_tests=set(subprocess.check_output(['git','diff','HEAD','--name-only','--','tests'],cwd=ROOT,text=True).splitlines())
 require(not(tracked_tests&changed_tests),'no old tracked test changed')
 log=path(value).with_name('stderr.txt');text=log.read_text(encoding='utf8');counts=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',text)
 require(len(counts)==1 and int(counts[0][0])>0 and text.rstrip().endswith('OK')and not re.search(r'^(FAIL|ERROR):',text,re.M),'actual Ran/OK original result')
 return data,{'receipt':rel(value),'sha256':digest(value),'stderr':rel(log),'stderr_sha256':digest(log),
  'stdout_sha256':digest(path(value).with_name('stdout.txt')),'actual_exit':0,'methods_run':int(counts[0][0]),'seconds':float(counts[0][1]),
  'source_files':len(data['source_sha256_after']),'source_unchanged':True,'modules':modules,
  'unchanged_existing_product_Python_static_JSON_files':len(kept),'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),
  'old_tracked_test_maintenance':False,'author_preparation_checks_are_subsets_not_added':True}

def necessary_attempt_history(final_value):
 result=[];final=path(final_value).resolve()
 for record_path in sorted((ROOT/'verification/sections').glob('302-necessary-*/process.json')):
  if record_path.resolve()==final:continue
  record=load(record_path);require(record['section']==302,'same-section actual necessary history only')
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
 require(record['section']==302 and record['parent_commit']==PARENT and record['old_tests_modified']is False
  and set(record['existing_production_changes'])==CHANGED_EXISTING,'exact sole old production seam and parent')
 expected={CANONICAL,DATA,MANIFEST,BUILDER,'rouge/ritual_weakening.py','rouge/ritual_weakening_view.py',
  *('tests/'+m.split('.')[-1]+'.py'for m in REQUIRED_MODULES)}
 expected|={p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file()}
 require(set(record['promoted'])==expected and record.get('native_script_pending',False)is False,'complete actual new functionality promotion includes canonical native')
 for name,pin in record['promoted'].items():
  require(type(pin)is str and digest(name)==pin,'exact promoted public byte '+name)
 for name,pin in record['existing_production_changes'].items():
  require(type(pin)is str and digest(name)==pin,'exact sole old panel final byte')
  parent_bytes=subprocess.check_output(['git','show',PARENT+':'+name],cwd=ROOT)
  require(sha256(parent_bytes).hexdigest()==record['before_existing_sha256'][name],'actual parent seam before bytes')
 require(digest(CANONICAL)==reviewed_sha,'final explicitly reviewed native source')
 final={n:digest(n)for n in sorted(expected|CHANGED_EXISTING)}
 require(all(tests['source_sha256_after'].get(n)==v for n,v in final.items()),'all final functional sources in actual necessary map')
 return final,{'receipt':rel(value),'sha256':digest(value),'new_functional_paths_including_final_native':len(expected),
  'feature_paths_including_existing':len(final),'canonical_native_separately_bound':{'path':CANONICAL,'sha256':reviewed_sha},
  'existing_production_paths':1,'old_tracked_test_maintenance':False,'promotion_is_provenance_not_acceptance':True}

def packet():
 require(digest(MANIFEST)==MANIFEST_SHA and digest(DATA)==DATA_SHA,'fixed302 manifest/data bytes')
 manifest=load(MANIFEST);data=load(DATA)
 require(manifest['schema']=='ritual_weakening_source_manifest_v1'and manifest['event_id']=='community_group_032'
  and manifest['data_file']==DATA and manifest['data_sha256']==DATA_SHA
  and manifest['runtime_reads_complete_primary_table']is False and manifest['runtime_verifies_complete_original_bytes']is False
  and manifest['all_runtime_members_required_for_each_target_query']is True,'lightweight complete selected records, whole package failclosed')
 for name,pin in manifest['files'].items():
  check_map({name:pin['sha256']},'complete public302 source');require(path(name).stat().st_size==pin['bytes'],'exact302 source lengths')
 require(set(manifest['runtime_files'])<=set(manifest['files'])and set(manifest['runtime_files']).isdisjoint(manifest['build_authority_files'])
  and all(v==manifest['files'][n]for n,v in manifest['runtime_files'].items()),'runtime selected vs full build authority explicit')
 rows=data['choices'];effects=data['weakening_references']
 expected=[(2,0,'3','1'),(2,1,'4','1'),(3,0,'6','3'),(3,1,'7','3'),(4,0,'9','2'),(4,1,'10','2')]
 require(len(rows)==6 and[(int(r['scene_key'].split(':')[-1]),int(r['choice_key'].split(':')[-1]),r['original_choice_id'].rsplit('_',1)[1],r['weakening_id'].rsplit('_',1)[1])for r in rows]==expected,'exact six choices and primary feature order1/3/2')
 require([e['weakening_id']for e in effects]==['rogue_6_chimera_weaken_1','rogue_6_chimera_weaken_3','rogue_6_chimera_weaken_2']
  and manifest['counts']=={'events':1,'choices':6,'weakening_references':3,'related_stages':1},'three distinct conditional effects, not six stacked grants')
 actual=('actual_choice','actual_weakening','actual_attached','actual_inventory','actual_consumed','actual_effect','actual_numeric_result','actual_eligible')
 require(all(all(row[k]is None for k in actual)for row in[data,*rows,*effects])
  and all(r['submission_reference']['quantity_reference']is None for r in rows),'actual quantities/inventory/attachment/activation unknown')
 require('首次'in effects[0]['effect_text']and'首次'in effects[0]['effect_source_text']and'待部署区'in effects[1]['effect_text']
  and effects[2]['effect_text']=='灾厄之口的伤害降低。','complete fixed documentation scope, no immunity claim from narrative')
 require(effects[2]['configuration_reference']['value']==0.5 and effects[2]['configuration_reference']['numerical_execution_verified']is False
  and all(e['feature_reference']['selector']=='enemy_2150_shchmr'for e in effects),'half parameter is only configuration for exact enemy selector')
 related=data['related_stage_reference']
 require(related['stage_id']=='ro6_b_6'and related['title']=='畸症'and related['reference_only']is True
  and related['immediate_transition']is None and related['enemy_level_reference']is None,'manual related battle, no fake transition or FEATURE enemy level')
 require(data['current_server_verified']is False and data['original_entry_restored']is False and data['calculation_applied']is False
  and data['run_state_updated']is False,'no server/entry/calculation/run claim')
 return{'manifest':MANIFEST,'manifest_sha256':MANIFEST_SHA,'data':DATA,'data_sha256':DATA_SHA,'source_members':len(manifest['files']),
  'runtime_fresh_members':len(manifest['runtime_files']),'runtime_fresh_bytes_including_manifest':sum(p['bytes']for p in manifest['runtime_files'].values())+path(MANIFEST).stat().st_size,
  'runtime_verifies_complete_original_bytes':False,'complete_build_originals_retained_and_hash_verified_at_closeout':True,
  'fixed_choice_count':6,'fixed_event_count':1,'fixed_weakening_count':3,'related_fixed_stage':'ro6_b_6','weakening_order':[1,3,2],
  'whole_package_failclosed_on_any_runtime_member':True,'actual_submission_attachment_consumption_effect_or_eligibility_verified':False,
  'damage_scale_half_is_configuration_only':True,'original_entry_restored':False}

def native(value,process_value,tests,reviewed_sha):
 data=load(value)
 require(data['section']==302 and data['kind']=='isolated_native_windows_ritual_weakening_reader'and data['passed']is True
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
 check_map(data['source_sha256_after'],'native302');joined=join_sources(tests['source_sha256_after'],data['source_sha256_after'])
 require(data['temporary_state_root']is True and data['state_paths_replaced_before_constructor']==['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE']
  and data['private_state_read_copied_or_restored']is False and data['external_entrypoints_blocked_before_original_call']is True,'temp four paths before constructor; no private copy/read')
 ops=data['external_operation_attempts'];require(set(ops)=={'game_enumeration','game_connect','game_capture','game_next_frame','desktop_start','desktop_request','provider_chat','credential_read'}
  and all(type(v)is int and v==0 for v in ops.values()),'eight actual external attempt counters zero')
 require(data['game_operated']is False and data['game_captures']==0 and data['chat_sent']is False and data['chat_attempted']is False
  and data['original_project_window_operated_or_restarted']is False and data['actual_process_termination_verified_by_this_script']is False
  and data['owned_supervisor_exit_and_cleanup_required_separately']is True
  and data['launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID']is True
  and data['actual_weakening_activation_or_numeric_result_verified']is False,'no actual game/effect/ancestry/terminal claims from fixture')
 raw,process=owned_process(process_value,value,data)
 require(data['requested_parent_client_size']==[1050,720]and data['requested_dialog_client_size']==[900,680]and data['requested_related_battle_client_size']==[1180,850],'actual requested parent and reader sizes')
 rows=data['actual_choice_readings'];expected_rows=load(DATA)['choices']
 tuples={(r['event_id'],r['scene_key'],r['choice_key'])for r in expected_rows}
 require(len(rows)==6 and{(r['event_id'],r['scene_key'],r['choice_key'])for r in rows}==tuples,'all six full tuple choices actually read')
 for row in rows:
  expected=next(r for r in expected_rows if(r['event_id'],r['scene_key'],r['choice_key'])==(row['event_id'],row['scene_key'],row['choice_key']))
  require(all(row[k]==expected[k]for k in('reference_id','original_choice_id','weakening_id','choice_title','condition_text','effect_text'))
   and row['related_stage_id']=='ro6_b_6'and row['actual_effect']is None and row['calculation_applied']is False,'each actual reading exact identity, distinct conditional effect, no numeric activation')
 battles=data['related_fixed_battle_readings']
 require(len(battles)==1 and battles[0]['stage_id']=='ro6_b_6'and battles[0]['enemy_id']=='enemy_2150_shchmr'
  and battles[0]['original_reference_level']==0 and battles[0]['actual_effect']is None and battles[0]['actual_transition']is None
  and battles[0]['fixed_enemy_unmodified']is True,'manual old fixed battle level0 kept separate from FEATURE level unknown')
 refresh=data['same_scope_refresh_observations']
 require(len(refresh)==4 and{r['path']for r in refresh}=={'unselected_parent','selected_dialog','selected_parent','selected_same_reference'}
  and all(r['nonzero_scroll']>0 and r['selection']and r['parent_unchanged']is True for r in refresh)
  and sum(r['selected']is None for r in refresh)==1,'unselected and selected refreshes retain actual nonzero reading and parent state')
 require(data['source_negative_fixtures']==[{'kind':'warm_complete_runtime_clone_manifest_bytes','member':MANIFEST,
  'old_child_stage_cleared':True,'actual_effect':None,'restore_sha256':MANIFEST_SHA,'restored_unselected':True}],
  'warm real source damage clears old choices/effects/child stage, restoration remains unselected')
 names={'player-effect-rogue_6_chimera_weaken_1','player-effect-rogue_6_chimera_weaken_3',
  'player-effect-rogue_6_chimera_weaken_2','player-source-unavailable','related-fixed-map-player'}
 images=data['screenshots'];require(data['screenshot_count']==len(images)==len(names)and{r['name']for r in images}==names
  and sum(r['direct_player_text']for r in images)==4 and sum(r['related_fixed_map']for r in images)==1,'five actual images:three distinct effects/source loss/fixed map')
 for image in images:
  if image['name'].startswith('player-effect-'):
   effect=next(e for e in load(DATA)['weakening_references']if image['name']=='player-effect-'+e['weakening_id'])
   require(image['effect_text_anchored_in_player_viewport']==effect['effect_text'],'each actual player PNG anchors its complete exact conditional effect')
 handles={}
 def handle(row):
  sizes={'parent':[1050,720],'dialog':[900,680],'battle':[1180,850]}
  require(row['kind']in sizes and row['client_size']==sizes[row['kind']]and row['qpa']=='windows'
   and type(row['hwnd'])is int and row['hwnd']>0 and row['process_id']==data['process_id'],'actual owned HWND/PID/exact client size')
  handles.setdefault(row['kind'],set()).add(row['hwnd'])
 require(bool(data['native_observations']),'actual observed owned native HWNDs')
 for row in data['native_observations']:handle(row)
 for image in images:
  file=raw.with_name(raw.stem+'-'+image['name']+'.png');require(Path(image['path']).resolve()==file.resolve(),'exact raw screenshot source path')
  blob=path(path(value).with_name(file.name)).read_bytes()
  require(sha256(blob).hexdigest()==image['sha256']and blob[:8]==b'\x89PNG\r\n\x1a\n'and len(blob)>24
   and all(v>0 for v in struct.unpack('>II',blob[16:24])),'actual PNG hash/header/dimensions');handle(image['native_window'])
 require(set(handles)=={'parent','dialog','battle'}and all(len(s)==1 for s in handles.values())
  and len(set.union(*handles.values()))==3,'distinct main/modeless reader/related fixed battle HWNDs')
 return data,{'receipt':rel(value),'sha256':digest(value),'reviewed_native_source_sha256':reviewed_sha,
  'source_selected_files':len(data['source_sha256_after']),'source_unchanged':True,'source_join':joined,
  'unique_checks':data['unique_checks'],'actual_assertion_executions':data['successful_assertion_executions_including_repeated_guards'],
  'representative_images':len(images),'screenshots':len(images),'actual_player_reader_images':4,'actual_related_fixed_map_images':1,
  'actual_Qt_exit':0,'owned_process':process,'actual_submission_attachment_consumption_effect_or_eligibility_verified':False,'game_or_chat_verified':False}

def main(args):
 require(Path(__file__).resolve()==(HERE/'close_section_302.py').resolve(),'canonical cache closeout helper')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 require(branch=='codex/p2-development'and parent==PARENT and not(ROOT/'verification/sections/302.json').exists(),'exact authorized branch/parent; exclusive302 receipt')
 require(digest(CANONICAL)==args.native_source_sha256,'approved native bytes checked before its selected-source producer')
 source_ref=packet();archive_ref=preparation_archive(args.preparation_archive_manifest);tests,test_ref=necessary(args.necessary_receipt)
 feature_map,promotion_ref=promotion(args.promotion_receipt,tests,args.native_source_sha256)
 window,window_ref=native(args.window_receipt,args.window_process_receipt,tests,args.native_source_sha256)
 window_ref['root_visual_review']=visual_review(args.window_receipt,window)
 main_ref=original_window(args.main_window_receipt,args.focus_receipt,window,tests,args.necessary_receipt,args.window_receipt)
 full=load(FULL);require(digest(FULL)==FULL_SHA and full['after_section']==290 and full['available_checks_passed']is True
  and full['scope_not_reduced']is True and full['complete_repository_validation']is False,'only original historical290 available full reused')
 cp=load('DEVELOPMENT_CHECKPOINT.json')
 require(cp['completed_sections']==cp['latest_functional_section']==301 and cp['next_section']==302 and cp['active_section']['section']==302
  and cp['policy']['priority_order']==['P3','P2','P1']and cp['policy']['current_user_batch_target_section']is None
  and cp['policy']['stop_after_section']is None,'active302/P3-first/no numeric endpoint')
 require(cp['last_full_validation']['after_section']==290 and cp['current_available_full_validation']['section']==290
  and cp['policy']['full_validation_interval']==15 and cp['policy']['full_validation_anchor_section']==125
  and 125+((302-125)//15+1)*15==305,'unchanged full cadence/original290 proof')
 cloud=cp['last_verified_cloud_save'];proof=load(cloud['proof'])
 require(cloud['section']==301 and digest(cloud['proof'])==cloud['proof_sha256']and proof['passed']is True
  and proof['commit']==proof['remote_HEAD']==cloud['commit']and proof['push_primary_exit']==0,'actual previous301 ordinary publication')
 docs={n:path(n).read_bytes()for n in('DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','AGENTS.md')}
 progress=path('PROJECT_PROGRESS.md').read_bytes();require(sha256(progress).hexdigest()==PROGRESS_SHA_BEFORE,'remaining work not falsely retired by fixed source candidate reading')
 now=datetime.now(timezone(timedelta(hours=8))).isoformat()
 capability=('调谐仪式六个完整交付选项按三步分组，分别阅读首次灾厄之口不摧毁危朽、不再封锁待部署区和伤害降低的固定资料；'
  '三条同名源私钥选项分开，保留对应交付条件和机制物品1/3/2顺序。默认未选，手选只读；显式按钮打开独立的固定畸症资料，保留父面板与已有作战阅读。'
  '同范围刷新保留非零滚动和选区，来源或范围失效清旧选项/效果/子作战，恢复后手选；不改本局或数值计算。')
 limits=['固定文献与原表配置不等于当前服务器或本局实际执行；资格、库存、实际交付、消耗、附着和生效仍未知。',
  'damage_scale=0.5仅作配置参考，不等于完整伤害计算；选项“无法再吞噬生命”是叙事，不表示免伤。首次不摧毁危朽的限定保留。',
  '源私钥可替代对应步骤的需求，不表示一次交付获得全部三种效果，不推数量。相关畸症是手动固定资料入口，不是立即转场，不新增event_battle_links。',
  '运行期fresh精选完整记录约0.73MB，完整17.9MB原表与固定完整HTML只作构建依据；未把当前检索工具正文冒作固定完整HTML。',
  '原17typed/190资源、15全局层数、25场景/57选项、10未解析附注、整图81/59和逐格10图18关58点边界不变；P3/P2/P1未完成，识别最后，无路线建议。',
  '本节必要与原生流程，原290全量按原来源保留，下次305；无数字终点。']
 receipt={'section':302,'kind':'functional_section','title':TITLE,'at_Beijing':now,'branch':branch,'prior_commit':parent,
  'remaining_item':'P3调谐仪式选项与首领机制条件的集中只读资料','new_capability':capability,
  'files':sorted(feature_map),'source_sha256':feature_map,'source_reference':source_ref,'source_promotion':promotion_ref,'preparation_archive':archive_ref,
  'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),'existing_source_changes_including_test_maintenance':sorted(CHANGED_EXISTING),
  'old_tracked_test_maintenance':False,'actual_server_generation_or_inventory_verified':False,
  'remaining_global_stage_floor_gaps_unchanged':15,'original_entry_gaps_unchanged':[25,57],'unparsed_notes_unchanged':10,
  'typed_named_grant_count_unchanged':17,'partial_direct_reference_scope_unchanged':[10,18,58],'whole_map_gaps_unchanged':[81,59],
  'necessary_validation':test_ref,'necessary_attempt_history':necessary_attempt_history(args.necessary_receipt),'native_windows_validation':{**window_ref,'original_project_window':main_ref},
  'full_validation':{'receipt':FULL,'sha256':FULL_SHA,'after_section':290,'full_suite_rerun':False,'new302_source_full_validation_claimed':False,
   'next_periodic_section':305,'scope_not_reduced':True,'complete_repository_validation':False},
  'PROJECT_PROGRESS_unchanged_sha256':PROGRESS_SHA_BEFORE,'limits':limits,'next_section':303,
  'cloud_publication_binding':'enclosing_commit','cloud_published':False,'P3_complete':False,'P2_complete':False}
 history='historical_before302_current_pointers';require(history not in cp,'exclusive302 pointer archive')
 cp[history]={k:deepcopy(cp[k])for k in('current_section_save','current_section_validation','latest_section_environment','active_section','current_batch','cloud_publication_closeout')if k in cp}
 cp.pop('active_section',None);cp.pop('cloud_publication_closeout',None)
 cp.update(completed_sections=302,latest_functional_section=302,next_section=303,batch_status='P3_SECTION302_VALIDATED_AWAITING_PUBLICATION',
  next_full_validation_after=305,next_action='从303继续有证P3剩余事项，无数字终点；下次完整可用全量305。')
 cp['policy']['next_full_validation_after']=305;cp['current_batch_commit_policy']['next_full_validation_after']=305
 cp['current_batch'].update(status=cp['batch_status'],next_section=303,next_section_started=False,receipt='verification/sections/302.json',next_full_validation_after=305,batch_closed=False)
 cp['confirmed_next_stage_direction'].update(last_completed_functional_section=302,next_functional_section_started=False)
 cp['sections'].append({'number':302,'completion_ref':'p3-section-302','topic':TITLE,'verification':'verification/sections/302.json'})
 cp['current_section_save']={'section':302,'verification':'verification/sections/302.json','scope':'current_functional_section',
  'binding':'enclosing_commit','commit_reference':'commit containing302 exact ritual weakening reader and manual fixed battle, real acceptance, requirements and index'}
 cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_section_validation']={'section':302,'receipt':'verification/sections/302.json','necessary_methods_passed':test_ref['methods_run'],
  'native_isolated_window_checks':window['unique_checks'],'full_suite_rerun':False,'last_full_receipt':FULL,'full_source_is_historical290':True}
 cp['latest_section_environment']={'section':302,'receipt':'verification/sections/302.json',
  'native_windows':f"{test_ref['methods_run']} actual necessary; {window['unique_checks']} unique native; {window_ref['screenshots']} representative PNG including player text; original visible/private5 unchanged",
  'native_game_or_chat_verified':False,'current_section_full_rerun':False,'new_Linux_Wine_full_run':False,'last_full_receipt':FULL}
 cp['functional_sections_since_latest_requirement']=list(dict.fromkeys([*cp['functional_sections_since_latest_requirement'],302]))
 completed=(f'## 功能第302节 · {TITLE}\n\n{now}。{capability}\n\n'
  f"实际{test_ref['methods_run']}必要检查、原生{window['unique_checks']}唯一检查通过；{window_ref['screenshots']}张代表PNG由根代理查看，包含三种效果的玩家正文、来源失效及手动相关固定作战；原项目窗口更新/私人5路径不变。"
  '来源及原回执verification/sections/302.json；六个选项只是既有条件资料集中阅读，不表示实际交付/消耗/附着/生效，不伪造转场或数量，不减少其它入口、奖励或地图待办。'
  '首个作者24/F1的DOM标题测试前提错误及修后24/0分开保存，不额外叠入正式验收。290全量原来源沿用，下次305，后续303，无数字终点。待普通推送核对。\n\n')
 mutations={'verification/sections/302.json':encode(receipt),'DEVELOPMENT_CHECKPOINT.json':encode(cp),'PROJECT_COMPLETED.md':completed.encode()+docs['PROJECT_COMPLETED.md']}
 wip=docs['WORK_IN_PROGRESS.md'].decode();require('## 功能第301节'in wip,'preserve prior301 history')
 mutations['WORK_IN_PROGRESS.md']=(completed+wip[wip.index('## 功能第301节'):]).encode()
 req=docs['PROJECT_REQUIREMENTS.md'].decode();a,b=req.index('<!-- current-delivery:start -->'),req.index('<!-- current-delivery:end -->')
 block=('<!-- current-delivery:start -->\n## 当前交付与续接 · 第302节\n\n2026-10-16继续P3，无数字终点。'+capability
  +f"实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过；原窗口更新/私人5路径不变。"
  +'固定削弱说明不等于本局交付、消耗、附着、生效或数值计算；17typed、15/25/57/10与81/59待办保持。290全量原来源/下次305；P3→P2→P1、识别最后，无路线建议。待普通推送核对。\n')
 mutations['PROJECT_REQUIREMENTS.md']=(req[:a]+block+req[b:]).encode()
 agents=docs['AGENTS.md'].decode();a,b=agents.index('## 当前续接 · 第301节'),agents.index('## 当前优先顺序与输出可读性')
 mutations['AGENTS.md']=(agents[:a]+'## 当前续接 · 第302节已完成功能与必要/原生验收\n\n'+capability
  +'来源及实际回执verification/sections/302.json；实际交付、消耗、附着、资格与生效仍未知，17typed与15/25/57/10待办不变。'
  +'原窗口更新/私人5路径不变；未跑302全量，290完整范围沿用原来源。下一节303/下次305，无数字终点。'
  +'P3→P2→P1、识别最后，不推荐/排序/自动选路；待普通推送核对，源码/要求/验收/索引同提交。\n\n'+agents[b:]).encode()
 require('初次招募时即处于已进阶状态'in mutations['PROJECT_REQUIREMENTS.md'].decode()and'初次招募即处于已进阶状态'in mutations['AGENTS.md'].decode(),'verified直升 terminology preserved')
 require(all(str(i)+'.'in mutations['AGENTS.md'].decode().split('## 当前续接')[0]for i in range(1,6)),'highest five judgment/source requirements preserved')
 archive=ROOT/'verification/sections/302-preparation/closeout-tools';require(not archive.exists(),'exclusive closeout source archive')
 copies={'close_section_302.py':path(HERE/'close_section_302.py').read_bytes(),'CONTRACT.md':path(HERE/'CONTRACT.md').read_bytes()}
 copies.update({'before-'+name:raw for name,raw in docs.items()})
 archive_manifest={'kind':'SECTION302_PUBLIC_CLOSEOUT_TOOLS_NOT_PRIVATE_STATE','files':{n:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}for n,raw in copies.items()},'private_contents_or_hash_lists_copied':False}
 print(json.dumps({'gates_passed':True,'apply_requested':args.apply,'necessary_actual_methods':test_ref['methods_run'],'native_actual_unique_checks':window['unique_checks'],
  'source_join':window_ref['source_join'],'feature_paths':len(feature_map),'planned_public_files':list(mutations),'PROJECT_PROGRESS_modified':False,
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
  with target.open('xb'if name=='verification/sections/302.json'else'wb')as stream:stream.write(raw)
 print(json.dumps({'section':302,'local_closeout_written':True,'cloud_published':False,'next_section':303,'next_full_section':305}))

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--necessary-receipt',required=True);parser.add_argument('--window-receipt',required=True)
 parser.add_argument('--window-process-receipt',required=True);parser.add_argument('--native-source-sha256',required=True)
 parser.add_argument('--promotion-receipt',default='verification/sections/302-preparation/promotion.json')
 parser.add_argument('--preparation-archive-manifest',default='verification/sections/302-preparation/preparation-archive-manifest.json')
 parser.add_argument('--main-window-receipt',default='verification/sections/302-main-window.json')
 parser.add_argument('--focus-receipt',default='verification/sections/302-main-window-focus.json')
 parser.add_argument('--apply',action='store_true');main(parser.parse_args())
