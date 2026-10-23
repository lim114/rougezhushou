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
parent='356b809a63feb400967057d56d4f166d5c2e9d92';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='分队初始物品与印记招募券的准确取得来源'
change='通用藏品与探索设置加入十条非事件具名取得资料：八条准确分队初始物品、两条印记对应随机直升临时招募券。来源/时点分别筛选，可从分队、藏品或零件准确反向进入，并分别打开两侧原文。地质初始时点保留社区补证，印记在黑流树海的实际发放时点保持未知；多边贸易初始3件与每次入店1件不相加。父刷新保持搜索、准确目标、声明和两种阅读，坏源清旧并关闭完整所属树。单次核对复用同一次已经验证的招募券资料，不跨刷新缓存或跳过来源检查。项目要求永久补充待办按实际功能归类，不单列版本迁移。'
limits='十条明确id/count与固定国服原件及PRTS442954分队整行核对；不是完整取得池或当前已生效/已领取。博士银印水月主题备注不能套到黑流；变量名不证明发放时钟，同名基础分队不能借强化档位。只有两张准确券原文能进入已有招募券目录，未在该目录新增反向UI，不把354留存、360新典训或361助力重复记新机制。完整随机候选、人选/培养、当前解锁/实际发放及服务器执行未知，无计算/本局写入、游戏聊天操作、概率或路线建议。P3/P2/P1未完成。'
validation='最终本机28项必要测试、55项原生窗口唯一检查通过，十条来源与两侧原文、18个真实普通反向入口、数量/时点/同名档位边界、两非零阅读/搜索/精确请求经实际父刷新保持、真实来源损坏与手选恢复、完整深层树关闭。首轮28测试通过，原生约两分钟在反向按钮可见性失败；同一目标独立locate有效，旧时限关闭可能影响可见性，原因未冒称已确定。保留原失败和改前源码；减少同次重复读取、补两张券原物品不匹配拒绝，并保留首个超时错误。新验收预算300秒，最终约95秒完成全部55项，不当作生产耗时承诺或性能基准。七真实外部操作零，临时本局/旧计算保持。独立子代理实际逐张查看最终七图；本机测试窗正常更新可见响应，正常重启全程私人五路径保持。592旧选择器原序保留，新2个共594；350全量仅历史，下次365。当前索引/要求实际验证、未变25索引单测复用；缺私样本/1314/游戏聊天不计通过，继续至370后暂停。'
nname='verification/sections/363-necessary-attempt2/process.json';wname='verification/sections/363-native-attempt2/actual/window.json';pname='verification/sections/363-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/363-main-window.json');a=read('verification/sections/363-source-audit.json');v=read('verification/sections/363-root-visual.json')
assert n['passed']and n['methods_ran']==28 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==55 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['all10_readings'])==10 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous592_preserved']and len(a['current_selectors'])==594
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section363-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':363,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/363-root-visual.json'),'source_audit':pin('verification/sections/363-source-audit.json'),'original_project_window':pin('verification/sections/363-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/363.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第363节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述363为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第363节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第363节 + '+title+'\n\n'+details+'\n\n继续P3；364从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第363节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
old='全部具名物品的其余取得来源';assert s.count(old)==1;s=s.replace(old,'十条非事件来源在本局的实际生效/持有/领取、人事部铜印与博士银印的黑流树海发放时点；全部具名物品的其余取得来源')
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==362 and cp['next_section']==363
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before363_'+key]=cp.pop(key)
cp.update(completed_sections=363,latest_functional_section=363,next_section=364,batch_status='P3_SECTION363_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第363节 + '+title+'已本机必要验收；普通推送核对后364接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':363,'completion_ref':'p3-section-363','topic':title,'verification':'verification/sections/363.json'});cp['functional_sections_since_latest_requirement'].append(363)
cp['current_section_save']={'section':363,'verification':'verification/sections/363.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':363,'receipt':'verification/sections/363.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':363,'receipt':'verification/sections/363.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=363,next_section=364,next_section_started=False,receipt='verification/sections/363.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update({'current_non_event_named_sources': 10, 'current_named_squad_initial_sources': 8, 'current_mark_ticket_sources_with_unknown_timing': 2, 'current_non_event_actual_receipt_verified': False})
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section363-handoff:start -->\n## 第363节 + '+title+'\n\n'+details+'\n<!-- section363-handoff:end -->\n')
out=ROOT/'verification/sections/363-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_363.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':363,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next364_started':False,'at_Beijing':now}))
print(json.dumps({'section':363,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
