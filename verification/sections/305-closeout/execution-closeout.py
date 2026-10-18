"""Root explicit local closeout only after actual complete305 and app review."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from datetime import datetime,timezone,timedelta
import argparse,json,re,runpy
ROOT=Path(__file__).resolve().parents[1]
DOCS=('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','AGENTS.md','PROJECT_REQUIREMENTS.md','PROJECT_PROGRESS.md','DEVELOPMENT_CHECKPOINT.json','CLOUD_INDEX.json','CLOUD_HANDOFF.md')
def load(name):return json.loads((ROOT/name).read_bytes())
def digest(raw):return sha256(raw).hexdigest()
def encode(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def pin(name):
 p=ROOT/name;return{'file':name,'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args();assert args.apply
 proposal=load('.cache/p3-305-closeout/actual-gated-proposal.json')
 assert proposal['kind']=='ROOT_REVIEW_ONLY_305_CLOSEOUT_PROPOSAL_NOT_APPLIED'
 for name,p in proposal['actual_bound_inputs'].items():assert digest((ROOT/name).read_bytes())==p['sha256'],name
 cp=load('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==304 and cp['next_section']==305
 assert cp['policy']['usage_wrap_up_triggered']is True and cp['policy']['usage_wrap_up_after_active_section']==305
 assert cp['policy']['wrap_up_below_usage_percent']==15
 n=load('verification/sections/305-necessary-readable/process.json');w=load('verification/sections/305-window-attempt2/actual/window.json')
 full=load('verification/full-305/summary.json')
 assert n['passed']and n['exit_code']==0 and n['methods_ran']==65
 assert w['passed']and w['unique_checks']==72 and w['qt_exit_code']==0
 assert full['available_checks_passed']is True and full['actual_validation_attempt']==2 and full['scope_not_reduced']is True
 for key in('source_sha256','supplemental_public_inputs_sha256'):
  for name,h in load(full['source_freeze'])[key].items():assert digest((ROOT/name).read_bytes())==h,name
 now=datetime.now(timezone(timedelta(hours=8))).isoformat()
 pending='<!-- section305-publication-pending -->当前为本地完整验收完成，普通推送与实际远端核对尚待完成。'
 details=(now+'。'+proposal['capability']+'\n\n实际65项必要检查、72个功能原生唯一检查通过；最终完整可用全量305通过，完整469选择器、旧52状态与原typed核对、原30及独立29、全部20项补充窗口范围保留。原30符号链接1314缺权限仍未通过；73项历史跳过、私有/原Windows及Linux/Wine、游戏和聊天不冒充通过。第一轮失败及修复来源另存，未覆盖原件。根代理查看本轮全部实际PNG，原项目测试窗口已更新可见响应，启动前后私人5路径不变。\n\n'+proposal['limits']+'\n\n用户2026-10-18已恢复严格低于15%的收尾阈值，并明确要求完整完成305后暂停；此前4%触发为历史记录。完成305普通发布核对后结束本批，306未启动，等待用户恢复；下次定期全量320。'+pending)
 receipt=deepcopy(proposal['receipt305_fields'])
 receipt.update(title=proposal['title'],at_Beijing=now,branch='codex/p2-development',prior_commit=proposal['prior_commit_declared_by_root'],remaining_item='P3节点事件与藏品交换资料',source_sha256=n['source_sha256_after'],validated_source_sha256=w['source_sha256_after'],files=sorted(set(n['source_sha256_after'])|set(w['source_sha256_after'])),P3_complete=False,P2_complete=False)
 receipt['necessary_validation'].update(receipt='verification/sections/305-necessary-readable/process.json',actual_exit=0,methods_run=65,source_unchanged=True)
 receipt['native_windows_validation'].update(receipt='verification/sections/305-window-attempt2/actual/window.json',unique_checks=72,actual_Qt_exit=0,actual_assertion_executions=w['successful_assertion_executions_including_repeated_guards'],actual_flow_readings=w['actual_flow_readings'])
 receipt['full_validation'].update(receipt='verification/full-305/summary.json',after_section=305,full_suite_rerun=True,scope_not_reduced=True,available_checks_passed=True,next_periodic_section=320)
 receipt['maintenance_validation']={'receipt':'verification/full-305/repairs-after-first/necessary/process.json','actual_exit':0,'methods_run':50,'native296_process':'verification/full-305/native296-maintenance-attempt1/process.json','native296_unique_checks':80,'first_failed_full_archive':'verification/full-305/execution-attempt1/archive-manifest.json','changes_count_as_additional_functional_section':False}
 staged={'verification/sections/305.json':encode(receipt)}
 texts={name:(ROOT/name).read_text('utf8')for name in DOCS if name.endswith('.md')}
 for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
  staged[name]=('## 功能第305节 · '+proposal['title']+'\n\n'+details+'\n\n以下保留历史记录；当前断点以上述305收尾为准。\n\n'+texts[name]).encode('utf8')
 agent=texts['AGENTS.md'];start=agent.index('## 当前续接 · 第304节');end=agent.index('\n## ',start+3)
 staged['AGENTS.md']=(agent[:start]+'## 当前续接 · 第305节完成完整可用验收，额度收尾中\n\n'+details+'\n'+agent[end:]).encode('utf8')
 req=texts['PROJECT_REQUIREMENTS.md'];start=req.index('<!-- current-delivery:start -->');end=req.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->')
 staged['PROJECT_REQUIREMENTS.md']=(req[:start]+'<!-- current-delivery:start -->\n## 当前交付与续接 · 第305节\n\n'+details+'\n<!-- current-delivery:end -->'+req[end:]).encode('utf8')
 progress=texts['PROJECT_PROGRESS.md'];progress=re.sub(r'最后更新：\s*2026-\d\d-\d\d','最后更新：'+now[:10],progress,count=1)
 staged['PROJECT_PROGRESS.md']=progress.encode('utf8')
 cp=deepcopy(cp)
 for key in proposal['preserve_under_historical_before305']:
  if key in cp:cp['historical_before305_'+key]=cp.pop(key)
 cp.update(deepcopy(proposal['checkpoint_top_level_overlay']))
 cp['current_section_save']['commit_reference']='enclosing functional305 snapshot; actual ordinary publication proof remains separately bound'
 cp['current_available_full_validation'].update(available_scope_passed=True,actual_validation_attempt=2,source_freeze=full['source_freeze'],source_freeze_sha256=full['source_freeze_sha256'],native_windows_game_chat_verified=False)
 for dotted,value in proposal['checkpoint_nested_edits'].items():
  if dotted=='policy.development_paused_by_latest_user_request':continue
  parent,key=dotted.split('.',1);cp[parent][key]=value
 cp['current_batch']['completed_sections']=305
 assert not any(x['number']==305 for x in cp['sections']);cp['sections'].append(proposal['append_exactly_once']['sections'])
 assert 305 not in cp['functional_sections_since_latest_requirement'];cp['functional_sections_since_latest_requirement'].append(305)
 staged['DEVELOPMENT_CHECKPOINT.json']=encode(cp)
 handoff=texts['CLOUD_HANDOFF.md'];start=handoff.index('<!-- live-cloud-index:start -->');end=handoff.index('<!-- live-cloud-index:end -->')+len('<!-- live-cloud-index:end -->')
 staged['CLOUD_HANDOFF.md']=(handoff[:start]+'<!-- live-cloud-index:start -->\n# 当前云端续接索引 · 第305节\n\n'+details+'\n<!-- live-cloud-index:end -->\n\n<!-- section305-handoff:start -->\n## 当前第305节验收与额度收尾\n\n'+details+'\n<!-- section305-handoff:end -->'+handoff[end:]).encode('utf8')
 index=load('CLOUD_INDEX.json');index.update(completed_sections=305,next_section=306,batch_status=cp['batch_status'],sections=cp['sections']);index['requirements']['sha256']=digest(staged['PROJECT_REQUIREMENTS.md']);staged['CLOUD_INDEX.json']=encode(index)
 out=ROOT/'verification/sections/305-closeout';assert not out.exists();out.mkdir()
 before={name:(ROOT/name).read_bytes()if(ROOT/name).exists()else None for name in staged}
 backup=ROOT/'.cache/p3-305-closeout/before-root-apply';assert not backup.exists();backup.mkdir()
 for name,raw in before.items():
  if raw is not None:
   p=backup/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 try:
  for name,raw in staged.items():(ROOT/name).write_bytes(raw)
  runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
 except BaseException:
  for name,raw in before.items():
   if raw is None:(ROOT/name).unlink(missing_ok=True)
   else:(ROOT/name).write_bytes(raw)
  raise
 (out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes())
 report={'section':305,'actual_local_closeout_applied':True,'at_Beijing':now,'outputs':{name:pin(name)for name in staged},'actual_cloud_publication_verified':False,'usage_wrap_up_triggered':True,'next306_started':False,'next_full_validation_after':320,'private_state_read_copied_or_restored':False}
 (out/'apply.json').write_bytes(encode(report));print(json.dumps({'local305_accepted':True,'outputs':len(staged),'next306_started':False,'publication_pending':True},ensure_ascii=False))
if __name__=='__main__':main()
