from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='8258919f1c4fe99d06c4d151b93b170ff577eeeb';B=R/'verification/maintenance/guest-readers-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
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
names=['knights','crystals','material'];changed=['rouge/current_guest_'+n+'_view.py'for n in names]+['rouge/guest_mechanism_view.py']
snapshots=['research/guest-readers-review-20261031/before-current-guest-'+n+'-view.py'for n in names]
for n,s in zip(changed,snapshots):assert old(n)==(R/s).read_bytes()
unchanged=['rouge/current_guest_'+n+'.py'for n in names]+['rouge/current_battle_view.py','rouge/battle_enemy_readers.py','rouge/current_map_position_view.py','rouge/current_battle_reference.py','rouge/run_state.py','rouge/app.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data','research/runtime-reference-loaders-20261031']).strip()
class GlobalModel(ast.NodeTransformer):
 def visit_Attribute(self,node):
  if isinstance(node.value,ast.Name)and node.value.id=='self'and node.attr=='model':return ast.copy_location(ast.Name(id='model',ctx=ast.Load()),node)
  return self.generic_visit(node)
def methods(raw,name,normalize=False):
 c=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef)and n.name==name)
 return {n.name:ast.dump(GlobalModel().visit(n)if normalize else n,include_attributes=False)for n in c.body if isinstance(n,ast.FunctionDef)}
shared=(R/changed[-1]).read_bytes();base_methods=methods(shared,'GuestMechanismPanel',True);dialog=methods(shared,'GuestMechanismDialog')
for n,s in zip(names,snapshots):
 cname='CurrentGuest'+n.title();m=methods((R/s).read_bytes(),cname+'Panel');assert len(m)==8
 assert all(m[k]==base_methods[k]for k in m if k!='_topic_changed')
 d=methods((R/s).read_bytes(),cname+'Dialog');assert all(d[k]==dialog[k]for k in ['closeEvent','reject'])
counts={'before_three':sum(len(old(n).splitlines())for n in changed[:3]),'after_three_and_shared':sum(len((R/n).read_bytes().splitlines())for n in changed)};assert counts=={'before_three':470,'after_three_and_shared':203}
suite=read(prefix+'tests/results.json');native=read(prefix+'native/window.json');comparisons=read(prefix+'tests/comparisons.json')['comparisons']
assert suite['passed']and suite['tests_run']==34 and not suite['skipped']and not suite['forbidden_external_calls']
assert native['passed']and native['unique_checks']==124 and not native['source_drift']and not any(native['external_operation_attempts'].values())
for folder in ['tests','native']:assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
assert len(comparisons)==10 and all(c['full_reference_equal']for c in comparisons)
state_count=sum(c['reading_states_compared']for c in comparisons)
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256']
for n in ['verify_guest_readers_review.py','verify_enemy_readers_review.py']:(B/'native'/n).write_bytes((R/'scripts'/n).read_bytes())
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'prior_own_source':[pin(n)for n in snapshots],'unchanged_models_parent_map_state_and_requirements':[pin(n)for n in unchanged],'all_seven_common_panel_methods_AST_equal_after_model_binding':True,'original_close_and_reject_AST_equal':True,'complete_source_and_text_replay':comparisons,'reading_states_compared':state_count,'physical_lines':counts,'net_physical_lines_removed':267,'preserved_differences':'Knights original three ordered technical fields and charge-duration interpretation; crystals and material retained documentary scope. Original dialog class names, titles and sizes preserved.','not_fixed':'Original owned-map allocation remains; complete window release, video layout, source coverage and independent mechanism accuracy still pending.','REA_scope':'Complete Python source directly reviewed per reverse-engineer-anything; no new REA invocation. Earlier actual bridge and toolbar REA evidence remains separate.','application_review_complete':False})
images=[];previous=R/'verification/maintenance/enemy-readers-review-20261031/native'
for p in sorted((B/'native').glob('*.png')):
 q=previous/p.name;same=q.is_file()and q.read_bytes()==p.read_bytes()
 images.append({**pin(p.relative_to(R)),'review':'exact_bytes_reuse_of_previously_individually_viewed_original'if same else 'individually_viewed_with_view_image_this_batch','previous':q.relative_to(R).as_posix()if same else None})
assert len(images)==12 and sum(bool(v['previous'])for v in images)==9
write(prefix+'image-review.json',{'reviewer':'/root','images':images,'exact_prior_originals_reused':9,'new_map_originals_individually_viewed':3,'whole_video_parity_claimed':False,'scope':'Original guest readings unchanged byte for byte; new maps show original grid and independently calibrated map-center limits. No actual combat or complete video-layout claim.'})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/guest-readers-review-live-status.json');time.sleep(2.2);b=read('.cache/guest-readers-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='三类来访首领共用原界面，保留完整机制说明并净减267行'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':34,'native_unique_checks':124,'supported_fixed_configurations_compared':10,'reading_states_compared':state_count,'source_review':pin(prefix+'source-review.json'),'test_receipt':pin(prefix+'tests/results.json'),'native_receipt':pin(prefix+'native/window.json'),'image_review':pin(prefix+'image-review.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'production_physical_source_lines_net_removed':267,'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/guest-readers-review-20261031/README.md',f'''# 三类来访首领界面的共同实现

按REA技能直接审查完整Python源码，沿用Qt和本项目已有组件；本轮没有新REA调用，不机械扫描字节码，也没有引入第三方框架或复制外部项目源码。双骑士、双晶兽与物欲拮抗者原界面的七个公共方法在模型绑定归一后AST相同，原关闭和拒绝方法也相同，现集中到GuestMechanismPanel和GuestMechanismDialog。三个原公开类名、提供者、标题和尺寸保持。

双骑士三条完整技术字段、蓄力参数解释和原始敌人数据库保留；另两类的完整文献范围独立保留，技术字段插入次序不变。原来源检查、刷新后的阅读保持、来源失效后清除和恢复后手选、准确地图及独立位置核对保持。没有更改模型、游戏数据、运行声明、技能数值或私人状态；本轮不处理原地图对象重复分配，不把保持旧行为当作窗口释放已解决。

三份原界面470行，三个适配文件加共享实现203行，净减267物理行（含注释和空行）；不是速度或复杂度测量。执行自有旧代码与新代码，对照全部10份固定支持配置、{state_count}个实体/招式阅读状态，完整资料和玩家/技术正文、分类、关联、头像像素、地图可用性一致。34项相关测试、124项原生界面检查实际退出0，没有跳过；原生检查包含原七类入口及三类地图实际点击、Escape、地图来源失效和恢复，不涉及实机游戏或聊天。

12张原生原图中9张与前批逐张查看的原件完全相同，3张新地图原图已分别查看；图片不代替交互证明。原项目测试窗已更新，可见响应，Qt计时推进；启动期间六处私人路径保持，只公开布尔结果。新增1份应用源码，清点535份，不等于全程序审查完成。

功能仍440，441未启动。全程序回顾、完整视频效果、P3/P2/P1均未完成，识别最后；full440只适用于其原冻结源码。下一步核对事件到作战入口是否能复用现有紧凑阅读窗，保留准确候选和来源清理，其余机制/独立算例及完整视觉差异继续保留。回执：`../../{prefix}summary.json`。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');assert '当前总范围534份'in t;t=t.replace('当前总范围534份','当前总范围535份');t+='\n[三类来访首领界面回顾](research/guest-readers-review-20261031/README.md)共享原构建/刷新/地图流程并保留完整独立技术说明，净减267物理行；10份配置和全部实体/招式状态新旧对照一致，34项相关测试/124项原生检查通过。其它窗口释放、机制独立准确性、完整视频与全程序仍未完成。\n';text(n,t)
for n,addition in {
 'VIDEO_PARITY.md':'[三类来访首领界面回顾](research/guest-readers-review-20261031/README.md)合并已有重复构建并保持原外观与说明，9张原件整字节一致，3张地图另审；不将代码精简当作视频外观一致。完整折叠、表格、其它窗口几何及所有视频交互仍待核对。',
 'IMPLEMENTATION_STRATEGY.md':'[三类来访首领共同实现](research/guest-readers-review-20261031/README.md)用已有Qt与本地公共基类替代470行重复构建，合计203行，提供者和独立技术差异仍在原适配文件；有完整输出回放及原生核对，不新增通用引擎。下一步检查事件到作战入口复用现有紧凑资料窗；原地图对象释放仍待处理，不虚报性能改善。'
}.items():text(n,(R/n).read_text('utf8')+'\n'+addition+'\n')
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');assert '、三类来访首领界面的重复构建'in t;text(n,t.replace('、三类来访首领界面的重复构建',''))
entry=f'''<!-- guest-readers-review-20261031:start -->
## 实现回顾维护 · {title}

三份原界面470行合并为203行（含注释和空行），保留七个公共方法、原公开类与各自完整技术说明；未改变模型和资料，未声称性能提升或完整机制准确。10份固定配置、{state_count}个阅读状态新旧对照一致，34项相关测试/124项原生唯一检查实际退出0。12张原图中9张与已审原件整字节一致、3张新地图逐张查看；实际项目小窗更新响应，启动六处私人路径保持。回执：`{prefix}summary.json`。

功能440/未开441，源码清点535份不作完整审查；原地图对象分配、事件作战窗复用、其它资料与完整视频仍待推进，全程序/P3/P2/P1未完成，识别最后。
<!-- guest-readers-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_shared_guest_readers','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续全程序回顾：核对事件到作战入口能否复用已有紧凑阅读窗，保留准确配置/来源/阅读清理；原地图对象释放、完整事件和战斗资料、视频折叠/表格/几何、独立机制和算例仍待处理。三类首领重复界面已合并，不重复计推进；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==708 and selectors[-1]=='tests.test_guest_readers_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
tracked={p for p in subprocess.check_output(['git','ls-files','rouge']).decode('utf8').splitlines()if p.endswith(('.py','.cjs','.js'))};assert len(tracked|{changed[-1]})==535
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':708,'application_source_files':535,'related_tests':34,'native_checks':124,'reading_states_compared':state_count,'physical_source_lines_net_removed':267,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive})
print(json.dumps({'passed':True,'related_tests':34,'native_checks':124,'reading_states':state_count,'archive_files':len(archive),'goal_complete':False}))
