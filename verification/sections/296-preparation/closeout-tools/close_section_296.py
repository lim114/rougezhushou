"""Unexecuted strict296 closeout: preview by default; --apply writes public delivery.

No tests/Qt/game/chat/private contents/window restart/Git mutation are run.
Native and necessary counts are read only from the actual final receipts.
"""
import argparse,ast
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,re,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'.cache/p3-296-closeout/revision5'
PARENT='c772147f4ee4846464b32b88f51c88f874db3fcd'
TITLE='固定战斗对应事件入口反查与无效验尸配置阅读'
CANONICAL='scripts/verify_battle_entry_references_window_296.py'
FULL='verification/full-290/summary.json'
FULL_SHA='2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
REVERSE_PACKET='research/p3-battle-event-references-296'
CONFIG_PACKET='research/p3-stage-entry-configuration-296'
EVENT_MANIFEST=REVERSE_PACKET+'/source-manifest.json'
CONFIG_MANIFEST=CONFIG_PACKET+'/manifest.json'
PACKETS=(REVERSE_PACKET,CONFIG_PACKET)
CHANGED_EXISTING={'rouge/app.py','rouge/battle_view.py','rouge/node_catalog_view.py','rouge/player_node_information.py'}
MODULES=['tests.test_stage_entry_configuration_296','tests.test_battle_event_references_296',
 'tests.test_battle_entry_reference_view_296','tests.test_battle_entry_integration_296',
 'tests.test_stage_context','tests.test_event_planning','tests.test_event_preview_filters_292',
 'tests.test_player_node_information_286','tests.test_node_catalog_view','tests.test_documented_item_integration_295']
STAGES=['ro6_t_1','ro6_t_2','ro6_t_3','ro6_t_4','ro6_t_5','ro6_e_t_3','ro6_e_t_4','ro6_e_t_5']
PINNED={
 EVENT_MANIFEST:'c6a7d1294e48b6fec896f736d56baa0c09f25f3365de471cc11c88d74705de21',
 'rouge/data/battle-event-references.json':'9381a854dfaef444f51e01e9508cf2a4fa61b4fa15507a5b261e5d8a7b847e4d',
 CONFIG_MANIFEST:'47b272989530c116163c59e683dca7cf77a6798f2eb1180b4d112ad350c01976',
 'rouge/data/stage-entry-configuration-reference.json':'d30165125724bad4d520bd84506666f7c4eba151080a4b231bda8721d8761bcf'}
NATIVE_ONLY_DOCUMENT='research/p3-stage-context/community-main.html'
NATIVE_ONLY_DOCUMENT_SHA='366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9'
PROGRESS_SHA_BEFORE='111962b1622515c494ae81a06ac19b915db797211e926165a9947b80fade8a0b'

def require(value,message):
 if value is not True:raise ValueError('296 closeout prerequisite: '+message)

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
 require(process['section']==296 and process['kind']=='actual_native_window_owned_process_execution'
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
 require(path(main_value).resolve()==(ROOT/'verification/sections/296-main-window.json').resolve()
  and path(focus_value).resolve()==(ROOT/'verification/sections/296-main-window-focus.json').resolve(),
  'strict same-section canonical296 main/focus receipt paths')
 require(main['section']==296 and focus['section']==296
  and main['necessary_receipt_sha256']==digest(necessary_value)
  and main['native_receipt_sha256']==digest(native_value)
  and main['native_receipt']==rel(native_value) and main['necessary_receipt']==rel(necessary_value)
  and focus['main_receipt_sha256']==digest(main_value),
  'actual296 main binds both final evidence receipts; focus binds exact same main bytes')
 require(main['source_sha256_before']==main['source_sha256_after']==fixture['source_sha256_after']
  and set(main['source_sha256_after'])==selected_window_sources(),
  'same final actual native_selected source map stable through original window restart')
 check_map(main['source_sha256_after'],'original296 window final native_selected sources')
 timestamps={name:datetime.fromisoformat(value.replace('Z','+00:00')) for name,value in {
  'started':main['started_utc'],'finished':main['finished_utc'],'focus':focus['at_utc'],
  'necessary_finished':necessary_data['finished_utc'],'native_finished':fixture['finished_at']}.items()}
 require(all(value.tzinfo is not None and value.utcoffset() is not None for value in timestamps.values()),
  'actual main/focus/final-check timestamps are timezone-aware')
 require(timestamps['started']>timestamps['necessary_finished'] and timestamps['started']>timestamps['native_finished']
  and timestamps['finished']>=timestamps['started'] and timestamps['focus']>=timestamps['finished'],
  'original296 restart occurs after both final validations; focus follows completed main receipt')
 require(main['passed'] is True and main['private_file_hash_comparison_count']==5 and main['private_hashes_equal'] is True
  and main['changed_private_paths']==[] and main['private_contents_parsed_copied_or_restored'] is False and main['no_private_restoration'] is True,
  'actual original-window update/private5 hash unchanged, no content parsing/copy/restore')
 require(len(main['visible_windows'])==1,'one visible original project window');visible=main['visible_windows'][0]
 require(visible['visible'] is True and visible['responding'] is True and visible['minimized'] is False and visible['hwnd']>0
  and visible['pid']!=fixture['process_id'],'original window responsive/visible and not fixture')
 require(focus['visible'] is True and focus['pid']==visible['pid'] and focus['hwnd']==focus['actual_foreground']==visible['hwnd'],
  'actual foreground original project window')
 return {'receipt':rel(main_value),'sha256':digest(main_value),'focus_receipt':rel(focus_value),'focus_sha256':digest(focus_value),
  'section':296,'necessary_receipt_sha256':digest(necessary_value),'native_receipt_sha256':digest(native_value),
  'native_selected_current_source_unchanged':True,'started_after_final_necessary_and_native':True,'focus_after_main_finished':True,
  'private_hash_comparisons':5,'changed_private_paths':0,'visible_responsive_foreground':True,'private_contents_read_by_helper':False}


def packet():
 """Read exact public files only; do not import the product or an existing lru."""
 check_map(PINNED,'fixed source authority')
 records={}
 for name in (EVENT_MANIFEST,CONFIG_MANIFEST):
  value=load(name)
  require(type(value['files'])is dict and bool(value['files']),'source manifest members')
  for member,expected in value['files'].items():
   require(type(expected)is dict and type(expected['bytes'])is int and expected['bytes']>=0,
    'actual source member length')
   check_map({member:expected['sha256']},'fresh source member')
   require(path(member).stat().st_size==expected['bytes'],'fresh source member length '+member)
  if 'data_file'in value:
   require(digest(value['data_file'])==value['data_sha256'],'separate runtime data binding')
  records[name]={'sha256':digest(name),'bound_members':len(value['files'])}
 reverse=load('rouge/data/battle-event-references.json')
 expected={'raw_edges':14,'admitted_edges':11,'explicit_exclusions':3,'events':5,'choices':8,'stage_ids':8}
 require(reverse['schema_version']==1 and reverse['reference_kind']=='fixed_battle_documented_event_choices'
  and reverse['stage_ids']==STAGES and reverse['counts']==expected,'exact 8-stage/14-edge source scope')
 edges=reverse['edges']
 require(len(edges)==14 and len({e['reference_id']for e in edges})==14
  and sum(e['excluded_by_explicit_difficulty']is False for e in edges)==11
  and sum(e['excluded_by_explicit_difficulty']is True for e in edges)==3,
  '14 unique source identities, 11 admitted and 3 explicit exclusions')
 exclusions={(e['stage_id'],e['event_id'],e['scene_key'],e['choice_key'])for e in edges
  if e['excluded_by_explicit_difficulty']}
 require(exclusions=={(s,e,e+':scene:'+str(n),e+':scene:'+str(n)+':choice:0')for s,e,n in
  [('ro6_t_3','community_group_014',2),('ro6_t_4','community_group_015',2),('ro6_t_5','community_group_016',8)]},
  'ordinary versions of three explicitly emergency choices excluded')
 config=load('rouge/data/stage-entry-configuration-reference.json')
 require(config['schema']=='stage_entry_configuration_reference_v1'
  and config['reference_kind']=='documented_stage_entry_configuration'
  and config['stage']['id']=='ro6_t_12' and config['stage']['name']=='无效验尸'
  and len(config['rows'])==4 and [r['main_floor_reference']for r in config['rows']]==[3,4,5,None],
  'autopsy four configurations and fake-layer boundary')
 require(all(config[k]is None for k in('actual_eligibility','actual_node','actual_entry','actual_reward',
  'actual_count','complete_stage_floor_pool')),'autopsy actual eligibility and results unknown')
 require(all(r['configured_limit_is_actual_count']is False
  and all(r[k]is None for k in('actual_feature_attached','actual_node_marked','actual_stage_replacement','actual_count'))
  for r in config['rows']),'source limit is not count or attachment')
 build=load(CONFIG_PACKET+'/build-receipt.json')
 require(build['status']=='SOURCE_SELECTION_AND_DATA_BUILD_ONLY'
  and build['selected_complete_objects']==21 and build['feature_rows']==4
  and build['runtime_main_floor_references']==[3,4,5,None]
  and build['qt_or_product_tests']is False and build['game_chat_private_operations']==0
  and build['data_sha256']==digest('rouge/data/stage-entry-configuration-reference.json'),
  '21 complete original objects; derived source build is not product validation')
 rbuild=load(REVERSE_PACKET+'/build-receipt.json')
 require(rbuild['kind']=='PURE_SOURCE_RECONSTRUCTION_NOT_PRODUCT_PASS'
  and rbuild['source_manifest_sha256']==PINNED[EVENT_MANIFEST] and rbuild['counts']==expected
  and rbuild['network_game_chat_private_Qt_or_tests_executed']is False,
  'reverse source build is not product validation')
 for member,pin in rbuild['outputs'].items():
  require(digest(member)==pin['sha256']and path(member).stat().st_size==pin['bytes'],'reverse builder output '+member)
 return reverse,{'manifests':records,'reverse_counts':expected,'autopsy_complete_original_objects':21,
  'autopsy_rows':4,'autopsy_main_floor_references':[3,4,5,None],
  'current_eligibility_actual_entry_actual_reward_and_global_floor_pool_verified':False}


def selected_window_sources():
 """Interpret the reviewed bound_files literal, never execute a Qt harness."""
 tree=ast.parse(path(CANONICAL).read_text(encoding='utf8'))
 fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='bound_files')
 assignment=next(n for n in fn.body if isinstance(n,ast.Assign)
  and any(isinstance(t,ast.Name)and t.id=='names'for t in n.targets))
 require(isinstance(assignment.value,ast.Set),'selected native literal source set')
 constants={'CANONICAL':CANONICAL,'EVENT_MANIFEST':EVENT_MANIFEST,'CONFIG_MANIFEST':CONFIG_MANIFEST}
 names=set()
 for value in assignment.value.elts:
  if isinstance(value,ast.Name):
   require(value.id in constants,'fixed native source constant');names.add(constants[value.id])
  else:
   require(isinstance(value,ast.Constant)and type(value.value)is str,'literal native source path');names.add(value.value)
 for name in (EVENT_MANIFEST,CONFIG_MANIFEST):
  manifest=load(name);names.update(manifest['files'])
  if'data_file'in manifest:names.add(manifest['data_file'])
  names.update(p.relative_to(ROOT).as_posix()for p in path(name).parent.rglob('*')if p.is_file())
 require({CANONICAL,EVENT_MANIFEST,CONFIG_MANIFEST,'rouge/battle_entry_reference_view.py',
  'tests/test_battle_entry_reference_view_296.py','tests/test_battle_entry_integration_296.py'}<=names,
  'new model/UI/integration and public source guard included')
 return names


def unchanged_existing_sources(data):
 previous=load('verification/sections/295.json');reference=previous['necessary_validation']
 require(digest(reference['receipt'])==reference['sha256'],'actual previous295 necessary reference')
 old=load(reference['receipt'])
 require(old['section']==295 and old['exit_code']==0 and old['source_unchanged']is True
  and old['source_sha256_before']==old['source_sha256_after'],'original295 actual stable source map')
 unchanged={name:expected for name,expected in old['source_sha256_after'].items()
  if name.startswith('rouge/')and name not in CHANGED_EXISTING
  and(name.endswith('.py')or(name.startswith('rouge/data/')and name.endswith('.json')))}
 require(bool(unchanged)and all(data['source_sha256_after'].get(name)==value for name,value in unchanged.items()),
  'every previous product Python/static JSON unchanged except four intended integrations')
 scope=load('verification/sections/296-preparation/scope.json')
 require(scope['section']==296 and scope['parent']==PARENT and scope['functional_complete']is False,
  'original before-functional scope remains a preparation receipt')
 require(set(scope['before_existing_sources'])==CHANGED_EXISTING,'exact four existing sources authorized')
 for name in CHANGED_EXISTING:
  before='verification/sections/296-preparation/before-'+Path(name).name
  require(digest(before)==scope['before_existing_sources'][name]['sha256']==old['source_sha256_after'][name],
   'preserved true pre296 source '+name)
 require(digest('PROJECT_PROGRESS.md')==PROGRESS_SHA_BEFORE,'remaining-only todo bytes unchanged')
 return {'previous_section':295,'previous_necessary_receipt':reference['receipt'],
  'previous_necessary_sha256':reference['sha256'],'unchanged_existing_Python_static_JSON_files':len(unchanged),
  'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),
  'old_research_or_images_not_in_this_producer_are_not_required_or_inserted':True,
  'PROJECT_PROGRESS_unchanged':True}



def join_selected_native_sources(necessary_map,native_map,label):
 """Permit exactly this one native-guarded old document, never arbitrary missing paths.

 Native guard proves its actual run bytes before/after. Current bytes and the
 fixed parent blob independently close the one source absent from necessary.
 Historical native common sources compare only to their historical producer;
 they are not silently asserted equal to changed live code.
 """
 extra=set(native_map)-set(necessary_map)
 require(extra=={NATIVE_ONLY_DOCUMENT},label+' exact one native-only historical document')
 common=set(native_map)&set(necessary_map)
 require(bool(common)and all(native_map[name]==necessary_map[name]for name in common),
  label+' all common source bytes exactly equal')
 require(native_map[NATIVE_ONLY_DOCUMENT]==NATIVE_ONLY_DOCUMENT_SHA==digest(NATIVE_ONLY_DOCUMENT),
  label+' exact additional actual native/current source bytes')
 parent_bytes=subprocess.check_output(['git','show',PARENT+':'+NATIVE_ONLY_DOCUMENT],cwd=ROOT)
 require(sha256(parent_bytes).hexdigest()==NATIVE_ONLY_DOCUMENT_SHA,
  label+' unchanged parent Git blob bytes independently verified')
 return {'necessary_source_files':len(necessary_map),'native_selected_source_files':len(native_map),
  'common_source_files':len(common),'common_source_bytes_equal':True,
  'native_is_subset_of_necessary':False,
  'additional_native_source_files':{NATIVE_ONLY_DOCUMENT:{
   'sha256':NATIVE_ONLY_DOCUMENT_SHA,'actual_native_before_after_guarded':True,
   'current_file_verified':True,'parent_commit':PARENT,'parent_blob_verified':True,
   'not_in_necessary_producer_source_map':True}},
  'joined_source_files':len(set(necessary_map)|set(native_map)),
  'arbitrary_missing_sources_permitted':False}


def necessary(value,parent):
 data=load(value)
 require(data['section']==296 and data['kind']=='necessary_change_related_tests_not_full_suite'
  and type(data['exit_code'])is int and data['exit_code']==0 and data['source_unchanged']is True
  and data['source_sha256_before']==data['source_sha256_after'],'actual final necessary0/stable source')
 require(data['modules']==MODULES and data['argv'][1:7]==['-B','-X','utf8','-m','unittest','-v']
  and data['argv'][-len(MODULES):]==MODULES and data['source_commit_before']==parent==PARENT,
  'all ten exact necessary modules/current parent')
 require(data['game_sampling_verified']is False and data['chat_verified']is False
  and data['full_scope_reduced']is False and data['full_suite_rerun']is False,'necessary-only no external/full claims')
 minimum={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/**/*.py')}
 minimum|={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/data/*.json')}
 minimum|={'tests/'+m.split('.')[-1]+'.py'for m in MODULES}
 minimum|=selected_window_sources()-{NATIVE_ONLY_DOCUMENT}
 for packet_name in PACKETS:
  minimum|={p.relative_to(ROOT).as_posix()for p in(ROOT/packet_name).rglob('*')if p.is_file()}
 require(minimum<=set(data['source_sha256_after']),'all production/static data, ten modules and common selected native sources bound; exact one separately native-verified document excluded')
 check_map(data['source_sha256_after'],'final necessary')
 baseline=unchanged_existing_sources(data)
 stderr=path(value).with_name('stderr.txt');log=path(stderr).read_text(encoding='utf8')
 matches=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',log)
 require(len(matches)==1 and int(matches[0][0])>0 and log.rstrip().endswith('OK')
  and not re.search(r'^(FAIL|ERROR):',log,re.M),'actual terminal methods/OK, no prefilled test count')
 return data,{'receipt':rel(value),'sha256':digest(value),'stderr':rel(stderr),'stderr_sha256':digest(stderr),
  'stdout_sha256':digest(path(value).with_name('stdout.txt')),'actual_exit':0,
  'methods_run':int(matches[0][0]),'seconds':float(matches[0][1]),'source_files':len(data['source_sha256_after']),
  'source_unchanged':True,'modules':MODULES,'author_checks_are_subsets_not_added_again':True,
  'existing_source_boundary':baseline}


def source_expected_tokens(reverse):
 """Reconstruct exact documented identity from public bytes; not an eligibility query."""
 catalog=load('rouge/data/node-catalog.json');manifest=load(EVENT_MANIFEST)
 identity={'manifest_sha256':digest(EVENT_MANIFEST),
  'reference_data_sha256':manifest['files']['rouge/data/battle-event-references.json']['sha256'],
  'node_catalog_sha256':manifest['files']['rouge/data/node-catalog.json']['sha256'],
  'event_planning_data_sha256':manifest['files']['rouge/data/event-planning-reference.json']['sha256'],
  'battle_previews_sha256':manifest['files']['rouge/data/battle-previews.json']['sha256'],
  'game_commit':reverse['sources']['original_game']['commit'],
  'documents':[{'revision':r['revision'],'sha256':r['sha256']}for r in reverse['sources']['documents']]}
 tokens={}
 for edge in reverse['edges']:
  if edge['excluded_by_explicit_difficulty']:continue
  event=next(e for e in catalog['events']if e['id']==edge['event_id'])
  i,scene=next((i,s)for i,s in enumerate(event['scenes'],1)if s['key']==edge['scene_key'])
  j=next(j for j,c in enumerate(scene['choices'],1)if c['key']==edge['choice_key'])
  tokens[edge['reference_id']]={'reference_kind':'fixed_battle_to_documented_event_choice',
   **{k:deepcopy(edge[k])for k in('reference_id','stage_id','event_id','scene_key','choice_key','stage_record','stage_page','level_source')},
   'scene_number':i,'choice_number':j,'source_identity':deepcopy(identity)}
 return tokens


def native(value,process_value,necessary_data,reviewed_sha,reverse):
 data=load(value)
 require(data['section']==296 and data['kind']=='isolated_native_windows_fixed_battle_entry_references'
  and data['passed']is True and data['failure']is None and data['qpa']=='windows'
  and type(data['qt_exit_code'])is int and data['qt_exit_code']==0 and data['verification_window_closed']is True,
  'actual canonical native Windows/Qt/owned-window close completion')
 require(re.fullmatch('[0-9a-f]{64}',reviewed_sha)is not None and digest(CANONICAL)==reviewed_sha,
  'explicit final reviewed canonical native source SHA, not an initial candidate pin')
 require(type(data['process_id'])is int and data['process_id']>0,'actual fixture PID independent of launcher')
 tree=ast.parse(path(CANONICAL).read_text(encoding='utf8'))
 required={call.args[1].value for call in ast.walk(tree)if isinstance(call,ast.Call)
  and isinstance(call.func,ast.Name)and call.func.id=='require'and len(call.args)>1
  and isinstance(call.args[1],ast.Constant)and type(call.args[1].value)is str}
 # Dynamic labels are additionally bound by the actual owned-HWND/image observations.
 require(type(data['checks'])is list and len(data['checks'])==len(set(data['checks']))==data['unique_checks']
  and required<=set(data['checks'])
  and data['successful_assertion_executions_including_repeated_guards']>=len(data['checks']),
  'all reviewed literal assertions represented; actual unique/repeated counts')
 selected=selected_window_sources()
 require(data['source_sha256_before']==data['source_sha256_after']
  and set(data['source_sha256_after'])==selected
  and data['source_guard_is_selected_not_all_transitive_dependencies']is True,'exact selected native source map stable')
 check_map(data['source_sha256_after'],'native final')
 source_join=join_selected_native_sources(necessary_data['source_sha256_after'],
  data['source_sha256_after'],'final native/necessary source join')
 require(data['temporary_state_root']is True and data['state_paths_replaced_before_constructor']
  ==['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE']and data['private_state_read_copied_or_restored']is False
  and data['external_entrypoints_blocked_before_original_call']is True,'temporary four state paths and external guards before constructor')
 attempts=data['external_operation_attempts']
 require(set(attempts)=={'game_enumeration','game_connect','game_capture','game_next_frame','desktop_start',
  'desktop_request','provider_chat','credential_read'}and all(type(n)is int and n==0 for n in attempts.values()),
  'all eight actual original external-entry attempts zero')
 require(data['game_operated']is False and type(data['game_captures'])is int and data['game_captures']==0
  and data['chat_sent']is False and data['chat_attempted']is False
  and data['original_project_window_operated_or_restarted']is False,'no game/chat/private/original-window operations')
 require(data['actual_process_termination_verified_by_this_script']is False
  and data['owned_supervisor_exit_and_cleanup_required_separately']is True
  and data['launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID']is True,
  'fixture does not invent process ancestry or cleanup proof')
 raw,process_ref=owned_process(process_value,value,data)
 require(data['requested_parent_client_size']==[1050,720]and data['requested_dialog_client_size']==[900,680],
  'actual one parent/dialog size contract')
 handles={'parent':set(),'dialog':set()}
 def check_handle(row):
  kind=row['kind']
  require(kind in handles and row['process_id']==data['process_id']and row['qpa']=='windows'
   and type(row['hwnd'])is int and row['hwnd']>0
   and row['client_size']==([1050,720]if kind=='parent'else[900,680]),
   'native own HWND, fixture PID and exact logical dimensions')
  handles[kind].add(row['hwnd'])
 require(bool(data['native_observations']),'actual native observations present')
 for row in data['native_observations']:check_handle(row)
 expected_images=set()
 for call in ast.walk(tree):
  if not isinstance(call,ast.Call)or not isinstance(call.func,ast.Name):continue
  index=0 if call.func.id=='save_image'else 2 if call.func.id=='damage_source'else None
  if index is not None and len(call.args)>index and isinstance(call.args[index],ast.Constant):
   require(type(call.args[index].value)is str,'literal screenshot identity');expected_images.add(call.args[index].value)
 images=data['screenshots']
 require(bool(expected_images)and len(images)==data['screenshot_count']==len(expected_images)
  and{image['name']for image in images}==expected_images,'all actual source-declared representative images, no prefilled count')
 for image in images:
  expected=raw.with_name(raw.stem+'-'+image['name']+'.png')
  require(Path(image['path']).resolve()==expected.resolve(),'unaltered raw PNG sibling provenance')
  pixels=path(path(value).with_name(expected.name)).read_bytes()
  require(sha256(pixels).hexdigest()==image['sha256']and pixels[:8]==b'\x89PNG\r\n\x1a\n'
   and len(pixels)>24 and all(n>0 for n in struct.unpack('>II',pixels[16:24])),'exact archived native PNG bytes')
  check_handle(image['native_window'])
 require(all(len(values)==1 for values in handles.values())and handles['parent'].isdisjoint(handles['dialog']),
  'one parent and one distinct owned dialog HWND, all screenshots same fixture PID')
 expected=source_expected_tokens(reverse);actual=data['navigated_documented_entries']
 require(len(actual)==len(expected)==11 and data['actually_navigated_entry_count']==len(actual)
  and data['actually_navigated_stage_count']==len(STAGES)
  and{row['reference_id']for row in actual}==set(expected),'all 11 admitted identities really navigated across eight exact stages')
 for row in actual:
  token=expected[row['reference_id']]
  require(row['emitted_token']==token and all(row[k]==token[k]for k in('stage_id','event_id','scene_key','choice_key')),
   'actual emitted full stage/event/scene/choice/page/source identity token')
  edge=next(e for e in reverse['edges']if e['reference_id']==row['reference_id'])
  anchor=row['body_reading_anchor'];heading=f"选项 {token['choice_number']}：{edge['choice_title']}"
  keys={'selected_heading','scene_number','choice_number','selection_start','selection_end',
   'scene_heading_end','next_scene_start','scroll_value','cursor_top','cursor_bottom','viewport_height','player_tab_current'}
  require(type(anchor)is dict and set(anchor)==keys
   and anchor['selected_heading']==heading and anchor['scene_number']==token['scene_number']
   and anchor['choice_number']==token['choice_number']and anchor['player_tab_current']is True,
   'actual player tab and source-derived exact choice heading inside the requested scene')
  integer_keys=keys-{'selected_heading','next_scene_start','player_tab_current'}
  require(all(type(anchor[k])is int for k in integer_keys)
   and anchor['selection_start']>anchor['scene_heading_end']>=0
   and anchor['selection_end']-anchor['selection_start']==len(heading.encode('utf-16-le'))//2
   and(anchor['next_scene_start']is None or(type(anchor['next_scene_start'])is int
    and anchor['selection_end']<=anchor['next_scene_start']))
   and anchor['scroll_value']>=0
   and 0<=anchor['cursor_top']<=anchor['cursor_bottom']<=anchor['viewport_height']
   and anchor['viewport_height']>0,'real UTF16 selection, source-scene boundaries and visible viewport anchor')
  require(re.fullmatch('[0-9a-f]{64}',row['battle_state_sha256'])is not None,'actual retained battle-state fingerprint')
 ex=data['explicit_exclusions'];source_ex={e['reference_id']:e for e in reverse['edges']if e['excluded_by_explicit_difficulty']}
 require(len(ex)==len(source_ex)==3 and{r['excluded_reference_id']for r in ex}==set(source_ex)
  and all(r['manual_navigation']is False and r['stage_id']==source_ex[r['excluded_reference_id']]['stage_id']
   and r['choice_key']==source_ex[r['excluded_reference_id']]['choice_key']for r in ex),
  'three explicit ordinary-version exclusions really rejected')
 negatives=data['source_negative_fixtures']
 require(len(negatives)==2 and{r['manifest']for r in negatives}=={EVENT_MANIFEST,CONFIG_MANIFEST}
  and all(r['temporary_only']is True and r['restored_manifest_sha256']==digest(r['manifest'])for r in negatives),
  'both source failures use restored public clones, never live bytes')
 refresh=data['same_scope_refresh_observations']
 require({r['path']for r in refresh}=={'dialog_refresh','same_stage_set','parent_reference_refresh'}
  and all(type(r['source_scroll'])is int and r['source_scroll']>0 for r in refresh),
  'three real refresh paths retain nonzero source scroll')
 require(len(data['public_observations'])==1,'one actual combined public observation record')
 public=data['public_observations'][0]
 require(public['actually_navigated_stage_ids']==sorted(STAGES)and public['actual_manual_reference_clicks']==len(actual)
  and public['guarded_explicit_exclusions']==len(ex)
  and public['actual_game_event_or_stage_entry']is None and public['actual_generated_stage_floor_pool']is None
  and public['screenshots_are_representative_not_every_stage']is True,
  'actual manual reading scope without game entry or global-floor inference')
 require(len(public['configuration_readings'])==1,'one actual autopsy configuration reading')
 config=public['configuration_readings'][0]
 require(config['stage_id']=='ro6_t_12'and config['main_floor_references']==[3,4,5,None]
  and config['event_controls_visible']is False and config['event_choice_count']==0
  and config['floor_eligibility_evaluated']is False
  and all(config[k]is None for k in('actual_entry','actual_node','actual_reward','actual_count'))
  and re.fullmatch('[0-9a-f]{64}',config['default_reader_sha256'])is not None,
  'actual four-row configuration reading remains distinct from event or current eligibility')
 return data,{'receipt':rel(value),'sha256':digest(value),'reviewed_native_source_sha256':reviewed_sha,
  'source_selected_files':len(selected),'source_unchanged':True,'source_join':source_join,'unique_checks':data['unique_checks'],
  'actual_assertion_executions':data['successful_assertion_executions_including_repeated_guards'],
  'actual_parent_client_size':[1050,720],'actual_dialog_client_size':[900,680],
  'screenshots':len(images),'actual_Qt_exit':0,'actual_windows_closed':True,'owned_process':process_ref,
  'all_documented_admitted_entries_navigated':len(actual),'all_actual_body_reading_anchors_checked':len(actual),'explicit_exclusions_guarded':len(ex),
  'images_visually_reviewed_by_helper':False,'game_or_chat_verified':False}


def visual_review(window_value,window):
 name='verification/sections/296-preparation/root-visual-review.json';review=load(name)
 require(review['section']==296 and review['kind']=='root_archived_native_images_review'
  and review['actual_images_opened_with_view_image']is True,'actual root native-image visual review')
 expected={rel(path(window_value).with_name(Path(r['path']).name)):r['sha256']for r in window['screenshots']}
 require(review['images']==expected and review['actual_image_count']==len(expected),'root reviewed all actual representative images')
 return {'receipt':name,'sha256':digest(name),'actual_root_reviewed_images':len(expected),'helper_performed_visual_inspection':False}


def preparation_evidence(directory):
 """Bind the preserved earlier run, counterexample and corrected run separately."""
 base=path(Path(directory)/'revision2/correction.json').parent.parent
 require(base.resolve()==(ROOT/'verification/sections/296-preparation/reverse').resolve(),
  'canonical public reverse preparation evidence, no private/cache clone')
 refs={}
 for folder,n,core in [
  ('backend-first',25,'0e0e957ce1b47219a226a583b25a35b1156a01e2bd7b5b210417663729ba3a11'),
  ('backend-revision2-first',27,'ab6149db963dfed0d47083fc725c49d4df6c731e357d70f225f6473cdd540add')]:
  process_path=base/folder/'process.json';process=load(process_path)
  receipt_path=base/folder/'receipt.json';record=load(receipt_path)
  require(process['kind']=='ACTUAL_CACHE_BACKEND_NECESSARY_OBSERVER'and type(process['exit_code'])is int
   and process['exit_code']==0 and process['source_unchanged']is True
   and process['source_sha256_before']==process['source_sha256_after']
   and process['not_formal_product_acceptance']is True
   and process['actual_Qt_GUI_game_chat_private_Git_operations']is False,
   'preserved actual cache observer0, not native/product scope')
  require(record['tests_run']==n and record['failures']==record['errors']==record['skipped']==0
   and record['success']is True and record['Qt_modules_imported']==[]
   and record['model_sha256']==core,'actual separate original25/corrected27 cache result')
  refs[folder]={'process':rel(process_path),'process_sha256':digest(process_path),'receipt':rel(receipt_path),
   'receipt_sha256':digest(receipt_path),'actual_cache_methods':n,'not_added_to_final_necessary_count':True}
 counter_path=base/'cached-choice-original-counterexample/result.json';counter=load(counter_path)
 require(counter['kind']=='ACTUAL_ISOLATED_CACHED_CHOICE_DESCRIPTION_COUNTEREXAMPLE'
  and counter['module_sha256']=='0e0e957ce1b47219a226a583b25a35b1156a01e2bd7b5b210417663729ba3a11'
  and counter['whole_cached_target_event_differs_from_fresh_file_but_navigation_still_admitted']is True
  and counter['restored_public_catalog_cache']is True
  and counter['production_or_private_bytes_changed']is False and counter['Qt_or_game_chat_Git_operations']is False,
  'actual original cached-source counterexample remains public and distinct')
 correction_path=base/'revision2/correction.json';correction=load(correction_path)
 require(correction['original_core_sha256']==counter['module_sha256']
  and correction['revised_core_sha256']==digest('rouge/battle_event_references.py')
  and correction['original25_test_method_AST_unchanged']is True
  and correction['source_manifest_data_builder_unchanged']is True
  and len(correction['new_methods'])==2,'two-line source consistency correction; original25 not overwritten')
 refs['counterexample']={'receipt':rel(counter_path),'sha256':digest(counter_path)}
 refs['correction']={'receipt':rel(correction_path),'sha256':digest(correction_path)}
 # This is source-build provenance only, never added as a test pass.
 source_process=base/'source-build-first/process.json';source=load(source_process)
 require(type(source['exit_code'])is int and source['exit_code']==0,'actual original pure-source build0')
 refs['source_build']={'receipt':rel(source_process),'sha256':digest(source_process),'not_product_validation':True}
 return refs



def prompt_assertion_correction(final_data):
 """Preserve the real first failure; admit only the proved new-test wording delta."""
 base='verification/sections/296-preparation/prompt-assertion-correction'
 correction_path=base+'/correction.json';correction=load(correction_path)
 original_path=base+'/original-test.py'
 test='tests/test_battle_entry_reference_view_296.py'
 before='8cff84555d701d470d0d2e0b4684a0627eed77082a659e744ce43118bc48673e'
 after='191d70d1fbd07d9ede4cdfed5ae2b27fb9a9d7a35ad0e45e1bf3df6e2f351929'
 require(correction['section']==296 and correction['kind']=='NEW_TEST_PROMPT_ASSERTION_CORRECTION'
  and correction['path']==test and correction['before_sha256']==before and correction['after_sha256']==after
  and correction['production_source_or_mechanism_or_data_changed']is False
  and correction['final_pass_not_claimed']is True and digest(original_path)==before and digest(test)==after,
  'canonical preserved new-test prompt correction, never a production or mechanism repair')
 old=path(original_path).read_text(encoding='utf8');current=path(test).read_text(encoding='utf8')
 old_assert="self.assertIn('请选择',self.panel.reference_text.toPlainText())"
 new_assert="self.assertIn('选择事件与完整选项',self.panel.reference_text.toPlainText());self.assertIn('不会自动跳转',self.panel.reference_text.toPlainText())"
 require(old.count(old_assert)==1 and ast.dump(ast.parse(old.replace(old_assert,new_assert,1)),include_attributes=False)
  ==ast.dump(ast.parse(current),include_attributes=False),
  'whole-module AST differs only by one prompt assertion replaced with two semantic checks')
 first_value=correction['first_actual_necessary_receipt']
 require(first_value=='verification/sections/296-necessary-first/process.json','canonical actual first necessary receipt')
 first=load(first_value);stderr=path(first_value).with_name('stderr.txt');log=path(stderr).read_text(encoding='utf8')
 stdout=path(first_value).with_name('stdout.txt')
 require(first['section']==296 and first['kind']=='necessary_change_related_tests_not_full_suite'
  and type(first['exit_code'])is int and first['exit_code']==correction['actual_first_exit']==1
  and first['source_unchanged']is True and first['source_sha256_before']==first['source_sha256_after']
  and first['modules']==final_data['modules']==MODULES and first['argv']==final_data['argv']
  and first['source_commit_before']==final_data['source_commit_before']==PARENT,
  'real first same-module run exit1 and stable original sources; not a current pass')
 counts=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',log)
 failures=re.findall(r'^FAIL: ([^\r\n]+)',log,re.M)
 require(len(counts)==1 and int(counts[0][0])==correction['actual_first_methods']
  and len(failures)==correction['actual_first_failures']==1
  and failures[0]=='test_all_eight_exact_versions_default_unselected_and_only_admit_matching_source_rows (tests.test_battle_entry_reference_view_296.BattleEntryReferenceView296Tests.test_all_eight_exact_versions_default_unselected_and_only_admit_matching_source_rows)'
  and log.rstrip().endswith('FAILED (failures=1)')and not re.search(r'^ERROR:',log,re.M)
  and "AssertionError: '请选择' not found"in log and '请在上方选择事件与完整选项'in log,
  'actual first132 one-failure raw trace is precisely the incorrect prompt expectation')
 old_map=first['source_sha256_after'];new_map=final_data['source_sha256_after']
 require(set(old_map)==set(new_map)and old_map[test]==before and new_map[test]==after
  and{k for k in old_map if old_map[k]!=new_map[k]}=={test},
  'between first failed and final necessary only this exact new-test source changed')
 promotion=load('verification/sections/296-preparation/promotion.json')
 require(promotion['promoted'][test]==before,'initial promotion SHA kept as historical original, not overwritten')
 return {'correction_receipt':correction_path,'correction_sha256':digest(correction_path),
  'original_test':original_path,'original_test_sha256':before,'final_test':test,'final_test_sha256':after,
  'first_actual_receipt':first_value,'first_receipt_sha256':digest(first_value),'first_actual_exit':1,
  'first_actual_methods':int(counts[0][0]),'first_actual_failures':len(failures),
  'first_stderr':rel(stderr),'first_stderr_sha256':digest(stderr),'first_stdout_sha256':digest(stdout),
  'whole_module_AST_only_the_declared_prompt_replacement':True,'production_models_data_native_unchanged':True,
  'initial_promotion_original_SHA_preserved':True,'first_failure_not_added_to_final_pass_count':True}



def intermediate_necessary():
 value='verification/sections/296-necessary-final/process.json';data=load(value)
 require(data['section']==296 and data['kind']=='necessary_change_related_tests_not_full_suite'
  and type(data['exit_code'])is int and data['exit_code']==0 and data['source_unchanged']is True
  and data['source_sha256_before']==data['source_sha256_after']and data['modules']==MODULES
  and data['source_commit_before']==PARENT,'actual post-prompt intermediate necessary0, not final reading repair')
 stderr=path(value).with_name('stderr.txt');log=path(stderr).read_text(encoding='utf8')
 rows=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',log)
 require(len(rows)==1 and int(rows[0][0])>0 and log.rstrip().endswith('OK')
  and not re.search(r'^(FAIL|ERROR):',log,re.M),'actual intermediate terminal OK and methods')
 return data,{'receipt':value,'sha256':digest(value),'actual_exit':0,'methods_run':int(rows[0][0]),
  'stderr':rel(stderr),'stderr_sha256':digest(stderr),'stdout_sha256':digest(path(value).with_name('stdout.txt')),
  'scope':'Post-prompt necessary before discovered reading-anchor gap; not final reading repair validation.'}


def reading_anchor_correction(final_data,intermediate,correction_value):
 require(rel(correction_value)=='verification/sections/296-preparation/reading-anchor-correction/correction.json'
  and digest(correction_value)=='6d9a190ac1fab071158d8948e9591f7de21d8848a2069a23d1aff84a557c6908',
  'exact actual public reading-gap correction receipt, not a prior-test failure')
 correction=load(correction_value)
 require(correction['section']==296
  and correction['kind']=='ACTUAL_ROOT_VISUAL_READING_GAP_CORRECTION_NOT_PRIOR_TEST_FAILURE'
  and correction['prior_native_status']=='narrow_scope_pass_not_final_reading_anchor_validation'
  and correction['accepted_final_necessary_or_native_run_by_this_script']is False
  and correction['full_suite_rerun']is False,'actual visual correction distinct from original narrow native pass')
 changed={'rouge/node_catalog_view.py','tests/test_battle_entry_integration_296.py',CANONICAL}
 old_map=intermediate['source_sha256_after'];new_map=final_data['source_sha256_after']
 require(set(old_map)==set(new_map)and{k for k in old_map if old_map[k]!=new_map[k]}==changed,
  'intermediate-to-final only the three authorized reading-anchor sources changed')
 require(final_data['argv']==intermediate['argv']and final_data['modules']==intermediate['modules']==MODULES
  and old_map['tests/test_battle_entry_reference_view_296.py']
  ==new_map['tests/test_battle_entry_reference_view_296.py']
  =='191d70d1fbd07d9ede4cdfed5ae2b27fb9a9d7a35ad0e45e1bf3df6e2f351929',
  'same ten modules and no second change to corrected prompt test')
 require(correction['before']=={k:old_map[k]for k in changed}
  and correction['after']=={k:new_map[k]for k in changed}
  and set(correction['before_archive'])==changed
  and correction['intermediate_necessary_receipt']=='verification/sections/296-necessary-final/process.json'
  and correction['intermediate_necessary_sha256']==digest(correction['intermediate_necessary_receipt']),
  'actual correction exact before/after maps and intermediate necessary binding')
 require(correction['after']=={
  'rouge/node_catalog_view.py':'c3c3b78b93a4d6511653c2e862aff9f40e90f0b04906e935043d1912c443795c',
  'tests/test_battle_entry_integration_296.py':'32c3367fba3a27db8360269ededb6603e01bdd9542fb563611fb533b87980f24',
  CANONICAL:'507df358f4f4ff210da930a3a9360df699a1cf0c8d6cb4ca802d3334c5a55e10'},
  'exact reviewed three-source reading-anchor repair, not a candidate-before value')
 originals={};directory=path(correction_value).parent
 for name in sorted(changed):
  relative=correction['before_archive'][name]
  require(type(relative)is str and Path(relative).name==relative,'safe original reading-source basename')
  matches=[directory/relative]
  require(digest(matches[0])==old_map[name],'original pre-reading source exact bytes preserved '+name)
  originals[name]={'before_sha256':old_map[name],'after_sha256':new_map[name],
   'original_files':[rel(p)for p in sorted(matches)]}
 # The historical successful native fixture had a narrower assertion set.
 # Keep its exact archive and actual success; do not reinterpret it as final.
 archive='verification/sections/296-window-attempt1';manifest_path=archive+'/archive-manifest.json'
 manifest=load(manifest_path)
 require(manifest['kind']=='296_EXACT_PUBLIC_NATIVE_ATTEMPT_OUTPUTS'and manifest['attempt']==1
  and manifest['original_actual_paths_preserved']is True and manifest['private_state_copied']is False,
  'original native attempt1 immutable public archive')
 for name,pin in manifest['files'].items():
  require(type(name)is str and not Path(name).is_absolute()and'..'not in Path(name).parts and'\\'not in name,
   'safe original archive member')
  member=archive+'/'+name
  require(digest(member)==pin['sha256']and path(member).stat().st_size==pin['bytes'],'every original native attempt1 member unchanged')
 process_path=archive+'/process.json';process=load(process_path)
 window_path=archive+'/actual/window.json';window=load(window_path)
 sup_path=archive+'/supervisor.json';sup=load(sup_path)
 require(correction['prior_native_receipt']==window_path
  and correction['prior_native_sha256']==digest(window_path)
  and correction['prior_native_unique_checks']==window['unique_checks']
  and correction['prior_native_repeated_assertions']==window['successful_assertion_executions_including_repeated_guards']
  and correction['visual_evidence']==archive+'/actual/window-exact-event-option-opened.png'
  and digest(correction['visual_evidence'])==correction['visual_evidence_sha256']
  ==manifest['files']['actual/window-exact-event-option-opened.png']['sha256'],
  'actual root visual gap evidence and prior narrow-scope counts bind the untouched original image/receipt')
 require(process['section']==296 and process['attempt']==1 and process['status']=='completed'
  and type(process['exit_code'])is int and process['exit_code']==0
  and type(process['child_primary_exit'])is int and process['child_primary_exit']==0
  and process['timed_out']is False and process['owned_job_no_live_execution_verified']is True
  and process['source_before_after_unchanged']is True
  and process['window_receipt_sha256']==digest(window_path),'native1 actual narrow-scope supervisor/child0 remains original')
 require(sup['status']=='completed'and sup['supervisor_exit']==sup['child_primary_exit']==0
  and sup['argv']==process['child_argv']and sup['timed_out']is False and sup['owned_handle_retained']is True
  and sup['owned_job_assigned']is True and sup['owned_job_no_live_execution_verified']is True,
  'native1 actual retained process and job closed; no natural-all-exit inference')
 require(window['section']==296 and window['kind']=='isolated_native_windows_fixed_battle_entry_references'
  and window['passed']is True and window['failure']is None and window['qpa']=='windows'
  and window['qt_exit_code']==0 and window['verification_window_closed']is True
  and window['source_sha256_before']==window['source_sha256_after']
  and digest(archive+'/execution-tools/window.py')==window['source_sha256_after'][CANONICAL],
  'native1 success bound to original frozen script and stable source map')
 historical_source_join=join_selected_native_sources(old_map,window['source_sha256_after'],
  'historical native1/intermediate source join')
 require(set(window['external_operation_attempts'])=={'game_enumeration','game_connect','game_capture','game_next_frame',
  'desktop_start','desktop_request','provider_chat','credential_read'}
  and all(type(n)is int and n==0 for n in window['external_operation_attempts'].values())
  and window['private_state_read_copied_or_restored']is False,'native1 no game/chat/private operations')
 require(window['unique_checks']==len(window['checks'])==len(set(window['checks']))
  and window['successful_assertion_executions_including_repeated_guards']>=window['unique_checks'],
  'native1 original actual counts retained without treating them as final')
 return {'correction_receipt':rel(correction_value),'correction_sha256':digest(correction_value),
  'exact_three_source_transition':originals,'prompt_test_191d_unchanged':True,
  'models_data_source_packets_and_other_production_bytes_unchanged':True,
  'historical_native_attempt1':{'process':process_path,'process_sha256':digest(process_path),
   'window':window_path,'window_sha256':digest(window_path),'archive_manifest':manifest_path,
   'archive_manifest_sha256':digest(manifest_path),'actual_supervisor_exit':0,'actual_child_exit':0,
   'actual_narrow_scope_pass':True,'final_reading_anchor_validation':False,
   'original_unique_checks':window['unique_checks'],
   'original_assertion_executions':window['successful_assertion_executions_including_repeated_guards'],
   'original_selected_sources':len(window['source_sha256_after']),'original_png_count':len(window['screenshots']),
   'source_join':historical_source_join},
  'first_reading_necessary_receipt':'verification/sections/296-necessary-reading-final/process.json',
  'final_native_requires_new_attempt2':True}



def failed_reading_necessary():
 value='verification/sections/296-necessary-reading-final/process.json';data=load(value)
 require(data['section']==296 and data['kind']=='necessary_change_related_tests_not_full_suite'
  and type(data['exit_code'])is int and data['exit_code']==1 and data['source_unchanged']is True
  and data['source_sha256_before']==data['source_sha256_after']and data['modules']==MODULES
  and data['source_commit_before']==PARENT,'actual first reading necessary1, not a final pass')
 stderr=path(value).with_name('stderr.txt');log=path(stderr).read_text(encoding='utf8')
 rows=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',log)
 failures=re.findall(r'^FAIL: ([^\r\n]+)',log,re.M)
 require(len(rows)==1 and int(rows[0][0])>0 and len(failures)==1
  and failures[0]=='test_all_eleven_real_entry_buttons_open_exact_scene_choice_without_resetting_battle (tests.test_battle_entry_integration_296.BattleEntryIntegration296Tests.test_all_eleven_real_entry_buttons_open_exact_scene_choice_without_resetting_battle)'
  and log.rstrip().endswith('FAILED (failures=1)')and not re.search(r'^ERROR:',log,re.M)
  and 'AssertionError: 367 not less than or equal to 342'in log,
  'preserved real viewport assertion failure, not an identity error or weakened visibility check')
 return data,{'receipt':value,'sha256':digest(value),'actual_exit':1,'methods_run':int(rows[0][0]),
  'actual_failures':len(failures),'stderr':rel(stderr),'stderr_sha256':digest(stderr),
  'stdout_sha256':digest(path(value).with_name('stdout.txt')),'not_added_to_final_pass_count':True}


def deferred_layout_correction(final_data,failed,correction_value):
 require(rel(correction_value)=='verification/sections/296-preparation/deferred-anchor-correction/correction.json'
  and digest(correction_value)=='077a281e91ec6c24806b552aab3d8617c63649c3be48fa35b4b7951dd7e3b7d7','exact actual deferred-layout correction receipt')
 correction=load(correction_value);name='rouge/node_catalog_view.py'
 before='c3c3b78b93a4d6511653c2e862aff9f40e90f0b04906e935043d1912c443795c'
 after='945bff0687761effcb156b94c502ea6dbb05d133a7c8971ad75b278269833a5c'
 require(correction['section']==296
  and correction['kind']=='ACTUAL_FAILED_VIEWPORT_TEST_DEFERRED_LAYOUT_CORRECTION'
  and correction['source']==name and correction['before_sha256']==before and correction['after_sha256']==after
  and correction['tests_loosened_or_modified']is False and correction['native_source_modified']is False
  and correction['accepted_final_run_by_this_script']is False
  and correction['prior_reading_source_chain']=='verification/sections/296-preparation/reading-anchor-correction/correction.json'
  and correction['final_required_necessary_directory']=='verification/sections/296-necessary-reading-retry2',
  'reader-scoped timer repair only; strict tests and native source unchanged')
 old_map=failed['source_sha256_after'];new_map=final_data['source_sha256_after']
 require(set(old_map)==set(new_map)and{k for k in old_map if old_map[k]!=new_map[k]}=={name}
  and old_map[name]==before and new_map[name]==after==digest(name)
  and failed['argv']==final_data['argv']and failed['modules']==final_data['modules']==MODULES,
  'reading failure-to-final only exact node reader timer source changed, not tests/native/models/data')
 original=path(correction_value).with_name('before-node_catalog_view.py')
 require(digest(original)==before,'real pre-deferred node source preserved')
 old=original.read_text(encoding='utf8');current=path(name).read_text(encoding='utf8')
 line='        reader.setTextCursor(choice_cursor);reader.ensureCursorVisible()\n'
 replacement=line+(
  '        # The parent app changes its outer tab after this method returns.\n'
  '        # Re-check after that layout settles, using the reader as timer context.\n'
  '        from PySide6.QtCore import QTimer\n'
  '        QTimer.singleShot(0,reader,reader.ensureCursorVisible)\n')
 require(old.count(line)==1 and ast.dump(ast.parse(old.replace(line,replacement,1)),include_attributes=False)
  ==ast.dump(ast.parse(current),include_attributes=False),
  'whole production module AST only adds the reader-context zero-delay ensure-visible call')
 failed_value='verification/sections/296-necessary-reading-final/process.json'
 require(correction['failed_receipt']==failed_value
  and correction['failed_receipt_sha256']==digest(failed_value)
  and correction['failed_stderr_sha256']==digest(path(failed_value).with_name('stderr.txt')),
  'actual failed viewport receipt and raw assertion trace bind correction')
 return {'correction_receipt':rel(correction_value),'correction_sha256':digest(correction_value),
  'before_source':rel(original),'before_source_sha256':before,'final_source':name,'final_source_sha256':after,
  'whole_module_AST_only_reader_context_zero_timer_added':True,'tests_or_native_assertions_modified':False,
  'models_data_qualification_and_other_sources_changed':False,
  'final_necessary_receipt':'verification/sections/296-necessary-reading-retry2/process.json',
  'prior_viewport_failure_not_added_to_final_pass_count':True}


def feature_sources(promotion_value,tests):
 """The promotion record is provenance; final test maps bind later repairs."""
 record=load(promotion_value)
 require(record['section']==296 and type(record['promoted'])is dict
  and set(record['existing_production_changes'])==CHANGED_EXISTING,'actual root promotion and four old integrations')
 expected=set(CHANGED_EXISTING)|{CANONICAL,'rouge/battle_entry_reference_view.py',
  'rouge/battle_event_references.py','rouge/stage_entry_reference.py',
  'rouge/data/battle-event-references.json','rouge/data/stage-entry-configuration-reference.json',
  'scripts/build_battle_event_references_296.py','scripts/build_stage_entry_configuration_296.py',
  *('tests/'+m.split('.')[-1]+'.py'for m in MODULES[:4])}
 for packet_name in PACKETS:
  expected|={p.relative_to(ROOT).as_posix()for p in(ROOT/packet_name).rglob('*')if p.is_file()}
 require(set(record['promoted'])==expected,'exact final combined source scope, not a prefilled count')
 actual={name:digest(name)for name in sorted(expected)}
 require(all(tests['source_sha256_after'].get(name)==value for name,value in actual.items()),
  'every combined feature source bound by actual final necessary producer')
 require(all(type(value)is str and re.fullmatch('[0-9a-f]{64}',value)is not None
  for value in record['promoted'].values()),'original promotion provenance hashes')
 return actual,{'receipt':rel(promotion_value),'sha256':digest(promotion_value),
  'actual_promoted_paths':len(expected),'final_source_map_from_necessary':True,
  'later_revisions_after_initial_promotion':{name:{'original_promotion_sha256':record['promoted'][name],
   'final_tested_sha256':actual[name]}for name in actual if actual[name]!=record['promoted'][name]}}


def main(args):
 require(Path(__file__).resolve()==(HERE/'close_section_296.py').resolve(),'reviewed canonical cache helper')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 require(branch=='codex/p2-development'and parent==PARENT
  and not(ROOT/'verification/sections/296.json').exists(),'authorized branch/parent/exclusive section receipt')
 reverse,source=packet();tests,test_ref=necessary(args.necessary_receipt,parent)
 feature_map,promoted=feature_sources(args.promotion_receipt,tests)
 preparation=preparation_evidence(args.reverse_evidence_directory)
 require(rel(args.necessary_receipt)=='verification/sections/296-necessary-reading-retry2/process.json',
  'actual final deferred-reading necessary retry, never earlier failed or narrower run')
 intermediate,intermediate_ref=intermediate_necessary()
 prompt_repair=prompt_assertion_correction(intermediate)
 failed_reading,failed_reading_ref=failed_reading_necessary()
 reading_repair=reading_anchor_correction(failed_reading,intermediate,args.reading_anchor_correction)
 deferred_repair=deferred_layout_correction(tests,failed_reading,args.deferred_anchor_correction)
 require(rel(args.window_process_receipt)=='verification/sections/296-window-attempt2/process.json'
  and rel(args.window_receipt)=='verification/sections/296-window-attempt2/actual/window.json',
  'new actual attempt2 final native receipts, not successful narrower attempt1')
 window,window_ref=native(args.window_receipt,args.window_process_receipt,tests,args.native_source_sha256,reverse)
 window_ref['root_visual_review']=visual_review(args.window_receipt,window)
 main_ref=original_window(args.main_window_receipt,args.focus_receipt,window,tests,args.necessary_receipt,args.window_receipt)
 full=load(FULL)
 require(digest(FULL)==FULL_SHA and full['after_section']==290 and full['available_checks_passed']is True
  and full['scope_not_reduced']is True and full['complete_repository_validation']is False and full['P2_complete']is False,
  'historical290 full remains its original source, no new296 full claim')
 cp=load('DEVELOPMENT_CHECKPOINT.json')
 require(cp['completed_sections']==cp['latest_functional_section']==295 and cp['next_section']==296
  and cp['active_section']['section']==296 and cp['policy']['priority_order']==['P3','P2','P1']
  and cp['policy']['current_user_batch_target_section']is None and cp['policy']['stop_after_section']is None,
  'real295 to active296/P3 first/no numeric endpoint')
 require(cp['last_full_validation']['after_section']==290 and cp['current_available_full_validation']['section']==290
  and cp['policy']['full_validation_interval']==15 and cp['policy']['full_validation_anchor_section']==125
  and 125+((296-125)//15+1)*15==305,'actual cadence290/next305')
 prior=cp['last_verified_cloud_save'];proof=load(prior['proof'])
 require(prior['section']==295 and digest(prior['proof'])==prior['proof_sha256']and proof['passed']is True
  and proof['commit']==proof['remote_HEAD']==prior['commit']and proof['push_primary_exit']==0,
  'actual preceding295 ordinary publication')
 doc_names=('DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','AGENTS.md')
 docs={name:path(name).read_bytes()for name in doc_names}
 progress=path('PROJECT_PROGRESS.md').read_bytes()
 require(sha256(progress).hexdigest()==PROGRESS_SHA_BEFORE
  and all(text in progress.decode()for text in('其中10图/18关已有58格直接参考','81个关卡、59张独立原图',
   '游戏内实际展示','10条未解析附注','15个事件/特殊关卡','25个未绑定来源原场景、57个原选项')),
  'all existing remaining gaps kept; reference reading is not actual game entry or display')
 now=datetime.now(timezone(timedelta(hours=8))).isoformat()
 capability=('从8个精确固定作战反查资料中对应的事件、完整场景和选项；11条资料入口手动打开，'
  '另列3条被明确紧急条件排除的普通版本，并将正文定位高亮到实际场景中的具体选项。无效验尸单列4条配置与光明之末文献说明，'
  '第3、4、5层普通作战和假层保持区别。默认不选择；保留战斗页阅读与地图选点，'
  '来源失效清除旧入口和内容，恢复后不自动重选。')
 limits=['事件主层仅说明该事件资料，不作为关卡全局层数；15项全局层数缺口和25/57原入口不减少。',
  '无效验尸4条配置及21个完整原对象不证明FEATURE获取、附着、执行、实际资格、节点、进入或数量；假层不推主层或秘境。',
  '来源解析缓存必须每次鲜检原字节，并核已有前向缓存；原25项、真实反例和修后27项分别保留，不与本次必要数相加。',
  '固定资料入口手动阅读不等于游戏内按钮、当前服务器、实际选择、移动、作战或领取。',
  '旧17条typed奖励、10/18/58部分地格参考、81/59整图缺口、资格引擎和私人本局状态不变。',
  '本节只必要检查与真实隔离Windows新流程；沿用290全量原来源，下次305，不冒称296源码已全量。',
  'P3/P2/P1仍未完成，识别最后；无数字终点，不推荐、排序或自动选路，不操作游戏、聊天或私人状态。']
 receipt={'section':296,'kind':'functional_section','title':TITLE,'at_Beijing':now,'branch':branch,'prior_commit':parent,
  'remaining_item':'P3固定战斗对应节点/事件入口及条件资料','new_capability':capability,
  'files':sorted(feature_map),'source_sha256':feature_map,'source_reference':source,'source_promotion':promoted,
  'preserved_cache_counterexample_and_correction':preparation,
  'preserved_first_necessary_failure_and_prompt_correction':prompt_repair,
  'intermediate_post_prompt_necessary_not_final_reading':intermediate_ref,
  'preserved_reading_anchor_repair_and_narrow_native1':reading_repair,
  'preserved_viewport_failure_before_deferred_repair':failed_reading_ref,
  'preserved_deferred_layout_repair':deferred_repair,
  'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),
  'existing_engine_or_typed_reward_qualification_or_run_state_changed':False,
  'typed_named_grant_count_unchanged':17,'original_entry_gaps_unchanged':[25,57],
  'remaining_global_stage_floor_gaps_unchanged':15,'partial_direct_reference_scope_unchanged':[10,18,58],
  'whole_map_gaps_unchanged':[81,59],'necessary_validation':test_ref,
  'native_windows_validation':{**window_ref,'original_project_window':main_ref},
  'full_validation':{'receipt':FULL,'sha256':FULL_SHA,'after_section':290,'full_suite_rerun':False,
   'new296_source_full_validation_claimed':False,'scope_not_reduced':True,'next_periodic_section':305,
   'complete_repository_validation':False},'PROJECT_PROGRESS_unchanged_sha256':PROGRESS_SHA_BEFORE,
  'limits':limits,'next_section':297,'cloud_publication_binding':'enclosing_commit','cloud_published':False,
  'P3_complete':False,'P2_complete':False}
 history='historical_before296_current_pointers';require(history not in cp,'exclusive old pointers')
 cp[history]={key:deepcopy(cp[key])for key in('current_section_save','current_section_validation','latest_section_environment',
  'active_section','current_batch','cloud_publication_closeout')if key in cp}
 cp.pop('active_section',None);cp.pop('cloud_publication_closeout',None)
 cp.update(completed_sections=296,latest_functional_section=296,next_section=297,
  batch_status='P3_SECTION296_VALIDATED_AWAITING_PUBLICATION',next_full_validation_after=305,
  next_action='从297继续有证P3剩余事项，无数字终点；下次完整可用全量305。')
 cp['policy']['next_full_validation_after']=305;cp['current_batch_commit_policy']['next_full_validation_after']=305
 cp['current_batch'].update(status=cp['batch_status'],next_section=297,next_section_started=False,
  receipt='verification/sections/296.json',next_full_validation_after=305,batch_closed=False)
 cp['confirmed_next_stage_direction'].update(last_completed_functional_section=296,next_functional_section_started=False)
 cp['sections'].append({'number':296,'completion_ref':'p3-section-296','topic':TITLE,'verification':'verification/sections/296.json'})
 cp['current_section_save']={'section':296,'verification':'verification/sections/296.json','scope':'current_functional_section',
  'binding':'enclosing_commit','commit_reference':'commit containing296 combined documented entry reader/source, actual validation, requirements and index'}
 cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_section_validation']={'section':296,'receipt':'verification/sections/296.json',
  'necessary_methods_passed':test_ref['methods_run'],'native_isolated_window_checks':window['unique_checks'],
  'full_suite_rerun':False,'last_full_receipt':FULL,'full_source_is_historical290':True}
 cp['latest_section_environment']={'section':296,'receipt':'verification/sections/296.json',
  'native_windows':f"{test_ref['methods_run']} actual necessary; {window['unique_checks']} unique native; real MainWindow/entry reader/{window_ref['screenshots']} representative PNG; original visible/private5 unchanged",
  'native_game_or_chat_verified':False,'new_Linux_Wine_full_run':False,'current_section_full_rerun':False,'last_full_receipt':FULL}
 cp['functional_sections_since_latest_requirement']=list(dict.fromkeys([*cp['functional_sections_since_latest_requirement'],296]))
 completed=(f'## 功能第296节 · {TITLE}\n\n{now}。{capability}\n\n'
  f"实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过；"
  f"{window_ref['screenshots']}张代表性PNG已由根代理逐图查看，实际覆盖11条手动入口和3条排除，"
  '无效验尸配置与事件分列，原项目窗口更新/私人5路径不变。'
  '原缓存25项、真实反例与修后27项分别留存，不相加；不销15项全局层数、25/57原入口或其它待办，PROJECT_PROGRESS原字节保留。'
  '来源及实际回执verification/sections/296.json；290全量沿用原来源，下次305、后续297，无数字终点。待普通推送核对。\n\n')
 mutations={'verification/sections/296.json':encode(receipt),'DEVELOPMENT_CHECKPOINT.json':encode(cp),
  'PROJECT_COMPLETED.md':completed.encode()+docs['PROJECT_COMPLETED.md']}
 wip=docs['WORK_IN_PROGRESS.md'].decode();require('## 功能第295节'in wip,'preserve295 onward history')
 mutations['WORK_IN_PROGRESS.md']=(completed+wip[wip.index('## 功能第295节'):]).encode()
 req=docs['PROJECT_REQUIREMENTS.md'].decode();a,b=req.index('<!-- current-delivery:start -->'),req.index('<!-- current-delivery:end -->')
 block=('<!-- current-delivery:start -->\n## 当前交付与续接 · 第296节\n\n2026-10-16继续P3，无数字终点。'+capability
  +f"实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过，原窗口更新/私人5路径不变。"
  +'资料入口和配置不放宽原资格、全局层数或本局实际结果；15/25/57缺口及17条typed奖励、10/18/58参考与81/59整图待办不变。'
  +'290全量沿用原来源，下次305；P3→P2→P1、识别最后，不提供路线建议。待普通推送核对，源码/要求/回执/索引同提交。\n')
 mutations['PROJECT_REQUIREMENTS.md']=(req[:a]+block+req[b:]).encode()
 agents=docs['AGENTS.md'].decode();a,b=agents.index('## 当前续接 · 第295节'),agents.index('## 当前优先顺序与输出可读性')
 mutations['AGENTS.md']=(agents[:a]+'## 当前续接 · 第296节已完成功能与必要/原生验收\n\n'+capability
  +'来源及实际回执verification/sections/296.json；原资格、15项全局层数和25/57入口不变，实际进入/作战/领取仍未知。'
  +'原项目窗口更新/私人5路径不变；未跑296全量，290完整可用范围沿用原来源。下一节297/下次305，无数字终点。'
  +'P3→P2→P1、识别最后，不推荐/排序/自动选路。本节待普通推送并核对真实远端，源码/要求/验收/索引同提交。\n\n'+agents[b:]).encode()
 require('初次招募时即处于已进阶状态'in mutations['PROJECT_REQUIREMENTS.md'].decode()
  and'初次招募即处于已进阶状态'in mutations['AGENTS.md'].decode(),'keep verified recruitment terminology')
 require(all(str(i)+'.'in mutations['AGENTS.md'].decode().split('## 当前续接')[0]for i in range(1,6)),
  'keep highest-priority five independent-judgment requirements')
 archive=ROOT/'verification/sections/296-preparation/closeout-tools';require(not archive.exists(),'exclusive closeout tool archive')
 copies={'close_section_296.py':path(HERE/'close_section_296.py').read_bytes(),'CONTRACT.md':path(HERE/'CONTRACT.md').read_bytes()}
 copies.update({'before-'+name:raw for name,raw in docs.items()})
 manifest={'kind':'SECTION296_PUBLIC_CLOSEOUT_TOOLS_NOT_PRIVATE_STATE',
  'files':{name:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}for name,raw in copies.items()},
  'private_contents_or_hash_lists_copied':False,'tests_Qt_GUI_game_chat_Git_publish_or_full_executed_by_helper':False}
 print(json.dumps({'gates_passed':True,'apply_requested':args.apply,
  'necessary_actual_methods':test_ref['methods_run'],'native_actual_unique_checks':window['unique_checks'],
  'native_selected_source_files':len(selected_window_sources()),'combined_feature_source_paths':len(feature_map),
  'source_join':window_ref['source_join'],
  'planned_public_files':list(mutations),'PROJECT_PROGRESS_modified':False,'full_rerun':False,
  'next_full_section':305,'numeric_endpoint':None,'cloud_published':False},ensure_ascii=False))
 if not args.apply:return
 for name,raw in docs.items():require(path(name).read_bytes()==raw,'public document unchanged before apply '+name)
 require(path('PROJECT_PROGRESS.md').read_bytes()==progress,'todo bytes unchanged before apply')
 check_map(tests['source_sha256_after'],'final pre-write necessary')
 check_map({NATIVE_ONLY_DOCUMENT:NATIVE_ONLY_DOCUMENT_SHA},'final pre-write additional native-only source')
 archive.mkdir(parents=True)
 for name,raw in copies.items():
  with(archive/name).open('xb')as stream:stream.write(raw)
 with(archive/'archive-manifest.json').open('xb')as stream:stream.write(encode(manifest))
 for name,raw in mutations.items():
  destination=ROOT/name;destination.parent.mkdir(parents=True,exist_ok=True)
  with destination.open('xb'if name=='verification/sections/296.json'else'wb')as stream:stream.write(raw)
 print(json.dumps({'section':296,'local_closeout_written':True,'cloud_published':False,'next_section':297,'next_full_section':305}))


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--necessary-receipt',required=True);parser.add_argument('--window-receipt',required=True)
 parser.add_argument('--window-process-receipt',required=True)
 parser.add_argument('--native-source-sha256',required=True)
 parser.add_argument('--deferred-anchor-correction',default='verification/sections/296-preparation/deferred-anchor-correction/correction.json')
 parser.add_argument('--reading-anchor-correction',default='verification/sections/296-preparation/reading-anchor-correction/correction.json')
 parser.add_argument('--promotion-receipt',default='verification/sections/296-preparation/promotion.json')
 parser.add_argument('--reverse-evidence-directory',default='verification/sections/296-preparation/reverse')
 parser.add_argument('--main-window-receipt',default='verification/sections/296-main-window.json')
 parser.add_argument('--focus-receipt',default='verification/sections/296-main-window-focus.json')
 parser.add_argument('--apply',action='store_true');main(parser.parse_args())
