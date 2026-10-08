"""External-only one-line boolean observation exclusion over source-frozen bytes."""
import ast,difflib,hashlib,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent;REPO=Path('/workspace/rougezhushou')
SOURCE=Path('/workspace/.continuation/p2-crew-count-boolean-089-source')
BASE='1ce970fd30aa3b42d8ef787cde02513f05682b66'
def sha(d):return hashlib.sha256(d).hexdigest()
def bind(p):
 d=p.read_bytes();return {'source_path':str(p),'bytes':len(d),'sha256':sha(d)}
def write(name,value):
 p=OUT/name
 with p.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
 return p
def main():
 mf=SOURCE/'public-manifest.json';assert sha(mf.read_bytes())=='adf1b2a619cadea7c747669e9bb2f9c710c5d12ce83de48a63afcc992b3b7aca'
 old=(SOURCE/'frozen/rouge/run_state.py').read_bytes()
 transported=subprocess.check_output(['git','-C',str(REPO),'show',BASE+':rouge/run_state.py'])
 assert old==transported==(REPO/'rouge/run_state.py').read_bytes()
 needle=b"        crew=observed.get('crew_count')\r\n";assert old.count(needle)==1
 new=old.replace(needle,needle+b'        if isinstance(crew,bool):crew=None\r\n',1)
 assert b'\n' not in new.replace(b'\r\n',b'');ast.parse(new.decode())
 for side,data in (('baseline',old),('draft',new)):
  p=OUT/side/'rouge/run_state.py';p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(data)
 test=OUT/'draft/tests/test_run_crew_count_boolean_input.py';test_data=test.read_bytes();assert b'\r\n' not in test_data
 test_tree=ast.parse(test_data.decode());methods=[n.name for n in ast.walk(test_tree) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
 assert len(methods)==7
 product_diff=''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='a/rouge/run_state.py',tofile='b/rouge/run_state.py'))
 test_diff=''.join(difflib.unified_diff([],test_data.decode().splitlines(True),fromfile='/dev/null',tofile='b/tests/test_run_crew_count_boolean_input.py'))
 patch=OUT/'section89.patch'
 with patch.open('xb') as f:f.write((product_diff+test_diff).encode())
 registry=subprocess.check_output(['git','-C',str(REPO),'show',BASE+':scripts/verify_cloud.py'])
 assert registry==(REPO/'scripts/verify_cloud.py').read_bytes()
 module='tests.test_run_crew_count_boolean_input';token=b'MODULES = (\n';assert registry.count(token)==1 and module.encode() not in registry
 inserted=registry.replace(token,token+b'    "'+module.encode()+b'",\n',1)
 registry_path=OUT/'registry-proposal.patch'
 with registry_path.open('xb') as f:f.write(''.join(difflib.unified_diff(registry.decode().splitlines(True),inserted.decode().splitlines(True),fromfile='a/scripts/verify_cloud.py',tofile='b/scripts/verify_cloud.py')).encode())
 write('registry-proposal.json',{'base_commit':BASE,'module':module,'change':'Single module literal insertion at MODULES start; root adapts insertion to later88registry after a static transport check.',
   'base_sha256':sha(registry),'proposed_sha256':sha(inserted),'patch':bind(registry_path),'tracked_apply_owner':'root'})
 checked=subprocess.run(['git','-C',str(REPO),'apply','--check',str(patch)],capture_output=True,text=True)
 assert checked.returncode==0,checked.stderr
 receipt=write('draft-freeze089.json',{'status':'FROZEN_EXTERNAL_DRAFT_BUDGET_APPROVED','source_base_commit':'0f27027e7e1f49c08f298706b599e310e299238b',
   'transport_root_commit':BASE,'source38_manifest':bind(mf),'source_run_state_old_sha256':sha(old),
   'files':[bind(OUT/'draft/rouge/run_state.py'),bind(test)],'product_added_line':'if isinstance(crew,bool):crew=None',
   'inverse_exact_source38_old_bytes':new.replace(b'        if isinstance(crew,bool):crew=None\r\n',b'',1)==old,
   'section_patch':bind(patch),'registry_proposal':bind(OUT/'registry-proposal.json'),'new_test_methods':methods,
   'approved_author_budget':{'new_scenario_groups':12,'constructors_new':12,'constructors_reload':2,'seed_apply':12,'subject_apply':12,'actual_apply_entries':24},
   'product_runtime_not_yet_executed':True,'git_apply_check_returncode':checked.returncode,'git_apply_check_stdout':checked.stdout,'git_apply_check_stderr':checked.stderr,
   'damage_app_training_formatter_Qt_Wine':0,'old5_source_repro_repeated':False,'tracked_edits':0})
 print(json.dumps({'status':'FROZEN_EXTERNAL_DRAFT_BUDGET_APPROVED','freeze':bind(receipt),'patch':bind(patch),'new_tests':7,'product_added_lines':1,'project_calls':0}))
if __name__=='__main__':main()
