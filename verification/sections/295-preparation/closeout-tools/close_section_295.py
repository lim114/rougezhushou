"""Unexecuted strict295 closeout. Preview by default; --apply writes public closeout.

No tests/Qt/game/chat/private contents/window restart/Git publication are run.
Historical full290 remains its actual source, not a new full295 execution.
"""
import argparse,ast
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,re,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'.cache/p3-295-closeout'
PARENT='e517095f388baad3aa7824dbd5b9dee6a68fb450'
TITLE='线人选项的沙盘α独立图标与完整物品说明'
CANONICAL='scripts/verify_documented_choice_item_window_295.py'
CANONICAL_SHA='a93e69365eef3032a20c9b65c90ea598990a590b357a9fc69f978a5ce7b10f89'
FULL='verification/full-290/summary.json'
FULL_SHA='2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
PACKET='research/p3-documented-choice-items-295'
MANIFEST=PACKET+'/source-manifest.json'
MANIFEST_SHA='e98f48e0629307f9fdbc98c8e6cb8ca4b6ffbe93e3939c3cf4d489ef476853e9'
DATA='rouge/data/documented-choice-items.json'
DATA_SHA='1c1049961ed87c0992e8f293cdd3ad131a951f770cb299469b9140278fa86c88'
SOURCE_BUILD=PACKET+'/source-build-receipt.json'
SOURCE_BUILD_SHA='2b81e0ab21b5ec6810701e66b48a791c2ec827643e1a0a0c5941f9b98e99504c'
BUILDER='scripts/build_documented_choice_items_295.py'
BASELINE='verification/sections/295-preparation/pre295-query-baseline.json'
BASELINE_SHA='50799b7758d235963e97f3c844211abcce9cfcb3caf5b3be16a69495a347bb27'
EVENT='community_group_021'
SCENE=EVENT+':scene:0'
CHOICE=SCENE+':choice:0'
ITEM='rogue_6_relic_final_1'
REFERENCE=CHOICE+':documented-item:'+ITEM
CHANGED_EXISTING={'rouge/player_node_information.py','rouge/node_catalog_view.py'}
PACKET_MEMBERS={PACKET+'/'+name for name in('original-records.json','prts-events-427904.html',
 'prts-events-440271.html','bwiki-investigation.html','extraction.json')}
PACKET_MEMBERS|={DATA,'rouge/data/node-catalog.json','rouge/data/relic-icons/'+ITEM+'.png'}
MODULES=['tests.test_documented_choice_items_295','tests.test_documented_choice_item_view_295',
 'tests.test_documented_item_integration_295','tests.test_event_named_reward_integration_289',
 'tests.test_event_named_reward_links_289','tests.test_node_rewards',
 'tests.test_player_node_information_286','tests.test_node_catalog_view']
PROGRESS_SHA_BEFORE='111962b1622515c494ae81a06ac19b915db797211e926165a9947b80fade8a0b'


def require(value,message):
 if value is not True:raise ValueError('295 closeout prerequisite: '+message)

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
 require(process['section']==295 and process['kind']=='actual_native_window_owned_process_execution'
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

"""Source fragment for cache-only strict295 closeout; never executed during preparation."""

def packet():
 require(digest(MANIFEST)==MANIFEST_SHA and digest(DATA)==DATA_SHA
  and digest(SOURCE_BUILD)==SOURCE_BUILD_SHA and digest(BASELINE)==BASELINE_SHA,
  'fixed documented-item packet, separately pinned derived construction and pre295 baseline')
 manifest=load(MANIFEST)
 require(manifest['section']==295 and set(manifest['files'])==PACKET_MEMBERS,'exact eight bound public source members')
 for name,expected in manifest['files'].items():
  require(path(name).stat().st_size==expected['bytes'] and digest(name)==expected['sha256'],'fixed member '+name)
 data=load(DATA);ref=data['reference'];item=data['item']
 require(data['schema_version']==1 and data['scope']=='documented_named_item_not_grant'
  and data['event_id']==EVENT and ref['reference_id']==REFERENCE
  and(ref['event_id'],ref['scene_key'],ref['choice_key'],ref['item_id'])==(EVENT,SCENE,CHOICE,ITEM)
  and(item['id'],item['iconId'],item['name'],item['type'])==(ITEM,ITEM,'沙盘α','RELIC'),
  'exact event/scene/choice/item, documented identity separate from typed grant')
 require(data['current_server_verified']is False and data['inventory_updated']is False
  and data['source_scene_link_verified']is False
  and all(data[name]is None for name in('actual_reward','actual_quantity','actual_selectable'))
  and all(ref[name]is None for name in('quantity_reference','actual_reward','actual_selectable'))
  and all(ref[name]is False for name in('source_scene_link_verified','original_item_pointer_present','original_choice_entry_bound')),
  'no quantity, source entry, actual grant, eligibility or inventory upgrade')
 require(data['expected_event']['scenes'][0]['choices'][0]['key']==CHOICE
  and data['expected_event']['scenes'][0]['choices'][0]['game_choice_ids']==[],
  'original community choice remains unmapped')
 original=load(PACKET+'/original-records.json')
 require(original['choice']['displayData']['itemId']is None and original['choice']['displayData']['type']=='NORMAL',
  'original typed pointer remains null and is not changed to a documented item')
 icon=ref['icon_reference']
 require(icon['file']=='rouge/data/relic-icons/'+ITEM+'.png'
  and icon['item_id']==icon['icon_id']==ITEM and digest(icon['file'])==icon['sha256']
  =='1d07a123253172ede9a4585abdcd1b301350e096b245bc046539c48f6c6fb825',
  'actual existing fixed icon identity and bytes')
 build=load(SOURCE_BUILD)
 require(build['status']=='SOURCE_RECONSTRUCTION_ONLY' and build['documented_item_count']==1
  and build['source_manifest_sha256']==MANIFEST_SHA and build['qt_or_tests_executed']is False
  and build['network_requests']==build['game_chat_private_operations']==0,
  'derived source-construction receipt is not a product or Qt pass')
 for name,expected in build['output_files'].items():
  require(digest(name)==expected['sha256']and path(name).stat().st_size==expected['bytes'],'actual builder output '+name)
 build_process='verification/sections/295-preparation/source-build-first/process.json'
 actual_build=load(build_process)
 require(type(actual_build['exit_code'])is int and actual_build['exit_code']==0
  and actual_build['scope']=='cache-only pure public source build, no product/Qt/test imports'
  and '--source-root'in actual_build['command']and '--output-dir'in actual_build['command'],
  'preserved actual pure-source builder execution0, not invented product validation')
 require(digest('verification/sections/295-preparation/source-build-first/original-builder.py')==digest(BUILDER)
  =='3714d0a5196b5b96fe2833f65cc6f2c9d210dbf27670b75335feffa9eb519b17',
  'actual preserved builder source matches formal builder')
 baseline=load(BASELINE)
 require(baseline['kind']=='ACTUAL_PRE295_PUBLIC_QUERY_AND_PLAYER_OUTPUT_NOT_TEST_PASS'
  and len(baseline['events'])==38 and baseline['node_catalog_sha256']==digest('rouge/node_catalog.py'),
  'actual pre295 full query/player snapshot, unchanged catalog module')
 require({row['revision']for row in data['sources']['documents']}=={'427904','440271','349818'},
  'fixed document versions, not current-server execution')
 return {'manifest':MANIFEST,'manifest_sha256':MANIFEST_SHA,'bound_members':len(manifest['files']),
  'runtime_data':DATA,'runtime_sha256':DATA_SHA,'source_build_receipt':SOURCE_BUILD,
  'source_build_sha256':SOURCE_BUILD_SHA,'source_build_is_not_product_test':True,
  'actual_source_build_process':build_process,'actual_source_build_process_sha256':digest(build_process),
  'actual_source_build_exit':0,
  'pre295_baseline':BASELINE,'pre295_baseline_sha256':BASELINE_SHA,'baseline_events':38,
  'reference_id':REFERENCE,'icon':icon['file'],'icon_sha256':icon['sha256'],
  'current_server_verified':False,'original_item_pointer_present':False,'original_choice_entry_bound':False,
  'quantity_reference':None,'actual_reward':None,'actual_selectable':None,'inventory_updated':False}


def selected_window_sources():
 module=ast.parse(path(CANONICAL).read_text(encoding='utf8'))
 fn=next(n for n in module.body if isinstance(n,ast.FunctionDef)and n.name=='bound_files')
 assignments=[n for n in fn.body if isinstance(n,ast.Assign)
  and any(isinstance(t,ast.Name)and t.id=='names'for t in n.targets)]
 require(len(assignments)==1 and isinstance(assignments[0].value,ast.Set),'native source literal set')
 values=assignments[0].value.elts;names=set()
 for value in values:
  if isinstance(value,ast.Name):
   require(value.id in('CANONICAL','MANIFEST'),'fixed native source constant')
   names.add(CANONICAL if value.id=='CANONICAL'else MANIFEST)
  else:
   require(isinstance(value,ast.Constant)and isinstance(value.value,str),'literal native selected path')
   names.add(value.value)
 names.update(load(MANIFEST)['files'])
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file())
 require(BASELINE in names and DATA in names and all('tests/'+m.split('.')[-1]+'.py'in names for m in MODULES),
  'baseline, runtime data and all eight necessary test sources included')
 return names


def expected_necessary_sources():
 paths=set(ROOT.glob('rouge/**/*.py'))|set(ROOT.glob('rouge/data/*.json'))
 paths|={ROOT/('tests/'+module.split('.')[-1]+'.py')for module in MODULES}
 paths|={ROOT/CANONICAL,ROOT/BUILDER,ROOT/BASELINE,ROOT/'rouge/data/relic-icons'/str(ITEM+'.png')}
 for name in('p3-documented-choice-items-295','p3-event-named-rewards-289'):
  paths|={p for p in(ROOT/'research'/name).rglob('*')if p.is_file()}
 return{p.relative_to(ROOT).as_posix()for p in paths}


def unchanged_existing_sources(data):
 previous=load('verification/sections/294.json');reference=previous['necessary_validation']
 require(digest(reference['receipt'])==reference['sha256'],'actual previous294 necessary reference')
 old=load(reference['receipt'])
 require(old['section']==294 and old['exit_code']==0 and old['source_unchanged']is True
  and old['source_sha256_before']==old['source_sha256_after'],'original294 stable actual source')
 unchanged={name:expected for name,expected in old['source_sha256_after'].items()
  if name.startswith('rouge/')and name not in CHANGED_EXISTING
  and(name.endswith('.py')or(name.startswith('rouge/data/')and name.endswith('.json')))}
 require(bool(unchanged)and all(data['source_sha256_after'].get(name)==value for name,value in unchanged.items()),
  'all prior production Python/staticJSON remain exact except two intended display integrations')
 for name in CHANGED_EXISTING:
  before='verification/sections/295-preparation/before-'+Path(name).name
  require(digest(before)==old['source_sha256_after'][name],'actual pre295 integration source '+name)
 require(digest('verification/sections/295-preparation/before-node_catalog.py')
  ==old['source_sha256_after']['rouge/node_catalog.py']==digest('rouge/node_catalog.py'),
  'catalog and typed reward query implementation remain exact')
 scope=load('verification/sections/295-preparation/scope.json')
 require(scope['section']==295 and scope['parent']==PARENT,'actual pre295 scope/current parent')
 require(digest('PROJECT_PROGRESS.md')==PROGRESS_SHA_BEFORE,'remaining-only todo file still unchanged')
 return {'previous_section':294,'previous_necessary_receipt':reference['receipt'],
  'previous_necessary_sha256':reference['sha256'],'unchanged_existing_Python_static_JSON_files':len(unchanged),
  'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),
  'node_catalog_and_typed_reward_query_unchanged':True,
  'old_research_or_images_not_in_this_producer_are_not_required_or_inserted':True,
  'PROJECT_PROGRESS_unchanged':True}


def necessary(value,parent):
 data=load(value)
 require(data['section']==295 and data['kind']=='necessary_change_related_tests_not_full_suite'
  and type(data['exit_code'])is int and data['exit_code']==0 and data['source_unchanged']is True
  and data['source_sha256_before']==data['source_sha256_after'],'actual final necessary0/stable sources')
 require(data['modules']==MODULES and data['argv'][1:7]==['-B','-X','utf8','-m','unittest','-v']
  and data['argv'][-len(MODULES):]==MODULES and data['source_commit_before']==parent==PARENT,
  'actual complete eight-module necessary command/current parent')
 require(data['game_sampling_verified']is False and data['chat_verified']is False
  and data['full_scope_reduced']is False and data['full_suite_rerun']is False,'necessary-only no external/full claims')
 require(expected_necessary_sources()==set(data['source_sha256_after']),
  'exact actual necessary producer scope: production/static JSON, new and289 packet, eight tests, script, builder, baseline and icon')
 check_map(data['source_sha256_after'],'final necessary')
 baseline=unchanged_existing_sources(data)
 logpath=path(value).with_name('stderr.txt');log=path(logpath).read_text(encoding='utf8')
 counts=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',log)
 require(len(counts)==1 and int(counts[0][0])>0 and log.rstrip().endswith('OK')
  and not re.search(r'^(FAIL|ERROR):',log,re.M),'actual terminal Ran/OK, no prefilled N')
 return data,{'receipt':rel(value),'sha256':digest(value),'stderr':rel(logpath),'stderr_sha256':digest(logpath),
  'stdout_sha256':digest(path(value).with_name('stdout.txt')),'actual_exit':0,'methods_run':int(counts[0][0]),
  'seconds':float(counts[0][1]),'source_files':len(data['source_sha256_after']),'source_unchanged':True,
  'modules':MODULES,'author14_and_dialog8_are_subsets_not_added_again':True,'existing_source_boundary':baseline}


def visual_review(window_value,window):
 name='verification/sections/295-preparation/root-visual-review.json';review=load(name)
 require(review['section']==295 and review['kind']=='root_archived_native_images_review'
  and review['actual_images_opened_with_view_image']is True,'actual root visual inspection')
 expected={rel(path(window_value).with_name(Path(row['path']).name)):row['sha256']for row in window['screenshots']}
 require(review['images']==expected and review['actual_image_count']==len(expected)==3,
  'root review binds all three actual original screenshots')
 return {'receipt':name,'sha256':digest(name),'actual_root_reviewed_images':len(expected),
  'helper_performed_visual_inspection':False}


def main(args):
 require(Path(__file__).resolve()==(HERE/'close_section_295.py').resolve(),'reviewed canonical cache helper')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 require(branch=='codex/p2-development'and parent==PARENT
  and not(ROOT/'verification/sections/295.json').exists(),'authorized branch/parent/exclusive receipt')
 source=packet();tests,test_ref=necessary(args.necessary_receipt,parent)
 window,window_ref=native(args.window_receipt,args.window_process_receipt,tests)
 window_ref['root_visual_review']=visual_review(args.window_receipt,window)
 main_ref=original_window(args.main_window_receipt,args.focus_receipt,window,tests,args.necessary_receipt,args.window_receipt)
 full=load(FULL)
 require(digest(FULL)==FULL_SHA and full['after_section']==290 and full['available_checks_passed']is True
  and full['scope_not_reduced']is True and full['complete_repository_validation']is False and full['P2_complete']is False,
  'historical290 full remains its original source, no full295 claim')
 cp=load('DEVELOPMENT_CHECKPOINT.json')
 require(cp['completed_sections']==cp['latest_functional_section']==294 and cp['next_section']==295
  and cp['active_section']['section']==295 and cp['policy']['priority_order']==['P3','P2','P1']
  and cp['policy']['current_user_batch_target_section']is None and cp['policy']['stop_after_section']is None,
  'real294 to active295/P3 first/no numeric endpoint')
 require(cp['last_full_validation']['after_section']==290 and cp['current_available_full_validation']['section']==290
  and cp['policy']['full_validation_interval']==15 and cp['policy']['full_validation_anchor_section']==125
  and 125+((295-125)//15+1)*15==305,'actual cadence290/next305')
 prior=cp['last_verified_cloud_save'];proof=load(prior['proof'])
 require(prior['section']==294 and digest(prior['proof'])==prior['proof_sha256']and proof['passed']is True
  and proof['commit']==proof['remote_HEAD']==prior['commit']and proof['push_primary_exit']==0,
  'actual preceding294 ordinary publication')
 docs={name:path(name).read_bytes()for name in('DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md',
  'WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','AGENTS.md')}
 progress=path('PROJECT_PROGRESS.md').read_bytes()
 require(sha256(progress).hexdigest()==PROGRESS_SHA_BEFORE
  and all(text in progress.decode()for text in('其中10图/18关已有58格直接参考','81个关卡、59张独立原图',
    '游戏内实际展示','10条未解析附注')),'all remaining gaps kept, no todo deletion')
 now=datetime.now(timezone(timedelta(hours=8))).isoformat()
 scope=('为线人资料中明确写出的沙盘α增加独立的具名物品阅读入口；默认不选中，手动打开其固定图标、'
  '用途、完整说明和解锁原文。保留父页面与弹窗的选择、页签、文字选区和实际非零滚动；'
  '来源失效清空旧说明和图标，恢复后不自动选择，切换事件清除旧范围。')
 limits=['文献物品阅读使用独立API，旧17条typed具名奖励及全部旧奖励查询逐值保持，不把文献身份加入旧奖励结果。',
  '原物品指针仍为空、原game_choice_ids仍空；不恢复25/57原入口，不确定数量、领取、可选性、已持有或效果激活。',
  '“完成游戏结局”是物品解锁原文，不等于事件完整出现条件，也不证明当前账号解锁。',
  '固定来源版本427904/440271/349818和原表仅为内容证据，不是当前服务器、本局或游戏操作验收。',
  '本节只必要检查与真实隔离Windows入口/弹窗，3张PNG；沿用290全量原冻结来源，下次305。',
  '部分地图参考10图18关58点与regular12/24不变，完整81/59和10条未解析附注等其它待办全部保留。',
  'P3/P2/P1仍未完成，识别最后；不推荐、排序或自动选路，不操作游戏/聊天或私人状态。']
 changed={CANONICAL,BUILDER,DATA,'rouge/documented_choice_items.py','rouge/documented_choice_item_view.py',
  *CHANGED_EXISTING,'tests/test_documented_choice_items_295.py','tests/test_documented_choice_item_view_295.py',
  'tests/test_documented_item_integration_295.py'}
 changed.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file())
 check_map({name:digest(name)for name in changed},'final feature sources')
 receipt={'section':295,'kind':'functional_section','title':TITLE,'at_Beijing':now,'branch':branch,'prior_commit':parent,
  'remaining_item':'P3节点事件具名物品图文资料','new_capability':scope,'files':sorted(changed),
  'source_sha256':{name:digest(name)for name in sorted(changed)},'source_reference':source,
  'existing_engine_or_typed_reward_qualification_or_run_state_changed':False,
  'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),
  'typed_named_grant_count_unchanged':17,'original_entry_gaps_unchanged':[25,57],
  'partial_direct_reference_scope_unchanged':[10,18,58],'whole_map_gaps_unchanged':[81,59],
  'necessary_validation':test_ref,'native_windows_validation':{**window_ref,'original_project_window':main_ref},
  'full_validation':{'receipt':FULL,'sha256':FULL_SHA,'after_section':290,'full_suite_rerun':False,
   'new295_source_full_validation_claimed':False,'scope_not_reduced':True,'next_periodic_section':305,
   'complete_repository_validation':False},'PROJECT_PROGRESS_unchanged_sha256':PROGRESS_SHA_BEFORE,
  'limits':limits,'next_section':296,'cloud_publication_binding':'enclosing_commit','cloud_published':False,
  'P3_complete':False,'P2_complete':False}
 history='historical_before295_current_pointers';require(history not in cp,'exclusive old pointers')
 cp[history]={key:deepcopy(cp[key])for key in('current_section_save','current_section_validation','latest_section_environment',
  'active_section','current_batch','cloud_publication_closeout')if key in cp}
 cp.pop('active_section',None);cp.pop('cloud_publication_closeout',None)
 cp.update(completed_sections=295,latest_functional_section=295,next_section=296,
  batch_status='P3_SECTION295_VALIDATED_AWAITING_PUBLICATION',next_full_validation_after=305,
  next_action='从296继续有证P3剩余事项，无数字终点；下次完整可用全量305。')
 cp['policy']['next_full_validation_after']=305;cp['current_batch_commit_policy']['next_full_validation_after']=305
 cp['current_batch'].update(status=cp['batch_status'],next_section=296,next_section_started=False,
  receipt='verification/sections/295.json',next_full_validation_after=305,batch_closed=False)
 cp['confirmed_next_stage_direction'].update(last_completed_functional_section=295,next_functional_section_started=False)
 cp['sections'].append({'number':295,'completion_ref':'p3-section-295','topic':TITLE,'verification':'verification/sections/295.json'})
 cp['current_section_save']={'section':295,'verification':'verification/sections/295.json','scope':'current_functional_section',
  'binding':'enclosing_commit','commit_reference':'commit containing295 documented item reader/source, actual validation, requirements and cloud index'}
 cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_section_validation']={'section':295,'receipt':'verification/sections/295.json','necessary_methods_passed':test_ref['methods_run'],
  'native_isolated_window_checks':window['unique_checks'],'full_suite_rerun':False,'last_full_receipt':FULL,'full_source_is_historical290':True}
 cp['latest_section_environment']={'section':295,'receipt':'verification/sections/295.json',
  'native_windows':f"{test_ref['methods_run']} actual necessary; {window['unique_checks']} unique native checks; real MainWindow/850x650 item dialog/3PNG; original visible/private5 unchanged",
  'native_game_or_chat_verified':False,'new_Linux_Wine_full_run':False,'current_section_full_rerun':False,'last_full_receipt':FULL}
 cp['functional_sections_since_latest_requirement']=list(dict.fromkeys([*cp['functional_sections_since_latest_requirement'],295]))
 completed=(f'## 功能第295节 · {TITLE}\n\n{now}。{scope}\n\n'
  f"实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过；真实主入口、沙盘α图标及三页清空/恢复未选、"
  '三次同范围刷新和父/子阅读留存已核，原项目窗口更新/私人5路径不变。'
  '独立文献资料不放宽17条typed奖励，不补25/57原入口或数量/实际领取；未将作者14/弹窗8项重复计入本次必要数。'
  '地图10图18关58点及全部其它待办保留，PROJECT_PROGRESS未修改。'
  '实际来源与回执verification/sections/295.json；290全量沿用原来源，下次305、后续296，无数字终点。待普通推送核对。\n\n')
 mutations={'verification/sections/295.json':encode(receipt),'DEVELOPMENT_CHECKPOINT.json':encode(cp),
  'PROJECT_COMPLETED.md':completed.encode()+docs['PROJECT_COMPLETED.md']}
 wip=docs['WORK_IN_PROGRESS.md'].decode();require('## 功能第294节'in wip,'preserve294 onward history')
 mutations['WORK_IN_PROGRESS.md']=(completed+wip[wip.index('## 功能第294节'):]).encode()
 req=docs['PROJECT_REQUIREMENTS.md'].decode();a,b=req.index('<!-- current-delivery:start -->'),req.index('<!-- current-delivery:end -->')
 block=('<!-- current-delivery:start -->\n## 当前交付与续接 · 第295节\n\n2026-10-16继续P3，无数字终点。'+scope
  +f"最终实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过，原窗口更新/私人5路径不变。"
  +'独立文献物品不放宽17条typed奖励或25/57入口，数量与本局领取未知；待办原样保留。'
  +'290全量沿用原来源，下次305；P3→P2→P1、识别最后，不提供路线建议。待普通推送核对，源码/要求/回执/索引同提交。\n')
 mutations['PROJECT_REQUIREMENTS.md']=(req[:a]+block+req[b:]).encode()
 agents=docs['AGENTS.md'].decode();a,b=agents.index('## 当前续接 · 第294节'),agents.index('## 当前优先顺序与输出可读性')
 mutations['AGENTS.md']=(agents[:a]+'## 当前续接 · 第295节已完成功能与必要/原生验收\n\n'+scope
  +'来源及实际回执verification/sections/295.json；原17条typed奖励与25/57入口不变，数量/实际领取/资格仍未知。'
  +'原项目窗口更新/私人5路径不变；未跑295全量，290完整可用范围沿用原来源。下一节296/下次305，无数字终点。'
  +'P3→P2→P1、识别最后，不推荐/排序/自动选路。本节待普通推送并核对真实远端，源码/要求/验收/索引同提交。\n\n'+agents[b:]).encode()
 require('初次招募时即处于已进阶状态'in mutations['PROJECT_REQUIREMENTS.md'].decode()
  and'初次招募即处于已进阶状态'in mutations['AGENTS.md'].decode(),'keep verified recruitment terminology')
 require(all(str(i)+'.'in mutations['AGENTS.md'].decode().split('## 当前续接')[0]for i in range(1,6)),
  'keep highest-priority five independent-judgment requirements')
 archive=ROOT/'verification/sections/295-preparation/closeout-tools';require(not archive.exists(),'exclusive public helper archive')
 copies={'close_section_295.py':path(HERE/'close_section_295.py').read_bytes(),'CONTRACT.md':path(HERE/'CONTRACT.md').read_bytes()}
 copies.update({'before-'+name:raw for name,raw in docs.items()})
 manifest={'kind':'SECTION295_PUBLIC_CLOSEOUT_TOOLS_NOT_PRIVATE_STATE',
  'files':{name:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}for name,raw in copies.items()},
  'private_contents_or_hash_lists_copied':False,'tests_Qt_GUI_game_chat_Git_publish_or_full_executed_by_helper':False}
 print(json.dumps({'gates_passed':True,'apply_requested':args.apply,'necessary_actual_methods':test_ref['methods_run'],
  'native_actual_unique_checks':window['unique_checks'],'native_selected_source_files':len(selected_window_sources()),
  'planned_public_files':list(mutations),'PROJECT_PROGRESS_modified':False,'full_rerun':False,
  'next_full_section':305,'numeric_endpoint':None,'cloud_published':False},ensure_ascii=False))
 if not args.apply:return
 for name,raw in docs.items():require(path(name).read_bytes()==raw,'public document unchanged before apply '+name)
 require(path('PROJECT_PROGRESS.md').read_bytes()==progress,'todo bytes unchanged before apply')
 check_map(tests['source_sha256_after'],'final pre-write necessary')
 archive.mkdir(parents=True)
 for name,raw in copies.items():
  with(archive/name).open('xb')as f:f.write(raw)
 with(archive/'archive-manifest.json').open('xb')as f:f.write(encode(manifest))
 for name,raw in mutations.items():
  destination=ROOT/name;destination.parent.mkdir(parents=True,exist_ok=True)
  with destination.open('xb'if name=='verification/sections/295.json'else'wb')as f:f.write(raw)
 print(json.dumps({'section':295,'local_closeout_written':True,'cloud_published':False,'next_section':296,'next_full_section':305}))


def native(value,process_value,necessary_data):
 data=load(value)
 require(data['section']==295 and data['kind']=='isolated_native_windows_documented_choice_item_reading'
  and data['passed'] is True and data['failure'] is None and data['qpa']=='windows'
  and type(data['qt_exit_code']) is int and data['qt_exit_code']==0 and data['verification_window_closed'] is True,
  'actual canonical native Windows/Qt/owned-window close completion')
 require(type(data['process_id']) is int and data['process_id']>0,'actual fixture PID positive independently of launcher')
 require(digest(CANONICAL)==CANONICAL_SHA,'exact reviewed revision3 native source bytes')
 source_ast=ast.parse(path(CANONICAL).read_text(encoding='utf8'))
 required={call.args[1].value for call in ast.walk(source_ast)
  if isinstance(call,ast.Call)and isinstance(call.func,ast.Name)and call.func.id=='require'
  and len(call.args)>1 and isinstance(call.args[1],ast.Constant)and isinstance(call.args[1].value,str)}
 required|={'parent_actual_native_HWND_visible','parent_HWND_owned_by_fixture_and_not_minimized',
  'dialog_actual_native_HWND_visible','dialog_HWND_owned_by_fixture_and_not_minimized',
  'actual_parent_documented_item_QTest_click_visible_enabled_inside_actual_client',
  'actual_item_description_QTest_click_visible_enabled_inside_actual_client',
  'reopen_exact_item_before_event_change_QTest_click_visible_enabled_inside_actual_client',
  'return_main_entry_QTest_click_visible_enabled_inside_actual_client'}
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
 require(data['requested_parent_client_size']==[1050,720] and data['minimum_dialog_client_size']==[850,650]
  and bool(data['native_observations']),'actual one parent size and bounded dialog observations')
 handles={'parent':set(),'dialog':set()}
 def check_handle(handle):
  kind=handle['kind'];require(kind in handles and handle['process_id']==data['process_id']
   and handle['qpa']=='windows' and type(handle['hwnd']) is int and handle['hwnd']>0,'own actual native HWND/fixture PID')
  size=handle['client_size'];require(type(size) is list and len(size)==2 and all(type(n) is int for n in size),'actual logical client size')
  require(size==[1050,720] if kind=='parent' else size[0]>=850 and size[1]>=650,'parent exact/dialog minimum actual logical dimensions')
  handles[kind].add(handle['hwnd'])
 for handle in data['native_observations']:check_handle(handle)
 images=data['screenshots']
 expected_images={'parent-entry':'parent','alpha-item-description':'dialog','source-invalidated':'dialog'}
 require(data['screenshot_count']==len(images)==len(expected_images)
  and {image['name'] for image in images}==set(expected_images),'all three actual parent/item/source-failure image originals')
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
 expected_read={'reference_id':REFERENCE,'icon_file':'rouge/data/relic-icons/'+ITEM+'.png',
  'icon_sha256':'1d07a123253172ede9a4585abdcd1b301350e096b245bc046539c48f6c6fb825',
  'actual_reward':None,'actual_quantity':None,'actual_selectable':None,'original_entry_bound':False}
 require(record['documented_item_reads']==[expected_read]and record['same_scope_refresh_rounds']==3
  and record['original_entry_bound']is False
  and record['same_event_typed_reward_query_unchanged_during_reading']is True
  and record['old_typed_reward_source_sha256']==digest('rouge/data/node-reward-reference.json'),
  'one exact documented item, three actual same-scope refreshes and unchanged typed query values')
 require(all(record[name]is None for name in('default_choice','actual_game_choice','actual_inventory','actual_quantity','actual_item_active'))
  and record['source_failure_is_only_an_explicit_temporary_public_clone_negative_fixture']is True,
  'public-clone negative fixture only; actual choice/inventory/quantity/effect remain unknown')
 return data,{'receipt':rel(value),'sha256':digest(value),'source_selected_files':len(selected),
  'source_unchanged':True,'unique_checks':len(checks),
  'actual_assertion_executions':data['successful_assertion_executions_including_repeated_guards'],
  'actual_parent_client_size':[1050,720],'minimum_dialog_client_size':[850,650],
  'screenshots':len(images),'actual_Qt_exit':0,'actual_windows_closed':True,
  'images_visually_reviewed_by_helper':False,'owned_process':process_ref,'game_or_chat_verified':False}

def original_window(main_value,focus_value,fixture,necessary_data,necessary_value,native_value):
 main,focus=load(main_value),load(focus_value)
 require(path(main_value).resolve()==(ROOT/'verification/sections/295-main-window.json').resolve()
  and path(focus_value).resolve()==(ROOT/'verification/sections/295-main-window-focus.json').resolve(),
  'strict same-section canonical295 main/focus receipt paths')
 require(main['section']==295 and focus['section']==295
  and main['necessary_receipt_sha256']==digest(necessary_value)
  and main['native_receipt_sha256']==digest(native_value)
  and main['native_receipt']==rel(native_value) and main['necessary_receipt']==rel(necessary_value)
  and focus['main_receipt_sha256']==digest(main_value),
  'actual295 main binds both final evidence receipts; focus binds exact same main bytes')
 require(main['source_sha256_before']==main['source_sha256_after']==fixture['source_sha256_after']
  and set(main['source_sha256_after'])==selected_window_sources(),
  'same final actual native_selected source map stable through original window restart')
 check_map(main['source_sha256_after'],'original295 window final native_selected sources')
 timestamps={name:datetime.fromisoformat(value.replace('Z','+00:00')) for name,value in {
  'started':main['started_utc'],'finished':main['finished_utc'],'focus':focus['at_utc'],
  'necessary_finished':necessary_data['finished_utc'],'native_finished':fixture['finished_at']}.items()}
 require(all(value.tzinfo is not None and value.utcoffset() is not None for value in timestamps.values()),
  'actual main/focus/final-check timestamps are timezone-aware')
 require(timestamps['started']>timestamps['necessary_finished'] and timestamps['started']>timestamps['native_finished']
  and timestamps['finished']>=timestamps['started'] and timestamps['focus']>=timestamps['finished'],
  'original295 restart occurs after both final validations; focus follows completed main receipt')
 require(main['passed'] is True and main['private_file_hash_comparison_count']==5 and main['private_hashes_equal'] is True
  and main['changed_private_paths']==[] and main['private_contents_parsed_copied_or_restored'] is False and main['no_private_restoration'] is True,
  'actual original-window update/private5 hash unchanged, no content parsing/copy/restore')
 require(len(main['visible_windows'])==1,'one visible original project window');visible=main['visible_windows'][0]
 require(visible['visible'] is True and visible['responding'] is True and visible['minimized'] is False and visible['hwnd']>0
  and visible['pid']!=fixture['process_id'],'original window responsive/visible and not fixture')
 require(focus['visible'] is True and focus['pid']==visible['pid'] and focus['hwnd']==focus['actual_foreground']==visible['hwnd'],
  'actual foreground original project window')
 return {'receipt':rel(main_value),'sha256':digest(main_value),'focus_receipt':rel(focus_value),'focus_sha256':digest(focus_value),
  'section':295,'necessary_receipt_sha256':digest(necessary_value),'native_receipt_sha256':digest(native_value),
  'native_selected_current_source_unchanged':True,'started_after_final_necessary_and_native':True,'focus_after_main_finished':True,
  'private_hash_comparisons':5,'changed_private_paths':0,'visible_responsive_foreground':True,'private_contents_read_by_helper':False}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--necessary-receipt',required=True);parser.add_argument('--window-receipt',required=True)
 parser.add_argument('--window-process-receipt',required=True)
 parser.add_argument('--main-window-receipt',default='verification/sections/295-main-window.json')
 parser.add_argument('--focus-receipt',default='verification/sections/295-main-window-focus.json')
 parser.add_argument('--apply',action='store_true');main(parser.parse_args())
