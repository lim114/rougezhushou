from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone, timedelta
import json, runpy, subprocess, shutil
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return {'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
parent='1b509f69e83b3876dd2ea779346d0d4fb2ea789b'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='当前调谐仪式的逐步选项、三种削弱与材料来源作战'
change='新增当前调谐仪式6段对话与11个选项、泪之聚落3段对话与2个选项的逐步阅读。三组指定材料/源私钥替代方式逐项对应同一削弱，不重复叠加；分别说明首次灾厄之口保护危朽、避免待部署区封锁和降低伤害，不把降低当归零。三件材料可分别打开倾囊资助原选项、当前回滚文明具名奖励条文和无效验尸固定地图；另设畸症相关资料入口，明确不是即时进入且未套用削弱。版本页的对应情景、原选项和4件材料可准确进入；源私钥仅打开总览，不自动指定用途。父页刷新保留两组非零阅读与已开材料页，切换/重复开窗/源失效/父窗关闭清理旧子窗，交换资料单独失效不影响仪式和首领资料。'
limits='逐格复用实际下载且核对SHA的BWIKI352356两张完整原表与PRTS433770完整第三结局DOM；当前网页文字重新查证材料来源和三种作用，新441984原HTML的TLS失败保留，不冒称新下载成功。选项按完整文案及明确后续对话对应，不按编号猜父情景；泪之聚落采用当前游戏的倾囊资助，旧文献倾囊相助差异保留。完整对照bee3当前记录与a550旧基准，文献流程不当游戏脚本或服务器实际资格。交付件数、源私钥连续替代/库存消耗、实际削弱和完整发放条件仍未知，不假定1件或一把完成三项，也不改敌人或旧计算。无效验尸只在已注明的光明之末条件下为材料来源，不当所有普通作战必掉。P3/P2/P1均未完成，识别最后；不操作游戏、聊天或私人状态，不推荐路线。'
validation='本机首次55项必要检查中54项通过、1项失败，原因是测试误写分组编号group-5而真实为5。仅将该断言改成从明确原选项查对应组，保留其余验证；完整重建初版测试字节并核对原SHA，确认运行源码未变，只单独重验失败1项通过，其余54项不重复执行。最终34项Windows原生唯一检查通过，实际主窗口验证全部9情景/13选项、三种材料来源、两份固定地图、替代未知、交换源单独失效、核心资料实际损坏清旧/恢复手选、父窗和子窗生命周期。两组真实非零滚动/选区经父页刷新保留，八张最终截图全部直接查看，七类采样/聊天/凭证调用为零，临时本局和旧计算上下文不变。原项目窗口正常更新可见响应，正常关闭至启动期间私人五路径不变。515旧维护选择器原序保留，现517；不重跑已通过且未变的全量或索引单测，历史320范围、失败及不可用原件保留，不当本节全量，下次335。'
nname='verification/sections/324-necessary-attempt3/process.json';wname='verification/sections/324-native-attempt1/actual/window.json';pname='verification/sections/324-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/324-main-window.json');a=read('verification/sections/324-source-audit.json');v=read('verification/sections/324-root-visual.json');scope=read('verification/sections/324-check-scope.json')
assert n['passed']and n['methods_ran']==1 and scope['passed']and scope['initial_passed']==54
assert w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==34 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==8 and len(w['actual_readings'])==13 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['directly_viewed'])==8 and a['ordered_previous515_preserved']and len(a['current_selectors'])==517
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section324-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':324,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run_on_final_test':1,'initial55_receipt':'verification/sections/324-necessary-attempt2/process.json','initial_passed54_reused':True,'initial_failed1_corrected_and_rechecked':True,'scope':pin('verification/sections/324-check-scope.json'),'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':34,'actual_Qt_exit':0,'documented_flow_scenes':9,'documented_flow_choices':13,'material_source_types':3,'fixed_related_maps':2,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/324-root-visual.json'),'source_audit':pin('verification/sections/324-source-audit.json'),'original_project_window':pin('verification/sections/324-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/324.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT)
prefix=('## 第324节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述324为准。\n\n').replace('\n','\r\n').encode('utf8');(ROOT/'WORK_IN_PROGRESS.md').write_bytes(prefix+old_wip)
doc('PROJECT_COMPLETED.md','## 第324节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第324节 + '+title+'\n\n'+details+'\n\n继续P3；325从当前事件前置、完整奖励池和固定地图的实际剩余缺口接续，未启动。测试优先本机，保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第324节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余具名奖励来源、完整掉落池与零件池范围';new='调谐仪式完整前置、实际交付件数与源私钥连续替代及消耗、三件材料的实际领取条件/件数和削弱生效核验、其余具名奖励来源、完整掉落池与零件池范围';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==323 and cp['next_section']==324
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before324_'+key]=cp.pop(key)
cp.update(completed_sections=324,latest_functional_section=324,next_section=325,batch_status='P3_SECTION324_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第324节 + '+title+'已本机必要验收；普通推送核对后325接续P3实际剩余缺口，未启动。下次定期全量335。',full_validation_due=False)
cp['sections'].append({'number':324,'completion_ref':'p3-section-324','topic':title,'verification':'verification/sections/324.json'});cp['functional_sections_since_latest_requirement'].append(324)
cp['current_section_save']={'section':324,'verification':'verification/sections/324.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':324,'receipt':'verification/sections/324.json','initial55_passed54_failed1':True,'failed1_rechecked_passed':True,'other54_reused_not_rerun':True,'native_isolated_window_checks':34,'flow_scenes':9,'flow_choices':13,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':324,'receipt':'verification/sections/324.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=324,next_section=325,next_section_started=False,receipt='verification/sections/324.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=69,current_usage_receipt='verification/sections/324-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_ritual_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_ritual_document_revision=352356,current_ritual_independent_document_revision=433770,current_ritual_documented_scenes=9,current_ritual_documented_choices=13,current_ritual_effects_applied=False,current_ritual_consumption_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section324-handoff:start -->\n## 第324节 + '+title+'\n\n'+details+'\n<!-- section324-handoff:end -->\n')
out=ROOT/'verification/sections/324-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_324.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/324-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':324,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next325_started':False,'at_Beijing':now}))
print(json.dumps({'section':324,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
