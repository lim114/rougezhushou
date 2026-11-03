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
parent='1e682c03073b87f7e88ddebc714013d8a6dfb8f1';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='襁褓准确来源与失败助力的双局条件'
change='通用藏品与探索设置增加跨局助力目录：14份当前原件按五种实际分支查阅，13襁褓连接已有培育来源，六份同名羽蛇独立连接准确蓝色支援。隐藏助力单独对照失败那局和下次开始的模式、保密等级与失败/开始声明，0–3与4的限制和开始其它难度消耗判定的文献风险分开呈现；不自动代填任何一局。可打开准确影像、难度、种子和开局原文，并从真实相关藏品/选项/难度/场景反向进入。父刷新保持本页声明与阅读，失效清旧并关闭所属树，恢复手选。'
limits='14份当前原件与旧固定表相同，不声称版本改了继承机制，不把旧培育和蓝支援重新算新功能。仅四份黄色原ID有旧种子明确来源，其余同组变体不借同名证明。公开PRTS434554支持双局常规等级0–3及判定消耗提示，但主动放弃/准备退出是否等同失败未证；实际判定、当前持有、已领取/已消耗与服务器完整资格未知。所有声明仅本页，不领取、重置本局或写数值；无游戏聊天操作、路线建议及概率，P3/P2/P1均未完成。'
validation='最终本机33项必要测试、64项原生窗口唯一检查通过，真实14原件、13种子原文/6独立蓝支援、25个0–4双局组合、五档难度和影像准确原文、相关多类别反向入口；两非零阅读与声明经真实父刷新保持，定向改坏361成员清旧及手选恢复，深层子树关闭。首次33单测通过，原生验收器从未提供目录的节点页取总览失败；保留失败及改前验收器，纠正为真实藏品页入口后最终33/64通过，未为测试扩产品入口。七真实外部操作零、临时本局及旧计算保持。独立子代理逐张实际查看最终七图并说明折外未见范围；原项目测试窗正常更新且可见响应，重启全程私人五路径保持。588旧选择器原序保留，新2个共590。350全量仅改前历史，下次365；未变索引25单测复用，当前要求/索引实际校验，不可用私样本/1314/游戏聊天不计通过。继续至370后暂停。'
nname='verification/sections/361-necessary-attempt2/process.json';wname='verification/sections/361-native-attempt2/actual/window.json';pname='verification/sections/361-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/361-main-window.json');a=read('verification/sections/361-source-audit.json');v=read('verification/sections/361-root-visual.json')
assert n['passed']and n['methods_ran']==33 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==64 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==59 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous588_preserved']and len(a['current_selectors'])==590
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section361-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':361,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/361-root-visual.json'),'source_audit':pin('verification/sections/361-source-audit.json'),'original_project_window':pin('verification/sections/361-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/361.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第361节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述361为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第361节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第361节 + '+title+'\n\n'+details+'\n\n继续P3；362从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第361节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
old='上次继承状态、实际结算及未证数值';assert s.count(old)==1;s=s.replace(old,'襁褓精确变体的实际培育来源、失败与下次开始的真实资格/判定消耗/领取、上次继承状态、实际结算及未证数值')
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==360 and cp['next_section']==361
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before361_'+key]=cp.pop(key)
cp.update(completed_sections=361,latest_functional_section=361,next_section=362,batch_status='P3_SECTION361_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第361节 + '+title+'已本机必要验收；普通推送核对后362接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':361,'completion_ref':'p3-section-361','topic':title,'verification':'verification/sections/361.json'});cp['functional_sections_since_latest_requirement'].append(361)
cp['current_section_save']={'section':361,'verification':'verification/sections/361.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':361,'receipt':'verification/sections/361.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':361,'receipt':'verification/sections/361.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=361,next_section=362,next_section_started=False,receipt='verification/sections/361.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update({'current_legacy_records': 14, 'current_legacy_blue_support_links': 6, 'current_legacy_actual_claim_verified': False})
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section361-handoff:start -->\n## 第361节 + '+title+'\n\n'+details+'\n<!-- section361-handoff:end -->\n')
out=ROOT/'verification/sections/361-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_361.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':361,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next362_started':False,'at_Beijing':now}))
print(json.dumps({'section':361,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
