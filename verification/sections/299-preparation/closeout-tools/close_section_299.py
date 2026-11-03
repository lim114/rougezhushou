"""Strict299 cache preparation. Preview by default; root-only --apply.
No Qt/tests, game/chat/private operations or Git mutation. Reads actual public receipts.
"""
import argparse,ast,runpy
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,re,struct,subprocess
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
HERE=ROOT/'.cache/p3-299-closeout/revision2'
PARENT='b56cbf352cf5d171f52ba05839312950df462e8c'
TITLE='完整候选组与关联条目的手动阅读和独立固定预览'
CANONICAL='scripts/verify_spawn_candidates_window_299.py'
PACKET='research/p3-spawn-candidates-299';MANIFEST=PACKET+'/source-manifest.json';DATA='rouge/data/spawn-candidates.json'
MANIFEST_SHA='7cba1db922459fea7eddd86a12ad37998bf93e5616ac63e46aa83fc6b6fab08c'
DATA_SHA='aaef1b86a73613ce833a4a5fe2ce39abb6241c0dcc2457fcc00a5b51fd61fbd2'
BUILDER='scripts/build_spawn_candidates_299.py'
FULL='verification/full-290/summary.json';FULL_SHA='2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
CHANGED_EXISTING={'rouge/battle_view.py','rouge/battle_event_references.py'}
MODULES=['tests.test_spawn_candidates_299','tests.test_spawn_candidates_view_299','tests.test_spawn_candidates_integration_299',
 'tests.test_battle_planning_161_170','tests.test_battle_preview_039','tests.test_player_battle_information_286',
 'tests.test_player_information_view_286','tests.test_battle_entry_integration_296','tests.test_event_preview_filters_292',
 'tests.test_battle_event_references_296','tests.test_battle_entry_compatibility_299']
PROGRESS_SHA_BEFORE='111962b1622515c494ae81a06ac19b915db797211e926165a9947b80fade8a0b'


def require(value,message):
 if value is not True:raise ValueError('299 closeout prerequisite: '+message)


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
 require(process['section']==299 and process['kind']=='actual_native_window_owned_process_execution'
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
 require(path(main_value).resolve()==(ROOT/'verification/sections/299-main-window.json').resolve()
  and path(focus_value).resolve()==(ROOT/'verification/sections/299-main-window-focus.json').resolve(),
  'strict same-section canonical299 main/focus receipt paths')
 require(main['section']==299 and focus['section']==299
  and main['necessary_receipt_sha256']==digest(necessary_value)
  and main['native_receipt_sha256']==digest(native_value)
  and main['native_receipt']==rel(native_value) and main['necessary_receipt']==rel(necessary_value)
  and focus['main_receipt_sha256']==digest(main_value),
  'actual299 main binds both final evidence receipts; focus binds exact same main bytes')
 require(main['source_sha256_before']==main['source_sha256_after']==fixture['source_sha256_after']
  and set(main['source_sha256_after'])==selected_window_sources(),
  'same final actual native_selected source map stable through original window restart')
 check_map(main['source_sha256_after'],'original299 window final native_selected sources')
 timestamps={name:datetime.fromisoformat(value.replace('Z','+00:00')) for name,value in {
  'started':main['started_utc'],'finished':main['finished_utc'],'focus':focus['at_utc'],
  'necessary_finished':necessary_data['finished_utc'],'native_finished':fixture['finished_at']}.items()}
 require(all(value.tzinfo is not None and value.utcoffset() is not None for value in timestamps.values()),
  'actual main/focus/final-check timestamps are timezone-aware')
 require(timestamps['started']>timestamps['necessary_finished'] and timestamps['started']>timestamps['native_finished']
  and timestamps['finished']>=timestamps['started'] and timestamps['focus']>=timestamps['finished'],
  'original299 restart occurs after both final validations; focus follows completed main receipt')
 require(main['passed'] is True and main['private_file_hash_comparison_count']==5 and main['private_hashes_equal'] is True
  and main['changed_private_paths']==[] and main['private_contents_parsed_copied_or_restored'] is False and main['no_private_restoration'] is True,
  'actual original-window update/private5 hash unchanged, no content parsing/copy/restore')
 require(len(main['visible_windows'])==1,'one visible original project window');visible=main['visible_windows'][0]
 require(visible['visible'] is True and visible['responding'] is True and visible['minimized'] is False and visible['hwnd']>0
  and visible['pid']!=fixture['process_id'],'original window responsive/visible and not fixture')
 require(focus['visible'] is True and focus['pid']==visible['pid'] and focus['hwnd']==focus['actual_foreground']==visible['hwnd'],
  'actual foreground original project window')
 return {'receipt':rel(main_value),'sha256':digest(main_value),'focus_receipt':rel(focus_value),'focus_sha256':digest(focus_value),
  'section':299,'necessary_receipt_sha256':digest(necessary_value),'native_receipt_sha256':digest(native_value),
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
 name='verification/sections/299-preparation/root-visual-review.json';review=load(name)
 require(review['section']==299 and review['kind']=='root_archived_native_images_review'
  and review['actual_images_opened_with_view_image']is True,'root actually reviewed new299 images')
 expected={rel(path(value).with_name(Path(row['path']).name)):row['sha256']for row in window['screenshots']}
 require(review['images']==expected and review['actual_image_count']==len(expected),'root visual review exact all actual images')
 return{'receipt':name,'sha256':digest(name),'actual_root_reviewed_images':len(expected),'helper_performed_visual_review':False}


def selected_window_sources():
 # The already-reviewed canonical script has no product/Qt import at module scope.
 # Its explicit public-byte bound_files() is the actual producer, not guessed counts.
 result=runpy.run_path(str(path(CANONICAL)))['bound_files']()
 check_map(result,'canonical selected public source producer')
 return set(result)

def packet():
 require(digest(MANIFEST)==MANIFEST_SHA and digest(DATA)==DATA_SHA,'fixed299 public authority/data bytes')
 manifest=load(MANIFEST);data=load(DATA)
 require(manifest['schema']=='spawn_candidates_source_manifest_v1'and manifest['data_file']==DATA
  and manifest['data_sha256']==DATA_SHA and manifest['runtime_reads_primary_character_table']is False,
  'fresh fixed source authority, no private/current-server input')
 for name,pin in manifest['files'].items():
  check_map({name:pin['sha256']},'fresh299 source member');require(path(name).stat().st_size==pin['bytes'],'member exact byte length')
 stages=data['stages'];level_files={s['original_level_file']for s in stages.values()}
 counts={'stages':len(stages),'original_levels':len(level_files),
  'groups':sum(len(s['groups'])for s in stages.values()),'packages':sum(len(s['packages'])for s in stages.values())}
 require(data['reference_kind']=='fixed_main_queue_group_and_package_membership'and counts==data['counts']
  and counts=={'stages':69,'original_levels':38,'groups':285,'packages':215},'complete fixed main-source group/package inventory, not actual enemy totals')
 for sid,stage in stages.items():
  require(stage['stage_id']==sid and manifest['stage_files'][sid]==stage['original_level_file']
   and digest(stage['original_level_file'])==stage['original_level']['sha256'],'each stage exact original level identity')
 require(data['battle_source']['file']=='rouge/data/battle-previews.json'
  and digest(data['battle_source']['file'])==data['battle_source']['sha256'],'full fixed battle source bound, no branch borrowing')
 return{'manifest':MANIFEST,'manifest_sha256':MANIFEST_SHA,'data':DATA,'data_sha256':DATA_SHA,
  'source_members':len(manifest['files']),'fixed_source_inventory':counts,'inventory_is_actual_enemy_or_selection_count':False,
  'probabilities_or_simultaneous_spawn_inferred':False,'current_server_or_live_battle_verified':False}

def necessary(value):
 data=load(value)
 require(data['section']==299 and data['kind']=='necessary_change_related_tests_not_full_suite'
  and type(data['exit_code'])is int and data['exit_code']==0 and data.get('timed_out',False)is False
  and data['source_unchanged']is True and data['source_sha256_before']==data['source_sha256_after'],
  'actual final necessary0/stable, no timeout')
 require(data['modules']==MODULES and data['argv'][1:7]==['-B','-X','utf8','-m','unittest','-v']
  and data['argv'][-len(MODULES):]==MODULES and data['source_commit_before']==PARENT,'actual complete eleven modules and exact parent')
 require(data['game_sampling_verified']is False and data['chat_verified']is False
  and data['full_scope_reduced']is False and data['full_suite_rerun']is False,'necessary only; no full/game/chat claim')
 minimum={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/**/*.py')}
 minimum|={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/data/*.json')}
 minimum|={'tests/'+m.split('.')[-1]+'.py'for m in MODULES}|selected_window_sources()|{BUILDER}
 minimum|={p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-battle-entry-compatibility-299').rglob('*')if p.is_file()}
 for authority in('research/p3-battle-entry-compatibility-299/source-manifest.json','research/p3-battle-event-references-296/source-manifest.json'):
  minimum.add(authority);minimum.update(load(authority)['files'])
 minimum.update(('verification/sections/298-preparation/before/rouge/event_planning.py',
  'verification/sections/298-preparation/before/rouge/node_catalog.py',
  'verification/sections/299-preparation/before/rouge/battle_event_references.py'))
 require(minimum<=set(data['source_sha256_after']),'actual necessary source map covers complete selected native/public closure')
 check_map(data['source_sha256_after'],'final299 necessary')
 prior=load('verification/sections/298.json')['necessary_validation']
 require(digest(prior['receipt'])==prior['sha256'],'exact previous298 actual necessary receipt')
 old=load(prior['receipt']);kept={n:v for n,v in old['source_sha256_after'].items()if n.startswith('rouge/')
  and n not in CHANGED_EXISTING and(n.endswith('.py')or(n.startswith('rouge/data/')and n.endswith('.json')))}
 require(bool(kept)and all(data['source_sha256_after'].get(n)==v for n,v in kept.items()),'all old product Python/staticJSON except battle_view and declared source-binding controller unchanged')
 tracked_tests=set(subprocess.check_output(['git','ls-tree','-r','--name-only',PARENT,'--','tests'],cwd=ROOT,text=True).splitlines())
 changed_tests=set(subprocess.check_output(['git','diff','HEAD','--name-only','--','tests'],cwd=ROOT,text=True).splitlines())
 require(not(tracked_tests&changed_tests),'no old tracked tests changed or silently migrated')
 log=path(value).with_name('stderr.txt');text=log.read_text(encoding='utf8');counts=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',text)
 require(len(counts)==1 and int(counts[0][0])>0 and text.rstrip().endswith('OK')and not re.search(r'^(FAIL|ERROR):',text,re.M),
  'actual original terminal Ran/OK; counts never prepared')
 return data,{'receipt':rel(value),'sha256':digest(value),'stderr':rel(log),'stderr_sha256':digest(log),
  'stdout_sha256':digest(path(value).with_name('stdout.txt')),'actual_exit':0,'methods_run':int(counts[0][0]),'seconds':float(counts[0][1]),
  'source_files':len(data['source_sha256_after']),'source_unchanged':True,'modules':MODULES,
  'unchanged_existing_product_Python_static_JSON_files':len(kept),'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),
  'old_tracked_test_maintenance':False,'author_preparation_checks_are_subsets_not_added':True}

def compatibility_repair(tests):
 name='verification/sections/299-preparation/entry-binding-repair.json';record=load(name)
 old_manifest='research/p3-battle-event-references-296/source-manifest.json'
 new_manifest='research/p3-battle-entry-compatibility-299/source-manifest.json'
 controller='rouge/battle_event_references.py'
 require(record['section']==299 and record['kind']=='source_compatibility_repair_in_functional_section'
  and record['first_necessary_receipt']=='verification/sections/299-necessary-first/process.json'
  and record['old_manifest']==old_manifest and record['new_manifest']==new_manifest
  and record['new_controller']==controller and record['only_controller_MANIFEST_and_MANIFEST_SHA_assignments_changed']is True
  and record['data_or_game_mechanics_changed']is False and record['all_existing_tests_preserved']is True,
  'explicit source-only compatibility repair; no assertion or mechanism weakening')
 require(digest(old_manifest)==record['old_manifest_sha256']=='c6a7d1294e48b6fec896f736d56baa0c09f25f3365de471cc11c88d74705de21'
  and digest(new_manifest)==record['new_manifest_sha256']=='26fadacc46fcd890aef672509db414ca3fad1a407b5affc06a18753f45427a3c',
  'historical296 authority retained; new current authority exact bytes')
 old=load(old_manifest);new=load(new_manifest);bindings=record['changed_source_bindings']
 require(set(bindings)=={'rouge/event_planning.py','rouge/node_catalog.py'}and set(old['files'])==set(new['files']),
  'same complete source member set; exactly two current code bindings')
 changed={n for n in old['files']if old['files'][n]!=new['files'][n]}
 require(changed==set(bindings),'only two code member pins change; no data/document/14-edge change')
 for n,pin in new['files'].items():
  check_map({n:pin['sha256']},'compatibility current complete source')
  require(path(n).stat().st_size==pin['bytes'],'compatibility current exact source length')
  if n in bindings:
   row=bindings[n];require(row['old']==old['files'][n]and row['current']==pin
    and digest(row['historical_original'])==row['old']['sha256']
    and path(row['historical_original']).stat().st_size==row['old']['bytes'],
    'old/current two code identities independently retained')
 original=record['old_controller'];require(digest(original)==record['old_controller_sha256']=='ab6149db963dfed0d47083fc725c49d4df6c731e357d70f225f6473cdd540add'
  and digest(controller)==record['new_controller_sha256']=='25760d4c5b613bc587c6c46fc8004baa977c2d7f21b916f71d7e2bc369c7e3e5',
  'actual old and repaired controller source bytes')
 old_tree=ast.parse(path(original).read_text(encoding='utf8'));new_tree=ast.parse(path(controller).read_text(encoding='utf8'))
 before_assign={n.targets[0].id:n for n in old_tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
 after_assign={n.targets[0].id:n for n in new_tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
 require(after_assign['MANIFEST'].value.value==new_manifest and after_assign['MANIFEST_SHA256'].value.value==digest(new_manifest),
  'controller references precisely new complete authority')
 for key in('MANIFEST','MANIFEST_SHA256'):before_assign[key].value=deepcopy(after_assign[key].value)
 require(ast.dump(old_tree,include_attributes=False)==ast.dump(new_tree,include_attributes=False),
  'all controller AST except two declared constants identical, strict source/identity guards remain')
 first_value=record['first_necessary_receipt'];first=load(first_value);logpath=path(first_value).with_name('stderr.txt');log=logpath.read_text(encoding='utf8')
 require(first['section']==299 and first['kind']=='necessary_change_related_tests_not_full_suite'
  and first['exit_code']==1 and first.get('timed_out',False)is False and first['source_unchanged']is True
  and first['source_sha256_before']==first['source_sha256_after']and first['modules']==MODULES[:-2]
  and first['source_commit_before']==PARENT,'actual original stable nine-module nonpass retained')
 ran=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',log)
 failures=re.findall(r'^FAIL: (.+)$',log,re.M);errors=re.findall(r'^ERROR: (.+)$',log,re.M)
 require(len(ran)==1 and int(ran[0][0])==record['actual_first_methods']==135
  and len(failures)==record['actual_first_failures']==1 and len(errors)==record['actual_first_errors']==5
  and log.rstrip().endswith('FAILED (failures=1, errors=5)'),
  'first actual135/1F5E raw terminal records are not added to final passes')
 require(failures==['test_existing_entry_reader_map_and_reward_interfaces_survive_candidate_navigation (tests.test_spawn_candidates_integration_299.SpawnCandidatesParentIntegration299Tests.test_existing_entry_reader_map_and_reward_interfaces_survive_candidate_navigation)']
  and all('(tests.test_battle_entry_integration_296.BattleEntryIntegration296Tests.'in row for row in errors),
  'six concrete first-run failed identities preserved rather than inferred from progress')
 common=set(first['source_sha256_after'])&set(tests['source_sha256_after'])
 delta={n for n in common if first['source_sha256_after'][n]!=tests['source_sha256_after'][n]}
 require(delta=={CANONICAL,controller}and first['source_sha256_after'][controller]==record['old_controller_sha256']
  and tests['source_sha256_after'][controller]==record['new_controller_sha256'],
  'between actual first and final existing sources only declared controller and native selected-set binding change')
 # Native provenance is separately linked by final repaired promotion. The original
 # source hash is authoritative even if root stores that exact source elsewhere.
 require(first['source_sha256_after'][CANONICAL]=='8a359acb41c7c8d963f6ebc2a304ae58c9cc415234d80608c055947c4b1f17c7'
  and tests['source_sha256_after'][CANONICAL]=='4a3b71df8119eae543388e3fbe8f3221efa42fb762451be52f044f8c14e75d4d',
  'actual original native and only-bound-source revision3 identities')
 data=load('rouge/data/battle-event-references.json')
 require(data['counts']=={'raw_edges':14,'admitted_edges':11,'explicit_exclusions':3,'events':5,'choices':8,'stage_ids':8},
  'unchanged complete14/11/3 reverse source identities, not actual entry')
 return{'receipt':name,'sha256':digest(name),'old_manifest':old_manifest,'old_manifest_sha256':digest(old_manifest),
  'current_manifest':new_manifest,'current_manifest_sha256':digest(new_manifest),
  'changed_source_bindings':sorted(changed),'controller_only_constant_AST_change_verified':True,
  'first_nonpassing_receipt':first_value,'first_nonpassing_receipt_sha256':digest(first_value),
  'first_nonpassing_stderr':rel(logpath),'first_nonpassing_stderr_sha256':digest(logpath),
  'first_actual_methods':135,'first_actual_failures':1,'first_actual_errors':5,'first_methods_not_added_to_final_pass_count':True,
  'all_old_tests_preserved':True,'data_or_game_mechanics_changed':False,'source_failure_still_unknown':True,
  'current_compatibility_validation_required_and_in_final_eleven_modules':True}


def promotion(value,tests,reviewed_sha):
 record=load(value)
 require(record['section']==299 and record['kind']=='root_final_functional_and_compatibility_scope_before_revalidation'
  and set(record['existing_production_changes'])==CHANGED_EXISTING,'exact root repaired freeze and two declared old production paths')
 expected={CANONICAL,DATA,MANIFEST,BUILDER,'rouge/spawn_candidates.py','rouge/spawn_candidates_view.py',
  'tests/test_battle_entry_compatibility_299.py',*('tests/'+m.split('.')[-1]+'.py'for m in MODULES[:3])}
 expected|={p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file()}
 expected|={p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-battle-entry-compatibility-299').rglob('*')if p.is_file()}
 require(set(record['promoted'])==expected and record['native_script_pending']is False,'exact full final new-source allowlist, counts derived')
 require(record['initial_promotion']=='verification/sections/299-preparation/promotion.json'
  and record['pre_repair_freeze']=='verification/sections/299-preparation/final-promotion.json'
  and record['source_compatibility_repair']=='verification/sections/299-preparation/entry-binding-repair.json'
  and record['native_READY_sha256']=='bc148c16f9447dcfe8049e9cb44b74dc44bf63365961232f39712e3e21c5863b'
  and record['native_repair_READY_sha256']=='28cbf8852d7fc5c0af08052e2414bd35d2cdcfa61aee2bd94bcbee36dbb1fe63',
  'actual original promotion/native freeze plus explicitly independent source-repair/native3 provenance')
 previous=load(record['pre_repair_freeze']);original=load(record['initial_promotion'])
 normalized=deepcopy(record)
 for n in set(record['promoted'])-set(previous['promoted']):normalized['promoted'].pop(n)
 normalized['promoted'][CANONICAL]=deepcopy(previous['promoted'][CANONICAL])
 normalized['existing_production_changes'].pop('rouge/battle_event_references.py')
 normalized['kind']='root_final_functional_scope_source_freeze_before_actual_product_tests'
 for key in('pre_repair_freeze','source_compatibility_repair','native_repair_READY_sha256'):normalized.pop(key)
 require(normalized==previous,'repaired freeze differs only by declared compatibility sources/controller and native bound-source set')
 normalized=deepcopy(previous);normalized['promoted'].pop(CANONICAL)
 normalized['kind']='root_backend_view_parent_promotion_before_actual_product_validation';normalized['native_script_pending']=True
 normalized.pop('initial_promotion');normalized.pop('native_READY_sha256')
 require(normalized==original,'initial49 and first final50 promotions remain exact immutable predecessors')
 for name,pin in record['promoted'].items():
  require(set(pin)=={'sha256','bytes'}and digest(name)==pin['sha256']and path(name).stat().st_size==pin['bytes'],
   'exact final promoted byte source actually current '+name)
 for name,pin in record['existing_production_changes'].items():
  require(set(pin)=={'before_sha256','sha256','bytes'}and digest(name)==pin['sha256']and path(name).stat().st_size==pin['bytes'],
   'exact declared old production source repaired/final '+name)
  parent_bytes=subprocess.check_output(['git','show',PARENT+':'+name],cwd=ROOT)
  require(sha256(parent_bytes).hexdigest()==pin['before_sha256'],'actual original parent bytes '+name)
 require(digest(CANONICAL)==reviewed_sha,'reviewed actual final canonical native source')
 final={n:digest(n)for n in sorted(expected|CHANGED_EXISTING)}
 require(all(tests['source_sha256_after'].get(n)==v for n,v in final.items()),'all final functional and maintenance sources in actual final necessary map')
 compatibility=compatibility_repair(tests)
 return final,{'receipt':rel(value),'sha256':digest(value),'initial_promotion':record['initial_promotion'],
  'initial_promotion_sha256':digest(record['initial_promotion']),'pre_repair_freeze':record['pre_repair_freeze'],
  'pre_repair_freeze_sha256':digest(record['pre_repair_freeze']),'original_promoted_paths':len(original['promoted']),
  'new_functional_and_maintenance_paths':len(expected),'feature_paths_including_existing':len(final),
  'canonical_native_separately_bound':{'path':CANONICAL,'sha256':reviewed_sha},'existing_production_paths':len(CHANGED_EXISTING),
  'old_tracked_test_maintenance':False,'compatibility_maintenance':compatibility,'initial_promotion_is_provenance_not_acceptance':True}



def native(value,process_value,tests,reviewed_sha):
 data=load(value)
 require(data['section']==299 and data['kind']=='isolated_native_windows_spawn_candidate_reader'and data['passed']is True
  and data['failure']is None and data['qpa']=='windows'and type(data['qt_exit_code'])is int and data['qt_exit_code']==0
  and data['verification_window_closed']is True,'actual native Windows MainWindow, dialog, independent preview closed')
 require(type(data['process_id'])is int and data['process_id']>0 and re.fullmatch('[0-9a-f]{64}',reviewed_sha)is not None
  and digest(CANONICAL)==reviewed_sha,'actual fixture PID and explicitly reviewed final canonical')
 tree=ast.parse(path(CANONICAL).read_text(encoding='utf8'))
 labels={n.args[1].value for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='require'
  and len(n.args)>1 and isinstance(n.args[1],ast.Constant)and type(n.args[1].value)is str}
 require(type(data['checks'])is list and len(data['checks'])==len(set(data['checks']))==data['unique_checks']
  and labels<=set(data['checks'])and data['successful_assertion_executions_including_repeated_guards']>=len(data['checks']),
  'all reviewed literal assertion labels actually recorded; dynamic counts')
 require(data['source_sha256_before']==data['source_sha256_after']and set(data['source_sha256_after'])==selected_window_sources()
  and data['source_guard_is_selected_not_all_transitive_dependencies']is True,'exact selected native source closure stable')
 check_map(data['source_sha256_after'],'native299');joined=join_sources(tests['source_sha256_after'],data['source_sha256_after'])
 require(data['temporary_state_root']is True and data['state_paths_replaced_before_constructor']==['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE']
  and data['private_state_read_copied_or_restored']is False and data['external_entrypoints_blocked_before_original_call']is True,
  'four temp paths and blocked external entrypoints before actual MainWindow constructor')
 ops=data['external_operation_attempts'];require(set(ops)=={'game_enumeration','game_connect','game_capture','game_next_frame',
  'desktop_start','desktop_request','provider_chat','credential_read'}and all(type(v)is int and v==0 for v in ops.values()),'all eight external attempts zero')
 require(data['game_operated']is False and data['game_captures']==0 and data['chat_sent']is False and data['chat_attempted']is False
  and data['original_project_window_operated_or_restarted']is False and data['actual_process_termination_verified_by_this_script']is False
  and data['owned_supervisor_exit_and_cleanup_required_separately']is True
  and data['launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID']is True,'no invented game/chat/ancestry/terminal claims')
 raw,process=owned_process(process_value,value,data)
 require(data['requested_parent_client_size']==data['requested_preview_client_size']==[1050,720]
  and data['requested_dialog_client_size']==[900,680],'actual three owned window sizes required, not assumed size hints')
 readings=data['candidate_readings'];require(len(readings)==3 and{r['kind']for r in readings}=={
  'manual_other_candidate','package_member_without_group','empty_activation_and_blank_and_branch'}
  and all(r['actual_selected']is None for r in readings),'actual three distinct source flows, no actual chosen spawn inference')
 other=next(r for r in readings if r['kind']=='manual_other_candidate')
 require(other['stage_id']=='ro6_n_2_1'and other['origin_action_id']=='w1.f4.a1'and other['member_action_id']=='w1.f4.a8'
  and other['enemy_id']=='enemy_1352_eslime'and other['level_reference']==0 and other['parent_unchanged']is True,
  'manual exact different candidate preview, source level not player elite tier, parent preserved')
 refresh=data['same_scope_refresh_observations'];require(len(refresh)==3 and{r['path']for r in refresh}=={'dialog','parent','same_reference'}
  and all(r['source_scroll']>0 and r['source_selection']and r['parent_unchanged']is True and r['child_same_instance']is True for r in refresh),
  'actual three refresh paths preserve nonzero scroll/selection and same independent child')
 require(data['source_negative_fixtures']==[{'kind':'warm_manifest','manifest':MANIFEST,'damaged_member':MANIFEST,
  'public_clone_only':True,'restored_sha256':MANIFEST_SHA,'prior_child_closed':True,'actual_selection':None}],
  'warm valid public clone really damaged/restored; stale child cleared and no automatic choice')
 expected={'player-other-candidate','independent-fixed-preview','source-unavailable','player-package-ungrouped-member','player-empty-activation'}
 images=data['screenshots'];require(data['screenshot_count']==len(images)==len(expected)and{r['name']for r in images}==expected
  and sum(r['direct_player_text']is True for r in images)>=2,'actual five representative images, at least two ordinary player readers')
 handles={}
 def handle(row):
  sizes={'main':[1050,720],'dialog':[900,680],'candidate_preview':[1050,720]}
  require(row['kind']in sizes and row['client_size']==sizes[row['kind']]and row['qpa']=='windows'
   and type(row['hwnd'])is int and row['hwnd']>0 and row['process_id']==data['process_id'],'actual owned visible HWND/PID and exact client sizes')
  handles.setdefault(row['kind'],set()).add(row['hwnd'])
 require(bool(data['native_observations']),'actual HWND observations')
 for row in data['native_observations']:handle(row)
 for image in images:
  file=raw.with_name(raw.stem+'-'+image['name']+'.png');require(Path(image['path']).resolve()==file.resolve(),'actual raw screenshot path preserved')
  blob=path(path(value).with_name(file.name)).read_bytes()
  require(sha256(blob).hexdigest()==image['sha256']and blob[:8]==b'\x89PNG\r\n\x1a\n'and len(blob)>24
   and all(v>0 for v in struct.unpack('>II',blob[16:24])),'exact actual screenshot bytes/PNG dimensions');handle(image['native_window'])
 require(set(handles)=={'main','dialog','candidate_preview'}and all(len(s)==1 for s in handles.values())
  and len(set.union(*handles.values()))==3,'one distinct owned window for each real main/dialog/independent preview')
 return data,{'receipt':rel(value),'sha256':digest(value),'reviewed_native_source_sha256':reviewed_sha,
  'source_selected_files':len(data['source_sha256_after']),'source_unchanged':True,'source_join':joined,
  'unique_checks':data['unique_checks'],'actual_assertion_executions':data['successful_assertion_executions_including_repeated_guards'],
  'representative_images':len(images),'screenshots':len(images),'actual_player_reader_images':sum(r['direct_player_text']is True for r in images),
  'actual_Qt_exit':0,'owned_process':process,'actual_selection_or_probability_verified':False,'game_or_chat_verified':False}

def main(args):
 require(Path(__file__).resolve()==(HERE/'close_section_299.py').resolve(),'canonical cache closeout helper')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 require(branch=='codex/p2-development'and parent==PARENT and not(ROOT/'verification/sections/299.json').exists(),'exact authorized branch/parent; exclusive299 receipt')
 require(digest(CANONICAL)==args.native_source_sha256,'approved native bytes checked before its selected-source producer')
 source_ref=packet();tests,test_ref=necessary(args.necessary_receipt)
 feature_map,promotion_ref=promotion(args.promotion_receipt,tests,args.native_source_sha256)
 window,window_ref=native(args.window_receipt,args.window_process_receipt,tests,args.native_source_sha256)
 window_ref['root_visual_review']=visual_review(args.window_receipt,window)
 main_ref=original_window(args.main_window_receipt,args.focus_receipt,window,tests,args.necessary_receipt,args.window_receipt)
 full=load(FULL);require(digest(FULL)==FULL_SHA and full['after_section']==290 and full['available_checks_passed']is True
  and full['scope_not_reduced']is True and full['complete_repository_validation']is False,'only original historical290 available full reused')
 cp=load('DEVELOPMENT_CHECKPOINT.json')
 require(cp['completed_sections']==cp['latest_functional_section']==298 and cp['next_section']==299 and cp['active_section']['section']==299
  and cp['policy']['priority_order']==['P3','P2','P1']and cp['policy']['current_user_batch_target_section']is None
  and cp['policy']['stop_after_section']is None,'active299/P3-first/no numeric endpoint')
 require(cp['last_full_validation']['after_section']==290 and cp['current_available_full_validation']['section']==290
  and cp['policy']['full_validation_interval']==15 and cp['policy']['full_validation_anchor_section']==125
  and 125+((299-125)//15+1)*15==305,'unchanged full cadence/original290 proof')
 cloud=cp['last_verified_cloud_save'];proof=load(cloud['proof'])
 require(cloud['section']==298 and digest(cloud['proof'])==cloud['proof_sha256']and proof['passed']is True
  and proof['commit']==proof['remote_HEAD']==cloud['commit']and proof['push_primary_exit']==0,'actual previous298 ordinary publication')
 docs={n:path(n).read_bytes()for n in('DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','AGENTS.md')}
 progress=path('PROJECT_PROGRESS.md').read_bytes();require(sha256(progress).hexdigest()==PROGRESS_SHA_BEFORE,'remaining work not falsely retired by fixed source candidate reading')
 now=datetime.now(timezone(timedelta(hours=8))).isoformat()
 capability=('固定战斗预览可手动阅读当前条目的完整候选组和本关关联条目，区分敌人、场景物件与空白记录；'
  '仅对已能唯一对应的常规出怪资料手动打开独立固定预览，保留父页筛选、地图选点、当前敌人和阅读状态。'
  '换范围或来源失效清除旧资料及子预览，恢复后重新手选；同范围刷新保留阅读。'
  '同时将旧作战入口反查绑定到当前已核实代码，保留原14条联系、11可阅读入口与3明确排除；严格失效保护不关闭。')
 limits=['69关、38原关卡、285组和215关联包是固定资料条目范围，不是实际敌人数、当前选择、同时出场或概率。',
  '分支不能借用常规候选；场景物件和空白记录不借敌人头像或固定出怪入口，不推本局实际出现或生成结果。',
  '不减少17typed奖励、15全局层数、25场景/57选项、10未解析附注、完整地图81/59或逐格10图18关58点的剩余边界。',
  '本节必要与原生流程；290全量仅沿用原来源，下次305。P3/P2/P1未完成、识别最后，无路线推荐或数字终点。']
 receipt={'section':299,'kind':'functional_section','title':TITLE,'at_Beijing':now,'branch':branch,'prior_commit':parent,
  'remaining_item':'P3固定出怪条件、分组关系及地图与敌人资料对应','new_capability':capability,
  'files':sorted(feature_map),'source_sha256':feature_map,'source_reference':source_ref,'source_promotion':promotion_ref,
  'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),'existing_source_changes_including_test_maintenance':sorted(CHANGED_EXISTING),
  'old_tracked_test_maintenance':False,'compatibility_maintenance':promotion_ref['compatibility_maintenance'],'actual_server_generation_or_inventory_verified':False,
  'remaining_global_stage_floor_gaps_unchanged':15,'original_entry_gaps_unchanged':[25,57],'unparsed_notes_unchanged':10,
  'typed_named_grant_count_unchanged':17,'partial_direct_reference_scope_unchanged':[10,18,58],'whole_map_gaps_unchanged':[81,59],
  'necessary_validation':test_ref,'native_windows_validation':{**window_ref,'original_project_window':main_ref},
  'full_validation':{'receipt':FULL,'sha256':FULL_SHA,'after_section':290,'full_suite_rerun':False,'new299_source_full_validation_claimed':False,
   'next_periodic_section':305,'scope_not_reduced':True,'complete_repository_validation':False},
  'PROJECT_PROGRESS_unchanged_sha256':PROGRESS_SHA_BEFORE,'limits':limits,'next_section':300,
  'cloud_publication_binding':'enclosing_commit','cloud_published':False,'P3_complete':False,'P2_complete':False}
 history='historical_before299_current_pointers';require(history not in cp,'exclusive299 pointer archive')
 cp[history]={k:deepcopy(cp[k])for k in('current_section_save','current_section_validation','latest_section_environment','active_section','current_batch','cloud_publication_closeout')if k in cp}
 cp.pop('active_section',None);cp.pop('cloud_publication_closeout',None)
 cp.update(completed_sections=299,latest_functional_section=299,next_section=300,batch_status='P3_SECTION299_VALIDATED_AWAITING_PUBLICATION',
  next_full_validation_after=305,next_action='从300继续有证P3剩余事项，无数字终点；下次完整可用全量305。')
 cp['policy']['next_full_validation_after']=305;cp['current_batch_commit_policy']['next_full_validation_after']=305
 cp['current_batch'].update(status=cp['batch_status'],next_section=300,next_section_started=False,receipt='verification/sections/299.json',next_full_validation_after=305,batch_closed=False)
 cp['confirmed_next_stage_direction'].update(last_completed_functional_section=299,next_functional_section_started=False)
 cp['sections'].append({'number':299,'completion_ref':'p3-section-299','topic':TITLE,'verification':'verification/sections/299.json'})
 cp['current_section_save']={'section':299,'verification':'verification/sections/299.json','scope':'current_functional_section',
  'binding':'enclosing_commit','commit_reference':'commit containing299 exact fixed candidate reader, real acceptance, requirements and index'}
 cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_section_validation']={'section':299,'receipt':'verification/sections/299.json','necessary_methods_passed':test_ref['methods_run'],
  'native_isolated_window_checks':window['unique_checks'],'full_suite_rerun':False,'last_full_receipt':FULL,'full_source_is_historical290':True}
 cp['latest_section_environment']={'section':299,'receipt':'verification/sections/299.json',
  'native_windows':f"{test_ref['methods_run']} actual necessary; {window['unique_checks']} unique native; {window_ref['screenshots']} representative PNG including player text; original visible/private5 unchanged",
  'native_game_or_chat_verified':False,'current_section_full_rerun':False,'new_Linux_Wine_full_run':False,'last_full_receipt':FULL}
 cp['functional_sections_since_latest_requirement']=list(dict.fromkeys([*cp['functional_sections_since_latest_requirement'],299]))
 completed=(f'## 功能第299节 · {TITLE}\n\n{now}。{capability}\n\n'
  f"实际{test_ref['methods_run']}必要检查、原生{window['unique_checks']}唯一检查通过；{window_ref['screenshots']}张代表PNG由根代理查看，包含默认玩家正文；原项目窗口更新/私人5路径不变。"
  '来源及原回执verification/sections/299.json；69/38/285/215仅资料范围，不推本局选择、同时出场或概率，不减少其它入口、奖励或地图待办。'
  '首轮9模块135项出现1失败5错误，原件保留；修复旧入口来源绑定后完整11模块重新实测，首轮和准备检查不叠加为最终通过数。'
  '290全量原来源沿用，下次305，后续300，无数字终点。待普通推送核对。\n\n')
 mutations={'verification/sections/299.json':encode(receipt),'DEVELOPMENT_CHECKPOINT.json':encode(cp),'PROJECT_COMPLETED.md':completed.encode()+docs['PROJECT_COMPLETED.md']}
 wip=docs['WORK_IN_PROGRESS.md'].decode();require('## 功能第298节'in wip,'preserve prior298 history')
 mutations['WORK_IN_PROGRESS.md']=(completed+wip[wip.index('## 功能第298节'):]).encode()
 req=docs['PROJECT_REQUIREMENTS.md'].decode();a,b=req.index('<!-- current-delivery:start -->'),req.index('<!-- current-delivery:end -->')
 block=('<!-- current-delivery:start -->\n## 当前交付与续接 · 第299节\n\n2026-10-16继续P3，无数字终点。'+capability
  +f"实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过；原窗口更新/私人5路径不变。"
  +'固定资料范围不等于实际选择、数量或概率；17typed、15/25/57/10与81/59待办保持。290全量原来源/下次305；P3→P2→P1、识别最后，无路线建议。待普通推送核对。\n')
 mutations['PROJECT_REQUIREMENTS.md']=(req[:a]+block+req[b:]).encode()
 agents=docs['AGENTS.md'].decode();a,b=agents.index('## 当前续接 · 第298节'),agents.index('## 当前优先顺序与输出可读性')
 mutations['AGENTS.md']=(agents[:a]+'## 当前续接 · 第299节已完成功能与必要/原生验收\n\n'+capability
  +'来源及实际回执verification/sections/299.json；实际选择、数量、同时出场与概率仍未知，17typed与15/25/57/10待办不变。'
  +'原窗口更新/私人5路径不变；未跑299全量，290完整范围沿用原来源。下一节300/下次305，无数字终点。'
  +'P3→P2→P1、识别最后，不推荐/排序/自动选路；待普通推送核对，源码/要求/验收/索引同提交。\n\n'+agents[b:]).encode()
 require('初次招募时即处于已进阶状态'in mutations['PROJECT_REQUIREMENTS.md'].decode()and'初次招募即处于已进阶状态'in mutations['AGENTS.md'].decode(),'verified直升 terminology preserved')
 require(all(str(i)+'.'in mutations['AGENTS.md'].decode().split('## 当前续接')[0]for i in range(1,6)),'highest five judgment/source requirements preserved')
 archive=ROOT/'verification/sections/299-preparation/closeout-tools';require(not archive.exists(),'exclusive closeout source archive')
 copies={'close_section_299.py':path(HERE/'close_section_299.py').read_bytes(),'CONTRACT.md':path(HERE/'CONTRACT.md').read_bytes()}
 copies.update({'before-'+name:raw for name,raw in docs.items()})
 archive_manifest={'kind':'SECTION299_PUBLIC_CLOSEOUT_TOOLS_NOT_PRIVATE_STATE','files':{n:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}for n,raw in copies.items()},'private_contents_or_hash_lists_copied':False}
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
  with target.open('xb'if name=='verification/sections/299.json'else'wb')as stream:stream.write(raw)
 print(json.dumps({'section':299,'local_closeout_written':True,'cloud_published':False,'next_section':300,'next_full_section':305}))

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--necessary-receipt',required=True);parser.add_argument('--window-receipt',required=True)
 parser.add_argument('--window-process-receipt',required=True);parser.add_argument('--native-source-sha256',required=True)
 parser.add_argument('--promotion-receipt',default='verification/sections/299-preparation/final-promotion-repair.json')
 parser.add_argument('--main-window-receipt',default='verification/sections/299-main-window.json')
 parser.add_argument('--focus-receipt',default='verification/sections/299-main-window-focus.json')
 parser.add_argument('--apply',action='store_true');main(parser.parse_args())
