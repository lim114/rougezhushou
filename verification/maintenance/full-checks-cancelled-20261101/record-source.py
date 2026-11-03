from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
import json,subprocess,runpy,difflib
R=Path.cwd();B=R/'verification/maintenance/full-checks-cancelled-20261101';B.mkdir(exist_ok=False)
BASE='ce7b27f044f7e92c70717663f217c5aca5996dcb'
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
def save(p,text):
 p=R/p;a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=text.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in a],[v.rstrip('\r\n')for v in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
 p.write_bytes(''.join(b).encode('utf8'))
cp=json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_bytes());assert cp['completed_sections']==449 and cp['next_section']==450
old={'root_next_full':cp['next_full_validation_after'],'policy':{k:v for k,v in cp['policy'].items()if k in ('full_validation_interval','full_validation_anchor_section','next_full_validation_after','cloud_save_destination','validation_per_section','repair_full_validation_after_functional_260')},'batch_commit_policy':{k:v for k,v in cp['current_batch_commit_policy'].items()if 'full' in k},'batch_next_full':cp['current_batch']['next_full_validation_after']}
(B/'former-schedule-history.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n','utf8')
cp['next_full_validation_after']=None;cp['full_validation_due']=False
cp['policy'].update(full_validation_mode='disabled_by_user',full_validation_interval=None,full_validation_anchor_section=None,next_full_validation_after=None,full_validation_restore_requires_explicit_user_request=True,cloud_save_destination='Every completed section:commit and ordinary push origin codex/p2-development.Full checks cancelled until explicit user request.',validation_per_section='Only necessary targeted checks tied to current changes;no automatic full suite.',repair_full_validation_after_functional_260=False)
cp['current_batch_commit_policy'].update(full_validation_interval=None,next_full_validation_after=None)
cp['current_batch']['next_full_validation_after']=None
cp['next_action']=cp['next_action'].replace('后续450，下次完整455。','后续450；所有原定全量检查已取消，用户明确要求前不得恢复。')
cp['current_maintenance_save']={'title':'按用户要求取消全部预定全量检查','receipt':'verification/maintenance/full-checks-cancelled-20261101/summary.json','binding':'enclosing_commit','functional_section_added':False}
cp['full_checks_cancellation']={'user_instruction':'取消所有原定的全量检查，在我没有明确说明之前不恢复全量检查机制','after_completed_section':449,'historical_schedule':'verification/maintenance/full-checks-cancelled-20261101/former-schedule-history.json','restoration_requires_explicit_user_request':True,'targeted_checks_retained':True}
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
note='## 当前执行规则：全量检查已取消\n\n用户最新明确要求：取消所有原定的全量检查，在用户明确说明之前不恢复全量检查机制。原第455节及每15节安排均取消，未来不按节数、批次收尾或历史要求自动启动全量；仅运行当前改动所需定向检查。旧验收、失败和冻结资料保留为历史，不构成待执行安排。功能进度仍449，后续450；本次为执行规则维护，不新增功能节数。\n\n'
save('WORK_IN_PROGRESS.md',note+(R/'WORK_IN_PROGRESS.md').read_text('utf8'))
p='PROJECT_REQUIREMENTS.md';s=(R/p).read_text('utf8');s=s.replace('当前功能第447节','当前功能第449节',1).replace('下一完整范围455。','全量检查已按用户最新要求取消，明确要求前不恢复。',1);lines=s.splitlines(keepends=True);lines.insert(2,'\n'+note);s=''.join(lines);s=s.replace('- 定期全量仍每15节：本批215、230、245及最终260；检查范围保持。每节仅作改动相关必要检查，不重复已通过且未变的检查；全量范围不缩减。','- 历史规则（现已取消）：曾安排每15节的定期全量及批次最终全量；当前执行以上方“全量检查已取消”为准。旧范围和验收记录保留，不自动重跑。');save(p,s)
p='PROJECT_PROGRESS.md';s=(R/p).read_text('utf8');s=s.replace('## 功能节要求','## 当前检查安排\n\n所有原定全量与每15节周期均已取消，包含原第455节安排；只有用户明确要求后才可恢复。当前改动所需的定向检查保留。\n\n## 功能节要求',1);save(p,s)
p='PROJECT_COMPLETED.md';save(p,'## 执行规则维护：取消预定全量检查\n\n按用户最新指示清除全部当前全量到期节、周期及锚点，云端续接显示取消状态；恢复必须由用户明确要求。旧验收记录保留，功能仍449，不新增功能节数。\n\n'+(R/p).read_text('utf8'))
(B/'summary.json').write_text(json.dumps({'kind':'user_requested_execution_policy_maintenance','section':449,'functional_section_added':False,'next_section':450,'user_instruction':cp['full_checks_cancellation']['user_instruction'],'cancelled_due_section':455,'cancelled_interval':15,'all_four_active_due_pointers_null':all(v is None for v in (cp['next_full_validation_after'],cp['policy']['next_full_validation_after'],cp['current_batch_commit_policy']['next_full_validation_after'],cp['current_batch']['next_full_validation_after'])),'full_check_process_detected':False,'codex_automation_tomls_found':0,'targeted_checks_retained':True,'historical_full_receipts_changed':False,'full_check_executed':False,'product_code_or_private_state_changed':False,'test_window_restart_required':False,'verification_pending':'Only cloud-index policy tests;not full suite.','at_UTC':datetime.now(timezone.utc).isoformat()},ensure_ascii=False,indent=2)+'\n','utf8')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);idx['validate_delivery'](R,cp)
assert '全量检查机制已取消；仅在用户明确要求后恢复。'in(R/'CLOUD_HANDOFF.md').read_text('utf8').split('<!-- live-cloud-index:end -->')[0]
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());print('Cancelled scheduled full checks;functional section remains449,next450;no full suite run.')
