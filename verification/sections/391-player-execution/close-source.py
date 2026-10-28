from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,runpy,sys,subprocess
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts')]
f=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'));read=f['read'];write=f['write'];pin=f['pin'];source=f['source'];block=f['block'];git=f['git']
n=391;assert git('branch','--show-current').decode().strip()=='codex/p2-development'
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==390
native=read('verification/sections/391-player-window/window.json');unit=read('verification/sections/391-player-checks/process.json');process=read('verification/sections/391-player-window-process/process.json');runtime=read('verification/sections/391-main-window/window.json')
assert native['passed']and unit['passed']and process['passed']and runtime['passed']
assert native['source_sha256_after']==unit['source_sha256_after']==runtime['source_sha256']==source()
assert native['unique_checks']==39 and len(native['screenshots'])==4 and not any(native['external_operation_attempts'].values())
assert runtime['private_five_paths_unchanged']and runtime['desktop_full_display_actually_reviewed']
review={'section':391,'reviewer':'root','actual_view_image_calls':4,'images':native['screenshots'],'blocking_visual_issues':[],
 'scope':'Final exact four isolated Qt renders individually viewed after source-specific checks. Map pictures use explicitly labelled public templates, never private game samples.',
 'interaction_evidence':'verification/sections/391-player-window/window.json','game_accuracy_or_eligibility_proven_by_images':False}
for item in review['images']:assert pin(item['file'])['sha256']==item['sha256']
write('verification/sections/391-visual-agent-review.json',review)
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();previous=read('verification/sections/390-source-audit.json')['current_selectors'];assert selectors==previous+['tests.test_player_reference_391']
write('verification/sections/391-source-audit.json',{'section':391,'passed':True,'current_selectors':selectors,'ordered_previous_preserved':True,'source_sha256':source(),'numeric_model_changed':False})
data=read('research/public-reference-391/snapshot.json');art=read('rouge/data/map-art/sources.json')
write('verification/sections/391-public-source.json',{'section':391,'passed':True,'authorization':'verification/sections/388-data-scope.json','read_scope':'Fixed public GETs only. No private data, query, login, image or account supplied. Runtime refresh is explicit, never automatic.',
 'provenance':data['provenance'],'normalized_snapshot':pin('research/public-reference-391/snapshot.json'),'version_pool_counts':{k:len(v)for k,v in data['versions'].items()},'named_items':len(data['items']),
 'map_art_manifest':pin('rouge/data/map-art/sources.json'),'art_files':len(art['sources']),'sprites':len(art['sprites']),
 'code_copied_or_executed_from_site':False,'DLC2_declared_by_pool_source':False,'candidate_frequency_is_claimed_reward_probability':False})
write('verification/sections/391-usage.json',{'remaining_percent':93,'used_percent':7,'window_duration_mins':10080,'secondary_window':None,'triggered':False,'source':'actual get_usage_limits response in this turn','account_identifier_saved':False,'strict_below_threshold':15})
title='视频式浮动工具条、整层图标地图与路标离线资料'
change='小窗改为七图标横向浮动工具条，按需展开地图、藏品与设置。地图使用来源明确的游戏节点图标和背景，展示整层连线，可切换本局已记录楼层、缩放、点击节点展开分组事件/作战/功能资料并准确跳转作战预览；保留所选节点、条目及历史空地原类型，不把固定模板当已读，不把全目录当作单节点候选。接入路标本体70池、DLC1的72池及427件具名物品、楼层与树洞入口条件资料；支持本机搜索和手动公开更新，频率分子/分母与重叠来源分开显示，不上传本局。'
limits='源池只声明本体/DLC1，未证明DLC2完整；本图已知节点约束后的条件概率、完整事件/结算掉落统计仍待核验。地图只提供资料，不推荐或自动选路；当前真实游戏识别与聊天未测。示例地图仅用于隔离界面验收。'
receipt={'section':391,'kind':'functional_section','title':title,'new_capability':change,'limitations':limits,
 'necessary_validation':pin('verification/sections/391-player-checks/process.json'),'unit_tests_run':45,
 'native_windows_validation':{**pin('verification/sections/391-player-window/window.json'),'unique_checks':39,'process':pin('verification/sections/391-player-window-process/process.json')},
 'root_visual_review':pin('verification/sections/391-visual-agent-review.json'),'public_sources':pin('verification/sections/391-public-source.json'),'runtime_test_window':pin('verification/sections/391-main-window/window.json'),
 'source_sha256':source(),'full_suite_rerun':False,'last_full_receipt':'verification/full-380/summary.json','last_full_is_historical_for_current_changes':True,
 'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_state_included':False,'cloud_publication_binding':'enclosing_commit','recorded_at_UTC':datetime.now(timezone.utc).isoformat()}
write('verification/sections/391.json',receipt)
cp['historical_before391_current_batch']=cp['current_batch'];cp.update(completed_sections=391,latest_functional_section=391,next_section=392,batch_start_section=391,batch_target_section=None,batch_status='PLAYER_SECTION391_PUBLICATION_PENDING')
cp['next_action']='继续P3：核验路标资料对DLC2的覆盖和本图条件统计，完善地图资料交互；不上传本局、不推荐路线。下一定期全量395，P3/P2/P1未全部完成，识别最后。'
cp['sections'].append({'number':391,'completion_ref':'player-section-391','topic':title,'verification':'verification/sections/391.json'})
cp['current_section_save']={'section':391,'verification':'verification/sections/391.json','scope':'current_functional_section','binding':'enclosing_commit'}
cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['policy'].update(new_functional_sections_paused=False,development_paused_by_latest_user_request=False,stop_after_section=None,current_user_batch_target_section=None,batch_target_section=None,current_user_batch_completed=False,public_statistics_enabled=True,current_usage_remaining_percent=93,current_usage_receipt='verification/sections/391-usage.json',usage_percent_available=True,usage_wrap_up_triggered=False)
cp['policy'].pop('paused_after_completed_section',None)
cp['current_batch']={'start':391,'end':None,'next_full_validation_after':395,'status':cp['batch_status'],'completed_sections':391,'next_section':392,'next_section_started':False,'batch_closed':False,'receipt':'verification/sections/391.json'}
for k in('current_available_full_validation','last_full_validation'):
 cp[k]['historical_for_current_changed_source']=True
 if k=='current_available_full_validation':cp[k]['current_worktree_validation_authority']=False
cp['current_section_validation']={'section':391,'receipt':'verification/sections/391.json','full_suite_rerun':False,'last_full_receipt':'verification/full-380/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':391,'native_windows_verified':True,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-380/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['windows_native_validation']='当前391：45项必要检查、39项原生Qt唯一检查通过；四张隔离原图主代理实际查看。原项目测试工具条在完整Windows-MCP桌面图中可见，Win32核对响应及五份私人路径保持；不证明游戏或聊天。380全量为历史，下一到期395。'
cp['functional_sections_since_latest_requirement'].append(391)
cp['cloud_publication_closeout']={'section':391,'current_commit_kind':'functional section pending actual publication','next_section_started':False,'development_paused':False}
write('DEVELOPMENT_CHECKPOINT.json',cp)
body='## 当前第391节 + '+title+'\n\n'+change+'\n\n'+limits+'\n\n45项必要检查与39项原生窗口唯一检查通过，九类外部操作零；主代理逐张查看四张最终隔离原图。真实项目测试工具条已启动并在Windows-MCP完整桌面图中实际确认，五份私人路径仅摘要对比不变，原截图未公开。裁剪截图与后台短生命周期启动的早期观察保留为范围有限的历史，不作为当前桌面确认。380完整回执为历史，本节未重跑全量，下一到期395。\n\n<!-- player-publication-pending -->普通推送与远端核对待完成。\n\n用户已明确继续并要求地图达到参考视频的呈现方式，旧390暂停已解除；未指定新的数字终点。P3/P2/P1仍未全部完成，识别最后。'
for name in('AGENTS.md','WORK_IN_PROGRESS.md'):block(name,body)
block('PROJECT_REQUIREMENTS.md','## 当前地图与公开资料要求 · 2026-10-28\n\n项目级最高五条要求继续有效。参考用户本地录像：采用可拖动置顶横向图标工具条，面板按需展开；地图应为游戏风格的整层地图，保留实际位置对应、楼层切换、图标与连接、点击节点展开分组资料、历史记录和刷新阅读状态。不得以示意图坐标列表替代最终效果；未揭示、模板固定、本局历史和当前已读必须区分。节点概率与公开联网统计为当前要求，显示真实来源、样本、分母、版本和适用条件；不得把候选出现频率当实际领取概率或把旧统计冒充DLC2条件概率。已获授权读取路标节点/事件/掉落数据、展示、本机缓存及随仓库分发，仅抓取公开资料在本机计算，禁止上传任何个人对局、游戏画面、聊天、培养或本局状态。每节功能、必要验收、项目要求与索引一起普通推送并核对远端。\n\n'+body)
block('PROJECT_COMPLETED.md',body)
p=R/'PROJECT_PROGRESS.md';s=p.read_text('utf8');s=s.replace('以及事件/掉落完整统计；只读取公开数据，不上传本局。','以及DLC2事件/完整掉落和结算统计；核对已接入本体/DLC1样本的来源、版本与重叠口径；只读取公开数据，不上传本局。')
s=s.replace('移除其他干员仍能看到的灰色机械师时序等专属工具按钮，保留已正确隐藏的培养/技能条件表单；','')
s=s.replace('节点只列候选及条件，不要求生成概率。','节点资料列候选及条件；按最新要求继续核验节点概率与公开统计，不上传个人对局，不推荐路线。')
p.write_text(s,encoding='utf8',newline='\n')
public=R/'research/public-reference-391/README.md';public.write_text('# 路标公开资料快照\n\n按用户明确授权读取并随项目分发。原始游戏内容权利属于原权利人；路标档案馆为本次公开资料来源。来源 URL、下载字节及 SHA256 见 snapshot.json 的 provenance；游戏节点图标和背景的独立来源/摘要见 rouge/data/map-art/sources.json。仅保存所需的数据，不复制或运行网站程序代码。\n\n本体70池、DLC1的72池分开查询；427件具名物品不代表当前完整藏品。资料未声明DLC2覆盖。候选出现频率按出现次数/对应分母计算，不是实际领取概率；统计记录数不等于候选总数，不叠加重叠来源。树洞只按来源明确的进入层3/4/5筛选，事件仍有前置条件，条件资料不表示本局已满足。\n\n运行时先读随包资料；点击“更新公开资料”才请求两个固定公开JSON。无个人数据上传、账号或图像输入。网络失败保留已验证本机缓存。地图美术仅为显示装饰，不证明生成规则、当前位置或真实游戏读取。\n',encoding='utf8',newline='\n')
runpy.run_path(str(R/'scripts/update_cloud_index.py'))['update'](R)
assert read('CLOUD_INDEX.json')['completed_sections']==391
runner=R/'verification/sections/391-player-execution/close-source.py';runner.parent.mkdir(parents=True,exist_ok=True);runner.write_bytes(Path(__file__).read_bytes())
print(json.dumps({'section':391,'actual_checks':45,'native_unique':39,'ordered_selectors':len(selectors),'public_pending':True},ensure_ascii=False))
