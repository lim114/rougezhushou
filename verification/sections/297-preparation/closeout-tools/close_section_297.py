"""Strict297 preview-only closeout unless --apply is explicitly supplied.
No product imports, tests/Qt/window/game/chat/private operations or Git mutation.
Final actual receipts and source maps determine every validation count.
"""
import argparse,ast
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,re,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'.cache/p3-297-closeout'
PARENT='7706a982b84fe64148da87d6d073786704c188d1'
TITLE='未涉足之树派出、归来与休息结果和手动信标图文'
CANONICAL='scripts/verify_expedition_results_window_297.py'
PACKET='research/p3-expedition-results-297'
MANIFEST=PACKET+'/source-manifest.json'
DATA='rouge/data/expedition-results.json'
BUILDER='scripts/build_expedition_results_297.py'
BASELINE='verification/sections/297-preparation/before-output-hashes.json'
MANIFEST_SHA='5227f6fc7171430dc820668daf636489c72673d62a5f1e9b82d26d0021cf323e'
DATA_SHA='f83ca0ec16a24e634e48500186da6f6f7f3269092d51045d99779f1a9439d3ff'
BASELINE_SHA='b2f8a69361a7ca612fcbe4192d97ca0cdf90ab69330a4eefa84f78bd0f893a2a'
FULL='verification/full-290/summary.json'
FULL_SHA='2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
EVENT='community_group_024';SCENE=EVENT+':scene:0';ITEM='rogue_6_relic_final_3'
CHOICES=tuple(SCENE+':choice:'+str(i)for i in range(3))
REFS=tuple(c+':expedition-result'for c in CHOICES)
CHANGED_EXISTING={'rouge/node_catalog_view.py','rouge/player_node_information.py'}
HISTORICAL_TEST='tests/test_documented_item_integration_295.py'
HISTORICAL_BEFORE_SHA='6ff4e7b67c1aaf2ef36715b735c542b2ac6788430cf4ee93d5254cdd5eafc7e9'
HISTORICAL_AFTER_SHA='4e946fd3579f37bc3f222f855f9c23811c1279c946a4345431161ed141fcc2f9'
MODULES=['tests.test_expedition_results_297','tests.test_expedition_results_view_297',
 'tests.test_expedition_integration_297','tests.test_event_planning',
 'tests.test_player_node_information_286','tests.test_node_catalog_view',
 'tests.test_documented_item_integration_295','tests.test_battle_entry_integration_296']
PROGRESS_SHA_BEFORE='111962b1622515c494ae81a06ac19b915db797211e926165a9947b80fade8a0b'

def require(value,message):
 if value is not True:raise ValueError('297 closeout prerequisite: '+message)

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
 require(process['section']==297 and process['kind']=='actual_native_window_owned_process_execution'
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
 require(path(main_value).resolve()==(ROOT/'verification/sections/297-main-window.json').resolve()
  and path(focus_value).resolve()==(ROOT/'verification/sections/297-main-window-focus.json').resolve(),
  'strict same-section canonical297 main/focus receipt paths')
 require(main['section']==297 and focus['section']==297
  and main['necessary_receipt_sha256']==digest(necessary_value)
  and main['native_receipt_sha256']==digest(native_value)
  and main['native_receipt']==rel(native_value) and main['necessary_receipt']==rel(necessary_value)
  and focus['main_receipt_sha256']==digest(main_value),
  'actual297 main binds both final evidence receipts; focus binds exact same main bytes')
 require(main['source_sha256_before']==main['source_sha256_after']==fixture['source_sha256_after']
  and set(main['source_sha256_after'])==selected_window_sources(),
  'same final actual native_selected source map stable through original window restart')
 check_map(main['source_sha256_after'],'original297 window final native_selected sources')
 timestamps={name:datetime.fromisoformat(value.replace('Z','+00:00')) for name,value in {
  'started':main['started_utc'],'finished':main['finished_utc'],'focus':focus['at_utc'],
  'necessary_finished':necessary_data['finished_utc'],'native_finished':fixture['finished_at']}.items()}
 require(all(value.tzinfo is not None and value.utcoffset() is not None for value in timestamps.values()),
  'actual main/focus/final-check timestamps are timezone-aware')
 require(timestamps['started']>timestamps['necessary_finished'] and timestamps['started']>timestamps['native_finished']
  and timestamps['finished']>=timestamps['started'] and timestamps['focus']>=timestamps['finished'],
  'original297 restart occurs after both final validations; focus follows completed main receipt')
 require(main['passed'] is True and main['private_file_hash_comparison_count']==5 and main['private_hashes_equal'] is True
  and main['changed_private_paths']==[] and main['private_contents_parsed_copied_or_restored'] is False and main['no_private_restoration'] is True,
  'actual original-window update/private5 hash unchanged, no content parsing/copy/restore')
 require(len(main['visible_windows'])==1,'one visible original project window');visible=main['visible_windows'][0]
 require(visible['visible'] is True and visible['responding'] is True and visible['minimized'] is False and visible['hwnd']>0
  and visible['pid']!=fixture['process_id'],'original window responsive/visible and not fixture')
 require(focus['visible'] is True and focus['pid']==visible['pid'] and focus['hwnd']==focus['actual_foreground']==visible['hwnd'],
  'actual foreground original project window')
 return {'receipt':rel(main_value),'sha256':digest(main_value),'focus_receipt':rel(focus_value),'focus_sha256':digest(focus_value),
  'section':297,'necessary_receipt_sha256':digest(necessary_value),'native_receipt_sha256':digest(native_value),
  'native_selected_current_source_unchanged':True,'started_after_final_necessary_and_native':True,'focus_after_main_finished':True,
  'private_hash_comparisons':5,'changed_private_paths':0,'visible_responsive_foreground':True,'private_contents_read_by_helper':False}


def packet():
 require(digest(MANIFEST)==MANIFEST_SHA and digest(DATA)==DATA_SHA and digest(BASELINE)==BASELINE_SHA,
  'exact expedition source/data and genuine prechange baseline')
 manifest=load(MANIFEST)
 require(manifest['schema']=='expedition_results_source_manifest_v1'and manifest['data_file']==DATA
  and manifest['data_sha256']==DATA_SHA and manifest['runtime_reads_primary_table']is False,
  'fixed selected-source runtime packet, no primary-table runtime claim')
 require(len(manifest['files'])==9,'exact nine public runtime source members')
 for name,pin in manifest['files'].items():
  check_map({name:pin['sha256']},'fresh public packet member')
  require(path(name).stat().st_size==pin['bytes'],'public member exact length '+name)
 data=load(DATA)
 require(data['schema']=='expedition_results_reference_v1'and data['event_id']==EVENT
  and data['current_server_verified']is False and data['inventory_updated']is False
  and data['eligibility_evaluated']is False and len(data['rows'])==3,'three documented choices only, no actual effects')
 ids=['choice_ro6_scout_1','choice_ro6_scout_3','choice_ro6_scout_2','choice_ro6_scout_4']
 require(data['source_reference']['original_choice_ids']==ids
  and data['source_reference']['original_return_item_pointer']==ITEM,'exact four original choices and fixed return item pointer')
 unknown=('actual_dispatched_operator','actual_returned','actual_reward','actual_quantity','actual_advanced','actual_return_clock','actual_selectable')
 for i,row in enumerate(data['rows']):
  require((row['event_id'],row['scene_key'],row['choice_key'],row['reference_id'],row['original_choice_id'])
   ==(EVENT,SCENE,CHOICES[i],REFS[i],ids[i])and all(row[k]is None for k in unknown),'exact complete choice and unknown actual state')
  require(row['effect_phase_reference']==('on_choice'if i==2 else'on_return')
   and row['immediate_resource_references']==([{'resource':'hope','quantity_reference':2}]if i==2 else[])
   and row['return_resource_references']==([{'resource':'hope','quantity_reference':2}]if i==1 else[]),
   'rest immediate versus root-only return references, never summed')
  require(row['promotion_reference']is(False if i==1 else None),'root no-advance reference does not prove normal promotion')
  if i==1:
   require(row['documented_return_item']['item_id']==ITEM
    and row['documented_return_item']['quantity_reference']is None
    and row['beak_reference']['applies_to_root_branch']is None,'beacon quantity and beak interaction remain unknown')
 annotation=data['return_explanatory_reference']
 require(annotation['choice_key']==EVENT+':scene:2:choice:1'and annotation['game_choice_ids']==[]
  and annotation['is_actual_button']is False and annotation['effect_phase']=='on_return',
  'return note stays explanatory, no fourth actual button')
 baseline=load(BASELINE)
 require(baseline['kind']=='ACTUAL_PRECHANGE_PUBLIC_DEFAULT_CONTEXT_OUTPUT_HASHES'
  and baseline['actual_scene_query_count']==len(baseline['choice_resources_scenes'])==190
  and baseline['actual_player_query_count']==len(baseline['player_events'])==38
  and baseline['private_state_or_Qt_game_chat_used']is False,'real complete default-context output baseline')
 for name,old in baseline['source_before_after_sha256'].items():
  if name!='rouge/player_node_information.py':require(digest(name)==old,'old resource/catalog source exact '+name)
 return data,{'manifest':MANIFEST,'manifest_sha256':MANIFEST_SHA,'runtime_data':DATA,'runtime_sha256':DATA_SHA,
  'source_members':len(manifest['files']),'actual_choice_references':3,'original_choice_ids':ids,
  'explanatory_note_is_actual_button':False,'beacon_item':ITEM,'beacon_quantity_reference':None,
  'baseline':BASELINE,'baseline_sha256':BASELINE_SHA,'old_resource_queries':190,
  'other_event_player_outputs':37,'current_server_or_actual_run_verified':False}


def selected_window_sources():
 tree=ast.parse(path(CANONICAL).read_text(encoding='utf8'))
 fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='bound_files')
 assignment=next(n for n in fn.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='names'for t in n.targets))
 require(isinstance(assignment.value,ast.Set),'native source literal set')
 constants={'CANONICAL':CANONICAL,'DATA':DATA,'MANIFEST':MANIFEST}
 names=set()
 for item in assignment.value.elts:
  if isinstance(item,ast.Name):
   require(item.id in constants,'known native source constant');names.add(constants[item.id])
  else:
   require(isinstance(item,ast.Constant)and type(item.value)is str,'literal native source path');names.add(item.value)
 names.update(load(MANIFEST)['files'])
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file())
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'tests').glob('test_expedition*297.py'))
 require({CANONICAL,MANIFEST,DATA,'rouge/expedition_results.py','rouge/expedition_results_view.py',BUILDER,
  *('tests/'+m.split('.')[-1]+'.py'for m in MODULES[:3])}<=names,'native new model/UI/integration closure')
 return names


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


def unchanged_existing_sources(data):
 previous=load('verification/sections/296.json');ref=previous['necessary_validation']
 require(digest(ref['receipt'])==ref['sha256'],'actual preceding296 final necessary receipt')
 old=load(ref['receipt'])
 require(old['section']==296 and old['exit_code']==0 and old['source_unchanged']is True
  and old['source_sha256_before']==old['source_sha256_after'],'actual preceding stable source map, no rerun')
 unchanged={n:v for n,v in old['source_sha256_after'].items()if n.startswith('rouge/')and n not in CHANGED_EXISTING
  and(n.endswith('.py')or(n.startswith('rouge/data/')and n.endswith('.json')))}
 require(bool(unchanged)and all(data['source_sha256_after'].get(n)==v for n,v in unchanged.items()),
  'every previous product Python/static JSON unchanged except two intended target integrations')
 scope=load('verification/sections/297-preparation/scope.json')
 require(scope['section']==297 and scope['parent']==PARENT and scope['functional_complete']is False
  and set(scope['before_existing_sources'])==CHANGED_EXISTING,'actual before-functional scope and exact two old sources')
 for name in CHANGED_EXISTING:
  before='verification/sections/297-preparation/before-'+Path(name).name
  require(digest(before)==scope['before_existing_sources'][name]['sha256']==old['source_sha256_after'][name],
   'true original pre297 integration source '+name)
 require(digest('PROJECT_PROGRESS.md')==PROGRESS_SHA_BEFORE,'remaining-only todo bytes unchanged')
 return{'previous_section':296,'previous_necessary_receipt':ref['receipt'],'previous_necessary_sha256':ref['sha256'],
  'unchanged_existing_product_Python_static_JSON_files':len(unchanged),'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),
  'old_research_and_images_not_in_this_producer_not_required_or_filled_in':True,'PROJECT_PROGRESS_unchanged':True}


def necessary(value,parent):
 data=load(value)
 require(data['section']==297 and data['kind']=='necessary_change_related_tests_not_full_suite'
  and type(data['exit_code'])is int and data['exit_code']==0 and data['source_unchanged']is True
  and data['source_sha256_before']==data['source_sha256_after'],'actual final necessary0/stable')
 require(data['modules']==MODULES and data['argv'][1:7]==['-B','-X','utf8','-m','unittest','-v']
  and data['argv'][-len(MODULES):]==MODULES and data['source_commit_before']==parent==PARENT,'all eight exact modules/current parent')
 require(data['game_sampling_verified']is False and data['chat_verified']is False
  and data['full_scope_reduced']is False and data['full_suite_rerun']is False,'necessary only, no external/full claims')
 minimum={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/**/*.py')}
 minimum|={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/data/*.json')}
 minimum|={'tests/'+m.split('.')[-1]+'.py'for m in MODULES}|{CANONICAL,BUILDER,BASELINE}
 minimum|={p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file()}
 require(minimum<=set(data['source_sha256_after']),'actual producer covers product, static data, eight modules, new source packet and baseline')
 check_map(data['source_sha256_after'],'final necessary');old=unchanged_existing_sources(data)
 logpath=path(value).with_name('stderr.txt');log=path(logpath).read_text(encoding='utf8')
 matches=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',log)
 require(len(matches)==1 and int(matches[0][0])>0 and log.rstrip().endswith('OK')
  and not re.search(r'^(FAIL|ERROR):',log,re.M),'actual terminal Ran/OK, methods not prefilled')
 # These tests were actually included above, not independently rerun here.
 source=path('tests/test_expedition_integration_297.py').read_text(encoding='utf8')
 methods={n.name for n in ast.walk(ast.parse(source))if isinstance(n,ast.FunctionDef)}
 require({'test_all_190_old_resource_queries_are_exactly_unchanged',
  'test_all_37_other_event_player_outputs_are_exactly_unchanged'}<=methods,'source-bound complete legacy comparison tests included')
 return data,{'receipt':rel(value),'sha256':digest(value),'stderr':rel(logpath),'stderr_sha256':digest(logpath),
  'stdout_sha256':digest(path(value).with_name('stdout.txt')),'actual_exit':0,'methods_run':int(matches[0][0]),
  'seconds':float(matches[0][1]),'source_files':len(data['source_sha256_after']),'source_unchanged':True,'modules':MODULES,
  'author24_and_UI16_are_subsets_not_added_again':True,'existing_source_boundary':old,
  'old_190_resource_and_37_other_event_outputs_verified_by_included_tests':True}


def rejected_map_attempt():
 base='verification/sections/297-preparation';name=base+'/map-first-fit/archive-manifest.json';manifest=load(name)
 require(manifest['kind']=='REJECTED_ACTUAL_FIRST_GROUND_FITS_NOT_FUNCTIONAL_COMPLETION'
  and manifest['accepted_for_production']==[]and manifest['old_4px_gate_retained']is True
  and manifest['observations_adjusted']is False and manifest['raw_source_map_images_unchanged']is True
  and manifest['product_sources_changed_by_fit']is False,'rejected maps remain maintenance only; gate not tuned')
 for member,pin in manifest['files'].items():
  require(type(member)is str and member.startswith('map-first-fit/')and'..'not in Path(member).parts
   and'\\'not in member,'safe map-attempt archive member')
  file=base+'/'+member
  require(digest(file)==pin['sha256']and path(file).stat().st_size==pin['bytes'],'original failed-fit artifact '+member)
 fit_name=base+'/map-first-fit/initial-fit-results.json';fits=load(fit_name)
 require(digest(fit_name)=='a76a1d3dc60a0b7a232b0f1d2886890f06248e3ffde03f4662ca20dde3425d92'
  and len(fits)==2 and{r['id']for r in fits}=={'ro6_c_2','ro6_c_4'}
  and all(r['accepted']is False and max(c['error_px']for c in r['checks'])>4 for r in fits),'actual first two fits rejected at unchanged4px')
 require(digest('rouge/data/battle-map-projections.json')==digest(base+'/map-first-fit/prior-projections.json'),
  'failed map attempt changed no runtime regular projections')
 regular=load('rouge/data/battle-map-projections.json');direct=load('rouge/data/fixed-landmark-references.json')
 require((len(regular['calibrations']),len(regular['stages']))==(12,24)
  and(len(direct['references']),len(direct['stages']),sum(len(v['points'])for v in direct['references'].values()))==(10,18,58),
  'existing regular12/24 and direct10/18/58 preserved')
 return{'archive_manifest':name,'sha256':digest(name),'initial_fit_receipt':fit_name,'initial_fit_sha256':digest(fit_name),
  'source_pixel_gate':4,'accepted_for_production':[],'counted_as_functional_progress':False,
  'results':[{'id':r['id'],'accepted':False,'holdouts':len(r['checks']),'max_error_px':max(c['error_px']for c in r['checks'])}for r in fits]}


def native(value,process_value,necessary_data,reviewed_sha,source):
 data=load(value)
 require(data['section']==297 and data['kind']=='isolated_native_windows_expedition_choice_results'
  and data['passed']is True and data['failure']is None and data['qpa']=='windows'
  and type(data['qt_exit_code'])is int and data['qt_exit_code']==0 and data['verification_window_closed']is True,
  'actual new canonical native Windows/Qt/owned-window completion')
 require(type(data['process_id'])is int and data['process_id']>0
  and re.fullmatch('[0-9a-f]{64}',reviewed_sha)is not None and digest(CANONICAL)==reviewed_sha,
  'actual fixture PID and explicit final reviewed native source SHA')
 tree=ast.parse(path(CANONICAL).read_text(encoding='utf8'))
 required={call.args[1].value for call in ast.walk(tree)if isinstance(call,ast.Call)
  and isinstance(call.func,ast.Name)and call.func.id=='require'and len(call.args)>1
  and isinstance(call.args[1],ast.Constant)and type(call.args[1].value)is str}
 require(type(data['checks'])is list and len(data['checks'])==len(set(data['checks']))==data['unique_checks']
  and required<=set(data['checks'])
  and data['successful_assertion_executions_including_repeated_guards']>=len(data['checks']),
  'all reviewed meaningful native assertions; counts from actual report')
 selected=selected_window_sources()
 require(data['source_sha256_before']==data['source_sha256_after']and set(data['source_sha256_after'])==selected
  and data['source_guard_is_selected_not_all_transitive_dependencies']is True,'exact selected native sources stable, not all transitive scope')
 check_map(data['source_sha256_after'],'native final')
 joined=join_sources(necessary_data['source_sha256_after'],data['source_sha256_after'])
 require(data['temporary_state_root']is True and data['state_paths_replaced_before_constructor']
  ==['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE']and data['private_state_read_copied_or_restored']is False
  and data['external_entrypoints_blocked_before_original_call']is True,'four temp paths/external guards before constructor')
 operations=data['external_operation_attempts']
 require(set(operations)=={'game_enumeration','game_connect','game_capture','game_next_frame','desktop_start',
  'desktop_request','provider_chat','credential_read'}and all(type(n)is int and n==0 for n in operations.values()),
  'all eight actual external-entry attempts zero')
 require(data['game_operated']is False and type(data['game_captures'])is int and data['game_captures']==0
  and data['chat_sent']is False and data['chat_attempted']is False and data['original_project_window_operated_or_restarted']is False,
  'no game/chat/private/original-project operations during isolated fixture')
 require(data['actual_process_termination_verified_by_this_script']is False
  and data['owned_supervisor_exit_and_cleanup_required_separately']is True
  and data['launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID']is True,
  'fixture does not claim ancestry/job closure itself')
 raw,process_ref=owned_process(process_value,value,data)
 require(data['requested_parent_client_size']==[1050,720]and data['requested_dialog_client_size']==[900,680],
  'one actual MainWindow size and modeless dialog size')
 handles={'parent':set(),'dialog':set()}
 def handle(row):
  kind=row['kind']
  require(kind in handles and row['process_id']==data['process_id']and row['qpa']=='windows'
   and type(row['hwnd'])is int and row['hwnd']>0
   and row['client_size']==([1050,720]if kind=='parent'else[900,680]),'actual own HWND/fixture PID/client size')
  handles[kind].add(row['hwnd'])
 require(bool(data['native_observations']),'actual own native observations present')
 for row in data['native_observations']:handle(row)
 expected={'parent-entry','rest-immediate','source-return-item','event-source-invalidated','item-source-invalidated'}
 images=data['screenshots']
 require(data['screenshot_count']==len(images)==len(expected)and{r['name']for r in images}==expected,
  'all five representative actual main/result/item/failure screenshots')
 for image in images:
  expected_file=raw.with_name(raw.stem+'-'+image['name']+'.png')
  require(Path(image['path']).resolve()==expected_file.resolve(),'unaltered actual raw PNG path')
  pixels=path(path(value).with_name(expected_file.name)).read_bytes()
  require(sha256(pixels).hexdigest()==image['sha256']and pixels[:8]==b'\x89PNG\r\n\x1a\n'
   and len(pixels)>24 and all(n>0 for n in struct.unpack('>II',pixels[16:24])),'exact archived actual PNG bytes')
  handle(image['native_window'])
 require(all(len(v)==1 for v in handles.values())and handles['parent'].isdisjoint(handles['dialog']),
  'one parent and one distinct owned dialog HWND, both actual fixture PID')
 by_choice={row['choice_key']:row for row in data['choice_readings']}
 expected_rows=[
  {'choice_key':CHOICES[2],'reference_id':REFS[2],'effect_phase_reference':'on_choice','hope_reference':2,
   'actual_reward':None,'actual_quantity':None},
  {'choice_key':CHOICES[0],'reference_id':REFS[0],'effect_phase_reference':'on_return','hope_reference':None,
   'promotion_reference':None,'actual_reward':None},
  {'choice_key':CHOICES[1],'reference_id':REFS[1],'effect_phase_reference':'on_return','hope_reference':2,
   'quantity_reference':None,'promotion_reference':False,'beak_applies_to_root_branch':None,'actual_reward':None}]
 require(len(data['choice_readings'])==3 and set(by_choice)==set(CHOICES)
  and all(by_choice[row['choice_key']]==row for row in expected_rows),'three actual separate phase/unknown references, never grants or summed amounts')
 require(data['four_original_choice_ids']==['choice_ro6_scout_1','choice_ro6_scout_3','choice_ro6_scout_2','choice_ro6_scout_4'],
  'all four original identities retained, explanatory note not a fourth actual choice')
 negatives=data['source_negative_fixtures'];by_kind={r['kind']:r for r in negatives}
 require(len(negatives)==2 and set(by_kind)=={'event','item'},'both distinct real warm source failures')
 for kind,name in [('event',MANIFEST),('item',source['icon_reference']['file'])]:
  row=by_kind[kind]
  require(row['manifest']==MANIFEST and row['damaged_member']==name and row['public_clone_only']is True
   and row['restored_sha256']==digest(name)and row['actual_reward']is None,'real restored public-clone source negative, not simulated query')
 refresh=data['same_scope_refresh_observations']
 require(len(refresh)==3 and{r['path']for r in refresh}=={'dialog_refresh','parent_refresh','same_scope_set_reference'}
  and all(r['choice_reference']==REFS[1]and type(r['source_scroll'])is int and r['source_scroll']>0
   and r['manual_item_retained']is True for r in refresh),'three real refresh paths preserve actual scroll/manual-item state')
 return data,{'receipt':rel(value),'sha256':digest(value),'reviewed_native_source_sha256':reviewed_sha,
  'source_selected_files':len(selected),'source_unchanged':True,'source_join':joined,'unique_checks':data['unique_checks'],
  'actual_assertion_executions':data['successful_assertion_executions_including_repeated_guards'],
  'actual_parent_client_size':[1050,720],'actual_dialog_client_size':[900,680],'screenshots':len(images),
  'actual_Qt_exit':0,'actual_windows_closed':True,'owned_process':process_ref,'actual_choice_readings':3,
  'game_or_chat_verified':False,'images_visually_reviewed_by_helper':False}


def visual_review(value,window):
 name='verification/sections/297-preparation/root-visual-review.json';review=load(name)
 require(review['section']==297 and review['kind']=='root_archived_native_images_review'
  and review['actual_images_opened_with_view_image']is True,'root actually reviewed new297 images')
 expected={rel(path(value).with_name(Path(row['path']).name)):row['sha256']for row in window['screenshots']}
 require(review['images']==expected and review['actual_image_count']==len(expected),'root visual review exact all actual images')
 return{'receipt':name,'sha256':digest(name),'actual_root_reviewed_images':len(expected),'helper_performed_visual_review':False}


def historical_presentation_scope(tests):
 base='verification/sections/297-preparation/historical295-presentation-scope'
 original=base+'/original-test.py';name=base+'/migration.json';record=load(name)
 require(record['kind']=='PROACTIVE_HISTORICAL_PRESENTATION_SCOPE_REPLAY_NOT_FAILED_TEST_REPAIR'
  and record['path']==HISTORICAL_TEST and record['before_sha256']==digest(original)==HISTORICAL_BEFORE_SHA
  and record['after_sha256']==digest(HISTORICAL_TEST)==HISTORICAL_AFTER_SHA
  and tests['source_sha256_after'][HISTORICAL_TEST]==HISTORICAL_AFTER_SHA,
  'historical295 exact original and final tested maintenance bytes')
 require(record['all_original_assertion_AST_preserved']is True
  and record['legacy37_comparison_still_includes_expedition_event']is True
  and record['only_new297_reference_temporarily_disabled_for_historical295_player_comparison']is True
  and record['current_default37_nontarget_and190resource_hashes_covered_by']=='tests/test_expedition_integration_297.py'
  and record['production_source_changes']is False and record['actual_tests_executed_by_this_script']is False,
  'maintenance producer does not claim product execution or change source behavior')
 old=ast.parse(path(original).read_text(encoding='utf8'));new=ast.parse(path(HISTORICAL_TEST).read_text(encoding='utf8'))
 method='test_non_target_player_output_is_exactly_unchanged'
 old_fn=next(n for n in ast.walk(old)if isinstance(n,ast.FunctionDef)and n.name==method)
 new_fn=next(n for n in ast.walk(new)if isinstance(n,ast.FunctionDef)and n.name==method)
 require(len(new_fn.body)==2 and isinstance(new_fn.body[1],ast.With),'only historical presentation loop wrapped')
 wrapper=new_fn.body[1]
 call=ast.parse("patch('rouge.player_node_information.expedition_results.event_reference',return_value=None)",mode='eval').body
 require(len(wrapper.items)==1 and wrapper.items[0].optional_vars is None
  and ast.dump(wrapper.items[0].context_expr,include_attributes=False)==ast.dump(call,include_attributes=False),
  'disable only new297 presentation reference during historical comparison')
 new_fn.body=[new_fn.body[0],*wrapper.body]
 require(ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),
  'all original module/assertion AST and37 event loop exactly preserved after unwrapping')
 return{'receipt':name,'sha256':digest(name),'original_test':original,'original_sha256':HISTORICAL_BEFORE_SHA,
  'path':HISTORICAL_TEST,'final_tested_sha256':HISTORICAL_AFTER_SHA,'all_original_module_AST_preserved_after_exact_wrapper_removal':True,
  'legacy37_includes_target_event':True,'current_default37_nontarget_and190resources_verified_by_new_included_tests':True,
  'proactive_historical_scope_replay_not_failed_test_repair':True,'production_source_changes':False}


def promotion(value,tests):
 record=load(value)
 require(record['section']==297 and type(record['promoted'])is dict
  and set(record['existing_production_changes'])==CHANGED_EXISTING,'actual root promotion and exact two old integration files')
 expected=set(CHANGED_EXISTING)|{CANONICAL,BUILDER,DATA,'rouge/expedition_results.py','rouge/expedition_results_view.py',
  *('tests/'+m.split('.')[-1]+'.py'for m in MODULES[:3])}
 expected|={p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file()}
 require(set(record['promoted'])==expected,'exact promoted expedition feature scope, not prefilled path count')
 current={name:digest(name)for name in sorted(expected)}
 require(all(tests['source_sha256_after'].get(n)==v for n,v in current.items()),'final feature bytes from actual tested source map')
 maintenance=historical_presentation_scope(tests);current[HISTORICAL_TEST]=maintenance['final_tested_sha256']
 return current,{'receipt':rel(value),'sha256':digest(value),'actual_promoted_paths':len(expected),
  'separately_maintained_historical_test':maintenance,'feature_and_maintenance_paths':len(current),
  'initial_promotion_is_provenance_not_final_acceptance':True,
  'revisions_since_original_promotion':{n:{'original':record['promoted'][n],'final_tested':v}
   for n,v in current.items()if n in record['promoted']and record['promoted'][n]!=v}}


def main(args):
 require(Path(__file__).resolve()==(HERE/'close_section_297.py').resolve(),'reviewed canonical cache helper')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 require(branch=='codex/p2-development'and parent==PARENT and not(ROOT/'verification/sections/297.json').exists(),
  'authorized branch/parent/exclusive receipt')
 source,source_ref=packet();tests,test_ref=necessary(args.necessary_receipt,parent)
 feature_map,promotion_ref=promotion(args.promotion_receipt,tests);map_ref=rejected_map_attempt()
 window,window_ref=native(args.window_receipt,args.window_process_receipt,tests,args.native_source_sha256,source)
 window_ref['root_visual_review']=visual_review(args.window_receipt,window)
 main_ref=original_window(args.main_window_receipt,args.focus_receipt,window,tests,args.necessary_receipt,args.window_receipt)
 full=load(FULL)
 require(digest(FULL)==FULL_SHA and full['after_section']==290 and full['available_checks_passed']is True
  and full['scope_not_reduced']is True and full['complete_repository_validation']is False and full['P2_complete']is False,
  'reuse historical290 full original source, never new297 full')
 cp=load('DEVELOPMENT_CHECKPOINT.json')
 require(cp['completed_sections']==cp['latest_functional_section']==296 and cp['next_section']==297
  and cp['active_section']['section']==297 and cp['policy']['priority_order']==['P3','P2','P1']
  and cp['policy']['current_user_batch_target_section']is None and cp['policy']['stop_after_section']is None,
  'actual296 to active297, P3 first and no numeric endpoint')
 require(cp['last_full_validation']['after_section']==290 and cp['current_available_full_validation']['section']==290
  and cp['policy']['full_validation_interval']==15 and cp['policy']['full_validation_anchor_section']==125
  and 125+((297-125)//15+1)*15==305,'unchanged actual full cadence290/305')
 cloud=cp['last_verified_cloud_save'];proof=load(cloud['proof'])
 require(cloud['section']==296 and digest(cloud['proof'])==cloud['proof_sha256']and proof['passed']is True
  and proof['commit']==proof['remote_HEAD']==cloud['commit']and proof['push_primary_exit']==0,'actual preceding296 ordinary publication')
 docs={n:path(n).read_bytes()for n in('DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','AGENTS.md')}
 progress=path('PROJECT_PROGRESS.md').read_bytes()
 require(sha256(progress).hexdigest()==PROGRESS_SHA_BEFORE and all(s in progress.decode()for s in(
  '81个关卡、59张独立原图','其中10图/18关已有58格直接参考','15个事件/特殊关卡',
  '25个未绑定来源原场景、57个原选项','10条未解析附注','游戏内实际展示')),
  'remaining-only progress unchanged, no gaps retired through partial references or failed maps')
 now=datetime.now(timezone(timedelta(hours=8))).isoformat()
 capability=('未涉足之树三种选择按完整身份集中阅读：休息的即时2希望、普通派出尚未明确的归来物资、'
  '探索源头归来时的2希望与怦然信标分列；保留不进阶、归来时点及喙适用关系的资料边界。'
  '手动打开信标固定图标、用途、完整说明及解锁原文，默认不选；'
  '同事件刷新保留阅读，换选项或来源失效清除旧物品，恢复后不自动重选。')
 limits=['只阅读固定资料，不代表当前可选、派出者、已归来、实际收益、数量、培养或服务器执行；信标数量未知。',
  '原文进入新区域与社区下一层分别保留；特殊区域、归来时钟、普通派出是否必然进阶和喙对源头的关系不猜测。',
  '四条原choice身份与说明块分开；不增加实际游戏按钮，不放宽原资源/资格、17typed、25/57入口或10条未解析附注。',
  '本节完整190旧资源查询和37其它事件玩家输出逐哈希保持；仅target玩家输出明确延后结果。',
  '两图首轮拟合均失败，原4px不改、不调点，不晋升、不计功能；regular12/24、direct10/18/58及81/59整图缺口保持。',
  '只必要检查与新隔离Windows流程；290完整可用范围沿用原source，下次305，P3/P2/P1仍未完成。',
  '识别最后、无数字终点，不推荐/排序/自动选路，不操作游戏、聊天或私人状态。']
 receipt={'section':297,'kind':'functional_section','title':TITLE,'at_Beijing':now,'branch':branch,'prior_commit':parent,
  'remaining_item':'P3具名奖励来源、具体选择及延后结果说明','new_capability':capability,'files':sorted(feature_map),
  'source_sha256':feature_map,'source_reference':source_ref,'source_promotion':promotion_ref,
  'rejected_map_attempt_not_functional_completion':map_ref,'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),
  'existing_source_changes_including_test_maintenance':sorted(CHANGED_EXISTING|{HISTORICAL_TEST}),
  'historical295_presentation_scope_replay':promotion_ref['separately_maintained_historical_test'],
  'existing_engine_or_typed_reward_qualification_or_run_state_changed':False,
  'old_resource_query_count_unchanged':190,'other_event_player_output_count_unchanged':37,
  'typed_named_grant_count_unchanged':17,'unparsed_notes_unchanged':10,'original_entry_gaps_unchanged':[25,57],
  'remaining_global_stage_floor_gaps_unchanged':15,'partial_direct_reference_scope_unchanged':[10,18,58],
  'whole_map_gaps_unchanged':[81,59],'necessary_validation':test_ref,
  'native_windows_validation':{**window_ref,'original_project_window':main_ref},
  'full_validation':{'receipt':FULL,'sha256':FULL_SHA,'after_section':290,'full_suite_rerun':False,
   'new297_source_full_validation_claimed':False,'scope_not_reduced':True,'next_periodic_section':305,
   'complete_repository_validation':False},'PROJECT_PROGRESS_unchanged_sha256':PROGRESS_SHA_BEFORE,
  'limits':limits,'next_section':298,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'P3_complete':False,'P2_complete':False}
 history='historical_before297_current_pointers';require(history not in cp,'exclusive pre297 pointers')
 cp[history]={k:deepcopy(cp[k])for k in('current_section_save','current_section_validation','latest_section_environment',
  'active_section','current_batch','cloud_publication_closeout')if k in cp}
 cp.pop('active_section',None);cp.pop('cloud_publication_closeout',None)
 cp.update(completed_sections=297,latest_functional_section=297,next_section=298,
  batch_status='P3_SECTION297_VALIDATED_AWAITING_PUBLICATION',next_full_validation_after=305,
  next_action='从298继续有证P3剩余事项，无数字终点；下次完整可用全量305。')
 cp['policy']['next_full_validation_after']=305;cp['current_batch_commit_policy']['next_full_validation_after']=305
 cp['current_batch'].update(status=cp['batch_status'],next_section=298,next_section_started=False,
  receipt='verification/sections/297.json',next_full_validation_after=305,batch_closed=False)
 cp['confirmed_next_stage_direction'].update(last_completed_functional_section=297,next_functional_section_started=False)
 cp['sections'].append({'number':297,'completion_ref':'p3-section-297','topic':TITLE,'verification':'verification/sections/297.json'})
 cp['current_section_save']={'section':297,'verification':'verification/sections/297.json','scope':'current_functional_section',
  'binding':'enclosing_commit','commit_reference':'commit containing297 expedition source/manual item reader, actual validation, requirements and cloud index'}
 cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_section_validation']={'section':297,'receipt':'verification/sections/297.json','necessary_methods_passed':test_ref['methods_run'],
  'native_isolated_window_checks':window['unique_checks'],'full_suite_rerun':False,'last_full_receipt':FULL,'full_source_is_historical290':True}
 cp['latest_section_environment']={'section':297,'receipt':'verification/sections/297.json',
  'native_windows':f"{test_ref['methods_run']} actual necessary; {window['unique_checks']} unique native; manual MainWindow/expedition dialog/beacon and {window_ref['screenshots']}PNG; original visible/private5 unchanged",
  'native_game_or_chat_verified':False,'new_Linux_Wine_full_run':False,'current_section_full_rerun':False,'last_full_receipt':FULL}
 cp['functional_sections_since_latest_requirement']=list(dict.fromkeys([*cp['functional_sections_since_latest_requirement'],297]))
 completed=(f'## 功能第297节 · {TITLE}\n\n{now}。{capability}\n\n'
  f"实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过；"
  f"{window_ref['screenshots']}张代表性PNG由根代理逐图查看，原项目窗口更新/私人5路径不变。"
  '作者24与UI16为本次必要子集，不重复相加；190旧资源和37其它事件输出保持。'
  '295历史展示比较仅在原37事件循环外屏蔽新增297说明，原断言全部保留；当前默认输出由297测试另核。'
  '两图首轮拟合失败原件保留、原4px未调整，不计完成。未减少其它入口/数量/层数待办，PROJECT_PROGRESS不变。'
  '实际来源和回执verification/sections/297.json；290全量沿用原来源，下次305、后续298，无数字终点。待普通推送核对。\n\n')
 mutations={'verification/sections/297.json':encode(receipt),'DEVELOPMENT_CHECKPOINT.json':encode(cp),
  'PROJECT_COMPLETED.md':completed.encode()+docs['PROJECT_COMPLETED.md']}
 wip=docs['WORK_IN_PROGRESS.md'].decode();require('## 功能第296节'in wip,'preserve296 onward history')
 mutations['WORK_IN_PROGRESS.md']=(completed+wip[wip.index('## 功能第296节'):]).encode()
 req=docs['PROJECT_REQUIREMENTS.md'].decode();a,b=req.index('<!-- current-delivery:start -->'),req.index('<!-- current-delivery:end -->')
 block=('<!-- current-delivery:start -->\n## 当前交付与续接 · 第297节\n\n2026-10-16继续P3，无数字终点。'+capability
  +f"实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过，原窗口更新/私人5路径不变。"
  +'原190资源/37其它事件输出与资格保持；原17typed、10附注、25/57入口、15层数和81/59整图待办不变。'
  +'两图首轮拟合失败不计功能；290全量原来源沿用，下次305；P3→P2→P1、识别最后，无路线建议。'
  +'待普通推送核对，源码/要求/回执/索引同提交。\n')
 mutations['PROJECT_REQUIREMENTS.md']=(req[:a]+block+req[b:]).encode()
 agents=docs['AGENTS.md'].decode();a,b=agents.index('## 当前续接 · 第296节'),agents.index('## 当前优先顺序与输出可读性')
 mutations['AGENTS.md']=(agents[:a]+'## 当前续接 · 第297节已完成功能与必要/原生验收\n\n'+capability
  +'来源及实际回执verification/sections/297.json；原190资源/37其它事件、资格、17typed与15/25/57/10缺口保持。'
  +'失败地图拟合不计完成，旧12/24和10/18/58不变。原窗口更新/私人5路径不变；未跑297全量，290完整范围沿用原来源。'
  +'下一节298/下次305，无数字终点。P3→P2→P1、识别最后，不推荐/排序/自动选路。'
  +'待普通推送核对真实远端，源码/要求/验收/索引同提交。\n\n'+agents[b:]).encode()
 require('初次招募时即处于已进阶状态'in mutations['PROJECT_REQUIREMENTS.md'].decode()
  and'初次招募即处于已进阶状态'in mutations['AGENTS.md'].decode(),'preserve verified recruitment terminology')
 require(all(str(i)+'.'in mutations['AGENTS.md'].decode().split('## 当前续接')[0]for i in range(1,6)),
  'preserve five highest-priority independent-judgment requirements')
 archive=ROOT/'verification/sections/297-preparation/closeout-tools';require(not archive.exists(),'exclusive public closeout archive')
 copies={'close_section_297.py':path(HERE/'close_section_297.py').read_bytes(),'CONTRACT.md':path(HERE/'CONTRACT.md').read_bytes()}
 copies.update({'before-'+n:raw for n,raw in docs.items()})
 manifest={'kind':'SECTION297_PUBLIC_CLOSEOUT_TOOLS_NOT_PRIVATE_STATE',
  'files':{n:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}for n,raw in copies.items()},
  'private_contents_or_hash_lists_copied':False,'helper_tests_Qt_GUI_game_chat_Git_or_full_executed':False}
 print(json.dumps({'gates_passed':True,'apply_requested':args.apply,'necessary_actual_methods':test_ref['methods_run'],
  'native_actual_unique_checks':window['unique_checks'],'source_join':window_ref['source_join'],'feature_paths':len(feature_map),
  'planned_public_files':list(mutations),'PROJECT_PROGRESS_modified':False,'full_rerun':False,'next_full_section':305,
  'numeric_endpoint':None,'cloud_published':False},ensure_ascii=False))
 if not args.apply:return
 for n,raw in docs.items():require(path(n).read_bytes()==raw,'public document unchanged before apply '+n)
 require(path('PROJECT_PROGRESS.md').read_bytes()==progress,'todo bytes unchanged before apply')
 check_map(tests['source_sha256_after'],'final pre-write necessary')
 check_map(window['source_sha256_after'],'final pre-write complete native source set')
 archive.mkdir(parents=True)
 for n,raw in copies.items():
  with(archive/n).open('xb')as stream:stream.write(raw)
 with(archive/'archive-manifest.json').open('xb')as stream:stream.write(encode(manifest))
 for n,raw in mutations.items():
  destination=ROOT/n;destination.parent.mkdir(parents=True,exist_ok=True)
  with destination.open('xb'if n=='verification/sections/297.json'else'wb')as stream:stream.write(raw)
 print(json.dumps({'section':297,'local_closeout_written':True,'cloud_published':False,'next_section':298,'next_full_section':305}))


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--necessary-receipt',required=True);parser.add_argument('--window-receipt',required=True)
 parser.add_argument('--window-process-receipt',required=True);parser.add_argument('--native-source-sha256',required=True)
 parser.add_argument('--promotion-receipt',default='verification/sections/297-preparation/promotion.json')
 parser.add_argument('--main-window-receipt',default='verification/sections/297-main-window.json')
 parser.add_argument('--focus-receipt',default='verification/sections/297-main-window-focus.json')
 parser.add_argument('--apply',action='store_true');main(parser.parse_args())
