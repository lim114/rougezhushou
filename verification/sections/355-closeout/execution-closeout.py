from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+chr(10)).encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return{'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
parent='f29a820d40d4818aa07ebdfbbe239ea073769e52';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='当前出怪候选与关联成员、原条目和地图参考联动'
change='固定作战预览加入出怪候选与关联记录阅读页，主波次和条件分支分别筛选，逐组查看具体敌人、空白记录和未指定装置，可准确跳到本关原出怪条目与已有地图位置参考。184份配置、113份原关卡中的604候选组与393关联记录分别保留，重复关系不累加实际敌人数；同名标记只在同一片段或阶段匹配。空白记录不显示不可用地图的误导说明，未指定装置不借其它物件替代。补齐通用页到已开作战及下层的真实刷新，源失效清旧关系并关闭所属地图；主页面换关和关闭整树。'
limits='采用固定bee3原关卡及明确原字段，只证明记录归属与候选目录，不能证明实际采用、同时发生、互斥次数或出现概率。固定当前条件分支没有候选组/关联标记，分支作用域仅有独立边界测试，不充真实游戏正例。全局出怪时钟、分支实际触发、真实路径/脚点、未校准原图中心、完整服务器资格与实际敌人数继续未知。位置完全复用既有准入，不补坐标。未操作游戏、发聊天或改本局及旧计算；P3/P2/P1未完成，识别最后。'
validation='最终本机32项必要测试与29项原生窗口唯一检查通过，核对184配置的完整原关系、同键跨片段/波次/分支/阶段不合并、空白/未指定装置/真实敌人、候选组与关联记录分开、精确父出怪和既有地图入口、两组非零阅读及真实父刷新、坏源清除和恢复手选、主窗所属树关闭。七类真实外部操作均零，本局与旧计算不变。首次原生暴露父刷新未传入作战子窗，已修正并保留失败及改前源码；第二次原生通过后视觉发现空白项仍附通用地图提示，澄清阅读文案后最终复验。新增文案断言最初误放到未选目录，原失败保留，原断言移到准确空白项测试后32项通过，不删有效断言。最终六张实际截图主代理逐张查看，含实际地图子窗。原项目窗口正常更新可见响应，完整关闭/启动区间私人五路径保持。576旧选择器原序保留，新加2个共578；350全量仅改前历史证据，下一定期365。本节复用25项未变索引单测并实际验证要求与索引；不可用私样本/Windows1314/游戏聊天未冒称通过。按授权继续370后暂停。'
nname='verification/sections/355-necessary-attempt4/process.json';wname='verification/sections/355-native-attempt3/actual/window.json';pname='verification/sections/355-native-attempt3/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/355-main-window.json');a=read('verification/sections/355-source-audit.json');v=read('verification/sections/355-root-visual.json')
assert n['passed']and n['methods_ran']==32 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==29 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==6 and len(w['actual_readings'])==4 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==6 and a['ordered_previous576_preserved']and len(a['current_selectors'])==578
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section355-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':355,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'current_stage_configurations':184,'current_original_levels':113,'main_candidate_groups':604,'main_packages':393,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/355-root-visual.json'),'source_audit':pin('verification/sections/355-source-audit.json'),'original_project_window':pin('verification/sections/355-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/355.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第355节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述355为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第355节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第355节 + '+title+'\n\n'+details+'\n\n继续P3；356从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。固定候选关系不替代实际出怪和未知全局时钟。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第355节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='条件分支在实际游戏中的激活、路线作用域';assert s.count(old)==1;s=s.replace(old,'已列候选/关联记录的实际抽取、互斥与出现次数；条件分支在实际游戏中的激活、路线作用域');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==354 and cp['next_section']==355
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before355_'+key]=cp.pop(key)
cp.update(completed_sections=355,latest_functional_section=355,next_section=356,batch_status='P3_SECTION355_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第355节 + '+title+'已本机必要验收；普通推送核对后356接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':355,'completion_ref':'p3-section-355','topic':title,'verification':'verification/sections/355.json'});cp['functional_sections_since_latest_requirement'].append(355)
cp['current_section_save']={'section':355,'verification':'verification/sections/355.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':355,'receipt':'verification/sections/355.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'current_stage_configurations':184,'current_original_levels':113,'main_candidate_groups':604,'main_packages':393,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':355,'receipt':'verification/sections/355.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=355,next_section=356,next_section_started=False,receipt='verification/sections/355.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_spawn_relation_configs=184,current_spawn_relation_groups=604,current_spawn_relation_packages=393,current_spawn_actual_execution_verified=False)
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section355-handoff:start -->\n## 第355节 + '+title+'\n\n'+details+'\n<!-- section355-handoff:end -->\n')
out=ROOT/'verification/sections/355-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_355.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':355,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next356_started':False,'at_Beijing':now}))
print(json.dumps({'section':355,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
