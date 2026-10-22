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
parent='e7ce31c7b3d2dd8300db525e7ca5831e961aadff';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='十一种具名奖励的统一取得入口与阅读空间'
change='物品页取得方式新增接入11种具名奖励及11条准确领取选项，连接7类现有完整阅读器：他缚、“剑锤”、一串钱伥、翱翼、虬蜕、猎印、厄运火杆、击坠“神明”、焚毁“文明”、源私钥与犬植浆。原338追忆/同行者/笼控器3种物品6条选项原样保留，统一入口合计14种物品17条选项，不把现有笼控器两来源重复记新增。按准确领取原文和原项明确物品指针核对，源私钥唯一缺指针则保留全文唯一同名参考；剑锤/翱翼/虬蜕仅允许外层中文引号差异且仍须明确指针，不按序号/模糊名称配对。持有笼控器与领取猎印、消耗/交付源私钥与领取源私钥、复原文明付自然物与等待结果领取、接取悬赏与胜利生效、犬植浆与行动力分开显示，不重复扣费/合计或把持有/图标当领取。每种物品可逐条打开准确现有事件情景/原项，原前置未知则保留原件范围，不补父菜单；全部默认不选中、不认定本局领取，件数未知不补1。缩短取得选项列表最高120逻辑像素，为正文留空间，并按准确按钮名提示而不误称下方入口。真实版本父刷新保留两组非零阅读/选区、选项、页签与已前进的子原文；重复打开/取消选择/父失效及实际主窗关闭清理所属整树。新源坏清旧及子窗，恢复须手选；新源坏不移除原338独立三物品。未新增奖励机制、完整掉落池、地图校准或数值计算。'
limits='直接复用固定bee3国服七类现有阅读器、准确原项与完整已归档文献，当前PRTS剑锤及引擎配件目录核对名称/来源；旧笼控器来源已覆盖，未重复推进。没有新下载HTML/图片，没有重新猜机制。10条原项有明确物品指针，源私钥仍只按唯一同名全文对应，缺指针不冒称已补齐。原件与文献的前置/父关系、当前服务器完整资格、独立领取件数、实际消费/领取、所有其它来源和完整奖励池仍未知；焚毁文明不在领取时再扣自然物，源私钥两处99不合计，悬赏胜利与叠加不由持有推定。新清单11条及原6条只是已核对取得资料，14物品不等于全游戏物品覆盖。不操作游戏、不发聊天、不支付/领取、不改本局记忆、地图、计算数值或私人设置，不给路线建议/排序/概率。P3/P2/P1未完成，识别最后。'
validation='最终本机39项相关测试与Windows原生临时MainWindow48项唯一检查通过，完整资料构建字节一致；14种物品的17条新旧领取选项全部实际点击并核对准确事件/情景/原项，七类适配器不串项，原6条保持，默认未选择、数量/资格/领取未知。缺指针与99不合计、持有条件不冒充领取/消耗、等待结果不二次付自然物、犬植浆准确原图/效果、短列表留正文空间、两组真实非零阅读/选区及页签经真实版本父刷新保留、子原文已前进位置保持、重复打开/取消选择清子、新源坏清旧/手选恢复且旧338不受影响、伪造目标拒绝和实际主窗关闭整树通过。最终7张PNG主代理逐张查看。初次准备将猎印误选cargo8，被明确指针/名称严格门拦下，保留原稿与退出1，按原项cargo12更正，未放宽匹配。39测试首轮1条旧338断言仍认为源私钥无取得入口而失败；按新准确领取原文更新并保留不纳交付的检查后39项第二轮通过。原生第一轮47项通过，视觉发现单条列表挤占小窗正文及方向提示不准，保留当时源码/回执后改最高120及准确按钮名；最终39第三轮与原生48第二轮按最终源码重新通过，不伪称已通过轮次失败。七类真实外部操作零，临时本局/旧计算上下文不变；原项目测试窗正常更新，可见响应且未最小化，正常重启全过程私人五路径不变，未确认前台。561旧维护选择器原序保留，现563。只跑本机必要/原生检查，云端不重复；335全量属历史，下次350。索引实现未变，复用历史25项单测，当前要求/断点/来源与索引实际校验。'
nname='verification/sections/347-necessary-attempt3/process.json';wname='verification/sections/347-native-attempt2/actual/window.json';pname='verification/sections/347-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/347-main-window.json');a=read('verification/sections/347-source-audit.json');v=read('verification/sections/347-root-visual.json')
assert n['passed']and n['methods_ran']==39 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==48 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==17 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous561_preserved']and len(a['current_selectors'])==563
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section347-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':347,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':39,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':48,'actual_Qt_exit':0,'new_named_acquisitions':11,'new_named_items':11,'new_upstream_reader_kinds':7,'old338_choices_retained':6,'combined_items':14,'all_acquisition_entries_exercised':17,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/347-root-visual.json'),'source_audit':pin('verification/sections/347-source-audit.json'),'original_project_window':pin('verification/sections/347-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/347.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第347节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述347为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第347节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第347节 + '+title+'\n\n'+details+'\n\n继续P3；348从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。统一取得入口不替代完整获取池、服务器前置、实际领取或完整地图核验。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第347节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其它具名物品的已核对取得入口';assert s.count(old)==1;s=s.replace(old,'尚未逐项核对的其余具名发放来源（含出发/归来、战后选择与其它阶段）');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==346 and cp['next_section']==347
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before347_'+key]=cp.pop(key)
cp.update(completed_sections=347,latest_functional_section=347,next_section=348,batch_status='P3_SECTION347_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第347节 + '+title+'已本机必要验收；普通推送核对后348接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':347,'completion_ref':'p3-section-347','topic':title,'verification':'verification/sections/347.json'});cp['functional_sections_since_latest_requirement'].append(347)
cp['current_section_save']={'section':347,'verification':'verification/sections/347.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':347,'receipt':'verification/sections/347.json','methods_run':39,'native_isolated_window_checks':48,'new_named_acquisitions':11,'new_named_items':11,'new_upstream_reader_kinds':7,'old338_choices_retained':6,'combined_items':14,'all_acquisition_entries_exercised':17,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':347,'receipt':'verification/sections/347.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=347,next_section=348,next_section_started=False,receipt='verification/sections/347.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_named_rewards_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_named_rewards_new_acquisitions=11,current_named_rewards_new_items=11,current_named_rewards_upstream_readers=7,current_named_rewards_combined_items=14,current_named_rewards_combined_rows=17,current_named_rewards_complete_pool=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section347-handoff:start -->\n## 第347节 + '+title+'\n\n'+details+'\n<!-- section347-handoff:end -->\n')
out=ROOT/'verification/sections/347-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_347.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':347,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next348_started':False,'at_Beijing':now}))
print(json.dumps({'section':347,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
