from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import difflib,json,re,runpy,subprocess,sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='7aef6c07ae56f1b52cabcfb3ca9f3d57b77e852d'
B=R/'verification/maintenance/grade16-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
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
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
changed=['rouge/app.py','rouge/battle_preview.py','rouge/current_battle_reference.py','rouge/current_enemy_forecast.py','rouge/enemy_environment.py','rouge/node_catalog_view.py','rouge/run_badges.py','rouge/run_config.py','rouge/run_modifiers.py']
unchanged=['AGENTS.md','rouge/damage.py','rouge/run_state.py','rouge/relic_recognition.py','rouge/capture.py','rouge/recognition.py','rouge/page_ocr.py','rouge/recognition_cache.py']
for n in unchanged:assert subprocess.check_output(['git','show',BASE+':'+n])==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data']).strip()
ids=[]
for folder,count in(('tests-closure',119),('recognition-final',33)):
 result=read(prefix+folder+'/results.json');assert result['passed']and result['tests_run']==count and not result['failed']and not result['errors']and not result['skipped']and not result['forbidden_external_calls']
 assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
 cases=re.findall(r'^test_\w+ \(([^)]+)\)',(B/folder/'stderr.txt').read_text('utf8'),re.M);assert len(cases)==len(set(cases))==count;ids+=cases
assert len(ids)==len(set(ids))==152
matrix=read(prefix+'profile-audit-closure/results.json');assert matrix['passed']and len(matrix['old_new_full_result_comparisons'])==48
assert matrix['grade16_matrix']['counts']=={'qualified':1049,'unqualified':1011}
assert read(prefix+'profile-audit-closure-process.json')['actual_observed_exit']==0
native=read(prefix+'native-final/receipt.json');assert native['passed']and native['unique_checks']==33 and not any(native['external_operation_attempts'].values())
assert read(prefix+'native-final-process.json')['actual_observed_exit']==0
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256']
images=native['screenshots']+read(prefix+'native-final/images.json')['images']
earlier=read(prefix+'native/receipt.json')['screenshots']+read(prefix+'native/images.json')['images']
assert len(images)==len(earlier)==6
for row,prior in zip(images,earlier):assert sha256((R/row.get('file',row.get('path'))).read_bytes()).hexdigest()==row['sha256']==prior['sha256']
write(prefix+'native-final/visual-review.json',{'images':images,'six_paths_five_distinct_original_images':len({r['sha256']for r in images})==5,'five_original_images_individually_viewed':True,'final_images_equal_whole_bytes_to_viewed_originals':True,'grade16_numbers_and_plain_unknown_totals_checked':True,'video_parity_complete':False})
live=read(prefix+'live-window-final/window.json');assert live['passed']and live['private_six_paths_unchanged']and live['qt_timer_advanced']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256']
import win32gui,win32process,ctypes
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
write(prefix+'live-window-final/desktop-review.json',{'actual_Windows_MCP_snapshot_viewed':True,'region':[1716,1164,2130,1218],'current_window_visible_responding_and_timer_advanced':True,'private_six_paths_unchanged':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
for n in('node_catalog_view.py','test_relic_grade_sync_032.py'):
 source=('rouge/'if n=='node_catalog_view.py'else'tests/')+n
 (R/'research/grade16-review-20261031'/('before-'+n)).write_bytes(subprocess.check_output(['git','show',BASE+':'+source]))
for n in('.cache/run_grade16_checks.py','.cache/run_grade16_recognition_checks.py','.cache/audit_grade16_profiles.py','.cache/run_grade16_matrix.py','.cache/verify_grade16_native_final.py','.cache/run_grade16_native_final.py'):(B/Path(n).name).write_bytes((R/n).read_bytes())
(B/'tests-closure/test-source.py').write_bytes((R/'tests/test_grade16_review.py').read_bytes())
write(prefix+'retained-failures.json',{'all_original_test_directories_retained':True,'tests-initial':'System python lacked PySide6; exit1 before product import','tests-runtime':'Base shared runtime without project venv lacked PySide6; exit1 before product import','tests-project-runtime':'Public temporary fixture used timestamp1000 earlier than default run start; one error. Corrected fixture started_at999, not production state','recognition-checks':'Existing invalid-range test used16. Source now proves it valid; moved out-of-range case to17, all other invalid types/modes unchanged','profile-audit':'First audit loader lacked __file__; observed tool exit1 before comparison','profile-audit-final':'Second audit iterated dictionary keys as records; observed tool exit1. Corrected to items, all13groups actually checked','live-window-final':'Receipt path already existed after successful application launch; observed surviving child without relaunch. Initial observation expected one PID, but Windows virtualenv redirector+runtime child share args. Actual window ownership and unchanged private files then verified.','production_acceptance_thresholds_weakened':False})
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'unchanged_source':[pin(n)for n in unchanged],'numeric_formula_changed':False,'source_data_files_changed':False,'interface':'Existing prepare_run and resolve_enemy accept a trusted verified profile packet. Current qualified forecast passes grade16 packet; ordinary legacy calculator keeps0–15. No copied numerical kernel, new broad try/catch, or single-use helper.','recognition':'Current NORMAL0–16 shared range; canonical label strings retained. Real16 glyph not independently validated.','fixed_node_catalog':'Current16 remains recorded, old catalog gets unknown difficulty rather than15 or a ValueError. No16 node-generation coverage claimed.','all_existing_code_compliant':False})
title='打通保密等级16的读取、同局复用与已证敌人环境分项'
write(prefix+'summary.json',{'passed':True,'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'functional_section':440,'functional_section_added':False,'different_necessary_tests':152,'native_unique_checks':33,'old_new_complete_preview_comparisons':48,'current_matrix_stages':184,'current_matrix_references':2060,'qualified_environment_components':1049,'unqualified':1011,'current_normal_grade16_region_growth_percent':25,'relic_groups_verified':13,'current_full_totals_known':False,'real_grade16_glyph_accuracy_or_actual_panel_calibrated':False,'whole_program_review_complete':False,'all_existing_code_compliant':False,'full_regression_rerun':False,'next_full':455,'whole_video_parity_complete':False,'private_six_paths_unchanged_at_window_start':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False,'local_only_client_OCR_probe_excluded_from_public_artifacts':True,'at_UTC':datetime.now(timezone.utc).isoformat()})
text('research/grade16-review-20261031/README.md','''# 保密等级16与原计算复用回顾

固定国服原表 bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d 的NORMAL有0–16共17档。16档bossValue=25、addDesc明确每进入新区攻击和生命额外+25%；原0–15五字段逐项一致。固定来源与完整选取见[源表摘录](../../verification/maintenance/grade16-review-20261031/profile-audit-closure/source-selection.json)，镜像与原件摘要已由现有封存包核对，不是游戏官方服务接口或本机/服务器版本证明。[机制文献](https://prts.wiki/w/沉沦者的黑流树海)的搜索摘要也说明难度继承与区域成长；本轮完整页面读取超时，不冒称已取得全文。沿用项目既有区域叠乘和阈值依据，没有重写数值公式或由参数猜脚本。

读取范围与各计算器固定基准分开：徽标两条数字读取和标签读取接受16，主控显示并锁定真实16；保存、重启、历史和分组沿用同局数据。确认过的16与分队可避免重复徽标搜索，旧几何不复用。旧数值入口仍只接受0–15；当前战斗页只对来源、类别与四项属性均已核验相同的引用传入当前难度表。完整本局总量未知，不将分项称完整预测。旧节点目录未证明16，条件留未知而不是报错或偷换15。

184关2060候选引用中1049可给16档环境分项，1011仍缺资格；这不是实际敌人数。13组同图藏品的当前分档原表与原表相同，16沿用已证最高门槛，不推定新档或全部效果生效。152项不同必要检查、33项原生窗口检查通过，48组0–15三类敌人完整富结果新旧一致；它们是接口/兼容证明，不是独立游戏数值或16字形准确率证明。

五份不同原生图实际逐张查看，封口六路径整字节相同复用；测试小窗更新可见响应，六私人路径保持。启动器最后写回执时目录冲突、后续PID计数错误均保留，实际已成功运行的窗口经重新观察确认，没有重复启动或恢复旧状态。其它环境/验证器失败见retained-failures；完整修正后通过，不改产品保护门槛。

OCR同步做了本机只读客户区探测，不改焦点/操作游戏，不保存帧、识别内容或本局状态；该本机记录不进入公开归档。所见页面仍依赖完整发现，主要耗时在全文OCR，不能据少量输入声称提速或完整准确。下一步核对视觉路由与真实客户区页面特征，等级16同局复用只证明能省去重复徽标查找。

全程序回顾采用REA技能允许的完整源码与实际运行路线，本批未新增REA工具调用，未复制许可不明代码。现有prepare_run/resolve_enemy共享固定版本输入，合并重复调用表达式，未抽单次函数或新增宽泛异常兜底。三条约束对新增和已有代码同样有效，但存量未全部整改；功能仍440、441未开，P3/P2/P1及完整视频一致性未完成。
''')
entry=f'''<!-- grade16-review-20261031:start -->
## 实现回顾维护 · {title}

NORMAL0–16读取、主控真实等级、历史/分组和同局复用已衔接。16档按固定当前25%区域成长调用原环境模型，184关2060候选引用中1049可列分项、1011仍未知；13组藏品分档原表一致。旧干员计算仍限制0–15，旧节点目录的16难度条件留未知，不偷换15。完整总量与真实16字形/面板未验，不视为全程序完成。

152项不同必要检查、33项原生与48组0–15完整输出对照通过，原失败保留；实际小窗可见响应、六私人路径保持。OCR本机只读探测不公开私人输入，不声称整页提速。回执：`{prefix}summary.json`。440/未开441、723有序选择器；识别同步，存量三条约束继续逐模块整改。
<!-- grade16-review-20261031:end -->

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):text(n,entry+(R/n).read_text('utf8'))
n='PROGRAM_REVIEW.md';text(n,(R/n).read_text('utf8')+'\n[等级16与计算复用回顾](research/grade16-review-20261031/README.md)：现有读取/主控/保存/历史/分组与13组藏品分档可接16，当前1049引用给环境分项。普通旧干员数值、旧节点16条件、实际字形及完整面板仍未完成；存量三条代码约束和全程序回顾继续，不以152项检查替代。只读客户区耗时探测保留本机，不作为公开游戏验收。\n')
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8').replace('、保密等级16、完整藏品/阶段/技能修正','、保密等级16的完整藏品/阶段/技能修正',1).replace('等级16及新增/变更分队','等级16的旧干员计算与完整效果、实际面板/字形核对，以及新增/变更分队',1).replace('在正确游戏客户区输入中核对未知路由、本局信息读取及完整检测/分类的主要耗时','修正真实客户区页面仍需完整发现的路由覆盖，核对本局信息复用和完整文字检测/分类的主要耗时',1);text(n,s)
n='PROJECT_REQUIREMENTS.md';s=(R/n).read_text('utf8');marker='## 敌人数值与条件展示';assert marker in s;s=s.replace(marker,'## 难度读取与资料适用范围\n\n识别、保存和展示的常规难度范围，与每个计算器/固定目录已核验范围分别管理。读取到较新等级时保留真实值及同局复用，不降级套用旧档；不支持的完整计算或条件判断明确未知。提供版本数据的调用方先核对来源，再复用原模型；新增接口不能绕过版本或属性资格校验。\n\n'+marker,1);text(n,s)
n='IMPLEMENTATION_STRATEGY.md';text(n,(R/n).read_text('utf8')+'\n[等级16回顾](research/grade16-review-20261031/README.md)复用原环境核，可信版本表由已封存当前引用提供；读取资格与计算覆盖分开，旧入口和节点条件不冒用新档。同步复用同局确认的16，OCR整页路由继续按实测修正，不添加多套数值核或无证防御。\n')
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_grade16_reading_and_qualified_environment','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续存量代码与视频/P3回顾，完善1011条引用及完整藏品/阶段/技能影响、旧干员计算的16档和节点条件版本范围；补独立游戏算例，不把分项当完整总量。OCR同步优先真实客户区探索视觉路由和全文检测耗时，同局信息复用保持；全程序/三条代码约束尚未整体合规，441未启动。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==723 and selectors[-1]=='tests.test_grade16_review'
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'different_tests':152,'native_checks':33,'matrix_references':2060,'qualified_references':1049,'ordered_selectors':723,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':files})
print(json.dumps({'passed':True,'different_tests':152,'native_checks':33,'ordered_selectors':723,'archive_files':len(files),'whole_goal_complete':False}))
