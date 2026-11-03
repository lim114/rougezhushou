"""Archive only actual completed same-source rechecks and root observed exits."""
from pathlib import Path
from hashlib import sha256
import json,sys
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.cache/full320-attempt2-prep';HERE=ROOT/'.cache/full320-recheck298';sys.path.insert(0,str(BASE))
from full320_common import bound,sha,now,write_new,PYTHON
from review_results320 import terminal
PARENT='e320b50d43f713c50941a29ffc1e89c2311761dc';FROZEN='954012182a0f700e504ae4349f8b5847b4ab2ced6bb2ab5bce3abec3ee98cb51';ACT='796d46e88869e1854e938d61a8ff8d7ec1bb80ff8b64b23b186d4b7be3bbe596'
def read(p):return json.loads(p.read_bytes())
def main():
 data,_=bound(PARENT,FROZEN,ACT);proc=read(HERE/'root-launch/controller-process.json');assert proc['status']=='completed'and type(proc['actual_observed_exit'])is int and proc['exit_observed_directly_from_retained_popen']and proc['exit_inferred_from_output_json']is False
 assert int((HERE/'root-launch/process.exit').read_text())==proc['actual_observed_exit']
 for n,h in read(HERE/'root-launch/source-pins.json').items():assert sha(HERE/n)==h
 namespace=Path(read(HERE/'once.json')['actual_namespace']);observed=read(namespace/'recheck-observed.json');assert[x['name']for x in observed['steps']]==['p3_298','p3_311','p3_312']
 shared=['--expected-parent-commit',PARENT,'--freeze-sha256',FROZEN,'--activation-sha256',ACT]
 for row in observed['steps']:
  n=row['name'];child=[str(PYTHON),'-B','-X','utf8',str(HERE/'component_child320_recheck.py'),'--mode',n,'--out',str(namespace/n/'actual'),*shared];terminal(namespace/n,child,success=False)
 out=ROOT/'verification/full-320/rechecks-source-freeze2-1';assert not out.exists();out.mkdir();files={}
 def copy(p,name,role):
  assert p.is_file()and not p.is_symlink()and not Path(name).is_absolute()and'..'not in Path(name).parts
  target=out/name;assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);raw=p.read_bytes();target.write_bytes(raw);assert sha(p)==sha(target);files[name]={'sha256':sha(p),'bytes':len(raw),'role':role}
 for name in('owned-execution.json','recheck-observed.json','p3_298-recheck-observed.json','p3_311-recheck-observed.json','p3_312-recheck-observed.json'):copy(namespace/name,name,'actual original observations')
 for name in('controller-process.json','stdout.txt','stderr.txt','process.exit','source-pins.json'):copy(HERE/'root-launch'/name,'root-launch/'+name,'actual root retained Popen and source pins')
 for name in('controller.py','component_child320_recheck.py','preparation.json','once.json'):copy(HERE/name,'execution-tools/'+name,'exact executed tools or original preparation')
 copy(ROOT/'.cache/run_owned_recheck320.py','root-launch/execution-root-wrapper.py','actual retained root Popen source');copy(Path(__file__),'execution-archive.py','exact archive consumer')
 for row in observed['steps']:
  n=row['name'];folder=namespace/n
  for p in sorted(folder.iterdir()):
   if p.is_file():copy(p,n+'/'+p.name,'actual assigned-job supervisor and retained process original')
  for p in sorted((folder/'actual').iterdir()):
   if p.is_file()and p.suffix in('.json','.png'):copy(p,n+'/actual/'+p.name,'flat public isolated fixture output; no private or clone traversal')
 bound(PARENT,FROZEN,ACT)
 report={'section':320,'kind':'EXACT_SAME_FROZEN_SOURCES_THREE_CANONICAL_RECHECKS','source_freeze_sha256':FROZEN,'activation_sha256':ACT,'parent_commit':PARENT,'modes':['p3_298','p3_311','p3_312'],'all_original_40_components_preserved':'verification/full-320/execution-attempt2/archive-manifest.json','actual_root_controller_exit':proc['actual_observed_exit'],'every_retained_Popen_and_assigned_job_terminal':True,'canonical_or_product_sources_changed':False,'all_recheck_actual_child_and_supervisor_exit0':observed['all_primary_and_supervisor_exit0'],'311_profiling_visible_ms':300000,'311_original_120s_timeout_remains_a_failure':True,'311_profile_is_not_a_performance_PASS':True,'298_312_original_argparse_default_visible_ms':120000,'full_suite_rerun':False,'files':files,'sealed_at':now(),'private_contents_copied':False,'PNG_appearance_review_claimed':False};write_new(out/'archive-manifest.json',report);print(json.dumps({'archive':str(out),'all3_actual0':report['all_recheck_actual_child_and_supervisor_exit0'],'files':len(files)}))
if __name__=='__main__':main()
