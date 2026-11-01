from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,runpy,difflib,sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/sections/451-reference-window';D=R/'research/reference-window-451';D.mkdir(exist_ok=True);BASE='5f5a91aade226ebd37a3a3da6c519b9993f3fb96'
def read(p):return json.loads((R/p).read_bytes())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
def pin(p):
 p=R/p;raw=p.read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def save(p,s):
 p=R/p
 if p.exists():
  old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=s.splitlines(keepends=True)
  for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in old],[v.rstrip('\r\n')for v in new],autojunk=False).get_matching_blocks():new[y:y+k]=old[x:x+k]
  p.write_bytes(''.join(new).encode('utf8'))
 else:p.write_text(s,'utf8')
# Preparation changed mixed line endings; retain the exact unchanged historical bytes.
for p in ['WORK_IN_PROGRESS.md','DEVELOPMENT_CHECKPOINT.json']:
 old=subprocess.check_output(['git','show',BASE+':'+p]).decode('utf8').splitlines(keepends=True);new=(R/p).read_text('utf8').splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in old],[v.rstrip('\r\n')for v in new],autojunk=False).get_matching_blocks():new[y:y+k]=old[x:x+k]
 (R/p).write_bytes(''.join(new).encode('utf8'))
sources=['rouge/player_reference_window.py','rouge/player_compact.py','tests/test_reference_window_451.py'];methods=0;runs=[]
for name in ['unit-final2','frame-current','binding-current','notebook-current']:
 p=B/name;x=read(p/'results.json');proc=read(p/'process.json');assert x['passed'] and proc['actual_observed_exit']==0 and proc['tested_source_unchanged'];assert not(x['failed']or x['errors']or x['skipped']or x['forbidden_external_calls'])
 for n,h in read(p/'source-before.json').items():assert sha256((R/n).read_bytes()).hexdigest()==h,n
 methods+=x['tests_run'];runs.append({'result':(p/'results.json').relative_to(R).as_posix(),'process':(p/'process.json').relative_to(R).as_posix(),'tests_run':x['tests_run']})
assert methods==49
n=read(B/'native-delivery/window.json');assert n['passed'] and n['unique_checks']==63 and not n['source_drift'] and not any(n['external_operation_attempts'].values()) and read(B/'native-delivery/process.json')['actual_observed_exit']==0
for p,h in n['source_sha256_after'].items():assert sha256((R/p).read_bytes()).hexdigest()==h,p
private=read('.cache/reference451-private-before.json');assert all((sha256((R/p).read_bytes()).hexdigest()if(R/p).is_file()else None)==h for p,h in private.items())
live=read(B/'live-window/window.json');assert live['passed'] and live['private_six_paths_unchanged'] and not live['desktop_visual_review_pending']
title='主要资料共用浮窗与返回前进导航'
scope='地图、藏品与零件、场景笔记、对局记录、队伍、最近节点资料、概况和设置在同一个原生资料窗切换；返回/前进保留已测搜索、类型筛选、页签和阅读状态。真实未保存笔记可阻止离开、关闭和Esc；收起恢复继续使用原页面。'
limits='完整作战/敌人/事件详情、笔记目录、公开档案及完整工作区仍有独立窗口，尚未全部迁入；成熟网页尚未接入。首次打开部分页面仍会在下一轮界面更新后增高，笔记900×360变为约900×662的反例未通过，原因未明；不声称所有页面尺寸或全视频外观一致。导航按钮位置、密度、完整跨屏/游戏绑定仍需继续对照。未修改识别算法，不能宣称本轮识别提速或准确率提升。'
write(B/'source-review.json',{'section':451,'changed_or_new_sources':{p:pin(p)for p in sources},'review':'QWidget pages, not reparented native PlayerDialogs; single retained QStackedWidget/FramelessDialog host. Header/resources remain real widgets. Central close guard handles switch/back/close/Escape. Removed obsolete compact NotesPopover and duplicate page-close loop. External exact readers retain existing ToolPopover implementation.','no_new_game_input_chat_or_upload':True,'low_probability_defensive_scaffolding_added':False,'limits':limits})
write(B/'unresolved-size.json',{'status':'not_passed','expected_initial_note_size':[900,360],'observed_after_process_events':[900,662],'evidence':['native-03/window.json','native-04-diagnostic/window.json','native-05-current/window.json','native-06-size-trace/window.json','native-07-grab-diagnostic/window.json','native-08-current/window.json','native-09-window-min/window.json'],'facts':['Explicit resize returns requested360, later event delivery increases height.','Widget/QWindow minimum sizes in latest diagnostic were0; a simple remaining minimum-size explanation is not established.','Initial native01 exposed visible unregistered settings; fixed via explicit initial page hide, and checked in final native scope.','Native final delivery does not count initial-size consistency as passed.'],'restart_condition':'New Qt/Windows geometry-event trace or independent minimal reproducer identifying the height-changing caller; no further blind constraint toggling.','full_video_parity':False})
import PySide6
write(D/'reuse.json',{'external_dependencies':{'Qt':{'version':PySide6.__version__,'official_docs':'https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QStackedWidget.html','used':'Actual addWidget/setCurrentWidget ownership and retained pages; navigation remains local implementation.'},'frameless':{'source':'https://github.com/zhiyiYo/PyQt-Frameless-Window/tree/fc00919f4915c91a2b6320a8ae7eb1d977ca4f57','commit':'fc00919f4915c91a2b6320a8ae7eb1d977ca4f57','version':'0.8.2','license':'LGPL-3.0','notice':'third_party/qframelesswindow/NOTICE.md','used':'Previously vendored FramelessDialog and StandardTitleBar, now one reference host. No new upstream patch or package installed.'}},'decision':'Reuse mature Qt page ownership and existing legally retained public frame rather than force native QDialogs into a stack or introduce a new full UI framework. Mature website hybrid is approved but not implemented here.','source_video':'137sec frame revisited locally; single window relationship additionally confirmed by user. Arrow semantics/placement are not claimed verified from video.','unknown':limits})
save(D/'README.md',f'# 第451节 + {title}\n\n{scope}\n\n{limits}\n\n复用Qt自身的页面栈和已固定版本、保留LGPL署名的公开无边框窗框，详情见[复用说明](reuse.json)。本节没有找到或宣称复用了参考视频原项目源码，也没有安装新依赖。\n\n49个当前定向方法与63个原生唯一检查通过；真实编辑器的未保存内容、Esc、切换与收起恢复均已实际触发。原串页、Esc关闭递归修正前及初始尺寸失败回执保留；初始尺寸缺口继续未通过。没有运行全量检查。测试窗口已更新，Windows-mcp已看见主地图窗及工具条，六份私人状态保持。\n\n[本节回执](../../verification/sections/451.json)，[未解决尺寸问题](../../verification/sections/451-reference-window/unresolved-size.json)。\n')
entry=f'## 第451节 + {title}\n\n{scope}\n\n49个当前定向方法、63个原生唯一检查通过，最终Qt图已核对；测试窗已更新，Windows-mcp确认可见，六私人状态保持。{limits} 本目标保持继续开发，全量检查继续取消。[回执](verification/sections/451.json)。\n\n'
for p in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:save(p,entry+(R/p).read_bytes().decode('utf8'))
p='PROJECT_PROGRESS.md';s=(R/p).read_bytes().decode('utf8');s=s.replace('补齐单一主资料浮窗的页面切换、共享导航与阅读状态；','继续将精确作战/敌人/事件详情、笔记目录、公开档案与完整工作区迁入主资料浮窗；核对首次切换后窗口异常增高及剩余阅读状态/导航外观；',1);s=s.replace('本机工具条的桌面像素核对（Win32可见/响应而MCP截图返回背景，原因未定）；','本机工具条的其余多屏/遮挡桌面像素核对；',1);save(p,s)
p='PROJECT_REQUIREMENTS.md';s=(R/p).read_bytes().decode('utf8').replace('本次仅保存需求，开发保持450后暂停。','四项决定继续有效；用户已恢复开发。',1).replace('当前功能第450节','当前功能第451节',1);s+='\n主资料窗使用同一原生窗口与保留的页面实例；返回、前进、关闭及Esc使用一致的草稿离开保护，刷新或收起后保留有效阅读。当前已接入的主要页面不代表所有嵌套详情和网页均已统一。首次打开后的异常增高单列未通过，不以交互检查通过替代外观/尺寸验收。\n';save(p,s)
for p,text in [('VIDEO_PARITY.md','主要页面共用一个原生资料窗及返回/前进；137秒帧已重新查看，视频箭头的具体语义/位置尚不宣称相同。嵌套精确详情、首次尺寸、完整外观仍未完成。'),('IMPLEMENTATION_STRATEGY.md','采用Qt官方QStackedWidget持有普通页面，继续复用已固定LGPL的公开frameless实现；避免将原生对话框硬嵌套或引入整套新框架。成熟网页仍待后续接入。'),('PROGRAM_REVIEW.md','CompactAssistant主要资料从独立对话框改为普通页面；统一导航与草稿离开保护，修复未注册页面串页和Esc重入关闭。保留真实来源失效、私人状态与防重复发送保护；首次窗口增高待新的几何事件证据。')]:save(p,(R/p).read_bytes().decode('utf8')+f'\n[第451节：主要资料共用浮窗](research/reference-window-451/README.md)：{text}\n')
receipt={'section':451,'kind':'functional_section','title':title,'new_capability':scope,'passed':True,'passed_scope':'Named main-page host, navigation, read state and draft/hide guard only; not whole video or all sizing.','limitations':limits,'unit_tests_run':49,'necessary_validation':runs,'native_windows_scopes':{'current':{'receipt':'verification/sections/451-reference-window/native-delivery/window.json','unique_checks':63}},'source_sha256':{p:pin(p)['sha256']for p in sources},'source_review':'verification/sections/451-reference-window/source-review.json','actual_local_test_window':'verification/sections/451-reference-window/live-window/window.json','unpassed_scope':'verification/sections/451-reference-window/unresolved-size.json','full_checks_cancelled':True,'full_suite_rerun':False,'whole_program_or_video_complete':False,'goal_active':True,'at_UTC':datetime.now(timezone.utc).isoformat()};write('verification/sections/451.json',receipt)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==450
cp.update(completed_sections=451,next_section=452,batch_start_section=451,batch_target_section=None,batch_status='ACTIVE_AFTER451');cp['sections'].append({'number':451,'completion_ref':'player-section-451','topic':title,'verification':'verification/sections/451.json'});cp['current_section_save']={'section':451,'verification':'verification/sections/451.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section';cp['current_section_validation']={'section':451,'receipt':'verification/sections/451.json','necessary_checks':49,'native_scopes':{'current':63},'full_validation_rerun':False}
if 'current_maintenance_save'in cp:cp['historical_video_decisions_before451']=cp.pop('current_maintenance_save')
cp['current_batch'].update(start=451,end=None,status='ACTIVE_AFTER451',batch_closed=False,completed_sections=451,next_section=452,next_section_started=False,receipt='verification/sections/451.json',scope=scope+' '+limits)
cp['policy'].update(new_functional_sections_paused=False,development_paused_by_latest_user_request=False,stop_after_section=None,pause_after_active_section_requested=False,current_user_batch_target_section=None,batch_target_section=None,current_user_batch_completed=False,current_usage_remaining_percent=32)
cp['next_action']='继续单一主资料窗：迁入精确作战/事件/敌人详情与笔记目录，保留来源更新、失效清理和阅读状态；尺寸问题须先获得新的Qt/Windows几何调用证据再修，不能重复盲试。按成熟网站/公开代码优先核对许可和本地参数；继续其余视频效果与识别回顾。全量检查保持取消。'
cp['functional_sections_since_latest_requirement'].append(451)
if isinstance(cp.get('player_feature_sections'),list):cp['player_feature_sections'].append(451)
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);idx['validate_delivery'](R,cp)
write(B/'final-audit.json',{'passed':True,'section':451,'necessary_distinct_tests':49,'native_checks':63,'unpassed_initial_size_explicit':True,'private_six_unchanged':True,'full_checks_cancelled':True,'goal_active':True,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json')})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():pin(p)for root in(B,D)for p in root.rglob('*')if p.is_file()and p.name!='archive-manifest.json'};files['verification/sections/451.json']=pin('verification/sections/451.json');write(B/'archive-manifest.json',{'kind':'explicit_public_section451_no_private_cache_models_or_video','files':files})
print(json.dumps({'section':451,'targeted_methods':49,'native_checks':63,'public_files':len(files),'initial_size_gap_preserved':True,'goal_active':True}))
