from pathlib import Path
from hashlib import sha256
import json,difflib,runpy
R=Path.cwd();B=R/'verification/maintenance/compact-battle-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,value):(R/n).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,value):
 p=R/n;old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=value.splitlines(keepends=True);out=list(new)
 for a,b,num in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in old],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():
  for i in range(num):out[b+i]=old[a+i]
 p.write_bytes(''.join(out).encode('utf8'))
rows=[]
names=['verify_current_battle_window_314.py','verify_current_rewards_window_315.py','verify_current_settlement_window_318.py','verify_current_settlement_modes_window_362.py']
for name,count in zip(names,[24,29,30,51]):
 tag=name.rsplit('_',1)[-1][:-3];folder=prefix+'maintained-native-current/'+tag+'/'
 receipt=read(folder+'window.json');assert receipt['passed']and receipt['unique_checks']==count and receipt['qt_exit_code']==0 and receipt['verification_window_closed']
 assert receipt['source_sha256_before']==receipt['source_sha256_after']and not any(receipt['external_operation_attempts'].values())
 assert not receipt['private_contents_read_copied_or_restored']and not receipt['game_operated']and not receipt['chat_sent']
 assert read(folder+'process.json')['actual_observed_exit']==0
 assert read(prefix+'maintained-native/'+tag+'/process.json')['actual_observed_exit']==1
 (R/folder/'verifier-source.py').write_bytes((R/'scripts'/name).read_bytes())
 rows.append({'script':pin('scripts/'+name),'receipt':pin(folder+'window.json'),'unique_checks_within_this_gate':count,'not_summed_with_other_gates':True,'raw_initial_failure':pin(prefix+'maintained-native/'+tag+'/window.json')})
assert read(prefix+'maintained-native-current/process-summary.json')['all_actual_exits_zero']
source=read(prefix+'source-review.json');source['maintained_verification_sources']=[pin('scripts/'+n)for n in names]+[pin('scripts/native_workspace_navigation.py')];source['maintained_verification_scope']={'current_gates':rows,'original_prechange_verifiers':'research/compact-battle-review-20261031/before-native-scripts/','first_adapted_failing_versions':prefix+'maintained-native/first-adapted-source/','failure_cause':'All four first adapted runs still assumed one-level MainWindow tabs. PlayerWorkspace has real group and reader tabs; old indexOf(inner reader)=-1 clicked the first group. New shared native helper clicks both real levels and requires exact visible reader. No product code modified to satisfy this legacy assumption.','other_updates':'314 uses explicit raw-source control; 315 uses visible shared parent refresh; 318/362 open both grouped reward layers and 318 uses visible shared parent refresh. Original quantity/conditions/typed source/source-loss cases retained.','full_engineering_validation_claimed':False};write(prefix+'source-review.json',source)
summary=read(prefix+'summary.json');summary['source_review']=pin(prefix+'source-review.json');summary['additional_maintained_native_gates']=rows;summary['all_four_actual_exits_zero']=True;write(prefix+'summary.json',summary)
image=read(prefix+'image-review.json');image['additional_maintained_native_screenshots']='Retained unchanged as recorded interaction artifacts; not all newly inspected for appearance and not added to the seven actually reviewed final player originals.';write(prefix+'image-review.json',image)
summary['image_review']=pin(prefix+'image-review.json');write(prefix+'summary.json',summary)
paragraph='\n同批维护314/315/318/362四份当前原生验收入口：完整保留数值、非零滚动/选择、准确来源和损坏/恢复场景。首轮均被更早遗留的单层主窗口导航阻挡，原失败及当时脚本保留；新增共享真实两层导航，改用合并奖励入口、显式原始资料及可见父刷新按钮。四份最终实际退出0，分别24/29/30/51项唯一检查，交叠范围不相加，也不冒称全工程整轮通过。附加截图仅保留为交互原件，未全部新做外观审阅。\n'
n='research/compact-battle-review-20261031/README.md';t=(R/n).read_text('utf8');assert '同批维护314/315/318/362'not in t;text(n,t+paragraph)
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:
 t=(R/n).read_text('utf8');marker='<!-- compact-battle-review-20261031:end -->';assert t.count(marker)==1;text(n,t.replace(marker,paragraph.strip()+'\n'+marker,1))
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');text(n,t+'\n本批四份保留原生入口已同步两层主导航和新的作战资料分组，24/29/30/51项独立范围分别真实退出0；首轮单层导航失败原件保留，不累计成全工程通过。其余历史入口和全工程当前源码整轮仍需核对。\n')
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']['review_checklist_sha256']=pin('PROGRAM_REVIEW.md')['sha256'];text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
audit=read(prefix+'final-audit.json');audit['summary']=pin(prefix+'summary.json');audit['cloud_index']=pin('CLOUD_INDEX.json');audit['additional_maintained_native_gates_passed']=True;write(prefix+'final-audit.json',audit)
(B/'native-compatibility-finalization-source.py').write_bytes(Path(__file__).read_bytes())
archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive});print(json.dumps({'passed':True,'current_native_gates':[r['unique_checks_within_this_gate']for r in rows],'archive_files':len(archive),'full_validation_claimed':False}))
