"""Actual per-section execution, public handoff and ordinary verified publication."""
from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
import argparse,json,subprocess,sys,runpy,copy
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts')]
def read(n):return json.loads((R/n).read_bytes())
def enc(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
def write(n,d):p=R/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(enc(d))
def pin(n):b=(R/n).read_bytes();return {'receipt':n,'sha256':sha256(b).hexdigest(),'bytes':len(b)}
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
def source():
 from player_ui_verification import source_hashes
 return source_hashes()
def execute(argv,out):
 p=R/out;assert not p.exists();p.mkdir(parents=True)
 before=source();start=datetime.now(timezone.utc).isoformat()
 with(p/'stdout.txt').open('xb')as o,(p/'stderr.txt').open('xb')as e:
  child=subprocess.Popen(argv,cwd=R,stdout=o,stderr=e);code=child.wait()
 after=source();result={'argv':argv,'started_UTC':start,'finished_UTC':datetime.now(timezone.utc).isoformat(),
  'actual_retained_Popen_pid':child.pid,'actual_observed_exit':code,'source_sha256_before':before,'source_sha256_after':after,
  'passed':code==0 and before==after}
 write(out+'/process.json',result)
 if not result['passed']:raise RuntimeError((p/'stderr.txt').read_text('utf8')+'\n'+(p/'stdout.txt').read_text('utf8'))
 return result
def block(name,body):
 p=R/name;s=p.read_text('utf8');start='<!-- player-batch-current:start -->';end='<!-- player-batch-current:end -->'
 if start in s:
  a,rest=s.split(start,1);prior,b=rest.split(end,1);s=a+(prior.strip()+'\n\n'if name=='PROJECT_COMPLETED.md'else'')+b.lstrip('\n')
 p.write_text(start+'\n'+body+'\n'+end+'\n\n'+s,encoding='utf8',newline='\n')
def verify(n,s):
 execute([sys.executable,'-B','-X','utf8','-m','unittest',s['test'],'-v'],f'verification/sections/{n}-player-checks')
 execute([sys.executable,'-B','-X','utf8',s['native'],'--receipt',f'verification/sections/{n}-player-window/window.json'],f'verification/sections/{n}-player-window-process')
def close(n,s):
 assert not(R/f'verification/sections/{n}.json').exists()
 cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==n-1
 unit=read(f'verification/sections/{n}-player-checks/process.json');native=read(f'verification/sections/{n}-player-window/window.json');np=read(f'verification/sections/{n}-player-window-process/process.json')
 assert unit['passed']and native['passed']and np['passed']and source()==native['source_sha256_after']==unit['source_sha256_after']

 if n==390:
  runtime=read('verification/sections/390-main-window-attempt3/window.json');integrated=read('verification/sections/390-player-integrated-checks/process.json')
  assert runtime['passed']and integrated['passed']and source()==runtime['source_sha256_after']==integrated['source_sha256_after']
 view=read(f'.cache/player-visual{n}.json');assert view['section']==n and view['actual_view_image_calls']==len(native['screenshots'])and not view['blocking_visual_issues']
 for image in native['screenshots']:assert view['images'][0]['sha256']==image['sha256']==pin(image['file'])['sha256']
 from scripts.verify_full_available import maintained_selectors
 selectors=maintained_selectors();previous=read(f'verification/sections/{n-1}-source-audit.json')['current_selectors']
 assert selectors==previous+[s['test']]
 write(f'verification/sections/{n}-source-audit.json',{'section':n,'passed':True,'current_selectors':selectors,'ordered_previous_preserved':True,'source_sha256':source(),'numeric_model_changed':False})
 write(f'verification/sections/{n}-visual-agent-review.json',view)
 receipt={'section':n,'kind':'functional_section','title':s['title'],'new_capability':s['change'],'limitations':s['limits'],
 'necessary_validation':pin(f'verification/sections/{n}-player-checks/process.json'),
 'native_windows_validation':{**pin(f'verification/sections/{n}-player-window/window.json'),'process':pin(f'verification/sections/{n}-player-window-process/process.json'),'unique_checks':native['unique_checks']},
 'root_visual_review':pin(f'verification/sections/{n}-visual-agent-review.json'),'source_sha256':source(),
 'full_suite_rerun':False,'last_full_receipt':'verification/full-380/summary.json','last_full_is_historical_for_current_changes':True,
 'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_state_included':False,
 'cloud_publication_binding':'enclosing_commit','recorded_at_UTC':datetime.now(timezone.utc).isoformat()}
 write(f'verification/sections/{n}.json',receipt)
 if n==381:
  cp['historical_before381_batch']={k:cp.get(k)for k in('current_batch','batch_status','batch_start_section','batch_target_section')}
  cp.update(batch_start_section=381,batch_target_section=390)
  cp['current_batch']={'start':381,'end':390,'next_full_validation_after':395}
 cp.update(completed_sections=n,latest_functional_section=n,next_section=n+1,batch_status=f'PLAYER_SECTION{n}_PUBLICATION_PENDING',next_action=f'第{n}节实际验收后普通推送；按新要求整合玩家界面，至390暂停。')
 cp['sections'].append({'number':n,'completion_ref':f'player-section-{n}','topic':s['title'],'verification':f'verification/sections/{n}.json'})
 cp['current_section_save']={'section':n,'verification':f'verification/sections/{n}.json','scope':'current_functional_section','binding':'enclosing_commit'}
 cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['policy'].update(new_functional_sections_paused=False,development_paused_by_latest_user_request=False,stop_after_section=390,current_user_batch_target_section=390,batch_target_section=390,current_user_batch_completed=False)
 cp['policy'].pop('paused_after_completed_section',None)
 if (R/f'verification/sections/{n}-usage.json').exists():
  _usage=read(f'verification/sections/{n}-usage.json');cp['policy'].update(current_usage_remaining_percent=_usage['remaining_percent'],current_usage_receipt=f'verification/sections/{n}-usage.json',usage_percent_available=_usage['remaining_percent']is not None,usage_wrap_up_triggered=_usage['triggered'])
 cp['current_batch'].update(status=cp['batch_status'],completed_sections=n,next_section=n+1,next_section_started=False,batch_closed=False,receipt=f'verification/sections/{n}.json')
 for k in('current_available_full_validation','last_full_validation'):
  cp[k]['historical_for_current_changed_source']=True
  if k=='current_available_full_validation':cp[k]['current_worktree_validation_authority']=False
 cp['current_section_validation']={'section':n,'receipt':f'verification/sections/{n}.json','full_suite_rerun':False,'last_full_receipt':'verification/full-380/summary.json','last_full_receipt_is_historical_for_current_changes':True}
 cp['latest_section_environment']={'section':n,'native_windows_verified':True,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-380/summary.json','last_full_receipt_is_historical_for_current_changes':True}
 cp['functional_sections_since_latest_requirement'].append(n)
 cp['cloud_publication_closeout']={'section':n,'current_commit_kind':'functional section pending actual publication','next_section_started':False,'development_paused':False}
 write('DEVELOPMENT_CHECKPOINT.json',cp)
 body=f'## 当前第{n}节 + {s["title"]}\n\n{s["change"]}\n\n本机必要检查和{native["unique_checks"]}项原生窗口检查实际通过，公开隔离状态，七类外部操作零；本轮原图已实际审阅。380完整回执是历史范围，不证明改后界面；本节未重跑全量，下一到期395。P3/P2/P1未完成，识别最后。\n\n<!-- player-publication-pending -->普通推送与远端核对待完成。\n\n本批按2026-10-28新要求继续至390；本节之后仍只做玩家界面整合，不恢复路线推荐。'
 if n==390:
  body=body.replace('本批按2026-10-28新要求继续至390；本节之后仍只做玩家界面整合，不恢复路线推荐。','本批已完成至390，发布核对后暂停，不启动391；路线推荐仍不做。')
  body+='\n\n改后界面34项必要回归和44项本机窗口联验通过。真实项目小窗已打开、可见且响应；本次正常关闭与重新启动区间五份私人路径仅摘要核对保持。两次启动检查误把虚拟环境启动器PID当成窗口PID，失败原件保留；已改为核对实际项目子窗口，不计前两次通过，也不将其误报为启动性能问题。节点统计仅为历史分布；当前DLC条件概率及事件/掉落完整联网统计仍在待办。实际回执verification/sections/390-player-integrated-checks/process.json及verification/sections/390-main-window-attempt3/window.json。'
 for name in('AGENTS.md','WORK_IN_PROGRESS.md'):block(name,body)
 block('PROJECT_REQUIREMENTS.md','## 当前玩家界面要求 · 2026-10-28\n\n最高优先五条要求继续有效。本批优先将零碎界面合并为本局、地图与节点、干员计算、资料查询、聊天五大栏目；开发校准不作为默认玩家入口。按用户提供录像核对：采用场景关联快捷入口、本局信息复用、图文藏品筛选、本地场景笔记与紧凑置顶小窗；不只更换栏目标题。视频回顾范围及385–390计划见verification/sections/385-video-review.json。个人笔记只留本机，不上传对局数据；按最新要求接入节点概率和公开联网统计，只读取、不上传本局；显示样本数、来源和适用条件；不推荐或自动选路，不复制未证的识别能力。只作局外查阅与后台只读采样，不代替玩家操作或规划。每节真实功能、必要验收、要求与索引同提交普通推送；至390完整收尾后暂停。\n\n'+body)
 block('PROJECT_COMPLETED.md',body)
 todo=R/'PROJECT_PROGRESS.md';text=todo.read_text('utf8');rows=read('verification/sections/385-video-review.json')['planned_functional_sections'];remaining='；'.join(rows[str(i)]for i in range(n+1,391))
 prefix='| 本批优先 | 玩家界面整合 |'
 text='\n'.join(line for line in text.splitlines()if not line.startswith(prefix))+'\n'
 if remaining:text=text.replace('| --- | --- | --- |','| --- | --- | --- |\n'+prefix+' '+remaining+' |',1)
 todo.write_text(text,encoding='utf8',newline='\n')
 runpy.run_path(str(R/'scripts/update_cloud_index.py'))['update'](R)
 _runner=R/f'verification/sections/{n}-player-execution/pipeline-source.py';_runner.parent.mkdir(parents=True,exist_ok=True);_runner.write_bytes(Path(__file__).read_bytes())
 staged=git('diff','--cached','--name-only').strip();assert not staged
 names=set(git('diff','--name-only').decode().splitlines())|set(git('ls-files','--others','--exclude-standard').decode().splitlines())
 docs={'AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','CLOUD_INDEX.json','CLOUD_HANDOFF.md','DEVELOPMENT_CHECKPOINT.json'}
 for name in names:assert name in docs or name=='verification/sections/385-video-review.json' or name.startswith(('research/public-statistics-388/','rouge/','scripts/','tests/',f'verification/sections/{n}')),name
 subprocess.run(['git','add','--',*sorted(names)],cwd=R,check=True)
 subprocess.run(['git','-c','core.whitespace=cr-at-eol,-blank-at-eof','diff','--cached','--check'],cwd=R,check=True)
 subprocess.run(['git','-c','gc.auto=0','commit','--quiet','-m',f'第{n}节：'+s['title']],cwd=R,check=True)
 publish(n,'functional')
def publish(n,phase):
 head=git('rev-parse','HEAD').decode().strip();assert git('branch','--show-current').decode().strip()=='codex/p2-development'
 out=f'verification/sections/{n}-publication-execution'if phase=='functional'else f'.cache/player{n}-metadata-publication'
 p=R/out
 if p.exists():
  base=out;attempt=2
  while(R/(base+f'/retry-{attempt}')).exists():attempt+=1
  out=base+f'/retry-{attempt}';p=R/out
 p.mkdir(parents=True)
 argv=['git','push','origin','HEAD:refs/heads/codex/p2-development']
 with(p/'stdout.txt').open('xb')as stdout,(p/'stderr.txt').open('xb')as stderr:
  child=subprocess.Popen(argv,cwd=R,stdout=stdout,stderr=stderr);code=child.wait()
 write(out+'/process.json',{'argv':argv,'actual_retained_Popen_pid':child.pid,'actual_observed_exit':code,'ordinary_push':True,'force_push':False})
 assert code==0,(p/'stderr.txt').read_text('utf8')
 assert git('ls-remote','origin','refs/heads/codex/p2-development').decode().split()[0]==head
 subprocess.run(['git','fetch','origin','codex/p2-development'],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 assert git('rev-parse','origin/codex/p2-development').decode().strip()==head
 names={v.decode('utf8')for v in git('diff-tree','--no-commit-id','--name-only','-r','-z',head).split(b'\0')if v}|set(source())
 tree={}
 for row in git('ls-tree','-rz',head).split(b'\0'):
  if row:
   meta,name=row.split(b'\t',1);tree[name.decode()]=meta.decode().split()
 proofs={}
 for name in sorted(names):
  assert not name.startswith(('.local/','.cache/'))and name!='local-settings.json'
  raw=(R/name).read_bytes();mode,kind,blob=tree[name]
  assert mode=='100644'and kind=='blob'and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,name
  proofs[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw),'git_blob_sha1':blob}
 report={'section':n,'passed':True,'branch':'codex/p2-development','commit':head,'local_HEAD':head,'remote_HEAD':head,
 'remote_branch':'origin/codex/p2-development','push_primary_exit':code,'ordinary_push':True,'force_push':False,
 'phase':phase,'verified_commit_tree_and_local_public_bytes':proofs,'private_state_included':False,'full_validation_rerun':n in(395,410,425),
 'last_full_is_historical_for_current_changes':n not in(395,410,425),'publication_itself_reexecuted_tests':False,'at_UTC':datetime.now(timezone.utc).isoformat()}
 write(out+'/remote-proof.json',report)
 if phase=='functional':write(f'verification/sections/{n}-publication.json',report)
 print(json.dumps({'phase':phase,'section':n,'actual_verified_remote_commit':head,'public_files_compared':len(proofs)},ensure_ascii=False),flush=True)
def metadata(n):
 proof=read(f'verification/sections/{n}-publication.json');cp=read('DEVELOPMENT_CHECKPOINT.json')
 assert git('rev-parse','HEAD').decode().strip()==proof['commit']and proof['passed']
 cp['last_verified_cloud_save']={'section':n,'scope':'current_functional_section','binding':'verified_remote_commit','commit':proof['commit'],'proof':f'verification/sections/{n}-publication.json','proof_sha256':pin(f'verification/sections/{n}-publication.json')['sha256']}
 paused=n==390;cp['batch_status']=f'PLAYER_SECTION{n}_PUBLISHED'+('_PAUSED'if paused else'')
 cp['current_batch'].update(status=cp['batch_status'],batch_closed=paused)
 cp['policy'].update(new_functional_sections_paused=paused,development_paused_by_latest_user_request=paused,current_user_batch_completed=paused)
 if paused:cp['policy']['paused_after_completed_section']=n
 cp['cloud_publication_closeout']={'section':n,'functional_commit':proof['commit'],'proof':f'verification/sections/{n}-publication.json','current_commit_kind':'publication metadata only','next_section_started':False,'development_paused':paused}
 cp['next_action']=('第390节完整发布后暂停，不启动391。'if paused else f'从第{n+1}节继续玩家界面整合至390。')+'P3/P2/P1未完成；识别最后；下次定期全量395。'
 write('DEVELOPMENT_CHECKPOINT.json',cp)
 for name in('AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','PROJECT_COMPLETED.md'):
  p=R/name;t=p.read_text('utf8');assert t.count('<!-- player-publication-pending -->普通推送与远端核对待完成。')==1
  p.write_text(t.replace('<!-- player-publication-pending -->普通推送与远端核对待完成。',f'本节功能提交{proof["commit"]}已普通推送并核对远端与{len(proof["verified_commit_tree_and_local_public_bytes"])}份公开文件。'+('本批已在390结束并暂停，391未启动。'if paused else f'本批继续至390，后续{n+1}尚未启动。')),encoding='utf8',newline='\n')
 runpy.run_path(str(R/'scripts/update_cloud_index.py'))['update'](R)
 names=['AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','PROJECT_COMPLETED.md','DEVELOPMENT_CHECKPOINT.json','CLOUD_INDEX.json','CLOUD_HANDOFF.md',f'verification/sections/{n}-publication.json',f'verification/sections/{n}-publication-execution']
 subprocess.run(['git','add','--',*names],cwd=R,check=True)
 subprocess.run(['git','-c','gc.auto=0','commit','--quiet','-m',f'同步第{n}节发布证明与项目索引'],cwd=R,check=True);publish(n,'metadata')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('phase',choices=('verify','close','metadata'));p.add_argument('section',type=int);a=p.parse_args()
 assert 381<=a.section<=390
 s=read(f'.cache/player-spec{a.section}.json');globals()[a.phase](a.section,s)if a.phase!='metadata'else metadata(a.section)
