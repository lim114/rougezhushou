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
parent='3b107fed989d26ccbdf25a37c83ce42b980a8018';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='招募券按职业与券种查阅，留存规则与准确取券入口'
change='通用藏品与零件页加入招募券用途与留存入口，47种券与各自明确留存原件配对，可按八职业和五券种交叉筛选，查看自身中文用途、星级及原券/留存券区别。说明初始三张、初始招募不可留存、满额不可替换、取出不能再次存入、取出时随机效果重新判定；配置1与15不冒称本局容量。准确打开险路尽头召集同伴与安全角落求援原文，保留血管前置与实际未知；所选券与总览都保持刷新和所属事件子窗，切主页面或关闭主窗清理整树。'
limits='券种依据固定bee3原表，留存文献为实际下载的PRTS修订442954。47对覆盖94原件是目录覆盖，不是本局库存、奖励池或可领张数；原券与留存券相同参数不代表随机人选或直升结果相同。实际库存、当前容量、希望费用、具体人选、实际培养和服务器执行未证；求援随机菜单名额仍未知。未操作游戏、未发聊天或修改本局/计算；没有路线建议或概率。P3/P2/P1未完成，识别最后。'
validation='本机28项必要测试、33项原生窗口唯一检查通过，包括47配对与94原件、八职业五券种交集、四类特殊券星级/用途、3与15边界、全部manifest成员破坏及底层提供者失效、实际通用页面入口与两个准确原文、选券和总览子窗刷新、两组非零选区/滚动/页签保持、坏源清除与恢复手选、页面切换和主窗整树关闭。七类真实外部操作均零，临时本局与旧计算不变；五张券页截图主代理逐张查看，它们不冒充事件子窗截图，子窗身份另由实际控件读取验证。原项目窗口正常更新可见响应，完整关闭/启动区间私人五路径保持。574旧选择器保留原序，新加2个共576。本节未重复全量，350仅改前历史证据、下一定期365；不可用Windows私样本/符号链接1314/游戏聊天未冒称通过。索引实现未改，复用25项历史单测并实际验证当前索引及要求。按用户授权继续至370后暂停。'
nname='verification/sections/354-necessary-attempt1/process.json';wname='verification/sections/354-native-attempt1/actual/window.json';pname='verification/sections/354-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/354-main-window.json');a=read('verification/sections/354-source-audit.json');v=read('verification/sections/354-root-visual.json')
assert n['passed']and n['methods_ran']==28 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==33 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==5 and len(w['actual_readings'])==4 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==5 and a['ordered_previous574_preserved']and len(a['current_selectors'])==576
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section354-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':354,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'ticket_original_stashed_pairs':47,'raw_ticket_records':94,'ticket_families':5,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/354-root-visual.json'),'source_audit':pin('verification/sections/354-source-audit.json'),'original_project_window':pin('verification/sections/354-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/354.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第354节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述354为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第354节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第354节 + '+title+'\n\n'+details+'\n\n继续P3；355从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。招募券目录不替代本局库存和实际发放。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第354节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='留存券库存/费用/实际结果';assert s.count(old)==1;s=s.replace(old,'留存券库存/当前容量/实际人选与随机结果/费用/培养和真实发放');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==353 and cp['next_section']==354
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before354_'+key]=cp.pop(key)
cp.update(completed_sections=354,latest_functional_section=354,next_section=355,batch_status='P3_SECTION354_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第354节 + '+title+'已本机必要验收；普通推送核对后355接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':354,'completion_ref':'p3-section-354','topic':title,'verification':'verification/sections/354.json'});cp['functional_sections_since_latest_requirement'].append(354)
cp['current_section_save']={'section':354,'verification':'verification/sections/354.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':354,'receipt':'verification/sections/354.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'ticket_original_stashed_pairs':47,'raw_ticket_records':94,'ticket_families':5,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':354,'receipt':'verification/sections/354.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=354,next_section=355,next_section_started=False,receipt='verification/sections/354.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_recruit_ticket_pairs=47,current_recruit_ticket_originals=94,current_recruit_stash_document_revision=442954,current_recruit_actual_inventory_verified=False)
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section354-handoff:start -->\n## 第354节 + '+title+'\n\n'+details+'\n<!-- section354-handoff:end -->\n')
out=ROOT/'verification/sections/354-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_354.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':354,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next355_started':False,'at_Beijing':now}))
print(json.dumps({'section':354,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
