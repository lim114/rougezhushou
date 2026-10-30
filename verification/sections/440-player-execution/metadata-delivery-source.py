"""Per-section save and verified ordinary publication; execute only completed sections."""
from pathlib import Path
from datetime import datetime,timezone
import runpy,json,sys,re,subprocess
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts')]
base=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'))
read,write,pin,source,block,git,publish=[base[k]for k in('read','write','pin','source','block','git','publish')]
DOCS={'AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','CLOUD_INDEX.json','CLOUD_HANDOFF.md','DEVELOPMENT_CHECKPOINT.json','VIDEO_PARITY.md','IMPLEMENTATION_STRATEGY.md'}
def preserve_document_eols():
 import difflib
 for name in DOCS-{'CLOUD_INDEX.json','CLOUD_HANDOFF.md'}:
  p=R/name
  old=git('show','HEAD:'+name).decode('utf8').splitlines(keepends=True)
  new=p.read_text('utf8').splitlines(keepends=True)
  output=list(new)
  matcher=difflib.SequenceMatcher(None,[x.rstrip('\r\n')for x in old],[x.rstrip('\r\n')for x in new],autojunk=False)
  for a,b,size in matcher.get_matching_blocks():
   for i in range(size):output[b+i]=old[a+i]
  p.write_bytes(''.join(output).encode('utf8'))

def stage_commit(n,message):
 assert git('branch','--show-current').decode().strip()=='codex/p2-development'
 names={v.decode('utf8')for v in git('diff','--name-only','-z').split(b'\0')if v}|{v.decode('utf8')for v in git('ls-files','--others','--exclude-standard','-z').split(b'\0')if v}
 extra=('verification/sections/382-repaired-for395-attempt2/','verification/sections/382-repaired-for395-attempt2-process/')if n==395 else()
 for name in names:assert name in DOCS or name.startswith(('rouge/','scripts/','tests/',f'verification/sections/{n}',f'verification/full-{n}/','research/public-compendium-413/',*extra)),name
 # Include manifest-declared public logs even when ordinary Git ignores them.
 # Never force-stage arbitrary ignored working files, cache or private state.
 from hashlib import sha256
 from pathlib import PurePosixPath
 full_scope=R/f'verification/full-{n}'
 if full_scope.is_dir():
  for manifest in sorted(full_scope.glob('execution-attempt*/archive-manifest.json')):
   archive=manifest.parent;declared=read(manifest.relative_to(R).as_posix())
   assert declared['section']==n and declared['kind']==f'EXACT_FULL{n}_ORIGINAL_EXECUTION_ARCHIVE'
   for member,expected in declared['files'].items():
    rel=PurePosixPath(member);assert not rel.is_absolute()and'..'not in rel.parts and'\\'not in member and':'not in member
    target=archive.joinpath(*rel.parts);assert target.is_file()and not target.is_symlink()and target.resolve().is_relative_to(full_scope.resolve())
    raw=target.read_bytes();assert sha256(raw).hexdigest()==expected['sha256']and len(raw)==expected['bytes']
    names.add(target.relative_to(R).as_posix())
 # Full archives exceed Windows' command-line length. Keep exact audited paths.
 pathspec=R/f'.cache/stage-{n}.paths';pathspec.write_bytes(b'\0'.join(name.encode('utf8')for name in sorted(names))+b'\0')
 subprocess.run(['git','--literal-pathspecs','add','-f','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul'],cwd=R,check=True)
 subprocess.run(['git','-c','core.whitespace=cr-at-eol,-blank-at-eof','diff','--cached','--check'],cwd=R,check=True)
 subprocess.run(['git','-c','gc.auto=0','commit','--quiet','-m',message],cwd=R,check=True)
def close(n):
 s=read(f'.cache/spec{n}.json');cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==n-1
 up=s.get('unit_receipt',f'verification/sections/{n}-player-checks/process.json');wp=s.get('native_receipt',f'verification/sections/{n}-player-window/window.json');pp=s.get('native_process_receipt',f'verification/sections/{n}-player-window-process/process.json')
 unit=read(up);native=read(wp);np=read(pp)
 assert all(v['passed']for v in(unit,native,np))and source()==unit['source_sha256_after']==native['source_sha256_after']
 assert not any(native['external_operation_attempts'].values())and native['unique_checks']==len(set(native['checks']))>0
 log=(R/up).with_name('stderr.txt').read_text('utf8');count=int(re.search(r'Ran (\d+) tests?',log)[1])
 view=read(f'.cache/visual{n}.json');assert view['actual_view_image_calls']==len(native['screenshots'])and not view['blocking_visual_issues']
 for image in native['screenshots']:assert pin(image['file'])['sha256']==image['sha256']
 write(f'verification/sections/{n}-visual-agent-review.json',view)
 from scripts.verify_full_available import maintained_selectors
 selectors=maintained_selectors();assert selectors==read(f'verification/sections/{n-1}-source-audit.json')['current_selectors']+[s['test']]
 write(f'verification/sections/{n}-source-audit.json',{'section':n,'passed':True,'current_selectors':selectors,'ordered_previous_preserved':True,'source_sha256':source()})
 full=n==440;lastfull=n if full else 425
 if full:
  summary=read(f'verification/full-{n}/summary.json');assert summary['available_checks_passed']and summary['scope_not_reduced']
  if n==425 and summary.get('composition_verified'):
   assert summary['actual_root_controller_exit']==1 and summary['actual_selected_repair_controller_exit']==0 and summary['single_available_scope_execution_all_green']is False
   assert summary['all_product_and_game_data_bytes_equivalent_across_composition'] and read('verification/full-425/selected-repair4-audit.json')['passed']
   assert read('verification/full-425/selected-repair4-process/process.json')['actual_observed_exit']==0
  else:assert summary['actual_root_controller_exit']==0
 receipt={'section':n,'kind':'functional_section','title':s['title'],'new_capability':s['change'],'limitations':s['limits'],'necessary_validation':pin(up),'unit_tests_run':count,'native_windows_validation':{**pin(wp),'unique_checks':native['unique_checks'],'process':pin(pp)},'root_visual_review':pin(f'verification/sections/{n}-visual-agent-review.json'),'source_sha256':source(),'full_suite_rerun':full,'last_full_receipt':f'verification/full-{lastfull}/summary.json','last_full_is_historical_for_current_changes':not full,'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_state_included':False,'cloud_publication_binding':'enclosing_commit','acceptance_criteria':s['criteria'],'recorded_at_UTC':datetime.now(timezone.utc).isoformat()}
 if full:receipt['complete_available_validation']=pin(f'verification/full-{n}/summary.json')
 if n==410:
  runtime_path='verification/sections/410-main-window/window.json';runtime=read(runtime_path)
  desktop_path='verification/sections/410-main-window/desktop-review.json';desktop=read(desktop_path)
  assert runtime['passed'] and runtime['private_six_paths_including_shortcut_unchanged'] and not runtime['private_contents_or_hashes_published']
  assert runtime['source_sha256_before']==runtime['source_sha256_after']==source()
  assert desktop['section']==410 and desktop['actor']=='/root' and desktop['actual_windows_mcp_snapshot_called'] and desktop['actual_live_surface_reviewed'] and not desktop['blocking_issues']
  assert desktop['runtime_receipt_sha256']==pin(runtime_path)['sha256'] and set(desktop['matching_owned_pids']) & {row['pid']for row in runtime['owned_windows']if row['visible']and row['responding']}
  receipt['original_project_runtime_validation']={'native_read_only_observation':pin(runtime_path),'actual_desktop_review':pin(desktop_path)}
 if n==411:
  runtime_path='verification/sections/411-main-window/window.json';runtime=read(runtime_path)
  desktop_path='verification/sections/411-main-window/desktop-review.json';desktop=read(desktop_path)
  assert runtime['passed'] and runtime['private_six_paths_unchanged'] and runtime['source_sha256_after']==source()
  assert desktop['actual_windows_mcp_snapshot_called'] and desktop['actual_live_surface_reviewed'] and not desktop['blocking_issues']
  assert desktop['runtime_receipt_sha256']==pin(runtime_path)['sha256']
  receipt['original_project_runtime_validation']={'native_read_only_observation':pin(runtime_path),'actual_desktop_review':pin(desktop_path)}
 if n==412:
  runtime_path='verification/sections/412-main-window-attempt2/window.json';runtime=read(runtime_path)
  desktop_path='verification/sections/412-main-window-attempt2/desktop-review.json';desktop=read(desktop_path)
  assert runtime['passed'] and runtime['private_six_paths_unchanged'] and runtime['source_sha256_after']==source()
  assert desktop['actual_windows_mcp_snapshot_called'] and desktop['actual_live_surface_reviewed'] and not desktop['blocking_issues']
  assert desktop['runtime_receipt_sha256']==pin(runtime_path)['sha256']
  receipt['original_project_runtime_validation']={'native_read_only_observation':pin(runtime_path),'actual_desktop_review':pin(desktop_path)}
 if n==413:
  runtime_path='verification/sections/413-main-window/window.json';runtime=read(runtime_path)
  desktop_path='verification/sections/413-main-window/desktop-review.json';desktop=read(desktop_path)
  assert runtime['passed'] and runtime['private_six_paths_unchanged'] and runtime['source_sha256_after']==source()
  assert desktop['actual_windows_mcp_snapshot_called'] and desktop['actual_live_surface_reviewed'] and not desktop['blocking_issues']
  assert desktop['runtime_receipt_sha256']==pin(runtime_path)['sha256']
  receipt['original_project_runtime_validation']={'native_read_only_observation':pin(runtime_path),'actual_desktop_review':pin(desktop_path)}
 if n==417:
  runtime_path='verification/sections/417-main-window-attempt7/window.json';runtime=read(runtime_path)
  desktop_path='verification/sections/417-main-window-attempt7/desktop-review.json';desktop=read(desktop_path)
  assert runtime['passed'] and runtime['private_six_paths_unchanged'] and runtime['source_sha256_after']==source()
  assert desktop['actual_windows_mcp_snapshot_called'] and desktop['actual_live_surface_reviewed'] and desktop['actual_shop_text_hover_card_visible'] and not desktop['blocking_issues']
  assert desktop['runtime_receipt_sha256']==pin(runtime_path)['sha256']
  receipt['original_project_runtime_validation']={'native_read_only_observation':pin(runtime_path),'actual_desktop_review':pin(desktop_path)}
 if n==425:
  probe_path='verification/sections/425-overlay-input-probe-attempt2/receipt.json';probe_process='verification/sections/425-overlay-input-probe-process-attempt2/process.json';probe=read(probe_path);observed=read(probe_process)
  assert probe['passed']and observed['passed']and probe['source_sha256_before']==probe['source_sha256_after']==observed['source_sha256_before']==observed['source_sha256_after']==source()
  assert probe['all_native_point_hits_reached_underlying_owned_process']and probe['all_query_points_verified_on_painted_overlay_pixels']and probe['foreground_unchanged_by_own_annotation_show']and probe['actual_owned_child_exit']==0
  assert probe['own_underlay_verified_below_overlay_in_native_z_order']
  assert not probe['game_operated']and not probe['chat_sent']and not probe['mouse_moved']and not probe['keyboard_or_mouse_input_sent']
  receipt['native_overlay_passthrough_validation']={'owned_two_process_fixture':pin(probe_path),'actual_observed_process':pin(probe_process),'real_game_integration_claimed':False}
  runtime_path='verification/sections/425-main-window/window.json';runtime=read(runtime_path)
  desktop_path='verification/sections/425-main-window/desktop-review.json';desktop=read(desktop_path)
  assert runtime['passed'] and runtime['private_six_paths_unchanged'] and runtime['source_sha256_after']==source()
  assert desktop['actual_windows_mcp_snapshot_called'] and desktop['actual_live_surface_reviewed'] and not desktop['blocking_issues']
  assert desktop['runtime_receipt_sha256']==pin(runtime_path)['sha256']
  receipt['original_project_runtime_validation']={'native_read_only_observation':pin(runtime_path),'actual_desktop_review':pin(desktop_path)}
 if n==440:
  runtime_path='verification/sections/440-main-window-attempt2/window.json';runtime=read(runtime_path)
  desktop_path='verification/sections/440-main-window-attempt2/desktop-review.json';desktop=read(desktop_path)
  assert runtime['passed'] and runtime['private_six_paths_unchanged'] and runtime['source_sha256_before']==runtime['source_sha256_after']==source()
  assert runtime['private_contents_or_hashes_published'] is False and runtime['game_operated'] is False and runtime['chat_sent'] is False
  assert desktop['actual_windows_mcp_snapshot_called'] and desktop['actual_live_surface_reviewed'] and not desktop['blocking_issues']
  assert desktop['runtime_receipt_sha256']==pin(runtime_path)['sha256']
  assert set(desktop['matching_owned_pids']) & {row['pid']for row in runtime['owned_windows']if row['visible']and row['responding']}
  final_path='verification/sections/440-main-window-attempt2/final-response.json';final=read(final_path)
  final_desktop_path='verification/sections/440-main-window-attempt2/final-desktop-review.json';final_desktop=read(final_desktop_path)
  assert final['passed'] and final['actual_after_complete_full_scope'] and final['all_runtime_source_paths_match_completed_full_freeze']
  assert final['source_sha256_before']==final['source_sha256_after']==source() and final['actual_Qt_timer_status_advanced']
  assert final['complete_full_summary_sha256']==pin('verification/full-440/summary.json')['sha256']
  assert final_desktop['actual_windows_mcp_snapshot_called'] and final_desktop['actual_live_surface_reviewed'] and not final_desktop['blocking_issues']
  assert final_desktop['final_response_sha256']==pin(final_path)['sha256'] and final_desktop['complete_full_summary_sha256']==final['complete_full_summary_sha256']
  receipt['original_project_runtime_validation']={'native_read_only_observation':pin(runtime_path),'initial_actual_desktop_review':pin(desktop_path),'actual_post_full_response':pin(final_path),'final_actual_desktop_review':pin(final_desktop_path)}
 if s.get('source_receipt'):receipt['sources']=pin(s['source_receipt'])
 write(f'verification/sections/{n}.json',receipt)
 cp.update(completed_sections=n,latest_functional_section=n,next_section=n+1,batch_start_section=426,batch_target_section=440,batch_status=f'PLAYER_SECTION{n}_PUBLICATION_PENDING',next_full_validation_after=440 if n<440 else 455)
 cp['sections'].append({'number':n,'completion_ref':f'player-section-{n}','topic':s['title'],'verification':f'verification/sections/{n}.json'})
 cp['current_section_save']={'section':n,'verification':f'verification/sections/{n}.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_batch']={'start':426,'end':440,'next_full_validation_after':440 if n<440 else 455,'status':cp['batch_status'],'completed_sections':n,'next_section':n+1,'next_section_started':False,'batch_closed':False,'receipt':f'verification/sections/{n}.json'}
 cp['policy'].update(new_functional_sections_paused=False,development_paused_by_latest_user_request=False,stop_after_section=440,current_user_batch_target_section=440,batch_target_section=440,current_user_batch_completed=False,pause_after_active_section_requested=False,next_full_validation_after=440 if n<440 else 455)
 cp['policy'].pop('paused_after_completed_section',None)
 cp.pop('active_functional_work',None)
 cp['policy']['video_appearance_parity_required']=True
 cp['implementation_strategy']['status']='ongoing_functional_delivery_not_full_video_completion'
 cp['implementation_strategy']['last_functional_section']=n
 cp['implementation_strategy']['next_functional_section_started']=False
 cp['implementation_strategy']['sha256']=pin('IMPLEMENTATION_STRATEGY.md')['sha256']
 usage_path=R/f'verification/sections/{n}-usage.json'
 if n==425:usage_path=R/'verification/sections/425-usage-publication.json'
 if n==440:usage_path=R/'verification/sections/440-usage-closeout.json'
 if usage_path.exists():
  usage=read(usage_path.relative_to(R).as_posix());cp['policy'].update(current_usage_remaining_percent=usage['remaining_percent'],current_usage_receipt=usage_path.relative_to(R).as_posix(),usage_percent_available=usage['remaining_percent']is not None,usage_wrap_up_triggered=usage['triggered'])
 cp['current_batch_commit_policy']['next_full_validation_after']=cp['next_full_validation_after']
 cp['next_action']=s['next']
 if full:
  cp['historical_before_full'+str(n)]={k:cp.get(k)for k in('current_available_full_validation','last_full_validation')}
  proof={'receipt':f'verification/full-{n}/summary.json','sha256':pin(f'verification/full-{n}/summary.json')['sha256'],'source_freeze':summary['source_freeze'],'source_freeze_sha256':summary['source_freeze_sha256'],'actual_validation_attempt':summary['actual_validation_attempt'],'archive_manifests_sha256':summary['archive_manifests_sha256'],'root_PNG_visual_review':summary['root_PNG_visual_review']}
  cp['current_available_full_validation']={'section':n,'receipt':proof['receipt'],'available_scope_passed':True,'actual_validation_attempt':summary['actual_validation_attempt'],'actual_root_controller_exit':summary['actual_root_controller_exit'],'single_available_scope_execution_all_green':summary.get('single_available_scope_execution_all_green',True),'validation_composition':summary.get('validation_composition'),'actual_selected_repair_controller_exit':summary.get('actual_selected_repair_controller_exit'),'historical_for_current_changed_source':False,'current_worktree_validation_authority':True,'public_complete_proof':proof}
  cp['last_full_validation']={'after_section':n,'receipt':proof['receipt'],'available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,'source_freeze':summary['source_freeze'],'source_freeze_sha256':summary['source_freeze_sha256'],'historical_for_current_changed_source':False,'public_complete_proof':proof}
 else:
  cp['current_available_full_validation'].update(historical_for_current_changed_source=True,current_worktree_validation_authority=False);cp['last_full_validation']['historical_for_current_changed_source']=True
 cp['current_section_validation']={'section':n,'receipt':f'verification/sections/{n}.json','full_suite_rerun':full,'last_full_receipt':f'verification/full-{lastfull}/summary.json','last_full_receipt_is_historical_for_current_changes':not full}
 cp['latest_section_environment']={'section':n,'native_windows_verified':True,'native_game_or_chat_verified':False,'current_section_full_rerun':full,'last_full_receipt':f'verification/full-{lastfull}/summary.json','last_full_receipt_is_historical_for_current_changes':not full}
 cp['functional_sections_since_latest_requirement'].append(n);cp['cloud_publication_closeout']={'section':n,'current_commit_kind':'functional section pending actual publication','next_section_started':False,'development_paused':False}
 cp['windows_native_validation']=f'当前{n}：{count}项必要检查、{native["unique_checks"]}项原生窗口检查通过；隔离状态与九类外部操作零。'+('当前完整可用范围已按本节来源重新验收；原私样本、历史系统和实际游戏/聊天不冒充通过。'if full else'425全量仅历史，不证明改后源码；下次440。')
 write('DEVELOPMENT_CHECKPOINT.json',cp)
 body=f'## 当前第{n}节 + '+s['title']+'\n\n'+s['change']+'\n\n'+s['limits']+f'\n\n实际{count}项必要检查、{native["unique_checks"]}项原生窗口唯一检查通过，原图逐张查看；只用临时状态，九类外部操作零。'+(('到期完整原范围及实际组合复验已核对；未变产品源码和资料按整字节复用，原失败和退出保留，不称单轮全绿。'if summary.get('composition_verified')else'到期完整可用范围已按当轮源冻结验收。')if full else'425全量仅为历史来源，下一440完整范围不缩减。')+' P3/P2/P1未全部完成，识别最后。\n\n<!-- player-publication-pending -->普通推送与远端核对待完成。'
 if n==440:body+='\n\n原项目实际测试小窗已更新到本节源码并打开，Windows桌面实见且响应。正常关闭旧测试窗与启动区间六份私人路径仅本机摘要核对保持，不复制或发布内容。窗口只证明本机运行，不代替实机游戏、聊天或计算准确性验收。'
 for name in('AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):block(name,body)
 p=R/'WORK_IN_PROGRESS.md';text=p.read_text('utf8');text=re.sub(r'<!-- active410:start -->.*?<!-- active410:end -->\s*','',text,flags=re.S);text=re.sub(r'<!-- active-player-section:start -->.*?<!-- active-player-section:end -->\s*','',text,flags=re.S);p.write_text(text,encoding='utf8',newline='\n')
 requirements='## 当前批次要求 · 视频全部效果与外观对齐\n\n用户明确继续开发，用户已解除425后的暂停；本批从426自主推进至440，完成440到期完整可用范围、普通发布核对后暂停，不启动441。最高优先五条要求继续有效。最终同时达到参考录像演示的功能、实际交互及界面外观：以项目目录中用户提供的视频原件为准，不确定时先回看片段；逐页对照布局、配色、字体、图标、留白、圆角、浮窗比例与位置、地图和悬浮提示，不使用笼统的“视频风格”措辞冒充一致；不同分辨率按合适比例适配，不以新增栏目或功能存在代替外观验收。\n\n保留现有Python/Qt实现，优先整合场景资料和笔记流程、共享读取结果与本机缓存。实现思路可独立取舍；隐私、只读、不自动选路等明确边界不变。方案见IMPLEMENTATION_STRATEGY.md，逐项缺口见VIDEO_PARITY.md。每节实际功能、必要验收、要求与索引同提交普通推送并核对真实远端；下一到期完整可用范围440，严格低于15%开始当前完整小节收尾。\n\n仅局外查阅和后台只读采样，不操作游戏、不发送开发测试聊天、不上传私人数据、不清空本局或覆盖私人配置；只有用户手动新局重置本局。普通ChatGPT聊天目标保留，不用Codex分析后端代替。历史比例、权重与本局概率分别说明，未知先查来源；P3优先，P2/P1保留，识别优化最后。\n\n'
 requirements+='商店有现成文字，优先读取本帧商品名称并用价格文字核对对应位置；已确认商店而文字不足时保持未确认，不强行以图标补猜。价格标签用于定位不代表已读取售价、购买或持有状态；5秒是悬停触发等待，实际文字读取另需时间。\n\n'
 block('PROJECT_REQUIREMENTS.md',requirements+body)
 preserve_document_eols()
 runpy.run_path(str(R/'scripts/update_cloud_index.py'))['update'](R)
 result=runpy.run_path(str(R/'scripts/update_cloud_index.py'))['validate_delivery'](R,read('DEVELOPMENT_CHECKPOINT.json'));write(f'verification/sections/{n}-index-validation.json',{'passed':True,'validation':result})
 out=R/f'verification/sections/{n}-player-execution';out.mkdir(exist_ok=True);(out/'delivery-source.py').write_bytes(Path(__file__).read_bytes());(out/'publication-helper-source.py').write_bytes((R/'.cache/player_batch_pipeline.py').read_bytes());write(f'verification/sections/{n}-player-execution/spec.json',s)
 stage_commit(n,f'第{n}节：'+s['title']);publish(n,'functional')
def metadata(n):
 proof=read(f'verification/sections/{n}-publication.json');assert proof['passed']and git('rev-parse','HEAD').decode().strip()==proof['commit'];cp=read('DEVELOPMENT_CHECKPOINT.json');paused=n==440
 cp['last_verified_cloud_save']={'section':n,'scope':'current_functional_section','binding':'verified_remote_commit','commit':proof['commit'],'proof':f'verification/sections/{n}-publication.json','proof_sha256':pin(f'verification/sections/{n}-publication.json')['sha256']}
 cp['batch_status']=f'PLAYER_SECTION{n}_PUBLISHED'+('_PAUSED'if paused else'');cp['current_batch'].update(status=cp['batch_status'],batch_closed=paused);cp['policy'].update(new_functional_sections_paused=paused,development_paused_by_latest_user_request=paused,current_user_batch_completed=paused)
 if paused:
  cp['next_action']='第440节已完成普通发布核对并暂停；441未启动，等待用户明确恢复。'
  cp['policy'].update(paused_after_completed_section=n,pause_after_active_section_requested=True)
 cp['cloud_publication_closeout']={'section':n,'functional_commit':proof['commit'],'proof':f'verification/sections/{n}-publication.json','current_commit_kind':'publication metadata only','next_section_started':False,'development_paused':paused}
 if n==440:cp['cloud_publication_closeout']['public_manifest_member_delivery_repair']=pin('verification/sections/440-publication-ignored-members.json')
 write('DEVELOPMENT_CHECKPOINT.json',cp)
 for name in('AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','PROJECT_COMPLETED.md'):
  p=R/name;text=p.read_text('utf8');pending='<!-- player-publication-pending -->普通推送与远端核对待完成。';assert text.count(pending)==1
  if n==440 and name=='PROJECT_REQUIREMENTS.md':
   old='下一到期完整可用范围440，严格低于15%开始当前完整小节收尾。'
   assert text.count(old)==1
   text=text.replace(old,'440到期完整可用范围已验收；下次455仅在用户恢复后适用，严格低于15%开始当前完整小节收尾。')
  if n==440:
   visual_notice='本节窗口原图已实际查看。完整范围保留679条图片路径：14张新原图由主代理逐张查看，另665条仅按整字节相同复用既有审阅（含30条接触表审阅），保留原审阅者与方式；图片不代替交互证明。'
   start='<!-- player-batch-current:start -->';marker='<!-- player-batch-current:end -->'
   assert text.count(start)==text.count(marker)==1
   prefix,rest=text.split(start,1);current,suffix=rest.split(marker,1)
   assert current.count('原图逐张查看')==1
   current=current.replace('原图逐张查看',visual_notice,1)
   notice='完整归档发布补充：功能提交的代码与公开文件已核对；归档清单内1290条被忽略的公开日志在本次发布元数据提交补齐。原发布缺口单独保留，不改写原始记录；不新增功能节数。后续发布须按归档清单逐路径核对，不能只核对Git默认列出的文件；仅强制加入已核对的公开验收清单成员，保留私人目录忽略规则。'
   text=prefix+start+current+notice+'\n'+marker+suffix
  p.write_text(text.replace(pending,f'本节功能提交{proof["commit"]}已普通推送并核对真实远端及{len(proof["verified_commit_tree_and_local_public_bytes"])}份公开文件。'+('已到440并暂停，441未启动。'if paused else f'后续{n+1}尚未启动，本批终点440。')),encoding='utf8',newline='\n')
 preserve_document_eols()
 runpy.run_path(str(R/'scripts/update_cloud_index.py'))['update'](R)
 out=R/f'verification/sections/{n}-player-execution'
 (out/'metadata-delivery-source.py').write_bytes(Path(__file__).read_bytes())
 stage_commit(n,f'同步第{n}节发布证明、要求与云端索引');publish(n,'metadata')
if __name__=='__main__':
 assert sys.argv[1]in('close','metadata');globals()[sys.argv[1]](int(sys.argv[2]))
