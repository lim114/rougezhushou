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
parent='ee3e7241fc541959aa60cd989340216b9efd8108';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='进阶券职业星级范围与新典训准确来源'
change='通用藏品与零件页加入18份当前进阶券的专门目录，职业、券种、资料星级分别筛选；同名原项保留准确来源。八份新典训与所附券按明确发放指针关联，可从藏品反向查看券，再读原文；高级物资配给券准确链接安全角落选项。进阶、首次招募直升和留存分开说明，券列出的星级不冒充本局可选人选。父刷新保持两种阅读与筛选，源失效清空并关闭所属深层原文，恢复后手选。'
limits='固定国服原表及实际保存PRTS440806/355079完整正文；前期HTTP200验证页原失败保留且不作机制证据。18份记录不是18个不同券种或当前持有18张。八新典训明确附1张券，但安全角落原文未单列张数；普通同名券不借新典训来源。券适用星级不证明低星或具体成员可进阶，无希望用途不推其它成本全免。完整取得池、当前持有/资格/具体培养和结果仍未知。旧招募/留存配对不重计，战斗藏品效果只作说明，无数值或本局写入、游戏聊天操作、概率或路线建议。P3/P2/P1未完成。'
validation='最终本机29项必要测试和52项原生窗口唯一检查通过，18原券与三类筛选、8准确新典训原文/反向、精确物资选项、两真实非零阅读经父刷新保持、真实公开成员损坏清旧及手选恢复、四层原文所属树关闭。首轮真实入口暴露Dialog参数签名不匹配，已兼容旧parent调用并为新target逐项核对准确来源；首轮旧正文断言仍要求开发节数，已保留原失败及改前源码，改为断言同样的留存边界后重验29/52。七类真实外部操作均零，临时本局与旧计算保持。独立子代理逐张实际查看最终七图，无可见阻断。原测试窗正常更新且可见响应，重启全程私人五路径保持。586旧选择器原序保留，新增2个共588；350全量仅历史，下一定期365。索引25旧单测复用并实际校验本次索引和要求。已真实读取账户窗口93%剩余，其它窗口未知，未触发严格低于15%收尾。不可用私样本/1314/实机游戏聊天未计通过。继续至370后暂停。'
nname='verification/sections/360-necessary-attempt2/process.json';wname='verification/sections/360-native-attempt2/actual/window.json';pname='verification/sections/360-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/360-main-window.json');a=read('verification/sections/360-source-audit.json');v=read('verification/sections/360-root-visual.json')
assert n['passed']and n['methods_ran']==29 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==52 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['all18_original_readings'])==18 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous586_preserved']and len(a['current_selectors'])==588
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section360-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':360,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/360-root-visual.json'),'source_audit':pin('verification/sections/360-source-audit.json'),'original_project_window':pin('verification/sections/360-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/360.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第360节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述360为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第360节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第360节 + '+title+'\n\n'+details+'\n\n继续P3；361从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第360节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
old='全部具名物品的其余取得来源';assert s.count(old)==1;s=s.replace(old,'18进阶券的实际持有、可选人选、培养资格及未列来源；全部具名物品的其余取得来源')
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==359 and cp['next_section']==360
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before360_'+key]=cp.pop(key)
cp.update(completed_sections=360,latest_functional_section=360,next_section=361,batch_status='P3_SECTION360_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第360节 + '+title+'已本机必要验收；普通推送核对后361接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':360,'completion_ref':'p3-section-360','topic':title,'verification':'verification/sections/360.json'});cp['functional_sections_since_latest_requirement'].append(360)
cp['current_section_save']={'section':360,'verification':'verification/sections/360.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':360,'receipt':'verification/sections/360.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':360,'receipt':'verification/sections/360.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=360,next_section=361,next_section_started=False,receipt='verification/sections/360.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
u=read('verification/sections/360-usage.json');cp['policy'].update(current_usage_remaining_percent=u['remaining_percent'],current_usage_receipt='verification/sections/360-usage.json',usage_percent_available=True,usage_wrap_up_triggered=u['triggered'])
cp['current_data_versions'].update({'current_upgrade_ticket_records': 18, 'current_upgrade_relic_sources': 8, 'current_upgrade_actual_eligibility_verified': False})
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section360-handoff:start -->\n## 第360节 + '+title+'\n\n'+details+'\n<!-- section360-handoff:end -->\n')
out=ROOT/'verification/sections/360-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_360.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':360,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next361_started':False,'at_Beijing':now}))
print(json.dumps({'section':360,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
