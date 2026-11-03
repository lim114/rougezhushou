from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,ast,difflib,subprocess,runpy,re,sys

R=Path.cwd();BASE='472967dc6310b7fea193ec6844e8cb40f7a9e178';stem='notes-history-layout-20261101'
B=R/'verification/maintenance'/stem;research=R/'research'/stem
title='笔记按内容伸缩与历史阅读收拢（窗口高度仍待修正）'
def read(n):return json.loads((R/n).read_bytes())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def save(n,s):
 p=R/n
 if not p.exists():p.write_text(s,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=s.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in a],[v.rstrip('\r\n')for v in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
 p.write_bytes(''.join(b).encode('utf8'))
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
t=read(B/'related-delivery/results.json');assert t['passed']and t['tests_run']==125 and not(t['failed']or t['errors']or t['skipped']or t['forbidden_external_calls'])
assert read(B/'related-delivery/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(B/'related-delivery/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==125
native=[]
for name,file,count in [('notes-delivery','receipt.json',34),('history-delivery','receipt.json',35),('compact-delivery','window.json',28)]:
 receipt=read(B/name/file)
 assert receipt['passed']and receipt['unique_checks']==count and not receipt['source_drift']and not any(receipt['external_operation_attempts'].values())
 assert read(B/name/'process.json')['actual_observed_exit']==0
 for n,h in receipt['source_sha256_after'].items():assert sha256((R/n).read_bytes()).hexdigest()==h,n
 native.append(pin(B/name/file))
portrait=read(B/'compact-delivery/portrait-deferred.json');defer=read(B/'portrait-deferral.json')
assert portrait['requested']==[640,650]and portrait['actual']==[640,699]and portrait['exact_portrait_target_passed']is False
assert defer['repair_attempts']==3 and defer['not_closed']
for n in defer['failed_receipts']:assert read(B/n)['passed']is False
images=[]
for name,file in [('notes-delivery','receipt.png'),('history-delivery','receipt.png'),('compact-delivery','window.png')]:
 manifest=read(B/name/'images.json')
 for row in(manifest['images']if isinstance(manifest,dict)else manifest):images.append({'file':row.get('path',row.get('file')),'sha256':row['sha256']})
 images.append({'file':(B/name/file).relative_to(R).as_posix(),'sha256':sha256((B/name/file).read_bytes()).hexdigest()})
unique={row['sha256']:row for row in images};assert len(images)==18 and len(unique)==16
prior={r['sha256']:r['file']for r in read('.cache/notes-history-previously-viewed.json')['images']}
direct_names=['notes-delivery/conflict-visible.png','history-delivery/session-cards.png','history-delivery/receipt.png','compact-delivery/plain-note.png','compact-delivery/compact-session-cards.png','compact-delivery/compact-history-map.png','compact-delivery/expanded-history-scope.png']
direct={sha256((B/n).read_bytes()).hexdigest()for n in direct_names};assert len(direct)==7
for row in images:assert sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256']
review=[]
for h,row in unique.items():
 assert h in direct or h in prior,h
 review.append({**row,'review':'current image actually viewed'if h in direct else'whole bytes identical to actually viewed earlier PNG','earlier_viewed_file':None if h in direct else prior[h]})
write(B/'root-image-review.json',{'current_image_entries':18,'current_unique_images':16,'current_directly_viewed':7,'current_byte_identical_reuse':9,'images':review,'public_synthetic_state_only':True,'appearance_not_interaction_proof':True,'exact_history_portrait_target_passed':False,'whole_video_complete':False})
status=read('.cache/notes-history-live-status.json');live=read(B/'live-window/window.json')
assert status['toolbar_visible']and status['notes_visible']and status['elapsed_since_launch']>4
assert live['passed']and live['private_six_paths_unchanged']
write(B/'live-window/desktop-review.json',{'Windows_mcp_region':[1220,910,1430,950],'actual_current_notes_title_viewed':True,'owned_notes_and_toolbar_visible_responding_Qt_timer_advanced':True,'startup_private_six_unchanged':True,'private_window_images_or_values_archived':False,'game_binding_active':status['game_binding_active'],'not_live_game_or_chat_accuracy':True})
before=read('.cache/notes-history-before.json')['private'];changed=[n for n,h in before.items()if(sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None)!=h]
write(B/'private-scope.json',{'whole_batch_six_private_paths_unchanged':not changed,'changed_paths_if_any':changed,'origin_not_inferred':bool(changed),'private_contents_or_hashes_published':False,'private_backup_restore_or_rollback':False})
sources=['rouge/player_compact.py','rouge/player_inline_notes.py','rouge/player_note_selector.py','rouge/player_note_style.py','rouge/player_replay.py','rouge/player_replay_archive.py','rouge/relic_quantities.py','scripts/verify_full_available.py','tests/test_notes_history_layout_review.py']
changes={}
for name in sources:
 p=research/('before-'+Path(name).name)
 if not p.exists():continue
 assert p.read_bytes()==subprocess.check_output(['git','show',BASE+':'+name])
 if not name.startswith('rouge/'):continue
 def methods(raw):
  tree=ast.parse(raw);answer={n.name:ast.dump(n,include_attributes=False)for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
  answer.update({parent.name+'.'+n.name:ast.dump(n,include_attributes=False)for parent in tree.body if isinstance(parent,ast.ClassDef)for n in parent.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))});return answer
 a,b=methods(p.read_bytes()),methods((R/name).read_bytes());assert a.keys()==b.keys()
 changes[name]=[key for key in a if a[key]!=b[key]]
assert changes['rouge/player_compact.py']==['CompactAssistant.open_replay']
assert sha256((research/'before-player_replay_nodes.py').read_bytes()).hexdigest()==sha256((R/'rouge/player_replay_nodes.py').read_bytes()).hexdigest()
sys.path[:0]=[str(R),str(R/'scripts')];ns={'__name__':'notes_history_baseline_selectors','__file__':str(R/'scripts/verify_full_available.py')};exec(compile(subprocess.check_output(['git','show',BASE+':scripts/verify_full_available.py']),ns['__file__'],'exec'),ns)
from verify_full_available import maintained_selectors
a,b=ns['maintained_selectors'](),maintained_selectors();assert len(a)==734 and len(b)==735 and b[:-1]==a
count=sum(p.suffix in('.py','.js','.cjs')for p in(R/'rouge').rglob('*')if p.is_file()and'__pycache__'not in p.parts);assert count==540,count
video=read('.cache/notes-history-video-20261101/observations.json');assert len(video['frames'])==6
write(research/'sources.json',{'video':{'sha256':video['video_sha256'],'actually_viewed_frames_seconds':[194,207,210,221,230,244],'frame_hashes':[{'second':x['second'],'sha256':x['sha256']}for x in video['frames']],'video_and_frames_local_only':True,'not_continuous_full_playback':True},'Qt_documentation':[{'url':'https://doc.qt.io/qt-6/qplaintextdocumentlayout.html','establishes':'Plain document size height is paragraphs, not vertical pixels; use actual wrapped block geometry.','retrieved_document_header':'Qt6.12.0; project behavior separately validated on installed PySide6; no6.12 source copied.'},{'url':'https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QPlainTextEdit.html','establishes':'Native plain editor document and actual widget viewport geometry.'},{'url':'https://doc.qt.io/qt-6/qsizepolicy.html','establishes':'Size policy and width-dependent height can affect layout; not proof of which local page causes699.'}],'source_candidate_lookup':{'repository':'https://github.com/qtproject/pyside-pyside-setup','fixed_commit':'24627cd36e1593adf22eb1f2950e4248e7bcc1ec','widgets_listing_sha256':sha256((R/'.cache/notes-history-external-20261101/qt-widgets-contents.json').read_bytes()).hexdigest(),'guessed_CodeEditor_paths':'Two guessed6.11.2 example paths returned404; listing did not identify it at that level. No CodeEditor source was obtained or copied.','candidate_adopted':False,'limitations':'Not a complete search of all external note/history implementations; do not claim no suitable project exists.'},'current_implementation':'Local geometry glue over mature native Qt text engine; this is not a new third-party project integration. Existing externally adopted theme and BSD Flow remain.','reference_video_program_source_obtained':False})
write(B/'source-review.json',{'base_commit':BASE,'changed_or_new_sources':{n:pin(n)for n in sources},'function_AST_review':changes,'application_source_files':540,'new_application_modules':0,'new_low_probability_defensive_layer':False,'quantity_ingress_check_reason':'Observed partial-history None record in retained failure; no guessed quantity or state mutation.','new_generic_exception_or_recovery_framework':False,'storage_schema_mechanism_math_OCR_game_overlay_unchanged':True,'external_theme_and_Flow_source_unchanged':True,'new_external_project_adopted':False,'previous734_selector_order_preserved':True,'ordered_selectors_after':735,'full_suite_rerun':False,'REA_scope':'Full Python source/runtime reviewed directly; no new REA tool invocation or entire-program completion claim.'})
write(B/'failure-disposition.json',{'first_unit_failure':'first-unit-failure.json','first_run_tests':17,'first_run_error_count':1,'actual_issue':'Full-current inventory_summary contract was incorrectly used on partial historical state; original assertion retained. Restored typed historical count and checked quantity ingress.','other_corrected_issues':['Qt documentSize paragraph units cannot be pixels','Measured editor chrome avoids needless short-text scrollbar','History header buttons expanded across the whole row without a stretch','Generic unsaved warning hid real external-save-conflict reason; original reason now kept.'],'portrait_target_failed':True,'portrait_deferral':'portrait-deferral.json','failed_attempts':3,'active_page_policy_experiment_removed':True,'intermediate_green_receipts_not_accumulated':True,'current_related_tests':125,'native_scopes_separate':[34,35,28],'independent28_checks_do_not_pass_failed_height_target':True,'test_thresholds_or_scope_admission_weakened':False,'no_game_chat_or_cross_screen_accuracy_claim':True})
save(research/'README.md',f'''# 笔记按内容伸缩与紧凑历史阅读

基线{BASE}。维护不增加功能节数，仍446、后续447。本批部分完成：历史默认640×650目标实测为640×699，未通过并保留待办；全程序、全部视频效果及P3/P2/P1均未完成。

## 原片与实际实现

实际回看194/207/210秒笔记选择、编辑与阅读，以及221/230/244秒历史卡片、楼层地图和资源。笔记短文不应固定占220像素，现按Qt实际换行段落和真实编辑器边框/视口测量，长文限制在可用高度并滚动；四列选择和正文边距收拢，保存、导出与上级只读内容保持。实际保存冲突原因不再被通用未保存警告盖掉。小图标身份没有可靠证据，不将其猜作干员、藏品或结局。

历史默认先列每局简短卡片，完整清单/结算未知说明保留在提示和辅助阅读，归档并非完整通关结算仍直接显示。阅读地图时当前/本机历史来源简短可见，详细范围按“记录说明”展开；失效提示始终直接显示。重复热水壶按原已确认物理件数读取，不再只数不同ID，不改历史存储、不回填结算/种子或未来信息。历史/当前地图资源与准确楼层规则保持。

## 外部代码优先的实际范围

优先目标是别人已成熟的代码方案，不是本项目内部组件。之前已接入的PyQtDarkTheme静态主题、Qt官方BSD Flow继续使用。本轮针对文本布局查阅Qt官方文档，并尝试固定Qt6.11.2的CodeEditor候选路径；两条猜测路径404，没有取得可用源文件，不冒称已采用示例，更不能据此声称全部外部方案均不适用。

本轮实际只是原生Qt文字引擎上的少量本机连接代码，没有引入外部笔记系统，也未宣称落实新的第三方项目接入。[QPlainTextDocumentLayout文档](https://doc.qt.io/qt-6/qplaintextdocumentlayout.html)说明其documentSize高度为段落数，不能当像素；因此使用Qt真实换行块和实际视口几何。在线文档头为Qt6.12，行为在本机安装版本另验，没有复制6.12源码。来源见sources.json。Qt尺寸策略文档只能解释可能因素，不能证明当前是哪一页造成699像素高度。

## 验收、保留失败与未决

最终125项不同相关检查通过；34项笔记、35项历史和28项独立紧凑流程原生检查分别通过，存在共用流程，不相加冒称97个不同交互。真实子进程退出0、源码未漂移、外部操作计数为零。18条最终图片对应16份不同原图：7份本轮直接查看，9份整字节等同此前已实际查看原图。图片不替代交互，隔离临时状态不是实机对局。实用改动仅在列明范围验收，不等于整批外观完全通过。

首轮17项中1错误原件保留：部分历史含None时被误用为完整当前库存，保持原断言并改正调用和件数入口。短编辑器滚动、过宽按钮、保存原因被覆盖的中间绿回执和图片保留；最后新增保存原因测试后重跑125项和三个原生范围，不累计中间结果。

历史640×650目标三次修复均仍640×699；原三失败、独立页面尺寸与真实打开上下文保留。隐藏页策略试验已撤掉；在定位具体页/宽高布局请求前不作第四次同类猜改。独立28流程继续验收不表示高度通过。当前缩窄宽度及阅读可用，但精确高度和其余图标/结算/种子/完整视频外观继续待办。

测试窗已正常更新并打开笔记，Qt计时器推进、可见响应。仅记录六私人路径是否保持，不发布其内容/哈希或截图；无私人备份/回滚，不操作游戏/发送聊天。本轮维护未执行全量，原734选择器原序保持、当前735，下次455；full440仅证明原冻结源码。无速度提升、代码总体精简或全程序完成声明。
''')
entry=f'''<!-- {stem}:start -->
## 界面实现维护 · {title}

笔记按Qt真实换行与视口伸缩，短文减少空白、长文滚动，保留真实保存失败原因；历史卡片收拢说明，来源/失效可见，修正已确认重复热水壶件数。原外部主题/Flow保持，本轮Qt接口连接不冒称新外部项目接入。

125项不同必要检查、34项笔记/35项历史/28项独立紧凑原生范围分别通过；16份当前原图按直接7份/整字节复用9份审阅。历史默认目标640×650仍实测640×699，三失败和重启条件保留，不销项；其它范围通过不替代该目标。测试窗已更新打开笔记，私人六路径保持。仍446、447未开，735有序选择器，下次完整455；全程序/视频及P3/P2/P1未完成。[回执](verification/maintenance/{stem}/summary.json)。
<!-- {stem}:end -->

'''
for name in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
 s=(R/name).read_text('utf8')
 if name=='WORK_IN_PROGRESS.md':s=s[s.index('<!-- map-layout-20261101:start -->'):]
 save(name,entry+s)
name='PROJECT_PROGRESS.md';s=(R/name).read_text('utf8');old='地图节点长文、小尺寸标签与其余资料展开效果、笔记/历史及其它窗口的比例、布局、字体、图标、间距与浮窗呈现逐页对齐；';assert old in s
remaining='地图节点长文、小尺寸标签与其余资料展开效果，历史初始目标640×650实际640×699（3次修复失败，须先定位具体页的高度请求再恢复），历史未辨明图标/结算/种子及笔记其它排版、分类/实机归属，和其它窗口的比例、布局、字体、图标、间距与浮窗呈现逐页对齐；'
save(name,s.replace(old,remaining,1))
name='PROGRAM_REVIEW.md';save(name,(R/name).read_text('utf8')+f'\n[笔记与历史呈现回顾](research/{stem}/README.md)完成本轮内容高度、说明收拢和真实保存原因修正；125项相关及34/35/28项独立原生范围分别核对。精确历史高度640×650仍实际640×699，三次失败保留待办；不是全外观通过。源码仍540份，未接入新的外部笔记项目。\n')
name='IMPLEMENTATION_STRATEGY.md';s=(R/name).read_text('utf8');old='下一步处理笔记/历史及地图其余细节、真实连续读取。';assert old in s
save(name,s.replace(old,'笔记内容高度与历史说明已在列明范围核对；历史精确高度仍640×699（目标640×650），先定位具体页的宽高布局请求再恢复修复。下一步处理其它未核对外观、历史未明图标/完整数据、地图细节及连续读取，并先寻找外部成熟方案。',1))
name='VIDEO_PARITY.md';s=(R/name).read_text('utf8');lines=s.splitlines();updated=[];notes=False;history=False
for line in lines:
 if line.startswith('| 03:')and('笔记' in line)and not notes:
  line=line[:-1]+f' 本轮[笔记内容高度](research/{stem}/README.md)按Qt真实换行/视口伸缩，收拢选择间距并保留真实保存失败原因；其余外观、分类/实机归属继续待验。 |';notes=True
 if line.startswith('| ')and('03:4' in line or '04:0' in line)and('历史' in line or '复盘' in line)and not history:
  line=line[:-1]+f' 本轮[紧凑历史](research/{stem}/README.md)收拢卡片和完整说明，修正已确认热水壶件数；来源/失效可见。精确初始640×650仍实际640×699，三次失败未销项；小图标身份、完整结算/种子不猜。 |';history=True
 updated.append(line)
assert notes and history,(notes,history)
save(name,'\n'.join(updated)+'\n')
name='PROJECT_REQUIREMENTS.md';s=(R/name).read_text('utf8');s=s.replace('持续完整程序回顾，优先复用经许可且适合本机的实现','持续完整程序回顾，优先寻找、评估并复用他人已成熟且许可适用的公开代码方案，再作本机适配',1);marker='P3→P2→P1；';assert marker in s
save(name,s.replace(marker,'笔记编辑和阅读按真实换行及可用空间调整内容高度，长文可滚动；保存失败保留具体原因，不用通用警告盖掉。历史列表可简短呈现，完整范围说明仍可展开或辅助读取；当前/历史来源和失效就地可见，未读结算、种子和图标身份不补猜。窗口比例按实测尺寸验收，请求尺寸不当成已达成。\n\n'+marker,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==446 and cp['next_section']==447
receipt={'kind':'implementation_maintenance','title':title,'section':446,'functional_section_added':False,'passed':False,'acceptance_status':'partial','implemented_scope_checks_passed':True,'portrait_target_passed':False,'portrait_requested':[640,650],'portrait_actual':[640,699],'portrait_deferral':pin(B/'portrait-deferral.json'),'new_capability':'笔记内容高度与真实保存原因、历史说明收拢和物理件数阅读。','limitations':'精确历史高度未通过；未辨明图标/结算/种子、实机连续读取与其余视频外观、P3/P2/P1仍未完成。','source_sha256':{n:sha256((R/n).read_bytes()).hexdigest()for n in sources},'necessary_tests':125,'native_scopes_separate':{'notes':34,'history':35,'independent_compact_workflows':28},'native_receipts':native,'local_test_window':pin(B/'live-window/window.json'),'source_review':pin(B/'source-review.json'),'image_review':pin(B/'root-image-review.json'),'full_suite_rerun':False,'old_full440_proves_current_source':False,'goal_active':True,'whole_program_or_video_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()};write(B/'summary.json',receipt)
cp['historical_map_layout_maintenance_save']=cp.pop('current_maintenance_save')
cp['current_maintenance_save']={'kind':'implementation_maintenance','title':title,'receipt':f'verification/maintenance/{stem}/summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_portrait_height_pending','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']=f'verification/maintenance/{stem}/summary.json';cp['current_batch']['scope']='Whole-program/video review active. Functional446 unchanged. Note content geometry, exact save reason and history reading refined; exact640x650 target fails at640x699 and remains open after3 attempts.447 not started.'
cp['policy']['public_source_reuse_guidance']='AGENTS.md#公开源码优先复用与本机适配'
cp['next_action']='优先寻找并评估别人已成熟公开代码方案后本机适配，内部组件/Qt接口不冒充新外部接入。继续其它未核对外观、历史图标/完整数据和地图细节及OCR连续读取；历史640×650目标三失败仍640×699，先定位具体页高度请求再恢复。全程序/P3/P2/P1未完成，功能446、后续447，下次完整455。'
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==446
write(B/'final-audit.json',{'passed':True,'scope':'Record/publication readiness for partial maintenance; not full visual acceptance.','acceptance_status':'partial','implemented_scope_checks_passed':True,'portrait_target_passed':False,'functional_section':446,'functional_section_added':False,'next_section':447,'current_distinct_tests':125,'native_scopes_separate':[34,35,28],'ordered_selectors':735,'next_full':455,'current_full_rerun':False,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'maintenance_receipt':pin(B/'summary.json'),'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());files={p.relative_to(R).as_posix():pin(p)for p in B.rglob('*')if p.is_file()and p.name!='archive-manifest.json'};write(B/'archive-manifest.json',{'kind':'explicit_public_archive_no_private_contents_or_expected_values','files':files})
print(json.dumps({'recorded':True,'acceptance':'partial','history_height_target_passed':False,'functional_section':446,'new_functional_section':False,'related_tests':125,'native_scopes_separate':[34,35,28],'ordered_selectors':735,'public_archive_files':len(files),'whole_batch_private_six_unchanged':not changed,'whole_goal_complete':False}))
