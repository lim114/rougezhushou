import ast,hashlib,json,shutil,subprocess
from pathlib import Path
root=Path('/workspace/rougezhushou');src=Path('/workspace/.continuation/p2-orchid-near-text-085');dst=root/'research/p2-orchid-near-text-input';sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)==''
assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()=='70445181154cd8b6d034395dd92ec64c37677fff'
cp=json.loads((root/'DEVELOPMENT_CHECKPOINT.json').read_text());assert cp['completed_sections']==84 and cp['last_full_validation']['after_section']==80 and not cp['full_validation_due']
fixed={'handoff-author-final085.json':'095f24f8355994185bc9bf0821d7b43408e5ada08f44e7c7b43336452209bb07','public-artifacts-manifest-author-final085.json':'7aa4cc32bc52ee05a34132c1ed62cf9ccb729f68048d527297e632af3da7cf20','section85-root84-surgical.patch':'f6950cd12326f8339d9e78320ae1e18cdb3eb094b940fd0bb180b61d351ad30d','guard085-crlf.txt':'b9de57946088ba471f239ee3c2d993ce0ede3b22079fb6904d753508f5f25ca2'}
for name,digest in fixed.items():assert sha((src/name).read_bytes())==digest,name
h=json.loads((src/'handoff-author-final085.json').read_text());assert h['status']=='AUTHOR_FINAL_FROZEN_FORMAL_PASS_READY_FOR_ROOT_SURGICAL_INTEGRATION'
for prefix in ('independent_final','independent_manifest'):assert sha(Path(h[prefix+'_path']).read_bytes())==h[prefix+'_sha256']
m=json.loads((src/'public-artifacts-manifest-author-final085.json').read_text());assert m['format_version']==1 and len(m['files'])==100
payloads=[]
for row in m['files']:
 name=Path(row['archive_path']);assert not name.is_absolute() and '..' not in name.parts
 b=Path(row['source_path']).read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256'];payloads.append((name,b))
assert len({n for n,b in payloads})==len(payloads)
before=(root/'rouge/damage.py').read_bytes();assert sha(before)=='d02b8571542d08a63a56f08e6b129e9dfb43a9047595e77aabb54a3e0d04de6b'
guard=(src/'guard085-crlf.txt').read_bytes();assert len(guard)==441 and guard.count(b'\r\n')==6
function=next(n for n in ast.parse(before.decode()).body if isinstance(n,ast.FunctionDef) and n.name=='_evaluate_damage_once');assert isinstance(function.body[-1],ast.Return)
offset=sum(map(len,before.splitlines(keepends=True)[:function.body[-1].lineno-1]));expected=before[:offset]+guard+before[offset:]
receipt=json.loads((src/'transport-root84-receipt085.json').read_text());assert sha(expected)==receipt['root_damage_after_exact_insertion_sha256']
patch=src/'section85-root84-surgical.patch';subprocess.run(['git','apply','--check',str(patch)],cwd=root,check=True);subprocess.run(['git','apply',str(patch)],cwd=root,check=True)
assert (root/'rouge/damage.py').read_bytes()==expected and expected.replace(guard,b'',1)==before
test=Path(h['new_test_path']).read_bytes();assert sha(test)==h['new_test_sha256'];target=root/'tests/test_orchid_near_text_input.py';assert not target.exists();target.write_bytes(test)
runner=root/'scripts/verify_cloud.py';b=runner.read_bytes();entry=b'    "tests.test_orchid_near_text_input",\n';assert entry not in b and b.count(b'MODULES = (\n')==1;runner.write_bytes(b.replace(b'MODULES = (\n',b'MODULES = (\n'+entry,1))
assert not dst.exists();dst.mkdir()
for name,b in payloads:
 p=dst/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);assert p.read_bytes()==b
for name in ('public-artifacts-manifest-author-final085.json','handoff-author-final085.json'):shutil.copyfile(src/name,dst/name)
shutil.copyfile(Path(__file__),dst/'root-apply-archive085.py')
(dst/'root-integration085.json').write_text(json.dumps({'passed':True,'section':85,'explicit_artifacts_verified_before_apply':100,'only_exact_six_CRLF_guard_lines_inserted':True,'all_prior83_84_bytes_preserved':True,'current_damage_sha256':sha(expected),'author_saved_scope':'197 strict JSON types/3 reports; no preencoding native tree claimed','formal_fresh_scope':'12 independent inputs with preencoding native trees/3 reports/source','final_hashes':fixed,'matrix_API_reruns':0,'native_mechanism_changes':False},indent=2)+'\n')
print(json.dumps({'section':85,'applied':True,'artifacts_archived':100,'current_damage_sha256':sha(expected)}))
