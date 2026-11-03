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
parent='5999df7d7ab2f8cde43fb6e6a4044cc05612917a';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='追忆、同行者和笼控器的取得方式反查与事件跳转'
change='收藏品或零件详情新增已核对取得方式入口：追忆3条、同行者1条、笼控器2条，分别显示事件、具体选项、各自代价与奖励原文，可直接打开对应事件、对话和选项。三种追忆代价与两种笼控器代价各自保留，不相加、不按重复记录多领；持有笼控器、消耗源私钥及前往/标记小狗不冒充额外奖励来源。只对准确物品及类别提供入口，源私钥等未覆盖项不显示无效按钮。页面默认总览无选择，不猜领取件数、不自动代入本局条件。刷新保留取得选项、两个真实非零阅读位置与选区、页签及已开事件中的条件；换条目、来源失效、父页或主窗关闭均清理所属窗口，恢复须手动重选。'
limits='复用333/335/336已完整核对的固定国服原件及对应文献表，不进行新下载、不从物品提示图标或名称推奖励。新增的是物品反查取得分支和准确事件入口，不是重新登记已有事件阅读器。仅覆盖三物品、三事件的六条已核对奖励分支，不声称完整获取池；缺失条目不等于不能获得。已列条件不是服务器完整资格；实际领取、数量、当前本局库存和服务器版本均未核验。未知范围不靠推测补齐，不改奖励池、地图或数值计算。仅局外资料查阅，不操作游戏、不发送聊天或改私人配置，不提供路线建议/排序/概率。P3/P2/P1未完成，识别最后。'
validation='本机首轮35项相关测试34通过、1失败：实际窗口获得焦点后自动选中了第一条取得方式。保留原失败及当时源码，产品明确清除当前行并把初始焦点放到阅读区；最终35项完整相关测试全部重跑通过，资料构建字节一致。Windows原生临时MainWindow共43项唯一检查通过，三物品六条真实入口逐项打开准确对话/选项，事件专用控件、默认未知条件、源私钥非奖励、两个真实非零阅读与选区/页签经实际父刷新保留、子窗本页条件保留、重复打开及换选项关闭、真实坏源清旧/手动恢复、父条目切换及实际主窗关闭清整树。7张实际PNG主代理直接查看。七类真实外部操作计数零，临时本局与旧计算上下文不变。原项目测试窗正常更新，可见响应且未最小化；正常关闭到启动私人五路径一致，未确认置前台。543旧维护选择器原序保留，现545。准备阶段旧测试文件后缀错误在测试子进程启动前修正；资料审计准备的编码、选择器范围及导入路径问题亦修正，不冒称通过或功能节。只跑本机必要与原生检查，不云端重复运行；335完整可用范围仍属历史，不冒称本节全量，下次350。索引实现未变，25单测按既有证据复用，但当前资料、要求和索引仍实际校验。'
nname='verification/sections/338-necessary-attempt3/process.json';wname='verification/sections/338-native-attempt1/actual/window.json';pname='verification/sections/338-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/338-main-window.json');a=read('verification/sections/338-source-audit.json');v=read('verification/sections/338-root-visual.json')
assert n['passed']and n['methods_ran']==35 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==43 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==6 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous543_preserved']and len(a['current_selectors'])==545
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section338-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':338,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':35,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':43,'actual_Qt_exit':0,'named_items':3,'events':3,'acquisition_branches':6,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/338-root-visual.json'),'source_audit':pin('verification/sections/338-source-audit.json'),'original_project_window':pin('verification/sections/338-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/338.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第338节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述338为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第338节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第338节 + '+title+'\n\n'+details+'\n\n继续P3；339从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。反查取得清单不是完整获取池或本局可选判定。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第338节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');assert s.count('其余具名奖励来源')==1;s=s.replace('其余具名奖励来源','其它具名物品的已核对取得入口，以及全部具名物品的其余取得来源');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==337 and cp['next_section']==338
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before338_'+key]=cp.pop(key)
cp.update(completed_sections=338,latest_functional_section=338,next_section=339,batch_status='P3_SECTION338_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第338节 + '+title+'已本机必要验收；普通推送核对后339接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':338,'completion_ref':'p3-section-338','topic':title,'verification':'verification/sections/338.json'});cp['functional_sections_since_latest_requirement'].append(338)
cp['current_section_save']={'section':338,'verification':'verification/sections/338.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':338,'receipt':'verification/sections/338.json','methods_run':35,'native_isolated_window_checks':43,'named_items':3,'events':3,'acquisition_branches':6,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':338,'receipt':'verification/sections/338.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=338,next_section=339,next_section_started=False,receipt='verification/sections/338.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_reward_origins_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_reward_origins_named_items=3,current_reward_origins_events=3,current_reward_origins_acquisition_branches=6,current_reward_origins_complete_pool_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section338-handoff:start -->\n## 第338节 + '+title+'\n\n'+details+'\n<!-- section338-handoff:end -->\n')
out=ROOT/'verification/sections/338-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_338.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':338,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next339_started':False,'at_Beijing':now}))
print(json.dumps({'section':338,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
