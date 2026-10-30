from pathlib import Path
from hashlib import sha256
import json,subprocess,sys,difflib,runpy,time,re,ctypes
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/node-card-visual-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
baseline='0d14332be97c18a2cee38f5095d35f1959c141d2'
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
changed=['rouge/player_map_hover.py','rouge/player_map.py','rouge/player_game_map.py','rouge/player_map_acceptance.py']
for folder,num in [('tests',60),('tests-final',14),('tests-current',60)]:
 result=read(prefix+folder+'/results.json');assert result['passed']and result['tests_run']==num and not result['forbidden_external_calls']
 assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
native=read(prefix+'native-current/window.json');assert native['passed']and native['unique_checks']==56 and not any(native['external_operation_attempts'].values())
assert read(prefix+'native-current/process.json')['actual_observed_exit']==0
assert all(native['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
assert not read(prefix+'native/window.json')['passed']and read(prefix+'native/process.json')['actual_observed_exit']==1
assert read(prefix+'native-attempt2/window.json')['passed']and read(prefix+'native-final/window.json')['passed']
ids=set(re.findall(r'^test_\w+ \(([^)]+)\)',(B/'tests-current/stderr.txt').read_text('utf8'),re.M));assert len(ids)==60
compare=read(prefix+'before-after.json');assert compare['passed']and len(compare['cases'])==15 and compare['current_hover_source_sha256']==pin('rouge/player_map_hover.py')['sha256']
shots=[]
for p in sorted((B/'native-current').glob('*.png')):
 same=p.read_bytes()==(B/'native-attempt2'/p.name).read_bytes()
 shots.append({'image':pin(p.relative_to(R)),'review_method':'exact bytes reuse from /root viewed original native-attempt2'if same else'individually loaded with view_image by /root','diagnostic_not_visible_card_proof':p.name=='node-hover.png'})
assert len(shots)==7
write(prefix+'image-review.json',{'reviewer':'/root','images':shots,'all_seven_attempt2_images_actually_loaded':True,'six_changed_current_images_actually_loaded':True,
 'reference_frame_actually_loaded_this_turn':pin('.cache/reference-local-video-385/timeline/frame-026.jpg'),
 'reference_recording_identity_source':pin('verification/sections/392-video-review.json'),'whole_video_parity_claimed':False})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']and all(live['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/runtime-node-visual-live-status.json');time.sleep(2.2);b=read('.cache/runtime-node-visual-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'reviewer':'/root','actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
write(prefix+'source-review.json',{'baseline_commit':baseline,'changed_source':[pin(n)for n in changed],
 'unchanged_models':[pin(n)for n in('rouge/node_catalog.py','rouge/player_map_reference.py','rouge/public_node_statistics.py','rouge/node_statistics_source.py','rouge/run_state.py')],
 'review_scope':'Node hover layout, image painting, native button input, readable limits/source, size used by map/game-bound display; no changed capture, mechanics, matching, or data eligibility.',
 'REA_scope':'Complete Python source reviewed with runtime validation under REA skill; prior REA bridge/toolbar records retained, no new reverse-analysis coverage claim.',
 'reuse':'Existing QToolButton input/signals/accessibility, existing event art/identity, existing QPainter patterns in player_toolbar and player_catalog_grid; Qt docs checked, no new dependency or external project code copied.',
 'rare_guards':'No private-state, identity, freshness or no-duplicate-send guard removed; replaces former independent icon-and-caption layout and repeated game card size with shared sizeHint.'})
title='节点速览图片叠字、统一底色与纵向卡片布局'
summary={'kind':'implementation_maintenance','title':title,'baseline_commit':baseline,'completed_sections':440,'functional_section_added':False,'next_section_started':False,'implemented_scope_passed':True,
 'related_unique_checks':60,'related_receipt':pin(prefix+'tests-current/results.json'),'native_checks':56,'native_receipt':pin(prefix+'native-current/window.json'),
 'before_after_cases':15,'comparison':pin(prefix+'before-after.json'),'source_review':pin(prefix+'source-review.json'),'image_review':pin(prefix+'image-review.json'),'runtime':pin(prefix+'live-window/desktop-review.json'),
 'first_native_failure':'Original 392 harness deliberately leaves card pinned. This extension initially clicked it off then expected it on; explicitly initialize test pin and explanation state. Product pin behavior unchanged. Original failed receipt retained under native/.',
 'final_subsets_not_added_to_unique_total':True,'external_operations':dict(native['external_operation_attempts']),
 'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,
 'publication_binding':'enclosing maintenance commit, actual remote checked after ordinary push'}
write(prefix+'summary.json',summary)
research='research/node-card-visual-review-20261031/README.md';(R/research).parent.mkdir(exist_ok=False)
text(research,'''# 节点速览与视频布局对照

本轮实际查看项目录像节点卡片帧，与现有原生窗口对照。视频使用三列类型、双列铺图及图底名称；本项目旧窗口图片和文字上下分开，滚动区黑底突兀，默认比例偏横。此记录只涉及节点卡片，不能称全部视频效果一致。

## 改动与复用判断

保留Python/Qt、准确条目和已核验插图，沿用现有QToolButton的点击、键盘、信号及无障碍名称，仅自绘图片和图底文字。参考项目已有工具条/图标网格的QPainter用法及Qt官方[按钮子类](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QAbstractButton.html)、[图片绘制](https://doc.qt.io/qtforpython-6/PySide6/QtGui/QPainter.html)文档。未找到与现有技术栈更低接入成本的现成图卡，不新增界面库、不声称复制参考程序源码。此取舍是本项目工程判断，不是通用性能结论。

图片等比居中裁切铺满双列，名称在渐变底部，长名视觉省略但完整名称保留供辅助阅读和悬停查看。缺图明确显示节点图标及“暂无对应插图”，不借邻项图片。统一深色滚动区，无独立黑色底板；默认保留玩家必须知道的“历史比例不是本局概率、当前版本适用性待核验”，来源和详细限制可点“说明”展开，刷新与隐藏恢复保留展开状态。

节点卡片统一380×600逻辑像素的纵向建议尺寸，游戏内标注与地图面板复用同一sizeHint，并按客户区/屏幕可用范围缩小；Qt负责逻辑像素与显示比例。该比例接近录像390×620画面的纵向构成，不能视为所有DPI/屏幕的像素级一致证明。未知频率不填数字，视频中的事件概率没有复制为本项目事实。

## 实际验收

最终60项相关检查、原生56项通过，15种类型/历史组合的新旧完整条目身份、顺序、标题、图标可用性、来源正文及类型数值保持。名称缺图说明从旧按钮文字末行移到独立绘制行，仅对照时去除该固定末行；不改变实际标题。鼠标/空格打开准确事件、固定阅读、说明展开保持、缩放、缺图及禁止外部调用均验证。初轮原生脚本沿用基础工具残留固定状态后又点击取消，误期待固定；显式初始化夹具后通过，原始失败保留，未放宽产品判断。截图发现缺图提示被渐变压暗，同批移到渐变后绘制并重新验证。

最终原图六张实际逐张查看，主地图图与已查看的原图整字节相同复用；额外node-hover.png是工具最终诊断抓图，不作当时可见卡片证明。8类型画面明确标注隔离布局声明，非本局识别或完整生成候选。测试小窗已更新打开；正常启动区间六处私人状态保持，内容和摘要均不发布。没有游戏操作、采样、聊天发送或个人上传。

全程序回顾、全部视频外观与交互及P3/P2/P1仍未完成；这不是87技能机制或当前DLC条件概率校准。本轮不增加功能节数，下一节仍441，full-440仅证明原冻结源码；下一完整周期455，识别优化最后。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');t+='\n[节点速览视觉回顾](research/node-card-visual-review-20261031/README.md)补齐铺图叠字、同色滚动区和统一纵向尺寸；条目语义保持，全部界面与视频仍未一致。\n';text(n,t)
n='VIDEO_PARITY.md';t=(R/n).read_text('utf8');t+='\n[节点速览视觉回顾](research/node-card-visual-review-20261031/README.md)已将节点卡片改为双列铺图、图底名称、同色滚动区与统一纵向建议尺寸。默认保留比例/版本限制，详细来源可展开并保留；缺图不借图。实际原生交互通过，完整数据、跨屏、游戏以及其它界面外观仍待验，不称全部一致。\n';text(n,t)
entry=f'''<!-- node-card-visual-review-20261031:start -->
## 实现维护 · {title}

按原片节点卡片改为双列铺图、图底名称、同色滚动区和380×600逻辑像素建议尺寸；地图与游戏标注复用并按可用范围缩小。沿用Qt按钮原生输入和无障碍名称；缺图明确提示。默认保留历史比例及版本限制，来源细节可展开并保持。

最终60项相关检查、原生56项及15种新旧完整入口对照通过，重叠不累计；初轮夹具残留固定状态的失败保留。实际查看最终变化原图，测试小窗已更新打开，启动区间六处私人路径保持；无游戏操作、聊天或个人上传。功能仍440、441未启动；全程序/视频全部一致与P3/P2/P1仍未完成，full-440仅证明原冻结源码。回执：`{prefix}summary.json`。
<!-- node-card-visual-review-20261031:end -->

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):text(n,entry+(R/n).read_text('utf8'))
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');t=t.replace('完整条件统计的证据、缺图和视频交互/外观','完整条件统计的证据、缺图、其余视频交互/外观及完整跨屏覆盖');text(n,t)
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_node_hover_video_layout_and_exact_navigation_checked','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾：其余资料窗口、状态/强化连续场景、完整数据和视频跨屏/游戏交互；节点铺图/叠字与来源共享已实现不重复推进。机制及本图完整条件概率仍需独立证据；识别优化最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
m=runpy.run_path(str(R/'scripts/update_cloud_index.py'));m['update'](R);assert m['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
assert len(maintained_selectors())==695 and maintained_selectors()[-1]=='tests.test_node_card_visual_review'
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':baseline,'summary':pin(prefix+'summary.json'),'cloud_index':pin('CLOUD_INDEX.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'ordered_selectors':695,'tests':60,'native':56,'source_matches_current_receipts':True,'private_contents_included':False,'application_review_complete':False,'video_parity_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
manifest={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':manifest})
print(json.dumps({'passed':True,'tests':60,'native':56,'files':len(manifest),'goal_complete':False}))
