from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='755d4d433f89e21968a77fc77056e107aa8238d7';B=R/'verification/maintenance/enemy-readers-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,value):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value,'utf8');return
 old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=value.splitlines(keepends=True);out=list(new)
 for a,b,num in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in old],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():
  for i in range(num):out[b+i]=old[a+i]
 p.write_bytes(''.join(out).encode('utf8'))
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
changed=['rouge/current_battle_view.py','rouge/battle_enemy_readers.py'];before='research/enemy-readers-review-20261031/before-current-battle-view.py';assert old(changed[0])==(R/before).read_bytes()
from rouge.battle_enemy_readers import _READERS
assert len(_READERS)==7
unchanged=['rouge/'+spec.provider+'.py'for spec in _READERS.values()]+['rouge/'+spec.provider.removesuffix('_reference')+'_view.py'for spec in _READERS.values()]+['rouge/current_battle_reference.py','rouge/run_state.py','rouge/app.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data','research/runtime-reference-loaders-20261031']).strip()
def methods(raw,name):
 c=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef)and n.name==name)
 return {n.name:ast.dump(n,include_attributes=False)for n in c.body if isinstance(n,ast.FunctionDef)}
a=methods(old(changed[0]),'CurrentBattlePanel');b=methods((R/changed[0]).read_bytes(),'CurrentBattlePanel');edited={fn+name for name in _READERS for fn in ['_close_','_sync_','open_']}
assert len(edited)==21 and a.keys()==b.keys()and all(a[n]==b[n]for n in a if n not in edited)
assert methods(old(changed[0]),'CurrentBattleDialog')==methods((R/changed[0]).read_bytes(),'CurrentBattleDialog')
counts={'parent_before':len(old(changed[0]).splitlines()),'parent_after':len((R/changed[0]).read_bytes().splitlines()),'new_shared_module':len((R/changed[1]).read_bytes().splitlines())};assert counts=={'parent_before':886,'parent_after':743,'new_shared_module':85};counts['combined_net_removed']=58
suite=read(prefix+'tests-current/results.json');native=read(prefix+'native/window.json');failed=read(prefix+'tests/results.json')
assert suite['passed']and suite['tests_run']==79 and not suite['skipped']and not suite['forbidden_external_calls']
assert failed['tests_run']==71 and failed['errors']==1 and read(prefix+'tests/process.json')['actual_observed_exit']==1
assert native['passed']and native['unique_checks']==91 and not native['source_drift']and not any(native['external_operation_attempts'].values())
for folder in ['tests-current','native']:assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256']
(B/'native/verifier-source.py').write_bytes((R/'scripts/verify_enemy_readers_review.py').read_bytes())
observations=read(prefix+'native/reader-images.json')['observations'];assert len(observations)==7 and {r['reader']for r in observations}==set(_READERS)
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'verified_own_prior_parent':pin(before),'unchanged_providers_views_state_and_requirements':[pin(n)for n in unchanged],'edited_parent_methods':sorted(edited),'all_other_parent_methods_and_dialog_AST_unchanged':True,'physical_source_lines':counts,'interface':'close_reader(parent,name), sync_reader(parent,name,keep), open_reader(parent,name). Existing public parent methods retained. Seven provider/dialog adaptations use the original implementation.','preserved_differences':'Elbert locate uses non-None semantics and sync checks base, opening checks result. Hanko keeps its original provider validation without adding a parent post-refresh source gate. Six original post-refresh source gates and boss-document exact enemy signal retained.','verified_comparison':'Seven real source fixtures: full result/base and both complete player/technical texts match executed prior parent. This is output preservation, not independent game-mechanic accuracy.','native_observations':observations,'first_failure':'New fixture setup assumed key for boss_documents; its original structure uses enemy_key. First original logs retained, not called a pass or a complete source freeze. No product correction was needed for that test setup issue.','performance_limit':'Physical source lines only, not runtime speed, recognition performance, independent source correctness or full-program completion.','data_and_runtime_manifest_worktree_unchanged':True,'skills':['reverse-engineer-anything','codebase-design'],'REA_scope':'Existing complete Python source reviewed directly per REA skill; previous actual bridge/toolbar REA evidence separate; no new REA call.','application_review_complete':False})
images=[pin(p.relative_to(R))for p in sorted((B/'native').glob('*.png'))];assert len(images)==9
write(prefix+'image-review.json',{'reviewer':'/root','all_nine_actual_native_originals_individually_loaded_with_view_image':images,'scope':'Seven original mechanism readers, one source-loss state and final original reader. No new numerical effects, full original-video match or pixel-equivalence claim. Long paragraphs, folding groups and remaining window geometry are still incomplete.','whole_video_parity_claimed':False})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/enemy-readers-review-live-status.json');time.sleep(2.2);b=read('.cache/enemy-readers-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='七类敌人机制窗共用打开刷新关闭流程，保留原读取器并净减58行'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':79,'test_receipt':pin(prefix+'tests-current/results.json'),'first_fixture_setup_error':pin(prefix+'tests/results.json'),'native_unique_checks':91,'native_receipt':pin(prefix+'native/window.json'),'source_review':pin(prefix+'source-review.json'),'image_review':pin(prefix+'image-review.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'production_physical_source_lines_net_removed':58,'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/enemy-readers-review-20261031/README.md','''# 七类敌人机制窗口的共同流程回顾

按REA技能直接审查已有完整Python源码，保留旧桥接/工具条的实际REA结果，本轮无新REA调用；使用codebase-design技能将真实存在的七套重复流程集中为一个小模块。未引入额外框架或复制外部项目源码。

汉科、埃尔伯特、熄日、通用首领文献、双骑士、双晶兽与物欲拮抗者，仍用各自原始读取器和窗口。只共享打开、可用性刷新与关闭流程；父页原21个方法名保持，其余父页方法和CurrentBattleDialog的AST不变。埃尔伯特locate按“不是None”判断，刷新核对base而打开核对result；汉科沿用其读取器自身核验，其余六类原有的父子来源核对保留。通用首领的关联敌人信号仍只连接一次。没有把具体机制、当前状态或数值抽成统一猜测。

主资料页886→743行，新增公共模块85行，两者物理源码行合计886→828，净减58行，包含注释和空行；不是复杂度或速度测量。原防止过期资料/错误跳转的保护保留，删除的是重复实现。本轮没有改变窗口布局，也没有修完其它辅助窗口的对象释放。

实际运行自有旧父类和新父类，七种固定资料的完整result/base及两份正文一致；不等于独立机制准确性。79个不同相关测试和91项原生检查通过，实际退出0/无跳过。原生逐一点击七类真实入口，核对实体与来源、分类/招式选择、真实非零滚动与选区、父刷新保留、来源失效及恢复后重新选择、换实体关闭清理。九张最终原图逐张查看。首轮新测试准备把通用文献的enemy_key错按其它记录的key读取，日志保留；修正的是测试适配，首轮不计通过，不称其有完整来源冻结。

实际项目小窗更新可见响应、Qt计时推进，启动六处私人路径保持；未操作游戏、发送聊天或上传个人信息，未改机制模型、图片和运行来源清单。当前新增1份应用源码，总范围534份；清点不等于全程序审查完成。三类来访首领界面还有相同的构建/刷新/地图方法，下一步可核对复用，但必须保留各自的完整技术说明。完整折叠布局、表格、其它事件/机制及全程序/视频/P3/P2/P1仍未完成，识别最后。功能仍440，旧full440只适用于原冻结来源。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');assert '当前总范围533份'in t;t=t.replace('当前总范围533份','当前总范围534份');t+='\n[七类机制窗流程回顾](research/enemy-readers-review-20261031/README.md)用同一小模块管理原七类读取器，父页21方法保持、净减58行；79项相关测试/91项原生检查通过，保留各自来源和刷新差异。机制、原正文与布局保持；整体验证、其它窗口释放及视频效果仍未完成。\n';text(n,t)
for n,addition in {
 'VIDEO_PARITY.md':'[机制窗共同流程回顾](research/enemy-readers-review-20261031/README.md)只合并重复窗口管理，原七类内容、招式分类和资料来源保持，真实刷新/选区/失效恢复已核对。未改变外观，不将代码净减或入口存在当作视频完整一致。',
 'IMPLEMENTATION_STRATEGY.md':'[七类机制窗回顾](research/enemy-readers-review-20261031/README.md)用三个共同操作替代七套重复流程，保留真实读取器及Elbert基础资料/Hanko核验差异，父页原方法兼容。物理源码净减58行，不声称性能提升；下一步可继续核对三类来访首领界面的相同构建/地图逻辑，不能因相似而丢掉各自技术说明。'
}.items():text(n,(R/n).read_text('utf8')+'\n'+addition+'\n')
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');t=t.replace('其余附属资料窗的对象释放','其余附属资料窗的对象释放、三类来访首领界面的重复构建');text(n,t)
entry=f'''<!-- enemy-readers-review-20261031:start -->
## 实现回顾维护 · {title}

原七类读取器/窗口不变，打开/刷新/关闭共用小模块，父页21方法保持；886→743行，新增模块85行，合计净减58行，不称性能提升。保留埃尔伯特基础资料、汉科自身核验、六类父子来源检查及通用首领单次关联信号。七份实际资料的新旧完整result/base与双正文相同，不冒称机制独立准确。

79个不同相关测试/91项原生唯一检查通过，实际退出0/无跳过，首轮测试准备字段错误原件保留；九张原图逐张查看。实际小窗更新响应，启动六处私人路径保持。当前应用源码清点534份，清点不作整体验证；其它窗口释放、三类来访界面重复实现及完整视频仍待推进。功能440/未开441，全程序/P3/P2/P1仍未完成，识别最后。回执：`{prefix}summary.json`。
<!-- enemy-readers-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_shared_enemy_reader_lifecycle','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾：核对三类来访首领界面的相同构建/刷新/地图方法，保留骑士时序原注释及晶兽/物欲完整技术范围；其余附属窗口释放、事件/固定作战完整资料、视频折叠/表格/几何和独立机制算例仍保留。七类机制窗管理已合并且新旧资料/正文保持，不重复计推进；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==707 and selectors[-1]=='tests.test_enemy_readers_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
tracked={p for p in subprocess.check_output(['git','ls-files','rouge']).decode('utf8').splitlines()if p.endswith(('.py','.cjs','.js'))};assert len(tracked|{changed[1]})==534
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':707,'application_source_files':534,'related_tests':79,'native_checks':91,'physical_source_lines_net_removed':58,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive})
print(json.dumps({'passed':True,'related_tests':79,'native_checks':91,'archive_files':len(archive),'net_removed':58,'goal_complete':False}))
