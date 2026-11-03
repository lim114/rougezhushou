"""Finalize functional320 only after exact complete local full320 acceptance."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return{'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode())

def main():
 title='当前出怪与预置装置条目直达地图格子和有证原图参考'
 change='当前关卡“出怪与条件”页新增条目位置入口，可直接查看基础出怪路线的出生格、移动目标格、再出现格和终点格，以及唯一具名预置装置/单位的声明格；全部184份当前配置逐项核对9440条记录，8198条有明确的名义位置引用。44422条位置与1709条有证原图中心均是跨条目重复引用，不是独立地块或实际出怪数量。玩家从位置列表选择后，左侧标出对应格子，右侧只在319已有核对依据时标出近似中心。654条条件分支出怪不借基础/额外路线数组；等待和消失的占位格不标图，重复或空别名不选对象，越界位置不裁剪到地图。刷新保留条目、位置、页签与阅读，源失效清图清旧、恢复手动选择，重复开窗/切换条目/关闭父窗均关闭旧位置窗。修正首轮新增布局破坏旧分栏阅读检查的问题，保留原分栏关系。'
 limits='这里只查看固定配置的名义格和已有独立中心参考，不证明实际出场、出生偏移/随机范围、装置激活、条件分支路线数组、全局时钟、实际脚点或连续寻路；不连接离散格子为敌人实际路线。1709条中心引用复用319的33配置/13原图部分中心，不是新增测量或扩大完整校准范围，四像素仍仅是旧记录相互差值上限。其余地图完整投影、高台表面与其它格、动态分支和结算、当前敌人完整预计面板、全部事件前置与掉落池等P3缺口保留。P3/P2/P1均未完成，识别优化最后。只读本地固定资料，不操作游戏、不发送聊天，不改本局记忆、私人设置或旧计算版本。'
 necessary='verification/sections/320-necessary-attempt4/process.json';native='verification/sections/320-native-attempt3/actual/window.json';process='verification/sections/320-native-attempt3/process.json';visual='verification/sections/320-root-final-visual.json';audit='verification/sections/320-source-audit.json';main_window='verification/sections/320-main-window.json';full_name='verification/full-320/summary.json'
 n,w,p,v,a,m,f=(read(x)for x in(necessary,native,process,visual,audit,main_window,full_name))
 assert n['passed']and n['exit_code']==0 and n['methods_ran']==40
 assert w['passed']and w['unique_checks']==24 and w['qpa']=='windows'and w['qt_exit_code']==0 and w['verification_window_closed']
 assert len(w['actual_readings'])==5 and len(w['same_identity_refresh_observations'])==2 and all(x==0 for x in w['external_operation_attempts'].values())
 assert p['passed']and p['window_receipt_sha256']==sha(native)
 for val in(n,w):
  assert val['source_sha256_before']==val['source_sha256_after']
  for name,digest in val['source_sha256_after'].items():assert sha(name)==digest,name
 assert v['all_six_final_images_individually_exact_SHA_equal_to_directly_viewed_pixels']and len(v['final_execution_PNG_reuse_by_byte_equality_not_prior_PASS'])==6
 assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
 assert f['after_section']==320 and f['available_checks_passed']and f['scope_not_reduced']and f['actual_validation_attempt']==2
 assert f['maintained_selectors']==509 and f['source_drift']==[]
 freeze=read(f['source_freeze'])
 for name,h in freeze['source_sha256'].items():assert sha(name)==h,name
 assert a['counts']['all_explicit_actions']==9440 and a['counts']['current_stage_configurations']==184
 usage=read('verification/sections/320-preparation/usage-final.json')
 now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section320-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
 validation='实际40项必要检查与24项Windows原生唯一检查通过；5组出怪/装置/分支/空别名/消失资料阅读、两组非零滚动选区保持、实际公开文件损坏清旧/恢复手动选择及父子窗生命周期通过。六张最终PNG逐一与已直接查看像素核对相同，七类游戏采样/聊天/凭证调用零次，临时本局与旧计算上下文不变。到期完整本机验收见verification/full-320/summary.json：509维护选择器、旧52状态及完整typed读回、原30/可用29与35项补充原生窗口范围保留；不可用权限和历史私样本仍不计通过。补全307公共历史展示辅助文件的源码核对范围，保留原始typed核对约束；首次完整执行的布局、旧资料版本检查和截止时间失败均保留原始回执；四个适配脚本保留原数据与窗口断言，布局修复保持1050×720、地图面积不变，第二次完整原范围中的298/311/312超时保留为失败；相同冻结源码下仅重验这三项，298/312按原120秒时限、311按明确记录的300秒含性能测量流程完整通过，未改产品或原验收断言、未重复其它通过项。311原120秒时限未通过；计数中的225次切换来自测试逐项按方向键浏览，不能判断为单次选择的重复刷新故障，正常单次耗时仍未测量。两次完整原始执行和三项复验共同保留全部范围，详情见current-scope-review及keyboard-navigation-timing-explanation。没有删断言、减范围或用旧PASS替代本次执行。原项目测试窗口已正常更新、可见响应，正常关闭至启动期间私人五路径不变。全部测试本机执行，按新要求节约重复云端运行。下次定期全量335。'
 r={'section':320,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(necessary),'methods_run':40,'actual_exit':0},'native_windows_validation':{**pin(native),'process':pin(process),'unique_checks':24,'actual_Qt_exit':0,'actual_source_readings_and_jumps':5,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin(visual),'final_native3_exact_pixel_proof':pin('verification/sections/320-root-final-source-visual.json'),'current_scope_review':pin('verification/full-320/current-scope-review.json'),'keyboard_timing_scope':pin('verification/full-320/keyboard-navigation-timing-explanation.json'),'original_project_window':pin(main_window),'source_audit':pin(audit),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'source_scope':a,'failed_product_validation_attempts':[pin('verification/sections/320-necessary-attempt1/process.json')],'preparation_failure_history':[pin('verification/sections/320-preparation/source-coverage-preflight-before.json')],'failure_explanation':'First necessary40 failed because new wrapper changed action_player parent splitter; restored original splitter parent and placed the new button below it. Full input preflight found307 public helper absent from standard source guard; expanded actual guard instead of removing original typed invariant. Final necessary4/native3 bind stable corrected source. First full40-component execution retained seven real failures: two layout, four historical source pins and one shortened311 deadline. Joined existing reading option checkboxes on a single row retaining exact1050x720; four adapters preserve all original data/UI assertions and bind current123/complete308 source;311 restores its120s original deadline. Second raw full run retained298/311/312 timeouts. Only those same frozen canonical sources rechecked:298/312 original120s,311 explicit300s profiled complete workflow. Its120s timeout remains failed;225 stage changes come from the fixture keyboard traversal, not a proven production duplicate-refresh defect. Original full scope and all raw failures retained, no repeated passing suite.','full_suite_rerun':True,'last_full_receipt':full_name,'current_available_full_validation':pin(full_name),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
 (ROOT/'verification/sections/320.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
 old_wip=subprocess.check_output(['git','show','e320b50d43f713c50941a29ffc1e89c2311761dc:WORK_IN_PROGRESS.md'],cwd=ROOT)
 prefix=('## 第320节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述320为准。\n\n').replace('\n','\r\n').encode();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(prefix+old_wip)
 doc('PROJECT_COMPLETED.md','## 第320节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
 text=(ROOT/'AGENTS.md').read_text('utf8');end=text.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第320节 + '+title+'\n\n'+details+'\n\n继续P3，321衔接节点条件、掉落、当前敌人和固定地图实际剩余缺口。测试优先本地，保留到期完整范围。严格低于15%才开始完整收尾，下次定期全量335。\n'+text[end:])
 text=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=text.index('<!-- current-delivery:start -->');end=text.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',text[:start]+'<!-- current-delivery:start -->\n## 第320节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+text[end:])
 text=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');text=text.replace('取得明确路线绑定后映射检查点；资料位置在其余固定原图上的投影准入仍受地图校准缺口限制','其余未明确绑定的条件路线与检查点；已有基础出怪/唯一预置别名名义格之外的实际脚点、偏移与连续路径仍待依据，原图投影准入仍受地图校准缺口限制',1);text=text.replace('功能跑通后统一优化界面；Windows安装包','功能跑通后统一优化界面；独立核对正常单次选择与连续键盘浏览的响应（311测试逐项遍历产生的225次切换不证明重复刷新故障，含性能测量总耗时不能当单次延迟）；Windows安装包',1);doc('PROJECT_PROGRESS.md',text)
 cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==319 and cp['next_section']==320
 for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section','current_available_full_validation','last_full_validation'):
  if key in cp:cp['historical_before320_'+key]=cp.pop(key)
 cp.update(completed_sections=320,latest_functional_section=320,next_section=321,batch_status='P3_SECTION320_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第320节 + '+title+'已本地完整验收；普通推送核对后321衔接P3实际剩余缺口，未启动。测试优先本机，下次定期全量335。',full_validation_due=False,next_full_validation_after=335)
 cp['sections'].append({'number':320,'completion_ref':'p3-section-320','topic':title,'verification':'verification/sections/320.json'});cp['functional_sections_since_latest_requirement'].append(320)
 cp['current_section_save']={'section':320,'verification':'verification/sections/320.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_section_validation']={'section':320,'receipt':'verification/sections/320.json','necessary_methods_passed':40,'native_isolated_window_checks':24,'actual_source_readings_and_jumps':5,'real_nonzero_refresh_states':2,'full_suite_rerun':True,'last_full_receipt':full_name,'full_source_is_historical305':False}
 cp['latest_section_environment']={'section':320,'receipt':'verification/sections/320.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':True,'last_full_receipt':full_name}
 cp['current_available_full_validation']={'section':320,'receipt':full_name,'available_scope_passed':True,'actual_validation_attempt':2,'source_freeze':f['source_freeze'],'source_freeze_sha256':f['source_freeze_sha256'],'native_windows_game_chat_verified':False}
 cp['last_full_validation']={'after_section':320,'receipt':full_name,'available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,'source_freeze':f['source_freeze'],'source_freeze_sha256':f['source_freeze_sha256']}
 cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=320,next_section=321,next_section_started=False,receipt='verification/sections/320.json',batch_closed=False,next_full_validation_after=335)
 cp['policy'].update(current_usage_remaining_percent=usage['remainingPercent'],current_usage_receipt='verification/sections/320-preparation/usage-final.json',next_full_validation_after=335,verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
 cp['current_batch_commit_policy']['next_full_validation_after']=335
 cp['current_data_versions'].update(current_action_positions_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_action_positions_current_stage_refs=184,current_action_positions_checked_actions=9440,current_action_positions_have_nominal_reference=8198,current_action_positions_complete_path_verified=False)
 (ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
 doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section320-handoff:start -->\n## 第320节 + '+title+'\n\n'+details+'\n<!-- section320-handoff:end -->\n')
 out=ROOT/'verification/sections/320-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_320.py',out/'execution-main-window.py')
 runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
 out=ROOT/'verification/sections/320-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':320,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next321_started':False,'at_Beijing':now}))
 print(json.dumps({'section':320,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
if __name__=='__main__':main()
