import gzip,hashlib,json,shutil,subprocess
from pathlib import Path
root=Path('/workspace/rougezhushou');src=Path('/workspace/.continuation/p2-neural-condition-text-input-083');dst=root/'research/p2-neural-condition-text-input'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)==''
assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()=='b5a40f30683bfc0945decaabbd4db5914c28427f'
cp=json.loads((root/'DEVELOPMENT_CHECKPOINT.json').read_text());assert cp['completed_sections']==82 and cp['last_full_validation']['after_section']==80 and not cp['full_validation_due']
fixed={'handoff.json':'836f030149d3449d03fc8443ca835409ccdd1209072f8a1c9704f053c9468148','public-artifacts-manifest.json':'ffd6a95b86cc6f72144fa342c65e81e1e3c592b91614a0da00d10279833a7944','draft.patch':'4d23463e553dcca35e10ebba701512a146d570cc5da8f6c861c451e22b59d246'}
for name,digest in fixed.items():assert sha((src/name).read_bytes())==digest,name
h=json.loads((src/'handoff.json').read_text());assert h['status']=='final_stable_author_and_two_independent_reviews_passed'
m=json.loads((src/'public-artifacts-manifest.json').read_text());assert m['format_version']==1 and len(m['files'])==253
payloads=[]
for row in m['files']:
 name=Path(row['archive_path']);assert not name.is_absolute() and '..' not in name.parts
 b=Path(row['source_path']).read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256'];payloads.append((name,b))
assert len({n for n,b in payloads})==len(payloads)
for key in ('independent_old_source','independent_formal_numeric_and_source'):
 proof=h[key];b=Path(proof['source_path']).read_bytes();assert sha(b)==proof['sha256'] and len(b)==proof['bytes']
 cm=json.loads(b);assert cm['format_version']==1 and len(cm['files'])==proof['listed_files']
 for row in cm['files']:
  b=Path(row['source_path']).read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256']
for row in json.loads((src/'lossless-compression083.json').read_text())['files']:
 data=(src/row['archive_path']).read_bytes();assert len(data)==row['archive_bytes'] and sha(data)==row['archive_sha256'];raw=gzip.decompress(data);assert len(raw)==row['original_bytes'] and sha(raw)==row['original_sha256']==row['decompressed_sha256']
for row in json.loads((src/'packed-independent-artifacts083.json').read_text())['files']:
 data=Path(row['compressed_source_path']).read_bytes();assert len(data)==row['compressed_bytes'] and sha(data)==row['compressed_sha256'];raw=gzip.decompress(data);assert len(raw)==row['original_bytes'] and sha(raw)==row['original_sha256']==row['decompressed_sha256']
before=(root/'rouge/damage.py').read_bytes();assert sha(before)=='84ff864244aed22307086df79686d485edf56700c727191ed7c3eca8bcbb9cec'
assert sha((root/'rouge/operator_engine.py').read_bytes())==h['unchanged_engine_82_sha256']
assert sha((root/'rouge/relics.py').read_bytes())=='79f5f607a247fbe366651c63ee951215a518e6a597868cd65e4212d16564e5d3'
guard=b''.join(line[1:] for line in (src/'draft.patch').read_bytes().splitlines(keepends=True) if line.startswith(b'+') and not line.startswith(b'+++'));assert guard.count(b'\r\n')==5
anchor=b"    result['report']=build_report(scenario,result)\r\n    return result\r\n\r\ndef _evaluate_damage(prepared,wine_phase=None) -> dict:";assert before.count(anchor)==1
patch=src/'draft.patch';subprocess.run(['git','apply','--check',str(patch)],cwd=root,check=True);subprocess.run(['git','apply',str(patch)],cwd=root,check=True)
expected=before.replace(anchor,anchor.replace(b'    return result\r\n',guard+b'    return result\r\n',1));assert (root/'rouge/damage.py').read_bytes()==expected;assert sha(expected)==h['draft_damage']['sha256']
test=h['new_test'];b=Path(test['source_path']).read_bytes();assert sha(b)==test['sha256'] and len(b)==test['bytes'];target=root/'tests/test_neural_condition_text_input.py';assert not target.exists();target.write_bytes(b)
runner=root/'scripts/verify_cloud.py';b=runner.read_bytes();entry=b'    "tests.test_neural_condition_text_input",\n';assert entry not in b and b.count(b'MODULES = (\n')==1;runner.write_bytes(b.replace(b'MODULES = (\n',b'MODULES = (\n'+entry,1))
assert not dst.exists();dst.mkdir()
for name,b in payloads:
 p=dst/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);assert p.read_bytes()==b
for name in ('public-artifacts-manifest.json','handoff.json'):shutil.copyfile(src/name,dst/name)
shutil.copyfile(Path(__file__),dst/'root-apply-archive083.py')
(dst/'root-integration083.json').write_text(json.dumps({'passed':True,'section':83,'explicit_artifacts_verified_before_apply':253,'preserved_engine82_and_relics81':True,'only_exact_five_CRLF_lines_changed':True,'source_only_patch_and_frozen_newtest_copy':True,'all_original_independent_46_and_132_entries_verified':True,'four_large_JSON_gzip_roundtrips_verified':True,'final_hashes':fixed,'matrix_API_reruns':0,'native_mechanism_changes':False},indent=2)+'\n')
print(json.dumps({'section':83,'applied':True,'artifacts_archived':253,'damage_sha256':sha(expected)}))
