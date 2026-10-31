from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,re,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='2c803bb13fce99ebb4f9ffaa56e74996b4125f9a';B=R/'verification/maintenance/replay-layout-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,v):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=v.splitlines(keepends=True);out=list(b)
 for x,y,k in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in a],[s.rstrip('\r\n')for s in b],autojunk=False).get_matching_blocks():
  for i in range(k):out[y+i]=a[x+i]
 p.write_bytes(''.join(out).encode('utf8'))
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
changed=['rouge/player_replay.py','rouge/player_replay_archive.py','rouge/player_replay_nodes.py','rouge/player_resource_strip.py','rouge/player_compact.py']
for n in changed:assert old(n)==(R/('research/replay-layout-review-20261031/before-'+Path(n).name)).read_bytes()
unchanged=['rouge/player_history_store.py','rouge/player_history_codec.py','rouge/player_floor_resources.py','rouge/player_resource_facts.py','rouge/player_resource_history.py','rouge/player_personal_statistics.py','rouge/player_statistics_cohorts.py','rouge/map_recognition.py','rouge/player_map.py','rouge/run_state.py','rouge/damage.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data']).strip()
def funcs(raw):return{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
before=funcs(old('rouge/player_replay_nodes.py'));after=funcs((R/'rouge/player_replay_nodes.py').read_bytes());assert before==after
tests=read(prefix+'tests-final/results.json');assert tests['passed']and tests['tests_run']==62 and tests['failed']==tests['errors']==0 and not tests['skipped']and not tests['forbidden_external_calls']
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/(prefix+'tests-final/stderr.txt')).read_text('utf8'),re.M);assert len(ids)==len(set(ids))==62
assert read(prefix+'tests-final/process.json')['actual_observed_exit']==0
native=read(prefix+'native-current/receipt.json');assert native['passed']and native['unique_checks']==35 and not any(native['external_operation_attempts'].values())and read(prefix+'native-current-process.json')['actual_observed_exit']==0
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256']
legacy=[]
for section,count in [(401,19),(402,22),(403,18)]:
 name=prefix+'legacy-native/'+str(section)+'/';rec=read(name+'receipt.json')
 assert rec['passed']and rec['unique_checks']==count and not any(rec['external_operation_attempts'].values())and read(name+'process.json')['actual_observed_exit']==0
 for n in changed:assert rec['source_sha256_after'][n]==pin(n)['sha256']
 legacy.append({'section':section,'unique_checks':count,'receipt':pin(name+'receipt.json'),'actual_exit':0,'new_visual_audit_claimed':False})
images=native['screenshots']+read(prefix+'native-current/images.json')['images'];assert len(images)==6
for row in images:assert sha256((R/row.get('file',row.get('path'))).read_bytes()).hexdigest()==row['sha256']
write(prefix+'native-current/visual-review.json',{'final_images':images,'all_six_final_originals_individually_viewed':True,'legacy_auxiliary_images_not_new_full_visual_audit':True,'initial_34_scope_intermediate_images_not_added_to_final35':True,'whole_video_parity_claimed':False})
for source in ('.cache/verify_replay_layout_native.py','.cache/run_replay_layout_checks.py','.cache/run_replay_legacy_native.py'):(B/Path(source).name).write_bytes((R/source).read_bytes())
(B/'tests-final/test-source.py').write_bytes((R/'tests/test_replay_layout_review.py').read_bytes())
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
first=read('.cache/replay-layout-review-live-status.json');time.sleep(2.2);last=read('.cache/replay-layout-review-live-status.json');assert last['toolbar_visible']and last['elapsed_since_launch']>first['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_Windows_MCP_snapshot_and_image_view':True,'region':[1716,1164,2130,1218],'test_window_visible_responding_and_Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
video=read('.cache/replay-layout-review-video/frames.json');assert len(video['frames'])==4 and video['video_sha256']=='0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda'
for frame in video['frames']:assert pin('.cache/replay-layout-review-video/'+str(frame['second'])+'.png')['sha256']==frame['sha256']
video.update({'all_four_original_frames_individually_viewed':True,'source_frames_kept_local_only':True,'whole_video_rewatched':False,'audio_transcribed':False,'observed_features':'Card list; selected run then floor tabs; resource pills above map; video also shows score, full resources, icons and mentions seed. Those absent recorded fields are not invented.'});write(prefix+'video-reference.json',video)
net=sum(len((R/n).read_bytes().splitlines())-len(old(n).splitlines())for n in changed)
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'unchanged_models_storage_and_requirements':[pin(n)for n in unchanged],'all_node_projection_top_level_functions_AST_equal':True,'reuse':'Existing RunHistoryStore identity/hash checks, selected_state and prefix node projection; Qt QListWidget cards and QTabBar; existing ResourceStrip/Qt FlowLayout with shared explicit-rows setter. No per-card QWidget, new database, decoder, history format or external dependency.','runtime_work_reduction_verified':'Three same-source refreshes keep card item objects and call card_text three times for current only, not once per archive per refresh. Archive summaries rebuilt only on explicit reload. No end-to-end time/RSS claim.','physical_production_lines_net_added':net,'net_code_reduction_claimed':False,'defensive_guards_removed':False,'source_and_private_state_guards_retained':True,'original_native_entry_adaptation':'401 explicitly selects retained read-record tab after compact entry now starts at card list; remaining original assertions unchanged.','primary_Qt_sources':['https://doc.qt.io/qt-6/qlistwidget.html','https://doc.qt.io/qt-6/qtabbar.html'],'REA_scope':'Previously read skill applied: complete Python source and actual runtime review, no new REA call. Earlier bytecode/CJS scope separate.','remaining':'Actual score, seed, complete resources/acquisition/settlement, roster icons/cards typography, all history lifecycle/cross-screen and full-video parity remain; recognition last.'})
title='历史对局卡片、楼层页签与同区域历史资源胶囊'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'different_tests':62,'passed_tests':62,'skipped':0,'new_tests':9,'native_primary_unique_checks':35,'legacy_native_ranges_separate':legacy,'overlapping_checks_not_added':True,'final_primary_images':6,'all_final_images_individually_viewed':True,'original_models_archive_and_data_unchanged':True,'test_window_updated':True,'private_six_paths_unchanged_during_startup':True,'source_review':pin(prefix+'source-review.json'),'tests':pin(prefix+'tests-final/results.json'),'native':pin(prefix+'native-current/receipt.json'),'full_validation_rerun':False,'full440_only_original_frozen_source':True,'whole_program_complete':False,'whole_video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_data_included':False,'publication_binding':'enclosing maintenance commit, ordinary push and actual remote/blob verification required'})
text('research/replay-layout-review-20261031/README.md','''# 历史对局卡片、楼层页签与历史资源胶囊

从整字节未变原片新取221/227/235/244秒四帧并实际逐张查看，保留哈希/解码位置；原片及新帧仅本机。看见对局卡片、楼层页签、地图上方资源胶囊，原片另有结算分数、图标和种子说明。本批没有这些字段的可靠读取，不拿原片数字或当前局补历史；完整功能与视觉一致仍未完成。按REA技能阅读完整Python源码和实际Qt链路，不新调用REA、不机械扫字节码，保留此前REA的真实范围。

复用原RunHistoryStore、摘要/身份校验、手动只读加载、历史前缀地图和资源快照。Qt原生QListWidget提供浅色圆角对局卡，点选准确归档后打开最后一条已保存地图记录；同一对局重开保留所读记录。原下拉仍作为同一选择控制器，不另建历史状态或恢复本局。已有读取记录、资源、队伍、商店与个人统计均保留在更多记录；默认先看卡片/地图，逐条回看按需展开。楼层页签复用原区域筛选，只列已保存区域，不把模板楼层或当前图当成已到达。

共享ResourceStrip新增显式行入口，历史只传所选记录之前最近一次同区域已保存资源，使用独立历史键、不连当前资源入口。切换早期记录、布局或缺来源时移除旧胶囊；原完整snapshot_text仍保留为提示/无记录说明，未列字段不是0。原node_steps/template_graph/zone_label等顶层投影函数AST完全不变；归档、编码、原子写入、统计数学和源资料未改。复用[Qt列表](https://doc.qt.io/qt-6/qlistwidget.html)、[Qt页签](https://doc.qt.io/qt-6/qtabbar.html)及现有附许可FlowLayout，无新依赖/数据库/每卡片独立控件。

归档卡摘要只在明确重读历史时构建；三次稳定刷新只算当前卡三次、原卡对象保持、历史文件扫描零次。这个组件工作量验证不是端到端耗时或内存结论。本批净增界面代码，没有为精简删除身份、摘要、旧来源清理或私人状态保护。

62个不同检查全通过，含9项新场景和53项既有历史/存储/前缀/资源胶囊范围；无跳过。最终实际原生主流程35项，原401/402/403入口各19/22/18项分别真实退出0，重叠不累计。实际鼠标点卡、楼层、早期记录、重读失败/恢复与手动重选，历史7/99、第二层11和当前999/777明确分开；归档字节未改、当前局不被回写。三种尺寸下保留准确阅读。首轮34项通过后实际看图仍见常驻八类页签和日志占位，同批收拢并重新验证到最终35项；不是失败重写或假装原图已一致。最终六张原图实际逐张查看；三份旧入口截图仅保留为交互原件，未新增完整视觉审阅。

原项目小窗已正常更新、可见响应且计时推进，启动六处私人路径保持；只用临时构造数据，不操作游戏、不发送聊天、不上传个人对局。功能440/未开441，选择器716；full440仍只证明原冻结源码。结算/种子/完整资源、名单图标、字体比例、跨屏和其余视频、完整程序/P3/P2/P1未完成，识别最后。
''')
entry=f'''<!-- replay-layout-review-20261031:start -->
## 实现回顾维护 · {title}

复用原归档/历史前缀与资源胶囊：卡片进入准确历史、楼层页签只列已读区域，原记录分类和逐条回看按需展开；同对局重开/刷新保持阅读，早期和其它层资源不借当前或未来数量。归档卡摘要只在重读时构建，稳定刷新保留卡对象；不称端到端提速或净减代码，原存储/模型/资料保持。

62个不同检查全通过，主原生35项及原401/402/403各19/22/18项分别真实退出0，重叠不累计；六张最终原图逐张查看。实际小窗更新响应，启动六处私人路径保持，无游戏/聊天/个人上传。回执：`{prefix}summary.json`。功能440/未开441；结算分数/种子/完整资源、图标和全部视频/跨屏、全程序及P3/P2/P1仍未完成，识别最后。
<!-- replay-layout-review-20261031:end -->

'''
for n in ('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):text(n,entry+(R/n).read_text('utf8'))
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');phrase='历史列表/楼层页签/资源胶囊与其余';assert phrase in t;t=t.replace(phrase,'历史卡片结算/种子/完整资源及图标字段与其余',1);text(n,t)
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8').replace('实际完整记录、归档列表卡片及全部视频流程/跨屏','实际完整记录、归档卡片的完整图标/结算/种子字段及全部视频流程/跨屏');t+='\n[历史卡片与楼层回顾](research/replay-layout-review-20261031/README.md)复用原归档/前缀和ResourceStrip，补卡片选择、楼层页签与准确历史资源，分类/时间线按需展开。62项不同检查及35/19/22/18原生范围分别通过；完整资源/结算/种子、外观/跨屏和全程序仍未完成。\n';text(n,t)
n='VIDEO_PARITY.md';t=(R/n).read_text('utf8');t+='\n[历史卡片、楼层与资源胶囊](research/replay-layout-review-20261031/README.md)按原片221–244秒的卡片到楼层查看流程接入，准确读取历史前缀与同区域资源；更多记录/逐条回看按需展开，原入口保持。未取得的结算分数、种子、完整资源/图标和实际奖励来源不补造，全部外观/跨屏与视频仍未完成。\n';text(n,t)
text('IMPLEMENTATION_STRATEGY.md',(R/'IMPLEMENTATION_STRATEGY.md').read_text('utf8')+'\n[历史阅读本机复用](research/replay-layout-review-20261031/README.md)沿用Qt原生列表/页签、现有归档/地图前缀和ResourceStrip显式行入口；不建重复存储或每卡控件，归档摘要只在明确重读时构建，稳定刷新保留卡对象。必要来源校验保持，净增界面代码，不称净精简或端到端提速。\n')
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_history_layout','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续全程序回顾与视频逐页对照：补历史卡片图标及有证字段、真实连续流程/结算与其它资源，审查其它附属阅读器、缓存失效和缺图；数值依赖/独立机制、字体比例/跨屏及完整程序仍未完成。卡片/楼层/历史资源已接入，不重复计推进；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==716 and selectors[-1]=='tests.test_replay_layout_review'
anchor=b"ADDITIONAL_MODULES += ('tests.test_notebook_layout_review',)";assert (R/'scripts/verify_full_available.py').read_bytes()==old('scripts/verify_full_available.py').replace(anchor,anchor+b"\r\n\r\nADDITIONAL_MODULES += ('tests.test_replay_layout_review',)")
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'different_tests':62,'native_ranges_separate':[35,19,22,18],'ordered_selectors':716,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':files})
print(json.dumps({'passed':True,'different_tests':62,'native_separate_ranges':[35,19,22,18],'final_image_paths':6,'archive_files':len(files),'whole_goal_complete':False}))
