"""Unexecuted293 strict closeout. Preview only unless root uses --apply.

Reads public actual receipts; never runs tests/Qt/game/chat, reads private
contents, restarts windows, publishes Git, or relabels full290 as full293.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,re,struct,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'.cache/p3-293-closeout/revision2'
CANONICAL='scripts/verify_resting_corner_window_293.py'
TITLE='安眠一隅四条随机选择的后续资料与手动场景阅读'
FULL='verification/full-290/summary.json'
FULL_SHA='2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
MANIFEST='research/p3-resting-results-293/source-manifest.json'
MANIFEST_SHA='3db8aee2815e898211bc902d0314e0d58e5e1fd5c585cd265fde280b4d2b5476'
PACKET_FILES={'research/p3-resting-results-293/prts-events-427904.html',
 'research/p3-resting-results-293/prts-events-440271.html',
 'research/p3-resting-results-293/original-records.json',
 'research/p3-resting-results-293/community-readback.json',
 'research/p3-resting-results-293/extraction.json','rouge/data/resting-corner-results.json',
 'rouge/data/node-catalog.json','scripts/build_resting_corner_results_293.py'}
MODULES=['tests.test_resting_corner_results_293','tests.test_resting_corner_view_293',
 'tests.test_event_preview_filters_292','tests.test_node_catalog_view',
 'tests.test_original_entry_planning','tests.test_event_planning']
EVENT='community_group_023'
CARDS=((EVENT+':scene:1:choice:0',3,3,(('小狗',2),('捕梦网',4),('松鼠',5))),
 (EVENT+':scene:6:choice:0',2,2,(('果园',7),('竞速比赛',3))),
 (EVENT+':scene:9:choice:1',2,1,(('动物泥偶',10),)),
 (EVENT+':scene:11:choice:0',2,3,(('果园',7),('竞速比赛',3),('动物泥偶',10))))

def require(value,message):
 if value is not True:raise ValueError('293 closeout prerequisite: '+message)


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
  and child[5]=='--receipt' and child[7:]==['--visible-ms','30000'],'canonical actual child argv, not a cache or synthetic result')
 raw=Path(child[6]);require(raw.is_absolute() and raw.name==path(window_value).name,'raw/public receipt basename preserved')
 require(process['section']==293 and process['kind']=='actual_native_window_owned_process_execution'
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



def packet():
 require(digest(MANIFEST)==MANIFEST_SHA,'fixed public source manifest, not a caller/candidate override')
 data=load(MANIFEST)
 require(set(data['files'])==PACKET_FILES,'exact eight public packet members')
 for name,expected in data['files'].items():
  require(path(name).stat().st_size==expected['bytes'] and digest(name)==expected['sha256'],'pinned public packet bytes '+name)
 return data
def selected_window_sources():
 names={CANONICAL,'rouge/app.py','rouge/node_catalog_view.py','rouge/resting_corner_view.py',
  'rouge/resting_corner_results.py','rouge/node_catalog.py','rouge/event_planning.py',
  'rouge/player_node_information.py','rouge/ui_state.py','rouge/data/node-catalog.json',
  'rouge/data/event-planning-reference.json','tests/test_resting_corner_results_293.py',
  'tests/test_resting_corner_view_293.py',MANIFEST}
 names.update(packet()['files'])
 return names
def expected_necessary_sources():
 paths=set(ROOT.glob('rouge/**/*.py'))|set(ROOT.glob('rouge/data/*.json'))
 paths|={ROOT/('tests/'+module.split('.')[-1]+'.py') for module in MODULES}
 paths|={ROOT/CANONICAL,ROOT/'verification/sections/293-preparation/before-node_catalog_view.py'}
 paths|={ROOT/MANIFEST}|{ROOT/name for name in packet()['files']}
 return {p.relative_to(ROOT).as_posix() for p in paths if p.is_file()}
def builder_evidence():
 application_path='verification/sections/293-preparation/promotion/application.json'
 application=load(application_path);prefix='verification/sections/293-preparation/promotion/'
 require(application['section']==293 and application['existing_engine_data_eligibility_state_modified'] is False,
  'promotion scope and original preparation labels retained')
 for name,expected in application['public_builder_originals'].items():
  require(Path(name).name==name and digest(prefix+name)==expected['sha256']
   and path(prefix+name).stat().st_size==expected['bytes'],'exact preserved builder original '+name)
 rows=[]
 for filename,expected in (('build-first-process.json',1),('build-attempt2-process.json',0),
   ('build-revision2-process.json',1),('build-revision3-process.json',0)):
  record=load(prefix+filename)
  require(type(record['exit_code']) is int and record['exit_code']==expected,'actual source-build exit '+filename)
  rows.append({'receipt':prefix+filename,'sha256':digest(prefix+filename),'actual_exit':expected})
 return {'application':application_path,'application_sha256':digest(application_path),
  'public_originals':len(application['public_builder_originals']),'source_build_attempts':rows,
  'two_actual_source_builder_failures_preserved':True,'necessary_test_failure_claimed':False,
  'preparation_labels_are_historical_not_current_test_status':True}
def unchanged_existing_sources(data):
 previous=load('verification/sections/292.json');reference=previous['necessary_validation']
 require(digest(reference['receipt'])==reference['sha256'],'published292 necessary raw receipt exact bytes')
 original=load(reference['receipt'])
 require(original['section']==292 and original['exit_code']==0 and original['source_unchanged'] is True
  and original['source_sha256_before']==original['source_sha256_after'],'original292 stable-source necessary evidence')
 old={name:expected for name,expected in original['source_sha256_after'].items()
  if name.startswith('rouge/') and name!='rouge/node_catalog_view.py'
  and (name.endswith('.py') or (name.startswith('rouge/data/') and name.endswith('.json')))}
 require(bool(old) and all(data['source_sha256_after'].get(name)==expected for name,expected in old.items()),
  'all prior public production Python/static JSON unchanged except intended NodeCatalogPanel UI seam')
 reused={name:expected for name,expected in original['source_sha256_after'].items()
  if name.startswith('rouge/') and not (name.endswith('.py') or name.endswith('.json'))}
 require(set(reused)=={'rouge/data/battle-maps/ro6_e_t_3.png'},'exact previous non-model image reference scope')
 check_map(reused,'previous image current-file reuse only, not a293 producer source')
 require(not(set(reused)&set(data['source_sha256_after'])),'reused image is not inserted into293 actual producer map')
 before='verification/sections/293-preparation/before-node_catalog_view.py'
 require(digest(before)==original['source_sha256_after']['rouge/node_catalog_view.py'],
  'actual pre293 NodeCatalogPanel source preserved against previous actual source map')
 return {'previous_section':292,'previous_necessary_receipt':reference['receipt'],
  'previous_necessary_sha256':reference['sha256'],'unchanged_existing_public_production_files':len(old),
  'only_existing_production_source_changed':'rouge/node_catalog_view.py',
  'previous_non_model_reference_current_file_reuse':reused,
  'previous_image_reuse_is_not_a293_producer_source_or_new_execution':True,
  'new_read_only_modules_and_reference_data_are_not_existing_mechanism_changes':True}
def necessary(value,parent):
 data=load(value)
 require(data['section']==293 and data['kind']=='necessary_change_related_tests_not_full_suite'
  and type(data['exit_code']) is int and data['exit_code']==0 and data['source_unchanged'] is True
  and data['source_sha256_before']==data['source_sha256_after'],'actual necessary0 with stable final source')
 require(data['modules']==MODULES and data['argv'][1:7]==['-B','-X','utf8','-m','unittest','-v']
  and data['argv'][-len(MODULES):]==MODULES and data['source_commit_before']==parent,
  'complete actual six-module argv and current parent')
 require(data['game_sampling_verified'] is False and data['chat_verified'] is False
  and data['full_scope_reduced'] is False and data['full_suite_rerun'] is False,'necessary only, no game/chat/full claims')
 require(set(data['source_sha256_after'])==expected_necessary_sources(),'exact necessary producer source inventory')
 check_map(data['source_sha256_after'],'final necessary')
 baseline=unchanged_existing_sources(data)
 logpath=path(value).with_name('stderr.txt');log=path(logpath).read_text(encoding='utf-8')
 counts=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',log)
 require(len(counts)==1 and int(counts[0][0])>0 and log.rstrip().endswith('OK')
  and not re.search(r'^(FAIL|ERROR):',log,re.M),'actual final complete Ran/OK, no prefilled N')
 stdout=path(value).with_name('stdout.txt');path(stdout)
 return data,{'receipt':rel(value),'sha256':digest(value),'stderr':rel(logpath),
  'stderr_sha256':digest(logpath),'stdout':rel(stdout),'stdout_sha256':digest(stdout),
  'actual_exit':0,'methods_run':int(counts[0][0]),'seconds':float(counts[0][1]),
  'source_unchanged':True,'source_files':len(data['source_sha256_after']),'modules':MODULES,
  'author22_and_UI11_are_subsets_not_added_again':True,'existing_source_boundary':baseline}
def native(value,process_value,necessary_data):
 data=load(value)
 require(data['section']==293 and data['kind']=='isolated_native_windows_resting_corner_reading'
  and data['passed'] is True and data['failure'] is None and data['qpa']=='windows'
  and type(data['qt_exit_code']) is int and data['qt_exit_code']==0 and data['verification_window_closed'] is True,
  'actual canonical native Windows/Qt/owned-window close completion')
 require(type(data['process_id']) is int and data['process_id']>0,'actual fixture PID positive independently of launcher')
 required={'native_windows_QPA','parent_actual_client_size_exact_1050x720',
  'dialog_actual_client_size_at_least_900x660','dedicated_resting_button_visible_inside_parent_1050x720',
  'actual_parent_button_constructed_and_retained_owned_dialog','parent_and_dialog_have_distinct_owned_HWNDs',
  'dialog_default_does_not_choose_card_branch_or_open_scene','four_cards_keep_exact_complete_choice_keys',
  'opening_child_preserves_parent_reading_state','literal_annotation_and_listed_branch_counts_3_2_1_3_preserved',
  'literal_branches_and_destinations_not_repaired_or_invented','branch_controls_use_complete_origin_specific_reference_ids',
  'player_reference_states_future_buttons_and_actual_unknown_without_sum',
  'player_result_uses_chinese_without_raw_identifiers_or_source_urls','both_count_conflicts_visible_in_player_result',
  'matching_counts_not_falsely_marked_conflicting','reading_cards_does_not_confirm_actual_result_pool_or_eligibility',
  'selecting_branch_alone_does_not_automatically_open_scene',
  'real_manual_button_opens_exact_community_destination_scene',
  'manual_destination_contains_its_distinct_scene_and_future_button_text',
  'scene_reading_never_claims_game_transition_or_reward',
  'ninety_nine_gold_destination_mismatch_visible_in_player_result',
  'all_six_distinct_destinations_manually_read_without_pool_inference',
  'all_nine_origin_specific_branches_remain_distinct','real_nonzero_scroll_and_nonempty_document_selection',
  'same_scope_refresh_retains_card_branch_scene_tab_text_cursor_selection_and_real_scroll',
  'child_navigation_and_parent_refresh_preserve_parent_reading_state',
  'temporary_complete_public_source_clone_validates_before_damage',
  'source_failure_clears_all_reference_controls_and_old_identity','source_failure_clears_all_three_old_reading_pages',
  'temporary_source_restored_from_true_original_bytes',
  'source_recovery_does_not_automatically_restore_choice_branch_or_scene',
  'source_recovery_does_not_reopen_stale_scene_text',
  'different_parent_event_invalidates_resting_scope_and_all_old_selections','different_event_clears_all_three_dialog_pages',
  'return_to_event_reuses_dialog_without_restoring_old_scope_selection',
  'manual_reading_never_changes_temporary_run_memory'}
 checks=data['checks']
 require(len(checks)==len(set(checks))==data['unique_checks'] and required<=set(checks)
  and data['successful_assertion_executions_including_repeated_guards']>=len(checks),
  'all meaningful UI behaviors with actual receipt-derived counts')
 selected=selected_window_sources()
 require(data['source_sha256_before']==data['source_sha256_after'] and set(data['source_sha256_after'])==selected
  and data['source_guard_is_selected_not_all_transitive_dependencies'] is True,'exact final selected public native source set')
 check_map(data['source_sha256_after'],'native final')
 require(all(necessary_data['source_sha256_after'].get(name)==expected for name,expected in data['source_sha256_after'].items()),
  'native exact same bytes as necessary source subset')
 require(data['temporary_state_root'] is True
  and data['state_paths_replaced_before_constructor']==['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE']
  and data['private_state_read_copied_or_restored'] is False and data['external_entrypoints_blocked_before_original_call'] is True,
  'temporary four paths before constructor and original external blocking')
 attempts=data['external_operation_attempts']
 require(set(attempts)=={'game_enumeration','game_connect','game_capture','game_next_frame',
   'desktop_start','desktop_request','provider_chat','credential_read'}
  and all(type(n) is int and n==0 for n in attempts.values()),'all eight original external attempts zero')
 require(data['game_operated'] is False and type(data['game_captures']) is int and data['game_captures']==0
  and data['chat_sent'] is False and data['chat_attempted'] is False
  and data['original_project_window_operated_or_restarted'] is False,'no game/chat/private/original window operations')
 require(data['actual_process_termination_verified_by_this_script'] is False
  and data['owned_supervisor_exit_and_cleanup_required_separately'] is True
  and data['launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID'] is True,
  'fixture does not invent process ancestry or job cleanup proof')
 raw,process_ref=owned_process(process_value,value,data)
 require(data['requested_parent_client_size']==[1050,720] and data['minimum_dialog_client_size']==[900,660]
  and bool(data['native_observations']),'actual one parent size and bounded dialog observations')
 handles={'parent':set(),'dialog':set()}
 def check_handle(handle):
  kind=handle['kind'];require(kind in handles and handle['process_id']==data['process_id']
   and handle['qpa']=='windows' and type(handle['hwnd']) is int and handle['hwnd']>0,'own actual native HWND/fixture PID')
  size=handle['client_size'];require(type(size) is list and len(size)==2 and all(type(n) is int for n in size),'actual logical client size')
  require(size==[1050,720] if kind=='parent' else size[0]>=900 and size[1]>=660,'parent exact/dialog minimum actual logical dimensions')
  handles[kind].add(handle['hwnd'])
 for handle in data['native_observations']:check_handle(handle)
 images=data['screenshots']
 expected_images={'parent-entry':'parent','first-three-branches':'dialog',
  'conflict-and-ninety-nine-scene':'dialog','source-reading-retained':'dialog',
  'source-invalidated':'dialog','restored-unselected':'dialog'}
 require(data['screenshot_count']==len(images)==len(expected_images)
  and {image['name'] for image in images}==set(expected_images),'all six own-window flow image originals')
 for image in images:
  expected=raw.with_name(raw.stem+'-'+image['name']+'.png')
  require(Path(image['path']).resolve()==expected.resolve(),'unaltered raw PNG sibling provenance')
  archived=path(value).with_name(expected.name);pixels=path(archived).read_bytes()
  require(sha256(pixels).hexdigest()==image['sha256'] and pixels[:8]==b'\x89PNG\r\n\x1a\n' and len(pixels)>24
   and all(n>0 for n in struct.unpack('>II',pixels[16:24])),'exact archived real native PNG bytes')
  require(image['native_window']['kind']==expected_images[image['name']],'PNG expected actual own-window kind')
  check_handle(image['native_window'])
 require(all(len(values)==1 for values in handles.values()) and handles['parent'].isdisjoint(handles['dialog']),
  'one parent and one distinct dialog native HWND, both actual fixture PID')
 require(len(data['public_observations'])==1,'one actual public observation group')
 record=data['public_observations'][0]
 expected_cards=[{'choice_key':key,'documented_count':annotation,'listed_branch_count':listed,
  'branch_ids':[key+':sub:'+str(i) for i in range(listed)]} for key,annotation,listed,branches in CARDS]
 expected_navigation=[{'choice_key':key,'branch_id':key+':sub:'+str(i),'label':label,
  'target_scene_key':EVENT+':scene:'+str(target)} for key,annotation,listed,branches in CARDS
  for i,(label,target) in enumerate(branches)]
 require(record['card_count_references']==expected_cards and record['manual_one_hop_reading']==expected_navigation,
  'literal four card references and all nine origin-specific manual scene requests')
 require(record['distinct_scene_keys']==sorted({row['target_scene_key'] for row in expected_navigation})
  and all(record[name] is None for name in ('default_choice','actual_game_transition','actual_choice_executed',
   'actual_rewards_granted','complete_actual_pool'))
  and record['source_failure_is_only_an_explicit_temporary_public_clone_negative_fixture'] is True,
  'six known community targets, source-clone negative fixture, all actual results unknown')
 return data,{'receipt':rel(value),'sha256':digest(value),'source_selected_files':len(selected),
  'source_unchanged':True,'unique_checks':len(checks),
  'actual_assertion_executions':data['successful_assertion_executions_including_repeated_guards'],
  'actual_parent_client_size':[1050,720],'minimum_dialog_client_size':[900,660],
  'screenshots':len(images),'actual_Qt_exit':0,'actual_windows_closed':True,
  'images_visually_reviewed_by_helper':False,'owned_process':process_ref,'game_or_chat_verified':False}

def visual_review(window_value,window):
 review_path='verification/sections/293-preparation/root-visual-review.json';review=load(review_path)
 require(review['section']==293 and review['kind']=='root_archived_native_images_review'
  and review['actual_images_opened_with_view_image'] is True,'actual root image review, not helper image inspection')
 expected={rel(path(window_value).with_name(Path(row['path']).name)):row['sha256'] for row in window['screenshots']}
 require(review['images']==expected and review['actual_image_count']==len(expected),
  'root actual review binds all exact six archived native images')
 require(any('not a separate image' in item and 'conflict' in item for item in review['not_verified_from_images']),
  'root image review explicitly preserves conflict-card screenshot coverage boundary')
 return {'receipt':review_path,'sha256':digest(review_path),'actual_root_reviewed_images':len(expected),
  'helper_performed_visual_inspection':False,'conflict_messages_checked_by_actual_native_assertions_not_separate_images':True}

def original_window(main_value,focus_value,fixture,necessary_data,necessary_value,native_value):
 main,focus=load(main_value),load(focus_value)
 require(path(main_value).resolve()==(ROOT/'verification/sections/293-main-window.json').resolve()
  and path(focus_value).resolve()==(ROOT/'verification/sections/293-main-window-focus.json').resolve(),
  'strict same-section canonical293 main/focus receipt paths')
 require(main['section']==293 and focus['section']==293
  and main['necessary_receipt_sha256']==digest(necessary_value)
  and main['native_receipt_sha256']==digest(native_value)
  and main['native_receipt']==rel(native_value) and main['necessary_receipt']==rel(necessary_value)
  and focus['main_receipt_sha256']==digest(main_value),
  'actual293 main binds both final evidence receipts; focus binds exact same main bytes')
 require(main['source_sha256_before']==main['source_sha256_after']==fixture['source_sha256_after']
  and set(main['source_sha256_after'])==selected_window_sources(),
  'same final actual native_selected source map stable through original window restart')
 check_map(main['source_sha256_after'],'original293 window final native_selected sources')
 timestamps={name:datetime.fromisoformat(value.replace('Z','+00:00')) for name,value in {
  'started':main['started_utc'],'finished':main['finished_utc'],'focus':focus['at_utc'],
  'necessary_finished':necessary_data['finished_utc'],'native_finished':fixture['finished_at']}.items()}
 require(all(value.tzinfo is not None and value.utcoffset() is not None for value in timestamps.values()),
  'actual main/focus/final-check timestamps are timezone-aware')
 require(timestamps['started']>timestamps['necessary_finished'] and timestamps['started']>timestamps['native_finished']
  and timestamps['finished']>=timestamps['started'] and timestamps['focus']>=timestamps['finished'],
  'original293 restart occurs after both final validations; focus follows completed main receipt')
 require(main['passed'] is True and main['private_file_hash_comparison_count']==5 and main['private_hashes_equal'] is True
  and main['changed_private_paths']==[] and main['private_contents_parsed_copied_or_restored'] is False and main['no_private_restoration'] is True,
  'actual original-window update/private5 hash unchanged, no content parsing/copy/restore')
 require(len(main['visible_windows'])==1,'one visible original project window');visible=main['visible_windows'][0]
 require(visible['visible'] is True and visible['responding'] is True and visible['minimized'] is False and visible['hwnd']>0
  and visible['pid']!=fixture['process_id'],'original window responsive/visible and not fixture')
 require(focus['visible'] is True and focus['pid']==visible['pid'] and focus['hwnd']==focus['actual_foreground']==visible['hwnd'],
  'actual foreground original project window')
 return {'receipt':rel(main_value),'sha256':digest(main_value),'focus_receipt':rel(focus_value),'focus_sha256':digest(focus_value),
  'section':293,'necessary_receipt_sha256':digest(necessary_value),'native_receipt_sha256':digest(native_value),
  'native_selected_current_source_unchanged':True,'started_after_final_necessary_and_native':True,'focus_after_main_finished':True,
  'private_hash_comparisons':5,'changed_private_paths':0,'visible_responsive_foreground':True,'private_contents_read_by_helper':False}



def main(args):
 require(Path(__file__).resolve()==(HERE/'close_section_293.py').resolve(),'reviewed canonical cache helper')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 require(branch=='codex/p2-development' and not (ROOT/'verification/sections/293.json').exists(),
  'authorized branch and exclusive new section receipt')
 builds=builder_evidence();tests,test_ref=necessary(args.necessary_receipt,parent)
 window,window_ref=native(args.window_receipt,args.window_process_receipt,tests)
 window_ref['root_visual_review']=visual_review(args.window_receipt,window)
 main_ref=original_window(args.main_window_receipt,args.focus_receipt,window,tests,args.necessary_receipt,args.window_receipt)
 full=load(FULL)
 require(digest(FULL)==FULL_SHA and full['after_section']==290 and full['available_checks_passed'] is True
  and full['scope_not_reduced'] is True and full['P2_complete'] is False and full['complete_repository_validation'] is False,
  'historical290 complete available scope preserved, not rerun or relabelled293')
 cp=load('DEVELOPMENT_CHECKPOINT.json')
 require(cp['completed_sections']==cp['latest_functional_section']==292 and cp['next_section']==293
  and cp['active_section']['section']==293 and cp['policy']['priority_order']==['P3','P2','P1']
  and cp['policy']['current_user_batch_target_section'] is None and cp['policy']['stop_after_section'] is None,
  'actual292 to active293 continuation/P3 first/no numeric endpoint')
 require(cp['policy']['full_validation_anchor_section']==125 and cp['policy']['full_validation_interval']==15
  and cp['last_full_validation']['after_section']==290 and cp['current_available_full_validation']['section']==290
  and 125+((293-125)//15+1)*15==305,'original full290 pointers and next305 cadence')
 prior=cp['last_verified_cloud_save'];proof=load(prior['proof'])
 require(prior['section']==292 and digest(prior['proof'])==prior['proof_sha256'] and proof['passed'] is True
  and proof['commit']==proof['remote_HEAD']==prior['commit'] and proof['push_primary_exit']==0,
  'real prior292 ordinary publication proof')
 now=datetime.now(timezone(timedelta(hours=8))).isoformat()
 scope=('安眠一隅四条具体随机选择按完整标识列出九条资料后续；分别列明未来按钮的20希望、15护盾、1件珍贵加工品或99源石锭，'
  '手动阅读六个对应社区场景。两处原注数量与所列项数冲突、99源石锭入口错配均明确保留；不把后续数量相加或当作当前领取。'
  '同范围刷新保留选项、分支和阅读，来源失效清空旧内容，恢复后不自动重选。')
 limits=['只新增固定资料一跳结果阅读；原有机制、资格/费用、目录和本局状态未改，10条附注及25原场景/57原选项入口缺口不减。',
  '四卡所列3/2/1/3条后续不是已闭合随机池；两处数量冲突、99源石锭原入口、本局发生/可选/实际领取仍未知。',
  '仅必要检查与真实隔离Windows新UI；290全量仍沿用原来源，下次305，不称293新源全量通过。',
  '两次来源构建失败和修证原件保留；作者22项与UI11项已包含于实际必要总数，不重复相加。',
  'P3/P2/P1未完、识别最后；不推荐、排序或自动选路；符号链接1314/Linux-Wine/原私样本/游戏聊天不计通过。']
 changed=['rouge/node_catalog_view.py','rouge/resting_corner_view.py','rouge/resting_corner_results.py',
  'rouge/data/resting-corner-results.json','scripts/build_resting_corner_results_293.py',
  'tests/test_resting_corner_results_293.py','tests/test_resting_corner_view_293.py',CANONICAL,
  *sorted(name for name in packet()['files'] if name.startswith('research/')),MANIFEST]
 receipt={'section':293,'kind':'functional_section','title':TITLE,'at_Beijing':now,'branch':branch,'prior_commit':parent,
  'remaining_item':'P3安眠一隅随机注释与后续奖励资料的可用阅读入口','new_capability':scope,'files':changed,
  'source_sha256':{name:digest(name) for name in changed},'existing_mechanics_eligibility_catalog_or_state_changed':False,
  'original_remaining_scenes':25,'original_remaining_choices':57,'existing_unparsed_annotations_not_closed':10,
  'reference_card_count':4,'listed_origin_specific_branch_count':9,'distinct_future_scene_count':6,
  'documented_listed_count_pairs':[[3,3],[2,2],[2,1],[2,3]],
  'actual_result_pool':None,'actual_current_grants':None,'actual_server_or_original_entry_verified':False,
  'necessary_validation':test_ref,'native_windows_validation':{**window_ref,'original_project_window':main_ref},
  'source_builder_preparation_history':builds,'full_validation':{'receipt':FULL,'sha256':FULL_SHA,'after_section':290,
   'full_suite_rerun':False,'new293_source_full_validation_claimed':False,'scope_not_reduced':True,
   'next_periodic_section':305,'complete_repository_validation':False},'limits':limits,'next_section':294,
  'cloud_publication_binding':'enclosing_commit','cloud_published':False,'P3_complete':False,'P2_complete':False}
 history='historical_before293_current_pointers';require(history not in cp,'exclusive prior-current history')
 cp[history]={key:deepcopy(cp[key]) for key in ('current_section_save','current_section_validation',
  'latest_section_environment','active_section','current_batch','cloud_publication_closeout') if key in cp}
 cp.pop('active_section',None);cp.pop('cloud_publication_closeout',None)
 cp.update(completed_sections=293,latest_functional_section=293,next_section=294,
  batch_status='P3_SECTION293_VALIDATED_AWAITING_PUBLICATION',next_full_validation_after=305,
  next_action='从294继续有证P3剩余事项，无连续数字终点；下一次完整可用全量305。')
 cp['policy']['next_full_validation_after']=305;cp['current_batch_commit_policy']['next_full_validation_after']=305
 cp['current_batch'].update(status=cp['batch_status'],next_section=294,next_section_started=False,
  receipt='verification/sections/293.json',next_full_validation_after=305,batch_closed=False)
 cp['confirmed_next_stage_direction'].update(last_completed_functional_section=293,next_functional_section_started=False)
 cp['sections'].append({'number':293,'completion_ref':'p3-section-293','topic':TITLE,'verification':'verification/sections/293.json'})
 cp['current_section_save']={'section':293,'verification':'verification/sections/293.json','scope':'current_functional_section',
  'binding':'enclosing_commit','commit_reference':'commit containing293 reading source, public references, necessary/native receipts, requirements and cloud index'}
 cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_section_validation']={'section':293,'receipt':'verification/sections/293.json',
  'necessary_methods_passed':test_ref['methods_run'],'native_isolated_window_checks':window['unique_checks'],
  'full_suite_rerun':False,'last_full_receipt':FULL,'full_source_is_historical290':True}
 cp['latest_section_environment']={'section':293,'receipt':'verification/sections/293.json',
  'native_windows':f"{test_ref['methods_run']} actual necessary; {window['unique_checks']} unique native UI checks, 1050x720 parent and at least900x660 dialog; original window visible/private5 unchanged",
  'native_game_or_chat_verified':False,'new_Linux_Wine_full_run':False,'current_section_full_rerun':False,'last_full_receipt':FULL}
 cp['functional_sections_since_latest_requirement']=list(dict.fromkeys([*cp['functional_sections_since_latest_requirement'],293]))
 docs={name:path(name).read_bytes() for name in ['DEVELOPMENT_CHECKPOINT.json','PROJECT_PROGRESS.md',
  'PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','AGENTS.md']}
 completed=(f'## 功能第293节 · {TITLE}\n\n{now}。{scope}\n\n'
  f"实际{test_ref['methods_run']}项必要检查与原生{window['unique_checks']}个唯一UI检查通过；1050×720父窗口、独立对话框、六场景阅读、真实非零滚动/选区留存与源失效恢复已核。"
  '原项目窗口更新且私人5路径hash不变。两次来源构建失败原件保留，不与必要检查重复计数；10条附注及25/57原入口缺口不减。'
  f'详见verification/sections/293.json，沿用{FULL}原冻结可用范围，不冒称293全量。后续294、下次305；P3/P2/P1未完、识别最后，无数字终点。待普通推送核对。\n\n')
 mutations={'verification/sections/293.json':encode(receipt),'DEVELOPMENT_CHECKPOINT.json':encode(cp),
  'PROJECT_COMPLETED.md':completed.encode()+docs['PROJECT_COMPLETED.md']}
 wip=docs['WORK_IN_PROGRESS.md'].decode();require('## 功能第292节' in wip,'keep292 onward history')
 mutations['WORK_IN_PROGRESS.md']=(completed+wip[wip.index('## 功能第292节'):]).encode()
 progress=docs['PROJECT_PROGRESS.md'].decode();anchor='10条未解析附注的结果/条件分类与来源核验；'
 require(progress.count(anchor)==1 and '游戏内实际展示' in progress,'exact remaining-only gap anchor and actual game display unknown retained')
 addition='安眠一隅两处原注数量冲突、完整候选范围与99源石锭原入口及本局实际结果；'
 require(addition not in progress,'exclusive new remaining gap wording')
 mutations['PROJECT_PROGRESS.md']=progress.replace(anchor,anchor+addition,1).encode()
 req=docs['PROJECT_REQUIREMENTS.md'].decode();a,b=req.index('<!-- current-delivery:start -->'),req.index('<!-- current-delivery:end -->')
 block=('<!-- current-delivery:start -->\n## 当前交付与续接 · 第293节\n\n2026-10-16继续P3，无数字终点。'+scope
  +f"最终实际{test_ref['methods_run']}必要检查和原生{window['unique_checks']}个唯一UI检查通过，原窗口更新/私人5路径不变。"
  +'10条附注与25/57原入口不减；290全量保留原来源，下次305。P3→P2→P1、识别最后，不提供路线建议；待普通推送核对，源码/要求/回执/索引同提交。\n')
 mutations['PROJECT_REQUIREMENTS.md']=(req[:a]+block+req[b:]).encode()
 agents=docs['AGENTS.md'].decode();a,b=agents.index('## 当前续接 · 第292节'),agents.index('## 当前优先顺序与输出可读性')
 mutations['AGENTS.md']=(agents[:a]+'## 当前续接 · 第293节已完成功能与必要/原生验收\n\n'+scope
  +'来源与实际回执见verification/sections/293.json；两次来源构建失败保留，10条附注/25与57原入口不减少，原窗口更新/私人5路径不变。'
  +'未跑293全量，290完整可用范围沿用原来源；下一节294/下次305，无数字终点。P3→P2→P1、识别最后，不推荐/排序/自动选路。'
  +'本节待普通推送并核对真实远端，源码/要求/验收/索引同提交。\n\n'+agents[b:]).encode()
 require('游戏内实际展示' in mutations['PROJECT_PROGRESS.md'].decode()
  and '10条未解析附注' in mutations['PROJECT_PROGRESS.md'].decode(),'game display and all10 notes remain unknown')
 require('初次招募时即处于已进阶状态' in mutations['PROJECT_REQUIREMENTS.md'].decode()
  and '初次招募即处于已进阶状态' in mutations['AGENTS.md'].decode(),'keep verified recruitment terminology')
 require(all(str(i)+'.' in mutations['AGENTS.md'].decode().split('## 当前续接')[0] for i in range(1,6)),
  'keep highest-priority five independent judgment requirements')
 archive=ROOT/'verification/sections/293-preparation/closeout-tools';require(not archive.exists(),'exclusive new public helper archive')
 copies={'close_section_293.py':path(HERE/'close_section_293.py').read_bytes(),
  'CONTRACT.md':path(HERE/'CONTRACT.md').read_bytes()}
 copies.update({'before-'+name:raw for name,raw in docs.items()})
 manifest={'kind':'SECTION293_PUBLIC_CLOSEOUT_TOOLS_NOT_PRIVATE_STATE',
  'files':{name:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)} for name,raw in copies.items()},
  'private_contents_or_hash_lists_copied':False,'tests_GUI_game_chat_git_publish_or_full_executed_by_helper':False}
 print(json.dumps({'gates_passed':True,'apply_requested':args.apply,'necessary_actual_methods':test_ref['methods_run'],
  'native_actual_unique_checks':window['unique_checks'],'native_selected_source_files':len(selected_window_sources()),
  'planned_public_files':list(mutations),'full_rerun':False,'last_full_section':290,
  'next_full_section':305,'numeric_endpoint':None,'cloud_published':False},ensure_ascii=False))
 if not args.apply:return
 for name,raw in docs.items():require(path(name).read_bytes()==raw,'document unchanged before apply '+name)
 check_map(tests['source_sha256_after'],'final pre-write necessary')
 archive.mkdir(parents=True)
 for name,raw in copies.items():
  with (archive/name).open('xb') as stream:stream.write(raw)
 with (archive/'archive-manifest.json').open('xb') as stream:stream.write(encode(manifest))
 for name,raw in mutations.items():
  dest=ROOT/name;dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb' if name=='verification/sections/293.json' else 'wb') as stream:stream.write(raw)
 print(json.dumps({'section':293,'local_closeout_written':True,'cloud_published':False,'next_section':294,'next_full_section':305}))

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--necessary-receipt',required=True);parser.add_argument('--window-receipt',required=True)
 parser.add_argument('--window-process-receipt',required=True)
 parser.add_argument('--main-window-receipt',default='verification/sections/293-main-window.json')
 parser.add_argument('--focus-receipt',default='verification/sections/293-main-window-focus.json')
 parser.add_argument('--apply',action='store_true');main(parser.parse_args())
