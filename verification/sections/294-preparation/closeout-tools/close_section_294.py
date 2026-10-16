"""Unexecuted294 strict closeout. Default preview; only --apply writes public closeout.

Does not run tests/Qt/windows/game/chat, read private contents or publish Git.
Historical full290 is reused at its actual source, not a new full294 result.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,re,struct,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'.cache/p3-294-closeout/revision2'
CANONICAL='scripts/verify_direct_map_window_294.py'
TITLE='生存习性与湖中魇的直接地格和固定途经点参考'
FULL='verification/full-290/summary.json'
FULL_SHA='2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
PACKET='research/p3-map-direct-checkpoints-294'
MANIFEST=PACKET+'/source-manifest.json'
MANIFEST_SHA='52e447bc1c616db021da9cad9c2cbc68a0a63849138cd7f9297b4ccc1b32c097'
COMPARISON=PACKET+'/build-receipt.json'
COMPARISON_SHA='25947432426d55cdae03ad126b32738c60d4a7650f6201250346da6ef0f8f8b9'
DATA='rouge/data/fixed-landmark-references.json'
DATA_SHA='63ec9488f8f905d2ced1a4e349413e9c92d78125b9f1c94c00293cafa4d348f5'
STAGES=('ro6_n_3_2','ro6_e_3_2','ro6_t_5','ro6_e_t_5')
SIZES=((1280,850),(1440,900),(1520,940))
MODULES=['tests.test_direct_landmark_294','tests.test_direct_landmark_mapping',
 'tests.test_direct_landmark_extension','tests.test_map_direct_continuation',
 'tests.test_direct_landmark_288','tests.test_player_tile_information_288']
OLD_PACKETS=('p3-map-direct-road-288','p3-map-direct-continuation','p3-direct-ground-expanded','p3-direct-ground-current')

def require(value,message):
 if value is not True:raise ValueError('294 closeout prerequisite: '+message)


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
  and child[5]=='--receipt' and child[7:]==['--visible-ms','60000'],'canonical actual child argv, not a cache or synthetic result')
 raw=Path(child[6]);require(raw.is_absolute() and raw.name==path(window_value).name,'raw/public receipt basename preserved')
 require(process['section']==294 and process['kind']=='actual_native_window_owned_process_execution'
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
 require(digest(MANIFEST)==MANIFEST_SHA and digest(COMPARISON)==COMPARISON_SHA and digest(DATA)==DATA_SHA,
  'actual fixed manifest, separately pinned derived comparison and runtime bytes')
 manifest=load(MANIFEST)
 expected={'AUTHOR_READINGS.json','BLIND_READINGS.json','REQUEST_MANIFEST.json','prior-direct-references.json',
  'prior-regular-projections.json','source-records.json','ro6_n_3_2.png','ro6_t_5.png',
  'level_rogue6_3-2.json','level_rogue6_t-5.json'}
 require(manifest['section']==294 and set(manifest['files'])==expected,'exact ten frozen original/prior public inputs')
 for name,row in manifest['files'].items():
  require(Path(name).name==name and digest(PACKET+'/'+name)==row['sha256']
   and path(PACKET+'/'+name).stat().st_size==row['bytes'],'exact frozen source member '+name)
 comparison=load(COMPARISON);runtime=load(DATA);prior=load(PACKET+'/prior-direct-references.json')
 accepted=[row for row in comparison['new_agreement_comparisons']if row['accepted_for_runtime']is True]
 require(comparison['new_requested_points']==len(comparison['new_agreement_comparisons'])==18
  and comparison['new_accepted_points']==len(accepted) and comparison['new_rejected_or_unknown_points']==18-len(accepted)
  and comparison['output_sha256']==DATA_SHA,'actual requested/accepted comparison rows and exact runtime output')
 require(all(runtime[group].get(key)==value for group in('references','stages')for key,value in prior[group].items()),
  'all old direct records and aliases preserved by value')
 require((len(prior['references']),len(prior['stages']),sum(len(row['points'])for row in prior['references'].values()))==(8,14,40),
  'original partial scope8/14/40')
 regular=load('rouge/data/battle-map-projections.json')
 require(path('rouge/data/battle-map-projections.json').read_bytes()==path(PACKET+'/prior-regular-projections.json').read_bytes()
  and (len(regular['calibrations']),len(regular['stages']))==(12,24),'whole regular12/24 bytes remain identical')
 stages=load('rouge/data/battle-previews.json')['stages']
 incomplete={key:value for key,value in stages.items()if key not in regular['stages']}
 require((len(incomplete),len({value['image']['sha256']for value in incomplete.values()}))==(81,59),
  'whole-map81/59 gaps are not closed by new direct points')
 expected_points={}
 for sid in STAGES:
  reference=runtime['stages'][sid]['reference']
  rows=[row for row in accepted if row['reference']==reference]
  points=[{'cell':{'row':row['row'],'col':row['col']},'source_pixel':row['observed_pixel']}for row in rows]
  actual=[{'cell':{'row':row['row'],'col':row['col']},'source_pixel':row['observed_pixel']}
   for row in runtime['references'][reference]['points']]
  require(bool(points)and actual==points,'exact accepted points for independently bound alias '+sid)
  expected_points[sid]=points
 require(comparison['absolute_position_accuracy_verified']is False and comparison['complete_calibration_added']==0
  and comparison['source_pixel_adjustments_after_comparison']==0 and comparison['inverse_cell_assignment']is False
  and comparison['checkpoint_connections']is False,'reference agreement is not live accuracy or a fitted/connected map')
 process_path='verification/sections/294-preparation/source-build-first-process.json';process=load(process_path)
 require(process['exit_code']==0 and process['source_before']==process['source_after'],
  'actual original pure-source builder0 without source writes')
 require(digest('verification/sections/294-preparation/source-build-first-builder.py')
  ==digest('scripts/extend_direct_landmark_294.py'),'actual original builder bytes retained')
 return {'manifest':MANIFEST,'manifest_sha256':MANIFEST_SHA,'actual_comparison_receipt':COMPARISON,
  'actual_comparison_sha256':COMPARISON_SHA,'actual_new_accepted_source_points':len(accepted),
  'runtime_sha256':DATA_SHA,'expected_points':expected_points,'old_direct_points_preserved':40,
  'total_partial_images':len(runtime['references']),'total_partial_stage_bindings':len(runtime['stages']),
  'total_partial_points':sum(len(row['points'])for row in runtime['references'].values()),
  'regular_image_stage_scope_preserved':[12,24],'remaining_whole_map_stage_image_gaps':[81,59],
  'source_builder_receipt':process_path,'source_builder_sha256':digest(process_path),
  'source_readers':'Two isolated-context agents; not human or live-game observations.',
  'absolute_game_position_accuracy_verified':False}
def selected_window_sources():
 names={CANONICAL,'rouge/app.py','rouge/battle_preview.py','rouge/battle_view.py',
  'rouge/map_projection.py','rouge/fixed_landmark_mapping.py','rouge/player_tile_information.py',
  'rouge/branch_choice.py','rouge/branch_reference_view.py','rouge/spawn_reference.py','rouge/ui_state.py',
  'rouge/data/battle-previews.json',DATA,'rouge/data/battle-map-projections.json',
  'scripts/extend_direct_landmark_294.py','tests/test_direct_landmark_294.py',COMPARISON}
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file())
 stages=load('rouge/data/battle-previews.json')['stages']
 names.update('rouge/data/'+stages[sid]['image']['file']for sid in STAGES)
 return names
def expected_necessary_sources():
 paths=set(ROOT.glob('rouge/**/*.py'))|set(ROOT.glob('rouge/data/*.json'))
 paths|={ROOT/('tests/'+module.split('.')[-1]+'.py')for module in MODULES}
 paths|={ROOT/CANONICAL,ROOT/'scripts/extend_direct_landmark_294.py'}
 for name in('p3-map-direct-checkpoints-294',*OLD_PACKETS):
  paths|={p for p in(ROOT/'research'/name).rglob('*')if p.is_file()}
 stages=load('rouge/data/battle-previews.json')['stages']
 paths|={ROOT/'rouge/data'/stages[sid]['image']['file']for sid in STAGES}
 return{p.relative_to(ROOT).as_posix()for p in paths}
def unchanged_existing_sources(data):
 previous=load('verification/sections/293.json');reference=previous['necessary_validation']
 require(digest(reference['receipt'])==reference['sha256'],'published293 actual necessary receipt')
 original=load(reference['receipt'])
 require(original['section']==293 and original['exit_code']==0 and original['source_unchanged']is True
  and original['source_sha256_before']==original['source_sha256_after'],'original293 actual stable source map')
 old={name:expected for name,expected in original['source_sha256_after'].items()
  if name.startswith('rouge/')and name!=DATA and(name.endswith('.py')or(name.startswith('rouge/data/')and name.endswith('.json')))}
 require(bool(old)and all(data['source_sha256_after'].get(name)==expected for name,expected in old.items()),
  'all prior production Python/staticJSON unchanged except intended direct-reference data')
 require(original['source_sha256_after'][DATA]==digest(PACKET+'/prior-direct-references.json'),
  'actual pre294 fixed-reference bytes preserved as pinned prior')
 return {'previous_section':293,'previous_necessary_receipt':reference['receipt'],
  'previous_necessary_sha256':reference['sha256'],'unchanged_existing_Python_static_JSON_files':len(old),
  'only_existing_production_file_changed':DATA,
  'old_research_or_image_sources_not_in_current_producer_are_not_required_or_filled_into_current_map':True}
def necessary(value,parent):
 data=load(value)
 require(data['section']==294 and data['kind']=='necessary_change_related_tests_not_full_suite'
  and type(data['exit_code'])is int and data['exit_code']==0 and data['source_unchanged']is True
  and data['source_sha256_before']==data['source_sha256_after'],'actual final necessary0/source stable')
 require(data['modules']==MODULES and data['argv'][1:7]==['-B','-X','utf8','-m','unittest','-v']
  and data['argv'][-len(MODULES):]==MODULES and data['source_commit_before']==parent,
  'complete actual six-module argv/current parent')
 require(data['game_sampling_verified']is False and data['chat_verified']is False
  and data['full_scope_reduced']is False and data['full_suite_rerun']is False,'necessary-only boundaries')
 require(set(data['source_sha256_after'])==expected_necessary_sources(),'actual necessary producer source scope')
 check_map(data['source_sha256_after'],'final necessary')
 baseline=unchanged_existing_sources(data)
 logpath=path(value).with_name('stderr.txt');log=path(logpath).read_text(encoding='utf-8')
 counts=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',log)
 require(len(counts)==1 and int(counts[0][0])>0 and log.rstrip().endswith('OK')
  and not re.search(r'^(FAIL|ERROR):',log,re.M),'actual final Ran/OK, N never prefilled')
 return data,{'receipt':rel(value),'sha256':digest(value),'stderr':rel(logpath),'stderr_sha256':digest(logpath),
  'stdout_sha256':digest(path(value).with_name('stdout.txt')),'actual_exit':0,'methods_run':int(counts[0][0]),
  'seconds':float(counts[0][1]),'source_unchanged':True,'source_files':len(data['source_sha256_after']),
  'modules':MODULES,'new_author_methods_are_subset_not_added_again':True,'existing_source_boundary':baseline}
def native(value,process_value,necessary_data,source):
 data=load(value)
 require(data['section']==294 and data['kind']=='isolated_native_windows_direct_map_checkpoints'
  and data['passed']is True and data['failure']is None and data['qpa']=='windows'
  and type(data['qt_exit_code'])is int and data['qt_exit_code']==0 and data['verification_window_closed']is True,
  'actual native Windows/Qt complete close')
 require(type(data['process_id'])is int and data['process_id']>0,'actual fixture PID positive independently')
 required={'actual_native_windows_QPA','actual_owned_native_HWND_visible','actual_HWND_owned_by_fixture_and_not_minimized',
  'actual_logical_client_size_equals_requested','actual_direct_center_projection_available',
  'right_original_direct_reference_disables_segments','all_runtime_points_equal_actual_accepted_source_rows',
  'accepted_logical_cell_maps_exact_source_center','actual_widget_scales_source_center_at_each_size',
  'fractional_cells_do_not_interpolate','source_and_widget_pixel_inverse_remain_unknown',
  'real_main_fixed_SPAWN_row_has_new_accepted_MOVE_checkpoint','actual_QTest_grid_click_emits_exact_logical_cell',
  'new_stage_initial_filters_explicitly_reset_to_all_fixed_references',
  'unfiltered_fixed_SPAWN_rows_match_exact_stage_source_ids',
  'selected_actual_candidate_filter_leaves_registered_nonspawn_manual_cell',
  'manual_known_ground_click_maps_to_matching_original_reference','real_original_image_click_does_not_invent_inverse_cell',
  'unknown_manual_grid_cell_clears_original_marker_and_stays_unmapped','actual_list_click_selects_exact_main_fixed_SPAWN_row',
  'selected_fixed_route_contains_exact_new_MOVE_cell','selected_MOVE_checkpoint_has_original_map_point',
  'MOVE_overlay_before_after_has_identical_widget_image_and_layout_geometry',
  'MOVE_negative_drawing_fixture_restores_exact_selected_object_and_all_selection_state',
  'same_geometry_native_pixels_add_yellow_MOVE_point_beyond_source_background',
  'same_size_refresh_preserves_options_row_ordinal_reading_selection_and_scroll',
  'resize_preserves_selected_options_row_ordinal_text_and_selections','real_nonzero_scroll_and_nonempty_selections',
  'all_four_actual_stage_images_saved','manual_fixed_map_reading_does_not_change_temporary_run_memory'}
 checks=data['checks']
 require(len(checks)==len(set(checks))==data['unique_checks']and required<=set(checks)
  and data['successful_assertion_executions_including_repeated_guards']>=len(checks),'actual meaningful native checks/counts')
 selected=selected_window_sources()
 require(data['source_sha256_before']==data['source_sha256_after']and set(data['source_sha256_after'])==selected
  and data['source_guard_is_selected_not_all_transitive_dependencies']is True,'exact selected native source scope stable')
 check_map(data['source_sha256_after'],'final native')
 require(all(necessary_data['source_sha256_after'].get(name)==expected for name,expected in data['source_sha256_after'].items()),
  'actual native is exact same-byte necessary subset')
 require(data['temporary_state_root']is True and data['state_paths_replaced_before_constructor']==['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE']
  and data['private_state_read_copied_or_restored']is False and data['external_entrypoints_blocked_before_original_call']is True,
  'four isolated state paths before constructor and original external blocking')
 attempts=data['external_operation_attempts']
 require(set(attempts)=={'game_enumeration','game_connect','game_capture','game_next_frame','desktop_start','desktop_request','provider_chat','credential_read'}
  and all(type(n)is int and n==0 for n in attempts.values()),'all eight original external attempts zero')
 require(data['game_operated']is False and data['game_captures']==0 and data['chat_sent']is False
  and data['chat_attempted']is False and data['original_project_window_operated_or_restarted']is False,
  'no game/chat/private/original-window operations')
 require(data['owned_supervisor_exit_and_cleanup_required_separately']is True
  and data['actual_process_termination_verified_by_this_script']is False
  and data['launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID']is True,'no invented PID equality or natural cleanup')
 raw,process_ref=owned_process(process_value,value,data)
 require(data['expected_stage_ids']==list(STAGES)and data['requested_logical_sizes']==[list(size)for size in SIZES]
  and data['accepted_point_source']==COMPARISON and data['actual_accepted_source_points']==source['actual_new_accepted_source_points']
  and data['prior_direct_points_preserved']==40 and data['regular_image_and_stage_scope_preserved']==[12,24]
  and data['remaining_full_map_stage_and_image_gaps']==[81,59],'native declared actual source/partial/full scope boundaries')
 observations=data['stage_observations'];require(len(observations)==data['screenshot_count']==4
  and [row['stage_id']for row in observations]==list(STAGES),'four actual ordered aliases and four PNGs only')
 stages=load('rouge/data/battle-previews.json')['stages'];handles=set()
 def handle(row,size):
  require(row['qpa']=='windows'and row['process_id']==data['process_id']and type(row['hwnd'])is int and row['hwnd']>0
   and row['client_size']==list(size),'actual own HWND/PID/exact requested client size')
  handles.add(row['hwnd'])
 for row in observations:
  sid=row['stage_id'];points=source['expected_points'][sid];known={(p['cell']['row'],p['cell']['col'])for p in points}
  require(len(row['sizes'])==3,'three actual size observations for each alias')
  for observed,size in zip(row['sizes'],SIZES):
   require(observed['requested_size']==list(size)and observed['same_size_refresh_preserved']is True,
    'each actual size and same-size refresh completed')
   handle(observed['native_window'],size)
   require([{'cell':p['cell'],'source_pixel':p['source_pixel']}for p in observed['mapped_accepted_points']]==points
    and all(type(p['widget_pixel'])is list and len(p['widget_pixel'])==2 for p in observed['mapped_accepted_points']),
    'every actual size maps all accepted source points, without inverse/plane extrapolation')
  handle(row['native_window'],SIZES[-1])
  expected=raw.with_name(raw.stem+'-'+sid+'.png');require(Path(row['screenshot']).resolve()==expected.resolve(),'unaltered actual PNG raw provenance')
  archived=path(value).with_name(expected.name);pixels=path(archived).read_bytes()
  require(sha256(pixels).hexdigest()==row['screenshot_sha256']and pixels[:8]==b'\x89PNG\r\n\x1a\n'
   and len(pixels)>24 and all(n>0 for n in struct.unpack('>II',pixels[16:24])),'exact public archived native PNG bytes')
  move=row['new_MOVE_cell'];require((move['row'],move['col'])in known,'selected MOVE cell belongs to accepted source')
  stage=stages[sid];matches=[a['action']for w in stage['waves']for f in w['fragments']for a in f['actions']
   if a['id']==row['actual_selected_main_SPAWN_row_id']]
  require(len(matches)==1 and matches[0]['actionType']=='SPAWN'and type(matches[0]['routeIndex'])is int,
   'real selected row is a main fixed source SPAWN action')
  route=stage['routes'][matches[0]['routeIndex']]
  require(any(cp['type']=='MOVE'and cp.get('position')=={'row':len(stage['map'])-1-move['row'],'col':move['col']}
   for cp in route.get('checkpoints')or[]),'selected original route has the exact displayed MOVE checkpoint')
  require(row['MOVE_unchanged_geometry']is True and row['MOVE_geometry_before']==row['MOVE_geometry_after']
   and row['MOVE_geometry_before']['main_client_size']==list(SIZES[0]),'same geometry pixel-difference proof at first size')
  require(all(type(row[key])is int and row[key]>=0 for key in('MOVE_yellow_before','MOVE_yellow_after','MOVE_added_yellow_pixels'))
   and 0<row['MOVE_added_yellow_pixels']<=row['MOVE_yellow_after'],'actual yellow-after minus yellow-before has added pixels')
  require(row['right_original_supports_segments']is False and row['logical_grid_existing_route_lines_unchanged']is True
   and row['actual_enemy_position_or_route_activation']is None and row['inverse_or_full_calibration_claimed']is False,
   'no original-image segments, live position, inverse or whole-map completion inferred')
 require(len(handles)==1,'one actual fixture HWND through all four aliases/twelve sizes/four PNGs')
 return data,{'receipt':rel(value),'sha256':digest(value),'source_selected_files':len(selected),'source_unchanged':True,
  'unique_checks':len(checks),'actual_assertion_executions':data['successful_assertion_executions_including_repeated_guards'],
  'stage_ids':list(STAGES),'actual_sizes_per_stage':[list(size)for size in SIZES],'actual_size_observations':12,
  'actual_PNGs':4,'MOVE_overlay_pixel_difference_checked_at':list(SIZES[0]),
  'coordinate_mapping_checked_at_all_three_sizes':True,'actual_Qt_exit':0,'actual_windows_closed':True,
  'images_visually_reviewed_by_helper':False,'owned_process':process_ref,'game_or_chat_verified':False}
def visual_review(window_value,window):
 review_path='verification/sections/294-preparation/root-visual-review.json';review=load(review_path)
 require(review['section']==294 and review['kind']=='root_archived_native_images_review'
  and review['actual_images_opened_with_view_image']is True,'root actual visual review, not helper image inspection')
 expected={rel(path(window_value).with_name(Path(row['screenshot']).name)):row['screenshot_sha256']for row in window['stage_observations']}
 require(review['images']==expected and review['actual_image_count']==len(expected)==4,'root review binds exact four stage images')
 return {'receipt':review_path,'sha256':digest(review_path),'actual_root_reviewed_images':4,
  'helper_performed_visual_inspection':False,'not_twelve_size_screenshots':True}

def original_window(main_value,focus_value,fixture,necessary_data,necessary_value,native_value):
 main,focus=load(main_value),load(focus_value)
 require(path(main_value).resolve()==(ROOT/'verification/sections/294-main-window.json').resolve()
  and path(focus_value).resolve()==(ROOT/'verification/sections/294-main-window-focus.json').resolve(),
  'strict same-section canonical294 main/focus receipt paths')
 require(main['section']==294 and focus['section']==294
  and main['necessary_receipt_sha256']==digest(necessary_value)
  and main['native_receipt_sha256']==digest(native_value)
  and main['native_receipt']==rel(native_value) and main['necessary_receipt']==rel(necessary_value)
  and focus['main_receipt_sha256']==digest(main_value),
  'actual294 main binds both final evidence receipts; focus binds exact same main bytes')
 require(main['source_sha256_before']==main['source_sha256_after']==fixture['source_sha256_after']
  and set(main['source_sha256_after'])==selected_window_sources(),
  'same final actual native_selected source map stable through original window restart')
 check_map(main['source_sha256_after'],'original294 window final native_selected sources')
 timestamps={name:datetime.fromisoformat(value.replace('Z','+00:00')) for name,value in {
  'started':main['started_utc'],'finished':main['finished_utc'],'focus':focus['at_utc'],
  'necessary_finished':necessary_data['finished_utc'],'native_finished':fixture['finished_at']}.items()}
 require(all(value.tzinfo is not None and value.utcoffset() is not None for value in timestamps.values()),
  'actual main/focus/final-check timestamps are timezone-aware')
 require(timestamps['started']>timestamps['necessary_finished'] and timestamps['started']>timestamps['native_finished']
  and timestamps['finished']>=timestamps['started'] and timestamps['focus']>=timestamps['finished'],
  'original294 restart occurs after both final validations; focus follows completed main receipt')
 require(main['passed'] is True and main['private_file_hash_comparison_count']==5 and main['private_hashes_equal'] is True
  and main['changed_private_paths']==[] and main['private_contents_parsed_copied_or_restored'] is False and main['no_private_restoration'] is True,
  'actual original-window update/private5 hash unchanged, no content parsing/copy/restore')
 require(len(main['visible_windows'])==1,'one visible original project window');visible=main['visible_windows'][0]
 require(visible['visible'] is True and visible['responding'] is True and visible['minimized'] is False and visible['hwnd']>0
  and visible['pid']!=fixture['process_id'],'original window responsive/visible and not fixture')
 require(focus['visible'] is True and focus['pid']==visible['pid'] and focus['hwnd']==focus['actual_foreground']==visible['hwnd'],
  'actual foreground original project window')
 return {'receipt':rel(main_value),'sha256':digest(main_value),'focus_receipt':rel(focus_value),'focus_sha256':digest(focus_value),
  'section':294,'necessary_receipt_sha256':digest(necessary_value),'native_receipt_sha256':digest(native_value),
  'native_selected_current_source_unchanged':True,'started_after_final_necessary_and_native':True,'focus_after_main_finished':True,
  'private_hash_comparisons':5,'changed_private_paths':0,'visible_responsive_foreground':True,'private_contents_read_by_helper':False}




def failed_native_history():
 prefix='verification/sections/294-window-attempt1/'
 archive=load(prefix+'archive-manifest.json')
 require(archive['kind']=='294_EXACT_PUBLIC_NATIVE_ATTEMPT_OUTPUTS'and archive['attempt']==1
  and archive['original_actual_paths_preserved']is True and archive['private_state_copied']is False,
  'exact immutable first actual failed native archive')
 for name,row in archive['files'].items():
  require(not Path(name).is_absolute()and'..'not in Path(name).parts
   and digest(prefix+name)==row['sha256']and path(prefix+name).stat().st_size==row['bytes'],
   'preserved first native raw/tool bytes '+name)
 process=load(prefix+'process.json');supervisor=load(prefix+'supervisor.json');window=load(prefix+'actual/window.json')
 require(process['section']==294 and process['attempt']==1 and process['status']=='completed'
  and type(process['exit_code'])is int and process['exit_code']==1 and process['child_primary_exit']==1
  and process['timed_out']is False and process['owned_job_no_live_execution_verified']is True
  and process['source_before_after_unchanged']is True and process['window_receipt_passed']is False,
  'actual first supervisor/primary1, not timeout, cleanup complete, not converted to PASS')
 require(supervisor['status']=='completed'and supervisor['supervisor_exit']==1 and supervisor['child_primary_exit']==1
  and supervisor['owned_handle_retained']is True and supervisor['owned_job_assigned']is True
  and supervisor['owned_job_no_live_execution_verified']is True and supervisor['timed_out']is False,
  'first actual owned job was closed without claiming natural descendant exit')
 require(window['passed']is False and window['qt_exit_code']==1
  and window['failure']['message']=='real_main_fixed_SPAWN_row_has_new_accepted_MOVE_checkpoint'
  and window['source_sha256_before']==window['source_sha256_after']
  and digest(prefix+'actual/window.json')==process['window_receipt_sha256'],
  'actual original assertion failure and stable original source map retained')
 require(window['source_sha256_before'][CANONICAL]==digest(prefix+'execution-tools/window.py')
  =='1469bdf02a81b58d43f50436f8fbe4f434268ca07d551c8225eccb2820e77468',
  'first failure source bound to original rev2, not later live source')
 return {'process_receipt':prefix+'process.json','process_sha256':digest(prefix+'process.json'),
  'raw_window_receipt':prefix+'actual/window.json','raw_window_sha256':digest(prefix+'actual/window.json'),
  'archive_manifest':prefix+'archive-manifest.json','archive_manifest_sha256':digest(prefix+'archive-manifest.json'),
  'actual_supervisor_exit':1,'actual_primary_child_exit':1,'actual_Qt_exit':1,
  'source_before_after_unchanged':True,'owned_job_cleanup_empty':True,
  'original_failure':window['failure']['message'],'not_counted_as_final_passed_checks':True,
  'classification':'Fixture global START exclusion is impossible for lake accepted MOVE cells; source JSON counterexample and complete real-row subgroup selection repair. Stale filter alone is not claimed as the cause.',
  'current_final_sources_not_required_to_equal_the_failed_historical_source':True,
  'all_descendants_natural_exit_claimed':False}


def main(args):
 require(Path(__file__).resolve()==(HERE/'close_section_294.py').resolve(),'reviewed canonical cache helper')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 require(branch=='codex/p2-development'and not(ROOT/'verification/sections/294.json').exists(),'authorized branch/exclusive new receipt')
 failed=failed_native_history();source=packet();tests,test_ref=necessary(args.necessary_receipt,parent)
 window,window_ref=native(args.window_receipt,args.window_process_receipt,tests,source)
 window_ref['root_visual_review']=visual_review(args.window_receipt,window)
 main_ref=original_window(args.main_window_receipt,args.focus_receipt,window,tests,args.necessary_receipt,args.window_receipt)
 full=load(FULL)
 require(digest(FULL)==FULL_SHA and full['after_section']==290 and full['available_checks_passed']is True
  and full['scope_not_reduced']is True and full['P2_complete']is False and full['complete_repository_validation']is False,
  'historical290 actual available scope, not new294 full/source validation')
 cp=load('DEVELOPMENT_CHECKPOINT.json')
 require(cp['completed_sections']==cp['latest_functional_section']==293 and cp['next_section']==294
  and cp['active_section']['section']==294 and cp['policy']['priority_order']==['P3','P2','P1']
  and cp['policy']['current_user_batch_target_section']is None and cp['policy']['stop_after_section']is None,
  'real293 to active294, P3 first/no numeric endpoint')
 require(cp['policy']['full_validation_anchor_section']==125 and cp['policy']['full_validation_interval']==15
  and cp['last_full_validation']['after_section']==290 and cp['current_available_full_validation']['section']==290
  and 125+((294-125)//15+1)*15==305,'same full290 history and next305 cadence')
 prior=cp['last_verified_cloud_save'];proof=load(prior['proof'])
 require(prior['section']==293 and digest(prior['proof'])==prior['proof_sha256']and proof['passed']is True
  and proof['commit']==proof['remote_HEAD']==prior['commit']and proof['push_primary_exit']==0,'actual previous293 ordinary publication')
 now=datetime.now(timezone(timedelta(hours=8))).isoformat()
 scope=('为生存习性和湖中魇两张固定原图、普通/紧急四个关卡新增18个近似地面格中心；来源是两名隔离上下文代理对原图的独立读数，'
  '保留原18请求和逐项一致性比较，不平均或调整像素。通过实际左格点击与主固定出怪条目的MOVE途经点在原图显示，'
  '三个尺寸逐关核对缩放和阅读保留。只标已核格点，不据此连原图路线、反查、插值或宣称当前敌人位置。')
 limits=['原40点逐值保留，现合计10图18关58格仅为部分直接参考；常规12图24关整体投影未改，81关59图完整校准缺口不减少。',
  '两代理4像素以内读数一致不等于实机绝对精度；可能存在共同判断偏差，地面中心也不证明实际出生位置或运行中的路线激活。',
  '原图无连线；逻辑格图既有资料途经点连线保留，不能视作实际寻路或当前敌人路径。无路线推荐、排序、自动选路或概率。',
  '本节仅必要检查与真实Windows四关三尺寸、四PNG；不是12张尺寸截图。像素增量在同一部件/布局下核，不复用原图自带黄色。',
  '原生首轮验收被错误全局START排除前提阻断，原失败及rev2源码保留；修后完整四关重验，旧失败不计入最终通过数。',
  '仅fixed-landmark-references.json已有生产文件变化；其余既有Python/staticJSON和资格/本局机制未改，10/25/57入口缺口保留。',
  '290全量沿用原冻结来源，下次305，不冒称294新源全量。P3/P2/P1未完、识别最后；1314/Linux-Wine/原私样本/游戏聊天未计通过。']
 changed=sorted(load('verification/sections/294-preparation/promotion.json')['promoted'])
 require(set(changed)=={CANONICAL,'scripts/extend_direct_landmark_294.py','tests/test_direct_landmark_294.py',DATA,
  *(p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file())},'exact new functional source/packet file set')
 source_public={key:value for key,value in source.items()if key!='expected_points'}
 receipt={'section':294,'kind':'functional_section','title':TITLE,'at_Beijing':now,'branch':branch,'prior_commit':parent,
  'remaining_item':'P3固定战斗地图逐格中心与固定出怪途经点显示','new_capability':scope,'files':changed,
  'source_sha256':{name:digest(name)for name in changed},'source_reference':source_public,
  'existing_Python_engine_or_regular_calibration_or_eligibility_state_changed':False,'only_existing_production_file_changed':DATA,
  'partial_scope_before':[8,14,40],'partial_scope_after':[source['total_partial_images'],source['total_partial_stage_bindings'],source['total_partial_points']],
  'whole_map_stage_image_gaps_unchanged':[81,59],'regular_image_stage_scope_unchanged':[12,24],
  'necessary_validation':test_ref,'native_windows_validation':{**window_ref,'original_project_window':main_ref},
  'first_failed_native_validation':failed,
  'full_validation':{'receipt':FULL,'sha256':FULL_SHA,'after_section':290,'full_suite_rerun':False,
   'new294_source_full_validation_claimed':False,'scope_not_reduced':True,'next_periodic_section':305,'complete_repository_validation':False},
  'limits':limits,'next_section':295,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'P3_complete':False,'P2_complete':False}
 history='historical_before294_current_pointers';require(history not in cp,'exclusive previous pointers history')
 cp[history]={key:deepcopy(cp[key])for key in('current_section_save','current_section_validation','latest_section_environment',
  'active_section','current_batch','cloud_publication_closeout')if key in cp}
 cp.pop('active_section',None);cp.pop('cloud_publication_closeout',None)
 cp.update(completed_sections=294,latest_functional_section=294,next_section=295,
  batch_status='P3_SECTION294_VALIDATED_AWAITING_PUBLICATION',next_full_validation_after=305,
  next_action='从295继续有证P3剩余事项，无连续数字终点；下次完整可用全量305。')
 cp['policy']['next_full_validation_after']=305;cp['current_batch_commit_policy']['next_full_validation_after']=305
 cp['current_batch'].update(status=cp['batch_status'],next_section=295,next_section_started=False,
  receipt='verification/sections/294.json',next_full_validation_after=305,batch_closed=False)
 cp['confirmed_next_stage_direction'].update(last_completed_functional_section=294,next_functional_section_started=False)
 cp['sections'].append({'number':294,'completion_ref':'p3-section-294','topic':TITLE,'verification':'verification/sections/294.json'})
 cp['current_section_save']={'section':294,'verification':'verification/sections/294.json','scope':'current_functional_section',
  'binding':'enclosing_commit','commit_reference':'commit containing294 direct-point data/source packet, necessary/native receipts, requirements and cloud index'}
 cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_section_validation']={'section':294,'receipt':'verification/sections/294.json','necessary_methods_passed':test_ref['methods_run'],
  'native_isolated_window_checks':window['unique_checks'],'full_suite_rerun':False,'last_full_receipt':FULL,'full_source_is_historical290':True}
 cp['latest_section_environment']={'section':294,'receipt':'verification/sections/294.json',
  'native_windows':f"{test_ref['methods_run']} actual necessary; {window['unique_checks']} unique native checks, four stages/three exact sizes/four PNGs, original visible/private5 unchanged",
  'native_game_or_chat_verified':False,'new_Linux_Wine_full_run':False,'current_section_full_rerun':False,'last_full_receipt':FULL}
 cp['functional_sections_since_latest_requirement']=list(dict.fromkeys([*cp['functional_sections_since_latest_requirement'],294]))
 docs={name:path(name).read_bytes()for name in('DEVELOPMENT_CHECKPOINT.json','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md',
  'WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','AGENTS.md')}
 completed=(f'## 功能第294节 · {TITLE}\n\n{now}。{scope}\n\n'
  f"实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过；四关各三尺寸、四PNG，"
  '同几何MOVE像素增量、选中对象与阅读留存已核；原项目窗口更新、私人5路径hash不变。'
  '原生首轮验收前提失败原件与旧源码保留，修后完整重验且未将旧断言计入本轮通过数。'
  '原40点与常规12/24字节保留，部分参考合计10图18关58格；81关59图仍未完整校准。'
  f'来源及实际回执见verification/sections/294.json；沿用{FULL}原来源，不冒称294全量。'
  '后续295、下次305；P3/P2/P1未完、识别最后，无数字终点。待普通推送核对。\n\n')
 mutations={'verification/sections/294.json':encode(receipt),'DEVELOPMENT_CHECKPOINT.json':encode(cp),
  'PROJECT_COMPLETED.md':completed.encode()+docs['PROJECT_COMPLETED.md']}
 wip=docs['WORK_IN_PROGRESS.md'].decode();require('## 功能第293节'in wip,'keep293 onward history')
 mutations['WORK_IN_PROGRESS.md']=(completed+wip[wip.index('## 功能第293节'):]).encode()
 progress=docs['PROJECT_PROGRESS.md'].decode();anchor='其中8图/14关已有40格直接参考'
 require(progress.count(anchor)==1 and '81个关卡、59张独立原图'in progress,'precise old partial-only todo wording')
 require((source['total_partial_images'],source['total_partial_stage_bindings'],source['total_partial_points'])==(10,18,58),
  'actual partial totals agree with exact requested todo text')
 mutations['PROJECT_PROGRESS.md']=progress.replace(anchor,'其中10图/18关已有58格直接参考',1).encode()
 require('游戏内实际展示'in mutations['PROJECT_PROGRESS.md'].decode()and'10条未解析附注'in mutations['PROJECT_PROGRESS.md'].decode()
  and'整图仍未校准'in mutations['PROJECT_PROGRESS.md'].decode(),'all unrelated remaining gaps and whole-map unknown preserved')
 req=docs['PROJECT_REQUIREMENTS.md'].decode();a,b=req.index('<!-- current-delivery:start -->'),req.index('<!-- current-delivery:end -->')
 block=('<!-- current-delivery:start -->\n## 当前交付与续接 · 第294节\n\n2026-10-16继续P3，无数字终点。'+scope
  +f"最终实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过，原窗口更新/私人5路径不变。"
  +'部分直接参考现10图18关58格，常规12/24与81/59完整校准缺口保留；290全量沿用原来源，下次305。'
  +'P3→P2→P1、识别最后，不提供路线建议；待普通推送核对，源码/要求/回执/索引同提交。\n')
 mutations['PROJECT_REQUIREMENTS.md']=(req[:a]+block+req[b:]).encode()
 agents=docs['AGENTS.md'].decode();a,b=agents.index('## 当前续接 · 第293节'),agents.index('## 当前优先顺序与输出可读性')
 mutations['AGENTS.md']=(agents[:a]+'## 当前续接 · 第294节已完成功能与必要/原生验收\n\n'+scope
  +'来源及实际回执verification/sections/294.json；部分参考10图18关58格，不减少81/59整图缺口。'
  +'原项目窗口更新/私人5路径不变；未跑294全量，290完整可用范围沿用原来源。下一节295/下次305，无数字终点。'
  +'P3→P2→P1、识别最后，不推荐/排序/自动选路。本节待普通推送并核对真实远端，源码/要求/验收/索引同提交。\n\n'+agents[b:]).encode()
 require('初次招募时即处于已进阶状态'in mutations['PROJECT_REQUIREMENTS.md'].decode()
  and'初次招募即处于已进阶状态'in mutations['AGENTS.md'].decode(),'keep verified recruitment terminology')
 require(all(str(i)+'.'in mutations['AGENTS.md'].decode().split('## 当前续接')[0]for i in range(1,6)),'keep highest-priority five requirements')
 archive=ROOT/'verification/sections/294-preparation/closeout-tools';require(not archive.exists(),'exclusive public helper archive')
 copies={'close_section_294.py':path(HERE/'close_section_294.py').read_bytes(),'CONTRACT.md':path(HERE/'CONTRACT.md').read_bytes()}
 copies.update({'before-'+name:raw for name,raw in docs.items()})
 archive_manifest={'kind':'SECTION294_PUBLIC_CLOSEOUT_TOOLS_NOT_PRIVATE_STATE',
  'files':{name:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}for name,raw in copies.items()},
  'private_contents_or_hash_lists_copied':False,'tests_Qt_GUI_game_chat_Git_publish_or_full_executed_by_helper':False}
 print(json.dumps({'gates_passed':True,'apply_requested':args.apply,'necessary_actual_methods':test_ref['methods_run'],
  'native_actual_unique_checks':window['unique_checks'],'native_selected_source_files':len(selected_window_sources()),
  'planned_public_files':list(mutations),'full_rerun':False,'next_full_section':305,'numeric_endpoint':None,'cloud_published':False},ensure_ascii=False))
 if not args.apply:return
 for name,raw in docs.items():require(path(name).read_bytes()==raw,'public document unchanged before apply '+name)
 check_map(tests['source_sha256_after'],'final pre-write necessary source')
 archive.mkdir(parents=True)
 for name,raw in copies.items():
  with(archive/name).open('xb')as stream:stream.write(raw)
 with(archive/'archive-manifest.json').open('xb')as stream:stream.write(encode(archive_manifest))
 for name,raw in mutations.items():
  destination=ROOT/name;destination.parent.mkdir(parents=True,exist_ok=True)
  with destination.open('xb'if name=='verification/sections/294.json'else'wb')as stream:stream.write(raw)
 print(json.dumps({'section':294,'local_closeout_written':True,'cloud_published':False,'next_section':295,'next_full_section':305}))

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--necessary-receipt',required=True);parser.add_argument('--window-receipt',required=True)
 parser.add_argument('--window-process-receipt',required=True)
 parser.add_argument('--main-window-receipt',default='verification/sections/294-main-window.json')
 parser.add_argument('--focus-receipt',default='verification/sections/294-main-window-focus.json')
 parser.add_argument('--apply',action='store_true');main(parser.parse_args())
