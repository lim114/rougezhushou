"""Per-section save and verified ordinary publication; execute only completed sections."""
from pathlib import Path
from datetime import datetime,timezone
import runpy,json,sys,re,subprocess
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts')]
base=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'))
read,write,pin,source,block,git,publish=[base[k]for k in('read','write','pin','source','block','git','publish')]
DOCS={'AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','CLOUD_INDEX.json','CLOUD_HANDOFF.md','DEVELOPMENT_CHECKPOINT.json','VIDEO_PARITY.md'}
def stage_commit(n,message):
 assert git('branch','--show-current').decode().strip()=='codex/p2-development'
 names=set(git('diff','--name-only').decode().splitlines())|set(git('ls-files','--others','--exclude-standard').decode().splitlines())
 extra=('verification/sections/382-repaired-for395-attempt2/','verification/sections/382-repaired-for395-attempt2-process/')if n==395 else()
 for name in names:assert name in DOCS or name.startswith(('rouge/','scripts/','tests/',f'verification/sections/{n}',f'verification/full-{n}/',*extra)),name
 # Full archives exceed Windows' command-line length. Keep exact audited paths.
 pathspec=R/f'.cache/stage-{n}.paths';pathspec.write_bytes(b'\0'.join(name.encode('utf8')for name in sorted(names))+b'\0')
 subprocess.run(['git','--literal-pathspecs','add','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul'],cwd=R,check=True)
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
 full=n in(395,410);lastfull=n if full else 395
 if full:
  summary=read(f'verification/full-{n}/summary.json');assert summary['available_checks_passed']and summary['scope_not_reduced']and summary['actual_root_controller_exit']==0
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
 if s.get('source_receipt'):receipt['sources']=pin(s['source_receipt'])
 write(f'verification/sections/{n}.json',receipt)
 cp.update(completed_sections=n,latest_functional_section=n,next_section=n+1,batch_start_section=395,batch_target_section=410,batch_status=f'PLAYER_SECTION{n}_PUBLICATION_PENDING',next_full_validation_after=410 if n<410 else 425)
 cp['sections'].append({'number':n,'completion_ref':f'player-section-{n}','topic':s['title'],'verification':f'verification/sections/{n}.json'})
 cp['current_section_save']={'section':n,'verification':f'verification/sections/{n}.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_batch']={'start':395,'end':410,'next_full_validation_after':410 if n<410 else 425,'status':cp['batch_status'],'completed_sections':n,'next_section':n+1,'next_section_started':False,'batch_closed':False,'receipt':f'verification/sections/{n}.json'}
 cp['policy'].update(new_functional_sections_paused=False,development_paused_by_latest_user_request=False,stop_after_section=410,current_user_batch_target_section=410,batch_target_section=410,current_user_batch_completed=False,next_full_validation_after=410 if n<410 else 425)
 cp['policy'].pop('paused_after_completed_section',None)
 usage_path=R/f'verification/sections/{n}-usage.json'
 if usage_path.exists():
  usage=read(usage_path.relative_to(R).as_posix());cp['policy'].update(current_usage_remaining_percent=usage['remaining_percent'],current_usage_receipt=usage_path.relative_to(R).as_posix(),usage_percent_available=usage['remaining_percent']is not None,usage_wrap_up_triggered=usage['triggered'])
 cp['current_batch_commit_policy']['next_full_validation_after']=cp['next_full_validation_after']
 cp['next_action']=s['next']+('第410节完成全部可用范围、普通发布核对后暂停，不启动411。'if n<410 else'第410节完整发布后暂停，411未启动。')
 if full:
  cp['historical_before_full'+str(n)]={k:cp.get(k)for k in('current_available_full_validation','last_full_validation')}
  proof={'receipt':f'verification/full-{n}/summary.json','sha256':pin(f'verification/full-{n}/summary.json')['sha256'],'source_freeze':summary['source_freeze'],'source_freeze_sha256':summary['source_freeze_sha256'],'actual_validation_attempt':summary['actual_validation_attempt'],'archive_manifests_sha256':summary['archive_manifests_sha256'],'root_PNG_visual_review':summary['root_PNG_visual_review']}
  cp['current_available_full_validation']={'section':n,'receipt':proof['receipt'],'available_scope_passed':True,'actual_validation_attempt':summary['actual_validation_attempt'],'actual_root_controller_exit':0,'single_available_scope_execution_all_green':True,'historical_for_current_changed_source':False,'current_worktree_validation_authority':True,'public_complete_proof':proof}
  cp['last_full_validation']={'after_section':n,'receipt':proof['receipt'],'available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,'source_freeze':summary['source_freeze'],'source_freeze_sha256':summary['source_freeze_sha256'],'historical_for_current_changed_source':False,'public_complete_proof':proof}
 else:
  cp['current_available_full_validation'].update(historical_for_current_changed_source=True,current_worktree_validation_authority=False);cp['last_full_validation']['historical_for_current_changed_source']=True
 cp['current_section_validation']={'section':n,'receipt':f'verification/sections/{n}.json','full_suite_rerun':full,'last_full_receipt':f'verification/full-{lastfull}/summary.json','last_full_receipt_is_historical_for_current_changes':not full}
 cp['latest_section_environment']={'section':n,'native_windows_verified':True,'native_game_or_chat_verified':False,'current_section_full_rerun':full,'last_full_receipt':f'verification/full-{lastfull}/summary.json','last_full_receipt_is_historical_for_current_changes':not full}
 cp['functional_sections_since_latest_requirement'].append(n);cp['cloud_publication_closeout']={'section':n,'current_commit_kind':'functional section pending actual publication','next_section_started':False,'development_paused':False}
 cp['windows_native_validation']=f'当前{n}：{count}项必要检查、{native["unique_checks"]}项原生窗口检查通过；隔离状态与九类外部操作零。'+('当前完整可用范围已按本节来源重新验收；原私样本、历史系统和实际游戏/聊天不冒充通过。'if full else'395全量仅历史，不证明改后源码；下次410。')
 write('DEVELOPMENT_CHECKPOINT.json',cp)
 body=f'## 当前第{n}节 + '+s['title']+'\n\n'+s['change']+'\n\n'+s['limits']+f'\n\n实际{count}项必要检查、{native["unique_checks"]}项原生窗口唯一检查通过，原图逐张查看；只用临时状态，九类外部操作零。'+('到期完整可用范围已按当轮源冻结验收。'if full else'395全量仅为历史来源，下一410完整范围不缩减。')+' P3/P2/P1未全部完成，识别最后。\n\n<!-- player-publication-pending -->普通推送与远端核对待完成。'
 for name in('AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):block(name,body)
 p=R/'WORK_IN_PROGRESS.md';text=p.read_text('utf8');text=re.sub(r'<!-- active410:start -->.*?<!-- active410:end -->\s*','',text,flags=re.S);p.write_text(text,encoding='utf8',newline='\n')
 requirements='## 当前批次要求 · 继续至410节\n\n最高优先五条项目要求继续有效。本批从395逐节实现至410；每节必须交付实际功能、必要验证、要求与云端索引，并普通推送核对远端。395和410执行到期完整可用范围，304/305显式传当轮source-freeze；410完整收尾后暂停，411不自动启动。严格低于15%可用额度才开始当前完整小节收尾。\n\n最终按VIDEO_PARITY.md逐项对齐普通玩家可理解的布局、交互、资料和统计。公开路标数据只读取并在本机计算，不上传个人对局/截图/聊天/培养。历史频率、抽取权重、本局条件概率分别说明；资料无充分依据时直接查来源并保留未知。同名版本不擅自合并。仅局外查阅和后台只读采样，不推荐或自动选路、不操作游戏、不发送开发测试聊天、不清空本局或覆盖私人配置；只有用户手动新局重置本局。识别优化最后。\n\n'
 block('PROJECT_REQUIREMENTS.md',requirements+body)
 runpy.run_path(str(R/'scripts/update_cloud_index.py'))['update'](R)
 result=runpy.run_path(str(R/'scripts/update_cloud_index.py'))['validate_delivery'](R,read('DEVELOPMENT_CHECKPOINT.json'));write(f'verification/sections/{n}-index-validation.json',{'passed':True,'validation':result})
 out=R/f'verification/sections/{n}-player-execution';out.mkdir(exist_ok=True);(out/'delivery-source.py').write_bytes(Path(__file__).read_bytes());(out/'publication-helper-source.py').write_bytes((R/'.cache/player_batch_pipeline.py').read_bytes());write(f'verification/sections/{n}-player-execution/spec.json',s)
 stage_commit(n,f'第{n}节：'+s['title']);publish(n,'functional')
def metadata(n):
 proof=read(f'verification/sections/{n}-publication.json');assert proof['passed']and git('rev-parse','HEAD').decode().strip()==proof['commit'];cp=read('DEVELOPMENT_CHECKPOINT.json');paused=n==410
 cp['last_verified_cloud_save']={'section':n,'scope':'current_functional_section','binding':'verified_remote_commit','commit':proof['commit'],'proof':f'verification/sections/{n}-publication.json','proof_sha256':pin(f'verification/sections/{n}-publication.json')['sha256']}
 cp['batch_status']=f'PLAYER_SECTION{n}_PUBLISHED'+('_PAUSED'if paused else'');cp['current_batch'].update(status=cp['batch_status'],batch_closed=paused);cp['policy'].update(new_functional_sections_paused=paused,development_paused_by_latest_user_request=paused,current_user_batch_completed=paused)
 cp['cloud_publication_closeout']={'section':n,'functional_commit':proof['commit'],'proof':f'verification/sections/{n}-publication.json','current_commit_kind':'publication metadata only','next_section_started':False,'development_paused':paused};write('DEVELOPMENT_CHECKPOINT.json',cp)
 for name in('AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','PROJECT_COMPLETED.md'):
  p=R/name;text=p.read_text('utf8');pending='<!-- player-publication-pending -->普通推送与远端核对待完成。';assert text.count(pending)==1
  p.write_text(text.replace(pending,f'本节功能提交{proof["commit"]}已普通推送并核对真实远端及{len(proof["verified_commit_tree_and_local_public_bytes"])}份公开文件。'+('已到410并暂停，411未启动。'if paused else f'后续{n+1}尚未启动，本批目标410。')),encoding='utf8',newline='\n')
 runpy.run_path(str(R/'scripts/update_cloud_index.py'))['update'](R)
 stage_commit(n,f'同步第{n}节发布证明、要求与云端索引');publish(n,'metadata')
if __name__=='__main__':
 assert sys.argv[1]in('close','metadata');globals()[sys.argv[1]](int(sys.argv[2]))
