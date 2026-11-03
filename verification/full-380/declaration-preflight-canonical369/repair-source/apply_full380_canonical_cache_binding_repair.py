"""Root-only guarded unexecuted capsule repair. No tests, Qt, Git or public writes."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,ast,json,shutil
R=Path(__file__).resolve().parents[1];B=R/'.cache/full380-prepared';D=R/'.cache/full380-canonical-cache-binding-repair';A=B/'attempt-1'
def require(v,m):
 if not v:raise ValueError(m)
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def fingerprint(raw):return{'bytes':len(raw),'sha256':sha256(raw).hexdigest()}
def pin(p):return fingerprint(p.read_bytes())
def regular(p,base=R):
 require(p.is_file()and not p.is_symlink()and p.resolve().is_relative_to(base.resolve()),'Exact regular input required: '+str(p))
 for parent in p.parents:
  if parent==base:break
  require(not parent.is_symlink(),'Linked input parent refused: '+str(p))
 return p
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');p.add_argument('--plan-sha256',required=True);p.add_argument('--preflight-evidence-dir',type=Path,required=True);p.add_argument('--observation-sha256',required=True);args=p.parse_args()
 plan_path=regular(D/'plan.json');require(pin(plan_path)['sha256']==args.plan_sha256,'Reviewed exact plan drift')
 plan=json.loads(plan_path.read_bytes())
 require(plan['kind']=='CACHE_ONLY_CANONICAL369_PREFREEZE_REPAIR_PLAN_NOT_APPLIED_NOT_FULL_EXECUTION','Reviewed prefreeze plan only')
 require(plan['existing_unexecuted_capsule']=='attempt-1'and len(plan['bindings'])==5 and len(plan['new_public_files'])==3,'Exact five/three reviewed scope required')
 require(A.is_dir()and not A.is_symlink(),'Original unexecuted capsule1 required')
 for name in('activation380.json','root-launch','full380-once.json','bound-legacy','bound-current'):
  require(not(A/name).exists(),'Refuse repair after activation/execution/bound files: '+name)
 public_full=R/'verification/full-380'
 require(not any(public_full.glob('source-freeze-attempt*.json'))and not any(public_full.glob('execution-attempt*'))and not(public_full/'summary.json').exists(),'No freeze, full execution archive or summary may exist')
 require(pin(regular(B/'PREPARED_READY380.json'))==plan['expected_prepared_READY'],'Prepared READY changed')
 require(pin(regular(A/'CONTROLLER_READY380.json'))==plan['expected_capsule_READY'],'Original capsule READY changed')
 require(pin(regular(A/'capsule380.json'))==plan['expected_capsule_descriptor'],'Original capsule descriptor changed')
 ready=json.loads((B/'PREPARED_READY380.json').read_bytes());control=json.loads((A/'CONTROLLER_READY380.json').read_bytes());capsule=json.loads((A/'capsule380.json').read_bytes())
 require(capsule['section']==380 and capsule['attempt']==1 and capsule['root_source_finalized']is False and capsule['execution_started']is False,'Original prefreeze capsule descriptor required')
 require(capsule['prepared_plan_sha256']==plan['expected_prepared_READY']['sha256'],'Original descriptor READY binding differs')
 for name,pn in ready['files'].items():require(pin(regular(B/name,B))==pn,'Original prepared file drift: '+name)
 for name,pn in control['files'].items():require(pin(regular(A/name,A))==pn,'Original capsule file drift: '+name)
 require(len([n for n in ready['files']if n.startswith(('template-legacy/','template-current/'))])==102,'All exact102 original templates required')
 review=plan['source_review'];review_path=regular(R/review['path']);require(pin(review_path)=={'bytes':review['bytes'],'sha256':review['sha256']},'Exact source review changed')
 evidence=args.preflight_evidence_dir
 if not evidence.is_absolute():evidence=R/evidence
 require(evidence.is_dir()and not evidence.is_symlink()and evidence.resolve().is_relative_to((R/'.cache').resolve()),'Explicit cache-only root observed-evidence directory required')
 observed=regular(evidence/'observed-terminal.json',evidence)
 require(pin(observed)['sha256']==args.observation_sha256,'Actual root observed terminal record differs')
 observed_json=json.loads(observed.read_bytes())
 require(observed_json.get('raw_complete_terminal_trace_file_available')is False,'Do not claim or reconstruct a missing full terminal trace')
 evidence_files=[]
 for file in evidence.iterdir():
  require(file.is_file()and not file.is_symlink()and file.suffix in('.json','.txt'),'Only explicit flat public observed-evidence files may be preserved')
  evidence_files.append(regular(file,evidence))
 for row in plan['bindings']:
  require(row['mode']=='p3_369'and row['canonical_script']=='scripts/verify_current_boss_documents_window_369.py','Canonical369-only binding required')
  require(row['local_path'].startswith('.cache/game-data/levels/')and row['public_path'].startswith(('research/','verification/full-380/explicit-public-build-inputs/')),'Exact reviewed public source names only')
  expected={'bytes':row['bytes'],'sha256':row['sha256']}
  local=regular(R/row['local_path']);public=regular(R/row['public_path'])
  require(pin(local)==pin(public)==expected and local.read_bytes()==public.read_bytes(),'Exact reviewed whole local/public original differs')
  for origin in row['origin_manifests']:
   path=regular(R/origin['path']);require(pin(path)=={'bytes':origin['bytes'],'sha256':origin['sha256']},'Original authority manifest drift')
   require(json.loads(path.read_bytes())['build_authority_files'][row['local_path']]=={'sha256':row['sha256'],'bytes':row['bytes']},'Original authority entry differs')
 replacements={}
 for name,row in plan['cache_file_replacements'].items():
  target=R/'.cache/patch380_final_closeout.py'if name.startswith('../')else B/name
  candidate=regular(R/row['candidate'],D);require(pin(candidate)==row['after']and pin(regular(target))==row['before'],'Reviewed candidate/before bytes changed: '+name)
  raw=candidate.read_bytes()
  if target.suffix=='.py':ast.parse(raw)
  replacements[target]=raw
  if name.startswith('tools/'):
   cap_target=A/name.removeprefix('tools/');require(pin(regular(cap_target,A))==row['before'],'Original capsule counterpart drift: '+name);replacements[cap_target]=raw
 backup=B/'pre-canonical369-input-binding-repair';require(not backup.exists(),'Never overwrite original preflight repair evidence')
 record={'kind':'EXPLICIT_CANONICAL369_INPUT_BINDING_PREFREEZE_CACHE_ADAPTATION_NOT_FULL_EXECUTION',
  'at_utc':datetime.now(timezone.utc).isoformat(),'reviewed_plan':{'path':plan_path.relative_to(R).as_posix(),**pin(plan_path)},
  'source_review':review,'root_observed_terminal':{'path':observed.relative_to(R).as_posix(),**pin(observed)},
  'raw_complete_terminal_trace_file_available':False,'terminal_trace_reconstructed':False,
  'original_unexecuted_capsule_attempt':1,'new_full_execution_attempt_created':False,'source_freeze_or_activation_or_full_started':False,
  'old_prepared_READY':plan['expected_prepared_READY'],'old_capsule_READY':plan['expected_capsule_READY'],'old_capsule_descriptor':plan['expected_capsule_descriptor'],
  'actual_five_local_public_pairs_and_origin_manifests_rechecked':plan['bindings'],
  'public_files_written_by_this_patcher':[],'private_files_read_or_copied':False,'formal_sources_modified':False,
  'generic_public_still_rejects_all_cache':True,'original102_templates_unchanged':True,
  'old_bindings_exact_and_original30_29_typed_scopes_unchanged':True,
  'cache_replacements':{path.relative_to(R).as_posix():fingerprint(raw)for path,raw in replacements.items()},
  'tests_or_Qt_or_Git_or_component_started':False,'applied':args.apply}
 record_raw=enc(record);record_path=B/'canonical369-input-binding-repair.json'
 require(not record_path.exists(),'Never overwrite repair record')
 for target,raw in replacements.items():
  if target.is_relative_to(B)and not target.is_relative_to(A):ready['files'][target.relative_to(B).as_posix()]=fingerprint(raw)
 ready['files'][record_path.relative_to(B).as_posix()]=fingerprint(record_raw);ready['files']=dict(sorted(ready['files'].items()))
 ready_raw=enc(ready);replacements[B/'PREPARED_READY380.json']=ready_raw
 capsule['prepared_plan_sha256']=sha256(ready_raw).hexdigest();capsule_raw=enc(capsule);replacements[A/'capsule380.json']=capsule_raw
 for name in control['files']:
  target=A/name
  if target in replacements:control['files'][name]=fingerprint(replacements[target])
 control_raw=enc(control);replacements[A/'CONTROLLER_READY380.json']=control_raw
 if args.apply:
  backup.mkdir()
  for target in replacements:
   dest=backup/target.relative_to(R/'.cache');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(target.read_bytes())
  (backup/'source-review-original.json').write_bytes(review_path.read_bytes());(backup/'reviewed-plan-original.json').write_bytes(plan_path.read_bytes())
  for file in evidence_files:
   dest=backup/'root-observed-preflight'/file.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(file.read_bytes())
  for target,raw in replacements.items():target.write_bytes(raw)
  record_path.write_bytes(record_raw)
  for name,pn in ready['files'].items():require(pin(regular(B/name,B))==pn,'Applied prepared READY mismatch: '+name)
  for name,pn in control['files'].items():require(pin(regular(A/name,A))==pn,'Applied capsule READY mismatch: '+name)
  require(not(A/'activation380.json').exists()and not any(public_full.glob('source-freeze-attempt*.json')),'Repair cannot freeze or activate')
  (D/'applied-cache-repair.json').write_bytes(enc({**record,'new_prepared_READY':fingerprint(ready_raw),'new_capsule_READY':fingerprint(control_raw),'new_capsule_descriptor':fingerprint(capsule_raw),'preserved_originals':backup.relative_to(R).as_posix()}))
 print(json.dumps({'applied':args.apply,'cache_only':True,'new_prepared_READY':fingerprint(ready_raw),'new_capsule_READY':fingerprint(control_raw),'old102_templates_preserved':True,'public_inputs_verified_not_written':5,'new_full_attempt_or_execution_started':False,'next_action':'Root may actually retry declaration preflight on this still-unexecuted capsule1 only after reviewing these actual hashes.'if args.apply else'Review plan/guards, then root alone supplies --apply; this plan does not change READY or tools.'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
