from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from copy import deepcopy
import ast,ctypes,difflib,json,re,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='dc5fbe145f99e52c746ee672ce9955b12cd747b5';B=R/'verification/maintenance/current-enemy-forecast-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,v):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=v.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in a],[s.rstrip('\r\n')for s in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
 p.write_bytes(''.join(b).encode('utf8'))
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
changed=['rouge/current_battle_reference.py','rouge/current_battle_view.py','rouge/current_enemy_traits.py','rouge/current_enemy_forecast.py','rouge/enemy_overview.py','rouge/player_map.py','rouge/player_map_reader.py','rouge/player_scene_battle.py','rouge/recognition.py']
unchanged=['rouge/app.py','rouge/battle_preview.py','rouge/enemy_environment.py','rouge/enemy_panel.py','rouge/enemy_reference_construction.py','rouge/run_modifiers.py','rouge/run_config.py','rouge/run_state.py','rouge/account_cache.py','rouge/capture.py','rouge/page_ocr.py','rouge/recognition_cache.py','rouge/dynamic_ocr.py','AGENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data']).strip()
before=ast.parse(old('rouge/recognition.py'));after=ast.parse((R/'rouge/recognition.py').read_bytes())
old_private=next(n for n in ast.walk(before)if isinstance(n,ast.FunctionDef)and n.name=='_read')
removed=[n for n in old_private.body if isinstance(n,ast.If)and ast.unparse(n.test)=='image is None or image.size == 0'];assert len(removed)==1
old_private.body.remove(removed[0]);assert ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False)
ids=[]
for folder,count in(('tests-closure',62),('ocr-entry-checks',91)):
 result=read(prefix+folder+'/results.json');assert result['passed']and result['tests_run']==count and result['failed']==result['errors']==0 and not result['skipped']and not result['forbidden_external_calls']
 assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
 cases=re.findall(r'^test_\w+ \(([^)]+)\)',(R/(prefix+folder+'/stderr.txt')).read_text('utf8'),re.M);assert len(cases)==len(set(cases))==count;ids+=cases
assert len(ids)==len(set(ids))==153
matrix=read(prefix+'matrix-latest/results.json');assert matrix['passed']and matrix['reference_count']==2060 and matrix['counts']=={'qualified':1049,'unqualified':1011}
assert read(prefix+'matrix-latest-process.json')['actual_observed_exit']==0
assert len(matrix['difficulty_profiles'])==16 and all(r['four_fields_equal']for r in matrix['difficulty_profiles'])
assert all(r['complete_current_total']is None for r in matrix['rows'])
assert read(prefix+'matrix-process.json')['actual_observed_exit']==1
native=read(prefix+'native-latest/receipt.json');assert native['passed']and native['unique_checks']==32 and not any(native['external_operation_attempts'].values())and read(prefix+'native-latest-process.json')['actual_observed_exit']==0
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256'],n
assert not read(prefix+'native/receipt.json')['passed']and read(prefix+'native-process.json')['actual_observed_exit']==1
images=native['screenshots']+read(prefix+'native-latest/images.json')['images'];earlier=read(prefix+'native-final/receipt.json')['screenshots']+read(prefix+'native-final/images.json')['images'];assert len(images)==len(earlier)==6
for row,prior in zip(images,earlier):
 raw=(R/row.get('file',row.get('path'))).read_bytes();assert sha256(raw).hexdigest()==row['sha256']==prior['sha256']
write(prefix+'native-latest/visual-review.json',{'images':images,'six_paths_five_distinct_byte_images':len({r['sha256']for r in images})==5,'all_six_native_final_paths_actual_images_individually_viewed':True,'latest_native_images_whole_bytes_equal_to_previously_viewed_final':True,'no_new_visual_claim_without_exact_bytes':True,'gallery_default_collapsed_and_plain_large_numbers_checked':True,'whole_video_parity_claimed':False})
profile=read(prefix+'ocr-profile/results.json');assert profile['passed']and len(profile['rows'])==8 and read(prefix+'ocr-profile-process.json')['actual_observed_exit']==0
assert [r['page']for r in profile['rows']]==['unknown']*8
distinct=[r for r in profile['rows']if r['reuse']=='none'];assert len(distinct)==2
live=read(prefix+'live-window-closure/window.json');assert live['passed']and live['private_six_paths_unchanged']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256'],n
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
first=read('.cache/current-enemy-forecast-review-live-status.json');time.sleep(2.2);last=read('.cache/current-enemy-forecast-review-live-status.json');assert last['toolbar_visible']and last['elapsed_since_launch']>first['elapsed_since_launch']
write(prefix+'live-window-closure/desktop-review.json',{'actual_Windows_MCP_snapshot_and_image_view':True,'region':[1716,1164,2130,1218],'test_window_visible_responding_and_Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
for n in ('.cache/run_current_enemy_forecast_checks.py','.cache/audit_current_enemy_forecasts.py','.cache/run_current_enemy_matrix.py','.cache/verify_current_enemy_forecast_native.py','.cache/run_current_enemy_forecast_native.py','.cache/profile_recorded_ocr_pipeline.py','.cache/run_recorded_ocr_profile.py'):(B/Path(n).name).write_bytes((R/n).read_bytes())
(B/'tests-closure/test-source.py').write_bytes((R/'tests/test_current_enemy_forecast_review.py').read_bytes())
(B/'ocr-entry-checks/test-source.py').write_bytes((R/'tests/test_ocr_cache_review.py').read_bytes())
write(prefix+'input-compatibility.json',read('.cache/current-enemy-input-audit.json'))
write(prefix+'preliminary-four-field-comparison.json',read('.cache/current-enemy-reuse-comparison.json'))
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'unchanged_numeric_models_data_state_capture_and_OCR_cache':[pin(n)for n in unchanged],'formula_or_source_data_changed':False,'method':'Whole stage SHA, four explicit core attributes, constructor mode, precise enemy identity/tier and four difficulty fields must agree before calling existing enemy_preview. No numerical model copied/reimplemented.','source_boundary':{'current_stages':184,'legacy_stages':105,'whole_stage_bytes_equal':102,'whole_stage_bytes_changed':3,'new_stages':79,'current_enemy_references':2060,'qualified_references_at_declared_conditions':1049,'unqualified':1011,'not_actual_enemy_counts':True},'unknown_totals':'Full current totals remain unknown; subtotal excludes complete relic/skill/phase effects. Grade16, new/changed references and missing sources stay unimplemented.','new_interface':'Separate forecast map consumed by existing seven-column classified tree and exact enemy reader, automatically fed only live reading conditions. Historical readers receive none; changed current conditions preserve selection/folds.','UI':'Default gallery collapsed to avoid duplicate portrait rows; figures use digit groups/two decimals, raw internal pending keys stay in metadata and player notes use Chinese.','recognition_entry':'Remove one duplicate empty-image check from private ScreenReader._read; public read unchanged and all other AST identical. Valid private calls still verified by existing page/seed tests; two new public boundary/cache tests.','OCR_profile_limitations':'Four requested reference-video positions produced only two distinct full frames and all routes were unknown. Two non-reuse reads 6135.80/3899.22ms; OCR2787.93/2184.35ms and run2342.49/1595.65ms. Six exact-frame reuse reads about2ms. Not a live-game benchmark, routing accuracy proof or speed improvement. Need correct client-area corpus before generalizing/optimizing unknown-route run cost.','retained_failed_validation':'Initial matrix expectation1050 omitted actual unknown tier in ro6_b_4_b/enemy_1177_dufrbl_2; production properly returned1049, expectation corrected without weakening checks. Initial native fixture deliberately changed isolated run but failed to remove its own fixture changes before outer equality gate; fixed verifier restoration, no actual run touched.','REA_scope':'Complete Python source and actual Qt/OCR runtime evidence under REA skill; no new REA tool invocation or whole-program/bytecode-complete claim.','new_low_probability_defenses_added':False,'full_program_or_video_complete':False})
title='复用已核验输入的敌人环境分项，自动跟随本局并整理数值表'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'necessary_test_groups':[62,91],'unique_tests_total':153,'failed':0,'errors':0,'skipped':0,'native_primary_unique_checks':32,'latest_native_image_paths':6,'distinct_latest_native_image_bytes':5,'matrix_stages':184,'matrix_references':2060,'qualified_references':1049,'unqualified_references':1011,'numeric_formula_changed':False,'complete_current_totals_unknown':True,'test_window_updated':True,'private_six_paths_unchanged_during_startup':True,'source_review':pin(prefix+'source-review.json'),'full_validation_rerun':False,'full440_only_original_frozen_source':True,'whole_program_complete':False,'whole_existing_code_compliant':False,'whole_video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'OCR_pipeline_profile_reads':8,'OCR_pipeline_distinct_input_frames':2,'OCR_pipeline_speedup_or_game_accuracy_claimed':False,'recognition_priority':'concurrent','game_operated':False,'chat_sent':False,'private_data_included':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob verification required'})
text('research/current-enemy-forecast-review-20261031/README.md','''# 当前敌人环境分项与视频表格回顾

当前固定184关中，105关在原计算基准中有记录，102份关卡原件整字节相同、3份变化，另79关新增。没有直接把相同名字当成相同数值。逐引用比较四项明确属性、构造模式、精确身份/类别及当前0–15难度的四字段后，1049条引用可复用已有enemy_preview环境分项，1011条仍不可用；2060是候选引用数，不是实际敌人数，也不是2060种不同敌人。

公式、旧计算器、当前游戏数据和私态代码未改，默认不给白值。总览复用原头像与普通/精英/领袖分组，增加生命、攻击、防御、法抗四分项；详情列出难度/区域条件。只读本局最近保存的条件，改变条件不重置阅读/折叠。历史预览不借当前条件；来源失效清分项，恢复后重新核验。完整本局总量仍未知：未完整计入藏品、技能和阶段。保密等级16、其它模式、新/变更配置及缺失/不符来源未完成；不能因输入相同或旧结果一致当作独立机制校准、当前服务器或实际游戏面板证明。

对照本机视频108秒原帧的敌人表格，重复上方图册默认收起，每行头像与图册可展开功能保持；大数用数字分组、最多两位小数，不显示指数格式。359条引用的原内部脚本提示改为普通玩家可理解的待计算说明，原始标识仍在元数据/原始资料中。完整表格列、地图/出怪/藏品影响、布局/比例及全视频效果尚未对齐，不能称与原片完全相同。

必要检查两组62/91项，合并去重153项均通过；第二组含公有读取空输入和完整帧复用两项新检查。ScreenReader私有_read中重复空图检查已删除，公有read仍先校验，其余AST保持。当前完整数据矩阵184关2060引用的可复用结果与原模型相同；这只证明复用映射/兼容，不证明1049条完整实际数值。Windows原生最新32项通过，6条图片路径含5份不同整字节原图；六条最终图逐一实际查看，后续封口图逐字节相等复用审阅。原项目测试小窗已更新且可见响应，六私人路径启动期间保持，零游戏操作/真实聊天/个人上传。

原始失败均保留：初始四字段审计1050未包含类别，实际模型还正确排除了净浊之焰的当前未确认类别，最终1049；不是放宽生产校验。首轮原生失败是验证器未移除自己在隔离局内的刻意fixture改动，改验证器后完整通过，未触及用户本局。其余通过批次保留各自源码范围，不叠加成全工程通过。

OCR同步做了整条读取链路的离线耗时定位：参考录像44/44.05/52/52.05秒八次读取只含两份不同像素输入，两份都路由未知；非复用约6.14/3.90秒，全文字读取约2.79/2.18秒，本局信息读取约2.34/1.60秒，同帧复用约2毫秒。没有保存/发布原帧或识别文字，不读取当前本局。这是录像整帧，不能推断真实游戏客户区性能或准确率，下一步须在正确客户区输入中核对未知路由与run阶段成本，不能仅追逐缓存微小开销或直接跳过读取。

沿REA技能的完整源码与实际运行路线，没有新增REA工具调用；此前工具条/三份CJS的分析另存。Tomimi公开源码尚缺明确复用许可，未复制其代码，本批复用本项目现有模型与Qt树。功能仍440、未开441，722有序选择器；537份源码是清点范围，整个程序、P3/P2/P1、存量代码约束及视频全部效果仍未完成。
''')
entry=f'''<!-- current-enemy-forecast-review-20261031:start -->
## 实现回顾维护 · {title}

按固定关卡原件、四项明确属性、构造/身份/类别与难度字段核验后，1049条候选引用复用原环境计算，1011条保留未接入。按图像与三档分类显示四分项，本局最近条件改变保留阅读，历史不混用当前条件；完整本局总量仍未知。图册默认收起、大数分组、内部提示中文化，公式与资料不改。

62/91两组必要检查去重153项通过；矩阵184关2060引用和最新原生32项通过，6条图片/5份不同原图已看并按整字节复用封口审阅。原始预期/隔离fixture失败保留。OCR入口重复校验已删，录像两份不同整帧的八次离线读取定位了文字/本局读取耗时，但路由均未知，不冒充游戏准确或整体提速。实际小窗更新、六私人路径保持、零游戏/聊天/上传。回执：`{prefix}summary.json`。440/未开441、722选择器；全程序、完整数值、视频及P3/P2/P1未完成。
<!-- current-enemy-forecast-review-20261031:end -->

'''
for n in ('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):text(n,entry+(R/n).read_text('utf8'))
n='PROGRAM_REVIEW.md';s=(R/n).read_text('utf8').replace('当前总范围536份','当前总范围537份',1);text(n,s+'\n[当前敌人分项与数值表回顾](research/current-enemy-forecast-review-20261031/README.md)使用原模型和已核验相同输入，1049/2060候选引用可给环境分项，完整本局总量仍未知。153项不同检查与32项原生通过，非机制独立校准。新增一份映射源码，清点不等于逐模块审查完成；OCR入口去重和录像整帧耗时定位保持其离线/未知页面边界。\n')
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8').replace('敌人完整预计数值表','敌人剩余来源/数值接入（本轮固定范围1011条引用）、保密等级16、完整藏品/阶段/技能修正和完整预计数值表',1);s=s.replace('定位完整检测、分类及页面分流的主要耗时','在正确游戏客户区输入中核对未知路由、本局信息读取及完整检测/分类的主要耗时',1);text(n,s)
n='IMPLEMENTATION_STRATEGY.md';text(n,(R/n).read_text('utf8')+'\n[当前敌人模型复用](research/current-enemy-forecast-review-20261031/README.md)先证明原件/明确属性/类别/难度输入一致再调用现有模型，避免重复写数值算法。分项与完整本局值分开；其余引用、等级16及完整效果仍须按来源接入。Qt原树增数值列，重复图册默认收起，保留手动展开与原精确导航；不借此宣布视频一致。\n')
n='VIDEO_PARITY.md';text(n,(R/n).read_text('utf8')+'\n[敌人表格与环境分项](research/current-enemy-forecast-review-20261031/README.md)继续对照108秒表格：原头像/分类树增加四项已证环境分量，重复图册默认收起、数字分组，并自动带入非历史阅读的本局最近条件。仅1049条相同输入引用复用旧环境模型；全本局数值、其余表列、所有效果和整体比例/外观仍未对齐，不把这项局部实现记作整表或视频完成。\n')
n='PROJECT_REQUIREMENTS.md';s=(R/n).read_text('utf8');marker='## OCR同步优化（2026-10-31最新更正）';s=s.replace(marker,'## 敌人数值与条件展示\n\n敌人总览按三档分类并配图，在可核验的范围展示生命、攻击、防御与法抗；不得用白值或同名/其它等级代替完整预测。完整结果受未核验项影响时，只显示已证环境分项，并把完整本局总量标为未知。自动带入的难度与区域须说明来源范围，历史阅读不借当前局条件；刷新保留有效选择和折叠。大数字使用普通数字分组，不显示程序字段或指数格式；内部脚本标识留在可展开原始资料。\n\n'+marker,1);text(n,s)
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_current_enemy_environment_components','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续当前敌人完整预测与视频表格：优先复用共享计算接口接入已知的等级16资料和其余1011引用，核验完整藏品/技能/阶段影响，不把已证环境分项当总量；补其余列/地图/出怪和外观。OCR同步在正确游戏客户区输入中核对未知路由与run阶段成本，录像整帧的两份未知页面不作真实游戏性能或准确证明。继续逐模块按三条代码约束整改，整体回顾/P3/P2/P1与视频尚未完成。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==722 and selectors[-1]=='tests.test_current_enemy_forecast_review'
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'different_tests':153,'native_checks':32,'matrix_references':2060,'qualified_references':1049,'ordered_selectors':722,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':files})
print(json.dumps({'passed':True,'different_tests':153,'native_checks':32,'matrix_references':2060,'qualified_references':1049,'archive_files':len(files),'whole_goal_complete':False}))
