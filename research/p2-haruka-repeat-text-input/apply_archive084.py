import hashlib,json,shutil,subprocess
from pathlib import Path
root=Path('/workspace/rougezhushou');src=Path('/workspace/.continuation/p2-haruka-repeat-text-input-084');dst=root/'research/p2-haruka-repeat-text-input';local=Path('/workspace/.continuation')
sha=lambda b:hashlib.sha256(b).hexdigest()
prior_sha='f5a462aa2571a71c288a3f56bc75d1541760d74b187c5fb38ee06715b19c421a'
assert subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)==''
assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()=='2f1e85e63a64a67efa4c48c09b97cb889f229907'
cp=json.loads((root/'DEVELOPMENT_CHECKPOINT.json').read_text());assert cp['completed_sections']==83 and cp['last_full_validation']['after_section']==80 and not cp['full_validation_due']
fixed={'handoff84.json':'19bb19c4439d62a7008d01d9021c992d637f05c9c6d1b69dcb02e9b9f52dc668','archivable-public-manifest84.json':'827236bfa945879e26bd5f69855ac4ce976b515009a8da1c6ef73426b041e29b','section84.patch':'3f38b22d4c7fcfc1f4fa683b0fad6dced4e2b8f10cc6334c5b6b3b1a2de87608'}
for name,digest in fixed.items():assert sha((src/name).read_bytes())==digest,name
h=json.loads((src/'handoff84.json').read_text());assert h['status']=='FINAL_SEALED'
for prefix in ('independent_final','independent_manifest'):assert sha(Path(h[prefix+'_path']).read_bytes())==h[prefix+'_sha256']
m=json.loads((src/'archivable-public-manifest84.json').read_text());assert m['format_version']==1 and len(m['files'])==85
payloads=[]
for row in m['files']:
 name=Path(row['archive_path']);assert not name.is_absolute() and '..' not in name.parts
 b=Path(row['source_path']).read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256'];payloads.append((name,b))
assert len({n for n,b in payloads})==len(payloads)
before=(root/'rouge/damage.py').read_bytes();assert sha(before)==prior_sha
guard=json.loads((src/'draft-freeze84.json').read_text())['guard'].encode();assert sha(guard)==h['guard_sha256'];assert guard.count(b'\r\n')==2
patch=local/'root-current-transport084.patch';receipt=local/'root-current-transport084.json'
subprocess.run([str(root/'.venv/bin/python'),str(src/'make-root-transport84.py'),'--repository',str(root),'--expected-current-damage-sha',prior_sha,'--output-patch',str(patch),'--output-receipt',str(receipt)],cwd=root,check=True)
transport=json.loads(receipt.read_text());assert transport['passed'] and transport['prior_current_bytes_preserved_exact_when_two_guard_lines_removed'];assert transport['current_damage_before_sha256']==prior_sha and sha(patch.read_bytes())==transport['patch_sha256'];assert transport['guard_sha256']==h['guard_sha256'] and transport['test_sha256']==h['test_sha256']
subprocess.run(['git','apply',str(patch)],cwd=root,check=True)
after=(root/'rouge/damage.py').read_bytes();assert after.count(guard)==1 and after.replace(guard,b'',1)==before and sha(after)==transport['adapted_damage_after_sha256'];assert sha((root/'tests/test_haruka_repeat_text_input.py').read_bytes())==h['test_sha256']
runner=root/'scripts/verify_cloud.py';b=runner.read_bytes();entry=b'    "tests.test_haruka_repeat_text_input",\n';assert entry not in b and b.count(b'MODULES = (\n')==1;runner.write_bytes(b.replace(b'MODULES = (\n',b'MODULES = (\n'+entry,1))
assert not dst.exists();dst.mkdir()
for name,b in payloads:
 p=dst/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);assert p.read_bytes()==b
for name in ('archivable-public-manifest84.json','handoff84.json'):shutil.copyfile(src/name,dst/name)
for p in (patch,receipt,Path(__file__)):shutil.copyfile(p,dst/p.name)
(dst/'root-integration084.json').write_text(json.dumps({'passed':True,'section':84,'explicit_artifacts_verified_before_apply':85,'only_exact_two_CRLF_guard_lines_inserted':True,'prior83_all_bytes_preserved':True,'approved_prior_damage_sha256':prior_sha,'current_adapted_damage_sha256':sha(after),'final_hashes':fixed,'matrix_API_reruns':0,'native_mechanism_changes':False},indent=2)+'\n')
print(json.dumps({'section':84,'applied':True,'artifacts_archived':85,'current_damage_sha256':sha(after)}))
