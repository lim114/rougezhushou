from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy,sys,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return {'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
title='当前固定地图方格、原图近似中心与跨版本地形核对'
change='当前关卡地图页新增独立方格/原图对照入口，全部184份当前配置可查看完整静态方格与地形中文标注。对13份旧公开完整原件重新核对SHA与字节数，固定完整mapData、mapId、cameraPlugin及tilesDisallowToLocate，与当前对应导出和原图字节分别比较；不靠名称、同ID或只有相同图片继承坐标。在33份当前配置、13张不同原图上显示265条跨配置的已独立复读中心引用（不是265个独立物理格），其中含10份旧地标没有同ID的DLC配置。左侧点格或从已核对中心列表选择，右侧仅画对应近似中心并随窗口缩放；未读格与未准入地图保留方格和准确原图，不造标记，不从图片反推格子，也不连成路径。刷新保留格子、列表、页签和非零阅读，坏源清图清旧并要求重新选格，重复打开/父窗关闭均关闭旧位置窗口。实际截图发现的格子列表回到占位项问题在本节修正，以稳定的格子标识保持同步。'
limits='这是完整导出几何与完全相同PNG下的已有中心引用复用，不是新增测量、完整平面投影或实际战斗位置。四像素仅是两次旧记录的相互差值上限，不能当绝对定位精度。原始地块语义包含所有mapData字段，不只核对四项地形摘要；相机/边界/标签/效果/层矩形/黑板及图像发生变化均不能继承。仅已证低地普通地面/道路中心可画，高台表面、其它地块、实际出生偏移、原图逆向点击和整段路径均未验证；其它151份配置仍无此中心映射。没有核验真实战场显示、服务器脚本或当前地图版本与安装客户端一致。新184引用/85原图的完整校准、节点事件条件、完整奖励池和时钟等P3缺口保留；P3/P2/P1未完成，识别优化最后。本局记忆、旧数值与聊天不变，不操作游戏。'

necessary='verification/sections/319-necessary-attempt2/process.json';native='verification/sections/319-native-attempt2/actual/window.json';process='verification/sections/319-native-attempt2/process.json';source='verification/sections/319-source-attempt2/process.json';visual='verification/sections/319-root-visual.json';main='verification/sections/319-main-window.json';reg='verification/sections/319-preparation/maintained-registration.json'
n,w,p,s,v,m=(read(x)for x in(necessary,native,process,source,visual,main))
assert n['passed']and n['exit_code']==0 and n['methods_ran']==48
assert w['passed']and w['unique_checks']==29 and w['qpa']=='windows'and w['qt_exit_code']==0 and w['verification_window_closed']
assert len(w['actual_readings'])==7 and len(w['same_identity_refresh_observations'])==2
assert all(x==0 for x in w['external_operation_attempts'].values())and p['passed']and p['window_receipt_sha256']==sha(native)
assert s['passed']and s['exit_code']==0
for value in(n,w,s):
 assert value['source_sha256_before']==value['source_sha256_after']
 for name,digest in value['source_sha256_after'].items():assert sha(name)==digest,name
assert v['all_reviewed']and len(v['images'])==5
for image in v['images']:assert image['root_viewed']and sha(image['file'])==image['sha256']
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
rr=read(reg);assert rr['before_count']==504 and rr['after_count']==507 and rr['original_ordered_prefix_unchanged']and rr['source_sha256']==sha('scripts/verify_full_available.py')
from rouge import current_map_position as model
ref=model.packet();assert ref is not None
scope={'game_commit':model.battle.version.NEW_COMMIT,'baseline_game_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add','full_current_static_grid_refs':184,'compatible_stage_refs':33,'unique_exact_pngs':13,'observed_center_refs_across_stage_configs_not_unique_physical_cells':265,'baseline_complete_public_originals_checked':13,'new_landmark_measurements':False,'new_DLC_refs_with_different_legacy_id':10,'geometry_keys':['mapData','mapId','cameraPlugin','tilesDisallowToLocate'],'complete_mapData_not_only_four_attributes':True,'full_map_projection_verified':False,'absolute_actual_battle_accuracy_verified':False,'inverse_or_route_segments_verified':False,'actual_run_memory_updated':False}
out=ROOT/'verification/sections/319-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_319.py',out/'execution-main-window.py');(out/'source-scope.json').write_bytes(enc(scope))
usage=read('verification/sections/319-preparation/usage-final.json');assert usage['remainingPercent']>=15
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section319-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':319,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development',
 'necessary_validation':{**pin(necessary),'methods_run':48,'actual_exit':0},'native_windows_validation':{**pin(native),'process':pin(process),'unique_checks':29,'actual_Qt_exit':0,'actual_source_readings_and_jumps':7,'real_nonzero_refresh_states':2,'actual_MainWindow_compact_viewport':True,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},
 'source_build':pin(source),'root_visual_review':pin(visual),'original_project_window':pin(main),'maintained_registry':pin(reg),'source_manifest':pin(model.MANIFEST),
 'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'source_scope':scope,
 'failed_product_validation_attempts':[pin('verification/sections/319-combo-regression-before/process.json')],'source_failure_history':[],
 'failure_explanation':'Initial necessary/native1 passed but root screenshot audit found mapped grid selection left combo on placeholder. Added semantic selected-choice regression and observed actual failure; changed internal QVariant tuple choices to stable scalar cell keys. Final necessary2/native2 bind exact corrected source; first screenshots and red test retained.',
 'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'P1_complete':False,
 'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/319.json').write_bytes(enc(r))
validation='实际48项必要检查、29项Windows原生唯一检查通过；主窗口打开三份有证地图及一份未准入地图，7组格子/中心与未映射阅读、两种真实窗口尺寸的标记比例核对、两组非零滚动选区保持、真实公开文件损坏清旧与手动恢复，以及重复开窗/父窗关闭通过。五张最终截图均已查看；七类游戏采样/聊天/凭证调用零次，临时本局与旧计算上下文不变。504维护选择器原序保持，现507。首轮截图发现的列表占位问题、实际失败回归、修复后最终回执并存。原项目窗口正常更新，可见响应，正常关闭至启动期间私人五路径不变。未重跑全量，305仅历史范围，下次定期全量320；符号链接1314、历史私样本、Linux/Wine和游戏聊天未计通过。'
details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
 text=(ROOT/name).read_text('utf8')
 if name=='WORK_IN_PROGRESS.md':assert text.startswith('## 正在进行第319节');text=text[text.index('## 第318节'):]
 doc(name,'## 第319节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述319为准。\n\n'+text)
text=(ROOT/'AGENTS.md').read_text('utf8');end=text.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第319节 + '+title+'\n\n'+details+'\n\n继续P3，后续320优先新事件前置/作战与地图入口、完整奖励池和原图映射的剩余缺口。严格低于15%才开始完整收尾，下次定期全量320。\n'+text[end:])
text=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');a=text.index('<!-- current-delivery:start -->');marker='<!-- current-delivery:end -->';b=text.index(marker)+len(marker)
doc('PROJECT_REQUIREMENTS.md',text[:a]+'<!-- current-delivery:start -->\n## 第319节 + '+title+'\n\n'+details+'\n'+marker+text[b:])
text=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');text=text.replace('新184引用/85原图的位置校准与独立地标核验','当前33引用/13原图的其余地块、绝对精度与脚点，以及其它151引用的位置校准和独立地标核验',1).replace('新184引用/85原图需按新关卡几何独立确认适用范围，不能仅凭同名或同图沿用旧矩阵','当前33引用/13原图的完整地块与绝对精度、其它151引用需独立确认的完整几何和像素对应；不能仅凭同名或同图沿用旧矩阵',1);doc('PROJECT_PROGRESS.md',text)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==318 and cp['next_section']==319
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
 if key in cp:cp['historical_before319_'+key]=cp.pop(key)
cp.update(completed_sections=319,latest_functional_section=319,next_section=320,batch_status='P3_SECTION319_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第319节 + '+title+'已本地验收。普通推送核对后接续事件前置/作战入口、完整奖励池和原图映射；320未启动，下一定期全量320。')
cp['sections'].append({'number':319,'completion_ref':'p3-section-319','topic':title,'verification':'verification/sections/319.json'});cp['functional_sections_since_latest_requirement'].append(319)
cp['current_section_save']={'section':319,'verification':'verification/sections/319.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':319,'receipt':'verification/sections/319.json','necessary_methods_passed':48,'native_isolated_window_checks':29,'actual_source_readings_and_jumps':7,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':319,'receipt':'verification/sections/319.json','native_windows':'48 necessary;29 native actual MainWindow/current grid and original center checks;7 readings and2 nonzero states;original app/private5 preservation verified','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=319,next_section=320,next_section_started=False,receipt='verification/sections/319.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=usage['remainingPercent'],current_usage_receipt='verification/sections/319-preparation/usage-final.json')
cp['current_data_versions'].update(current_map_position_game_commit=model.battle.version.NEW_COMMIT,current_map_position_manifest=model.MANIFEST,current_map_partial_center_stage_refs=33,current_map_partial_center_unique_images=13,current_map_full_projection_verified=False,current_map_new_landmark_measurements=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section319-handoff:start -->\n## 第319节 + '+title+'\n\n'+details+'\n<!-- section319-handoff:end -->\n')
import subprocess
p=ROOT/'WORK_IN_PROGRESS.md';current=p.read_bytes();old=subprocess.check_output(['git','show','9311073ebd2f38d7a00523f728a338e326407e10:WORK_IN_PROGRESS.md'],cwd=ROOT);marker='## 第318节'.encode();at=current.index(marker);assert current[at:].decode().replace('\r\n','\n')==old.decode().replace('\r\n','\n');prefix=current[:at].decode().replace('\r\n','\n').replace('\n','\r\n');p.write_bytes(prefix.encode()+old)
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/319-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':319,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next320_started':False,'at_Beijing':now}))
print(json.dumps({'section_label':read('CLOUD_INDEX.json')['current_section_label'],'scope':scope,'publication_pending':True},ensure_ascii=False))
