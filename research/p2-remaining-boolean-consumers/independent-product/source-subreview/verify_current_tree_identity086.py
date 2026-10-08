"""Bind the previous frozen blob checks to authoritative current-tree paths."""
from pathlib import Path
import hashlib
import json
import subprocess

OUT=Path(__file__).parent
BASE='9ef5a469673502754db3be320a8eece9a7fd18d4'
def sha(data):return hashlib.sha256(data).hexdigest()
def save_new(name,value):
 p=OUT/name;assert not p.exists(),str(p)
 p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
original_manifest_bytes=(OUT/'public-artifacts-manifest086.json').read_bytes()
assert sha(original_manifest_bytes)=='f2e5136968efd63d62135cb8631da8f07c450cf15046c1a4bc3b3ef8bc6f26ef'
original_manifest=json.loads(original_manifest_bytes)
assert original_manifest['format_version']==1 and len(original_manifest['files'])==11
for row in original_manifest['files']:
 data=Path(row['source_path']).read_bytes()
 assert sha(data)==row['sha256'] and len(data)==row['bytes'],row['source_path']
freeze=json.loads((OUT/'bound-current-baseline-freeze86.json').read_bytes())
assert freeze['base_commit']==BASE
tree=subprocess.check_output(['git','ls-tree','-r',BASE,'rouge','tests','scripts'],cwd='/workspace/rougezhushou',text=True)
fixed={}
for line in tree.splitlines():
 info,path=line.split('\t',1);mode,kind,gid=info.split()
 if path.endswith(('.py','.json')):
  assert kind=='blob';fixed[path]=gid
rows=freeze['files']
assert len(fixed)==len(rows)==723
assert fixed=={row['path']:row['git_blob'] for row in rows}
proof={'status':'PASS_FINAL_AUTHORITATIVE_PATH_TO_BLOB_BINDING','fixed_commit':BASE,'fixed_tree_paths_and_blob_ids_checked':723,'all_author_rows_equal_actual_fixed_tree':True,'original_sealed11_manifest_sha256':sha(original_manifest_bytes),'original11_files_immutable_and_rehashed':True,'binding_method':'git ls-tree -r gives actual fixed commit path->blob IDs; every row equals fixed tree. Original audit already checked these exact blobs, baseline and draft bytes. This sidecar completes the transitive fixed-tree proof without repeating any runtime checks.','evidence_scope_correction':'Initial script checked Git blob existence/content and exact fixed-tree path set; this new sidecar additionally binds each blob ID to its actual current fixed path. No mismatch found, no product failure and no previous frozen evidence modified.','new_API_helper_tests_GUI_Wine_tracked':0}
save_new('authoritative-current-tree-proof086.json',proof)
original_handoff=(OUT/'handoff-static-final086.json').read_bytes()
assert sha(original_handoff)=='855c65ab98102544af50499ca5d5af69a148fd78086a26e8ef672c99b11f12af'
save_new('handoff-static-complete086.json',{'status':'PASS_FINAL_STATIC_GUARDS_COMPLETE','section':86,'fixed_commit':BASE,'original_frozen_static_handoff_sha256':sha(original_handoff),'original_frozen_static_receipt_sha256':'b80dc520a155f2d840cdb217eda557536a3ac1523040a2afb078536ee350541f','authoritative_current_tree_proof_path':str(OUT/'authoritative-current-tree-proof086.json'),'authoritative_current_tree_proof_sha256':sha((OUT/'authoritative-current-tree-proof086.json').read_bytes()),'explicit_final_frozen':True,'baseline723_actual_fixed_tree_and_content_verified':True,'unchanged_old_draft721_verified':True,'old83_85_production_bytes_preserved':True,'all_Runtime_API_helper_tests_GUI_Wine_tracked':0,'parent_saved_and_fresh_numeric_review_separate':True,'scope':'static actual guard qualification/Oblvns reset and actual normal signal/exact override/legacy dominance/per-core error order; no universal outer-order proof or new native mechanics'})
files=[]
for path in sorted(OUT.iterdir()):
 if path.is_file():
  data=path.read_bytes();files.append({'source_path':str(path),'archive_path':path.name,'bytes':len(data),'sha256':sha(data)})
save_new('public-artifacts-manifest-complete086.json',{'format_version':1,'status':'FINAL_SEALED_COMPLETE_STATIC_SCOPE','section':86,'files':files,'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files),'manifest_self_excluded':True,'public_artifacts_only':True,'historical_sealed11_and_original_manifest_preserved':True,'excluded':['complete baseline/draft source execution copies; exact Git723 and721 unchanged hashes bound','old original tables/rank240/modules12/probes36: prior immutable manifests bound, not repeated','parent numeric saved/fresh/test outputs not owned by static child']})
for row in files:
 data=Path(row['source_path']).read_bytes();assert sha(data)==row['sha256'] and len(data)==row['bytes']
print(json.dumps({'status':'PASS_FINAL_STATIC_GUARDS_COMPLETE','handoff_path':str(OUT/'handoff-static-complete086.json'),'handoff_sha256':sha((OUT/'handoff-static-complete086.json').read_bytes()),'manifest_path':str(OUT/'public-artifacts-manifest-complete086.json'),'manifest_sha256':sha((OUT/'public-artifacts-manifest-complete086.json').read_bytes()),'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files),'authoritative_tree_proof_sha256':sha((OUT/'authoritative-current-tree-proof086.json').read_bytes())},ensure_ascii=False))
