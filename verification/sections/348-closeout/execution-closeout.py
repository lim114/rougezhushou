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
parent='8edcef2cb415bd31932ca206f9b4565529461f75';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='十张首领原图的入口目标标志与十六份配置对应'
change='固定地图位置预览新增10张完整原图、16份精确首领配置的可见入口与保护目标标志对应，覆盖铁腕迷思、哀悼铁腕、光荣远征、赤金厄运、狂热敬虔、冰冷流亡、永无安宁、痛苦将息、混沌源阶理论、失恒常量；前六各自普通/余径配置分开绑定。46处原图观测形成75组配置—标志对应，所选配置原mapData全部入口/目标标志逐一对应；完整地形、相机字段、关卡记录与原图元数据每份独立核对，不按同名或同图套用。可从当前配置预览打开格子/原图对照，选格后原图显示该可见标志的近似位置，两个窗口尺寸保持源图比例；其它格子清标、原图点击不反推、不插值连线。现有明确出怪条目的名义格只有恰好对应已观测标志时才获得图上入口，偏移、实际脚点、分支与全局时钟保留未知。混沌源阶理论/失恒常量首条路线终点为第4行第7列，未观测标志则保持不画，不硬贴到蓝点。原319的33配置/13原图局部地面中心、337两份熄日8标志范围保持，当前184引用中仍有133份完全没有位置绑定；本批16份也只有标志，没有其余地块或完整投影。真实父刷新保留两组非零阅读/选区、标志/页签，整源坏清原图/格图/标记且恢复须手选，不影响旧319/337；重复打开与关闭父作战/主窗清理所属地图窗口。'
limits='复用固定bee3国服完整关卡导出及de6cfb原图，10张完整512×286原图由主代理直接查看，按整个入口/目标拓扑与原mapData索引对应，再在明确可见符号框内统计红/蓝像素。人工近似与取色来自同一图片，不是独立外部标定；内部8像素一致性门不是绝对误差承诺。一处暗红标志默认130只检出6个亮边像素，90检出64个符号像素且与原人工69,173一致，人工位置和一致性门不变，保留初失败和完整阈值比较。不把符号、格中心、敌人脚点混用，不给其它地块、出生偏移/随机范围、完整坐标矩阵、反向点击或路线连线。当前PRTS普通/余径同名条目仅辅助区分资料，准确绑定由各份冻结关卡/地形/图片建立；没有新下载图片、采游戏或新运行时机制。新增16份完整地块与绝对精度、旧33/337其余地块及其余133份都仍待核验。不操作游戏、不发聊天、不改本局记忆、地图、数值或私人设置，不给路线建议/排序/概率。P3/P2/P1未完成，识别最后。'
validation='最终本机39项相关测试与Windows原生临时MainWindow37项唯一检查通过，资料构建字节一致。75组配置—标志对应全部实际点格并在两种窗口尺寸核对原图比例；10张原图各有最终窗口截图，另有旧337保护目标、出怪名义终点和坏源清空，共13张最终PNG主代理逐张查看。完整地形/相机/关卡/图片漂移拒绝、每个清单成员损坏拒绝、格子布尔值/越界/颜色或阈值错误拒绝、所有未观测格无位置、旧319/337保持与133未绑定范围、所有基础出怪条目只按准确观测格对应且两份首路线终点明确无标志、真实父刷新两组非零阅读/选区及选择/页签、重复打开/父作战/主窗关闭与坏源清旧/手选恢复均通过。初次观测构建在永无安宁暗红标志的一致性门失败，保留原件及实际退出1，独立分析阈值后修正该处明确取色阈值，未移动人工估计或放宽门。39测试首轮仅新写的一项误设首路线终点均为蓝点而失败，产品正确保留两份未标格；按原路线反例改为逐条核对所有基础条目及明确两负例后39第二轮通过，产品/观测未因测试改动。原生首轮37已通过；因引用的测试文件变动，按最终完整源绑定重跑原生第二轮37，不把首轮伪称失败。七类真实外部操作零，临时本局/旧计算上下文不变。原项目测试窗正常更新，可见响应且未最小化，正常重启全过程私人五路径不变，未确认前台。563旧维护选择器原序保留，现565。只跑本机必要/原生检查，云端不重复；335全量属历史，下次350。索引实现未改，复用历史25单测，当前要求/断点/来源与索引实际校验。'
nname='verification/sections/348-necessary-attempt2/process.json';wname='verification/sections/348-native-attempt2/actual/window.json';pname='verification/sections/348-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/348-main-window.json');a=read('verification/sections/348-source-audit.json');v=read('verification/sections/348-root-visual.json')
assert n['passed']and n['methods_ran']==39 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==37 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==13 and len(w['actual_readings'])==75 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==13 and a['ordered_previous563_preserved']and len(a['current_selectors'])==565
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section348-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':348,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':39,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':37,'actual_Qt_exit':0,'new_stage_bindings':16,'new_original_images':10,'new_visible_symbol_observations':46,'stage_symbol_pairs':75,'original319_bindings_retained':33,'original337_bindings_retained':2,'remaining_current_unbound_stages':133,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/348-root-visual.json'),'source_audit':pin('verification/sections/348-source-audit.json'),'original_project_window':pin('verification/sections/348-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/348.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第348节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述348为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第348节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第348节 + '+title+'\n\n'+details+'\n\n继续P3；349从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。可见标志对应不替代完整地图投影、实际脚点、偏移或完整路线核验。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第348节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='以及其它149引用';assert s.count(old)==2;s=s.replace(old,'以及本批16份配置/10张原图在可见入口/目标以外的地块、标志到实际脚点与绝对精度，以及其它133引用');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==347 and cp['next_section']==348
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before348_'+key]=cp.pop(key)
cp.update(completed_sections=348,latest_functional_section=348,next_section=349,batch_status='P3_SECTION348_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第348节 + '+title+'已本机必要验收；普通推送核对后349接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':348,'completion_ref':'p3-section-348','topic':title,'verification':'verification/sections/348.json'});cp['functional_sections_since_latest_requirement'].append(348)
cp['current_section_save']={'section':348,'verification':'verification/sections/348.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':348,'receipt':'verification/sections/348.json','methods_run':39,'native_isolated_window_checks':37,'new_stage_bindings':16,'new_original_images':10,'new_visible_symbol_observations':46,'stage_symbol_pairs':75,'original319_bindings_retained':33,'original337_bindings_retained':2,'remaining_current_unbound_stages':133,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':348,'receipt':'verification/sections/348.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=348,next_section=349,next_section_started=False,receipt='verification/sections/348.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(boss_map_markers_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',boss_map_markers_stage_bindings=16,boss_map_markers_images=10,boss_map_markers_observations=46,boss_map_markers_stage_pairs=75,current_remaining_stages_without_position_binding=133,boss_map_markers_full_projection_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section348-handoff:start -->\n## 第348节 + '+title+'\n\n'+details+'\n<!-- section348-handoff:end -->\n')
out=ROOT/'verification/sections/348-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_348.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':348,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next349_started':False,'at_Beijing':now}))
print(json.dumps({'section':348,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
