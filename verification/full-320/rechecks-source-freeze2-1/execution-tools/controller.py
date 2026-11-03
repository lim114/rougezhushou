"""One owned recheck, only after full320 attempt2 terminal; original120s TTL."""
from pathlib import Path
import sys,json,uuid,tempfile,ast,os
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'.cache/full320-attempt2-prep';HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from full320_common import bound,sha,write_new,now,PYTHON
from run_full320_controller import observed_step
PARENT='e320b50d43f713c50941a29ffc1e89c2311761dc';FROZEN='954012182a0f700e504ae4349f8b5847b4ab2ced6bb2ab5bce3abec3ee98cb51';ACT='796d46e88869e1854e938d61a8ff8d7ec1bb80ff8b64b23b186d4b7be3bbe596'
def read(p):return json.loads(p.read_bytes())
def main():
 data,_=bound(PARENT,FROZEN,ACT)
 root_process=read(BASE/'root-launch/controller-process.json');assert root_process['status']=='completed'and type(root_process['actual_observed_exit'])is int and root_process['exit_observed_directly_from_retained_popen']
 full=Path(read(BASE/'full320-once.json')['container']);control=read(full/'orchestration.json');assert control['status']=='all_required_components_terminal'and len(control['steps'])==40 and all(r['status']=='terminal'and r['owned_job_no_live_execution_verified']for r in control['steps'])
 failed={r['name']for r in control['steps']if r['child_primary_exit']!=0};assert failed=={'current30','p3_298','p3_311','p3_312'}
 prior=read(full/'p3_298/actual/window.json');assert prior['passed']is False and prior['failure']=={'type':'TimeoutError','message':'Natural-main-floor checks incomplete.'}
 target=ROOT/data['p3_scripts']['p3_298'];assert sha(target)==data['source_sha256'][data['p3_scripts']['p3_298']]
 calls=[n for n in ast.walk(ast.parse(target.read_bytes()))if isinstance(n,ast.Call)and any(isinstance(a,ast.Constant)and a.value=='--visible-ms'for a in n.args)]
 assert len(calls)==1 and next(k.value.value for k in calls[0].keywords if k.arg=='default')==120000
 namespace=Path(tempfile.gettempdir())/('rouge-full320-recheck298-'+uuid.uuid4().hex);assert not namespace.exists();write_new(HERE/'once.json',{'actual_namespace':str(namespace),'original_canonical_default_visible_ms':120000,'only_after_full40_terminal':True,'recheck_modes':['p3_298','p3_311','p3_312'],'311_profiler_visible_ms':300000,'311_longer_timing_diagnosis_not_original_deadline':True,'automatic_retry_allowed':False});namespace.mkdir()
 write_new(namespace/'owned-execution.json',{'section':320,'kind':'EXACT_CANONICAL298_311_312_SAME_SOURCE_RECHECKS_WITH_311_TIMING_DIAGNOSIS','controller_fixture_pid':os.getpid(),'parent_commit':PARENT,'source_freeze_sha256':FROZEN,'activation_sha256':ACT,'canonical_target':data['p3_scripts']['p3_298'],'canonical_sha256':sha(target),'complete40_original_execution_retained':str(full),'source_unchanged':True,'root_started_at':now()})
 shared=['--expected-parent-commit',PARENT,'--freeze-sha256',FROZEN,'--activation-sha256',ACT]
 child=[str(PYTHON),'-B','-X','utf8',str(HERE/'component_child320_recheck.py'),'--mode','p3_298','--out',str(namespace/'p3_298/actual'),*shared]
 rows=[]
 for mode in ('p3_298','p3_311','p3_312'):
  target=ROOT/data['p3_scripts'][mode];assert sha(target)==data['source_sha256'][data['p3_scripts'][mode]]
  command=[str(PYTHON),'-B','-X','utf8',str(HERE/'component_child320_recheck.py'),'--mode',mode,'--out',str(namespace/mode/'actual'),*shared]
  row=observed_step(namespace,mode,command,1200,1290,PARENT,FROZEN,ACT);rows.append(row)
  write_new(namespace/(mode+'-recheck-observed.json'),row)
 write_new(namespace/'recheck-observed.json',{'steps':rows,'all_primary_and_supervisor_exit0':all(v['child_primary_exit']==v['supervisor_exit']==0 for v in rows)})
 bound(PARENT,FROZEN,ACT)
 print(json.dumps({'actual_namespace':str(namespace),'steps':[{k:v[k] for k in ('name','child_primary_exit','supervisor_exit')} for v in rows],'canonical_source_not_edited':True}),flush=True)
 return 0 if all(v['child_primary_exit']==v['supervisor_exit']==0 for v in rows) else 1
if __name__=='__main__':raise SystemExit(main())
