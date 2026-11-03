from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,subprocess,runpy,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return{'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
parent='d01e307fe6d416d2fd0c345f11e125c171f59887';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='熄日两份配置的入口与保护目标图上标志'
change='为当前熄日两份明确配置补入7个入口和1个保护目标的可见标志对照，共16个配置-标志组合。原图上的标志位置来自本图直接观察及颜色像素中心计算；不按旧图、同名或附近格子外推。每份配置分别核对完整地形导出、相机字段和固定原图记录，全部来源和字节符合才提供标注。地图格子或带中文入口/保护目标名称的列表选择会在对应固定原图显示近似标记，窗口缩放仍保持原图位置；其余未标注格子不画点、图片点击不反推格子、不连接实际路线。现有出怪条目中明确引用保护目标的终点格，也可直接在原图查看保护目标标志；显示精确误差未测量，不冒充实际出生/到达点、偏移或完整出怪时钟。两个阅读区的真实非零滚动和选区、格子、下拉及页签经父页刷新保持。坏源清空旧图、格子和标记，恢复后须手选；重复打开和父战斗窗口关闭清理所属地图窗口。旧33引用的265个地面近似中心保持；新增2配置的可见标志单列，不与旧地面中心合称完整投影。'
limits='本节新增直接观察，不是独立外部实机地标验收。主代理查看固定512x286原图，按完整9x13原始地形中7个入口与唯一保护目标的空间排列逐项对应；记录逐点观察框、手工估计和可重复的颜色像素中心。两种像素估计来自同一原图，不冒充独立外部真值；没有误差上界、绝对精度或敌人脚点保证。只准入ro6_b_7与ro6_b_7_b，各自保留完整地形/相机字段、原图身份及明确版本记录；不按同名或同图推到其它配置。复用固定bee3国服公开原件与de6cfb资源原图，无新下载或游戏采样，不恢复当前服务器脚本。熄日其余格子、高台表面、出生偏移/随机范围、脚点、完整投影与反查/线段、实际地图或分支选择仍未知。仅局外查阅，不操作游戏、发送聊天或改本局/地图/数值计算，不提供路线建议/排序/概率。P3/P2/P1未完成，识别最后。'
validation='本机首轮42项相关测试中41项通过，1项因简短说明实际没有滚动条而未能执行非零滚动验收。保留原测试字节和失败日志，仅在隔离测试中把阅读区限制为52像素以产生真实滚动；产品文案和逻辑均未为此改动。最终完整相关42项重跑全部通过，构建字节一致。原生Windows临时MainWindow共31项唯一检查通过，实际两配置16个标志逐点选择、每点两种窗口大小、中文标志/脚点/精度范围、下拉同步、未测格与原图点击不造点、两个阅读区真实非零滚动及选区经父战斗页刷新保持；真实出怪条目位置按钮显示保护目标标志，实际坏源清空/手动恢复、重复打开和父窗口关闭清子窗。现有地面映射仍有效、未映射另一关仍不造点；必要测试保留旧33引用/265点完整来源核验和184当前关卡动作的准确来源绑定。6张实际PNG由主代理直接查看。七类真实外部操作计数零，临时本局和旧计算上下文不变；原项目测试窗口已正常更新、可见响应且未最小化，未确认置前台，正常关闭到启动私人五路径一致。541旧维护选择器原序保留，现543。只跑本机必要/原生验收；335完整可用范围和原失败及绑定维护复验仍属历史，不当本节全量，下一350。索引实现未变，25单测按原证据复用，但当前要求/断点和索引仍实际校验。'
nname='verification/sections/337-necessary-attempt2/process.json';wname='verification/sections/337-native-attempt1/actual/window.json';pname='verification/sections/337-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/337-main-window.json');a=read('verification/sections/337-source-audit.json');v=read('verification/sections/337-root-visual.json')
assert n['passed']and n['methods_ran']==42 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==31 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==6 and len(w['actual_readings'])==16 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==6 and a['ordered_previous541_preserved']and len(a['current_selectors'])==543
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section337-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':337,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':42,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':31,'actual_Qt_exit':0,'exact_stage_configurations':2,'visible_symbol_observations':8,'configuration_symbol_pairs':16,'original_map_bitmaps':1,'old_ground_reference_stages':33,'old_ground_points':265,'absolute_pixel_accuracy_claimed':False,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/337-root-visual.json'),'source_audit':pin('verification/sections/337-source-audit.json'),'original_project_window':pin('verification/sections/337-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/337.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第337节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述337为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第337节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第337节 + '+title+'\n\n'+details+'\n\n继续P3；338从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。可见标志不替代完整地块校准、独立外部地标或实际脚点验收。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第337节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');assert s.count('其它151引用')==2;s=s.replace('其它151引用','熄日两份配置的其余地块、标志到实际脚点与绝对精度，以及其它149引用');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==336 and cp['next_section']==337
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before337_'+key]=cp.pop(key)
cp.update(completed_sections=337,latest_functional_section=337,next_section=338,batch_status='P3_SECTION337_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第337节 + '+title+'已本机必要验收；普通推送核对后338接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':337,'completion_ref':'p3-section-337','topic':title,'verification':'verification/sections/337.json'});cp['functional_sections_since_latest_requirement'].append(337)
cp['current_section_save']={'section':337,'verification':'verification/sections/337.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':337,'receipt':'verification/sections/337.json','methods_run':42,'native_isolated_window_checks':31,'exact_stage_configurations':2,'visible_symbol_observations':8,'configuration_symbol_pairs':16,'original_map_bitmaps':1,'old_ground_reference_stages':33,'old_ground_points':265,'absolute_pixel_accuracy_claimed':False,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':337,'receipt':'verification/sections/337.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=337,next_section=338,next_section_started=False,receipt='verification/sections/337.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=94,current_usage_receipt='verification/sections/337-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_visible_map_markers_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_visible_map_markers_resource_commit='de6cfb30ed1d41d9102d93e8ea400fc0cefc8ff7',current_visible_map_marker_configurations=2,current_visible_map_marker_images=1,current_visible_map_marker_observations=8,current_visible_map_marker_configuration_pairs=16,current_ground_center_reference_stages=33,current_ground_center_reference_points=265,current_ground_or_marker_reference_union_stages=35,current_remaining_unannotated_stage_refs=149,current_new_external_independent_ground_truth_verified=False,current_actual_combat_pixel_accuracy_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section337-handoff:start -->\n## 第337节 + '+title+'\n\n'+details+'\n<!-- section337-handoff:end -->\n')
out=ROOT/'verification/sections/337-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_337.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/337-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':337,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next338_started':False,'at_Beijing':now}))
print(json.dumps({'section':337,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
