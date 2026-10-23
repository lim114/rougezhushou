from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];B=R/'.cache/full350-312-recheck'
sys.path.insert(0,str(R/'.cache/full350-attempt2'))
from full350_common import bound,sha
from review_results350 import terminal,closure,source_stable
def read(p):return json.loads(p.read_bytes())
P=read(B/'profile.json');freeze,activation=bound(P['parent_commit'],P['root_freeze_sha256'],P['activation_sha256'])
root=read(B/'root-launch/controller-process.json');C=Path(read(B/'once.json')['container'])
assert root['status']=='completed'and root['actual_observed_exit']==0 and root['owned_popen_retained']and root['exit_observed_directly_from_retained_popen']
assert int((B/'root-launch/process.exit').read_text())==0 and sha(B/'run.py')==root['runner_sha256_at_launch']
assert sha(B/'profile.json')==root['profile_sha256']
argv=[str(R/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(B/'component_child350_recheck.py'),'--mode','p3_312','--out',str(C/'p3_312/actual'),'--expected-parent-commit',P['parent_commit'],'--freeze-sha256',P['root_freeze_sha256'],'--activation-sha256',P['activation_sha256']]
terminal(C/'p3_312',argv)
target=R/'scripts/verify_gold_boss_window_312.py'
w,c=closure(C/'p3_312','p3_312',P['root_freeze_sha256'],P['activation_sha256'],target,[str(target),'--receipt',str(C/'p3_312/actual/window.json'),'--visible-ms','120000'])
expected={n:{**freeze['source_sha256'],**freeze['supplemental_public_inputs_sha256']}[n]for n in freeze['p3_script_selected_paths']['p3_312']}
source_stable(w,expected)
assert w['unique_checks']==31 and len(w['actual_topic_readings'])==12 and len(w['same_identity_refresh_observations'])==6 and w['verification_window_closed']
assert all(v==0 for v in w['external_operation_attempts'].values())
out=R/'verification/full-350/recheck-p3-312-default';assert not out.exists();out.mkdir();files={}
def copy(p,n):
 assert p.is_file()and not p.is_symlink();q=out/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());assert sha(q)==sha(p)
 files[n]={'sha256':sha(p),'bytes':p.stat().st_size}
for n in ('profile.json','once.json','run.py','component_child350_recheck.py'):copy(B/n,n)
for p in sorted((B/'root-launch').iterdir()):
 if p.is_file():copy(p,'root-launch/'+p.name)
for n in ('authority.json','result.json'):copy(C/n,n)
for p in sorted((C/'p3_312').iterdir()):
 if p.is_file():copy(p,'p3_312/'+p.name)
for p in sorted((C/'p3_312/actual').iterdir()):
 if p.is_file()and p.suffix in ('.json','.png'):copy(p,'p3_312/actual/'+p.name)
copy(Path(__file__),'execution-archive.py')
manifest={'section':350,'component':'p3_312','files':files,'root_freeze_sha256':P['root_freeze_sha256'],'all_actual_retained_execution_terminal':True,'root_actual_exit':0,'full_suite_rerun':False,'original60s_pass_claimed':False,'private_directories_copied':False}
(out/'archive-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ref(n):return{'path':(out/n).relative_to(R).as_posix(),'sha256':sha(out/n)}
receipt={'section':350,'passed':True,'root_freeze_sha256':P['root_freeze_sha256'],'profile':ref('profile.json'),'window':ref('p3_312/actual/window.json'),'closure':ref('p3_312/actual/full350-source-closure.json'),'step':ref('p3_312/step.json'),'root_process':ref('root-launch/controller-process.json'),'archive_manifest':ref('archive-manifest.json'),'source_unchanged':True,'original60s_pass_claimed':False,'normal_latency_improvement_claimed':False,'unique_checks':31,'topics':12,'refreshes':6,'full_suite_rerun':False}
(out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bound(P['parent_commit'],P['root_freeze_sha256'],P['activation_sha256'])
print(json.dumps(receipt,ensure_ascii=False))
