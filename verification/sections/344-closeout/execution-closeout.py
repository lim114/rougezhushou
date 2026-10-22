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
parent='5832cf5829e9b6090b5a7d79fb78e3b1c4e26705';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='回滚文明完整阶段、准确原文与交出物目录入口'
change='新增固定bee3国服回滚文明完整阅读：14处文献对话位置、13处选项，藏品/零件各自首次、再次领取和停止路径分开，重复文案保留独立阶段，六条完整路径各自结束而不无限循环。保留46段原对话与44份原选项，其中36份有明确目的对话、8份仅是没有nextSceneId的同文交换候选；90处版本条目各自打开完整原文，原对话不猜菜单，原选项仅沿明确后续，不按编号恢复交换转换或首次/再次类型。声带、手掌、首次同类和层数文献条件清楚展示，实际账户资格未知。仅复原文明显示默认未知的自然物件数对照，0/1不打开后续，2可查阅；领取焚毁文明不再扣2件、不借其它领取项的1件补数量，并有当前准确图片与效果说明。仅已明确的藏品交出/继续分支可打开既有323当前284件能否交出目录，领取、零件和类型未明的原继续项完全隐藏入口；目录不是奖励池或本局库存。真实父刷新保留两组非零阅读/选区、条件、页签及子目录筛选/选中项；可选目录源损坏只清目录，保留已证事件，恢复须手开；坏图文字回退、整源坏清旧、重复打开/父页/实际主窗关闭清理两入口整树。节点接入42条准确旧新对话关系，共36目录组、34标题、18类阅读器。'
limits='复用321真实下载的BWIKI352356完整回滚文明表和已归档PRTS433770原文，重新核对当前BWIKI与PRTS条件段；完整匹配固定bee3/baseline原件，不新下载HTML/图片。现有305旧流程与323当前目录范围保持，不作为重复完成；新增的是完整当前文献阶段及准确原件/目录入口。8份同文交换候选无明确后续，不当作已证服务器父关系；普通领取选项明确1件，但焚毁文明仅明确名称，独立数量未知。真实交换阶段、同文记录归属、声带/手掌账户状态、首次类型/剩余次数、实际交出与完整换入池、随机自然物成员/顺序、领取及服务器完整资格未知。只查资料，不支付/领取/改本局记忆、地图、数值或私人设置，不操作游戏或发聊天，不给路线建议/排序/概率。P3/P2/P1未完成，识别最后。'
validation='本机49项相关测试首轮通过；之后只有窗口验收脚本补上实际点击重新核对的恢复步骤，产品、测试、构建器和数据均字节未变，一致性证明保留，49项不重复运行。构建重新按当前冻结源码核对，字节一致。最终Windows原生临时MainWindow61项唯一检查通过，90处原文全部实际打开，36个明确后续和8个同文候选逐项核对；六条文献路径、自然物0/1/2边界及不重复扣费/猜数量、具名原图、仅相关藏品分支目录入口/284条非奖励池、真实子目录筛选保持与独立坏源恢复、两组真实非零阅读/选区及条件/页签经父刷新保留、坏图回退/整源清旧、手选恢复、节点版本提示与主窗同时关闭两套事件/目录窗口树通过。8张最终实际PNG主代理逐张查看。初次构建误纳通用离开同文案，被数量门拦截后改为本事件明确目的地筛选，保留原件和失败。原生首轮55检查/90原文后在最后恢复因未手点重新核对而StopIteration，整体失败保留；补上真实点击后完整重验61项。两个启动观察调用超时，各实际任务分别退出1/0，重跑因已确认失败及修复，不因观察超时。七类真实外部操作零，临时本局/旧计算上下文不变。实际项目测试窗正常更新，可见响应且未最小化，私人五路径整个正常重启不变，未确认前台。555旧维护选择器原序保留，现557。仅本机验证，云端不重复；335全量属历史，下次350。索引实现未改，复用历史25单测，当前要求/断点/来源与索引实际校验。'
nname='verification/sections/344-necessary-attempt1/process.json';wname='verification/sections/344-native-attempt2/actual/window.json';pname='verification/sections/344-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/344-main-window.json');a=read('verification/sections/344-source-audit.json');v=read('verification/sections/344-root-visual.json')
assert n['passed']and n['methods_ran']==49 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==61 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==8 and len(w['actual_readings'])==90 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
eq=read('verification/sections/344-native-fixture-repair/source-equivalence.json');assert eq['passed']and eq['unit_tests_reused_not_rerun']and eq['necessary_methods']==49
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():
  if result is n and name==eq['only_changed_file']:
   assert h==eq['differences'][name]['then']and sha(name)==eq['differences'][name]['now'];continue
  assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==8 and a['ordered_previous555_preserved']and len(a['current_selectors'])==557
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section344-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':344,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':49,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':61,'actual_Qt_exit':0,'original_scenes':46,'original_choices_preserved':44,'explicit_destination_choices':36,'full_literal_sacrifice_candidates':8,'document_contexts':14,'document_choice_groups':13,'current_named_item':1,'exact_original_version_entries':90,'catalogue_groups':36,'catalogue_titles':34,'reader_kinds':18,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/344-root-visual.json'),'source_audit':pin('verification/sections/344-source-audit.json'),'original_project_window':pin('verification/sections/344-main-window.json'),'source_sha256':w['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
r['necessary_validation'].update(native_fixture_only_changed_after_unit_execution=True,scope_equivalence=pin('verification/sections/344-native-fixture-repair/source-equivalence.json'),unit_tests_reused_not_rerun=True,original_whole_freeze_not_claimed_current=True)
(ROOT/'verification/sections/344.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第344节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述344为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第344节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第344节 + '+title+'\n\n'+details+'\n\n继续P3；345从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。完整文献阶段不替代同文原件归属、交换执行或本局领取核对。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第344节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='回滚文明首/再次交换与同文案记录的实际归属、完整换入池及账户选择、焚毁“文明”独立领取件数';assert s.count(old)==1;s=s.replace(old,'回滚文明同文交换候选的实际分支归属与转换阶段、声带/手掌账户状态及剩余次数、实际交出与完整换入池及账户选择、随机2自然物成员/顺序与焚毁“文明”独立领取件数');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==343 and cp['next_section']==344
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before344_'+key]=cp.pop(key)
cp.update(completed_sections=344,latest_functional_section=344,next_section=345,batch_status='P3_SECTION344_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第344节 + '+title+'已本机必要验收；普通推送核对后345接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':344,'completion_ref':'p3-section-344','topic':title,'verification':'verification/sections/344.json'});cp['functional_sections_since_latest_requirement'].append(344)
cp['current_section_save']={'section':344,'verification':'verification/sections/344.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':344,'receipt':'verification/sections/344.json','methods_run':49,'native_isolated_window_checks':61,'original_scenes':46,'original_choices_preserved':44,'explicit_destination_choices':36,'full_literal_sacrifice_candidates':8,'document_contexts':14,'document_choice_groups':13,'current_named_item':1,'exact_original_version_entries':90,'catalogue_groups':36,'catalogue_titles':34,'reader_kinds':18,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':344,'receipt':'verification/sections/344.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=344,next_section=345,next_section_started=False,receipt='verification/sections/344.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_reconstruction_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_reconstruction_original_scenes=46,current_reconstruction_original_choices_preserved=44,current_reconstruction_explicit_choices=36,current_reconstruction_same_literal_candidates=8,current_reconstruction_document_contexts=14,current_reconstruction_document_options=13,current_reconstruction_original_entry_views=90,current_node_reader_groups=36,current_node_reader_titles=34,current_node_reader_kinds=18,current_reconstruction_actual_exchange_or_server_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section344-handoff:start -->\n## 第344节 + '+title+'\n\n'+details+'\n<!-- section344-handoff:end -->\n')
out=ROOT/'verification/sections/344-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_344.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':344,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next345_started':False,'at_Beijing':now}))
print(json.dumps({'section':344,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
