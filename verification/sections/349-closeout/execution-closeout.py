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
parent='0325c4989dc6d3089954ead52b0f9b730805b31f';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='三件结局关键藏品的取得条件与准确原文入口'
change='物品页为谒日之祈、破碎噩兆、生命蓝图新增三条取得记录及专门条件面板，分别连接险路尽头完整阅读器和手术祭坛、制图桌文献流程，打开后直接选中准确原选项。原文虽未写藏品名，三份原项的明确物品指针与当前藏品、条件记录和原文逐一核对，不按图标或相似名称补配。谒日之祈仅显示主层、节点、更新后解锁与源石锭；破碎噩兆仅显示节点、首次倒下后的无标记不期而遇及本局救援是否已使用；生命蓝图不显示无依据的条件输入。默认未知，9/10源石锭边界不影响整个事件存在，救援半目标生命上限不混同当前生命，取整未知，制图桌完整资格不按普通节点假定。可打开准确现有流程，已前进的原文选项、手动条件和两个非零阅读/页签经真实父刷新保持；取消选择、坏源、重复打开和父主窗关闭清理所属整树。原338六条/三物品与347十一条/十一物品原样保留，统一物品取得入口现为十七物品二十条已核对选项，不是完整获取池。'
limits='复用固定bee3国服原件及316条件、321完整文献、339险路尽头的冻结来源，另查当前PRTS结局文献印证三项取得选项；资料不是当前服务器执行证明。原描述只写获得收藏品，明确itemId作为对应依据；独立件数仍未知，不补1件。完整出现前置、服务器资格、真实费用扣除/领取/生效、半生命上限取整、其余取得来源及全部掉落池仍待核对。手动条件仅本页对照，不写本局，也不把原文窗口自己的对照值自动视为同一状态。不新增机制、计算、地图绑定、路线建议或概率；P3/P2/P1未完成，识别最后。'
validation='最终本机49项相关测试与Windows原生临时MainWindow44项唯一检查通过，资料构建字节一致。逐条打开三项准确领取原文、仅相关条件、费用9/10边界、一次救援条件和制图桌未知、两组非零阅读/页签/手动条件及已前进原文经真实版本父刷新保持、坏源清整树/恢复手选、伪造目标拒绝与实际主窗关闭；原338/347回归保留。最终4张原生截图主代理逐张复查，七类真实外部操作零，临时本局/旧计算上下文不变；原项目测试窗正常更新，私人五路径保持。首轮49测试中两项新界面测试发现入口把原选项编号与现有文献选项编号混比，保留实际失败和改前源码，改为分别核对原文、明确指针及文献单一对应后第二轮49通过；原生首轮43通过，视觉复查修正对子窗口按钮名的提示，最终49第三轮、原生44第二轮按最终源码通过。原39项取得入口回归无失败。不伪称已通过轮次失败。只在本机运行，335全量历史保留，下次350。索引实现未改，复用历史25单测，实际执行本节索引和要求绑定校验。'
nname='verification/sections/349-necessary-attempt3/process.json';wname='verification/sections/349-native-attempt2/actual/window.json';pname='verification/sections/349-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/349-main-window.json');a=read('verification/sections/349-source-audit.json');v=read('verification/sections/349-root-visual.json')
assert n['passed']and n['methods_ran']==49 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==44 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==4 and len(w['actual_readings'])==3 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==4 and a['ordered_previous565_preserved']and len(a['current_selectors'])==567
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section349-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':349,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'new_item_acquisition_rows':3,'new_items':3,'specialized_condition_panels':3,'exact_original_flow_targets':3,'old338_rows_retained':6,'old347_rows_retained':11,'combined_items':17,'combined_rows':20,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/349-root-visual.json'),'source_audit':pin('verification/sections/349-source-audit.json'),'original_project_window':pin('verification/sections/349-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/349.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第349节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述349为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第349节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第349节 + '+title+'\n\n'+details+'\n\n继续P3；350从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。三项领取入口不替代完整获取池、当前服务器资格或实际领取。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第349节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='尚未逐项核对的其余具名发放来源（含出发/归来、战后选择与其它阶段）';assert s.count(old)==1;s=s.replace(old,'其余尚未逐项核对的具名发放来源（出发/归来、战后选择与其它阶段），以及三件结局关键藏品的其它取得来源、完整服务器资格、独立件数及实际发放');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==348 and cp['next_section']==349
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before349_'+key]=cp.pop(key)
cp.update(completed_sections=349,latest_functional_section=349,next_section=350,batch_status='P3_SECTION349_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第349节 + '+title+'已本机必要验收；普通推送核对后350接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':349,'completion_ref':'p3-section-349','topic':title,'verification':'verification/sections/349.json'});cp['functional_sections_since_latest_requirement'].append(349)
cp['current_section_save']={'section':349,'verification':'verification/sections/349.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':349,'receipt':'verification/sections/349.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'new_item_acquisition_rows':3,'new_items':3,'specialized_condition_panels':3,'exact_original_flow_targets':3,'old338_rows_retained':6,'old347_rows_retained':11,'combined_items':17,'combined_rows':20,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':349,'receipt':'verification/sections/349.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=349,next_section=350,next_section_started=False,receipt='verification/sections/349.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(critical_reward_origins_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',critical_reward_origins_items=3,critical_reward_origins_choices=3,unified_named_acquisition_items=17,unified_named_acquisition_rows=20,complete_acquisition_pool_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section349-handoff:start -->\n## 第349节 + '+title+'\n\n'+details+'\n<!-- section349-handoff:end -->\n')
out=ROOT/'verification/sections/349-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_349.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':349,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next350_started':False,'at_Beijing':now}))
print(json.dumps({'section':349,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
