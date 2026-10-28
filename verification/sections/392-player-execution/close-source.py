from pathlib import Path
from datetime import datetime,timezone
import runpy,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts')]
f=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'));read=f['read'];write=f['write'];pin=f['pin'];source=f['source'];block=f['block'];git=f['git']
assert git('branch','--show-current').decode().strip()=='codex/p2-development'
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==391
native=read('verification/sections/392-player-window/window.json');unit=read('verification/sections/392-player-checks/process.json');proc=read('verification/sections/392-player-window-process/process.json');reg=read('verification/sections/392-regression391-window/window.json');rp=read('verification/sections/392-regression391-process/process.json');runtime=read('verification/sections/392-main-window/window.json')
assert all(x['passed']for x in[native,unit,proc,reg,rp,runtime])
assert source()==native['source_sha256_after']==unit['source_sha256_after']==reg['source_sha256_after']==runtime['source_sha256_after']
assert native['unique_checks']==34 and reg['unique_checks']==39 and runtime['private_five_paths_unchanged']and runtime['desktop_full_display_actually_reviewed']
assert not any(native['external_operation_attempts'].values())and not any(reg['external_operation_attempts'].values())
images=native['screenshots']+reg['screenshots'];assert len(images)==6
for item in images:assert pin(item['file'])['sha256']==item['sha256']
write('verification/sections/392-visual-agent-review.json',{'section':392,'reviewer':'root','actual_view_image_calls':6,'images':images,'blocking_visual_issues':[], 'scope':'Final six exact isolated UI images individually viewed; previous thumbnail label clipping corrected and prior original images retained. Public fixtures only.','actual_game_accuracy_claimed':False})
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert selectors==read('verification/sections/391-source-audit.json')['current_selectors']+['tests.test_player_map_interaction_392']
write('verification/sections/392-source-audit.json',{'section':392,'passed':True,'current_selectors':selectors,'ordered_previous_preserved':True,'source_sha256':source(),'numeric_model_changed':False,'historical_denominator_renormalized_by_current_candidates':False})
art=read('rouge/data/map-event-art/sources.json');stats=read('verification/sections/392-public-statistics-recheck.json');assert stats['passed']and stats['same_counts_as_bundled_388']
write('verification/sections/392-public-source.json',{'section':392,'passed':True,'authorization':'verification/sections/388-data-scope.json','public_GET_only':True,'event_art_manifest':pin('rouge/data/map-event-art/sources.json'),'event_art_files':len(art['sources']),'public_statistics_live_recheck':pin('verification/sections/392-public-statistics-recheck.json'),'data_updated_at':stats['metadata']['updatedAt'],'DLC2_applicability_confirmed':False,'source_code_from_site_copied_or_executed':False,'private_data_uploaded':False})
write('verification/sections/392-usage.json',{'remaining_percent':92,'used_percent':8,'window_duration_mins':10080,'secondary_window':None,'triggered':False,'strict_below_threshold':15,'source':'actual get_usage_limits response at the start of this turn','account_identifier_saved':False})
title='节点类型位置高亮、图文悬浮卡与视频逐项验收'
change='地图增加左侧五类节点图标与可取消的单类筛选，按已读、模板、候选和过去类型分别高亮；仅对有依据的候选位置显示对应层/步数的历史比例，保留原分母，不给已读、固定和通过节点虚构概率。悬停出现可固定的图文卡，列精确类型候选和按节点/楼层整理的事件、作战，接入25张有来源插图，点击在地图侧栏打开对应资料，换层清除旧卡；浅色地图外框、最近记录资源条和中文玩家说明同时整合。按全片画面与字幕建立VIDEO_PARITY.md，明确终态逐项对齐以及尚未实现的交互、资料和统计。'
limits='图上为历史节点比例，当前DLC与本图条件概率仍未核验。真实游戏读取、完整事件条件及概率、商店快照、藏品悬停、全局快捷键、完整历史复盘与个人统计仍未全部完成；详见视频对照与待办。视频Agent为后续计划，不能冒称已有接口。不上传个人数据，不自动选路；P3/P2/P1未全部完成，识别最后。'
receipt={'section':392,'kind':'functional_section','title':title,'new_capability':change,'limitations':limits,'necessary_validation':pin('verification/sections/392-player-checks/process.json'),'unit_tests_run':62,
 'native_windows_validation':{**pin('verification/sections/392-player-window/window.json'),'unique_checks':34,'process':pin('verification/sections/392-player-window-process/process.json')},
 'previous_player_contract_regression':{**pin('verification/sections/392-regression391-window/window.json'),'unique_checks':39,'process':pin('verification/sections/392-regression391-process/process.json')},
 'root_visual_review':pin('verification/sections/392-visual-agent-review.json'),'public_sources':pin('verification/sections/392-public-source.json'),'video_review':pin('verification/sections/392-video-review.json'),'video_parity_document_sha256':pin('VIDEO_PARITY.md')['sha256'],'runtime_test_window':pin('verification/sections/392-main-window/window.json'),
 'source_sha256':source(),'full_suite_rerun':False,'last_full_receipt':'verification/full-380/summary.json','last_full_is_historical_for_current_changes':True,'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_state_included':False,'cloud_publication_binding':'enclosing_commit','recorded_at_UTC':datetime.now(timezone.utc).isoformat()}
write('verification/sections/392.json',receipt)
cp.update(completed_sections=392,latest_functional_section=392,next_section=393,batch_status='PLAYER_SECTION392_PUBLICATION_PENDING')
cp['next_action']='继续按VIDEO_PARITY.md逐项对齐：全局呼出/收起、藏品池与库存场景联动、完整本地复盘和个人统计；P3概率/版本证据缺口保留。识别最后，下一定期全量395。'
cp['sections'].append({'number':392,'completion_ref':'player-section-392','topic':title,'verification':'verification/sections/392.json'})
cp['current_section_save']={'section':392,'verification':'verification/sections/392.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['policy'].update(new_functional_sections_paused=False,development_paused_by_latest_user_request=False,stop_after_section=None,current_user_batch_target_section=None,batch_target_section=None,current_user_batch_completed=False,public_statistics_enabled=True,current_usage_remaining_percent=92,current_usage_receipt='verification/sections/392-usage.json',usage_percent_available=True,usage_wrap_up_triggered=False,video_final_parity_required=True,video_parity_document='VIDEO_PARITY.md')
cp['current_batch'].update(status=cp['batch_status'],completed_sections=392,next_section=393,next_section_started=False,batch_closed=False,receipt='verification/sections/392.json')
cp['current_section_validation']={'section':392,'receipt':'verification/sections/392.json','full_suite_rerun':False,'last_full_receipt':'verification/full-380/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':392,'native_windows_verified':True,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-380/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['windows_native_validation']='当前392：62项必要检查、新功能34项原生窗口唯一检查及上一批39项窗口契约回归通过，六张最终隔离原图逐张审阅。原项目地图与工具条已实际可见响应，正常重启区间五份私人路径保持。历史输入时序失败与标签裁剪原件保留，不冒充通过；380全量为历史，下一到期395。'
cp['functional_sections_since_latest_requirement'].append(392);cp['cloud_publication_closeout']={'section':392,'current_commit_kind':'functional section pending actual publication','next_section_started':False,'development_paused':False};write('DEVELOPMENT_CHECKPOINT.json',cp)
body='## 当前第392节 + '+title+'\n\n'+change+'\n\n'+limits+'\n\n62项必要检查、新功能34项原生窗口唯一检查与上一批39项窗口契约回归通过；两份隔离窗口的九类外部操作均零。主代理逐张审阅六张最终原图，视频按15张全段时间顺序图板、全段提取字幕和4张原尺寸交互画面重新核对；没有音轨转写或逐帧播放声明。原项目地图窗口与工具条经实际桌面确认可见，正常关闭/启动区间五份私人路径仅摘要比对保持。\n\n路标公开节点统计已重新联网读取，仍标记2026-10-01且与随包计数一致；DLC2适用性未证。原图卡标签裁剪已修复，悬停输入/卡片重开顺序的失败检查原件分开保留，不计通过。380全量仅历史，下一到期395；本节没有缩减全量范围。\n\n<!-- player-publication-pending -->普通推送与远端核对待完成。'
for name in('AGENTS.md','WORK_IN_PROGRESS.md'):block(name,body)
requirements='## 当前视频效果一致性要求 · 2026-10-28\n\n最高优先五条项目要求继续有效。用户最新要求为继续推进，并确保充分了解参考录像，最终效果与视频一致；终态验收按VIDEO_PARITY.md逐项核对布局、交互、自动关联、节点与图文资料、公开统计、笔记、本地复盘及个人统计，不以基础地图或换标题代替完整效果。仅有画面宣称、计划演示或来源缺失的能力分别记录，不能提前标为实现。视频全局快捷键、悬停联动、历史步骤/资源、库存筛选与统计卡等未完成项保留待办。\n\n保留本项目黑流树海国服、Windows原生客户端与后台只读范围。公开路标数据已获授权读取、展示、本机缓存及随仓库分发，全部个人对局/截图/聊天/培养信息禁止上传。节点概率和联网统计必须继续做，实际数据的版本、条件、分母和权重口径需核对，当前历史比例不能冒充DLC2或本图条件概率。只提供节点信息，不推荐或自动选路、不操作游戏、不发送开发测试聊天、不清空本局或覆盖私人配置。每节更新要求、索引及对照清单，同源码普通推送并核对远端。\n\n'
block('PROJECT_REQUIREMENTS.md',requirements+body);block('PROJECT_COMPLETED.md',body)
p=R/'PROJECT_PROGRESS.md';text=p.read_text('utf8');prefix='| P3 | 视频效果对齐剩余交互 |';text='\n'.join(line for line in text.splitlines()if not line.startswith(prefix))+'\n'
row=prefix+' 全局快捷键与呼出/收起、游戏窗口覆盖层；场景关联的敌人头像/资料快捷条；藏品悬停查池和库存多类筛选；队伍/零件箱视图；真实商店库存/刷新快照；完整场景笔记呈现与用户主动导出；真实历史对局逐层/逐步、奖励与资源变化复盘，完整记录支持下的个人统计与本机展示卡。各项范围、视频时间与剩余验收见VIDEO_PARITY.md；识别覆盖/耗时仍最后处理。 |'
text=text.replace('| --- | --- | --- |','| --- | --- | --- |\n'+row,1);p.write_text(text,encoding='utf8',newline='\n')
runpy.run_path(str(R/'scripts/update_cloud_index.py'))['update'](R)
assert read('CLOUD_INDEX.json')['completed_sections']==392
p=R/'verification/sections/392-player-execution/close-source.py';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(Path(__file__).read_bytes())
print(json.dumps({'section':392,'unit_tests':62,'native_unique':34,'regression_contract_unique':39,'ordered_selectors':len(selectors),'public_pending':True},ensure_ascii=False))
