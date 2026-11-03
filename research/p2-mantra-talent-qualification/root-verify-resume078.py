import gzip,hashlib,json,subprocess
from pathlib import Path
root=Path('/workspace/rougezhushou');dst=root/'research/p2-mantra-talent-qualification';src=Path('/workspace/.continuation/p2-mantra-talent-qualification-078')
def sha(b):return hashlib.sha256(b).hexdigest()
j=json.loads((dst/'root-integration078.json').read_text());m=json.loads((src/'manifest078.json').read_text());assert len(j['archives'])==len(m['files'])==58
for name,digest in j['final_hashes'].items():assert sha((src/name).read_bytes())==sha((dst/name).read_bytes())==digest
for row in j['archives']:
 name=row['source_path'];b=(src/name).read_bytes();out=(dst/row['archive_path']).read_bytes();assert sha(b)==m['files'][name]['sha256']==row['original_sha256'];assert len(b)==m['files'][name]['bytes']==row['original_bytes'];assert sha(out)==row['archived_sha256'] and len(out)==row['archived_bytes'];assert (gzip.decompress(out) if row['archive_path'].endswith('.gz') else out)==b
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();assert head==j['fixed_root_head']
before=subprocess.check_output(['git','show',head+':rouge/operator_engine.py'],cwd=root)
old="emit('麻痹触发天赋',attack*self.talent('噤声限域','atk_scale'),'elemental',triggers)".encode();new="emit('麻痹触发天赋',attack*self.talent('噤声限域','atk_scale'),'elemental',triggers if '噤声限域' in self.tv else 0.0)".encode();assert before.count(old)==1;assert (root/'rouge/operator_engine.py').read_bytes()==before.replace(old,new)
assert (root/'tests/test_mantra_talent_qualification.py').read_bytes()==(src/'test_mantra_talent_qualification.py').read_bytes()
runner=subprocess.check_output(['git','show',head+':scripts/verify_cloud.py'],cwd=root)
expected_runner=runner.replace(b'MODULES = (\n',b'MODULES = (\n    "tests.test_mantra_talent_qualification",\n',1)
assert (root/'scripts/verify_cloud.py').read_bytes()==expected_runner
receipt={'section':78,'passed':True,'already_pending_exact_source_and_archives_verified':True,'artifacts_verified':58,'engine_surgical_reconstruction':True,'preparation_rejected_clean_assertion_no_mutation_or_dependent_checks':True,'resume_preparation_syntax_error_no_mutation_or_dependent_checks':True,'preparation_failures':2,'native_windows':False}
(dst/'root-resume-verification078.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt))
