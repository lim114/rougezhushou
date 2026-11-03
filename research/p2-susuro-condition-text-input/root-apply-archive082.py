import hashlib,json,shutil,subprocess
from pathlib import Path
root=Path('/workspace/rougezhushou');src=Path('/workspace/.continuation/p2-empty-source-consumer-audit-after-080');dst=root/'research/p2-susuro-condition-text-input'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)==''
assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()=='ea7866be6f2a8e89d382ec2982a45f1cb9231141'
cp=json.loads((root/'DEVELOPMENT_CHECKPOINT.json').read_text());assert cp['completed_sections']==81 and not cp['full_validation_due'] and cp['last_full_validation']['after_section']==80
fixed={'handoff82.json':'87b9f89f9ba4d8cffbcbb7c9306eea2ac8587d0aafec550d0f29f5bd53c94959','archivable-public-manifest82.json':'94a194af36e06eb784aacca4be22d898c7aa0e9dcda36669d6cdb896716397aa','section82.patch':'8406b15688d6d850da375ab8a47c0eb0710071fa3a324ff717e9c30f958f9dc7'}
for name,digest in fixed.items():assert sha((src/name).read_bytes())==digest,name
h=json.loads((src/'handoff82.json').read_text());assert h['status']=='FINAL_SEALED'
for prefix in ('independent_final','independent_manifest'):assert sha(Path(h[prefix+'_path']).read_bytes())==h[prefix+'_sha256']
m=json.loads((src/'archivable-public-manifest82.json').read_text());assert m['format_version']==1 and len(m['files'])==59
payloads=[]
for row in m['files']:
 name=Path(row['archive_path']);assert not name.is_absolute() and '..' not in name.parts
 b=Path(row['source_path']).read_bytes();assert sha(b)==row['sha256'] and len(b)==row['bytes'];payloads.append((name,b))
assert len({n for n,b in payloads})==len(payloads)
before=(root/'rouge/operator_engine.py').read_bytes();assert sha(before)=='166ec75dbf1afb45f3ad23ee28b43b8932a9a002c92d4a670cff3f108a5b3df7'
anchor=b"        elif op in ('char_196_sunbr','char_2025_shu','char_298_susuro'):\r\n";assert before.count(anchor)==1
guard=json.loads((src/'draft-freeze82.json').read_text())['guard'].encode()
assert guard.count(b'\r\n')==3
patch=src/'section82.patch';subprocess.run(['git','apply','--check',str(patch)],cwd=root,check=True);subprocess.run(['git','apply',str(patch)],cwd=root,check=True)
assert (root/'rouge/operator_engine.py').read_bytes()==before.replace(anchor,anchor+guard)
assert sha((root/'rouge/operator_engine.py').read_bytes())==h['engine_after_sha256'];assert sha((root/'tests/test_susuro_condition_text_input.py').read_bytes())==h['test_sha256']
assert sha((root/'rouge/relics.py').read_bytes())=='79f5f607a247fbe366651c63ee951215a518e6a597868cd65e4212d16564e5d3'
runner=root/'scripts/verify_cloud.py';b=runner.read_bytes();assert b'tests.test_susuro_condition_text_input' not in b;assert b.count(b'MODULES = (\n')==1;runner.write_bytes(b.replace(b'MODULES = (\n',b'MODULES = (\n    "tests.test_susuro_condition_text_input",\n',1))
assert not dst.exists();dst.mkdir()
for name,b in payloads:
 p=dst/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);assert p.read_bytes()==b
for name in ('archivable-public-manifest82.json','handoff82.json'):shutil.copyfile(src/name,dst/name)
(dst/'root-integration082.json').write_text(json.dumps({'passed':True,'section':82,'explicit_artifacts_verified_before_apply':59,'only_exact_three_CRLF_guard_lines_changed':True,'preserved_section81_warning_order':True,'final_hashes':fixed,'native_mechanism_changes':False,'author_matrix_not_rerun':True},indent=2)+'\n')
print(json.dumps({'section':82,'applied':True,'artifacts_archived':59,'engine_sha256':sha((root/'rouge/operator_engine.py').read_bytes())}))
