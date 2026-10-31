from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,difflib,runpy,re,sys
R=Path.cwd();BASE='48712c7e453de4e23b542a509b69543137a168ed';B=R/'verification/sections/446-inventory-modes'
title='重复热水壶件数、合并与图文卡片切换'
def read(n):return json.loads((R/n).read_bytes())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def pin(n):
 p=R/n;raw=p.read_bytes();return {'receipt':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def save(n,text):
 p=R/n
 if not p.exists():p.write_text(text,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=text.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in a],[s.rstrip('\r\n')for s in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
 p.write_bytes(''.join(b).encode('utf8'))
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
t=read(B/'related-current/results.json');assert t['passed']and t['tests_run']==171 and not(t['failed']or t['errors']or t['skipped']or t['forbidden_external_calls'])
assert read(B/'related-current/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(B/'related-current/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==171
n=read(B/'native-current/window.json');assert n['passed']and n['unique_checks']==32 and not n['source_drift']and not any(n['external_operation_attempts'].values())
assert read(B/'native-current/process.json')['actual_observed_exit']==0
for name,digest in n['source_sha256_after'].items():assert sha256((R/name).read_bytes()).hexdigest()==digest,name
images=read(B/'native-current/extra-images.json')+n['screenshots'];assert len(images)==4
for row in images:assert sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256']
write(B/'native-current/root-image-review.json',{'actual_current_PNGs_viewed':4,'images':images,'public_synthetic_state_only':True,'appearance_does_not_replace32_interaction_checks':True,'whole_video_complete':False})
live=read(B/'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
status=read('.cache/inventory446-live-status.json');assert status['elapsed_since_launch']>4 and status['toolbar_visible']and status['inventory_visible']
write(B/'live-window/desktop-review.json',{'Windows_mcp_region':[2120,1450,2544,1520],'actual_toolbar_viewed':True,'native_inventory_visible_responding_and_fresh_Qt_timer':True,'game_binding_active':status['game_binding_active'],'private_window_images_or_contents_archived':False,'not_live_game_or_chat_accuracy':True})
before=read('.cache/inventory446-before.json')['private'];changed=[name for name,digest in before.items()if(sha256((R/name).read_bytes()).hexdigest()if(R/name).is_file()else None)!=digest]
write(B/'private-scope.json',{'whole_batch_private_six_unchanged':not changed,'changed_paths_if_any':changed,'change_origin_not_inferred':bool(changed),'startup_six_unchanged':True,'private_contents_or_hashes_published':False,'backup_restore_or_rollback':False})
sources=['rouge/relic_quantities.py','rouge/run_state.py','rouge/player_resource_facts.py','rouge/player_inventory.py','rouge/player_catalog_grid.py','rouge/player_parts.py','rouge/player_tools.py','rouge/player_shop_memory.py','rouge/player_acceptance.py','rouge/player_item_acceptance.py','scripts/verify_full_available.py','tests/test_inventory_modes_446.py']
for name in sources:
 old=R/'research/inventory-modes-446'/('before-'+Path(name).name)
 if old.exists():assert old.read_bytes()==subprocess.check_output(['git','show',BASE+':'+name])
sys.path[:0]=[str(R),str(R/'scripts')];from rouge import expansion_reference as reference
item=reference.packet()['current']['details']['items']['rogue_6_relic_legacy_1'];assert item['name']=='热水壶'
write('research/inventory-modes-446/evidence.json',{'base_commit':BASE,'local_video_sha256':'0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda','actual_local_frame_review_seconds':[158,166,174,178],'footer_crop_second':170,'observation':'Footer merge control is specific to repeated kettles. Small-slider description cards and large-slider icon grid are distinct.','not_continuous_full_playback':True,'source_urls':['https://prts.wiki/index.php?title=热水壶&oldid=434529','https://doc.qt.io/qt-6/qtextlayout.html','https://doc.qt.io/qt-6/qstyleditemdelegate.html'],'PRTS_theme_specific_facts':{'theme':'沉沦者的黑流树海','fallback_after_pool_exhaustion':True,'maximum_owned_copies':100,'resource_effect_not_replayed':True},'pinned_current_game_item':item,'video_and_frames_distributed':False,'Qt_API_use_is_not_new_external_project_adoption':True,'previous_external_production_code':['PyQtDarkTheme2.1.0 static QSS/palette/SVG with MIT license','Qt official6.11.2 BSD Flow Layout'], 'MaaFramework_production_integrated':False,'reference_program_source_obtained':False})
write(B/'source-review.json',{'base_commit':BASE,'changed_or_new_sources':{name:pin(name)for name in sources},'application_source_files':540,'new_application_modules':1,'implementation':'Count explicitly confirmed kettle slots independently of unique relic IDs; retain original storage schema/history/calculator identities. Qt description delegate and responsive footer use mature Qt APIs; upstream static theme and BSD Flow code stay.','defenses':'No general recovery framework, blanket try/catch, speculative fallback quantities or acquisition replay. Existing admission and private/sending protections remain.','REA_scope':'Complete Python source reviewed directly; no new REA invocation and no whole-program review claim.','mechanism_math_or_OCR_changed':False,'whole_program_or_video_complete':False})
oldfile=R/'.cache/inventory446-selectors-before.py';oldfile.write_bytes(subprocess.check_output(['git','show',BASE+':scripts/verify_full_available.py']))
old=runpy.run_path(str(oldfile))['maintained_selectors']();new=runpy.run_path(str(R/'scripts/verify_full_available.py'))['maintained_selectors']();assert len(old)==732 and len(new)==733 and new[:len(old)]==old
write(B/'selector-prefix.json',{'previous_count':732,'current_count':733,'old_order_preserved':True,'appended':list(new[len(old):]),'registration_not_full_execution':True})
write(B/'intermediate-disposition.json',{'originals_retained':['before-counts.json','related-final','native-first','native-final'],'current_acceptance':['related-current','native-current'],'before_counting_reproduction_is_product_issue':True,'intermediate_passes_not_added_to_current_counts':True,'final_wording_repair':'One-copy legacy completeness proof is not necessarily a stored full icon bar; display verified inventory provenance instead.','helper_setup_errors':'Initial local inspection helper missed sys.path; an atomic patch context mismatch made no source mutation. Corrected before current checks.','unavailable':'No actual repeated-kettle live game bar/multipage continuous capture, combat or chat validation; no fabricated pass.'})
entry=f'''<!-- player-section-446 -->
## 第446节 + {title}

按原片核对只合并重复热水壶；完整确认栏分别计算物理件数与不同资料身份，修正多热水壶误称未读全。合并/展开保持来源、选择和阅读，未知不猜；四类物品滑块左侧为图文效果卡、右侧为图标网格，窄窗页脚自动换行。现有外部PyQtDarkTheme静态主题和Qt官方BSD Flow代码保持，Qt排版API不冒称新外部项目接入。

最终171项不同必要检查、32项当前原生检查通过，四张最终隔离原图已看；首轮计数重现、中间回执与最终来源措辞修正保留，不累计中间测试。实际测试窗已更新打开，可见响应，启动六私人路径保持。旧732选择器原序保留，现733；未跑全量，下次455。实际重复图标/多页连续读取、地图/笔记/历史和全视频、P3/P2/P1未完成。回执verification/sections/446.json。

'''
for name in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
 text=(R/name).read_text('utf8')
 if name=='WORK_IN_PROGRESS.md':text=text[text.index('<!-- catalogue-header-20261101:start -->'):]
 save(name,entry+text)
name='PROJECT_REQUIREMENTS.md';text=(R/name).read_text('utf8');assert '当前功能第445节'in text
text=text.replace('当前功能第445节','当前功能第446节',1)
marker='P3→P2→P1；';assert marker in text
text=text.replace(marker,'重复热水壶须区分物理件数与不同资料身份，合并只影响显示，不合并其它同图分档，不由总数差额猜件数或由件数重放资源收益；证据不完整明确标未确认。滑块两端分别支持图文效果卡和图标网格，保持选择、完整说明与价格。\n\n'+marker,1);save(name,text)
name='PROJECT_PROGRESS.md';text=(R/name).read_text('utf8');old='核对并实现原片藏品合并筛选的准确口径与操作，不擅自合并独立变体身份或效果；';assert old in text
save(name,text.replace(old,'重复热水壶在实际游戏多页、滚动、动画与连续采样中的件数完整性，不能由合计差额或同图变体猜测；',1))
name='PROGRAM_REVIEW.md';text=(R/name).read_text('utf8');assert '当前总范围539份'in text
text=text.replace('当前总范围539份','当前总范围540份',1).replace('原片合并筛选的准确口径、','重复热水壶的实际多页连续读取、',1)
save(name,text+'\n[第446节](research/inventory-modes-446/README.md)完成重复热水壶件数/合并和四类物品图文卡片，修正按身份数误判完整性；新增一个件数事实模块。真实重复图标多页连续读取、其它页面及全视频仍未完成，Qt API不计作新外部项目复用。\n')
name='VIDEO_PARITY.md';text=(R/name).read_text('utf8').replace('原片藏品合并筛选的准确口径与剩余交互仍未完成','重复热水壶的实际连续读取与剩余交互仍未完成',1)
old='其它浮窗、图片缺项和完整跨屏外观仍待验收；当前DLC完整池未确认。';assert old in text
text=text.replace(old,'第446节按166/174秒与170秒页脚补齐小滑块图文卡、大滑块图标网格及仅合并重复热水壶；物理件数与不同资料身份分开，未知不猜。其它浮窗、图片缺项、真实重复图标多页连续读取和完整跨屏外观仍待验收；当前DLC完整池未确认。',1);save(name,text)
name='IMPLEMENTATION_STRATEGY.md';text=(R/name).read_text('utf8');old='下一步处理原片合并筛选的准确口径、地图/笔记/历史及剩余页面。';assert old in text
save(name,text.replace(old,'重复热水壶件数/合并与图文卡片已按第446节交付所列范围；下一步处理地图/笔记/历史及剩余页面、真实连续读取。',1))
receipt={'section':446,'kind':'functional_section','title':title,'new_capability':'完整已确认栏保留重复热水壶物理件数；只合并热水壶并保持来源与选择。四类物品支持图文效果卡/图标网格切换，窄窗页脚换行。','limitations':'真实游戏重复图标及多页连续读取、地图/笔记/历史及全视频和P3/P2/P1仍未完成。MaaFramework仍未接入生产；Qt排版API不是新外部项目复用。不改数值机制、不倒推资源。','necessary_validation':pin(B/'related-current/process.json'),'unit_tests_run':171,'native_windows_scopes':{'inventory_modes':{'receipt':str((B/'native-current/window.json').relative_to(R)).replace('\\','/'),'unique_checks':32}},'actual_local_test_window':pin(B/'live-window/window.json'),'source_review':pin(B/'source-review.json'),'source_sha256':{name:sha256((R/name).read_bytes()).hexdigest()for name in sources},'full_suite_rerun':False,'old_full440_proves_current_source':False,'goal_active':True,'whole_program_or_video_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()}
write('verification/sections/446.json',receipt)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==445 and cp['next_section']==446
cp['completed_sections']=446;cp['next_section']=447;cp['sections'].append({'number':446,'completion_ref':'player-section-446','topic':title,'verification':'verification/sections/446.json'})
cp['current_section_save']={'section':446,'verification':'verification/sections/446.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['historical_implementation_maintenance_before446']=cp.pop('current_maintenance_save')
cp['current_section_validation']={'section':446,'receipt':'verification/sections/446.json','necessary_checks':171,'native_scopes':{'inventory_modes':32},'full_validation_rerun':False}
cp['current_batch'].update(completed_sections=446,next_section=447,next_section_started=False,receipt='verification/sections/446.json',scope='Whole-program/video review active. Functional446 verified kettle quantities and exact merge plus description-card/icon modes completed in listed scope; other pages and real continuous recognition remain.447 not started.')
cp['next_action']='继续地图/笔记/历史及其余视频效果逐页回顾，优先外部成熟代码适配；保留重复热水壶的物理件数与身份区分和图文模式。MaaFramework多页面/连续等条件比较和OCR同步，全程序/视频及P3/P2/P1未完成。后续447，下次完整455。'
if isinstance(cp.get('player_feature_sections'),list):cp['player_feature_sections'].append(446)
assert cp['functional_sections_since_latest_requirement'][-1]==445;cp['functional_sections_since_latest_requirement'].append(446)
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==446
write(B/'final-audit.json',{'passed':True,'functional_section':446,'necessary_distinct_tests':171,'native_checks':32,'ordered_selectors':733,'active_functional_list_includes446':True,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'section_receipt':pin('verification/sections/446.json'),'current_full_rerun':False,'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():pin(p)for p in B.rglob('*')if p.is_file()and p.name!='archive-manifest.json'}
files['verification/sections/446.json']=pin('verification/sections/446.json')
write(B/'archive-manifest.json',{'kind':'exact_public_446_inventory_scope_not_globbed_older_theme_candidate','files':files})
print(json.dumps({'passed':True,'section':446,'necessary_distinct_tests':171,'native_checks':32,'public_archive_files':len(files),'private_batch_unchanged':not changed,'goal_complete':False}))
