"""Unexecuted292 strict closeout revision2. Preview only unless root uses --apply.

Reads public actual receipts; never runs tests/Qt/game/chat, accesses private
state, restarts windows, publishes Git, or repeats/relables full290 as full292.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,re,struct,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'.cache/p3-292-closeout/revision2'
CANONICAL='scripts/verify_event_preview_filters_window_292.py'
TITLE='按流程场景和完整选项筛选事件固定作战资料'
FULL='verification/full-290/summary.json'
FULL_SHA='2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
MODULES=['tests.test_event_preview_filters_292','tests.test_node_catalog_view',
 'tests.test_peace_guardian_integration_291','tests.test_resident_reference_signals_291',
 'tests.test_choice_recruitment_integration_290','tests.test_original_entry_planning','tests.test_event_planning']
FIRST='verification/sections/292-necessary-first/'
FIRST_FILES={'process.json':'833b3ddce03b7b78d7a800adebf3e8a78a0c697f633de716b13f20e2d99f37d5',
 'stdout.txt':'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
 'stderr.txt':'34129d6309ed0a45e009d660d8df0ae3b7361b1a655ef487942e3316cbf5b51a'}

def require(value,message):
 if value is not True:raise ValueError('292 closeout prerequisite: '+message)
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
def selected_window_sources():
 names={CANONICAL,'rouge/app.py','rouge/node_catalog_view.py','rouge/node_catalog.py','rouge/event_planning.py',
  'rouge/player_node_information.py','rouge/ui_state.py','rouge/battle_preview.py','rouge/battle_view.py',
  'rouge/node_rewards.py','rouge/event_named_reward_links.py','rouge/data/node-catalog.json',
  'rouge/data/event-planning-reference.json','rouge/data/event-current-observation.json',
  'rouge/data/battle-previews.json','rouge/data/battle-node-pools.json','rouge/data/node-reward-reference.json',
  'rouge/data/view-catalog.json','tests/test_event_preview_filters_292.py'}
 image=load('rouge/data/battle-previews.json')['stages']['ro6_e_t_3']['image'];names.add('rouge/data/'+image['file'])
 require(len(names)==20 and digest('rouge/data/'+image['file'])==image['sha256'],'exact20 selected sources including real preview image')
 return names
def expected_necessary_sources():
 paths=set(ROOT.glob('rouge/**/*.py'))|set(ROOT.glob('rouge/data/*.json'))
 paths|={ROOT/('tests/'+module.split('.')[-1]+'.py') for module in MODULES}
 paths|={ROOT/CANONICAL,ROOT/'verification/sections/292-preparation/before-node_catalog_view.py'}
 paths|={ROOT/name for name in selected_window_sources() if 'battle-maps/' in name}
 return {p.relative_to(ROOT).as_posix() for p in paths if p.is_file()}
def first_failure():
 for name,expected in FIRST_FILES.items():require(digest(FIRST+name)==expected,'first actual failure original '+name)
 record=load(FIRST+'process.json');log=path(FIRST+'stderr.txt').read_text(encoding='utf-8')
 require(record['section']==292 and record['exit_code']==1 and record['source_unchanged'] is True
  and record['source_sha256_before']==record['source_sha256_after'],'unchanged original actual failed run')
 require(re.findall(r'Ran (\d+) tests in',log)==['79'] and 'FAILED (failures=3, errors=3)' in log,
  'original actual79/3F3E kept, never overwritten or converted to pass')
 return record,{'receipt':FIRST+'process.json','sha256':FIRST_FILES['process.json'],'stderr_sha256':FIRST_FILES['stderr.txt'],
  'actual_exit':1,'actual_tests_run':79,'failures':3,'errors':3,'failure_originals_preserved':True}
def necessary(value,parent,first):
 data=load(value)
 require(data['section']==292 and data['kind']=='necessary_change_related_tests_not_full_suite'
  and type(data['exit_code']) is int and data['exit_code']==0 and data['source_unchanged'] is True
  and data['source_sha256_before']==data['source_sha256_after'],'final actual necessary0 with stable source')
 require(data['modules']==MODULES and data['argv'][1:7]==['-B','-X','utf8','-m','unittest','-v']
  and data['argv'][-len(MODULES):]==MODULES and data['source_commit_before']==parent,'complete actual final necessary module argv and current parent')
 require(data['game_sampling_verified'] is False and data['chat_verified'] is False
  and data['full_scope_reduced'] is False and data['full_suite_rerun'] is False,'necessary only, no integration/full claims')
 require(set(data['source_sha256_after'])==expected_necessary_sources(),'exact public necessary producer scope, no private paths')
 check_map(data['source_sha256_after'],'final necessary')
 baseline=first['source_sha256_after']
 unchanged={name:expected for name,expected in baseline.items() if name.startswith('rouge/') and name!='rouge/node_catalog_view.py'}
 require(all(data['source_sha256_after'].get(name)==expected for name,expected in unchanged.items()),
  'all first-run production engine/data bytes preserved except intended UI module')
 audit=load('verification/sections/292-preparation/existing-backend-capability-audit.json')
 for name,expected in audit['source_sha256'].items():
  if name.startswith('rouge/') and name!='rouge/node_catalog_view.py':require(digest(name)==expected,'existing engine/source semantics unchanged '+name)
 logpath=path(value).with_name('stderr.txt');log=path(logpath).read_text(encoding='utf-8')
 counts=re.findall(r'Ran (\d+) tests in ([0-9.]+)s',log)
 require(len(counts)==1 and int(counts[0][0])>0 and log.rstrip().endswith('OK') and not re.search(r'^(FAIL|ERROR):',log,re.M),
  'final actual complete Ran/OK, no prefilled N')
 return data,{'receipt':rel(value),'sha256':digest(value),'stderr':rel(logpath),'stderr_sha256':digest(logpath),
  'actual_exit':0,'methods_run':int(counts[0][0]),'seconds':float(counts[0][1]),'source_unchanged':True,
  'source_files':len(data['source_sha256_after']),'modules':MODULES,'unchanged_non_UI_production_files':len(unchanged)}
def owned_process(value,window_value,window):
 process=load(value);child=process['child_argv']
 require(len(child)==9 and Path(child[0]).resolve()==(ROOT/'.venv/Scripts/python.exe').resolve()
  and child[1:4]==['-B','-X','utf8'] and Path(child[4]).resolve()==(ROOT/CANONICAL).resolve()
  and child[5]=='--receipt' and child[7:]==['--visible-ms','30000'],'canonical actual child argv, not a cache or synthetic result')
 raw=Path(child[6]);require(raw.is_absolute() and raw.name==path(window_value).name,'raw/public receipt basename preserved')
 require(process['section']==292 and process['kind']=='actual_native_window_owned_process_execution'
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
def native(value,process_value,necessary_data):
 data=load(value)
 require(data['section']==292 and data['kind']=='isolated_native_windows_event_preview_filters' and data['passed'] is True
  and data['failure'] is None and data['qpa']=='windows' and type(data['qt_exit_code']) is int and data['qt_exit_code']==0 and data['verification_window_closed'] is True,
  'actual canonical native Windows/UI/Qt completion')
 require(type(data['process_id']) is int and data['process_id']>0,'actual fixture PID separately positive')
 required={'native_windows_QPA','actual_client_size_exact_1050x720','new_filter_visible_inside_1050x720',
  'new_scene_and_choice_filters_share_one_horizontal_row','same_title_options_remain_three_distinct_complete_keys',
  'same_title_nonbattle_options_have_no_borrowed_preview','exact_016_filtered_scene_choice_stage_token',
  'same_event_refresh_retains_filters_full_stage_token_readers_search_scroll_and_selection',
  'ordinary_option_preserves_ordinary_and_emergency_alternatives','actual_button_emits_exact_manual_fixed_stage_once',
  'actual_button_opens_correct_fixed_battle_preview','return_from_fixed_preview_preserves_event_filter_and_reading_state',
  'emergency_only_option_never_includes_ordinary_variant','stale_complete_origin_token_revalidated_before_click_without_emission',
  'nonbattle_option_empty_and_disabled_not_event_fallback','final_event_change_resets_both_filters',
  'real_nonzero_scroll_and_document_search_selections','manual_UI_preview_never_changes_temporary_run_memory'}
 checks=data['checks'];require(len(checks)==len(set(checks))==data['unique_checks'] and required<=set(checks)
  and data['successful_assertion_executions_including_repeated_guards']>=len(checks),'all meaningful UI behaviors and actual counts')
 require(data['source_sha256_before']==data['source_sha256_after'] and set(data['source_sha256_after'])==selected_window_sources()
  and data['source_guard_is_selected_not_all_transitive_dependencies'] is True,'exact selected20 native scope stable, not all dependencies')
 check_map(data['source_sha256_after'],'final native')
 require(all(necessary_data['source_sha256_after'][name]==expected for name,expected in data['source_sha256_after'].items()),'same final actual necessary/native bytes')
 require(data['temporary_state_root'] is True and data['state_paths_replaced_before_constructor']==['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE']
  and data['private_state_read_copied_or_restored'] is False and data['external_entrypoints_blocked_before_original_call'] is True,
  'four temporary paths before constructor and original external blocking')
 attempts=data['external_operation_attempts']
 require(set(attempts)=={'game_enumeration','game_connect','game_capture','game_next_frame','desktop_start','desktop_request','provider_chat','credential_read'}
  and all(type(value) is int and value==0 for value in attempts.values()),'all eight original external attempts zero')
 require(data['game_operated'] is False and data['game_captures']==0 and data['chat_sent'] is False and data['chat_attempted'] is False
  and data['original_project_window_operated_or_restarted'] is False,'no game/chat/private/original window operations')
 raw,process_ref=owned_process(process_value,value,data)
 require(data['requested_client_size']==[1050,720] and bool(data['native_observations']),'actual one-size new UI observation')
 handles=[]
 for handle in data['native_observations']:
  require(handle['process_id']==data['process_id'] and handle['qpa']=='windows' and handle['client_size']==[1050,720]
   and type(handle['hwnd']) is int and handle['hwnd']>0,'actual own HWND/PID/exact client size');handles.append(handle['hwnd'])
 images=data['screenshots'];require(data['screenshot_count']==len(images)==4
  and {i['name'] for i in images}=={'same-event-retained','ordinary-dual-reference','fixed-preview-opened','nonbattle-option-empty'},'four actual distinct own-window flow PNGs')
 for image in images:
  expected=raw.with_name(raw.stem+'-'+image['name']+'.png')
  require(Path(image['path']).resolve()==expected.resolve(),'unaltered raw PNG sibling provenance')
  archived=path(value).with_name(expected.name);pixels=path(archived).read_bytes()
  require(sha256(pixels).hexdigest()==image['sha256'] and pixels[:8]==b'\x89PNG\r\n\x1a\n' and len(pixels)>24
   and all(n>0 for n in struct.unpack('>II',pixels[16:24])),'exact public archived native PNG bytes')
  handle=image['native_window'];require(handle['process_id']==data['process_id'] and handle['client_size']==[1050,720]
   and handle['qpa']=='windows','every PNG same actual fixture PID and size');handles.append(handle['hwnd'])
 require(len(set(handles))==1 and handles[0]>0,'one native fixture HWND for flow and all four actual images')
 require(len(data['public_observations'])==1 and data['public_observations'][0]['manual_stage_requests']==['ro6_e_t_3']
  and data['public_observations'][0]['actual_game_transition'] is None
  and data['public_observations'][0]['actual_choice_executed'] is None,'only explicit fixed preview; no real event execution inferred')
 return data,{'receipt':rel(value),'sha256':digest(value),'source_selected_files':20,'source_unchanged':True,
  'unique_checks':len(checks),'actual_assertion_executions':data['successful_assertion_executions_including_repeated_guards'],
  'actual_client_size':[1050,720],'screenshots':len(images),'actual_Qt_exit':0,'actual_window_closed':True,
  'images_visually_reviewed_by_helper':False,'owned_process':process_ref,'game_or_chat_verified':False}
def original_window(main_value,focus_value,fixture,necessary_data,necessary_value,native_value):
 main,focus=load(main_value),load(focus_value)
 require(path(main_value).resolve()==(ROOT/'verification/sections/292-main-window.json').resolve()
  and path(focus_value).resolve()==(ROOT/'verification/sections/292-main-window-focus.json').resolve(),
  'strict same-section canonical292 main/focus receipt paths')
 require(main['section']==292 and focus['section']==292
  and main['necessary_receipt_sha256']==digest(necessary_value)
  and main['native_receipt_sha256']==digest(native_value)
  and main['native_receipt']==rel(native_value) and main['necessary_receipt']==rel(necessary_value)
  and focus['main_receipt_sha256']==digest(main_value),
  'actual292 main binds both final evidence receipts; focus binds exact same main bytes')
 require(main['source_sha256_before']==main['source_sha256_after']==fixture['source_sha256_after']
  and set(main['source_sha256_after'])==selected_window_sources(),
  'same final actual native20 source map stable through original window restart')
 check_map(main['source_sha256_after'],'original292 window final native20 sources')
 timestamps={name:datetime.fromisoformat(value.replace('Z','+00:00')) for name,value in {
  'started':main['started_utc'],'finished':main['finished_utc'],'focus':focus['at_utc'],
  'necessary_finished':necessary_data['finished_utc'],'native_finished':fixture['finished_at']}.items()}
 require(all(value.tzinfo is not None and value.utcoffset() is not None for value in timestamps.values()),
  'actual main/focus/final-check timestamps are timezone-aware')
 require(timestamps['started']>timestamps['necessary_finished'] and timestamps['started']>timestamps['native_finished']
  and timestamps['finished']>=timestamps['started'] and timestamps['focus']>=timestamps['finished'],
  'original292 restart occurs after both final validations; focus follows completed main receipt')
 require(main['passed'] is True and main['private_file_hash_comparison_count']==5 and main['private_hashes_equal'] is True
  and main['changed_private_paths']==[] and main['private_contents_parsed_copied_or_restored'] is False and main['no_private_restoration'] is True,
  'actual original-window update/private5 hash unchanged, no content parsing/copy/restore')
 require(len(main['visible_windows'])==1,'one visible original project window');visible=main['visible_windows'][0]
 require(visible['visible'] is True and visible['responding'] is True and visible['minimized'] is False and visible['hwnd']>0
  and visible['pid']!=fixture['process_id'],'original window responsive/visible and not fixture')
 require(focus['visible'] is True and focus['pid']==visible['pid'] and focus['hwnd']==focus['actual_foreground']==visible['hwnd'],
  'actual foreground original project window')
 return {'receipt':rel(main_value),'sha256':digest(main_value),'focus_receipt':rel(focus_value),'focus_sha256':digest(focus_value),
  'section':292,'necessary_receipt_sha256':digest(necessary_value),'native_receipt_sha256':digest(native_value),
  'native20_current_source_unchanged':True,'started_after_final_necessary_and_native':True,'focus_after_main_finished':True,
  'private_hash_comparisons':5,'changed_private_paths':0,'visible_responsive_foreground':True,'private_contents_read_by_helper':False}
def main(args):
 require(Path(__file__).resolve()==(HERE/'close_section_292.py').resolve(),'reviewed canonical cache helper')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 require(branch=='codex/p2-development' and not (ROOT/'verification/sections/292.json').exists(),'authorized branch and exclusive new section receipt')
 first,first_ref=first_failure();tests,test_ref=necessary(args.necessary_receipt,parent,first)
 window,window_ref=native(args.window_receipt,args.window_process_receipt,tests)
 main_ref=original_window(args.main_window_receipt,args.focus_receipt,window,tests,args.necessary_receipt,args.window_receipt)
 full=load(FULL);require(digest(FULL)==FULL_SHA and full['after_section']==290 and full['available_checks_passed'] is True
  and full['scope_not_reduced'] is True and full['P2_complete'] is False and full['complete_repository_validation'] is False,
  'historical290 complete available scope preserved, never rerun/relabelled292')
 cp=load('DEVELOPMENT_CHECKPOINT.json')
 require(cp['completed_sections']==cp['latest_functional_section']==291 and cp['next_section']==292
  and cp['active_section']['section']==292 and cp['policy']['priority_order']==['P3','P2','P1']
  and cp['policy']['current_user_batch_target_section'] is None and cp['policy']['stop_after_section'] is None,
  'actual291→292 active continuation/P3 first/no numeric endpoint')
 require(cp['policy']['full_validation_anchor_section']==125 and cp['policy']['full_validation_interval']==15
  and cp['last_full_validation']['after_section']==290 and cp['current_available_full_validation']['section']==290
  and 125+((292-125)//15+1)*15==305,'original full290 pointers and next305 cadence')
 prior=cp['last_verified_cloud_save'];proof=load(prior['proof'])
 require(prior['section']==291 and digest(prior['proof'])==prior['proof_sha256'] and proof['passed'] is True
  and proof['commit']==proof['remote_HEAD']==prior['commit'] and proof['push_primary_exit']==0,'real prior291 ordinary publication proof')
 now=datetime.now(timezone(timedelta(hours=8))).isoformat()
 scope=('在节点资料页按完整流程场景和具体选项手动筛选既有固定作战资料；同名选项、普通/紧急及同关不同来源保持独立。'
  '同事件刷新与预览返回保留筛选、完整关卡来源和阅读状态；无作战或过期候选拒绝沿用。仅改阅读入口，不新增作战机制、资格或奖励判定。')
 limits=['原机制、数据与资格/费用引擎未改；10条未解析附注和25原场景/57原选项入口缺口不减少。',
  '已选场景、选项和固定关卡仅为资料筛选，不证明本局出现、按钮可选、真实选择或战斗发生。',
  '本节只必要检查与一尺寸新UI原生流程；290全量沿用其原来源，下次305，不称292新源全量通过。',
  '首轮79项3失败3错误原件保留；修复后N按实际最终回执，不与首轮或缓存准备重复相加。',
  'P3/P2/P1未完、识别最后；无路线推荐、排序或自动选路。符号链接1314/Linux-Wine/原私样本/游戏聊天不计通过。']
 changed=['rouge/node_catalog_view.py','tests/test_event_preview_filters_292.py',CANONICAL]
 receipt={'section':292,'kind':'functional_section','title':TITLE,'at_Beijing':now,'branch':branch,'prior_commit':parent,
  'remaining_item':'P3事件具体场景/选项的作战资料阅读入口','new_capability':scope,'files':changed,
  'source_sha256':{name:digest(name) for name in changed},'backend_mechanics_or_data_changed':False,
  'original_remaining_scenes':25,'original_remaining_choices':57,'existing_unparsed_annotations_not_closed':10,
  'necessary_validation':test_ref,'native_windows_validation':{**window_ref,'original_project_window':main_ref},
  'first_failed_necessary_run':first_ref,'full_validation':{'receipt':FULL,'sha256':FULL_SHA,'after_section':290,
    'full_suite_rerun':False,'new292_source_full_validation_claimed':False,'scope_not_reduced':True,
    'next_periodic_section':305,'complete_repository_validation':False},'limits':limits,'next_section':293,
  'cloud_publication_binding':'enclosing_commit','cloud_published':False,'P3_complete':False,'P2_complete':False}
 history='historical_before292_current_pointers';require(history not in cp,'exclusive old-current history')
 cp[history]={k:deepcopy(cp[k]) for k in ('current_section_save','current_section_validation','latest_section_environment','active_section','current_batch','cloud_publication_closeout') if k in cp}
 cp.pop('active_section',None);cp.pop('cloud_publication_closeout',None)
 cp.update(completed_sections=292,latest_functional_section=292,next_section=293,batch_status='P3_SECTION292_VALIDATED_AWAITING_PUBLICATION',
  next_full_validation_after=305,next_action='从293继续有证P3剩余事项，无连续数字终点；下次完整可用全量305。')
 cp['policy']['next_full_validation_after']=305;cp['current_batch_commit_policy']['next_full_validation_after']=305
 cp['current_batch'].update(status=cp['batch_status'],next_section=293,next_section_started=False,receipt='verification/sections/292.json',next_full_validation_after=305,batch_closed=False)
 cp['confirmed_next_stage_direction'].update(last_completed_functional_section=292,next_functional_section_started=False)
 cp['sections'].append({'number':292,'completion_ref':'p3-section-292','topic':TITLE,'verification':'verification/sections/292.json'})
 cp['current_section_save']={'section':292,'verification':'verification/sections/292.json','scope':'current_functional_section',
  'binding':'enclosing_commit','commit_reference':'commit containing292 UI source, necessary/native receipts, requirements and cloud index'}
 cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_section_validation']={'section':292,'receipt':'verification/sections/292.json','necessary_methods_passed':test_ref['methods_run'],
  'native_isolated_window_checks':window['unique_checks'],'full_suite_rerun':False,'last_full_receipt':FULL,'full_source_is_historical290':True}
 cp['latest_section_environment']={'section':292,'receipt':'verification/sections/292.json','native_windows':f"{test_ref['methods_run']} actual necessary; {window['unique_checks']} unique native UI checks at1050x720; original window visible/private5 unchanged",
  'native_game_or_chat_verified':False,'new_Linux_Wine_full_run':False,'current_section_full_rerun':False,'last_full_receipt':FULL}
 cp['functional_sections_since_latest_requirement']=list(dict.fromkeys([*cp['functional_sections_since_latest_requirement'],292]))
 docs={name:path(name).read_bytes() for name in ['DEVELOPMENT_CHECKPOINT.json','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','AGENTS.md']}
 completed=(f'## 功能第292节 · {TITLE}\n\n{now}。{scope}\n\n'
  f"最终实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}个唯一UI检查通过；实际1050×720、四图、固定预览/返回及非零阅读留存已核，原项目窗口更新且私人5路径hash不变。"
  '首轮79项3F3E原件保留，未改引擎/资料、未清10条附注或25/57原入口；不证明本局选择/战斗。'
  f'详见verification/sections/292.json，沿用{FULL}原冻结可用范围，不重跑/冒称292全量。后续293、下次305；P3/P2/P1未完、识别最后，无数字终点。待普通推送核对。\n\n')
 mutations={'verification/sections/292.json':encode(receipt),'DEVELOPMENT_CHECKPOINT.json':encode(cp),
  'PROJECT_COMPLETED.md':completed.encode()+docs['PROJECT_COMPLETED.md']}
 wip=docs['WORK_IN_PROGRESS.md'].decode();require('## 功能第291节' in wip,'keep291 onward history')
 mutations['WORK_IN_PROGRESS.md']=(completed+wip[wip.index('## 功能第291节'):]).encode()
 progress=docs['PROJECT_PROGRESS.md'].decode();anchor='其余已绑定来源关系及原件明确目的地的实际可达、展示、跳转后状态与完整脚本；'
 require(progress.count(anchor)==1,'precise remaining-only event gap anchor')
 mutations['PROJECT_PROGRESS.md']=progress.replace(anchor,'10条未解析附注的结果/条件分类与来源核验；其余已绑定来源关系及原件明确目的地的真实可达、游戏内实际展示、跳转后状态与完整脚本；',1).encode()
 req=docs['PROJECT_REQUIREMENTS.md'].decode();a,b=req.index('<!-- current-delivery:start -->'),req.index('<!-- current-delivery:end -->')
 block=('<!-- current-delivery:start -->\n## 当前交付与续接 · 第292节\n\n2026-10-16继续P3，无数字终点。'+scope
  +f"最终实际{test_ref['methods_run']}必要检查和原生单尺寸{window['unique_checks']}个唯一UI检查通过，原窗口更新/私人5路径不变。"
  +'10条附注与25/57原入口不减；290全量保留原来源，下次305。P3→P2→P1、识别最后，不提供路线建议；待普通推送核对，源码/要求/回执/索引同提交。\n')
 mutations['PROJECT_REQUIREMENTS.md']=(req[:a]+block+req[b:]).encode()
 agents=docs['AGENTS.md'].decode();a,b=agents.index('## 当前续接 · 第291节'),agents.index('## 当前优先顺序与输出可读性')
 mutations['AGENTS.md']=(agents[:a]+'## 当前续接 · 第292节已完成功能与必要/原生验收\n\n'+scope
  +'来源与实际回执见verification/sections/292.json；首轮失败保留，10条附注/25与57原入口不减少，原窗口更新/私人5路径不变。'
  +'未跑292全量，290完整可用范围沿用原来源；下一节293/下次305，无数字终点。P3→P2→P1、识别最后，不推荐/排序/自动选路。'
  +'本节待普通推送并核对真实远端，源码/要求/验收/索引同提交。\n\n'+agents[b:]).encode()
 require('初次招募时即处于已进阶状态' in mutations['PROJECT_REQUIREMENTS.md'].decode()
  and '初次招募即处于已进阶状态' in mutations['AGENTS.md'].decode(),'keep verified terminology outside current block')
 require(all(str(i)+'.' in mutations['AGENTS.md'].decode().split('## 当前续接')[0] for i in range(1,6)),'keep highest-priority five requirements')
 archive=ROOT/'verification/sections/292-preparation/closeout-tools';require(not archive.exists(),'exclusive new public tool archive')
 copies={'close_section_292.py':path(HERE/'close_section_292.py').read_bytes(),'CONTRACT.md':path(HERE/'CONTRACT.md').read_bytes()}
 copies.update({'before-'+name:raw for name,raw in docs.items()})
 manifest={'kind':'SECTION292_PUBLIC_CLOSEOUT_TOOLS_NOT_PRIVATE_STATE','files':{name:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)} for name,raw in copies.items()},
  'private_contents_or_hash_lists_copied':False,'tests_GUI_game_chat_git_or_full_executed_by_helper':False}
 print(json.dumps({'gates_passed':True,'apply_requested':args.apply,'necessary_actual_methods':test_ref['methods_run'],
  'native_actual_unique_checks':window['unique_checks'],'planned_public_files':list(mutations),'full_rerun':False,'last_full_section':290,
  'next_full_section':305,'numeric_endpoint':None,'cloud_published':False},ensure_ascii=False))
 if not args.apply:return
 for name,raw in docs.items():require(path(name).read_bytes()==raw,'document unchanged before apply '+name)
 check_map(tests['source_sha256_after'],'final pre-write necessary')
 archive.mkdir(parents=True)
 for name,raw in copies.items():
  with (archive/name).open('xb') as f:f.write(raw)
 with (archive/'archive-manifest.json').open('xb') as f:f.write(encode(manifest))
 for name,raw in mutations.items():
  dest=ROOT/name;dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb' if name=='verification/sections/292.json' else 'wb') as f:f.write(raw)
 print(json.dumps({'section':292,'local_closeout_written':True,'cloud_published':False,'next_section':293,'next_full_section':305}))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--necessary-receipt',required=True);p.add_argument('--window-receipt',required=True)
 p.add_argument('--window-process-receipt',required=True)
 p.add_argument('--main-window-receipt',default='verification/sections/292-main-window.json')
 p.add_argument('--focus-receipt',default='verification/sections/292-main-window-focus.json')
 p.add_argument('--apply',action='store_true');main(p.parse_args())
