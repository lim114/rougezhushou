from pathlib import Path
from hashlib import sha256
import ast,json,subprocess
R=Path(__file__).resolve().parents[1];p=R/'.cache/publish369.py';raw=p.read_bytes();s=raw.decode('utf8')
old="names=changed|set(r['source_sha256'])|set(r['validated_source_sha256']);verified={}\nfor name in sorted(names):"
new="""names=changed|set(r['source_sha256'])|set(r['validated_source_sha256']);verified={}
manifests=('research/p3-boss-phase-309/source-manifest.json','research/p3-boss-cycle-310/source-manifest.json','research/p3-boss-hunt-311/source-manifest.json')
declared_local={}
for manifest_name in manifests:
 for name,pin in read(manifest_name)['build_authority_files'].items():
  if name.startswith('.cache/game-data/'):
   if name in declared_local:assert declared_local[name]==pin
   declared_local[name]=pin
local_names=names-set(tree)
assert local_names==set(declared_local) and len(local_names)==5
local_only={}
for name in sorted(local_names):
 path=ROOT/name;assert path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(ROOT.resolve())
 body=path.read_bytes();actual=sha256(body).hexdigest();pin=declared_local[name]
 assert actual==pin['sha256']and len(body)==pin['bytes']
 for group in('source_sha256','validated_source_sha256'):assert r[group][name]==actual
 local_only[name]={'sha256':actual,'bytes':len(body),'scope':'historical declared build authority only; local verified, absent from remote tree','remote_bytes_verified':False}
for name in sorted(names-local_names):"""
assert s.count(old)==1;s=s.replace(old,new)
old="'verified_commit_tree_and_local_public_bytes':verified,'private_state_included':False"
new="'verified_commit_tree_and_local_public_bytes':verified,'local_only_build_authority_sources_verified':local_only,'all_bound_sources_in_remote_tree':False,'local_build_authorities_are_runtime_requirements':False,'private_state_included':False"
assert s.count(old)==1;s=s.replace(old,new);ast.parse(s)
out=R/'.cache/section369-publication-partition-repair';out.mkdir();(out/'before-publish369.py').write_bytes(raw)
p.write_text(s,encoding='utf8',newline='\n')
record={'section':369,'original_functional_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip(),'original_git_push_exit':0,'publication_verifier_exit':1,'failure':'KeyError: .cache/game-data/levels/enemydata/enemy_database.json while requiring every selected local build authority to be a Git tree member','tool_output_reference':'functions.write_stdin chunk 8dd238; root transcription, not retained child stderr','local_build_authority_count':5,'scope':'historical manifests explicitly declare these only for build evidence; their runtime_files require public migrated snapshots instead','repair':'verify every tracked source/changed file against actual remote commit, separately rehash exact five local declared build authorities and check their pins; no cache/private files are uploaded','source_or_numeric_model_changed':False,'necessary_or_native_results_modified':False,'original_push_repeated_only_as_idempotent_normal_push':True,'before_publisher_sha256':sha256(raw).hexdigest(),'after_publisher_sha256':sha256(p.read_bytes()).hexdigest()}
(out/'failure-and-repair.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(out/'execution-repair.py').write_bytes(Path(__file__).read_bytes());print('369 publication verifier partition repaired; source/tests and existing commit unchanged; retry not executed.')
