import hashlib,json,shutil
from pathlib import Path,PurePosixPath

base=Path('/workspace/.continuation');archive=Path('/workspace/rougezhushou/research/p2-remaining-boolean-consumers')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def transport(folder,mf_name,expected,count,total,destname):
 src=base/folder;mf=src/mf_name;assert sha(mf)==expected
 rows=json.loads(mf.read_bytes())['files'];assert len(rows)==count and sum(r['bytes'] for r in rows)==total
 seen=set();out=archive/destname;assert not out.exists()
 for row in rows:
  name=PurePosixPath(row['archive_path']);assert not name.is_absolute() and '..' not in name.parts and str(name) not in seen
  seen.add(str(name));p=Path(row['source_path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
 out.mkdir()
 for row in rows:
  p=out/row['archive_path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['source_path'],p);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
 if mf.name in seen:assert sha(out/mf.name)==expected
 else:shutil.copyfile(mf,out/mf.name)
 return {'folder':destname,'files':count,'bytes':total,'manifest_sha256':expected}
packets=[transport('p2-section086-root-test-contract-supplement-independent','public-artifacts-manifest.json','32626ea27cd448c9422e955afbac7e41f92f02028839b3f0f3534db3ff75eaea',8,24250,'root-test-contract-independent')]
root=base/'p2-section086-root-test-contract-supplement';out=archive/'root-test-contract-supplement';assert not out.exists();shutil.copytree(root,out)
shutil.copyfile(base/'root-source-supplement-086.py',out/'root-source-supplement-086.py')
related=(base/'root-related-086.log').read_text();selected=json.loads((base/'root-selected-086.log').read_text().splitlines()[-1]);target=(out/'root-targeted-migration086.log').read_text();source=json.loads((out/'root-source-post-migration-086.json').read_bytes())
assert related.rstrip().endswith('OK') and 'Ran 122 tests' in related
assert selected['passed'] and selected['tests_run']==1027 and selected['skipped']==1 and selected['errors']==selected['failures']==0
assert target.rstrip().endswith('OK') and 'Ran 1 test' in target and source['passed']
receipt={'passed':True,'section':86,'fresh_related_run':122,'fresh_related_failures_errors':0,'migrated_historical_targeted_passed':1,'fresh_selected_run':1027,'fresh_selected_passed':1026,'historical_skips':1,'selected_failures_errors':0,'source_post_migration_old_sources_exact':719,'old_test_precise_contract_migration':True,'original130_unchanged':True,'independent_supplement':packets,'archive_preparation_failure':1,'static_helper_preparation_failure':1,'selected_old_expectation_failure':1,'all_failure_evidence_retained':True,'root_tests_API_calls_not_instrumented':True}
with (archive/'root-final-verification086.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
shutil.copyfile(__file__,archive/Path(__file__).name)
print(json.dumps(receipt))
