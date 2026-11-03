from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
import ast,ctypes,difflib,json,re,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='fbc30136d128d2908f6cebbe1be5b0d551a23477';B=R/'verification/maintenance/relic-display-image-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,v):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);out=v.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in a],[s.rstrip('\r\n')for s in out],autojunk=False).get_matching_blocks():
  for i in range(k):out[y+i]=a[x+i]
 p.write_bytes(''.join(out).encode('utf8'))
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
changed=['rouge/view_catalog.py','rouge/player_inventory.py','rouge/player_item_hover.py','rouge/player_shop_memory.py','rouge/public_archive_view.py','rouge/player_evidence_history.py']
for n in changed:assert old(n)==(R/('research/relic-display-image-review-20261031/before-'+Path(n).name)).read_bytes()
unchanged=['rouge/catalog.py','rouge/expansion_reference.py','rouge/public_archive.py','rouge/player_item_sources.py','rouge/relic_recognition.py','rouge/data/relic-icon-receipt.json','rouge/data/relic-reference-equivalence.json','rouge/run_state.py','rouge/damage.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data']).strip()
def funcs(raw):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
assert funcs(old('rouge/player_shop_memory.py'))==funcs((R/'rouge/player_shop_memory.py').read_bytes())
a=funcs(old('rouge/player_evidence_history.py'));b=funcs((R/'rouge/player_evidence_history.py').read_bytes());assert all(a[n]==b[n]for n in a if n!='evidence_icon')
tests=read(prefix+'tests-current/results.json');assert tests['passed']and tests['tests_run']==57 and tests['failed']==tests['errors']==0 and not tests['skipped']and not tests['forbidden_external_calls']
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/(prefix+'tests-current/stderr.txt')).read_text('utf8'),re.M);assert len(ids)==len(set(ids))==57
assert read(prefix+'tests-current/process.json')['actual_observed_exit']==0
native=read(prefix+'native-current/receipt.json');assert native['passed']and native['unique_checks']==106 and not any(native['external_operation_attempts'].values())and read(prefix+'native-current-process.json')['actual_observed_exit']==0
legacy=read(prefix+'legacy-native-414-current/receipt.json');assert legacy['passed']and legacy['unique_checks']==20 and not any(legacy['external_operation_attempts'].values())and read(prefix+'legacy-native-414-current/process.json')['actual_observed_exit']==0
for rec in (native,legacy):
 for n in changed:assert rec['source_sha256_after'][n]==pin(n)['sha256']
images=native['screenshots']+read(prefix+'native-current/images.json')['images'];assert len(images)==10
for row in images:assert sha256((R/row.get('file',row.get('path'))).read_bytes()).hexdigest()==row['sha256']
write(prefix+'native-current/visual-review.json',{'final_images':images,'all_ten_final_originals_individually_viewed':True,'legacy_auxiliary_images_not_new_full_visual_audit':True,'synthetic_shop_and_history_not_game_samples':True,'public_pool_native_uses_real_bundled_dlc1_data':True,'same_name_variant_cards_remain_visually_ambiguous':True,'whole_video_parity_claimed':False})
manifest=read('rouge/data/relic-display-icons.json');exact=[r for r in manifest['icons'].values()if r['display_scope']=='exact_named_asset'];groups=[r for r in manifest['icons'].values()if r['display_scope']=='group_reference'];assert len(exact)==21 and len(groups)==4
assert len({r['file']for r in exact})==len(list((R/'rouge/data/relic-display-icons').glob('*.png')))==16
for r in exact:
 raw=(R/'rouge/data'/r['file']).read_bytes();assert sha256(raw).hexdigest()==r['sha256'] and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob_sha1']
assert not read('research/relic-display-image-review-20261031/download-receipt.json')['failures']
comparison=read(prefix+'tests-current/catalog-comparison.json');assert comparison['total_rows']==298 and len(comparison['changed'])==25 and comparison['unchanged']==273 and comparison['remaining_missing']==['rogue_6_legacy_10']
for source in ('.cache/verify_relic_display_images_native.py','.cache/run_relic_display_image_checks.py','.cache/fetch_relic_display_images.py'):(B/Path(source).name).write_bytes((R/source).read_bytes())
(B/'tests-current/test-source.py').write_bytes((R/'tests/test_relic_display_images_review.py').read_bytes())
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
first=read('.cache/relic-display-image-review-live-status.json');time.sleep(2.2);last=read('.cache/relic-display-image-review-live-status.json');assert last['toolbar_visible']and last['elapsed_since_launch']>first['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_Windows_MCP_snapshot_and_image_view':True,'region':[1716,1164,2130,1218],'test_window_visible_responding_and_Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
net=sum(len((R/n).read_bytes().splitlines())-len(old(n).splitlines())for n in changed)
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'unchanged_models_recognition_and_requirements':[pin(n)for n in unchanged],'shop_pure_functions_and_history_evidence_rows_text_AST_equal':True,'reuse':'Pinned public original PNGs; Qt QIcon and shared view_catalog loader used by inventory/hover/shop/public-pool/history. Current fixed names may annotate otherwise unknown history rows with version/acquisition qualification; no history writes.','direct_UI_recognition_loader_dependency_removed':True,'old_39_artwork_aliases_preserved':True,'initial_tests_30_and_native92_scope_separate_from_final57_and106':True,'source_loss_scope':'EvidenceHistoryPage explicit refresh clears/restores references on packet loss/recovery; no claim that all parent refresh schedulers invalidate every source.','physical_production_lines_net_added':net,'net_code_reduction_claimed':False,'end_to_end_performance_claimed':False,'defensive_guards_removed':False,'source_and_private_state_guards_retained':True,'REA_scope':'Read skill applied to complete Python source and native runtime; no new REA call, earlier toolbar/CJS analyses remain separate.','image_provenance':{'repository':'fexli/ArknightsResource','commit':manifest['commit'],'exact_named_references':21,'unique_original_files':16,'explicit_group_references':4,'independent_variant_art_verified':False,'remaining_unavailable':['rogue_6_legacy_10'],'copyright_notice':'licenses/GAME-ICON-NOTICE.md'},'remaining':'Same-name variant cards readable distinction, four independent variant pictures, unavailable opening-aid art, other readers/caches, independent mechanisms, entire video/program remain; recognition last.'})
title='补齐DLC与遗产图片，统一目录、商店、公开池和历史的图片入口'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'different_tests':57,'passed_tests':57,'skipped':0,'new_tests':8,'native_primary_unique_checks':106,'legacy_native_414_unique_checks':20,'overlapping_checks_not_added':True,'final_primary_images':10,'all_final_images_individually_viewed':True,'exact_named_image_references':21,'unique_original_pngs':16,'labelled_group_picture_references':4,'remaining_missing':['rogue_6_legacy_10'],'old_273_catalog_images_unchanged':True,'recognition_templates_unchanged':True,'test_window_updated':True,'private_six_paths_unchanged_during_startup':True,'source_review':pin(prefix+'source-review.json'),'tests':pin(prefix+'tests-current/results.json'),'native':pin(prefix+'native-current/receipt.json'),'full_validation_rerun':False,'full440_only_original_frozen_source':True,'whole_program_complete':False,'whole_video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_data_included':False,'publication_binding':'enclosing maintenance commit, ordinary push and actual remote/blob verification required'})
text('research/relic-display-image-review-20261031/README.md',f'''# DLC与遗产图片及共享展示入口

核对当前298条目录的26个缺图：12个DLC物品在新版公开资源树中已有准确同名原图；9个遗产原图在原先固定树已有文件但旧下载范围未覆盖。固定公开仓库[ArknightsResource](https://github.com/fexli/ArknightsResource/tree/{manifest['commit']}/rogueitem)，实际浅克隆退出0，目录2181条；匿名API首轮403未反复尝试。21份原图逐份校验Git blob、SHA256、PNG解码并实际查看；羽蛇6份原图的完整字节相同，只存16份独立PNG，原字节未处理。

另4个猫/狗变体只由固定游戏itemIconGroupId声明分组，显示明确标注的参考图，不证明独立图样相同；开局助力仍无可靠原图，不借其它条目补齐。上游README版权部分已阅读，归于鹰角，保留[署名说明](../../licenses/GAME-ICON-NOTICE.md)，不将游戏图片按程序代码许可重授。完整上游README仅本机缓存，公开记录链接及摘要；数据来源和分组原值分别保留。

复用原QIcon和共享加载器，保留准确文件优先与原39共图变体，展示模块不再调用识别模型。新图放独立展示目录，不修改识别模板或计数模型。目录、悬浮资料、商店记录、公开掉落池、持有历史均共用入口；历史未知名称可补当前固定资料中文名，并明确当时版本/领取来源未核实，不写回历史。组件明确刷新时来源失效清参考、恢复保留选择；不声称全部上层刷新调度已处理。

最终57个不同检查通过，无跳过；全298条在28/46/72三尺寸逐一比较，原273条图像保持，25条新增显示由21准确引用与4参考图构成，剩余1条缺图。主原生106项与既有414的20项分开通过，十张最终原图逐张查看；商店/历史为隔离构造记录，公开池原生使用实际固定DLC1资料，缺概率仍未知；单元合成概率仅测试文字格式，不冒充统计来源。初轮30项/92项保留为较早范围，不累计覆盖。实际项目小窗更新响应，六处私人路径启动前后保持，零游戏/聊天/个人上传。

没有改变数值公式、识别、公开统计或存储；新增图像声明/说明代码，不称净减或实测提速。相同名称变体的卡片区分、4种独立图样、开局助力及其它图片、其余阅读器缓存、全部视频/跨屏、全程序和P3/P2/P1仍未完成，识别最后。功能440未增节，717个有序选择器，full440只证明原冻结源码。
''')
entry=f'''<!-- relic-display-image-review-20261031:start -->
## 实现回顾维护 · {title}

21份准确原图引用按完整字节共享为16份PNG，另4个变体明确分组参考；298条原273条图片保持，仍1项无可靠图。展示共享入口覆盖目录/悬浮卡/商店/公开池/历史，去掉对识别加载器的直接调用；历史补用当前名称就近限定资料版本口径，不回写记录。模型、识别模板与私人保护保持，不称净减代码或端到端提速。

最终57项不同检查全通过，主原生106项和原414的20项分开退出0，十张最终图逐张查看；实际小窗更新响应、启动六私人路径保持，无游戏/聊天/个人上传。回执：`{prefix}summary.json`。功能440/未开441，717选择器；4独立变体图/开局助力、同名卡片区分、其它缓存/图片/机制、全视频与全程序/P3/P2/P1未完成，识别最后。
<!-- relic-display-image-review-20261031:end -->

'''
for n in ('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):text(n,entry+(R/n).read_text('utf8'))
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8');s=s.replace('独立数值校准、缺图、历史卡片','独立数值校准、4种独立变体图片与开局助力/其它缺图、同名变体卡片区分、历史卡片',1);text(n,s)
n='PROGRAM_REVIEW.md';s=(R/n).read_text('utf8');s=s.replace('26个当前目录缺图条目及其它窗口的统一图片入口','当前目录1项无可靠图和4种独立变体图仍未核验、同名卡片区分；其余窗口图片/缓存入口仍需逐链核对');s+='\n[图片与共享展示入口回顾](research/relic-display-image-review-20261031/README.md)补21准确图引用/4分组参考，16独立PNG，保持原273图及39共图映射；目录/悬浮卡/商店/公开池/历史共用加载器，历史名称明确当前资料参考。57项不同检查与106/20原生范围分开通过，不证明全程序、独立机制或全视频完成。\n';text(n,s)
n='VIDEO_PARITY.md';text(n,(R/n).read_text('utf8')+'\n[图片入口补齐](research/relic-display-image-review-20261031/README.md)补DLC/遗产准确原图并贯通目录、商店、公开池和历史；4分组参考与1无图就近区分。相同名称变体卡片仍需阅读区分，完整布局/互动和原片仍未一致，不将补图视为全视频验收。\n')
n='IMPLEMENTATION_STRATEGY.md';text(n,(R/n).read_text('utf8')+'\n[共享图片本机适配](research/relic-display-image-review-20261031/README.md)复用固定公开原图、Qt原生QIcon和既有展示加载器；精确文件优先/明确声明回退，整字节相同才共享存储，展示与识别资产分开。去除多个直读路径和显示加载器对识别模块的调用，保留各自身份/数据/来源校验；不称净减代码或未经测量的提速。\n')
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_shared_image_paths','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续全程序回顾与视频逐页核对：同名物品变体卡片的可读区分、其余附属资料入口/缓存失效与图片，历史有证字段/结算，字段依赖与独立机制仍待核验。已补图和共享展示入口不重复计推进；完整视频/跨屏与程序未完成，识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==717 and selectors[-1]=='tests.test_relic_display_images_review'
a=b"ADDITIONAL_MODULES += ('tests.test_replay_layout_review',)";assert (R/'scripts/verify_full_available.py').read_bytes()==old('scripts/verify_full_available.py').replace(a,a+b"\r\n\r\nADDITIONAL_MODULES += ('tests.test_relic_display_images_review',)")
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'different_tests':57,'native_ranges_separate':[106,20],'ordered_selectors':717,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':files})
print(json.dumps({'passed':True,'different_tests':57,'native_separate_ranges':[106,20],'final_image_paths':10,'archive_files':len(files),'whole_goal_complete':False}))
