from pathlib import Path
from datetime import datetime,timezone
import runpy,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts')]
f=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'));read=f['read'];write=f['write'];pin=f['pin'];source=f['source'];block=f['block'];git=f['git']
assert git('branch','--show-current').decode().strip()=='codex/p2-development'
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==392
unit=read('verification/sections/393-player-checks/process.json');native=read('verification/sections/393-player-window/window.json');reg=read('verification/sections/393-regression392-window/window.json');runtime=read('verification/sections/393-main-window/window.json')
for p in ('393-player-window-process','393-regression392-process'):assert read('verification/sections/'+p+'/process.json')['passed']
assert all(v['passed']for v in (unit,native,reg,runtime))
assert source()==unit['source_sha256_after']==native['source_sha256_after']==reg['source_sha256_after']==runtime['source_sha256_after']
assert native['unique_checks']==reg['unique_checks']==34 and not any(native['external_operation_attempts'].values())and not any(reg['external_operation_attempts'].values())
assert runtime['private_five_paths_unchanged']and runtime['desktop_full_display_actually_reviewed']
images=native['screenshots']+reg['screenshots'];assert len(images)==3
for item in images:assert pin(item['file'])['sha256']==item['sha256']
write('verification/sections/393-visual-agent-review.json',{'section':393,'reviewer':'root','actual_view_image_calls':3,'images':images,'blocking_visual_issues':[],'scope':'Final three isolated exact PNGs individually viewed; settings, map and pinned hover. Actual desktop also viewed through Windows MCP, private desktop image not published.','actual_game_accuracy_claimed':False})
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert selectors==read('verification/sections/392-source-audit.json')['current_selectors']+['tests.test_player_hotkey_393']
write('verification/sections/393-source-audit.json',{'section':393,'passed':True,'current_selectors':selectors,'ordered_previous_preserved':True,'source_sha256':source(),'numeric_model_changed':False})
write('verification/sections/393-hotkey-sources.json',{'section':393,'sources':[
{'url':'https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey','established':'RegisterHotKey associates an owned window with a combination, posts WM_HOTKEY, supports MOD_NOREPEAT, and reports registration failure. F12 and Windows combinations are not offered.'},
{'url':'https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-unregisterhotkey','established':'Explicit release of the matching registered hotkey on its owner thread.'},
{'url':'https://doc.qt.io/qtforpython-6/PySide6/QtCore/QAbstractNativeEventFilter.html','established':'Distinguishes Windows native messages; an application-wide filter was investigated but not retained. Final implementation receives only its own hidden QWidget messages.'}],
'final_strategy':'Stable hidden receiver HWND, RegisterHotKey MOD_NOREPEAT, QWidget nativeEvent only; no input hooks, game messages or keyboard injection. No default plain-Tab takeover.',
'validation_boundary':'Real Windows OS register/conflict/release; synthetic WM_HOTKEY to owned receiver. No physical keyboard cross-application claim.',
'failure_records':{'wrong_unittest_selector':'393-first-selector-error','initial_hover_regression':'393-hover-regression-first-failure','filter_bool_hover':'393-filter-bool-hover-failure','receiver_reopen_test':'393-receiver-reopen-test-failure','stale_pre_layout_coordinate':'393-prelayout-hover-failure'},
'correction':'Initial attribution of hover failure to native filtering was not established. Changing the filter alone did not fix it. Final receiver avoids app-wide filtering; test now resolves coordinates after native layout settles. Retained failed outputs do not count as passes.'})
write('verification/sections/393-usage.json',{'remaining_percent':90,'used_percent':10,'window_duration_mins':10080,'secondary_window':None,'triggered':False,'strict_below_threshold':15,'source':'actual get_usage_limits response at start of this turn','account_identifier_saved':False})
title='快捷键呼出与收起、阅读保持和冲突保护'
change='工具设置接入可设置、启停的Windows全局快捷键，默认Ctrl+Alt+Space，明确同意占用后也可选视频中的单独Tab。按一次收起所有助手窗口，再按一次恢复地图、阅读和未保存笔记；收起取消待弹出的悬浮卡。独立隐藏窗口接收快捷键，不接管全应用消息；组合冲突保留原设置，退出释放注册。只在用户应用时保存独立本机快捷键配置，启动不写默认配置。'
limits='已验证真实Windows注册、冲突、释放以及投递到助手自己接收窗口的响应；没有向游戏发送按键，不冒称实体键盘跨应用验收。藏品悬停、完整复盘/个人统计、当前版本条件概率、真实读取及其它VIDEO_PARITY.md差距仍保留；不上传个人数据、不操作游戏、不推荐路线。P3/P2/P1仍未全部完成，识别最后。'
receipt={'section':393,'kind':'functional_section','title':title,'new_capability':change,'limitations':limits,'necessary_validation':pin('verification/sections/393-player-checks/process.json'),'unit_tests_run':56,'native_windows_validation':{**pin('verification/sections/393-player-window/window.json'),'unique_checks':34,'process':pin('verification/sections/393-player-window-process/process.json')},'previous_player_contract_regression':{**pin('verification/sections/393-regression392-window/window.json'),'unique_checks':34,'process':pin('verification/sections/393-regression392-process/process.json')},'root_visual_review':pin('verification/sections/393-visual-agent-review.json'),'public_sources':pin('verification/sections/393-hotkey-sources.json'),'video_parity_document_sha256':pin('VIDEO_PARITY.md')['sha256'],'runtime_test_window':pin('verification/sections/393-main-window/window.json'),'source_sha256':source(),'full_suite_rerun':False,'last_full_receipt':'verification/full-380/summary.json','last_full_is_historical_for_current_changes':True,'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_state_included':False,'cloud_publication_binding':'enclosing_commit','recorded_at_UTC':datetime.now(timezone.utc).isoformat()}
write('verification/sections/393.json',receipt)
cp.update(completed_sections=393,latest_functional_section=393,next_section=394,batch_status='PLAYER_SECTION393_PUBLICATION_PENDING')
cp['next_action']='继续按VIDEO_PARITY.md对齐藏品悬停查池/库存筛选、场景敌人入口、队伍与零件、完整本地复盘和个人统计；P3概率/版本证据缺口保留。识别最后，下一定期全量395。'
cp['sections'].append({'number':393,'completion_ref':'player-section-393','topic':title,'verification':'verification/sections/393.json'})
cp['current_section_save']={'section':393,'verification':'verification/sections/393.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['policy'].update(current_usage_remaining_percent=90,current_usage_receipt='verification/sections/393-usage.json',usage_wrap_up_triggered=False)
cp['current_batch'].update(status=cp['batch_status'],completed_sections=393,next_section=394,next_section_started=False,batch_closed=False,receipt='verification/sections/393.json')
cp['current_section_validation']={'section':393,'receipt':'verification/sections/393.json','full_suite_rerun':False,'last_full_receipt':'verification/full-380/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':393,'native_windows_verified':True,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-380/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['windows_native_validation']='当前393：56项必要检查、新功能34项原生窗口唯一检查与地图34项回归通过，三张最终隔离原图逐张查看。原项目工具条与设置窗实际可见响应；五份私人路径启动区间保持。未向游戏发送按键或聊天；物理按键跨应用未测。原失败分开保留，380全量仅历史，下一到期395。'
cp['functional_sections_since_latest_requirement'].append(393);cp['cloud_publication_closeout']={'section':393,'current_commit_kind':'functional section pending actual publication','next_section_started':False,'development_paused':False};write('DEVELOPMENT_CHECKPOINT.json',cp)
body='## 当前第393节 + '+title+'\n\n'+change+'\n\n'+limits+'\n\n56项必要检查、快捷键34项和地图34项原生窗口唯一检查通过；两组隔离窗口九类外部操作均零。三张最终原图逐张查看，原项目测试窗口已实际可见响应，启动区间五份私人路径保持。新增快捷键配置不写入仓库。380全量是历史，下一到期395，完整选择器前缀保持。\n\n首次错误测试名、悬停时序失败与接收器销毁后错误重用的测试失败原件分开保留。最初将悬停失败直接归因于过滤器尚不成立；最终采用独立接收窗口，并在布局稳定后重新求鼠标位置，两组验收实际通过。注册与自己窗口消息响应不冒充向游戏或实体键盘测试。\n\n<!-- player-publication-pending -->普通推送与远端核对待完成。'
for name in ('AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):block(name,body)
old=(R/'PROJECT_REQUIREMENTS.md').read_text('utf8').split('<!-- player-batch-current:start -->',1)[1].split('## 当前第392节',1)[0].strip()
old=old.replace('视频全局快捷键、悬停联动、历史步骤/资源、库存筛选与统计卡等未完成项保留待办。','藏品悬停联动、历史步骤/资源、库存筛选与统计卡等未完成项保留待办。全局快捷键默认Ctrl+Alt+Space，单键Tab必须由用户明确选择并同意占用；冲突不抢占、退出清理，保持阅读与未保存内容。')
block('PROJECT_REQUIREMENTS.md',old+'\n\n'+body)
p=R/'PROJECT_PROGRESS.md';text=p.read_text('utf8');text=text.replace('全局快捷键与呼出/收起、游戏窗口覆盖层；','游戏窗口覆盖层；');p.write_text(text,encoding='utf8',newline='\n')
runpy.run_path(str(R/'scripts/update_cloud_index.py'))['update'](R)
p=R/'verification/sections/393-player-execution/close-source.py';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(Path(__file__).read_bytes())
print(json.dumps({'section':393,'unit':56,'native':34,'map_regression':34,'ordered_selectors':len(selectors),'publication_pending':True}))
