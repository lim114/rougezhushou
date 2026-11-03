from pathlib import Path
from hashlib import sha256
import json,sys,subprocess,difflib,runpy,re,time,ctypes
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/history-reader-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
baseline='74b1f592434c5c39384580d9f9fd6ab26024391e'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,value):
 p=R/n
 if not p.exists():p.write_text(value,'utf8');return
 old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=value.splitlines(keepends=True);out=list(new)
 for a,b,num in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in old],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():
  for i in range(num):out[b+i]=old[a+i]
 p.write_bytes(''.join(out).encode('utf8'))
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==baseline
changed=['rouge/player_replay.py','rouge/player_replay_nodes.py','rouge/player_statistics_cohorts.py','rouge/player_personal_statistics.py','rouge/player_compact.py']
reviewed=['rouge/player_replay.py','rouge/player_replay_archive.py','rouge/player_history_store.py','rouge/player_history_codec.py','rouge/player_replay_nodes.py','rouge/player_resource_history.py','rouge/player_evidence_history.py','rouge/player_floor_resources.py','rouge/player_recorded_scene.py','rouge/player_statistics_samples.py','rouge/player_personal_statistics.py','rouge/player_cohort_ui.py','rouge/player_statistics_cohorts.py','rouge/player_statistics_card.py']
initial=read(prefix+'tests/results.json');assert initial['tests_run']==72 and initial['failed']==1 and initial['errors']==0
final=read(prefix+'tests-current-final/results.json');assert final['passed']and final['tests_run']==73 and not final['skipped']and not final['forbidden_external_calls']
assert read(prefix+'tests-current-final/process.json')['actual_observed_exit']==0
native_names=['native-current-final','native-statistics-final','native-samples-final'];natives=[]
for folder,num in zip(native_names,(42,19,19)):
 n=read(prefix+folder+'/window.json');assert n['passed']and n['unique_checks']==num and not any(n['external_operation_attempts'].values())
 assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
 scope=changed if folder=='native-current-final'else[n for n in changed if n!='rouge/player_replay_nodes.py']
 assert all(n['source_sha256_after'][p]==pin(p)['sha256']for p in scope)
 natives.append({'receipt':pin(prefix+folder+'/window.json'),'checks':num,'scope':'Current historical map/read-only archive workflow'if folder=='native-current-final'else'Final statistics/sample sources unchanged after independent historical-map top-margin adjustment; earlier native scope reused, not whole current source proof.'})
comparison=read(prefix+'before-after-current-final.json');assert comparison['passed']and comparison['cohort_input_cases_equal']==48 and comparison['full_statistic_sample_and_text_cases_equal']==20
for n,v in comparison['sources'].items():assert v['current_sha256']==pin(n)['sha256']
unchanged=['rouge/run_state.py','rouge/player_history_store.py','rouge/player_history_codec.py','rouge/player_statistics_samples.py','rouge/player_replay_archive.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert subprocess.check_output(['git','show',baseline+':'+n])==(R/n).read_bytes()
write(prefix+'source-review.json',{'baseline_commit':baseline,'changed_source':[pin(n)for n in changed],'source_read_scope':[pin(n)for n in reviewed],'unchanged_persistence_and_requirements':[pin(n)for n in unchanged],
 'REA_scope':'Existing complete Python source read directly under REA skill; no new REA/PYC or full application coverage claim. Prior toolbar/bridge reverse evidence retained.',
 'reuse':'Existing exact map templates, PreviewMapView, same-frame snapshot qualifier/text, archived-state codec/store and Qt controls; light palette adapted from existing NOTE_STYLE. No new dependency, external source code or speculative mechanism.',
 'simplification':'Remove redundant pre-filter archive qualification and unused statistics key; select one archive cohort for both result and sample view. History projection now invalidates on relevant indexed history input, not unrelated resource log append.',
 'retained_protections':'Archive identity/digest/atomic write, private state and no-overwrite rules, current-vs-history separation, exact map/source binding and unknown conditions preserved.',
 'application_review_complete':False})
shots=[]
for folder in native_names:
 for p in sorted((B/folder).glob('*.png')):shots.append({'image':pin(p.relative_to(R)),'reviewer':'/root','review_method':'individually loaded with view_image in this turn','scope':'isolated public fixture, not user game or actual history'})
assert len(shots)==7
write(prefix+'image-review.json',{'images':shots,'earlier_seven_pre_light_and_seven_pre_margin_images_actually_viewed':True,
 'reference_frames_actually_viewed':[pin('.cache/reference-local-video-385/timeline/'+n)for n in('frame-075.jpg','frame-079.jpg','frame-085.jpg')],
 'source_video_identity_receipt':pin('verification/sections/392-video-review.json'),'whole_video_parity_claimed':False})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']and all(live['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/runtime-history-review-live-status.json');time.sleep(2.2);b=read('.cache/runtime-history-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'reviewer':'/root','actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_test_window_visible_and_responding':True,'Qt_timer_advanced':True,'six_private_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='历史地图按已读记录累积、历史资源联动与统计筛选精简'
summary={'kind':'implementation_maintenance','title':title,'baseline_commit':baseline,'completed_sections':440,'functional_section_added':False,'next_section_started':False,'implemented_scope_passed':True,
 'related_unique_tests':73,'related_receipt':pin(prefix+'tests-current-final/results.json'),'native_ranges':natives,'native_ranges_overlap_not_summed':True,
 'comparison':pin(prefix+'before-after-current-final.json'),'source_review':pin(prefix+'source-review.json'),'image_review':pin(prefix+'image-review.json'),'runtime':pin(prefix+'live-window/desktop-review.json'),
 'first_failure':'New test appended a mutable fixture by reference then altered it, unintentionally changing an earlier saved test event. Corrected append to deepcopy; initial 72-test failure retained. Product history binding was not weakened.',
 'later_view_fix':'Actual screenshot showed historical position caption clipped. Reserve 30 logical pixels above recorded map and verify marker lies within view; final map native scope rerun.',
 'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,
 'publication_binding':'enclosing maintenance commit, ordinary push and actual remote/blob check follows'}
write(prefix+'summary.json',summary)
research='research/history-reader-review-20261031/README.md';(R/research).parent.mkdir(exist_ok=False)
text(research,'''# 历史阅读与个人统计链路回顾

本轮阅读历史保存/编码/回读、历史地图/资源/藏品队伍、准确场景关联、统计/分组/样本/展示卡的Python源码。按REA技能，完整源码直接审查并运行验证，不新建REA会话或机械生成PYC；此前工具条和桥接REA证据保留。这不是全程序审完，亦非完整机制校准。

## 实际问题、实现与复用

原逐层地图只画所选单条记录，即使此前已读到其它节点也不累积。现按原保存顺序，逐区域/准确布局累积截至所选记录的类型、明确经过/原类型、同节点同帧来源的已读内容和最近已读位置。保留白圈选中与金圈最近位置的区分；不从当前地图、最终库存或后来的记录补回过去。布局变化只清新布局中的累积，旧行仍保留旧图；未知布局不借旧图。历史资源复用已验收的同帧区域/资源快照资格，只有之前实际保存的快照可显示；换布局不借前布局数量，无记录明确未读，绝不作为入层/出层/奖励或结算。

复用项目现有PreviewMapView、map_data模板、FloorResources快照/中文说明、归档编码/存储和Qt控件，不增加数据库、重放引擎或新依赖。新能力是离线资料投影，不改采样/识别策略、不操作游戏、不生成路线建议。旧逐条template_graph接口保留以支持已有直接阅读入口；正常新投影不重复应用所选事件。

个人统计原每次render为结果和样本各筛一次；每个筛选又先完整资格遍历生成选项，再遍历进行筛选。删去结果相同的选项预检查，按实际条件一次筛选，结果与样本复用同一列表；未知/非法筛选仍返回空而非全体，完整性分母、去重和数学函数不变。删除未参与任何计算的旧key字段。保留归档摘要/身份核对、原子写入、不可覆盖和私人状态保护；不能仅因发生概率小就删除这些保护。

历史页在无关日志追加时不再重建全部地图投影；键包括相关记录原下标，插入或改动已有相关记录仍会失效。固定模板仍按现有进程缓存版本读取，本轮没有新增热更新承诺。

## 视频与普通玩家阅读

本轮查看本机录像历史列表、逐层地图和个人展示卡三个片段。历史窗口改为与项目笔记/视频一致方向的浅色底、白色内容卡和胶囊分支；地图仍用原有游戏素材。列表直接写“类型读到/确认经过 · 上排第几列”等位置，时间和步数放悬停说明；地图旁显示当时已保存资源。截图发现最近位置文字裁切，同批留出顶部空间并复验。仍未达到录像的完整历史卡片、楼层导航与资源胶囊/展示卡构成；没有读取到的分数、胜负、完整结算和收益不会填造，完整外观/流程继续列待办。

## 证据与实际边界

最终73项相关检查通过。当前历史窗口原生42项、统计19项、逐局样本19项分别通过，重叠不累计；统计两范围最终源码未变，后续仅历史图顶部留白变化，按范围复用，不把它们当全工程当前源码证明。48组纯分组、20组完整统计/样本/文字旧新对照一致；原节点行字段与顺序保持，新累积图明确是新增行为。新测试初轮因共享可变夹具改写了前条事件而失败，改为复制后通过；原失败保留。新保护未放宽。

40份公开构造归档的完整render，资格判断调用由160降至40；50次追加无关资源日志刷新中，历史投影调用由50降至0。一次本机测量20次稳定render中位批次约17.47→5.88毫秒，50次无关追加刷新约21.30→0.80毫秒。这是隔离组件工作量，不是绘制、启动、识别或整机加速，不能外推固定倍数。

最终7张原图实际逐张查看，均为明确隔离样例，不是用户历史/游戏采集。测试窗已正常更新打开并核对可见响应；启动区间六处私人路径保持，内容与摘要仅留本机。无真实游戏操作、聊天发送或个人上传；隔离验收的游戏/网络/聊天调用计数均零。功能仍440，441未开始；下次完整周期455，full-440仅证明原冻结来源。全程序回顾、全部视频效果及P3/P2/P1仍未完成，识别优化最后。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');marker='| 桌面聊天桥接 |';assert marker in t
t=t.replace(marker,'| 本机历史与个人统计 | 已读归档/编码/回读、地图/资源、场景及统计来源链路；历史按记录前缀累积，换布局清后续、旧图保留；精简重复筛选，分母/去重不变，历史与当前局隔离通过。 | 实际完整记录、归档列表卡片及全部视频流程/跨屏；其余未读字段、完整结算和真实连续游戏记录不计完成。 |\n'+marker)
t+='\n[历史阅读与统计回顾](research/history-reader-review-20261031/README.md)记录前缀地图、历史资源与筛选精简；只证明所列源码/组件/隔离原生范围，不证明完整实机记录或视频全部一致。\n';text(n,t)
n='VIDEO_PARITY.md';t=(R/n).read_text('utf8');t+='\n[历史阅读与统计回顾](research/history-reader-review-20261031/README.md)已使所选历史地图累积之前已读节点/经过/最近位置，并就地读历史资源；回退不泄漏后来状态。历史窗口浅色布局及列表位置说明已改进；录像中的完整列表卡片、楼层页签、资源胶囊和展示卡仍未全部一致，完整结算/未读数据不补造。\n';text(n,t)
entry=f'''<!-- history-reader-review-20261031:start -->
## 实现维护 · {title}

历史地图按原顺序累积截至所选记录的节点/经过/同帧内容和最近位置，就地展示之前同区域资源快照；换布局清后续，旧图保留，不借当前/后来状态。窗口浅色、位置短标题，修正位置文字裁切。复用现有模板/地图/快照/归档；个人统计只筛一次并删去冗余预检查和无用key，保持分母和未知。

最终73项相关检查通过；当前历史原生42项、统计19项、样本19项分别通过，重叠不累计。48组分组与20组完整统计/文字对照一致；40归档单次render资格调用160→40，50次无关日志更新投影50→0，仅组件测量。初轮可变夹具失败保留。最终原图实际查看，测试窗已更新可见响应，启动区间六处私人路径保持；不操作游戏、不发聊天、不上传个人数据。功能仍440、441未启动，P3/P2/P1和全程序/视频目标未完成。回执：`{prefix}summary.json`。
<!-- history-reader-review-20261031:end -->

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):text(n,entry+(R/n).read_text('utf8'))
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');t=t.replace('其余视频交互/外观及完整跨屏覆盖','历史列表/楼层页签/资源胶囊与其余视频交互/外观及完整跨屏覆盖');text(n,t)
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_history_prefix_and_statistics_sources_checked','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续全程序回顾：其余资料/笔记窗口、招募/强化连续状态与独立机制；视频历史列表/楼层导航/资源胶囊和个人展示卡构成仍未齐。历史前缀累积和重复筛选精简已交付不重复推进；完整结算/未读值不补造，识别优化最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');m=runpy.run_path(str(R/'scripts/update_cloud_index.py'));m['update'](R);assert m['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==696 and selectors[-1]=='tests.test_history_reader_review'
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':baseline,'summary':pin(prefix+'summary.json'),'cloud_index':pin('CLOUD_INDEX.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'ordered_selectors':696,'unique_tests':73,'native_range_counts':[42,19,19],'native_counts_not_summed':True,'private_contents_included':False,'whole_program_complete':False,'whole_video_parity_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
manifest={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':manifest});print(json.dumps({'passed':True,'tests':73,'native':[42,19,19],'archive_files':len(manifest),'goal_complete':False}))
